#!/usr/bin/env python3
"""
mindmap.py — Generador de mapas mentales HTML interactivos.
Crea un archivo HTML con CSS y JS integrado (sin dependencias externas).
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


def generate_mindmap_html(analysis: dict) -> str:
    """Generar HTML del mapa mental interactivo."""
    title = "Mapa Mental - Resumen de Reunion"
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Preparar datos
    executive = analysis.get("resumen_ejecutivo", "Sin resumen")
    key_points = analysis.get("puntos_clave", [])
    decisions = analysis.get("decisiones", [])
    actions = analysis.get("action_items", [])
    participants = analysis.get("participantes", [])
    topics = analysis.get("temas", [])
    sentiment = analysis.get("sentimiento", {})

    sentiment_color = {
        "positivo": "#22c55e",
        "negativo": "#ef4444",
        "neutral": "#eab308",
    }.get(sentiment.get("sentiment", "neutral"), "#eab308")

    sentiment_label = sentiment.get("sentiment", "neutral")

    # Construir items HTML
    def items_html(items, icon="•"):
        if not items:
            return '<li class="empty">No identificados</li>'
        return "".join(f"<li>{icon} {_escape_html(i)}</li>" for i in items)

    # Nodos del mapa mental
    nodes_html = f"""
    <div class="mindmap">
        <div class="center-node">
            <span class="center-title">Reunion</span>
            <span class="center-date">{date}</span>
        </div>

        <div class="branch branch-top">
            <div class="branch-label">Resumen</div>
            <div class="branch-content">
                <p>{_escape_html(executive)}</p>
            </div>
        </div>

        <div class="branch branch-right">
            <div class="branch-label">Puntos Clave</div>
            <div class="branch-content">
                <ul>{items_html(key_points, "&#10003;")}</ul>
            </div>
        </div>

        <div class="branch branch-bottom-right">
            <div class="branch-label">Decisiones</div>
            <div class="branch-content">
                <ul>{items_html(decisions, "&#9989;")}</ul>
            </div>
        </div>

        <div class="branch branch-bottom">
            <div class="branch-label">Tareas</div>
            <div class="branch-content">
                <ul>{items_html(actions, "&#9744;")}</ul>
            </div>
        </div>

        <div class="branch branch-bottom-left">
            <div class="branch-label">Participantes</div>
            <div class="branch-content">
                <ul>{items_html(participants, "&#128100;")}</ul>
            </div>
        </div>

        <div class="branch branch-left">
            <div class="branch-label">Temas</div>
            <div class="branch-content">
                <ul>{items_html(topics, "&#128196;")}</ul>
            </div>
        </div>

        <div class="branch branch-top-left">
            <div class="branch-label">Sentimiento</div>
            <div class="branch-content sentiment" style="border-color: {sentiment_color}">
                <span class="sentiment-dot" style="background: {sentiment_color}"></span>
                <strong>{sentiment_label.capitalize()}</strong>
            </div>
        </div>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            font-size: 1.8rem;
            margin-bottom: 5px;
            color: #f1f5f9;
        }}
        .subtitle {{
            text-align: center;
            color: #94a3b8;
            margin-bottom: 30px;
            font-size: 0.9rem;
        }}
        .mindmap {{
            position: relative;
            width: 100%;
            min-height: 700px;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-template-rows: 1fr 1fr 1fr;
            gap: 15px;
            padding: 20px;
        }}
        .center-node {{
            grid-column: 2;
            grid-row: 2;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 25px;
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            z-index: 10;
        }}
        .center-node:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 40px rgba(99, 102, 241, 0.5);
        }}
        .center-title {{
            font-size: 1.5rem;
            font-weight: bold;
            color: white;
        }}
        .center-date {{
            font-size: 0.8rem;
            color: #c7d2fe;
            margin-top: 5px;
        }}
        .branch {{
            background: rgba(30, 41, 59, 0.8);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(148, 163, 184, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
            overflow: hidden;
        }}
        .branch:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            border-color: rgba(99, 102, 241, 0.3);
        }}
        .branch-top {{ grid-column: 2; grid-row: 1; }}
        .branch-right {{ grid-column: 3; grid-row: 2; }}
        .branch-bottom-right {{ grid-column: 3; grid-row: 3; }}
        .branch-bottom {{ grid-column: 2; grid-row: 3; }}
        .branch-bottom-left {{ grid-column: 1; grid-row: 3; }}
        .branch-left {{ grid-column: 1; grid-row: 2; }}
        .branch-top-left {{ grid-column: 1; grid-row: 1; }}
        .branch-label {{
            font-size: 0.85rem;
            font-weight: bold;
            color: #a78bfa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }}
        .branch-content {{
            font-size: 0.85rem;
            line-height: 1.5;
            color: #cbd5e1;
        }}
        .branch-content ul {{
            list-style: none;
            padding: 0;
        }}
        .branch-content li {{
            padding: 3px 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.05);
        }}
        .branch-content li:last-child {{
            border-bottom: none;
        }}
        .branch-content li.empty {{
            color: #64748b;
            font-style: italic;
        }}
        .sentiment {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px;
            border-radius: 8px;
            border: 2px solid;
        }}
        .sentiment-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #64748b;
            font-size: 0.8rem;
        }}
        /* Conector visual */
        .connector {{
            position: absolute;
            background: rgba(99, 102, 241, 0.2);
            z-index: 1;
        }}
        /* Responsive */
        @media (max-width: 768px) {{
            .mindmap {{
                grid-template-columns: 1fr;
                grid-template-rows: auto;
            }}
            .center-node {{ grid-column: 1; grid-row: 1; }}
            .branch-top {{ grid-column: 1; grid-row: 2; }}
            .branch-right {{ grid-column: 1; grid-row: 3; }}
            .branch-bottom-right {{ grid-column: 1; grid-row: 4; }}
            .branch-bottom {{ grid-column: 1; grid-row: 5; }}
            .branch-bottom-left {{ grid-column: 1; grid-row: 6; }}
            .branch-left {{ grid-column: 1; grid-row: 7; }}
            .branch-top-left {{ grid-column: 1; grid-row: 8; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mapa Mental</h1>
        <p class="subtitle">Resumen de Reunion &mdash; {date}</p>
        {nodes_html}
        <p class="footer">Generado por Meeting Transcriber &bull; Clic en las ramas para interactuar</p>
    </div>
    <script>
        // Interactividad: expandir/colapsar ramas
        document.querySelectorAll('.branch').forEach(branch => {{
            branch.addEventListener('click', function() {{
                this.classList.toggle('expanded');
            }});
        }});

        // Animación de entrada
        document.addEventListener('DOMContentLoaded', () => {{
            const branches = document.querySelectorAll('.branch');
            branches.forEach((b, i) => {{
                b.style.opacity = '0';
                b.style.transform = 'translateY(20px)';
                setTimeout(() => {{
                    b.style.transition = 'opacity 0.5s, transform 0.5s';
                    b.style.opacity = '1';
                    b.style.transform = 'translateY(0)';
                }}, 100 + i * 100);
            }});
        }});
    </script>
</body>
</html>"""

    return html


def _escape_html(text: str) -> str:
    """Escapar caracteres HTML especiales."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    parser = argparse.ArgumentParser(description="Generador de mapas mentales HTML")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="Generar mapa mental")
    p_gen.add_argument("--input", "-i", required=True, help="Archivo JSON de analisis")
    p_gen.add_argument("--output", "-o", default=None, help="Archivo HTML de salida")

    args = parser.parse_args()

    if args.command == "generate":
        analysis = load_analysis(args.input)
        html = generate_mindmap_html(analysis)

        output = args.output or "mapa_mental.html"
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Mapa mental guardado: {output}")
        print(f"  Abrir en navegador para visualizar.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
