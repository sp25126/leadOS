import re
from rapidfuzz import fuzz

def normalize_name(name: str) -> str:
    """Strip common suffixes and normalize."""
    name = name.lower().strip()
    # Remove punctuation
    name = re.sub(r"[^\w\s]", " ", name)
    stopwords = ["pvt", "ltd", "inc", "llc", "co", "the", "and",
                 "cafe", "shop", "store", "centre", "center", "&"]
    for w in stopwords:
        name = re.sub(rf'\b{w}\b', '', name)
    return re.sub(r'\s+', ' ', name).strip()

def is_duplicate(a: dict, b: dict, threshold: int = 85) -> bool:
    """Return True if two leads refer to the same business."""
    # 1. Exact website match (fastest check)
    wa, wb = a.get("website","") or "", b.get("website","") or ""
    if wa and wb and wa.rstrip("/") == wb.rstrip("/"):
        return True

    # 2. Exact phone match (strong signal)
    pa = "".join(c for c in a.get("phone","") or "" if c.isdigit())[-10:]
    pb = "".join(c for c in b.get("phone","") or "" if c.isdigit())[-10:]
    if pa and pb and pa == pb and len(pa) >= 10:
        return True

    # 3. Fuzzy name match (catches "Google" vs "Google Inc.")
    na = normalize_name(a.get("name","") or "")
    nb = normalize_name(b.get("name","") or "")
    if na and nb and fuzz.ratio(na, nb) >= threshold:
        # Confirm with city/address to avoid false positives
        city_a = (a.get("address","") or "").lower()
        city_b = (b.get("address","") or "").lower()
        if not city_a or not city_b:
            return True  # No location to disambiguate - assume duplicate
        addr_sim = fuzz.partial_ratio(city_a, city_b)
        return addr_sim >= 60

    return False

def deduplicate(leads: list[dict]) -> list[dict]:
    """Preserve first occurrence and merge data from duplicates."""
    unique: list[dict] = []
    for lead in leads:
        matched = False
        for seen in unique:
            if is_duplicate(lead, seen):
                # Merge source info
                existing_sources = seen.get("merged_sources", seen.get("source", ""))
                new_source       = lead.get("source", "")
                if new_source and new_source not in existing_sources:
                    seen["merged_sources"] = f"{existing_sources}, {new_source}"
                
                # Keep better data: prefer non-empty phone/website/email
                for field in ["phone", "website", "email", "rating", "review_count"]:
                    if not seen.get(field) and lead.get(field):
                        seen[field] = lead[field]
                        if field == "website": seen["has_website"] = True
                
                matched = True
                break

        if not matched:
            lead_copy = lead.copy()
            lead_copy["merged_sources"] = lead.get("source", "")
            unique.append(lead_copy)

    return unique
