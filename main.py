"""
main.py — Punto de entrada de Meeting Transcriber App.
Versión async para Flet 0.85 con page.run_task().

Para Windows con ventana gráfica:
    uv run python main.py

Para servidor web (acceso desde navegador):
    uv run python main.py --web
"""

import flet as ft
from ui.app_fixed import main_app
import argparse


async def main(page):
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

    await main_app(page)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Run as web app")
    args = parser.parse_args()

    if args.web:
        # Servidor web - accesible desde http://localhost:8000
        ft.run(main=main, host="0.0.0.0", port=8000)
    else:
        # App de escritorio
        ft.run(main=main)
