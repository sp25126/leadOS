import json
import asyncio
import re
import os
from rapidfuzz import fuzz
import google.generativeai as genai
from services.llm_gateway import call_llm

SCORING_PROMPT = """
You are a Lead Generation & Sales Specialist for {target_service}.
Your goal is to evaluate if the business below is a GOOD fit for your offer.

Target Persona: {target_service}
Business Data:
{leads_json}

Strict Scoring Criteria (1-10):
- 10: High intent, high reviews, but NO website OR very broken website.
- 8-9: Competitive niche (Gym, Cafe, Clinic), decent reviews, but website is old/non-responsive.
- 5-7: Standard business, has website, but could use specific automation/features.
- 1-4: Already has a great tech stack / high-end website / wrong industry.

Analyze the data and return a JSON ARRAY of objects.
Each object MUST have:
1. "name": The exact name of the business.
2. "score": Int (1-10).
3. "reason": Why this score? Mention specific data points (e.g., "Has 200 reviews but no website").
4. "priority": "high" (8-10), "medium" (5-7), or "low" (1-4).
5. "pain_points": List of 2-3 specific business struggles they likely face.
6. "suggested_opening": A personalized, high-conversion first line for an email/WhatsApp. 
   - DO NOT say "Hi, I noticed your website...". 
   - DO say something like "I saw [Business Name] has incredible reviews in [City], but it looks like you're missing out on direct bookings..."

Return ONLY the raw JSON array.
"""

SAFE_FALLBACK_SCORE = {
    "score":             5,
    "reason":            "Could not score - manual review needed",
    "priority":          "medium",
    "pain_points":       ["unknown"],
    "suggested_opening": "Hi, I came across your business and wanted to reach out.",
}

LEAD_FIELDS_FOR_SCORING = [
    "name", "types", "has_website", "website", "rating",
    "review_count", "tech_hints", "address", "opening_hours",
    "social_media", "has_contact_form", "merged_sources", "city"
]


def _strip_fences(text: str) -> str:
    """Remove markdown code fences from Gemini response."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.MULTILINE)
    text = re.sub(r"```$",          "", text, flags=re.MULTILINE)
    return text.strip()


def _slim_lead(lead: dict) -> dict:
    """Send only scoring-relevant fields to Gemini - saves tokens."""
    return {k: lead.get(k, "") for k in LEAD_FIELDS_FOR_SCORING}


def _match_by_name(name: str, scored_items: list[dict]) -> dict | None:
    """Fuzzy-match Gemini response item back to original lead by name."""
    best_score = 0
    best_match = None
    name_clean = name.lower().strip()
    for item in scored_items:
        if not isinstance(item, dict):
            continue
        item_name = item.get("name", "").lower().strip()
        sim = fuzz.ratio(name_clean, item_name)
        if sim > best_score:
            best_score = sim
            best_match = item
    return best_match if best_score >= 70 else None


async def _score_batch(
    batch: list[dict],
    target_service: str,
    gemini_key: str = "",
    groq_key: str = "",
) -> list[dict]:
    """Score a batch of up to 5 leads in one LLM call."""
    slim_batch = [_slim_lead(l) for l in batch]
    prompt     = SCORING_PROMPT.format(
        target_service=target_service,
        leads_json=json.dumps(slim_batch, ensure_ascii=False, indent=2)
    )

    try:
        response_text = await call_llm(
            prompt, 
            expect_json=True, 
            gemini_key=gemini_key, 
            groq_key=groq_key
        )
        raw_text = _strip_fences(response_text)
        scored_raw = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"  [Scorer]    JSON parse error: {e} - applying fallback to batch")
        scored_raw = []
    except Exception as e:
        print(f"  [Scorer]   AI error: {e} - applying fallback to batch")
        scored_raw = []

    # Match output back to original leads
    results = []
    if not isinstance(scored_raw, list):
        scored_raw = []

    for lead in batch:
        enriched = lead.copy()
        matched  = _match_by_name(lead.get("name", ""), scored_raw)
        if matched and isinstance(matched, dict):
            try:
                enriched["score"]             = int(matched.get("score", 5))
                enriched["reason"]            = matched.get("reason", "")
                enriched["priority"]          = matched.get("priority", "medium")
                enriched["pain_points"]       = matched.get("pain_points", [])
                enriched["suggested_opening"] = matched.get("suggested_opening", "")
            except (ValueError, TypeError):
                enriched.update(SAFE_FALLBACK_SCORE)
        else:
            enriched.update(SAFE_FALLBACK_SCORE)
        results.append(enriched)

    return results


async def score_leads(
    leads: list[dict],
    target_service: str = "website and AI automation",
    gemini_key: str = "",
    groq_key: str = "",
) -> list[dict]:
    """
    Score all leads in batches of 5.
    Returns leads sorted: high -> medium -> low, then score descending.
    """
    if not leads:
        return []

    BATCH_SIZE    = 5
    all_scored    = []
    total         = len(leads)

    print(f"\n    Scoring {total} leads in batches of {BATCH_SIZE}...")

    for i in range(0, total, BATCH_SIZE):
        batch         = leads[i : i + BATCH_SIZE]
        batch_num     = (i // BATCH_SIZE) + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} leads)...", end=" ")

        scored = await _score_batch(batch, target_service, gemini_key, groq_key)
        all_scored.extend(scored)

        print(f"  scored [{', '.join(str(l['score']) for l in scored)}]")

    # Sort: priority order then score descending
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_scored.sort(key=lambda x: (
        priority_order.get(x.get("priority", "medium"), 1),
        -x.get("score", 0)
    ))

    high   = sum(1 for l in all_scored if l.get("priority") == "high")
    medium = sum(1 for l in all_scored if l.get("priority") == "medium")
    low    = sum(1 for l in all_scored if l.get("priority") == "low")
    print(f"\n    Scoring done ->   {high} high |   {medium} medium |   {low} low")

    return all_scored


async def score_single_lead(
    lead: dict,
    target_service: str = "website and AI automation",
    gemini_key: str = "",
    groq_key: str = "",
) -> dict:
    """Score a single lead - used by Telegram bot for quick preview."""
    results = await _score_batch([lead], target_service, gemini_key, groq_key)
    return results[0] if results else {**lead, **SAFE_FALLBACK_SCORE}

