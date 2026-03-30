import httpx
import json
import asyncio
import re
import random
from typing import Optional, List, Dict

GROQ_ENDPOINT   = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

SCORE_PROMPT = """\
You are a senior B2B sales analyst. Analyze this business and return ONLY valid JSON.

Business Name: {name}
Business Type: {business_type}
City: {city}
Address: {address}
Has Website: {has_website}
Website URL: {website}
Has Phone: {has_phone}
Has Social Media: {has_social}
Rating: {rating}
Review Count: {review_count}
Opening Hours: {opening_hours}
Target Service We Sell: {target_service}

Return ONLY this JSON (no markdown, no code blocks, no explanation):
{{
  "score": <integer 1-10>,
  "priority": "<high|medium|low>",
  "pain_points": ["<specific pain point 1>", "<specific pain point 2>"],
  "suggested_opening": "<personalized 1-2 sentence opener mentioning the business name, city, and a specific gap you noticed. Sound like a human, not a bot>",
  "reason": "<2 sentence explanation of why you gave this score>"
}}

Scoring Guide:
- 9-10: No website + active local business + competitive niche (cafe, gym, salon, clinic)
- 7-8: Has basic website but no booking/reviews/social or outdated site
- 5-6: Has some digital presence but gaps exist
- 3-4: Established chain or franchise with good digital presence
- 1-2: Large corporation, government body, or permanently closed

IMPORTANT: The suggested_opening must be personalized to THIS specific business.
Never use "Hi, I came across your business". Reference something specific about them.
"""

async def score_with_groq(lead: dict, groq_key: str, target_service: str) -> Optional[dict]:
    if not groq_key: return None
    
    prompt = SCORE_PROMPT.format(
        name=lead.get("name", "Unknown"),
        business_type=lead.get("types", "business"),
        city=lead.get("city", ""),
        address=lead.get("address", ""),
        has_website=bool(lead.get("website")),
        website=lead.get("website", "none"),
        has_phone=bool(lead.get("phone")),
        has_social=bool(lead.get("social_media") and lead["social_media"] != "{}"),
        rating=lead.get("rating", "unknown"),
        review_count=lead.get("review_count", 0),
        opening_hours=lead.get("opening_hours", "unknown"),
        target_service=target_service,
    )
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                GROQ_ENDPOINT,
                headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                }
            )
            if resp.status_code != 200: 
                print(f"[AI] Groq failed: {resp.status_code} {resp.text[:100]}")
                return None
            
            content = resp.json()["choices"][0]["message"]["content"].strip()
            if "```" in content:
                content = re.sub(r'```(?:json)?', '', content).strip("` \n")
            return json.loads(content)
    except Exception as e:
        print(f"[AI] Groq error: {e}")
        return None

async def score_with_gemini(lead: dict, gemini_key: str, target_service: str) -> Optional[dict]:
    if not gemini_key: return None
    
    prompt = SCORE_PROMPT.format(
        name=lead.get("name", "Unknown"),
        business_type=lead.get("types", "business"),
        city=lead.get("city", ""),
        address=lead.get("address", ""),
        has_website=bool(lead.get("website")),
        website=lead.get("website", "none"),
        has_phone=bool(lead.get("phone")),
        has_social=bool(lead.get("social_media") and lead["social_media"] != "{}"),
        rating=lead.get("rating", "unknown"),
        review_count=lead.get("review_count", 0),
        opening_hours=lead.get("opening_hours", "unknown"),
        target_service=target_service,
    )
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{GEMINI_ENDPOINT}?key={gemini_key}",
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3}}
            )
            if resp.status_code != 200:
                print(f"[AI] Gemini failed: {resp.status_code} {resp.text[:100]}")
                return None
            
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            if "```" in text:
                text = re.sub(r'```(?:json)?', '', text).strip("` \n")
            return json.loads(text)
    except Exception as e:
        print(f"[AI] Gemini error: {e}")
        return None

async def score_leads_batch(
    leads: List[Dict],
    gemini_key: str = "",
    groq_key: str = "",
    target_service: str = "digital marketing",
    concurrency: int = 5
) -> List[Dict]:
    """Score all leads with rate-limit-conscious concurrency."""
    # Log availability at entry
    def has(k): return "PRESENT" if k and len(k) > 5 else "MISSING"
    print(f"[AI] Entry: Gemini={has(gemini_key)}, Groq={has(groq_key)}, Target={target_service}")

    sem = asyncio.Semaphore(concurrency)
    
    async def bounded_score(lead: dict):
        async with sem:
            ai_res = None
            if groq_key:
                ai_res = await score_with_groq(lead, groq_key, target_service)
            if not ai_res and gemini_key:
                ai_res = await score_with_gemini(lead, gemini_key, target_service)
            
            if not ai_res:
                ai_res = _rule_based_score(lead)
                source_label = "Rule-based"
            else:
                source_label = "AI"
            
            return {
                **lead,
                "score": ai_res.get("score", 5),
                "priority": ai_res.get("priority", "medium"),
                "pain_points": ai_res.get("pain_points", ["unknown"]),
                "suggested_opening": ai_res.get("suggested_opening", f"Hi {lead.get('name')}, I saw you in {lead.get('city')} and noticed some gaps in your digital presence."),
                "reason": ai_res.get("reason", f"{source_label} score")
            }

    return list(await asyncio.gather(*[bounded_score(l) for l in leads]))


def _rule_based_score(lead: dict) -> dict:
    """Manual score when no AI keys are present. Varied outputs (no flat 5)."""
    name = lead.get("name", "Business")
    city = lead.get("city", "your city")
    
    score = 4 # Base
    pain_points = []
    
    # 1. Digital Presence Gaps
    if not lead.get("website"):
        score += 3
        pain_points.append("No official website found")
    elif not lead.get("website_live", True):
        score += 2
        pain_points.append("Website appears to be down")
        
    # 2. Social Media Gaps
    social = lead.get("social_media", "{}")
    if social == "{}" or not social:
        score += 2
        pain_points.append("Missing social media links")
        
    # 3. Reputation Metrics
    rating = lead.get("rating", 0.0)
    revs = lead.get("review_count", 0)
    if revs > 0 and rating < 4.0:
        score += 1
        pain_points.append(f"Lower rating ({rating}) compared to neighbors")
    elif revs == 0:
        score += 1
        pain_points.append("Zero online reviews")

    # 4. Final Clamp
    score = max(1, min(10, score))
    priority = "high" if score >= 8 else "medium" if score >= 4 else "low"
    
    # Personalized components
    if "No official website" in pain_points:
        opening = f"I was looking for {name} in {city} but couldn't find your website. Are you currently taking new clients primarily through word-of-mouth?"
    elif "Missing social media" in pain_points:
        opening = f"I noticed {name} has great ratings but your social links seem to be missing. It's making it harder for new people in {city} to find you!"
    else:
        opening = f"I saw {name} while researching top businesses in {city}. I noticed a few ways to boost your online visibility that I'd love to share."

    if not pain_points: pain_points = ["General optimization"]

    return {
        "score": score,
        "priority": priority,
        "pain_points": pain_points,
        "suggested_opening": opening,
        "reason": f"Rule-based analysis ({score}/10) - {', '.join(pain_points[:2])}"
    }
