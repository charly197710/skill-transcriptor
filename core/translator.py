"""
core/translator.py — Wrapper del script translate.py para usar desde la app.
"""

import json
import subprocess
from pathlib import Path


SKILL_DIR = Path(r"C:\Users\WIN10\.gemini\config\skills\translator\scripts")
TRANSLATE_SCRIPT = SKILL_DIR / "translate.py"


class Translator:
    """Traductor hibrido (local + API)."""

    def __init__(self, mode="local", api_key=None, source_lang="auto", target_lang="es"):
        self.mode = mode
        self.api_key = api_key
        self.source_lang = source_lang
        self.target_lang = target_lang

    def set_mode(self, mode):
        self.mode = mode

    def set_api_key(self, key):
        self.api_key = key

    def set_languages(self, source="auto", target="es"):
        self.source_lang = source
        self.target_lang = target

    def translate_text(self, text):
        """Traducir un texto."""
        cmd = [
            "uv", "run", "python", str(TRANSLATE_SCRIPT),
            self.mode,
            "--text", text,
            "--source", self.source_lang,
            "--target", self.target_lang,
        ]
        if self.mode == "api" and self.api_key:
            cmd.extend(["--api-key", self.api_key])

        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120,
        )
        if result.returncode != 0:
            error = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error en traduccion: {error[-300:]}")
        return result.stdout.strip()

    def translate_file(self, input_path, output_path=None):
        """Traducir un archivo."""
        if not output_path:
            stem = Path(input_path).stem
            output_path = str(Path(input_path).parent / f"{stem}_traducido.txt")

        cmd = [
            "uv", "run", "python", str(TRANSLATE_SCRIPT),
            self.mode,
            "--input", input_path,
            "--output", output_path,
            "--source", self.source_lang,
            "--target", self.target_lang,
        ]
        if self.mode == "api" and self.api_key:
            cmd.extend(["--api-key", self.api_key])

        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=300,
        )
        if result.returncode != 0:
            error = result.stderr or result.stdout or "Error desconocido"
            raise RuntimeError(f"Error en traduccion: {error[-300:]}")
        return output_path

    def translate_analysis(self, analysis_path, target_lang=None, output_path=None):
        """Traducir un analisis completo."""
        target = target_lang or self.target_lang

        with open(analysis_path, "r", encoding="utf-8") as f:
            analysis = json.load(f)

        if analysis.get("resumen_ejecutivo"):
            analysis["resumen_ejecutivo"] = self.translate_text(analysis["resumen_ejecutivo"])
        if analysis.get("puntos_clave"):
            analysis["puntos_clave"] = [self.translate_text(p) for p in analysis["puntos_clave"]]
        if analysis.get("decisiones"):
            analysis["decisiones"] = [self.translate_text(d) for d in analysis["decisiones"]]
        if analysis.get("action_items"):
            analysis["action_items"] = [self.translate_text(a) for a in analysis["action_items"]]

        if not output_path:
            stem = Path(analysis_path).stem
            output_path = str(Path(analysis_path).parent / f"{stem}_traducido.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        return output_path
