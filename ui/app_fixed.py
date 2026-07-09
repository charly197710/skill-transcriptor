"""
ui/app_fixed.py — App async para Meeting Transcriber (Flet 0.85 compatible).
Usa page.run_task() con async/await para operaciones sin bloquear la UI.
"""

import flet as ft
import os
import json
import asyncio
from core.transcriber import Transcriber
from core.analyzer import Analyzer
from core.summarizer import Summarizer
from core.translator import Translator
from database.db import add_meeting


async def main_app(page):
    page.window.prevent_close = True

    state = {"current_audio": None, "current_transcription_path": None, "current_analysis": None}

    file_info = ft.Text("Sin archivo seleccionado", size=14, color=ft.Colors.GREY_500)
    status_text = ft.Text("Listo. Cargue un archivo de audio o video.", size=14, color=ft.Colors.GREY_400)
    progress_bar = ft.ProgressBar(visible=False, color=ft.Colors.DEEP_PURPLE_400)
    transcription_view = ft.TextField(multiline=True, min_lines=5, max_lines=10, 
                                      text_size=12, read_only=True, expand=True, bgcolor="#1e293b")
    analysis_view = ft.TextField(multiline=True, min_lines=5, max_lines=10,
                                  text_size=12, read_only=True, expand=True, bgcolor="#1e293b")

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
                size_mb = os.path.getsize(path) / (1024 * 1024)
                file_info.value = f"Archivo: {os.path.basename(path)} ({size_mb:.1f} MB)"
                file_info.color = ft.Colors.GREEN_400
                status_text.value = "Archivo cargado. Clic en Transcribir."
                status_text.color = ft.Colors.BLUE_400
                page.update()
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    async def do_transcribe():
        audio = state.get("current_audio")
        if not audio:
            return
        try:
            status_text.value = "Transcribiendo (20-60 segundos)..."
            status_text.color = ft.Colors.YELLOW_400
            progress_bar.visible = True
            page.update()

            result = await asyncio.to_thread(
                transcriber.transcribe, audio, whisper_model="tiny", output_format="json"
            )
            state["current_transcription_path"] = result.get("output")
            transcription_view.value = result.get("text", "(sin texto detectado)")
            status_text.value = f"Transcripción completada. Idioma: {result.get('language', '?')}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        finally:
            progress_bar.visible = False
            page.update()

    async def do_analyze():
        trans_path = state.get("current_transcription_path")
        if not trans_path:
            status_text.value = "Primero debes transcribir."
            page.update()
            return
        try:
            status_text.value = "Analizando..."
            status_text.color = ft.Colors.YELLOW_400
            progress_bar.visible = True
            page.update()

            result = await asyncio.to_thread(analyzer.analyze, trans_path)
            state["current_analysis"] = result

            lines = []
            if result.get("idea_principal"):
                lines.append(f"IDEA PRINCIPAL:\n{result['idea_principal']}")
            if result.get("nota_pulida"):
                lines.append(f"\nNOTA PULIDA:\n{result['nota_pulida']}")
            if result.get("puntos_clave"):
                lines.append("\nPUNTOS CLAVE:")
                for i, p in enumerate(result["puntos_clave"], 1):
                    lines.append(f"  {i}. {p}")
            if result.get("decisiones"):
                lines.append("\nDECISIONES:")
                for i, d in enumerate(result["decisiones"], 1):
                    lines.append(f"  {i}. {d}")
            if result.get("action_items"):
                lines.append("\nTAREAS PENDIENTES:")
                for i, a in enumerate(result["action_items"], 1):
                    lines.append(f"  {i}. {a}")

            analysis_view.value = "\n".join(lines) if lines else "(sin resultados)"
            status_text.value = "Análisis completado"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        finally:
            progress_bar.visible = False
            page.update()

    async def do_summary(fmt):
        if not state.get("current_analysis"):
            return
        try:
            status_text.value = f"Generando resumen {fmt}..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = r"C:\Users\WIN10\MeetingApp\output\_temp.json"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state["current_analysis"], f, ensure_ascii=False)

            output = summarizer.generate_summary(tmp, format=fmt)
            status_text.value = f"Resumen guardado: {os.path.basename(output)}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    async def do_mindmap():
        if not state.get("current_analysis"):
            return
        try:
            status_text.value = "Generando mapa mental..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = r"C:\Users\WIN10\MeetingApp\output\_temp.json"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state["current_analysis"], f, ensure_ascii=False)

            output = summarizer.generate_mindmap(tmp)
            status_text.value = f"Mapa guardado: {os.path.basename(output)}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    async def do_translate():
        if not state.get("current_analysis"):
            return
        try:
            status_text.value = "Traduciendo..."
            status_text.color = ft.Colors.YELLOW_400
            page.update()

            tmp = r"C:\Users\WIN10\MeetingApp\output\_temp.json"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(state["current_analysis"], f, ensure_ascii=False)

            output = translator.translate_analysis(tmp, target_lang="en")
            status_text.value = f"Traducción guardada: {os.path.basename(output)}"
            status_text.color = ft.Colors.GREEN_400
        except Exception as ex:
            status_text.value = f"Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()


    async def do_summary_md():
        await do_summary("md")

    async def do_summary_pdf():
        await do_summary("pdf")
    def on_transcribe(e):
        page.run_task(do_transcribe)

    def on_analyze(e):
        page.run_task(do_analyze)

    def on_close(e):
        page.window.destroy()

    page.add(
        ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("Meeting Transcriber", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor="#16213e",
                    padding=15,
                    alignment=ft.alignment.Alignment(0, 0),
                ),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Text("1. CARGAR ARCHIVO", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.ElevatedButton(
                                "Seleccionar archivo",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click=pick_file,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_600, color=ft.Colors.WHITE, padding=15),
                            ),
                            file_info,
                            ft.Divider(height=20, color=ft.Colors.GREY_800),
                            ft.Text("2. PROCESAR", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            progress_bar,
                            status_text,
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton("Transcribir", icon=ft.Icons.TRANSCRIBE, on_click=on_transcribe,
                                         style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Analizar", icon=ft.Icons.ANALYTICS, on_click=on_analyze,
                                         style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE)),
                                ],
                                spacing=10,
                            ),
                            ft.Divider(height=20, color=ft.Colors.GREY_800),
                            ft.Text("3. RESULTADOS", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Text("Transcripción:", size=12, color=ft.Colors.WHITE),
                            transcription_view,
                            ft.Text("Análisis:", size=12, color=ft.Colors.WHITE),
                            analysis_view,
                            ft.Divider(height=20, color=ft.Colors.GREY_800),
                            ft.Text("4. EXPORTAR", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Row(
                                controls=[
                                    ft.ElevatedButton("Resumen MD", icon=ft.Icons.DESCRIPTION,
                                        on_click=lambda _: page.run_task(do_summary_md),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("PDF", icon=ft.Icons.PICTURE_AS_PDF,
                                        on_click=lambda _: page.run_task(do_summary_pdf),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Mapa Mental", icon=ft.Icons.ACCOUNT_TREE,
                                        on_click=lambda _: page.run_task(do_mindmap),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                    ft.ElevatedButton("Traducir", icon=ft.Icons.TRANSLATE,
                                        on_click=lambda _: page.run_task(do_translate),
                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)),
                                ],
                                spacing=10,
                            ),
                            ft.Container(height=20),
                            ft.ElevatedButton("Salir", icon=ft.Icons.EXIT_TO_APP,
                                on_click=on_close,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                ),
            ],
            expand=True,
        )
    )
