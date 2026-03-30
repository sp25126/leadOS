import re
from typing import Optional

# ============================================================
# PHONE EXTRACTION & VALIDATION
# ============================================================

# Patterns by country code
_PHONE_PATTERNS = {
    "IN":  re.compile(r'(?:\+91|91|0)?[\s\-]?([6-9]\d{9})'),
    "UAE": re.compile(r'(?:\+971|971|00971|0)?[\s\-]?([2-9]\d{7,8})'),
    "AU":  re.compile(r'(?:\+61|61|0)[\s\-]?([2-9]\d{8})'),
    "US":  re.compile(r'(?:\+1)?[\s\-]?\(?([2-9]\d{2})\)?[\s\-]?(\d{3})[\s\-]?(\d{4})'),
    "INT": re.compile(r'\+(\d{1,3})[\s\-]?(\d{4,14})'),
}

# Max digits in any real phone number (ITU-T E.164 allows 15 max)
_MAX_PHONE_DIGITS = 15
_MIN_PHONE_DIGITS = 7


def clean_phone(raw: str, country_hint: str = "IN") -> Optional[str]:
    """
    Extract a SINGLE clean phone number from raw text.
    Returns E.164 format string or None if invalid.
    Never concatenates multiple numbers.
    """
    if not raw:
        return None

    # Strip everything except digits and leading +
    digits_only = "".join(c for c in str(raw) if c.isdigit())
    has_plus = str(raw).startswith("+")

    # Reject if total digit count exceeds E.164 max - likely concatenated
    if len(digits_only) > _MAX_PHONE_DIGITS:
        # Try to rescue: extract the first valid phone from the raw string
        rescued = _extract_first_phone(str(raw), country_hint)
        if rescued:
            print(f"[PHONE] Concatenated sequence detected -> rescued '{rescued}'")
        return rescued

    if len(digits_only) < _MIN_PHONE_DIGITS:
        return None

    # India: +91 XXXXXXXXXX
    if country_hint == "IN":
        if len(digits_only) == 10 and digits_only[0] in '6789':
            return f"+91{digits_only}"
        if len(digits_only) == 12 and digits_only.startswith("91"):
            return f"+{digits_only}"

    # UAE: +971 XXXXXXXX
    if country_hint == "UAE":
        if len(digits_only) == 9 and digits_only[0] in '234567':
            return f"+971{digits_only}"
        if len(digits_only) == 12 and digits_only.startswith("971"):
            return f"+{digits_only}"

    # Australia: +61 XXXXXXXXX
    if country_hint == "AU":
        if len(digits_only) == 9:
            return f"+61{digits_only}"
        if len(digits_only) == 11 and digits_only.startswith("61"):
            return f"+{digits_only}"

    # International fallback: validate as E.164
    if has_plus:
        if _MIN_PHONE_DIGITS <= len(digits_only) <= _MAX_PHONE_DIGITS:
            return f"+{digits_only}"

    return None


def _extract_first_phone(text: str, country_hint: str = "IN") -> Optional[str]:
    """Extract only the FIRST valid phone from a string."""
    pattern = _PHONE_PATTERNS.get(country_hint, _PHONE_PATTERNS["INT"])
    match = pattern.search(text)
    if match:
        return clean_phone(match.group(0), country_hint)

    # Try international as fallback
    match = _PHONE_PATTERNS["INT"].search(text)
    if match:
        raw = match.group(0)
        digs = "".join(c for c in raw if c.isdigit())
        if _MIN_PHONE_DIGITS <= len(digs) <= _MAX_PHONE_DIGITS:
            return f"+{digs}"

    return None


def detect_country_from_location(location: str) -> str:
    """Best-effort country detection for phone formatting."""
    loc = str(location).lower()
    if any(x in loc for x in ['dubai', 'abu dhabi', 'sharjah', 'uae', 'emirates']):
        return "UAE"
    if any(x in loc for x in ['sydney', 'melbourne', 'brisbane', 'perth', 'australia', '.au']):
        return "AU"
    if any(x in loc for x in ['pune', 'mumbai', 'delhi', 'bangalore', 'ahmedabad', 'india', '.in']):
        return "IN"
    return "IN"
