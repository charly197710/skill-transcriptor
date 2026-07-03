"""
core/analyzer.py — Wrapper del script analyze.py para usar desde la app.
"""

import json
import subprocess
from pathlib import Path


SKILL_DIR = Path(r"C:\Users\WIN10\.gemini\config\skills\meeting-transcriber\scripts")
ANALYZE_SCRIPT = SKILL_DIR / "analyze.py"


class Analyzer:
    """Analizador de transcripciones."""

    def analyze(self, transcription_input: str, output_path: str = None) -> dict:
        """
        Analizar una transcripción (texto o JSON de transcripción).

        Args:
            transcription_input: Texto de transcripción o ruta a archivo
            output_path: Ruta de salida del análisis (opcional)

        Returns:
            dict con keys: resumen_ejecutivo, puntos_clave, decisiones, action_items,
                           participantes, temas, sentimiento
        """
        input_path = Path(transcription_input)

        if input_path.exists():
            file_to_analyze = str(input_path)
        else:
            # Es texto directo, guardar temporal
            tmp = Path(r"C:\Users\WIN10\MeetingApp\output") / "_temp_transcripcion.txt"
            tmp.write_text(transcription_input, encoding="utf-8")
            file_to_analyze = str(tmp)

        if not output_path:
            stem = Path(file_to_analyze).stem
            output_path = str(Path(r"C:\Users\WIN10\MeetingApp\output") / f"{stem}_analisis.json")

        cmd = [
            "uv", "run", "python", str(ANALYZE_SCRIPT),
            "full",
            "--input", file_to_analyze,
            "--output", output_path,
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        if result.returncode != 0:
            error = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error en analisis: {error[-500:]}")

        # Cargar resultado
        if Path(output_path).exists():
            with open(output_path, "r", encoding="utf-8") as f:
                return json.load(f)

        raise RuntimeError("No se genero el archivo de analisis.")
