#!/usr/bin/env python3
"""
transcribe.py — Motor de transcripción híbrido.
Modo local: faster-whisper (gratis, sin internet)
Modo API: OpenRouter (requiere API key)
"""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# ── Constantes ──────────────────────────────────────────────────
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".wma"}
VIDEO_EXT = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
ALL_EXT = AUDIO_EXT | VIDEO_EXT

CHUNK_DURATION = 30  # segundos por segmento

def clean_transcript(text):
    """Eliminar repeticiones de frases/palabras como 'a tu, a tu, a tu'."""
    if not text:
        return text
    import re
    
    # Eliminar repeticiones separadas por comas: "a tu, a tu, a tu" -> "a tu"
    parts = text.split(", ")
    cleaned_parts = []
    for part in parts:
        part_stripped = part.strip()
        if cleaned_parts and cleaned_parts[-1] == part_stripped:
            continue
        cleaned_parts.append(part)
    
    # Volver a unir
    cleaned = ", ".join(cleaned_parts)
    
    # Eliminar repeticiones simples sin coma: "mmm mmm mmm" -> "mmm"
    cleaned = re.sub(r"\b(\w+)\s+\1\b", r"\1", cleaned)
    
    # Normalizar espacios múltiples
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    
    return cleaned.strip()



def check_ffmpeg():
    """Verificar si ffmpeg está disponible."""
    import shutil
    return shutil.which("ffmpeg") is not None


def extract_audio(video_path, output_wav):
    """Extraer audio de un video usando ffmpeg."""
    import subprocess
    if not check_ffmpeg():
        print("ERROR: ffmpeg no encontrado en PATH.")
        print("Descarga: https://ffmpeg.org/download.html")
        sys.exit(1)
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", output_wav,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error extrayendo audio: {result.stderr[-300:]}")
        sys.exit(1)
    return output_wav


def transcribe_local(audio_path, model_size="base", lang="auto"):
    """Transcripción local con faster-whisper (sin internet)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper no instalado.")
        print("Instala con: uv pip install faster-whisper")
        sys.exit(1)

    print(f"Cargando modelo '{model_size}'...")
    device = "cpu"
    compute_type = "int8"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"Transcribiendo (local)...")
    start = time.monotonic()

    results = model.transcribe(
        audio_path,
        language=None if lang == "auto" else lang,
        task="transcribe",
        beam_size=5,
        vad_filter=True,
    )

    segments = []
    full_text = []
    detected_lang = None

    for segment in results[0]:
        segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
        })
        full_text.append(segment.text.strip())

    if results[1]:
        detected_lang = results[1].language

    elapsed = time.monotonic() - start
    text = " ".join(full_text)
    text = clean_transcript(text)  # Limpiar repeticiones

    return {
        "text": text,
        "segments": segments,
        "language": detected_lang or lang,
        "duration_seconds": round(elapsed, 2),
        "mode": "local",
        "model": f"faster-whisper-{model_size}",
    }


def transcribe_api(audio_path, api_key, model="openai/whisper-1", lang="auto"):
    """Transcripción vía API (OpenRouter o Groq)."""
    import base64
    import urllib.request
    import urllib.error
    import json as json_mod

    print(f"Transcribiendo via API ({model})...")
    start = time.monotonic()

    # Detectar el proveedor basado en el modelo o API key
    if "groq" in model.lower() or api_key.startswith("gsk_"):
        return _transcribe_groq(audio_path, api_key, model, lang, start)

    # OpenRouter (default)
    url = "https://openrouter.ai/api/v1/audio/transcriptions"

    # Leer archivo de audio y codificar en base64
    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    # Formato correcto para OpenAI Whisper API en OpenRouter
    payload = {
        "model": model,
        "input_audio": {
            "data": audio_data,
            "format": Path(audio_path).suffix.lstrip("."),
        },
    }
    if lang != "auto":
        payload["language"] = lang

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json_mod.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            result_data = json_mod.loads(response.read().decode("utf-8"))

        elapsed = time.monotonic() - start
        text = result_data.get("text", "")

        return {
            "text": text,
            "segments": [],
            "language": lang,
            "duration_seconds": round(elapsed, 2),
            "mode": "api",
            "model": model,
        }

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR API {e.code}: {error_body[:300]}")
        return {
            "text": "",
            "segments": [],
            "language": lang,
            "duration_seconds": round(time.monotonic() - start, 2),
            "mode": "api",
            "model": model,
            "error": f"HTTP {e.code}: {error_body[:200]}",
        }
    except Exception as e:
        print(f"ERROR API: {e}")
        return {
            "text": "",
            "segments": [],
            "language": lang,
            "duration_seconds": round(time.monotonic() - start, 2),
            "mode": "api",
            "model": model,
            "error": str(e),
        }


def _transcribe_groq(audio_path, api_key, model, lang, start):
    """Transcripción vía Groq (gratis)."""
    import base64, urllib.request, urllib.error, json as json_mod

    groq_url = "https://api.groq.com/openai/v1/audio/transcriptions"

    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": model or "whisper-large-v3-turbo",
        "input_audio": {
            "data": audio_data,
            "format": Path(audio_path).suffix.lstrip("."),
        },
    }
    if lang != "auto":
        payload["language"] = lang

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        req = urllib.request.Request(
            groq_url,
            data=json_mod.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            result_data = json_mod.loads(response.read().decode("utf-8"))

        elapsed = time.monotonic() - start
        text = result_data.get("text", "")
        print(f"  Groq OK: {text[:100]}...")
        return {
            "text": text,
            "segments": [],
            "language": lang,
            "duration_seconds": round(elapsed, 2),
            "mode": "api",
            "model": model or "whisper-large-v3-turbo",
        }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"  ERROR Groq {e.code}: {error_body[:300]}")
        return {
            "text": "", "segments": [], "language": lang,
            "duration_seconds": round(time.monotonic() - start, 2),
            "mode": "api", "model": model or "whisper-large-v3-turbo",
            "error": f"HTTP {e.code}: {error_body[:200]}",
        }
    except Exception as e:
        print(f"  ERROR Groq: {e}")
        return {
            "text": "", "segments": [], "language": lang,
            "duration_seconds": round(time.monotonic() - start, 2),
            "mode": "api", "model": model or "whisper-large-v3-turbo",
            "error": str(e),
        }


def transcribe_audio(audio_path, args):
    """Funcion principal de transcripcion."""
    path = Path(audio_path)
    if not path.exists():
        print(f"ERROR: Archivo no encontrado: {audio_path}")
        sys.exit(1)

    needs_cleanup = False
    if path.suffix.lower() in VIDEO_EXT:
        print("Detectado video. Extrayendo audio...")
        tmp_wav = tempfile.mktemp(suffix=".wav", prefix="mtg_audio_")
        audio_path = extract_audio(audio_path, tmp_wav)
        needs_cleanup = True

    mode = getattr(args, 'mode', None) or getattr(args, 'command', 'local')
    try:
        if mode == "local":
            result = transcribe_local(
                audio_path,
                model_size=getattr(args, "whisper_model", "base"),
                lang=args.lang,
            )
        elif mode == "api":
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key and hasattr(args, "api_key") and args.api_key:
                api_key = args.api_key
            if not api_key:
                print("ERROR: Se requiere OPENROUTER_API_KEY o --api-key")
                sys.exit(1)
            result = transcribe_api(audio_path, api_key, model=args.model, lang=args.lang)
        else:
            print(f"ERROR: Modo desconocido: {args.mode}")
            sys.exit(1)
    finally:
        if needs_cleanup and Path(audio_path).exists():
            os.unlink(audio_path)

    return result


def detect_language(audio_path):
    """Detectar idioma de un archivo de audio."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper requerido para deteccion de idioma.")
        sys.exit(1)
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    _, info = model.transcribe(audio_path, language=None, task="detect_language")
    print(f"Idioma detectado: {info.language} (confianza: {info.language_probability:.1%})")
    return info.language


