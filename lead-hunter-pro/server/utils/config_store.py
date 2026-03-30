import os
import json
import logging
from pathlib import Path
from threading import Lock
from typing import Optional

# Stored at server/config.json - mount as Docker volume for persistence.
# Priority: config.json > .env
CONFIG_PATH = Path(os.getenv("CONFIG_PATH", os.path.join(os.path.dirname(__file__), "..", "config", "config.json")))
_lock = Lock()
_cache: dict = {}

def _load() -> dict:
    """Load config from disk into cache."""
    global _cache
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r") as f:
                _cache = json.load(f)
    except Exception as e:
        logging.warning(f"Config load failed: {e}")
        _cache = {}
    return _cache

def _save(data: dict) -> None:
    """Persist config to disk."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

def get(key: str, fallback_env: Optional[str] = None) -> str:
    """
    Get a config value.
    Priority: config.json -> os.environ -> fallback_env default
    """
    if not _cache:
        _load()
    return (
        _cache.get(key)
        or os.getenv(fallback_env or key.upper(), "")
    )

def update(new_values: dict) -> None:
    """
    Merge new_values into config and persist.
    Only updates non-empty values (empty string = keep existing).
    """
    if not _cache:
        _load()
    with _lock:
        for k, v in new_values.items():
            if v and str(v).strip():      # never overwrite with empty
                _cache[k] = str(v).strip()
        _save(_cache)

def get_all_keys() -> dict:
    """Return config with values masked for display (last 4 chars only)."""
    if not _cache:
        _load()
    masked = {}
    for k, v in _cache.items():
        if v and len(v) > 4:
            masked[k] = " " * (len(v) - 4) + v[-4:]
        elif v:
            masked[k] = " "
        else:
            masked[k] = ""
    return masked

# Convenience accessors used throughout the codebase
def gemini_key()     -> str: return get("gemini_key",     "GEMINI_API_KEY")
def gmaps_key()      -> str: return get("gmaps_key",      "GOOGLE_MAPS_API_KEY")
def hunter_key()     -> str: return get("hunter_key",     "HUNTER_API_KEY")
def brevo_key()      -> str: return get("brevo_key",      "BREVO_API_KEY")
def sender_email()   -> str: return get("sender_email",   "SENDER_EMAIL")
def sender_name()    -> str: return get("sender_name",    "SENDER_NAME")
def groq_key()       -> str: return get("groq_key",       "GROQ_API_KEY")
def telegram_token() -> str: return get("telegram_token", "TELEGRAM_BOT_TOKEN")

# Initialize on import
_load()
