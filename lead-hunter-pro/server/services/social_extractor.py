import re
from typing import Optional, Dict

# ============================================================
# SOCIAL MEDIA EXTRACTION + VALIDATION
# ============================================================

# Raw URL patterns
_SOCIAL_URL_PATTERNS = {
    "instagram": re.compile(
        r'instagram\.com/([A-Za-z0-9_.]{3,30})(?:[/?]|$)',
        re.IGNORECASE
    ),
    "facebook": re.compile(
        r'facebook\.com/(?!(?:sharer|share|dialog|login|signup|'
        r'help|pages/create|events|groups|marketplace|'
        r'watch|gaming|pages$|profile\.php|people|'
        r'tr$|pg/|ads/|business/|policies|'
        r'\d{4}$|photo|photos|video|videos|posts|'
        r'story|stories|hashtag|search|home\.php|'
        r'messages|notifications|settings|'
        r'friends|find-friends))([A-Za-z0-9._%\-]{3,50})(?:[/?]|$)',
        re.IGNORECASE
    ),
    "twitter": re.compile(
        r'(?:twitter|x)\.com/(?!(?:intent|share|search|'
        r'home|login|signup|i/|hashtag|explore|'
        r'notifications|messages|settings|'
        r'privacy|tos|about))([A-Za-z0-9_]{3,15})(?:[/?]|$)',
        re.IGNORECASE
    ),
    "linkedin": re.compile(
        r'linkedin\.com/(?:company|in)/([A-Za-z0-9_\-]{3,50})(?:[/?]|$)',
        re.IGNORECASE
    ),
    "youtube": re.compile(
        r'youtube\.com/(?:@|channel/UC|c/|user/)?([A-Za-z0-9_\-]{3,50})(?:[/?]|$)',
        re.IGNORECASE
    ),
}

# Handles that look extracted but are navigation/UI elements
_JUNK_HANDLES = {
    # Facebook
    "profile.php", "people", "pages", "events", "groups",
    "marketplace", "watch", "gaming", "home", "login",
    "share", "sharer", "dialog", "tr", "pg",
    # Generic numbers
    "2008", "2009", "2010", "2011", "2012", "2013",
    "2014", "2015", "2016", "2017", "2018", "2019",
    "2020", "2021", "2022", "2023", "2024", "2025",
    # Twitter/X
    "home", "explore", "notifications", "messages",
    "i", "intent", "search", "hashtag",
}

# Handle must be 3+ chars and not a junk string
_HANDLE_MIN_LENGTH = 3
_HANDLE_LOOKS_REAL_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_.]{2,}$')


def extract_social_handles(html_or_text: str) -> Dict[str, str]:
    """
    Extract and validate social media handles from HTML or plain text.
    Returns dict like: {'instagram': 'mybusiness', 'facebook': 'mybusiness'}
    Only returns handles that look like real business pages.
    """
    handles = {}

    for platform, pattern in _SOCIAL_URL_PATTERNS.items():
        matches = pattern.finditer(html_or_text)
        for match in matches:
            handle = match.group(1).strip("/").strip()

            if len(handle) < _HANDLE_MIN_LENGTH:
                continue

            if handle.lower() in _JUNK_HANDLES:
                continue

            if not _HANDLE_LOOKS_REAL_RE.match(handle):
                continue

            # Found a good one, take the first unique one per platform
            if platform not in handles:
                handles[platform] = handle

    return handles


def format_social_for_csv(handles: Dict) -> str:
    """Format social handles dict as string for CSV storage."""
    if not handles:
        return ""
    return str(handles)
