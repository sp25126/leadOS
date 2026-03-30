"""
Email Waterfall Adapter
Bridges Octagon's battle-tested FreeOSINTWaterfall into the LeadOS enrichment pipeline.
Uses sys.path injection to import from the octagon/ directory already in the repo root.
Falls back gracefully if Octagon dependencies are unavailable.
"""

import sys
import os
import logging
import asyncio
from typing import Optional, Tuple

logger = logging.getLogger("LeadOS.waterfall_adapter")

#   Path injection to find octagon source  
_OCTAGON_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "octagon", "backend")
)

_waterfall_available = False

def _inject_octagon_path():
    """Add Octagon backend to sys.path so we can import its modules."""
    global _waterfall_available
    if not os.path.isdir(_OCTAGON_PATH):
        logger.warning(
            f"[WaterfallAdapter] Octagon path not found at {_OCTAGON_PATH}. "
            "Advanced email waterfall disabled."
        )
        return False
    if _OCTAGON_PATH not in sys.path:
        sys.path.insert(0, _OCTAGON_PATH)
    return True


def _try_load_waterfall():
    """Attempt to load the Octagon FreeOSINTWaterfall class."""
    global _waterfall_available
    if not _inject_octagon_path():
        return None
    try:
        # Octagon uses app.* imports - we need to mock/patch minimal env vars
        # so that app.config doesn't crash on missing DB vars
        _patch_octagon_env()
        from app.enrichment.email_waterfall import FreeOSINTWaterfall
        _waterfall_available = True
        logger.info("[WaterfallAdapter]   Octagon FreeOSINTWaterfall loaded successfully")
        return FreeOSINTWaterfall
    except ImportError as e:
        logger.warning(f"[WaterfallAdapter] Import failed (missing dep?): {e}")
        return None
    except Exception as e:
        logger.warning(f"[WaterfallAdapter] Load failed: {e}")
        return None


from utils import config_store

def _patch_octagon_env():
    """
    Octagon's app.config requires DB/Redis vars to exist.
    Provide values from config_store or defaults so it doesn't crash.
    """
    defaults = {
        "DATABASE_URL":       os.getenv("DATABASE_URL", "postgresql+asyncpg://dummy:dummy@localhost/dummy"),
        "SUPABASE_URL":       os.getenv("SUPABASE_URL", "https://dummy.supabase.co"),
        "SUPABASE_KEY":       os.getenv("SUPABASE_KEY", "dummy_key"),
        "REDIS_URL":          os.getenv("REDIS_URL", "redis://localhost:6379"),
        "GROQ_API_KEY":       config_store.groq_key(),
        "GEMINI_API_KEY":     config_store.gemini_key(),
        "GOOGLE_PLACES_API_KEY": config_store.gmaps_key(),
        "TELEGRAM_BOT_TOKEN": config_store.telegram_token(),
        "FROM_EMAIL":         config_store.sender_email(),
        "FROM_NAME":          config_store.sender_name(),
        "SMTP_HOST":          config_store.get("smtp_host", "SMTP_HOST") or "smtp.brevo.com",
        "SMTP_PORT":          config_store.get("smtp_port", "SMTP_PORT") or "587",
        "SMTP_USER":          config_store.get("smtp_user", "SMTP_USER") or "dummy",
        "SMTP_PASS":          config_store.get("smtp_pass", "SMTP_PASS") or config_store.brevo_key() or "dummy",
        "DOMAIN":             config_store.get("domain", "DOMAIN") or "localhost",
        "SENDER_EMAIL":       config_store.sender_email(),
        "SENDER_NAME":        config_store.sender_name(),
        "API_KEY":            os.getenv("API_KEY", os.getenv("MASTER_KEY", "leadoskey123")),
    }
    for k, v in defaults.items():
        if v: # Only set if we have a value
            os.environ[k] = str(v)


#   Lazy singleton  
_WaterfallClass = None
_waterfall_instance = None

def _get_waterfall():
    """Return a cached FreeOSINTWaterfall instance, or None if unavailable."""
    global _WaterfallClass, _waterfall_instance
    if _waterfall_instance is not None:
        return _waterfall_instance
    if _WaterfallClass is None:
        _WaterfallClass = _try_load_waterfall()
    if _WaterfallClass is None:
        return None
    try:
        _waterfall_instance = _WaterfallClass()
        return _waterfall_instance
    except Exception as e:
        logger.warning(f"[WaterfallAdapter] Instantiation failed: {e}")
        return None


#   Public API  

async def find_email_octagon(
    domain: str,
    founder_name: Optional[str] = None,
    company_name: Optional[str] = None,
    timeout: float = 20.0,
) -> Tuple[Optional[str], str]:
    """
    Run the Octagon OSINT waterfall to find an email for the given domain.

    Returns:
        (email, source) - email is None if not found
    """
    waterfall = _get_waterfall()
    if waterfall is None:
        return None, "waterfall_unavailable"

    try:
        result = await asyncio.wait_for(
            waterfall.find_osint_email(domain, founder_name),
            timeout=timeout
        )
        if result and result.email:
            logger.info(
                f"[WaterfallAdapter]   {domain} -> {result.email} "
                f"(source={result.source}, confidence={result.confidence})"
            )
            return result.email, result.source
    except asyncio.TimeoutError:
        logger.debug(f"[WaterfallAdapter] Timeout for {domain}")
    except Exception as e:
        logger.debug(f"[WaterfallAdapter] Error for {domain}: {type(e).__name__}: {e}")

    return None, "waterfall_not_found"


def is_waterfall_available() -> bool:
    """Quick check - can we use the Octagon waterfall?"""
    return _get_waterfall() is not None


def score_email_quality(email: str) -> int:
    """
    Score email quality on 0-3 scale.
    3 = Personal/named (john@company.com)
    2 = Role-based but not generic (founder@, ceo@)
    1 = Generic (info@, contact@, sales@)
    0 = No email
    """
    if not email or "@" not in email:
        return 0
    local = email.split("@")[0].lower()
    generic = {
        "info", "contact", "hello", "sales", "support", "admin",
        "team", "office", "enquiry", "help", "hi", "mail",
        "reception", "customercare", "customerservice", "service",
        "accounts", "billing", "careers", "jobs", "hr", "press",
        "marketing", "legal", "privacy", "webmaster", "postmaster",
    }
    valuable_roles = {"founder", "ceo", "cto", "coo", "owner", "director", "partner"}
    if local in generic:
        return 1
    if local in valuable_roles:
        return 2
    # Named email: contains letters and is not a known generic -> quality 3
    return 3
