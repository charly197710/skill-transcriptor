"""
ui/settings_page.py — Pagina de configuracion de la app.
"""

import flet as ft
import json
import os
from database.db import save_setting, get_setting

CONFIG_PATH = os.path.join(os.path.expanduser("~"), "MeetingApp", "config.json")


class SettingsPage:
    def __init__(self, page, state):
        self.page = page
        self.state = state

        # Campos de configuracion
        self.mode_dropdown = ft.Dropdown(
            label="Modo de transcripcion",
            value=get_setting("mode", "local"),
            width=250,
            options=[
                ft.dropdown.Option("local", "Local (sin internet)"),
                ft.dropdown.Option("api", "API (OpenRouter)"),
            ],
        )

        self.api_key_field = ft.TextField(
            label="OpenRouter API Key",
            value=get_setting("api_key", ""),
            password=True,
            can_reveal_password=True,
            width=400,
        )

        self.model_dropdown = ft.Dropdown(
            label="Modelo Whisper (local)",
            value=get_setting("whisper_model", "base"),
            width=250,
            options=[
                ft.dropdown.Option("tiny", "Tiny (rapido, menos preciso)"),
                ft.dropdown.Option("base", "Base (recomendado)"),
                ft.dropdown.Option("small", "Small (buen balance)"),
                ft.dropdown.Option("medium", "Medium (lento, preciso)"),
                ft.dropdown.Option("large-v3", "Large v3 (maxima precision)"),
            ],
        )

        self.lang_dropdown = ft.Dropdown(
            label="Idioma por defecto",
            value=get_setting("target_lang", "es"),
            width=250,
            options=[
                ft.dropdown.Option("es", "Espanol"),
                ft.dropdown.Option("en", "Ingles"),
                ft.dropdown.Option("auto", "Auto-detectar"),
            ],
        )

        self.output_dir_field = ft.TextField(
            label="Directorio de salida",
            value=get_setting("output_dir", os.path.join(os.path.expanduser("~"), "MeetingApp", "output")),
            width=400,
        )

        self.status_text = ft.Text("", size=14)

    def build(self):
        return ft.Column(
            [
                ft.Text("Configuracion", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Container(height=15),

                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("Motor de Transcripcion", size=18, weight=ft.FontWeight.W_600),
                                ft.Container(height=10),
                                self.mode_dropdown,
                                self.model_dropdown,
                            ],
                            spacing=10,
                        ),
                        padding=20,
                    ),
                    bgcolor="#1e293b",
                ),

                ft.Container(height=15),

                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("API (OpenRouter)", size=18, weight=ft.FontWeight.W_600),
                                ft.Container(height=10),
                                self.api_key_field,
                                ft.Text(
                                    "Obtener key: https://openrouter.ai/keys",
                                    size=12, color=ft.Colors.GREY_500,
                                ),
                            ],
                            spacing=10,
                        ),
                        padding=20,
                    ),
                    bgcolor="#1e293b",
                ),

                ft.Container(height=15),

                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("General", size=18, weight=ft.FontWeight.W_600),
                                ft.Container(height=10),
                                self.lang_dropdown,
                                self.output_dir_field,
                            ],
                            spacing=10,
                        ),
                        padding=20,
                    ),
                    bgcolor="#1e293b",
                ),

                ft.Container(height=20),

                ft.ElevatedButton(
                    "Guardar configuracion",
                    icon=ft.Icons.SAVE,
                    on_click=self._save_settings,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_700,
                        color=ft.Colors.WHITE,
                        padding=ft.padding.Padding(15, 30, 15, 30),
                    ),
                ),

                ft.Container(height=10),
                self.status_text,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _save_settings(self, e):
        """Guardar configuracion."""
        save_setting("mode", self.mode_dropdown.value)
        save_setting("api_key", self.api_key_field.value or "")
        save_setting("whisper_model", self.model_dropdown.value)
        save_setting("target_lang", self.lang_dropdown.value)
        save_setting("output_dir", self.output_dir_field.value)

        # Actualizar estado
        self.state["mode"] = {
            "mode": self.mode_dropdown.value,
            "api_key": self.api_key_field.value or "",
            "whisper_model": self.model_dropdown.value,
            "target_lang": self.lang_dropdown.value,
        }

        self.status_text.value = "Configuracion guardada correctamente"
        self.status_text.color = ft.Colors.GREEN_400
        self.page.update()
