import os
import time
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from utils.limiter import limiter

class ProviderKeyError(Exception):
    """Raised when an external AI/Email provider key is missing or invalid."""
    pass

#   Logging Setup  
import logging

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s | %(levelname)-8s | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: blue + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

logger = logging.getLogger("LeadOS")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def log_activity(msg: str, level: str = "info"):
    icon = {"info": "[INFO]", "success": "[SUCCESS]", "warning": "[WARNING]", "error": "[ERROR]", "api": "[API]"}.get(level, "")
    full_msg = f"{icon}{msg}"
    if level == "error": logger.error(full_msg)
    elif level == "warning": logger.warning(full_msg)
    else: logger.info(full_msg)


from services.whatsapp_client import check_wa_ready
from routers.leads    import router as leads_router
from routers.outreach import router as outreach_router
from routers.email    import router as email_router
from routers.agent    import router as agent_router
from routers.quota    import router as quota_router
from routers.whatsapp import router as whatsapp_router
from routers.enrich   import router as enrich_router
from routers.score    import router as score_router
from routers.forms    import router as forms_router
from routers.security import router as security_router
from routers.stats    import router as stats_router
from routers.config_router import router as config_router
from utils.rate_limiter       import quota

# Telegram webhook - only wire up if token is configured
_bot_app = None
try:
    from bot.telegram_bot import get_webhook_router
    _wh_router, _bot_app = get_webhook_router()
except Exception:
    _wh_router = None

from database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    #   Startup  
    print("\n  Lead Hunter Pro - API Starting")
    print(" " * 40)
    
    # Init DB tables
    try:
        await create_tables()
        print("  Database tables verified/created.")
    except Exception as e:
        print(f"  Database initialization failed: {e}")

    status = quota.status()
    for source, stat in status.items():
        remaining  = stat["remaining"]
        used       = stat["used"]
        total      = remaining + used
        bar_filled = int((remaining / max(total, 1)) * 12)
        bar        = " " * bar_filled + " " * (12 - bar_filled)
        print(f"  {source:<22} [{bar}] {remaining} left")
    print(" " * 40)
    yield
    #   Shutdown  
    print("\n  Shutting down Lead Hunter Pro")

app = FastAPI(
    title       = "Lead Hunter Pro",
    description = "AI-powered lead generation and outreach engine",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
from slowapi import _rate_limit_exceeded_handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(ProviderKeyError)
async def provider_key_exception_handler(request: Request, exc: ProviderKeyError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

#   CORS  
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins     = allowed_origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

import json

#   Middlewares  
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    #   Map Headers for Curl  
    headers_to_log = ["X-API-Key", "X-Gemini-Key", "X-Brevo-Key", "Content-Type"]
    curl_headers = []
    for h in headers_to_log:
        val = request.headers.get(h)
        if val: curl_headers.append(f'-H "{h}: {val}"')
    
    #   Log Incoming  
    body_summary = ""
    curl_body = ""
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                try:
                    data = json.loads(body)
                    body_summary = f"   {json.dumps(data)[:100]}..."
                    curl_body = f"-d '{json.dumps(data)}'"
                except:
                    body_summary = f"   ({len(body)} bytes)"
                    curl_body = f"--data-binary '@file.bin'" # Placeholder for binary
            
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
        except Exception as e:
            body_summary = f"   (body unreadable: {e})"

    # Simple path filtering to avoid noise
    if "health" in request.url.path or "quota" in request.url.path:
        return await call_next(request)

    #   Construct & Log Curl  
    curl_cmd = f"curl -X {request.method} {request.url} {' '.join(curl_headers)} {curl_body}".strip()
    # Print in a distinct magenta color for reproduction
    print(f"\n\x1b[35m[CURL] {curl_cmd}\x1b[0m\n")

    log_activity(f"{request.method} {request.url.path}{body_summary}", level="api")

    #   Execute & Log Response  
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        level = "api" if response.status_code < 400 else "error"
        log_activity(
            f"  {response.status_code} ({duration:.2f}s) for {request.url.path}",
            level=level
        )
        return response
    except Exception as e:
        duration = time.time() - start_time
        log_activity(f"  CRASH: {request.method} {request.url.path} -> {e} ({duration:.2f}s)", level="error")
        raise e

#   Routers  

app.include_router(leads_router,    prefix="/api/leads",    tags=["Leads"])
app.include_router(outreach_router, prefix="/api/outreach", tags=["Outreach"])
app.include_router(email_router,    prefix="/api/email",    tags=["Email"])
app.include_router(quota_router,    prefix="/api",          tags=["Quota"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(agent_router,    prefix="/api/agent",    tags=["Agent"])
app.include_router(enrich_router,   prefix="/api/enrich",   tags=["Enrich"])
app.include_router(score_router,    prefix="/api/score",    tags=["Score"])
app.include_router(forms_router,    prefix="/api/forms",    tags=["Forms"])
app.include_router(security_router, prefix="/api/security", tags=["Security"])
app.include_router(stats_router,    prefix="/api/stats",    tags=["Stats"])
app.include_router(config_router,   prefix="",             tags=["Config"])

if _wh_router is not None:
    app.include_router(_wh_router, prefix="/api/bot")

#   Health  
@app.get("/api/health", tags=["System"])
async def health():
    wa_ready = await check_wa_ready()
    return {
        "status":    "ok",
        "wa_server": wa_ready,
        "timestamp": time.time(),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host      = "0.0.0.0",
        port      = 8000,
        reload    = True,
        log_level = "info",
    )
