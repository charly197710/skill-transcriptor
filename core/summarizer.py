"""
core/summarizer.py — Wrapper de summary.py + mindmap.py para usar desde la app.
"""

import json
import subprocess
from pathlib import Path


SKILL_DIR = Path(r"C:\Users\WIN10\MeetingApp\scripts")
SUMMARY_SCRIPT = SKILL_DIR / "summary.py"
MINDMAP_SCRIPT = SKILL_DIR / "mindmap.py"


class Summarizer:
    """Generador de resumenes y mapas mentales."""

    def generate_summary(self, analysis_path: str, format: str = "md",
                         lang: str = "es", output_path: str = None) -> str:
        """
        Generar resumen desde un analisis.

        Args:
            analysis_path: Ruta al archivo JSON de analisis
            format: Formato de salida (txt/md/pdf)
            lang: Idioma del resumen
            output_path: Ruta de salida (opcional)

        Returns:
            Ruta del archivo generado
        """
        if not output_path:
            stem = Path(analysis_path).stem.replace("_analisis", "")
            output_path = str(Path(r"C:\Users\WIN10\MeetingApp\output") / f"{stem}_resumen.{format}")

        cmd = [
            "uv", "run", "python", str(SUMMARY_SCRIPT),
            format,
            "--input", analysis_path,
            "--output", output_path,
            "--lang", lang,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if result.returncode != 0:
            error = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error generando resumen: {error[-500:]}")

        return output_path

    def generate_mindmap(self, analysis_path: str, output_path: str = None) -> str:
        """
        Generar mapa mental HTML desde un analisis.

        Args:
            analysis_path: Ruta al archivo JSON de analisis
            output_path: Ruta de salida (opcional)

        Returns:
            Ruta del archivo HTML generado
        """
        if not output_path:
            stem = Path(analysis_path).stem.replace("_analisis", "")
            output_path = str(Path(r"C:\Users\WIN10\MeetingApp\output") / f"{stem}_mapa.html")

        cmd = [
            "uv", "run", "python", str(MINDMAP_SCRIPT),
            "generate",
            "--input", analysis_path,
            "--output", output_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

        if result.returncode != 0:
            error = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error generando mapa mental: {error[-500:]}")

        return output_path
