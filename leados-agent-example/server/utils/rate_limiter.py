"""
rate_limiter.py — Thread-safe API quota manager with persistence.

Manages free-tier quotas for multiple lead-discovery and enrichment APIs.
Persists state to JSON so quotas survive process restarts.
Automatically resets daily and monthly quotas when the calendar rolls over.
"""

import json
import os
import threading
from datetime import datetime, date
from typing import Dict, Optional


# Default quota definitions: source → (limit, period)
DEFAULT_QUOTAS: Dict[str, Dict] = {
    "overpass_main":   {"limit": 10000, "period": "daily"},
    "overpass_kumi":   {"limit": 10000, "period": "daily"},
    "overpass_private": {"limit": 10000, "period": "daily"},
    "google_maps":     {"limit": 10000, "period": "monthly"},
    "foursquare":      {"limit": 10000, "period": "monthly"},
    "here_places":     {"limit": 1000,  "period": "daily"},
    "hunter_io":       {"limit": 25,    "period": "monthly"},
    "abstract_email":  {"limit": 100,   "period": "monthly"},
}


class QuotaManager:
    """Thread-safe API quota manager with JSON persistence.

    Args:
        state_file: Path to the JSON file used for persisting quota state.

    Usage:
        >>> quota = QuotaManager()
        >>> if quota.has_quota("google_maps"):
        ...     quota.consume("google_maps")
    """

    def __init__(self, state_file: str = "server/data/quota_state.json") -> None:
        self._state_file: str = state_file
        self._lock: threading.Lock = threading.Lock()
        self._quotas: Dict[str, Dict] = {}
        self._load_or_init()

    # ── Persistence ──────────────────────────────────────────────

    def _load_or_init(self) -> None:
        """Load existing state from disk or initialise fresh quotas."""
        if os.path.exists(self._state_file):
            with open(self._state_file, "r", encoding="utf-8") as f:
                self._quotas = json.load(f)
            self._auto_reset()
        else:
            self._init_fresh()

    def _init_fresh(self) -> None:
        """Create quota state from defaults and persist."""
        today = date.today()
        for source, cfg in DEFAULT_QUOTAS.items():
            self._quotas[source] = {
                "limit": cfg["limit"],
                "used": 0,
                "period": cfg["period"],
                "reset_date": today.isoformat(),
                "reset_month": today.strftime("%Y-%m"),
            }
        self._save()

    def _save(self) -> None:
        """Write current state to disk."""
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(self._quotas, f, indent=2)

    # ── Auto-reset logic ─────────────────────────────────────────

    def _auto_reset(self) -> None:
        """Reset daily/monthly counters when the calendar rolls over."""
        today = date.today()
        today_iso = today.isoformat()
        this_month = today.strftime("%Y-%m")
        changed = False

        for source, state in self._quotas.items():
            period = state.get("period", "daily")

            if period == "daily" and state.get("reset_date") != today_iso:
                state["used"] = 0
                state["reset_date"] = today_iso
                changed = True

            if period == "monthly" and state.get("reset_month") != this_month:
                state["used"] = 0
                state["reset_month"] = this_month
                changed = True

        # Back-fill any new sources that were added after initial state creation
        for source, cfg in DEFAULT_QUOTAS.items():
            if source not in self._quotas:
                self._quotas[source] = {
                    "limit": cfg["limit"],
                    "used": 0,
                    "period": cfg["period"],
                    "reset_date": today_iso,
                    "reset_month": this_month,
                }
                changed = True

        if changed:
            self._save()

    # ── Public API ───────────────────────────────────────────────

    def has_quota(self, source: str) -> bool:
        """Check whether *source* still has remaining quota.

        Args:
            source: The API source name (e.g. ``"google_maps"``).

        Returns:
            ``True`` if at least one request can still be made.
        """
        with self._lock:
            state = self._quotas.get(source)
            if state is None:
                return False
            return state["used"] < state["limit"]

    def consume(self, source: str, count: int = 1) -> None:
        """Record *count* requests against *source*.

        Caps ``used`` at ``limit`` so remaining never goes negative.

        Args:
            source: The API source name.
            count: Number of requests to record (default ``1``).
        """
        with self._lock:
            state = self._quotas.get(source)
            if state is None:
                return
            state["used"] = min(state["used"] + count, state["limit"])
            self._save()

    def remaining(self, source: str) -> int:
        """Return the number of remaining requests for *source*.

        Args:
            source: The API source name.

        Returns:
            Non-negative integer of remaining quota.
        """
        with self._lock:
            state = self._quotas.get(source)
            if state is None:
                return 0
            return max(state["limit"] - state["used"], 0)

    def status(self) -> Dict[str, Dict]:
        """Return a snapshot of every source's quota status.

        Returns:
            Dict mapping source names to ``{limit, used, remaining, period}``.
        """
        with self._lock:
            result: Dict[str, Dict] = {}
            for source, state in self._quotas.items():
                result[source] = {
                    "limit": state["limit"],
                    "used": state["used"],
                    "remaining": max(state["limit"] - state["used"], 0),
                    "period": state["period"],
                }
            return result

    def reset_source(self, source: str) -> None:
        """Manually reset the counter for *source* back to zero.

        Args:
            source: The API source name.
        """
        with self._lock:
            state = self._quotas.get(source)
            if state is None:
                return
            state["used"] = 0
            self._save()


# ── Singleton instance ───────────────────────────────────────────
quota: QuotaManager = QuotaManager()
