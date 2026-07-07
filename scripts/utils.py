#!/usr/bin/env python3
"""
utils.py -- Funciones utilitarias para Meeting Transcriber.
Informacion de archivos, formatos soportados, configuracion.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


AUDIO_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".wma"}
VIDEO_EXT = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
ALL_EXT = AUDIO_EXT | VIDEO_EXT


def get_audio_info(file_path):
    """Obtener informacion de un archivo de audio/video."""
    path = Path(file_path)
    if not path.exists():
        print(f"ERROR: Archivo no encontrado: {file_path}")
        sys.exit(1)

    info = {
        "file": str(path),
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "type": "video" if path.suffix.lower() in VIDEO_EXT else "audio",
    }

    if shutil.which("ffprobe"):
        import subprocess
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration,size",
            "-show_entries", "stream=codec_name,sample_rate,channels",
            "-of", "json", str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                fmt = data.get("format", {})
                streams = data.get("streams", [])
                info["duration"] = float(fmt.get("duration", 0))
                info["duration_formatted"] = _format_duration(info["duration"])
                if streams:
                    s = streams[0]
                    info["codec"] = s.get("codec_name", "unknown")
                    info["sample_rate"] = int(s.get("sample_rate", 0))
                    info["channels"] = int(s.get("channels", 0))
            except (json.JSONDecodeError, ValueError):
                pass

    return info


def _format_duration(seconds):
    """Formatear duracion en HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def show_formats():
    """Mostrar formatos soportados."""
    print("Formatos soportados:")
    print()
    print("AUDIO:", ", ".join(sorted(AUDIO_EXT)))
    print("VIDEO:", ", ".join(sorted(VIDEO_EXT)))
    print()
    print("Requisitos: ffmpeg para video y formatos comprimidos")


def check_dependencies():
    """Verificar dependencias del sistema."""
    print("Verificando dependencias...")
    print()

    ffmpeg = shutil.which("ffmpeg")
    print(f"  ffmpeg: {'OK' if ffmpeg else 'NO ENCONTRADO'}")
    if not ffmpeg:
        print("    Descarga: https://ffmpeg.org/download.html")

    packages = {
        "sounddevice": "Grabacion de audio",
        "soundfile": "Lectura/escritura de audio",
        "faster_whisper": "Transcripcion local",
        "fpdf2": "Generacion de PDF",
    }

    for pkg, desc in packages.items():
        try:
            __import__(pkg)
            print(f"  {pkg}: OK ({desc})")
        except ImportError:
            print(f"  {pkg}: NO INSTALADO ({desc})")
            print(f"    Instala: uv pip install {pkg.replace('_', '-')}")


def main():
    parser = argparse.ArgumentParser(description="Utilidades Meeting Transcriber")
    sub = parser.add_subparsers(dest="command")

    p_info = sub.add_parser("info", help="Informacion de un archivo")
    p_info.add_argument("--input", "-i", required=True, help="Archivo de audio/video")

    sub.add_parser("formats", help="Formatos soportados")
    sub.add_parser("check", help="Verificar dependencias")

    args = parser.parse_args()

    if args.command == "info":
        info = get_audio_info(args.input)
        print(json.dumps(info, indent=2, ensure_ascii=False))
    elif args.command == "formats":
        show_formats()
    elif args.command == "check":
        check_dependencies()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
