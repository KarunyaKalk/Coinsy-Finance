import logging
import threading
import time
from typing import Optional
from app.db.session import SessionLocal
from app.services.insights_service import run_batch_insights_job

logger = logging.getLogger(__name__)

class InsightsScheduler:
    """
    Background batch job scheduler for pre-computing predictions and daily tips.
    Runs asynchronously off the main API loop to ensure endpoints serve insights instantly.
    """
    def __init__(self, interval_seconds: int = 86400):
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _worker(self):
        logger.info(f"InsightsScheduler worker started. Running every {self.interval_seconds}s.")
        # Run immediate initial batch job on startup
        self.run_once()

        while not self._stop_event.is_set():
            # Wait for interval_seconds or until stop requested
            stopped = self._stop_event.wait(self.interval_seconds)
            if stopped:
                break
            self.run_once()

        logger.info("InsightsScheduler worker thread stopped.")

    def run_once(self):
        logger.info("Running InsightsScheduler batch job...")
        db = SessionLocal()
        try:
            res = run_batch_insights_job(db)
            logger.info(f"InsightsScheduler batch job finished: processed {res.users_processed} users.")
        except Exception as e:
            logger.error(f"InsightsScheduler batch job error: {e}")
        finally:
            db.close()

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            logger.warning("InsightsScheduler already running.")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="InsightsSchedulerThread")
        self._thread.start()
        logger.info("InsightsScheduler thread launched successfully.")

    def stop(self):
        if self._thread is not None:
            self._stop_event.set()
            self._thread.join(timeout=5)
            logger.info("InsightsScheduler stopped cleanly.")


# Singleton scheduler instance
scheduler = InsightsScheduler()
