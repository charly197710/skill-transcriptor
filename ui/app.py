"""
ui/app.py -- App simple con una sola pagina.
"""

import flet as ft
import os
import json
import threading
from core.transcriber import Transcriber
from core.analyzer import Analyzer
from core.summarizer import Summarizer
from core.translator import Translator
from database.db import add_meeting


def main_app(page):
    page.window.prevent_close = True

    state = {"current_audio": None, "current_transcription": None, "current_analysis": None}

    status_text = ft.Text("Listo. Cargue un archivo de audio o video.", size=14, color=ft.Colors.GREY_400)
    progress_bar = ft.ProgressBar(visible=False, color=ft.Colors.DEEP_PURPLE_400)
    file_info = ft.Text("Sin archivo seleccionado", size=14, color=ft.Colors.GREY_500)
    transcription_text = ft.Text("", size=14, selectable=True, color=ft.Colors.WHITE)
    analysis_text = ft.Text("", size=14, selectable=True, color=ft.Colors.WHITE)

    transcriber = Transcriber(mode="local")
    analyzer = Analyzer()
    summarizer = Summarizer()
    translator = Translator()

    def pick_file(e):
        import tkinter as tk
        from tkinter import filedialog
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            filetypes = [("Audio/Video", "*.wav *.mp3 *.m4a *.ogg *.flac *.mp4 *.webm *.mkv *.avi *.mov"), ("Todos", "*.*")]
            path = filedialog.askopenfilename(filetypes=filetypes)
            root.destroy()
            if path and os.path.exists(path):
                state["current_audio"] = path
                file_info.value = f"Archivo: {os.path.basename(path)} ({os.path.getsize(path)/1024/1024:.1f} MB)"
                file_info.color = ft.Colors.GREEN_400
                status_text.value = "Archivo cargado. Clic en Transcribir para procesar."
                status_text.color = ft.Colors.BLUE_400
                page.update()
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    def do_transcribe():
        audio = state.get("current_audio")
        if not audio:
            return
        try:
            status_text.value = "Transcribiendo (esto toma 20-60 segundos)..."
            status_text.color = ft.Colors.YELLOW_400
            progress_bar.visible = True
            page.update()

            result = transcriber.transcribe(audio, whisper_model="tiny", output_format="json")
            state["current_transcription"] = result.get("output")
            transcription_text.value = result.get("text", "(sin texto detectado)")
            status_text.value = f"Transcripcion completada. Idioma: {result.get('language', '?')}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        finally:
            progress_bar.visible = False
            page.update()

    def on_transcribe(e):
        t = threading.Thread(target=do_transcribe, daemon=False)
        t.start()

    def do_analyze():
        trans = state.get("current_transcription")
        if not trans:
            return
        try:
            status_text.value = "Analizando..."
            status_text.color = ft.Colors.YELLOW_400
            progress_bar.visible = True
            page.update()

            result = analyzer.analyze(trans)
            state["current_analysis"] = result

            lines = []
            if result.get("resumen_ejecutivo"):
                lines.append(f"RESUMEN EJECUTIVO:\n{result['resumen_ejecutivo']}\n")
            if result.get("puntos_clave"):
                lines.append("PUNTOS CLAVE:")
                for i, p in enumerate(result["puntos_clave"], 1):
                    lines.append(f"  {i}. {p}")
                lines.append("")
            if result.get("decisiones"):
                lines.append("DECISIONES:")
                for i, d in enumerate(result["decisiones"], 1):
                    lines.append(f"  {i}. {d}")
                lines.append("")
            if result.get("action_items"):
                lines.append("TAREAS PENDIENTES:")
                for i, a in enumerate(result["action_items"], 1):
                    lines.append(f"  {i}. {a}")
                lines.append("")
            if result.get("sentimiento"):
                s = result["sentimiento"]
                lines.append(f"SENTIMIENTO: {s.get('sentiment', 'neutral')}")

            analysis_text.value = "\n".join(lines) if lines else "(sin resultados)"
            status_text.value = "Analisis completado"
            status_text.color = ft.Colors.GREEN_400

            try:
                add_meeting({
                    "title": os.path.basename(state.get("current_audio", "reunion")),
                    "audio_path": state.get("current_audio", ""),
                    "transcription_path": trans,
                    "analysis_path": "",
                    "summary_path": "",
                    "mindmap_path": "",
                    "language": result.get("language", "auto"),
                    "mode": "local",
                    "duration_seconds": 0,
                })
            except:
                pass
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        finally:
            progress_bar.visible = False
            page.update()

    def on_analyze(e):
        t = threading.Thread(target=do_analyze, daemon=False)
        t.start()

    def do_summary(fmt):
        analysis = state.get("current_analysis")
        if not analysis:
            return
        try:
            status_text.value = f"Generando resumen {fmt}..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp.json")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            output = summarizer.generate_summary(tmp, format=fmt)
            status_text.value = f"Resumen guardado: {output}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    def do_mindmap():
        analysis = state.get("current_analysis")
        if not analysis:
            return
        try:
            status_text.value = "Generando mapa mental..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp.json")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            output = summarizer.generate_mindmap(tmp)
            status_text.value = f"Mapa mental guardado: {output}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    def do_translate():
        analysis = state.get("current_analysis")
        if not analysis:
            return
        try:
            status_text.value = "Traduciendo..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp.json")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            output = translator.translate_analysis(tmp, target_lang="en")
            status_text.value = f"Traduccion guardada: {output}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    def on_close(e):
        page.window.destroy()

    page.add(
        ft.Column(
            [
                ft.Container(
                    content=ft.Text("Meeting Transcriber", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor="#16213e", padding=ft.padding.Padding(15, 12, 15, 12),
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("1. Cargar Archivo", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(height=5),
                            ft.ElevatedButton(
                                "Seleccionar archivo de audio o video",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=pick_file,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.DEEP_PURPLE_600,
                                    color=ft.Colors.WHITE,
                                    padding=ft.padding.Padding(15, 25, 15, 25),
                                ),
                            ),
                            file_info,
                            ft.Container(height=15),
                            ft.Text("2. Procesar", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(height=5),
                            progress_bar,
                            status_text,
                            ft.Container(height=10),
                            ft.Row(
                                [
                                    ft.ElevatedButton("Transcribir", icon=ft.Icons.TRANSCRIBE,
                                        on_click=on_transcribe,
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Analizar", icon=ft.Icons.ANALYTICS,
                                        on_click=on_analyze,
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE)),
                                ], spacing=10,
                            ),
                            ft.Container(height=15),
                            ft.Text("3. Resultados", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(height=5),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Transcripcion:", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                                    ft.Container(content=ft.ListView([transcription_text], expand=True, spacing=5, height=120), padding=5),
                                    ft.Text("Analisis:", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                                    ft.Container(content=ft.ListView([analysis_text], expand=True, spacing=5, height=120), padding=5),
                                ], expand=True),
                                bgcolor="#1e293b",
                                border_radius=10,
                                padding=15,
                                expand=True,
                            ),
                            ft.Container(height=15),
                            ft.Text("4. Exportar", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(height=5),
                            ft.Row(
                                [
                                    ft.ElevatedButton("Resumen MD", icon=ft.Icons.DESCRIPTION,
                                        on_click=lambda _: do_summary("md"),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Exportar PDF", icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=lambda _: do_summary("pdf"),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Mapa Mental", icon=ft.Icons.ACCOUNT_TREE,
                                        on_click=lambda _: do_mindmap(),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Traducir", icon=ft.Icons.TRANSLATE,
                                        on_click=lambda _: do_translate(),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                ], spacing=10, wrap=True,
                            ),
                            ft.Container(height=10),
                            ft.ElevatedButton("Salir", icon=ft.Icons.EXIT_TO_APP,
                                on_click=on_close,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                        spacing=5,
                    ),
                    padding=20,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )
    )
