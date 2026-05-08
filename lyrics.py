import time
import requests


PROVIDERS = [
    "lrclib",
    "lyrics_ovh"
]



def fetch_lrclib(title, artist):

    url = "https://lrclib.net/api/get"

    params = {
        "track_name": title,
        "artist_name": artist
    }

    r = requests.get(url, params=params, timeout=15)

    if r.status_code != 200:
        return None

    data = r.json()

    return data.get("syncedLyrics")



def fetch_lyrics_ovh(title, artist):

    url = f"https://api.lyrics.ovh/v1/{artist}/{title}"

    r = requests.get(url, timeout=15)

    if r.status_code != 200:
        return None

    data = r.json()

    lyrics = data.get("lyrics")

    if lyrics:
        return lyrics

    return None



def fetch_lrc(title, artist):

    start = time.time()

    for provider in PROVIDERS:

        try:

            if provider == "lrclib":
                result = fetch_lrclib(title, artist)
            elif provider == "lyrics_ovh":
                result = fetch_lyrics_ovh(title, artist)
            else:
                result = None

            if result:
                latency = round(time.time() - start, 2)
                return result, latency

        except Exception:
            pass

    latency = round(time.time() - start, 2)

    return None, latency
