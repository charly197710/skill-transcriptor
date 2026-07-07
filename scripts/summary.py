#!/usr/bin/env python3
"""
summary.py — Generador de resúmenes en múltiples formatos.
TXT, Markdown y PDF.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_analysis(input_path: str) -> dict:
    """Cargar análisis JSON."""
    path = Path(input_path)
    if not path.exists():
        print(f"ERROR: Archivo no encontrado: {input_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_txt(analysis: dict, lang: str = "es") -> str:
    """Generar resumen en texto plano."""
    lines = []
    lines.append("=" * 60)
    lines.append("RESUMEN DE REUNION")
    lines.append("=" * 60)
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Resumen ejecutivo
    lines.append("--- RESUMEN EJECUTIVO ---")
    lines.append(analysis.get("resumen_ejecutivo", "No disponible"))
    lines.append("")

    # Puntos clave
    puntos = analysis.get("puntos_clave", [])
    if puntos:
        lines.append("--- PUNTOS CLAVE ---")
        for i, p in enumerate(puntos, 1):
            lines.append(f"  {i}. {p}")
        lines.append("")

    # Decisiones
    decisiones = analysis.get("decisiones", [])
    if decisiones:
        lines.append("--- DECISIONES TOMADAS ---")
        for i, d in enumerate(decisiones, 1):
            lines.append(f"  {i}. {d}")
        lines.append("")

    # Action items
    actions = analysis.get("action_items", [])
    if actions:
        lines.append("--- TAREAS PENDIENTES ---")
        for i, a in enumerate(actions, 1):
            lines.append(f"  {i}. {a}")
        lines.append("")

    # Participantes
    participantes = analysis.get("participantes", [])
    if participantes:
        lines.append("--- PARTICIPANTES ---")
        for p in participantes:
            lines.append(f"  - {p}")
        lines.append("")

    # Sentimiento
    sentimiento = analysis.get("sentimiento", {})
    if sentimiento:
        lines.append("--- SENTIMIENTO GENERAL ---")
        lines.append(f"  Tono: {sentimiento.get('sentiment', 'neutral')}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("Fin del resumen")
    return "\n".join(lines)


def generate_md(analysis: dict, lang: str = "es") -> str:
    """Generar resumen en Markdown."""
    lines = []
    lines.append("# Resumen de Reunion")
    lines.append(f"\n*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    # Resumen ejecutivo
    lines.append("## Resumen Ejecutivo")
    lines.append(f"\n{analysis.get('resumen_ejecutivo', 'No disponible')}")
    lines.append("")

    # Puntos clave
    puntos = analysis.get("puntos_clave", [])
    if puntos:
        lines.append("## Puntos Clave")
        for p in puntos:
            lines.append(f"- {p}")
        lines.append("")

    # Decisiones
    decisiones = analysis.get("decisiones", [])
    if decisiones:
        lines.append("## Decisiones Tomadas")
        for d in decisiones:
            lines.append(f"- ✅ {d}")
        lines.append("")

    # Action items
    actions = analysis.get("action_items", [])
    if actions:
        lines.append("## Tareas Pendientes")
        lines.append("")
        lines.append("| # | Tarea |")
        lines.append("|---|-------|")
        for i, a in enumerate(actions, 1):
            lines.append(f"| {i} | {a} |")
        lines.append("")

    # Participantes
    participantes = analysis.get("participantes", [])
    if participantes:
        lines.append("## Participantes")
        for p in participantes:
            lines.append(f"- **{p}**")
        lines.append("")

    # Sentimiento
    sentimiento = analysis.get("sentimiento", {})
    if sentimiento:
        emoji = {"positivo": "🟢", "negativo": "🔴", "neutral": "🟡"}.get(
            sentimiento.get("sentiment", "neutral"), "🟡"
        )
        lines.append("## Sentimiento General")
        lines.append(f"\n{emoji} Tono: **{sentimiento.get('sentiment', 'neutral')}**")
        lines.append("")

    # Temas
    temas = analysis.get("temas", [])
    if temas:
        lines.append("## Temas Tratados")
        for t in temas:
            lines.append(f"- {t}")
        lines.append("")

    lines.append("---")
    lines.append("*Generado por Meeting Transcriber*")
    return "\n".join(lines)


def generate_pdf(analysis: dict, output_path: str, include_transcription: bool = False):
    """Generar resumen en PDF usando fpdf2."""
    try:
        from fpdf import FPDF
    except ImportError:
        print("ERROR: fpdf2 no instalado.")
        print("Instala con: uv pip install fpdf2")
        sys.exit(1)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Resumen de Reunion", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(2)

    # Fecha
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    # Resumen ejecutivo
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Resumen Ejecutivo", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, analysis.get("resumen_ejecutivo", "No disponible"))
    pdf.ln(5)

    # Puntos clave
    puntos = analysis.get("puntos_clave", [])
    if puntos:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Puntos Clave", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for i, p in enumerate(puntos, 1):
            text = f"{i}. {p}"
            pdf.multi_cell(0, 5, text)
        pdf.ln(3)

    # Decisiones
    decisiones = analysis.get("decisiones", [])
    if decisiones:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Decisiones Tomadas", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for i, d in enumerate(decisiones, 1):
            pdf.multi_cell(0, 5, f"{i}. {d}")
        pdf.ln(3)

    # Action items
    actions = analysis.get("action_items", [])
    if actions:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Tareas Pendientes", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for i, a in enumerate(actions, 1):
            pdf.multi_cell(0, 5, f"{i}. {a}")
        pdf.ln(3)

    # Participantes
    participantes = analysis.get("participantes", [])
    if participantes:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Participantes", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for p in participantes:
            pdf.cell(0, 5, f"- {p}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Sentimiento
    sentimiento = analysis.get("sentimiento", {})
    if sentimiento:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Sentimiento General", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, f"Tono: {sentimiento.get('sentiment', 'neutral')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 10, "Generado por Meeting Transcriber", align="C")

    pdf.output(output_path)
    print(f"PDF guardado: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Generador de resumenes")
    sub = parser.add_subparsers(dest="command")

    # txt
    p_txt = sub.add_parser("txt", help="Resumen en texto plano")
    p_txt.add_argument("--input", "-i", required=True, help="Archivo JSON de analisis")
    p_txt.add_argument("--output", "-o", default=None, help="Archivo de salida")
    p_txt.add_argument("--lang", default="es", help="Idioma (default: es)")

    # md
    p_md = sub.add_parser("md", help="Resumen en Markdown")
    p_md.add_argument("--input", "-i", required=True, help="Archivo JSON de analisis")
    p_md.add_argument("--output", "-o", default=None, help="Archivo de salida")
    p_md.add_argument("--lang", default="es", help="Idioma (default: es)")

    # pdf
    p_pdf = sub.add_parser("pdf", help="Resumen en PDF")
    p_pdf.add_argument("--input", "-i", required=True, help="Archivo JSON de analisis")
    p_pdf.add_argument("--output", "-o", default=None, help="Archivo de salida")
    p_pdf.add_argument("--lang", default="es", help="Idioma (default: es)")
    p_pdf.add_argument("--include-transcription", action="store_true", help="Incluir transcripcion completa")

    args = parser.parse_args()

    if args.command in ("txt", "md", "pdf"):
        analysis = load_analysis(args.input)

        if args.command == "txt":
            output = args.output or "resumen.txt"
            content = generate_txt(analysis, args.lang)
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Resumen TXT guardado: {output}")

        elif args.command == "md":
            output = args.output or "resumen.md"
            content = generate_md(analysis, args.lang)
            with open(output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Resumen MD guardado: {output}")

        elif args.command == "pdf":
            output = args.output or "resumen.pdf"
            generate_pdf(analysis, output, getattr(args, "include_transcription", False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
