import asyncio
from utils.rate_limiter import quota
from utils.request_manager import safe_get
from utils.phone_normalizer import normalize_phone
from services.overpass_scraper  import search_overpass
from services.google_places     import search_google_places
from services.foursquare_places import search_foursquare
from services.here_places       import search_here
from services.deduplicator      import deduplicate

MIN_RESULTS = 15   # Stop waterfall if we already have enough


async def geocode_location(location_str: str) -> tuple[float, float]:
    """Nominatim free geocoding — strictly 1 req/sec."""
    await asyncio.sleep(1)
    result = await safe_get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location_str, "format": "json", "limit": 1},
        is_scrape=True,
    )
    if result and isinstance(result, str):
        import json
        try:
            items = json.loads(result)
            if isinstance(items, list) and len(items) > 0:
                return float(items[0]["lat"]), float(items[0]["lon"])
            else:
                print(f"  ⚠️ Geocoding returned unexpected format: {str(items)[:80]}")
        except Exception as e:
            print(f"  ⚠️ Error parsing geocoding response: {e}")
            pass
    raise ValueError(f"Could not geocode location: '{location_str}'")


def _print_source_result(source: str, count: int, remaining: int | None = None) -> None:
    rem  = f" | {remaining} left" if remaining is not None else ""
    icon = "✅" if count > 0 else "⚠️ "
    print(f"  [{source:<16}] {icon} {count} results{rem}")


def _finalize(leads: list[dict]) -> list[dict]:
    unique = deduplicate(leads)

    for lead in unique:
        lead["phone"] = normalize_phone(lead.get("phone", ""))

    # No-website leads first (highest outreach priority); then by review count desc
    unique.sort(key=lambda x: (x.get("has_website", True), -x.get("review_count", 0)))

    print(f"\n  📊 Raw: {len(leads)} → Deduplicated: {len(unique)}")
    return unique


async def discover_leads(
    business_type: str,
    location: str,
    radius_km: int = 5,
) -> list[dict]:
    """Run the full waterfall across OSM → Google Maps → Foursquare → HERE.

    Returns deduplicated, phone-normalised leads sorted by outreach priority.
    """
    radius_m  = radius_km * 1000
    all_leads: list[dict] = []

    # ── Geocode location (needed for OSM + HERE) ───────────────
    lat, lon = None, None
    try:
        lat, lon = await geocode_location(location)
        print(f"  📍 Geocoded '{location}' → ({lat:.4f}, {lon:.4f})")
    except ValueError as e:
        print(f"  ❌ {e} — OSM and HERE will be skipped")

    # ── Source 1: OSM Overpass (3 mirrors) ────────────────────
    print(f"\n  🗺  [OSM Overpass]   Searching...")
    if lat and lon and any(quota.has_quota(k) for k in
                           ["overpass_main", "overpass_kumi", "overpass_private"]):
        osm = await search_overpass(business_type, lat, lon, radius_m)
        all_leads.extend(osm)
        rem = sum(quota.remaining(k) for k in
                  ["overpass_main", "overpass_kumi", "overpass_private"])
        _print_source_result("OSM Overpass", len(osm), rem)
    else:
        print("  [OSM Overpass]    ⚠️  Quota exhausted or no coordinates")

    if len(all_leads) >= MIN_RESULTS:
        print(f"  ✅ Sufficient results ({len(all_leads)}) — skipping remaining sources")
        return _finalize(all_leads)

    # ── Source 2: Google Maps ─────────────────────────────────
    print(f"  🔵 [Google Maps]     Searching...")
    if quota.has_quota("google_maps"):
        gmaps = await search_google_places(business_type, location, radius_m)
        all_leads.extend(gmaps)
        _print_source_result("Google Maps", len(gmaps), quota.remaining("google_maps"))
    else:
        print("  [Google Maps]     ⚠️  Monthly quota exhausted")

    if len(all_leads) >= MIN_RESULTS:
        return _finalize(all_leads)

    # ── Source 3: Foursquare ──────────────────────────────────
    print(f"  🟣 [Foursquare]      Searching...")
    if quota.has_quota("foursquare"):
        fsq = await search_foursquare(business_type, location, radius_m)
        all_leads.extend(fsq)
        _print_source_result("Foursquare", len(fsq), quota.remaining("foursquare"))
    else:
        print("  [Foursquare]      ⚠️  Monthly quota exhausted")

    if len(all_leads) >= MIN_RESULTS:
        return _finalize(all_leads)

    # ── Source 4: HERE (last resort) ─────────────────────────
    print(f"  🟡 [HERE Places]     Searching...")
    if quota.has_quota("here_places"):
        here = await search_here(business_type, location, radius_m)
        all_leads.extend(here)
        _print_source_result("HERE Places", len(here), quota.remaining("here_places"))
    else:
        print("  [HERE Places]     ⚠️  Daily quota exhausted — resets at midnight")

    return _finalize(all_leads)
