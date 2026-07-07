#!/usr/bin/env python3
"""
analyze.py — Análisis inteligente de transcripciones.
Extrae puntos clave, decisiones, action items, participantes, temas y sentimiento.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def load_transcription(input_path: str) -> str:
    """Cargar transcripción desde archivo."""
    path = Path(input_path)
    if not path.exists():
        print(f"ERROR: Archivo no encontrado: {input_path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Si es JSON (salida de transcribe.py), extraer el texto
    if input_path.endswith(".json"):
        try:
            data = json.loads(content)
            return data.get("text", content)
        except json.JSONDecodeError:
            pass

    return content


def extract_key_points(text: str) -> list:
    """Extraer puntos clave del texto."""
    points = []
    lines = text.split("\n")

    # Buscar marcadores de importancia
    importance_markers = [
        "importante", "clave", "clave", "punto clave", "esencial",
        "fundamental", "crucial", "critico", "prioridad", "urgente",
        "key", "important", "critical", "priority", "urgent",
        "must", "necesario", "requerido", "obligatorio",
    ]

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue

        # Por marcadores de importancia
        for marker in importance_markers:
            if marker in line_lower and len(line.strip()) > 20:
                points.append(line.strip())
                break

        # Por estructura: líneas que parecen títulos o encabezados
        if line.strip().startswith(("•", "-", "*", "→", "▸", "▪")):
            points.append(line.strip())

        # Por longitud: oraciones largas suelen ser más informativas
        words = line.split()
        if len(words) > 15 and line.strip()[-1] in ".!?":
            # Solo agregar si no está ya incluida
            if line.strip() not in points:
                points.append(line.strip())

    # Limitar a los más relevantes (máximo 15)
    return points[:15]


def extract_decisions(text: str) -> list:
    """Extraer decisiones tomadas."""
    decisions = []
    lines = text.split("\n")

    decision_markers = [
        "decidimos", "decidido", "acordamos", "acordado",
        "resuelto", "resolvimos", "aprobado", "aprobamos",
        "decisión", "decision", "acuerdo", "agreement",
        "concluimos", "concluido", "determinado", "determinamos",
        "we decided", "agreed", "resolved", "approved",
        "se decide", "se acordo", "se resolvio", "se aprobo",
    ]

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        for marker in decision_markers:
            if marker in line_lower and len(line.strip()) > 15:
                decisions.append(line.strip())
                break

    return decisions[:10]


def extract_action_items(text: str) -> list:
    """Extraer tareas y action items."""
    items = []
    lines = text.split("\n")

    action_markers = [
        "tarea", "task", "pendiente", "por hacer", "accion", "action",
        "responsable", "encargado", "asignado", "asignamos",
        "se debe", "hay que", "necesitamos", "tenemos que",
        "deadline", "fecha limite", "fecha", "plazo",
        "follow up", "seguimiento", "revisar", "verificar",
        "should", "must", "need to", "have to",
    ]

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        for marker in action_markers:
            if marker in line_lower and len(line.strip()) > 10:
                items.append(line.strip())
                break

    return items[:15]


def extract_participants(text: str) -> list:
    """Extraer nombres de participantes mencionados."""
    # Patrón simple: nombres propios (2+ palabras con mayúscula)
    # En reuniones, los participantes suelen mencionarse al inicio
    names = set()

    # Buscar patrones como "Juan Pérez", "María Lopez"
    pattern = r'\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b'
    matches = re.findall(pattern, text)

    for match in matches:
        # Filtrar palabras comunes que no son nombres
        common = {
            "El La", "Los Las", "Una Uno", "Este Esta", "Esa Esa",
            "Pero Como", "Mas Menos", "Sino Sobre", "Entre Hasta",
            "Hola Buenos", "Buenas Tardes", "Muchas Gracias",
        }
        if match not in common and len(match) > 4:
            names.add(match)

    return sorted(names)


def extract_topics(text: str) -> list:
    """Extraer temas principales tratados."""
    topics = []
    lines = text.split("\n")

    topic_markers = [
        "tema", "topic", "asunto", "punto", "agenda",
        "sobre", "acerca de", "respecto a", "en cuanto a",
        "discutimos", "hablamos de", "tratamos", "revisamos",
        "discussed", "talked about", "reviewed",
    ]

    for line in lines:
        line_lower = line.lower().strip()
        if not line_lower:
            continue
        for marker in topic_markers:
            if marker in line_lower and len(line.strip()) > 15:
                topics.append(line.strip())
                break

    return topics[:10]


def analyze_sentiment(text: str) -> dict:
    """Análisis básico de sentimiento."""
    positive_words = [
        "bien", "excelente", "genial", "perfecto", "bueno", "positivo",
        "acuerdo", "satisfecho", "contento", "feliz", "agradecido",
        "good", "great", "excellent", "perfect", "happy", "glad",
        "agreed", "satisfied", "positive", "wonderful", "amazing",
    ]
    negative_words = [
        "mal", "problema", "error", "difícil", "negativo", "preocupado",
        "insatisfecho", "frustrado", "molesto", "enojado", "urgente",
        "bad", "problem", "error", "difficult", "negative", "worried",
        "frustrated", "angry", "terrible", "awful", "wrong",
    ]

    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return {"sentiment": "neutral", "score": 0.5, "positive": 0, "negative": 0}

    score = pos_count / total
    if score > 0.6:
        sentiment = "positivo"
    elif score < 0.4:
        sentiment = "negativo"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "score": round(score, 2),
        "positive": pos_count,
        "negative": neg_count,
    }


def generate_executive_summary(text: str, decisions: list, action_items: list) -> str:
    """Generar resumen ejecutivo."""
    word_count = len(text.split())
    lines = text.split("\n")
    non_empty = [l.strip() for l in lines if l.strip()]

    parts = []
    parts.append(f"Reunion de {word_count} palabras.")

    if decisions:
        parts.append(f"Se tomaron {len(decisions)} decisiones principales.")

    if action_items:
        parts.append(f"Se identificaron {len(action_items)} tareas pendientes.")

    # Intentar extraer la primera oración significativa como contexto
    for line in non_empty[:5]:
        if len(line.split()) > 8:
            parts.append(f"Tema principal: {line[:100]}")
            break

    return " ".join(parts)


def analyze_full(text: str) -> dict:
    """Análisis completo de una transcripción."""
    print("Analizando transcripcion...")

    key_points = extract_key_points(text)
    decisions = extract_decisions(text)
    action_items = extract_action_items(text)
    participants = extract_participants(text)
    topics = extract_topics(text)
    sentiment = analyze_sentiment(text)
    summary = generate_executive_summary(text, decisions, action_items)

    return {
        "metadata": {
            "analyzed_at": datetime.now().isoformat(),
            "word_count": len(text.split()),
            "char_count": len(text),
        },
        "resumen_ejecutivo": summary,
        "puntos_clave": key_points,
        "decisiones": decisions,
        "action_items": action_items,
        "participantes": participants,
        "temas": topics,
        "sentimiento": sentiment,
    }


def main():
    parser = argparse.ArgumentParser(description="Analisis de transcripciones")
    sub = parser.add_subparsers(dest="command")

    # full
    p_full = sub.add_parser("full", help="Analisis completo")
    p_full.add_argument("--input", "-i", required=True, help="Archivo de transcripcion")
    p_full.add_argument("--output", "-o", default=None, help="Archivo JSON de salida")

    # extract
    p_extract = sub.add_parser("extract", help="Solo extraccion de partes clave")
    p_extract.add_argument("--input", "-i", required=True, help="Archivo de transcripcion")
    p_extract.add_argument("--output", "-o", default=None, help="Archivo JSON de salida")

    args = parser.parse_args()

    if args.command in ("full", "extract"):
        text = load_transcription(args.input)

        if args.command == "full":
            result = analyze_full(text)
        else:
            result = {
                "puntos_clave": extract_key_points(text),
                "decisiones": extract_decisions(text),
                "action_items": extract_action_items(text),
            }

        output = args.output
        if not output:
            stem = Path(args.input).stem
            output = f"{stem}_analisis.json"

        with open(output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\nAnalisis guardado: {output}")
        print(f"  Puntos clave: {len(result.get('puntos_clave', []))}")
        print(f"  Decisiones: {len(result.get('decisiones', []))}")
        print(f"  Action items: {len(result.get('action_items', []))}")
        if "participantes" in result:
            print(f"  Participantes: {len(result['participantes'])}")
        if "sentimiento" in result:
            print(f"  Sentimiento: {result['sentimiento']['sentiment']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
