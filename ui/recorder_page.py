"""
ui/recorder_page.py — Pagina de grabacion de audio.
"""

import flet as ft
from core.recorder import AudioRecorder
import threading


class RecorderPage:
    def __init__(self, page, state):
        self.page = page
        self.state = state
        self.recorder = AudioRecorder()
        self.timer_text = ft.Text("00:00", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        self.status_text = ft.Text("Listo para grabar", size=16, color=ft.Colors.GREY_400)
        self.is_recording = False
        self.timer_seconds = 0
        self._timer_thread = None

    def build(self):
        """Construir la pagina de grabacion."""

        self.record_btn = ft.FloatingActionButton(
            content=ft.Icon(ft.Icons.MIC, size=32),
            bgcolor=ft.Colors.RED_700,
            width=80,
            height=80,
            on_click=self._toggle_recording,
        )

        self.recording_indicator = ft.Container(
            visible=False,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, color=ft.Colors.RED, size=20),
                    ft.Text("GRABANDO", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                ],
                spacing=5,
            ),
        )

        self.duration_field = ft.TextField(
            label="Duracion (seg, 0=indefinido)",
            value="0",
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.last_file_text = ft.Text("", size=14, color=ft.Colors.GREY_500)

        self.go_results_btn = ft.ElevatedButton(
            "Ver resultados",
            icon=ft.Icons.ARROW_FORWARD,
            visible=False,
            on_click=self._go_to_results,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.DEEP_PURPLE_700,
                color=ft.Colors.WHITE,
            ),
        )

        recordings = self.recorder.get_recordings()
        recordings_list = ft.Column(
            [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.AUDIOTRACK),
                    title=ft.Text(r["name"]),
                    subtitle=ft.Text(f"{r['date']} -- {r['size_mb']} MB"),
                    on_click=lambda e, r=r: self._load_recording(r["path"]),
                )
                for r in recordings[:5]
            ],
            scroll=ft.ScrollMode.AUTO,
        )

        return ft.Column(
            [
                ft.Text("Grabar Audio", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Column(
                            [
                                self.recording_indicator,
                                ft.Container(height=10),
                                self.record_btn,
                                ft.Container(height=15),
                                self.timer_text,
                                ft.Container(height=10),
                                self.status_text,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=20),
                self.duration_field,
                ft.Container(height=10),
                self.last_file_text,
                self.go_results_btn,
                ft.Container(height=20),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Text("Grabaciones recientes", size=18, weight=ft.FontWeight.W_600),
                ft.Container(height=5),
                recordings_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=5,
        )

    def _toggle_recording(self, e):
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        try:
            duration = int(self.duration_field.value or "0")
        except ValueError:
            duration = 0

        try:
            output_file = self.recorder.start_recording(duration=duration)
            self.is_recording = True
            self.timer_seconds = 0
            self.state["current_audio"] = output_file

            self.record_btn.content = ft.Icon(ft.Icons.STOP, size=32)
            self.record_btn.bgcolor = ft.Colors.GREY_700
            self.recording_indicator.visible = True
            self.status_text.value = "Grabando audio..."
            self.status_text.color = ft.Colors.RED_400
            self.go_results_btn.visible = False

            self.page.update()

            self._timer_thread = threading.Thread(target=self._update_timer, daemon=True)
            self._timer_thread.start()

        except Exception as ex:
            self.status_text.value = f"Error: {ex}"
            self.status_text.color = ft.Colors.RED
            self.page.update()

    def _stop_recording(self):
        output = self.recorder.stop_recording()
        self.is_recording = False

        self.record_btn.content = ft.Icon(ft.Icons.MIC, size=32)
        self.record_btn.bgcolor = ft.Colors.RED_700
        self.recording_indicator.visible = False
        self.status_text.value = "Grabacion completada"
        self.status_text.color = ft.Colors.GREEN_400
        self.last_file_text.value = f"Archivo: {output}"
        self.go_results_btn.visible = bool(output)

        self.page.update()

    def _update_timer(self):
        import time
        while self.is_recording:
            self.timer_seconds += 1
            mins, secs = divmod(self.timer_seconds, 60)
            self.timer_text.value = f"{mins:02d}:{secs:02d}"
            try:
                self.page.update()
            except Exception:
                break
            time.sleep(1)

    def _go_to_results(self, e):
        if self.state.get("current_audio"):
            self.state["auto_process"] = True
            self.page.update()

    def _load_recording(self, path):
        self.state["current_audio"] = path
        self.status_text.value = f"Cargado: {path}"
        self.status_text.color = ft.Colors.BLUE_400
        self.go_results_btn.visible = True
        self.last_file_text.value = f"Archivo: {path}"
        self.page.update()
