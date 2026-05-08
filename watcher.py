from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from scanner import scan_music_folder


class MusicHandler(FileSystemEventHandler):

    def __init__(self, music_dir, state, push_update):
        self.music_dir = music_dir
        self.state = state
        self.push_update = push_update

    def on_created(self, event):

        if event.is_directory:
            return

        if not event.src_path.lower().endswith(".mp3"):
            return

        jobs = scan_music_folder(self.music_dir)

        existing = {
            j["mp3"] for j in self.state["jobs"]
        }

        for job in jobs:

            if job["mp3"] not in existing:
                self.state["jobs"].append(job)

        self.push_update()



def start_watcher(music_dir, state, push_update):

    event_handler = MusicHandler(
        music_dir,
        state,
        push_update
    )

    observer = Observer()

    observer.schedule(
        event_handler,
        music_dir,
        recursive=True
    )

    observer.start()
