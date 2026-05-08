from startup import validate_system

validate_system()
import os

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

from scanner import scan_music_folder
from worker import start_worker
from watcher import start_watcher
from metrics import get_metrics
from database import load_tracks

MUSIC_DIR = os.environ.get("MUSIC_DIR", "/music")

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent"
)

STATE = {
    "jobs": [],
    "errors": []
}


def push_update():
    """
    Push live dashboard updates to connected clients.
    """

    socketio.emit("update", {
        "jobs": STATE["jobs"],
        "errors": STATE["errors"],
        "metrics": get_metrics(
            len([
                j for j in STATE["jobs"]
                if j["status"] != "done"
            ])
        )
    })


def log_error(error):
    """
    Store and broadcast errors.
    """

    STATE["errors"].append(error)

    push_update()


@app.route("/")
def index():
    """
    Main dashboard page.
    """

    return render_template("index.html")


@app.route("/refresh")
def refresh():
    """
    Manual rescan endpoint.
    """

    scanned = scan_music_folder(MUSIC_DIR)

    existing = {
        j["mp3"] for j in STATE["jobs"]
    }

    for job in scanned:

        if job["mp3"] not in existing:
            STATE["jobs"].append(job)

    push_update()

    return jsonify({
        "status": "ok",
        "count": len(STATE["jobs"])
    })


@app.route("/api/jobs")
def jobs():
    """
    Return all jobs.
    """

    return jsonify(STATE["jobs"])


@app.route("/api/errors")
def errors():
    """
    Return all errors.
    """

    return jsonify(STATE["errors"])


@app.route("/api/metrics")
def metrics():
    """
    Dashboard metrics endpoint.
    """

    queue_depth = len([
        j for j in STATE["jobs"]
        if j["status"] != "done"
    ])

    return jsonify(
        get_metrics(queue_depth)
    )


if __name__ == "__main__":

    # Load persisted jobs from SQLite
    loaded = load_tracks()

    if loaded:
        STATE["jobs"] = loaded
    else:
        STATE["jobs"] = scan_music_folder(MUSIC_DIR)

    # Start worker queue
    start_worker(
        STATE,
        push_update
    )

    # Start filesystem watcher
    start_watcher(
        MUSIC_DIR,
        STATE,
        push_update
    )

    # Push initial dashboard state
    push_update()

    socketio.run(
        app,
        host="0.0.0.0",
        port=5001
    )
