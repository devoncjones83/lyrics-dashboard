import sqlite3
import os

DB_PATH = "/app/data.db"


SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    path TEXT UNIQUE,
    lrc_path TEXT,
    status TEXT,
    retries INTEGER DEFAULT 0
);
"""


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    conn.close()


def validate_schema():
    """Ensures DB is usable at runtime."""
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, title, artist, path FROM tracks LIMIT 1")
    except Exception as e:
        raise RuntimeError(f"DB schema invalid: {e}")

    conn.close()


def load_tracks():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT title, artist, path, lrc_path, status, retries FROM tracks")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "title": r[0],
            "artist": r[1],
            "path": r[2],
            "lrc_path": r[3],
            "status": r[4],
            "retries": r[5],
        }
        for r in rows
    ]


def upsert_track(track):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tracks (title, artist, path, lrc_path, status, retries)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(path) DO UPDATE SET
        status=excluded.status,
        retries=excluded.retries,
        lrc_path=excluded.lrc_path
    """, (
        track["title"],
        track["artist"],
        track["path"],
        track.get("lrc_path"),
        track.get("status"),
        track.get("retries", 0)
    ))

    conn.commit()
    conn.close()
