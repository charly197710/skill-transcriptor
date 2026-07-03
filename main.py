"""
main.py -- Punto de entrada de Meeting Transcriber App.
"""

import flet as ft
from ui.app import main_app


def main(page):
    page.title = "Meeting Transcriber"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.spacing = 0
    page.window.width = 1100
    page.window.height = 750
    page.window.min_width = 900
    page.window.min_height = 600
    page.bgcolor = "#1a1a2e"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.DEEP_PURPLE)

    main_app(page)


if __name__ == "__main__":
    ft.app(target=main)