def format_srt_time(seconds):
    """Formatear tiempo para SRT (HH:MM:SS,mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    parser = argparse.ArgumentParser(description="Transcripcion de audio/video")
    sub = parser.add_subparsers(dest="command")

    # local
    p_local = sub.add_parser("local", help="Transcripcion local (sin internet)")
    p_local.add_argument("--input", "-i", required=True, help="Archivo de audio/video")
    p_local.add_argument("--output", "-o", default=None, help="Archivo de salida")
    p_local.add_argument("--lang", default="auto", help="Idioma (default: auto-detect)")
    p_local.add_argument(
        "--whisper-model", default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Tamano del modelo Whisper (default: base)",
    )
    p_local.add_argument("--format", default="text", choices=["text", "json", "srt"])
    p_local.add_argument("--chunk-size", type=int, default=CHUNK_DURATION)

    # api
    p_api = sub.add_parser("api", help="Transcripcion via API (OpenRouter)")
    p_api.add_argument("--input", "-i", required=True, help="Archivo de audio/video")
    p_api.add_argument("--output", "-o", default=None, help="Archivo de salida")
    p_api.add_argument("--lang", default="auto", help="Idioma")
    p_api.add_argument("--model", default="openai/whisper", help="Modelo en OpenRouter")
    p_api.add_argument("--api-key", default=None, help="API key (o OPENROUTER_API_KEY)")
    p_api.add_argument("--format", default="text", choices=["text", "json", "srt"])
    p_api.add_argument("--chunk-size", type=int, default=CHUNK_DURATION)

    # detect-lang
    p_detect = sub.add_parser("detect-lang", help="Detectar idioma de un archivo")
    p_detect.add_argument("--input", "-i", required=True, help="Archivo de audio")

    args = parser.parse_args()

    if args.command == "detect-lang":
        detect_language(args.input)
        return

    if args.command in ("local", "api"):
        result = transcribe_audio(args.input, args)

        output = args.output
        if not output:
            stem = Path(args.input).stem
            ext = "txt" if args.format == "text" else args.format
            output = f"{stem}_transcripcion.{ext}"

        if args.format == "json":
            with open(output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        elif args.format == "srt":
            with open(output, "w", encoding="utf-8") as f:
                for i, seg in enumerate(result["segments"], 1):
                    start = format_srt_time(seg["start"])
                    end = format_srt_time(seg["end"])
                    f.write(f"{i}\n{start} --> {end}\n{seg['text']}\n\n")
        else:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result["text"])

        print(f"\nTranscripcion guardada: {output}")
        print(f"  Idioma: {result.get('language', '?')}")
        print(f"  Duracion: {result.get('duration_seconds', '?')}s")
        print(f"  Modo: {result.get('mode', '?')}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
