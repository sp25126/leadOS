import pytest
import json
from unittest.mock import patch, MagicMock


#   Helpers  
def make_lead(name, has_website=False, rating=4.5, reviews=200, tech=""):
    return {
        "name": name, "has_website": has_website, "rating": rating,
        "review_count": reviews, "types": "cafe", "tech_hints": tech,
        "address": "Test Street, Ahmedabad", "website": "",
        "opening_hours": "", "social_media": "", "has_contact_form": False,
        "merged_sources": "osm", "phone": "", "email": "", "source": "osm",
    }

def make_gemini_response(scored_list: list[dict]):
    mock_resp      = MagicMock()
    mock_resp.text = json.dumps(scored_list)
    return mock_resp


#   Tests  
class TestLeadScorer:

    @pytest.mark.asyncio
    async def test_returns_same_count_as_input(self):
        from services.lead_scorer import score_leads
        leads = [make_lead(f"Cafe {i}") for i in range(3)]
        mock_scores = [
            {"name": f"Cafe {i}", "score": 8, "reason": "test",
             "priority": "high", "pain_points": [], "suggested_opening": "Hi"}
            for i in range(3)
        ]
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.return_value = make_gemini_response(mock_scores)
            result = await score_leads(leads)
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_high_priority_sorted_first(self):
        from services.lead_scorer import score_leads
        leads = [make_lead("Low Cafe"), make_lead("High Cafe")]
        mock_scores = [
            {"name": "Low Cafe",  "score": 3, "reason": "r",
             "priority": "low",  "pain_points": [], "suggested_opening": "Hi"},
            {"name": "High Cafe", "score": 9, "reason": "r",
             "priority": "high", "pain_points": [], "suggested_opening": "Hi"},
        ]
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.return_value = make_gemini_response(mock_scores)
            result = await score_leads(leads)
        assert result[0]["name"] == "High Cafe"
        assert result[-1]["name"] == "Low Cafe"

    @pytest.mark.asyncio
    async def test_fallback_applied_on_gemini_error(self):
        from services.lead_scorer import score_leads
        leads = [make_lead("Mystery Cafe")]
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.side_effect = Exception("API error")
            result = await score_leads(leads)
        assert len(result) == 1
        assert result[0]["score"]    == 5
        assert result[0]["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_fallback_on_bad_json(self):
        from services.lead_scorer import score_leads
        leads = [make_lead("Broken Cafe")]
        mock_resp      = MagicMock()
        mock_resp.text = "```json\nThis is not valid JSON\n```"
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.return_value = mock_resp
            result = await score_leads(leads)
        assert result[0]["score"] == 5  # fallback score

    @pytest.mark.asyncio
    async def test_markdown_fences_stripped(self):
        from services.lead_scorer import _strip_fences
        raw = "```json\n[{\"name\": \"test\"}]\n```"
        assert _strip_fences(raw) == '[{"name": "test"}]'

    @pytest.mark.asyncio
    async def test_fuzzy_name_matching(self):
        from services.lead_scorer import _match_by_name
        scored = [{"name": "Green Leaf Cafe Ahmedabad", "score": 9}]
        result = _match_by_name("Green Leaf Cafe", scored)
        assert result is not None
        assert result["score"] == 9

    @pytest.mark.asyncio
    async def test_no_match_returns_none(self):
        from services.lead_scorer import _match_by_name
        scored = [{"name": "Totally Different Place", "score": 7}]
        result = _match_by_name("Green Leaf Cafe", scored)
        assert result is None

    @pytest.mark.asyncio
    async def test_score_single_lead(self):
        from services.lead_scorer import score_single_lead
        lead = make_lead("Solo Cafe")
        mock_scores = [{"name": "Solo Cafe", "score": 8, "reason": "no website",
                        "priority": "high", "pain_points": ["no website"],
                        "suggested_opening": "Hi Solo"}]
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.return_value = make_gemini_response(mock_scores)
            result = await score_single_lead(lead)
        assert result["score"]    == 8
        assert result["priority"] == "high"

    @pytest.mark.asyncio
    async def test_empty_input_returns_empty(self):
        from services.lead_scorer import score_leads
        result = await score_leads([])
        assert result == []

    @pytest.mark.asyncio
    async def test_score_field_is_int(self):
        from services.lead_scorer import score_leads
        leads = [make_lead("Type Test Cafe")]
        mock_scores = [{"name": "Type Test Cafe", "score": "9",  # string from Gemini
                        "reason": "r", "priority": "high",
                        "pain_points": [], "suggested_opening": "Hi"}]
        with patch("services.lead_scorer._model") as mock_model:
            mock_model.generate_content.return_value = make_gemini_response(mock_scores)
            result = await score_leads(leads)
        assert isinstance(result[0]["score"], int)  # must be cast to int
