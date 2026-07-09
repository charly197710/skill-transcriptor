#!/usr/bin/env python3
"""Meeting Transcriber - Versión standalone para PyInstaller."""

import flet as ft
import os
import json
import asyncio
import re
from pathlib import Path

class Analyzer:
    def analyze(self, text, output_path=None):
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
        pts = [s.strip() for s in sentences if any(k in s.lower() for k in kw) and len(s) > 30]
        return pts[:4] if pts else [sentences[0] if sentences else "N/A"]

    def _extract_decisions(self, sentences):
        kw = ["decisión", "vamos a", "vale", "quiero"]
        return [s.strip() for s in sentences if any(k in s.lower() for k in kw)][:3]

    def _extract_actions(self, sentences):
        kw = ["falta", "queda", "hay que", "debemos"]
        acts = []
        for s in sentences:
            for k in kw:
                if k in s.lower():
                    acts.append(s.strip())
                    break
        return acts[:3]


def clean_transcript(text):
    if not text:
        return text
    parts = text.split(", ")
    cleaned_parts = []
    for part in parts:
        p = part.strip()
        if p and (not cleaned_parts or cleaned_parts[-1] != p):
            cleaned_parts.append(p)
    cleaned = ", ".join(cleaned_parts)
    cleaned = re.sub(r"\b(\w{2,})\s+\1\b", r"\1", cleaned)
    return cleaned.strip()


class Transcriber:
    def transcribe(self, audio_path, whisper_model="tiny", output_format="text"):
        from faster_whisper import WhisperModel
        model = WhisperModel(whisper_model, device="cpu", compute_type="int8")
        results = model.transcribe(audio_path, language=None, task="transcribe", beam_size=5, vad_filter=True)
        full_text = [seg.text.strip() for seg in results[0]]
        text = clean_transcript(" ".join(full_text))
        lang = results[1].language if results[1] else "es"
        output = str(Path(audio_path).with_suffix(".transcript.txt"))
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
        return {"text": text, "language": lang, "output": output}


async def main_app(page):
    page.window.prevent_close = True
    state = {"current_audio": None, "current_analysis": None}

    file_info = ft.Text("Sin archivo", size=14, color=ft.Colors.GREY_500)
    status_text = ft.Text("Listo", size=14, color=ft.Colors.GREY_400)
    progress = ft.ProgressBar(visible=False)
    transcription = ft.TextField(multiline=True, min_lines=5, max_lines=10, read_only=True, expand=True, bgcolor="#1e293b")
    analysis = ft.TextField(multiline=True, min_lines=5, max_lines=10, read_only=True, expand=True, bgcolor="#1e293b")

    transcriber = Transcriber()
    analyzer = Analyzer()

    def pick_file(e):
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3 *.ogg *.flac"), ("Video", "*.mp4 *.mkv")])
        root.destroy()
        if path:
            state["current_audio"] = path
            file_info.value = f"Archivo: {os.path.basename(path)}"
            page.update()

    async def do_transcribe():
        audio = state.get("current_audio")
        if not audio:
            return
        try:
            status_text.value = "Transcribiendo..."
            progress.visible = True
            page.update()
            result = await asyncio.to_thread(transcriber.transcribe, audio, "tiny")
            transcription.value = result["text"]
            status_text.value = f"Listo. Idioma: {result['language']}"
        finally:
            progress.visible = False
            page.update()

    async def do_analyze():
        text = transcription.value
        if not text:
            return
        try:
            status_text.value = "Analizando..."
            progress.visible = True
            page.update()
            result = analyzer.analyze(text)
            state["current_analysis"] = result
            lines = [f"IDEA PRINCIPAL: {result['idea_principal']}", f"NOTA PULIDA:\n{result['nota_pulida']}\n\nPUNTOS CLAVE:"]
            for i, p in enumerate(result["puntos_clave"], 1):
                lines.append(f"  {i}. {p}")
            analysis.value = "\n".join(lines)
            status_text.value = "Análisis listo"
        finally:
            progress.visible = False
            page.update()

    page.add(
        ft.Column([
            ft.Container(ft.Text("Meeting Transcriber", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), bgcolor="#16213e", padding=15),
            ft.Container(padding=20, expand=True,
                content=ft.Column([
                    ft.ElevatedButton("Seleccionar archivo", on_click=pick_file, style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_600)),
                    file_info, progress, status_text,
                    ft.Row([
                        ft.ElevatedButton("Transcribir", on_click=lambda _: page.run_task(do_transcribe)),
                        ft.ElevatedButton("Analizar", on_click=lambda _: page.run_task(do_analyze)),
                    ]),
                    ft.Text("Transcripción:"), transcription, ft.Text("Análisis:"), analysis,
                ], scroll=ft.ScrollMode.AUTO, expand=True)),
        ], expand=True)
    )


async def main(page):
    page.title = "Meeting Transcriber"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1a1a2e"
    await main_app(page)


if __name__ == "__main__":
    ft.run(main=main)
