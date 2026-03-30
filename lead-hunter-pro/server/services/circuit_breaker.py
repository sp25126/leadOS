import json
import os
import time
import re
from typing import Optional

BREAKER_STATE_FILE = os.path.join("output", "breaker_state.json")
MAX_FAILURES       = 3
RESET_AFTER_HOURS  = 24  # Auto-reset after 24 hours

# Domains that must NEVER be blocked - they serve contact pages
NEVER_BLOCK_DOMAINS = {
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com",
    "linkedin.com", "www.linkedin.com",
    "youtube.com", "www.youtube.com",
    "google.com", "www.google.com",
    "maps.google.com", "maps.googleapis.com",
    "duckduckgo.com", "html.duckduckgo.com",
}

# Minimum domain validation - must look like a real domain
_VALID_DOMAIN_RE = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
)


def _load_state() -> dict:
    try:
        if os.path.exists(BREAKER_STATE_FILE):
            with open(BREAKER_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_state(state: dict) -> None:
    try:
        os.makedirs(os.path.dirname(BREAKER_STATE_FILE), exist_ok=True)
        with open(BREAKER_STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def _purge_stale(state: dict) -> dict:
    """
    Remove entries that are:
    1. In NEVER_BLOCK_DOMAINS
    2. Invalid domain strings
    3. Opened_at more than RESET_AFTER_HOURS ago
    """
    now = time.time()
    cutoff = now - (RESET_AFTER_HOURS * 3600)
    purged = []
    clean_state = {}

    for domain, data in state.items():
        # Never block certain domains
        if domain in NEVER_BLOCK_DOMAINS:
            purged.append(f"never-block: {domain}")
            continue

        # Drop invalid domain strings
        if not _VALID_DOMAIN_RE.match(domain):
            purged.append(f"invalid-domain: {domain}")
            continue

        opened_at = data.get("opened_at")

        # Auto-reset if opened_at is too old
        if opened_at and opened_at < cutoff:
            purged.append(f"stale ({RESET_AFTER_HOURS}h): {domain}")
            continue

        clean_state[domain] = data

    if purged:
        print(f"[BREAKER] Purged {len(purged)} stale/invalid entries: {purged[:5]}")

    return clean_state


def is_blocked(domain: str) -> bool:
    """Return True if domain is currently open (broken) in circuit breaker."""
    if domain in NEVER_BLOCK_DOMAINS:
        return False

    state = _purge_stale(_load_state())
    entry = state.get(domain, {})
    if entry.get("failures", 0) >= MAX_FAILURES and entry.get("opened_at"):
        return True
    return False


def record_failure(domain: str) -> None:
    """Increment failure count. Opens breaker at MAX_FAILURES."""
    if domain in NEVER_BLOCK_DOMAINS:
        return
    if not _VALID_DOMAIN_RE.match(domain):
        return  # Never record invalid domain strings

    state = _purge_stale(_load_state())
    entry = state.get(domain, {"failures": 0, "opened_at": None})
    entry["failures"] = entry.get("failures", 0) + 1
    if entry["failures"] >= MAX_FAILURES:
        entry["opened_at"] = time.time()
    state[domain] = entry
    _save_state(state)


def record_success(domain: str) -> None:
    """Reset a domain's failure count on success."""
    state = _purge_stale(_load_state())
    if domain in state:
        del state[domain]
        _save_state(state)


def reset_all() -> None:
    """Emergency reset - clears all entries."""
    _save_state({})
    print("[BREAKER] All entries cleared.")
