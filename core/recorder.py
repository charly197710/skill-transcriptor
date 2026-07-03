"""
core/recorder.py — Wrapper del script record.py para usar desde la app.
"""

import os
import sys
import threading
import subprocess
from pathlib import Path
from datetime import datetime


SKILL_DIR = Path(r"C:\Users\WIN10\.gemini\config\skills\meeting-transcriber\scripts")
RECORD_SCRIPT = SKILL_DIR / "record.py"


class AudioRecorder:
    """Grabador de audio que envuelve record.py."""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir or r"C:\Users\WIN10\MeetingApp\output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process: subprocess.Popen | None = None
        self.is_recording = False
        self.output_file: str | None = None

    def start_recording(self, duration: int = 0) -> str:
        """Iniciar grabación. Devuelve la ruta del archivo de salida."""
        if self.is_recording:
            raise RuntimeError("Ya se esta grabando.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_file = str(self.output_dir / f"grabacion_{timestamp}.wav")

        cmd = [
            "uv", "run", "python", str(RECORD_SCRIPT),
            "start",
            "--output", self.output_file,
            "--sample-rate", "16000",
            "--channels", "1",
        ]
        if duration > 0:
            cmd.extend(["--duration", str(duration)])

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.is_recording = True
        return self.output_file

    def stop_recording(self) -> str | None:
        """Detener grabación. Devuelve la ruta del archivo grabado o None."""
        if not self.is_recording or not self.process:
            return None

        # El script no tiene stop remoto; terminamos el proceso
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()

        self.is_recording = False

        if self.output_file and Path(self.output_file).exists():
            return self.output_file
        return None

    def get_output(self) -> str | None:
        """Devolver la ruta del archivo de salida."""
        return self.output_file

    @staticmethod
    def get_recordings(output_dir: str = None) -> list:
        """Listar grabaciones existentes."""
        d = Path(output_dir or r"C:\Users\WIN10\MeetingApp\output")
        if not d.exists():
            return []
        files = sorted(d.glob("*.wav"), key=lambda f: f.stat().st_mtime, reverse=True)
        return [
            {
                "name": f.name,
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            }
            for f in files
        ]
