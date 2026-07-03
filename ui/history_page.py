"""
ui/history_page.py — Pagina de historial de reuniones.
"""

import flet as ft
import os
from database.db import get_meetings, delete_meeting


class HistoryPage:
    def __init__(self, page, state):
        self.page = page
        self.state = state

    def build(self):
        meetings = get_meetings()

        if not meetings:
            return ft.Column(
                [
                    ft.Text("Historial", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Divider(color=ft.Colors.GREY_800),
                    ft.Container(height=30),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.INBOX, size=60, color=ft.Colors.GREY_600),
                            ft.Text("Sin reuniones aun. Grabe o cargue un archivo.", size=16, color=ft.Colors.GREY_500),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                expand=True,
            )

        rows = []
        for m in meetings:
            title = m.get("title", "Sin titulo") or "Sin titulo"
            date = m.get("created_at", "")
            lang = m.get("language", "?")
            mode = m.get("mode", "?")

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(title, size=14, selectable=True)),
                        ft.DataCell(ft.Text(date[:16] if date else "?")),
                        ft.DataCell(ft.Text(lang)),
                        ft.DataCell(ft.Text(mode)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.PLAY_ARROW,
                                        icon_color=ft.Colors.GREEN_400,
                                        tooltip="Cargar",
                                        on_click=lambda e, m=m: self._load_meeting(m),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Eliminar",
                                        on_click=lambda e, m=m: self._delete_meeting(m),
                                    ),
                                ],
                                spacing=0,
                            )
                        ),
                    ]
                )
            )

        return ft.Column(
            [
                ft.Text("Historial de Reuniones", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=10),
                ft.Text(f"{len(meetings)} reuniones", size=14, color=ft.Colors.GREY_400),
                ft.Container(height=10),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Titulo", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Idioma", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Modo", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=rows,
                    border=ft.border.all(1, ft.Colors.GREY_800),
                    border_radius=8,
                    vertical_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
                    horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_800),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _load_meeting(self, meeting):
        """Cargar una reunion del historial."""
        audio = meeting.get("audio_path", "")
        if audio and os.path.exists(audio):
            self.state["current_audio"] = audio
            self.state["current_transcription"] = meeting.get("transcription_path")
            self.state["current_analysis"] = meeting.get("analysis_path")
            self.state["current_summary"] = meeting.get("summary_path")
            self.state["current_mindmap"] = meeting.get("mindmap_path")
            # Navegar a resultados
            self.page.update()
        else:
            print(f"Audio no encontrado: {audio}")

    def _delete_meeting(self, meeting):
        """Eliminar una reunion del historial."""
        delete_meeting(meeting["id"])
        self.page.update()
