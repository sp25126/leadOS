import re

# ============================================================
# EMAIL QUALITY & VALIDATION
# ============================================================

# DNS infrastructure addresses - NEVER real business emails
DNS_INFRASTRUCTURE_EMAILS = {
    'dns@facebook.com', 'abuse@facebook.com', 'postmaster@facebook.com',
    'dns@google.com', 'noreply@google.com', 'dns-admin@google.com',
    'hostmaster@google.com', 'postmaster@google.com',
}

# Domains that are strictly for testing or placeholders
PLACEHOLDER_DOMAINS = {
    'example.com', 'test.com', 'domain.com', 'website.com',
    'placeholder.com', 'temp.com', 'mailinator.com', 'guerrillamail.com'
}

# Specific full emails that are placeholders
KNOWN_FAKE_EMAILS = {
    'user@domain.com', 'email@domain.com', 'test@test.com',
    'john@doe.com', 'admin@website.com', 'info@website.com'
}

# Generic prefixes that almost never reach a decision maker
JUNK_PREFIXES = {
    'info', 'contact', 'hello', 'support', 'admin', 'sales',
    'noreply', 'no-reply', 'webmaster', 'feedback', 'help',
    'service', 'mail', 'email', 'enquiry', 'enquiries',
    'query', 'queries', 'dns', 'postmaster', 'abuse',
    'hostmaster', 'webinfo', 'office', 'general',
}

# Unreliable extraction sources
UNRELIABLE_SOURCES = ['soa_dns', 'mx_record', 'whois']


def score_email_quality(email: str, source: str = "") -> int:
    """
    Returns 0-3 quality score:
    0 = Invalid / DNS record / placeholder / junk
    1 = Generic business email (info@, contact@)
    2 = Likely real but unverified  
    3 = High confidence personal/direct email
    """
    if not email or '@' not in email:
        return 0
    
    email_lower = email.lower().strip()
    
    # Check hard-reject lists
    if email_lower in DNS_INFRASTRUCTURE_EMAILS: return 0
    if email_lower in KNOWN_FAKE_EMAILS: return 0
    if source in UNRELIABLE_SOURCES: return 0
    
    parts = email_lower.split('@')
    if len(parts) != 2: return 0
    prefix, domain = parts
    
    # Reject placeholder domains
    if domain in PLACEHOLDER_DOMAINS:
        return 0
    
    # Reject DNS-pattern prefixes
    if re.match(r'^dns\b|^ns\d*\b', prefix):
        return 0
    
    # Score 1: Generic junk prefixes
    if prefix in JUNK_PREFIXES:
        return 1
    
    # Score 3: Personal name pattern (e.g., saumya.patel@...)
    # But ONLY if from a high-quality source
    personal_pattern = re.compile(r'^[a-z]+\.[a-z]+@', re.IGNORECASE)
    if personal_pattern.match(email_lower) and source in ['website_scrape', 'hunter', 'manual']:
        return 3
    
    # Score 2: Everything else that passed (e.g. name@company.com or brand@gmail.com)
    return 2


def determine_lead_status(lead: dict) -> str:
    """Determine lead readiness based on contact data quality."""
    phone = lead.get("phone", "")
    email = lead.get("email", "")
    email_score = lead.get("email_quality_score", 0)
    
    has_real_phone = bool(phone) and len(re.sub(r'\D', '', str(phone))) >= 10
    has_real_email = bool(email) and email_score >= 2
    
    if has_real_phone or has_real_email:
        return "READY"
    elif lead.get("website"):
        return "PARTIAL"
    else:
        return "NEW"
