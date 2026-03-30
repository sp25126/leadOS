import asyncio
from utils.rate_limiter import quota
from utils.request_manager import safe_post, OVERPASS_MIRRORS

CATEGORY_MAP = {
    "cafe":        ['"amenity"="cafe"', '"amenity"="coffee_shop"'],
    "restaurant":  ['"amenity"="restaurant"', '"amenity"="fast_food"'],
    "clinic":      ['"amenity"="clinic"', '"amenity"="doctors"', '"healthcare"="clinic"'],
    "hospital":    ['"amenity"="hospital"', '"healthcare"="hospital"'],
    "shop":        ['"shop"="general"', '"shop"="convenience"', '"shop"="clothes"'],
    "salon":       ['"shop"="hairdresser"', '"shop"="beauty"'],
    "gym":         ['"leisure"="fitness_centre"', '"leisure"="sports_centre"'],
    "hotel":       ['"tourism"="hotel"', '"tourism"="guest_house"'],
    "pharmacy":    ['"amenity"="pharmacy"'],
    "school":      ['"amenity"="school"', '"amenity"="college"'],
    "office":      ['"office"="company"', '"office"="it"'],
    "bakery":      ['"shop"="bakery"', '"amenity"="bakery"'],
    "bar":         ['"amenity"="bar"', '"amenity"="pub"'],
    "supermarket": ['"shop"="supermarket"', '"shop"="grocery"'],
    "dentist":     ['"amenity"="dentist"', '"healthcare"="dentist"'],
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
    query   = build_overpass_query(category, lat, lon, radius_m)
    payload = f"data={query}"

    for i, url in enumerate(OVERPASS_MIRRORS):
        key = MIRROR_KEYS[i]
        if not quota.has_quota(key):
            print(f"    [{key}] ⚠️  Quota exhausted, trying next mirror")
            continue

        result = await safe_post(url, data=payload)
        quota.consume(key)

        if result and isinstance(result, dict) and "elements" in result:
            leads = [_parse_element(el) for el in result["elements"] if isinstance(el, dict)]
            leads = [l for l in leads if l is not None]
            if leads:
                return leads
            print(f"    [{key}] ⚠️  0 results, trying next mirror")
        else:
            print(f"    [{key}] ❌ No response or bad format")

        await asyncio.sleep(1)

    return []
