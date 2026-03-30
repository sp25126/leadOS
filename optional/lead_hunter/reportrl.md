# LEADOS — BACKEND ENRICHMENT OVERHAUL REPORT

## 1. Executive Summary
The backend lead generation and enrichment pipeline has been completely overhauled to solve the critical data quality issues identified during testing. The system now uses a **5-stage Waterfall Enrichment** model that prioritizes business-only candidates, captures real contact data via Google Maps and DuckDuckGo, and scores leads using personalized AI context.

---

## 2. Infrastructure Fixes (BYOK Key Wiring)
- **File:** `server/utils/request_credentials.py`
- **Change:** Implemented a unified `RequestCredentials` dataclass that pulls API keys directly from request headers (`X-Gemini-Key`, `X-Groq-Key`, `X-Google-Maps-Key`).
- **Result:** AI Scoring and Google Maps searches now correctly use the user's keys, resolving "403 Forbidden" errors for missing or invalid environment variables.

---

## 3. Data Quality & Enrichment Overhaul

### **Stage 0: Pre-Enrichment Junk Filter**
- **File:** `server/services/lead_filter.py`
- **Fix:** Implemented pattern-based filtering to drop "Police Stations", "Canteens", "Hostels", and "Government Offices" *before* wasting enrichment resources.
- **Metric:** Expected to drop ~20% of low-quality OSM candidates.

### **Stage 1 & 2: Contact Waterfall (G-Maps + DDG)**
- **Fix:** 
    - **Google Maps Enricher:** Captures phone numbers, business ratings, and opening hours for leads missing phone data.
    - **DuckDuckGo OSINT Scraper:** Actively hunts for missing emails and social media handles (Instagram, FB, LinkedIn) using a multi-threaded scraper.
- **Result:** Phone coverage projected to increase from 36% to >70% for Indian SMBs.

### **Stage 3 & 4: Contact Discovery & Validation**
- **Fix:** 
    - **Website Scraper:** Updated to prioritize "Contact" and "About" page discovery.
    - **Email Quality Filter:** New scoring system (0-3) that explicitly rejects "dns@facebook.com", "SOA", and generic admin emails.
- **Result:** Status "READY" is now reserved for contactable leads with high-confidence data.

---

## 4. AI Scoring & Personalization (Stage 5)
- **File:** `server/services/ai_scorer.py`
- **Fix:** 
    - Removed static "5.0" scores.
    - Implemented a sales-first prompt that identifies specific "Pain Points" and generates "Suggested Openings" tailored to the business category.
    - Added a robust multi-provider support (Groq/Gemini) with rule-based fallback if all providers fail.
- **Result:** Accurate lead prioritization (High/Medium/Low) based on revenue potential and digital presence.

---

## 5. Category Map Refinement
- **File:** `server/services/overpass_scraper.py`
- **Fix:** Refined `CATEGORY_MAP` to prevent "Gym" searches from returning "Sports Centres". 
- **New Tags:** 
    - `gym`: `["leisure"="fitness_centre", "sport"="fitness"]`
    - `yoga studio`: `["sport"="yoga"]`
    - `salon`: `["shop"="hairdresser" or "shop"="beauty"]`
    - `cafe`: `["amenity"="cafe" or "cuisine"~"coffee"]`

---

## 6. Verification Checklist
- [x] **BYOK Keys:** Verified wiring for Groq/Gemini headers.
- [x] **Gym Results:** Filtered for fitness-specific tags.
- [x] **Junk Filter:** Checked against "Canteen Pune" test case.
- [x] **Scoring Accuracy:** Scores are now dynamic based on AI analysis.
- [x] **Email Filtering:** Generic DNS records are rejected.

**Report Generated:** March 20, 2026
**LeadOS Systems Engineering**
