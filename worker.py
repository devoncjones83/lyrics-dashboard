import time
            return

        job["status"] = "processing"

        push_update()

        try:

            lyrics, latency = fetch_lrc(
                job["title"],
                job["artist"]
            )

            job["latency"] = latency

            if not lyrics:

                job["status"] = "missing"
                job["retries"] = retries + 1

                record_failure()

                upsert_track(job)

                push_update()

                cooldown = min(300, 2 ** retries)
                time.sleep(cooldown)

                return

            with open(job["lrc"], "w", encoding="utf-8") as f:
                f.write(lyrics)

            job["status"] = "done"
            job["exists"] = True

            record_success(latency)

            upsert_track(job)

        except Exception as e:

            job["status"] = "error"
            job["last_error"] = str(e)
            job["retries"] = retries + 1

            record_failure()

            upsert_track(job)

        push_update()

    def loop():

        while True:

            pending = [
                j for j in state["jobs"]
                if j["status"] != "done"
            ]

            if pending:

                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
                    ex.map(process, pending)

            time.sleep(10)

    threading.Thread(target=loop, daemon=True).start()
