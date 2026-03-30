"""
server/scheduler.py
 
Nightly autonomous pipeline: ingest -> enrich -> score -> email.
Run alongside the main app: python scheduler.py
"""
import asyncio
import logging
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.makedirs("logs", exist_ok=True)
BASE_URL  = os.getenv("INTERNAL_API_URL", "http://localhost:8000")
API_KEY   = os.getenv("INTERNAL_API_KEY")
TIMEOUT   = 300
GAP_FILE  = "logs/last_run_timestamp.txt"

_job_running = False


async def call_internal(path: str, method: str = "POST", params: str = "") -> None:
    """Fire-and-forget call to our own FastAPI server."""
    url = f"{BASE_URL}/{path}"
    if params:
        url = f"{url}?{params}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            resp = await client.request(
                method,
                url,
                headers={"X-API-Key": API_KEY},
            )
            logger.info(f"Job {path} -> {method} HTTP {resp.status_code}")
    except Exception as e:
        logger.error(f"Job {path} failed: {e}")


#   Scheduled jobs  

async def job_enrich() -> None:
    """Enrich any NEW leads sitting in output CSVs (batch of 30)."""
    logger.info("  Running enrichment job")
    await call_internal("api/enrich/run", params="batchsize=30")


async def job_score() -> None:
    """Re-score leads after enrichment (batch of 100)."""
    logger.info("  Running scoring job")
    await call_internal("api/score/run", params="batchsize=100")


async def job_email_send() -> None:
    """Smart-send emails to READY leads, 50 per source, live mode."""
    global _job_running
    if _job_running:
        logger.warning("Nightly job already running - skipping overlap.")
        return
        
    # Check 7-8 hour gap
    if os.path.exists(GAP_FILE):
        try:
            with open(GAP_FILE, "r") as f:
                last_run = float(f.read().strip())
                if (time.time() - last_run) < (7 * 3600):
                    logger.warning("Gap guard: Less than 7 hours since last run. Skipping.")
                    return
        except Exception:
            pass

    _job_running = True
    try:
        logger.info("  Running smart email send job")
        await call_internal("api/email/send-run-by-source", params="source=all&batch_size=50&dry_run=false")
        
        # Log successful run time
        with open(GAP_FILE, "w") as f:
            f.write(str(time.time()))
    finally:
        _job_running = False


async def job_health_check() -> None:
    """Ping health endpoint to keep Render/Railway free-tier alive."""
    logger.info("  Health ping")
    await call_internal("api/health", method="GET")


#   Entry point  

def build_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

    # Enrich at 2am every day
    scheduler.add_job(job_enrich, CronTrigger(hour=2, minute=0),  id="enrich",     replace_existing=True)
    # Score at 3am (after enrich)
    scheduler.add_job(job_score,  CronTrigger(hour=3, minute=0),  id="score",      replace_existing=True)
    # Email send at 9am on weekdays
    scheduler.add_job(job_email_send, CronTrigger(hour=9, minute=0, day_of_week="mon-fri"), id="email_send", replace_existing=True)
    # Keep-alive ping every 10 minutes
    scheduler.add_job(job_health_check, "interval", minutes=10, id="health_ping",  replace_existing=True)

    return scheduler


async def main() -> None:
    scheduler = build_scheduler()
    scheduler.start()
    logger.info("  Scheduler started - jobs registered:")
    for job in scheduler.get_jobs():
        logger.info(f"   {job.id:<20} next: {job.next_run_time}")
    try:
        await asyncio.Event().wait()   # Run forever
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("  Scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())
