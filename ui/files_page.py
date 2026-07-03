"""
ui/files_page.py -- Pagina para cargar archivos de audio/video.
"""

import flet as ft
import os


class FilesPage:
    def __init__(self, page, state):
        self.page = page
        self.state = state
        self.selected_file_text = ft.Text("Ningun archivo seleccionado", size=14, color=ft.Colors.GREY_500)
        self.file_info_text = ft.Text("", size=13, color=ft.Colors.GREY_400)
        self.status_text = ft.Text("", size=14, color=ft.Colors.GREY_400)
        self.go_results_btn = ft.ElevatedButton(
            "Procesar archivo",
            icon=ft.Icons.PLAY_ARROW,
            visible=False,
            on_click=self._go_to_results,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.DEEP_PURPLE_700,
                color=ft.Colors.WHITE,
            ),
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("Cargar Archivo", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=15),

                # Boton grande para seleccionar archivo
                ft.ElevatedButton(
                    "Seleccionar archivo de audio o video",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=self._pick_file,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.DEEP_PURPLE_600,
                        color=ft.Colors.WHITE,
                        padding=ft.padding.Padding(20, 40, 20, 40),
                        text_style=ft.TextStyle(size=16, weight=ft.FontWeight.BOLD),
                    ),
                    width=400,
                    height=60,
                ),

                ft.Container(height=10),

                ft.Text(
                    "Formatos: .wav, .mp3, .m4a, .ogg, .flac, .mp4, .webm, .mkv, .avi, .mov",
                    size=13, color=ft.Colors.GREY_500,
                ),

                ft.Container(height=25),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=10),

                ft.Text("Archivo seleccionado:", size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                self.selected_file_text,
                self.file_info_text,
                ft.Container(height=15),
                self.go_results_btn,
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _pick_file(self, e):
        import tkinter as tk
        from tkinter import filedialog
        try:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            filetypes = [
                ("Audio/Video", "*.wav *.mp3 *.m4a *.ogg *.flac *.mp4 *.webm *.mkv *.avi *.mov"),
                ("Todos", "*.*"),
            ]
            path = filedialog.askopenfilename(filetypes=filetypes)
            root.destroy()
            if path and os.path.exists(path):
                self._on_file_selected(path)
        except Exception as ex:
            self.status_text.value = f"Error: {ex}"
            self.page.update()

    def _on_file_selected(self, path):
        if path and os.path.exists(path):
            self.state["current_audio"] = path
            fname = os.path.basename(path)
            self.selected_file_text.value = f"Archivo: {fname}"
            self.selected_file_text.color = ft.Colors.GREEN_400

            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.file_info_text.value = f"Tamano: {size_mb:.1f} MB"
            self.go_results_btn.visible = True
            self.page.update()

    def _go_to_results(self, e):
        if self.state.get("current_audio"):
            pass
