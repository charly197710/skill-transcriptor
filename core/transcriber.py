"""
core/transcriber.py — Wrapper del script transcribe.py para usar desde la app.
"""

import json
import subprocess
from pathlib import Path


SKILL_DIR = Path(r"C:\Users\WIN10\.gemini\config\skills\meeting-transcriber\scripts")
TRANSCRIBE_SCRIPT = SKILL_DIR / "transcribe.py"


class Transcriber:
    """Transcriptor híbrido (local + API)."""

    def __init__(self, mode: str = "local", api_key: str = None, lang: str = "auto"):
        self.mode = mode
        self.api_key = api_key
        self.lang = lang

    def set_mode(self, mode: str):
        """Cambiar modo: 'local' o 'api'."""
        self.mode = mode

    def set_api_key(self, key: str):
        """Establecer API key para modo API."""
        self.api_key = key

    def set_lang(self, lang: str):
        """Establecer idioma (auto para detección automática)."""
        self.lang = lang

    def transcribe(self, input_path: str, output_path: str = None,
                    whisper_model: str = "base", output_format: str = "json",
                    on_progress=None) -> dict:
        """
        Transcribir un archivo de audio/video.

        Args:
            input_path: Ruta al archivo de audio o video
            output_path: Ruta de salida (opcional, se genera automático)
            whisper_model: Tamaño del modelo (tiny/base/small/medium/large-v3)
            output_format: Formato de salida (text/json/srt)
            on_progress: Callback para reportar progreso (str -> None)

        Returns:
            dict con {'output': ruta, 'text': texto, 'language': idioma, ...}
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {input_path}")

        if not output_path:
            stem = input_file.stem
            ext = "txt" if output_format == "text" else output_format
            output_path = str(input_file.parent / f"{stem}_transcripcion.{ext}")

        cmd = [
            "uv", "run", "python", str(TRANSCRIBE_SCRIPT),
            self.mode,
            "--input", str(input_path),
            "--output", str(output_path),
            "--lang", self.lang,
            "--format", output_format,
        ]

        if self.mode == "local":
            cmd.extend(["--whisper-model", whisper_model])
        elif self.mode == "api":
            if self.api_key:
                cmd.extend(["--api-key", self.api_key])

        if on_progress:
            on_progress("Iniciando transcripcion...")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error en transcripcion: {error_msg[-500:]}")

        # Leer resultado si es JSON
        text = ""
        language = self.lang
        if output_format == "json" and Path(output_path).exists():
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = data.get("text", "")
                language = data.get("language", self.lang)
        elif Path(output_path).exists():
            with open(output_path, "r", encoding="utf-8") as f:
                text = f.read()

        if on_progress:
            on_progress("Transcripcion completada")

        return {
            "output": output_path,
            "text": text,
            "language": language,
        }

    def detect_language(self, input_path: str) -> dict:
        """Detectar idioma de un archivo de audio."""
        cmd = [
            "uv", "run", "python", str(TRANSCRIBE_SCRIPT),
            "detect-lang",
            "--input", str(input_path),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        return {"raw_output": result.stdout, "success": result.returncode == 0}
