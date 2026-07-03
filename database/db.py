"""
database/db.py — Base de datos SQLite para historial de reuniones.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


DB_PATH = Path(r"C:\Users\WIN10\MeetingApp\output\meeting_history.db")


def get_db():
    """Obtener conexión a la base de datos."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializar las tablas."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            audio_path TEXT,
            transcription_path TEXT,
            analysis_path TEXT,
            summary_path TEXT,
            mindmap_path TEXT,
            language TEXT,
            mode TEXT,
            duration_seconds REAL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_meeting(meeting_data: dict) -> int:
    """Agregar una reunión al historial."""
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO meetings (title, audio_path, transcription_path, analysis_path,
                              summary_path, mindmap_path, language, mode, duration_seconds)
        VALUES (:title, :audio_path, :transcription_path, :analysis_path,
                :summary_path, :mindmap_path, :language, :mode, :duration_seconds)
    """, meeting_data)
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    return meeting_id


def get_meetings(limit=50):
    """Obtener lista de reuniones."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM meetings ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_meeting(meeting_id: int):
    """Obtener una reunión por ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_meeting(meeting_id: int):
    """Eliminar una reunión."""
    conn = get_db()
    conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()


def save_setting(key: str, value: str):
    """Guardar una configuración."""
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_setting(key: str, default=None):
    """Obtener una configuración."""
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


# Inicializar al importar
init_db()
