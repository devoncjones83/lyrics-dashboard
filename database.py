import sqlite3
import os

DB_PATH = "/app/data.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        artist TEXT,
        path TEXT,
        lrc_path TEXT,
        status TEXT,
        retries INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def upsert_track(track):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tracks (title, artist, path, lrc_path, status, retries)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(path) DO UPDATE SET
        status=excluded.status,
        retries=excluded.retries
    """, (
        track.get("title"),
        track.get("artist"),
        track.get("path"),
        track.get("lrc_path"),
        track.get("status"),
        track.get("retries", 0)
    ))

    conn.commit()
    conn.close()
