import logging
import signal
import time

from analyzer import analyze
from config import CHECK_INTERVAL
from db import init_db
from discord_bot import send_to_discord
from github_api import get_all_commits
from health import start_health_server
from storage import filter_unseen, log_run, record_commits, utc_now

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("codictator")

_running = True


def _stop(signum, _frame):
    global _running
    log.info("Received signal %s, shutting down after current cycle", signum)
    _running = False


def run_once() -> int:
    started = utc_now()
    try:
        commits = get_all_commits()
        unseen_ids = filter_unseen(c["id"] for c in commits)
        new_commits = [c for c in commits if c["id"] in unseen_ids]

        if new_commits:
            report = analyze(new_commits)
            send_to_discord(report)
            recorded = record_commits(new_commits)
            log.info("Sent report for %d new commits (%d recorded)", len(new_commits), recorded)
        else:
            log.info("No new commits")

        log_run(started, "ok", len(new_commits))
        return len(new_commits)
    except Exception as exc:
        log.exception("Run failed")
        log_run(started, "error", 0, str(exc))
        return 0


def main() -> None:
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    init_db()
    start_health_server()
    log.info("Co-Dictator starting, interval=%ds", CHECK_INTERVAL)

    while _running:
        run_once()
        for _ in range(CHECK_INTERVAL):
            if not _running:
                break
            time.sleep(1)

    log.info("Stopped")


if __name__ == "__main__":
    main()
