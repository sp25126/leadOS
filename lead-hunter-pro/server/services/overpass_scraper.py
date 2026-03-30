import asyncio
from utils.rate_limiter import quota
from utils.request_manager import safe_post, OVERPASS_MIRRORS

CATEGORY_MAP = {
    "gym": [
        '"leisure"="fitness_centre"',
        '"amenity"="gym"',
        '"sport"="fitness"',
        '"leisure"="fitness_centre"]["sport"="fitness"',
    ],
    "yoga studio": [
        '"leisure"="fitness_centre"]["sport"="yoga"',
        '"amenity"="gym"]["sport"="yoga"',
    ],
    "salon": [
        '"shop"="hairdresser"',
        '"shop"="beauty"',
        '"amenity"="beauty_salon"',
    ],
    "cafe": [
        '"amenity"="cafe"',
        '"amenity"="coffee_shop"',
        '"shop"="coffee"',
    ],
    "restaurant": [
        '"amenity"="restaurant"',
        '"amenity"="fast_food"',
    ],
    "hospital": [
        '"amenity"="hospital"',
        '"amenity"="clinic"',
        '"amenity"="doctors"',
    ],
    "clinic":      ['"amenity"="clinic"', '"amenity"="doctors"', '"healthcare"="clinic"'],
    "pharmacy":    ['"amenity"="pharmacy"'],
    "hotel":       ['"tourism"="hotel"', '"tourism"="guest_house"'],
    "school":      ['"amenity"="school"'],
    "dental":      ['"amenity"="dentist"'],
    "lawyer":      ['"office"="lawyer"'],
    "ca":          ['"office"="accountant"', '"office"="tax_advisor"'],
}

MIRROR_KEYS = ["overpass_main", "overpass_kumi", "overpass_private"]


def build_overpass_query(category: str, lat: float, lon: float, radius_m: int = 5000) -> str:
    tags = CATEGORY_MAP.get(category.lower(), [f'"amenity"="{category}"'])
    union_parts = []
    for tag in tags:
        union_parts.append(f'  node(around:{radius_m},{lat},{lon})[{tag}];')
        union_parts.append(f'  way(around:{radius_m},{lat},{lon})[{tag}];')
    union_body = "\n".join(union_parts)
    return f"[out:json][timeout:25];\n(\n{union_body}\n);\nout body center;"


def _parse_element(el: dict) -> dict | None:
    tags = el.get("tags", {})
    name = tags.get("name", "").strip()
    if not name:
        return None

    lat = el.get("lat") or el.get("center", {}).get("lat", 0)
    lon = el.get("lon") or el.get("center", {}).get("lon", 0)

    phone = (
        tags.get("phone") or tags.get("contact:phone") or
        tags.get("mobile") or tags.get("contact:mobile") or ""
    )
    phone = "".join(c for c in phone if c.isdigit() or c == "+").strip()

    website = tags.get("website") or tags.get("contact:website") or ""
    if website and not website.startswith("http"):
        website = "https://" + website

    return {
        "name":          name,
        "address":       ", ".join(filter(None, [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:city", ""),
            tags.get("addr:state", ""),
        ])),
        "phone":         phone,
        "website":       website,
        "email":         tags.get("email") or tags.get("contact:email") or "",
        "has_website":   bool(website),
        "rating":        0.0,
        "review_count":  0,
        "types":         tags.get("amenity") or tags.get("shop") or tags.get("leisure") or "",
        "opening_hours": tags.get("opening_hours", ""),
        "lat":           lat,
        "lon":           lon,
        "source":        "osm",
    }


async def search_overpass(
    category: str, lat: float, lon: float, radius_m: int = 5000
) -> list[dict]:
    """
    Search Overpass API for leads.
    Auto-expands radius if results are sparse (less than 5).
    """
    current_radius = radius_m
    max_radius = 20000  # Max 20km

    for attempt in range(2): # Try initial, then expand if needed
        query   = build_overpass_query(category, lat, lon, current_radius)
        payload = f"data={query}"

        for i, url in enumerate(OVERPASS_MIRRORS):
            key = MIRROR_KEYS[i]
            if not quota.has_quota(key):
                print(f"    [{key}] [WARN] Quota exhausted, trying next mirror")
                continue

            result = await safe_post(url, data=payload)
            quota.consume(key)

            if result and isinstance(result, dict) and "elements" in result:
                elements = result.get("elements", [])
                leads = [_parse_element(el) for el in elements if isinstance(el, dict)]
                leads = [l for l in leads if l is not None]
                
                # If we have enough leads or we've already tried expanding, return
                if len(leads) >= 5 or current_radius >= max_radius or attempt > 0:
                    if attempt > 0:
                        print(f"    [OSM] Expanded search found {len(leads)} leads.")
                    return leads
                
                print(f"    [OSM] Sparse results ({len(leads)}). Expanding radius...")
                break # Try next attempt with larger radius
            else:
                print(f"    [{key}] [ERROR] No response or bad format")

        current_radius *= 2 # Double radius for next attempt
        if current_radius > max_radius: current_radius = max_radius
        await asyncio.sleep(1)

    return []
