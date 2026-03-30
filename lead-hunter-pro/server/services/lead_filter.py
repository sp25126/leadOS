import re

# ============================================================
# JUNK BUSINESS NAMES - drop before enrichment
# ============================================================
_JUNK_NAME_PATTERNS = [
    # Institutional/government catering
    r'\bcanteen\b', r'hostel\s*mess\b', r'\bmess\s*hall\b',
    r'police\s*station', r'railway\s*station', r'bus\s*stand',
    r'\bjudicial\b', r'army\s*canteen', r'\bncc\b',
    r'municipal\b', r'government\b', r'govt\.?\b',
    r'university\s*canteen', r'college\s*canteen',
    r'school\s*canteen', r'hospital\s*canteen',
    r'lab\s*canteen', r'\bcoep\b',
    r'microbiology', r'students?\s*mess',
    # Religious/public infrastructure
    r'\btemple\b', r'\bmandir\b', r'\bmasjid\b',
    r'\bchurch\b', r'\bgurudwara\b',
    r'\batm\b', r'parking', r'petrol\s*pump',
    r'fuel\s*station', r'charging\s*station',
    # Generic/unnamed
    r'^canteen$', r'^mess$', r'^restaurant$', r'^cafe$',
    r'^food$', r'^snacks?$',
]

_JUNK_REGEX = re.compile('|'.join(_JUNK_NAME_PATTERNS), re.IGNORECASE)

# ============================================================
# CHAIN / FRANCHISE NAMES - drop before enrichment
# ============================================================
_CHAIN_NAMES = [
    "mcdonald", "mcdonalds", "burger king", "kfc",
    "taco bell", "subway", "dominos", "domino's",
    "pizza hut", "starbucks", "barista",
    "cafe coffee day", "ccd", "costa coffee",
    "amul", "havmor", "bata", "reliance",
    "big bazaar", "dmart", "walmart",
    "hungry jacks", "red rooster",
    "wow momo", "haldiram", "bikaner",
]

# ============================================================
# GARBAGE OSM NAMES - single words, no meaning
# ============================================================
_GARBAGE_NAME_REGEX = re.compile(
    r'^(purohit|nishat|paramount|unknown|'
    r'n/?a|test|sample|new business|shop|store|outlet|point|place|'
    r'corner|centre|center|house|home|room|stall|counter)$',
    re.IGNORECASE
)

# Name too short to be a real business
_MIN_NAME_LENGTH = 3


def is_junk_lead(lead: dict) -> tuple[bool, str]:
    """
    Returns (should_drop: bool, reason: str).
    Call this BEFORE any enrichment.
    """
    name = (lead.get("name") or "").strip()

    # Empty or too short
    if len(name) < _MIN_NAME_LENGTH:
        return True, "name_too_short"

    # Purely numeric or coordinate-like
    if re.match(r'^[\d\s\.,\-/]+$', name):
        return True, "name_is_numeric"

    # Junk institutional name
    if _JUNK_REGEX.search(name):
        return True, f"junk_pattern"

    # Chain/franchise
    name_lower = name.lower()
    for chain in _CHAIN_NAMES:
        if chain in name_lower:
            return True, f"chain_brand: {chain}"

    # Garbage single-word OSM entry
    if _GARBAGE_NAME_REGEX.match(name):
        return True, f"garbage_osm_name"

    return False, ""


def filter_leads(leads: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Returns (valid_leads, dropped_leads).
    Each dropped lead has a 'drop_reason' key added.
    """
    valid, dropped = [], []
    for lead in leads:
        should_drop, reason = is_junk_lead(lead)
        if should_drop:
            dropped.append({**lead, "drop_reason": reason})
        else:
            valid.append(lead)

    if dropped:
        print(f"[FILTER] Dropped {len(dropped)}/{len(leads)}: "
              f"{[d.get('name','?') for d in dropped[:10]]}")
    return valid, dropped
