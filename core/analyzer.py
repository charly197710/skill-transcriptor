#!/usr/bin/env python3
core/analyzer.py — Analizador de transcripciones con estilo de redactor.
'''
import re
from pathlib import Path

class Analyzer:
    def analyze(self, transcription_input, output_path=None):
        input_path = Path(transcription_input)
        if input_path.exists():
            text = input_path.read_text(encoding="utf-8")
            try:
                import json
                data = json.loads(text)
                text = data.get("text", "")
            except:
                pass
        else:
            text = transcription_input
        result = self._generate_pro_analysis(text)
        if output_path:
            Path(output_path).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result

    def _generate_pro_analysis(self, text):
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        return {
            "idea_principal": sentences[0] if sentences else "No identificado",
            "nota_pulida": self._generate_pulida(sentences),
            "puntos_clave": self._extract_key_points(sentences),
            "decisiones": self._extract_decisions(sentences),
            "action_items": self._extract_actions(sentences),
        }

    def _generate_pulida(self, sentences):
        key = [s.capitalize() for s in sentences[:5] if len(s) > 20]
        return " ".join(key) + "." if key else "Transcripción procesada."

    def _extract_key_points(self, sentences):
        kw = ["importante", "clave", "servicio", "producto", "precio", "cliente"]
        pts = []
        for s in sentences:
            if any(k.lower() in s.lower() for k in kw) and len(s) > 30:
                pts.append(s.strip())
        return pts[:4] if pts else [sentences[0] if sentences else "N/A"]

    def _extract_decisions(self, sentences):
        kw = ["decisión", "vamos a", "vale", "quiero"]
        return [s.strip() for s in sentences if any(k.lower() in s.lower() for k in kw)][:3]

    def _extract_actions(self, sentences):
        kw = ["falta", "queda", "hay que", "debemos"]
        acts = []
        for s in sentences:
            for k in kw:
                if k.lower() in s.lower():
                    acts.append(s.strip())
                    break
        return acts[:3]
