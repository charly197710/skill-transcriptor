#!/usr/bin/env python3
"""
record.py — Grabación de audio desde micrófono.
Usa sounddevice + soundfile para grabar y guardar en WAV.
"""

import argparse
import os
import sys
import time
import threading
from pathlib import Path
from datetime import datetime

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print("ERROR: Requiere sounddevice y soundfile.")
    print("Instala con: uv pip install sounddevice soundfile")
    sys.exit(1)


def list_recordings(recordings_dir: str):
    """Listar grabaciones existentes."""
    path = Path(recordings_dir)
    if not path.exists():
        print(f"Directorio '{recordings_dir}' no existe.")
        return

    files = sorted(path.glob("*.wav"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not files:
        print("No hay grabaciones.")
        return

    print(f"{'ARCHIVO':<40} {'DURACIÓN':>10} {'FECHA':>20}")
    print("-" * 72)
    for f in files:
        try:
            info = sf.info(f)
            dur = f"{info.duration:.1f}s"
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"{f.name:<40} {dur:>10} {mtime:>20}")
        except Exception:
            print(f"{f.name:<40} {'?':>10} {'?':>20}")


def record_audio(
    output: str,
    duration: int = 0,
    sample_rate: int = 16000,
    channels: int = 1,
):
    """Grabar audio desde micrófono."""
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"🎙️  Grabando...")
    print(f"   Sample rate: {sample_rate} Hz")
    print(f"   Canales: {channels}")
    print(f"   Archivo: {output_path}")
    if duration > 0:
        print(f"   Duración: {duration} segundos")
    else:
        print("   Duración: indefinida (Ctrl+C para detener)")

    recorded_frames = []
    is_recording = True
    start_time = time.monotonic()

    def callback(indata, frames, time_info, status):
        if status:
            print(f"   ⚠️  {status}", file=sys.stderr)
        if is_recording:
            recorded_frames.append(indata.copy())

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            callback=callback,
        ):
            if duration > 0:
                print(f"\n   ⏱️  {duration}s restantes...")
                sd.sleep(int(duration * 1000))
            else:
                print("\n   Grabando... (Ctrl+C para detener)")
                while is_recording:
                    elapsed = int(time.monotonic() - start_time)
                    mins, secs = divmod(elapsed, 60)
                    print(f"\r   ⏱️  {mins:02d}:{secs:02d}", end="", flush=True)
                    sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n\n   ⏹️  Grabación detenida por usuario.")
    finally:
        is_recording = False

    if not recorded_frames:
        print("ERROR: No se grabó ningún audio.")
        sys.exit(1)

    # Concatenar frames y guardar
    import numpy as np

    audio_data = np.concatenate(recorded_frames, axis=0)
    sf.write(str(output_path), audio_data, sample_rate)

    elapsed = time.monotonic() - start_time
    file_size = output_path.stat().st_size / 1024
    print(f"\n✅ Guardado: {output_path}")
    print(f"   Duración: {elapsed:.1f}s | Tamaño: {file_size:.1f} KB")


def main():
    parser = argparse.ArgumentParser(description="Grabación de audio desde micrófono")
    sub = parser.add_subparsers(dest="command")

    # start
    p_start = sub.add_parser("start", help="Iniciar grabación")
    p_start.add_argument("--output", "-o", required=True, help="Archivo de salida (.wav)")
    p_start.add_argument(
        "--duration", "-d", type=int, default=0, help="Duración en segundos (0=indefinido)"
    )
    p_start.add_argument("--sample-rate", type=int, default=16000, help="Sample rate Hz")
    p_start.add_argument("--channels", type=int, default=1, help="Canales (1=mono)")

    # list
    p_list = sub.add_parser("list", help="Listar grabaciones")
    p_list.add_argument(
        "--dir", default="./recordings", help="Directorio de grabaciones"
    )

    args = parser.parse_args()

    if args.command == "start":
        record_audio(
            output=args.output,
            duration=args.duration,
            sample_rate=args.sample_rate,
            channels=args.channels,
        )
    elif args.command == "list":
        list_recordings(args.dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
