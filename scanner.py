import os
import re
from mutagen.easyid3 import EasyID3


def clean_filename(name: str) -> str:
    """
    Cleans song titles for use as LRC filenames.
    """

    if not name:
        return "Unknown Song"

    # Remove leading artist formatting
    name = re.sub(r"^.*?-\s*", "", name)

    # Remove bracketed junk
    name = re.sub(r"\(.*?\)", "", name)
    name = re.sub(r"\[.*?\]", "", name)

    # Remove invalid filename characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)

    # Collapse spaces
    name = re.sub(r"\s+", " ", name).strip()

    return name or "Unknown Song"


def generate_unique_lrc_path(root, clean_title):
    """
    Prevent duplicate filenames.
    """

    base_path = os.path.join(root, f"{clean_title}.lrc")

    if not os.path.exists(base_path):
        return base_path

    counter = 2

    while True:
        new_path = os.path.join(root, f"{clean_title} ({counter}).lrc")

        if not os.path.exists(new_path):
            return new_path

        counter += 1


def scan_music_folder(path):
    jobs = []

    for root, _, files in os.walk(path):

        for f in files:

            if not f.lower().endswith(".mp3"):
                continue

            mp3_path = os.path.join(root, f)
            base_name = os.path.splitext(f)[0]

            try:
                tags = EasyID3(mp3_path)

                title = tags.get("title", [base_name])[0]
                artist = tags.get("artist", ["Unknown Artist"])[0]
                album = tags.get("album", ["Unknown Album"])[0]

            except Exception:
                title = base_name
                artist = "Unknown Artist"
                album = "Unknown Album"

            clean_title = clean_filename(title)

            existing_lrc = os.path.join(root, f"{clean_title}.lrc")

            exists = os.path.exists(existing_lrc)

            if exists:
                lrc_path = existing_lrc
            else:
                lrc_path = generate_unique_lrc_path(root, clean_title)

            jobs.append({
                "mp3": mp3_path,
                "lrc": lrc_path,
                "title": clean_title,
                "artist": artist,
                "album": album,
                "exists": exists,
                "status": "done" if exists else "pending"
            })

    return jobs
