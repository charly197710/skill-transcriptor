"""
ui/results_page.py -- Pagina de resultados: transcripcion, analisis, resumen, traduccion.
"""

import flet as ft
import json
import os
import threading
from core.transcriber import Transcriber
from core.analyzer import Analyzer
from core.summarizer import Summarizer
from core.translator import Translator
from database.db import add_meeting


class ResultsPage:
    def __init__(self, page, state):
        self.page = page
        self.state = state
        self.transcriber = Transcriber()
        self.analyzer = Analyzer()
        self.summarizer = Summarizer()
        self.translator = Translator()

        self.progress_bar = ft.ProgressBar(visible=False, color=ft.Colors.DEEP_PURPLE_400)
        self.status_text = ft.Text("", size=14, color=ft.Colors.GREY_400)
        self.transcription_text = ft.Text("", size=14, selectable=True, color=ft.Colors.WHITE)
        self.analysis_text = ft.Text("", size=14, selectable=True, color=ft.Colors.WHITE)

        self.transcribe_btn = ft.ElevatedButton(
            "Transcribir", icon=ft.Icons.TRANSCRIBE,
            on_click=self._start_transcription,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )
        self.analyze_btn = ft.ElevatedButton(
            "Analizar", icon=ft.Icons.ANALYTICS,
            on_click=self._start_analysis, visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )
        self.summary_btn = ft.ElevatedButton(
            "Resumen MD", icon=ft.Icons.DESCRIPTION,
            on_click=self._generate_summary, visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )
        self.pdf_btn = ft.ElevatedButton(
            "Exportar PDF", icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self._generate_pdf, visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )
        self.mindmap_btn = ft.ElevatedButton(
            "Mapa Mental", icon=ft.Icons.ACCOUNT_TREE,
            on_click=self._generate_mindmap, visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )
        self.translate_btn = ft.ElevatedButton(
            "Traducir", icon=ft.Icons.TRANSLATE,
            on_click=self._translate_results, visible=False,
            style=ft.ButtonStyle(bgcolor=ft.Colors.DEEP_PURPLE_700, color=ft.Colors.WHITE),
        )

        self.lang_dropdown = ft.Dropdown(
            label="Idioma destino",
            value="en",
            width=150,
            options=[
                ft.dropdown.Option("en", "Ingles"),
                ft.dropdown.Option("es", "Espanol"),
                ft.dropdown.Option("fr", "Frances"),
                ft.dropdown.Option("de", "Aleman"),
                ft.dropdown.Option("pt", "Portugues"),
                ft.dropdown.Option("it", "Italiano"),
                ft.dropdown.Option("zh", "Chino"),
                ft.dropdown.Option("ja", "Japones"),
                ft.dropdown.Option("ko", "Coreano"),
            ],
        )

        self.tab_transcripcion = ft.Container(
            content=ft.Column([
                ft.Text("Transcripcion", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                ft.Container(content=ft.ListView([self.transcription_text], expand=True, spacing=5), padding=10),
            ], expand=True),
            expand=True,
            visible=True,
        )
        self.tab_analisis = ft.Container(
            content=ft.Column([
                ft.Text("Analisis", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                ft.Container(content=ft.ListView([self.analysis_text], expand=True, spacing=5), padding=10),
            ], expand=True),
            expand=True,
            visible=False,
        )

    def build(self):
        audio_path = self.state.get("current_audio", "")
        has_audio = bool(audio_path and os.path.exists(audio_path)) if audio_path else False
        file_info = f"Archivo: {audio_path}" if has_audio else "Sin archivo. Grabe o cargue un archivo primero."

        return ft.Column(
            [
                ft.Text("Resultados", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=5),
                ft.Text(file_info, size=14, color=ft.Colors.GREY_400),
                ft.Container(height=10),
                self.progress_bar,
                self.status_text,
                ft.Container(height=10),
                ft.Text("Acciones", size=16, weight=ft.FontWeight.W_600),
                ft.Row(
                    [self.transcribe_btn, self.analyze_btn, self.summary_btn, self.pdf_btn],
                    wrap=True, spacing=10,
                ),
                ft.Row(
                    [self.mindmap_btn, self.translate_btn, self.lang_dropdown],
                    wrap=True, spacing=10,
                ),
                ft.Container(height=15),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Row(
                    [
                        ft.TextButton("Transcripcion", icon=ft.Icons.TEXT_SNIPPET,
                            on_click=lambda _: self._show_tab(0),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                        ft.TextButton("Analisis", icon=ft.Icons.ANALYTICS,
                            on_click=lambda _: self._show_tab(1),
                            style=ft.ButtonStyle(color=ft.Colors.WHITE)),
                    ], spacing=5,
                ),
                ft.Container(height=5),
                self.tab_transcripcion,
                self.tab_analisis,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _show_tab(self, idx):
        self.tab_transcripcion.visible = (idx == 0)
        self.tab_analisis.visible = (idx == 1)
        self.page.update()

    def _set_status(self, msg, color=None):
        self.status_text.value = msg
        if color:
            self.status_text.color = color
        self.page.update()

    def _start_transcription(self, e):
        audio = self.state.get("current_audio")
        if not audio or not os.path.exists(audio):
            self._set_status("ERROR: No hay archivo de audio", ft.Colors.RED)
            return

        self.progress_bar.visible = True
        self.transcribe_btn.disabled = True
        self._set_status("Transcribiendo...")

        mode = self.state.get("mode", {}).get("mode", "local")
        model = self.state.get("mode", {}).get("whisper_model", "base")
        api_key = self.state.get("mode", {}).get("api_key", "")

        self.transcriber.set_mode(mode)
        if api_key:
            self.transcriber.set_api_key(api_key)

        def do_transcribe():
            try:
                result = self.transcriber.transcribe(
                    audio, whisper_model=model, output_format="json",
                    on_progress=lambda msg: self._set_status(msg),
                )
                self.state["current_transcription"] = result.get("output")
                self.transcription_text.value = result.get("text", "")
                self._set_status(f"Transcripcion completada ({result.get('language', '?')})", ft.Colors.GREEN_400)
                self.analyze_btn.visible = True
                self.translate_btn.visible = True
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            finally:
                self.progress_bar.visible = False
                self.transcribe_btn.disabled = False
                self.page.update()

        threading.Thread(target=do_transcribe, daemon=True).start()

    def _start_analysis(self, e):
        transcription = self.state.get("current_transcription")
        if not transcription:
            self._set_status("ERROR: No hay transcripcion", ft.Colors.RED)
            return

        self.progress_bar.visible = True
        self.analyze_btn.disabled = True
        self._set_status("Analizando...")

        def do_analyze():
            try:
                result = self.analyzer.analyze(transcription)
                self.state["current_analysis"] = result

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
                if result.get("participantes"):
                    lines.append(f"PARTICIPANTES: {', '.join(result['participantes'])}")
                if result.get("sentimiento"):
                    s = result["sentimiento"]
                    lines.append(f"SENTIMIENTO: {s.get('sentiment', 'neutral')}")

                self.analysis_text.value = "\n".join(lines)
                self._set_status("Analisis completado", ft.Colors.GREEN_400)
                self.summary_btn.visible = True
                self.pdf_btn.visible = True
                self.mindmap_btn.visible = True

                analysis_path = os.path.join(
                    r"C:\Users\WIN10\MeetingApp\output",
                    os.path.basename(transcription).replace("_transcripcion", "_analisis.json")
                )
                with open(analysis_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                add_meeting({
                    "title": os.path.basename(self.state.get("current_audio", "reunion")),
                    "audio_path": self.state.get("current_audio", ""),
                    "transcription_path": transcription,
                    "analysis_path": analysis_path,
                    "summary_path": "",
                    "mindmap_path": "",
                    "language": result.get("language", "auto"),
                    "mode": self.state.get("mode", {}).get("mode", "local"),
                    "duration_seconds": 0,
                })
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            finally:
                self.progress_bar.visible = False
                self.analyze_btn.disabled = False
                self.page.update()

        threading.Thread(target=do_analyze, daemon=True).start()

    def _generate_summary(self, e):
        analysis = self.state.get("current_analysis")
        if not analysis:
            self._set_status("ERROR: No hay analisis", ft.Colors.RED)
            return
        self._set_status("Generando resumen...")

        def do_summary():
            try:
                tmp_path = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp_analysis.json")
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
                output = self.summarizer.generate_summary(tmp_path, format="md")
                self.state["current_summary"] = output
                self._set_status(f"Resumen guardado: {output}", ft.Colors.GREEN_400)
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            self.page.update()

        threading.Thread(target=do_summary, daemon=True).start()

    def _generate_pdf(self, e):
        analysis = self.state.get("current_analysis")
        if not analysis:
            self._set_status("ERROR: No hay analisis", ft.Colors.RED)
            return
        self._set_status("Generando PDF...")

        def do_pdf():
            try:
                tmp_path = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp_analysis.json")
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
                output = self.summarizer.generate_summary(tmp_path, format="pdf")
                self._set_status(f"PDF guardado: {output}", ft.Colors.GREEN_400)
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            self.page.update()

        threading.Thread(target=do_pdf, daemon=True).start()

    def _generate_mindmap(self, e):
        analysis = self.state.get("current_analysis")
        if not analysis:
            self._set_status("ERROR: No hay analisis", ft.Colors.RED)
            return
        self._set_status("Generando mapa mental...")

        def do_mindmap():
            try:
                tmp_path = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp_analysis.json")
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)
                output = self.summarizer.generate_mindmap(tmp_path)
                self.state["current_mindmap"] = output
                self._set_status(f"Mapa mental guardado: {output}", ft.Colors.GREEN_400)
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            self.page.update()

        threading.Thread(target=do_mindmap, daemon=True).start()

    def _translate_results(self, e):
        analysis = self.state.get("current_analysis")
        if not analysis:
            self._set_status("ERROR: No hay analisis", ft.Colors.RED)
            return

        target_lang = self.lang_dropdown.value or "en"
        self._set_status(f"Traduciendo a {target_lang}...")

        def do_translate():
            try:
                tmp_path = os.path.join(r"C:\Users\WIN10\MeetingApp\output", "_temp_analysis.json")
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, ensure_ascii=False, indent=2)

                mode = self.state.get("mode", {}).get("mode", "local")
                api_key = self.state.get("mode", {}).get("api_key", "")
                self.translator.set_mode(mode)
                self.translator.set_api_key(api_key)
                output = self.translator.translate_analysis(tmp_path, target_lang=target_lang)

                with open(output, "r", encoding="utf-8") as f:
                    translated = json.load(f)

                lines = [f"TRADUCCION ({target_lang}):\n"]
                if translated.get("resumen_ejecutivo"):
                    lines.append(f"RESUMEN:\n{translated['resumen_ejecutivo']}\n")
                if translated.get("puntos_clave"):
                    lines.append("PUNTOS CLAVE:")
                    for i, p in enumerate(translated["puntos_clave"], 1):
                        lines.append(f"  {i}. {p}")

                self.analysis_text.value = "\n".join(lines)
                self._set_status(f"Traduccion completada: {output}", ft.Colors.GREEN_400)
            except Exception as ex:
                self._set_status(f"Error: {ex}", ft.Colors.RED)
            self.page.update()

        threading.Thread(target=do_translate, daemon=True).start()
