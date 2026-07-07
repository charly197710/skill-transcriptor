#!/usr/bin/env python3
"""
translate.py — Traductor simple usando translatepy (local) o API.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def translate_text(text, target="es", source="auto"):
    """Traducir texto usando translatepy (local)."""
    try:
        from translatepy import Translator
        tr = Translator()
        result = tr.translate(text, target)
        return result.result
    except ImportError:
        print("ERROR: translatepy no instalado. uv pip install translatepy")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR traduciendo: {e}")
        return text


def main():
    parser = argparse.ArgumentParser(description="Traducir texto")
    parser.add_argument("mode", choices=["local", "api"], default="local")
    parser.add_argument("--text", "-t", help="Texto a traducir")
    parser.add_argument("--input", "-i", help="Archivo de entrada")
    parser.add_argument("--output", "-o", help="Archivo de salida")
    parser.add_argument("--source", default="auto")
    parser.add_argument("--target", default="en")
    parser.add_argument("--api-key", help="API key (opcional)")

    args = parser.parse_args()

    if args.text:
        translated = translate_text(args.text, args.target, args.source)
        print(translated)
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        translated = translate_text(text, args.target, args.source)
        output = args.output or f"{Path(args.input).stem}_traducido.txt"
        with open(output, "w", encoding="utf-8") as f:
            f.write(translated)
        print(f"Traducción guardada: {output}")


if __name__ == "__main__":
    main()