import time

METRICS = {
    "songs_processed": 0,
    "songs_failed": 0,
    "total_latency": 0,
    "start_time": time.time(),
}


def record_success(latency):

    METRICS["songs_processed"] += 1
    METRICS["total_latency"] += latency



def record_failure():

    METRICS["songs_failed"] += 1



def get_metrics(queue_depth):

    runtime = max(time.time() - METRICS["start_time"], 1)

    processed = METRICS["songs_processed"]

    songs_per_minute = round(processed / (runtime / 60), 2)

    avg_latency = 0

    if processed:
        avg_latency = round(
            METRICS["total_latency"] / processed,
            2
        )

    success_rate = 0

    total_attempts = processed + METRICS["songs_failed"]

    if total_attempts:
        success_rate = round(
            (processed / total_attempts) * 100,
            2
        )

    return {
        "songs_per_minute": songs_per_minute,
        "success_rate": success_rate,
        "queue_depth": queue_depth,
        "avg_latency": avg_latency
    }
