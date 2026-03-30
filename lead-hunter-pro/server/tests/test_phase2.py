import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock

from services.overpass_scraper import build_overpass_query, _parse_element, search_overpass
from services.source_manager   import discover_leads, _finalize, MIN_RESULTS


#   Overpass tests  

class TestOverpass:
    def test_build_query_contains_category(self):
        q = build_overpass_query("cafe", 23.0, 72.0)
        assert "cafe" in q
        assert "23.0" in q
        assert "72.0" in q

    def test_unsupported_category_still_builds(self):
        q = build_overpass_query("unknown_biz", 0.0, 0.0)
        assert "unknown_biz" in q
        assert "[out:json]" in q

    @pytest.mark.asyncio
    async def test_search_returns_list_on_error(self):
        """All mirrors fail -> empty list returned, no exception raised."""
        with patch("services.overpass_scraper.safe_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = None
            result = await search_overpass("cafe", 23.0, 72.0)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_parses_valid_response(self):
        fake_response = {
            "elements": [
                {
                    "type": "node",
                    "lat": 23.01,
                    "lon": 72.01,
                    "tags": {
                        "name": "Test Cafe",
                        "amenity": "cafe",
                        "phone": "+919876543210",
                    },
                }
            ]
        }
        with patch("services.overpass_scraper.safe_post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = fake_response
            result = await search_overpass("cafe", 23.0, 72.0)

        assert len(result) == 1
        assert result[0]["name"] == "Test Cafe"
        assert result[0]["source"] == "osm"

    def test_skips_elements_without_name(self):
        el_no_name = {"type": "node", "lat": 0, "lon": 0, "tags": {"amenity": "cafe"}}
        assert _parse_element(el_no_name) is None

        el_with_name = {"type": "node", "lat": 0, "lon": 0, "tags": {"name": "My Shop"}}
        assert _parse_element(el_with_name) is not None


#   Source manager tests  

class TestSourceManager:
    @pytest.mark.asyncio
    async def test_returns_list_when_all_sources_empty(self):
        """When all APIs return nothing, discover_leads returns []."""
        with (
            patch("services.source_manager.geocode_location", new_callable=AsyncMock, side_effect=ValueError("no coords")),
            patch("services.source_manager.search_google_places", new_callable=AsyncMock, return_value=[]),
            patch("services.source_manager.search_foursquare",    new_callable=AsyncMock, return_value=[]),
            patch("services.source_manager.search_here",          new_callable=AsyncMock, return_value=[]),
        ):
            result = await discover_leads("cafe", "Unknown City")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_stops_after_sufficient_results(self):
        """If OSM returns   MIN_RESULTS leads, Google/FSQ/HERE are not called."""
        words = ["Apple", "Banana", "Cherry", "Dog", "Elephant", "Frog", "Giraffe", "Hat", "Igloo", "Jump", "Kite", "Lemon", "Monkey", "Nest", "Orange", "Penguin", "Queen", "Rabbit", "Snake", "Tiger", "Umbrella", "Violin"]
        fake_leads = [
            {"name": words[i % len(words)], "address": "",
             "phone": "", "website": "", "email": "", "has_website": False,
             "rating": 0.0, "review_count": 0, "types": "", "opening_hours": "",
             "lat": 0, "lon": 0, "source": "osm"}
            for i in range(MIN_RESULTS + 5)
        ]

        with (
            patch("services.source_manager.geocode_location",
                  new_callable=AsyncMock, return_value=(23.0, 72.0)),
            patch("services.source_manager.search_overpass",
                  new_callable=AsyncMock, return_value=fake_leads),
            patch("services.source_manager.search_google_places",
                  new_callable=AsyncMock, return_value=[]) as mock_gmaps,
            patch("services.source_manager.search_foursquare",
                  new_callable=AsyncMock, return_value=[]) as mock_fsq,
            patch("services.source_manager.search_here",
                  new_callable=AsyncMock, return_value=[]) as mock_here,
            patch("services.source_manager.quota.has_quota", return_value=True),
        ):
            result = await discover_leads("cafe", "Ahmedabad")

        mock_gmaps.assert_not_called()
        mock_fsq.assert_not_called()
        mock_here.assert_not_called()
        assert len(result) >= MIN_RESULTS

    def test_no_website_leads_sorted_first(self):
        leads = [
            {"name": "A", "address": "X", "phone": "", "website": "http://a.com",
             "email": "", "has_website": True,  "rating": 4.5, "review_count": 100,
             "types": "", "opening_hours": "", "lat": 0, "lon": 0, "source": "osm"},
            {"name": "B", "address": "Y", "phone": "", "website": "",
             "email": "", "has_website": False, "rating": 3.0, "review_count": 20,
             "types": "", "opening_hours": "", "lat": 0, "lon": 0, "source": "osm"},
            {"name": "C", "address": "Z", "phone": "", "website": "",
             "email": "", "has_website": False, "rating": 4.0, "review_count": 50,
             "types": "", "opening_hours": "", "lat": 0, "lon": 0, "source": "osm"},
        ]
        result = _finalize(leads)
        # First results must all be no-website leads
        no_website = [r for r in result if not r["has_website"]]
        has_website = [r for r in result if r["has_website"]]
        if no_website and has_website:
            assert result.index(no_website[0]) < result.index(has_website[0])
