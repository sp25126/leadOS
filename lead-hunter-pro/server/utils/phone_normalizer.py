"""
phone_normalizer.py - Normalize raw phone strings to E.164-style format.

Handles Indian numbers by default but works with any country code.
"""

import re
from typing import Optional


def normalize_phone(raw: Optional[str], country_code: str = "+91") -> str:
    """Normalize a raw phone string into a standardised international format.

    Rules:
        1. ``None`` or empty input -> ``""``.
        2. Strip everything except digits and a leading ``+``.
        3. If the result has a leading ``+``, keep as-is.
        4. If it starts with ``0``, replace the leading zero with *country_code*.
        5. If exactly 10 digits with no prefix, prepend *country_code*.
        6. Return ``""`` if fewer than 10 digits remain after cleaning.

    Args:
        raw: The raw phone string (may contain spaces, dashes, parentheses, etc.).
        country_code: Default country prefix, e.g. ``"+91"`` for India.

    Returns:
        The normalised phone string, or ``""`` if input is invalid.
    """
    if raw is None:
        return ""

    raw = str(raw).strip()
    if not raw:
        return ""

    # Preserve a leading '+', then strip everything non-digit
    has_plus = raw.startswith("+")
    digits = re.sub(r"[^\d]", "", raw)

    if not digits or len(digits) < 10:
        return ""

    if has_plus:
        return f"+{digits}"

    if raw.lstrip().startswith("0"):
        return f"{country_code}{digits[1:]}"

    if len(digits) == 10:
        return f"{country_code}{digits}"

    # More than 10 digits without a +, assume it already contains a country code
    return f"+{digits}"
