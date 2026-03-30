"""
request_manager.py — Async HTTP helpers with retry, backoff, and UA rotation.

Provides ``safe_get`` and ``safe_post`` for resilient API and scraping calls.
Uses exponential backoff with jitter for 429/timeout, and fast-fails on 403/404.
"""

import random
import asyncio
from typing import Any, Dict, List, Optional, Union

import httpx

try:
    from fake_useragent import UserAgent as _UserAgent
    _ua_instance = _UserAgent()
except Exception:
    _ua_instance = None


# ── Constants ────────────────────────────────────────────────────

OVERPASS_MIRRORS: List[str] = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

_FALLBACK_UAS: List[str] = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

DEFAULT_TIMEOUT: float = 30.0


# ── Header helpers ───────────────────────────────────────────────

def get_headers(is_api: bool = False) -> Dict[str, str]:
    """Return request headers with a rotating User-Agent.

    Args:
        is_api: If ``True``, include ``Accept: application/json``.

    Returns:
        Dict of HTTP headers.
    """
    if _ua_instance is not None:
        try:
            ua = _ua_instance.random
        except Exception:
            ua = random.choice(_FALLBACK_UAS)
    else:
        ua = random.choice(_FALLBACK_UAS)

    headers: Dict[str, str] = {"User-Agent": ua}
    if is_api:
        headers["Accept"] = "application/json"
    return headers


# ── Async GET ────────────────────────────────────────────────────

async def safe_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    retries: int = 3,
    base_delay: float = 2.0,
    is_scrape: bool = False,
) -> Optional[Union[Dict[str, Any], str]]:
    """Perform an async GET with retry and exponential backoff.

    Args:
        url: Target URL.
        params: Optional query parameters.
        retries: Maximum number of attempts.
        base_delay: Initial backoff delay in seconds.
        is_scrape: If ``True``, returns raw HTML text; otherwise parses JSON.

    Returns:
        Parsed JSON dict, raw HTML string, or ``None`` on failure.
    """
    delay = base_delay
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                headers = get_headers(is_api=not is_scrape)
                resp = await client.get(url, params=params, headers=headers)

                if resp.status_code in (403, 404):
                    return None

                if resp.status_code == 429:
                    jitter = random.uniform(0, delay * 0.5)
                    await asyncio.sleep(delay + jitter)
                    delay *= 2
                    continue

                resp.raise_for_status()
                return resp.text if is_scrape else resp.json()

        except httpx.TimeoutException:
            delay *= 2
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            continue

        except httpx.HTTPStatusError:
            if attempt < retries - 1:
                jitter = random.uniform(0, delay * 0.5)
                await asyncio.sleep(delay + jitter)
                delay *= 2
            continue

        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            continue

    return None


# ── Async POST ───────────────────────────────────────────────────

async def safe_post(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    retries: int = 3,
    base_delay: float = 2.0,
) -> Optional[Dict[str, Any]]:
    """Perform an async POST with retry and exponential backoff.

    Args:
        url: Target URL.
        data: Optional form data.
        json_body: Optional JSON body.
        retries: Maximum number of attempts.
        base_delay: Initial backoff delay in seconds.

    Returns:
        Parsed JSON dict or ``None`` on failure.
    """
    delay = base_delay
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                headers = get_headers(is_api=True)
                resp = await client.post(
                    url, data=data, json=json_body, headers=headers
                )

                if resp.status_code in (403, 404):
                    return None

                if resp.status_code == 429:
                    jitter = random.uniform(0, delay * 0.5)
                    await asyncio.sleep(delay + jitter)
                    delay *= 2
                    continue

                resp.raise_for_status()
                return resp.json()

        except httpx.TimeoutException:
            delay *= 2
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            continue

        except httpx.HTTPStatusError:
            if attempt < retries - 1:
                jitter = random.uniform(0, delay * 0.5)
                await asyncio.sleep(delay + jitter)
                delay *= 2
            continue

        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            continue

    return None
