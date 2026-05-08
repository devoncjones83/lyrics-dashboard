import sqlite3
        retries INTEGER DEFAULT 0,
        latency REAL DEFAULT 0,
        last_error TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)


def upsert_track(job):

    with lock:
        with conn:
            conn.execute(
                """
                INSERT INTO tracks (
                    mp3,
                    lrc,
                    title,
                    artist,
                    album,
                    status,
                    retries,
                    latency,
                    last_error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mp3)
                DO UPDATE SET
                    lrc=excluded.lrc,
                    title=excluded.title,
                    artist=excluded.artist,
                    album=excluded.album,
                    status=excluded.status,
                    retries=excluded.retries,
                    latency=excluded.latency,
                    last_error=excluded.last_error,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    job["mp3"],
                    job["lrc"],
                    job["title"],
                    job["artist"],
                    job["album"],
                    job["status"],
                    job.get("retries", 0),
                    job.get("latency", 0),
                    job.get("last_error", "")
                )
            )


def load_tracks():

    with lock:
        rows = conn.execute(
            "SELECT mp3,lrc,title,artist,album,status,retries,latency,last_error FROM tracks"
        ).fetchall()

    jobs = []

    for r in rows:
        jobs.append({
            "mp3": r[0],
            "lrc": r[1],
            "title": r[2],
            "artist": r[3],
            "album": r[4],
            "status": r[5],
            "retries": r[6],
            "latency": r[7],
            "last_error": r[8],
            "exists": r[5] == "done"
        })

    return jobs
