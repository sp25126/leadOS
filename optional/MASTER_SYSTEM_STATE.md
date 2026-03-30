# LeadOS / Lead Hunter Pro — MASTER SYSTEM STATE

**Date**: March 11, 2024
**Status**: Consolidating for UI Overhaul ("Galaxy Stars" Theme)

---

## 0. System Overview
LeadOS (formerly Lead Hunter Pro) is an AI-powered sales intelligence and automated outreach platform. It automates the entire sales funnel:
1.  **Discovery**: High-speed lead extraction from Google Maps, OpenStreetMap (OSM), Foursquare, and HERE.
2.  **Enrichment**: Multi-tier waterfall extraction of emails, social media, and business pain points using DuckDuckGo OSINT and specialized scrapers.
3.  **Scoring**: AI-driven intent scoring (1-10) using Gemini/Groq to prioritize high-value leads.
4.  **Outreach**: Automated multi-channel messaging via WhatsApp (whatsapp-web.js) and Email (Brevo SMTP).
5.  **Control**: A "Vapi-style" agentic UI and a Telegram bot for mobile command and control.

---

## 1. What is Working ✅
-   **Core Discovery Pipeline**: OSM and Google Maps scrapers are fully functional.
-   **BYOL (Bring Your Own Leads)**: Multipart file upload Supporting CSV, XLSX, XLS, and JSON with auto-normalization of columns and Indian phone numbers.
-   **AI Scoring Engine**: Gemini/Groq integration for analyzing business context.
-   **Enrichment Waterfall**: Snov.io, GetProspect, and DuckDuckGo OSINT fallbacks are wired.
-   **WhatsApp Outreach**: `wa-server` (Node.js) is functional and connects via `whatsapp-web.js`.
-   **Quota Management**: Persistent tracking of API usage limits.
-   **Service Deduplication**: Fuzzy matching to prevent duplicate leads across sources.
-   **FastAPI Backend**: Robust routing, global exception handling, and CORS configuration.

---

## 2. What Failed or is Broken ❌
-   **Gemini API Key**: Recently reported as expired/invalid in logs (needs renewal).
-   **Email Execution (Previously)**: `api/email/send-run-by-source` was a stub in earlier versions (Fix implemented in Phase 9, needs verification in current state).
-   **Baileys vs whatsapp-web.js**: Previous transitions between libraries caused session persistence issues; currently stabilized on `whatsapp-web.js`.
-   **Frontend UI Wipe**: The original UI has been wiped to make way for the Galactic redesign; currently in a placeholder/reconstruction state.

---

## 3. What is Partially Built ⚠️
-   **Multi-User SaaS Auth**: NextAuth.js v5 configured with GitHub/Google, but full session persistence for BYOK (Bring Your Own Key) is partially client-side (localStorage).
-   **AI Orchestrator**: `actions` contract (NAVIGATE, API_CALL) exists but requires tighter frontend-backend synchronization.
-   **Circuit Breaker**: Enrichment breaker resets on server restart (backported persistence needed).

---

## 4. Planned but Never Executed 📋
-   **India SaaS Mega-Feed**: Automation of 20+ India-specific sources (YourStory, Inc42).
-   **Trojan Horse Partner Offer**: Automated 10-20% referral tracking in the DB.
-   **Autonomous AI Behaviors**: Fully hands-off "ingest -> enrich -> score -> send" loop without user confirmation.
-   **Voice Agent Integration**: Vapi/Twilio call triggers (defined in Colab tests but not in main app).

---

## 5. Backend Complete API Inventory
| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/health` | GET | System health & service status |
| `/api/quota/status` | GET | Remaining API credits |
| `/api/leads/search` | POST | Live discovery search |
| `/api/leads/{id}/download`| GET | Export leads to CSV |
| `/api/leads/upload` | POST | Bulk import (CSV/Excel) |
| `/api/leads` | GET | CRM/Dashboard data |
| `/api/outreach/start` | POST | Initiate WA/Email campaign |
| `/api/outreach/status/{id}`| GET | Real-time campaign progress |
| `/api/email/skip-report` | GET | List leads blocked by junk filters |
| `/api/email/send-run-by-source`| POST | 10-per-source smart outreach |
| `/api/enrich/run` | POST | Trigger enrichment batch |
| `/api/score/run` | POST | Trigger AI scoring batch |
| `/api/agent/chat` | POST | AI Copilot (returns messages + actions) |

---

## 6. Frontend Route Map (v2)
-   `/login`: Auth portal (Google/GitHub).
-   `/leados/dashboard`: Main command center.
-   `/leados/ingest`: Discovery & Upload controls.
-   `/leados/outreach`: Campaign management & WA status.
-   `/leados/history`: Past lead sessions (IndexedDB).
-   `/leados/settings`: BYOK Key Management (AES-256 encrypted).
-   `/leados/refer`: Partner tracking.
-   `/hire-me`: Professional services contact.

---

## 7. External Services & API Keys
-   **AI**: Gemini, Groq, OpenRouter, OpenAI, Ollama (Local).
-   **Discovery**: Google Maps, Foursquare, HERE, Overpass (OSM).
-   **Enrichment**: Hunter.io, Snov.io, GetProspect.
-   **Outreach**: Brevo (SMTP), `wa-server` (Local instance).
-   **Storage**: Supabase (Postgres), Local CSV, Browser IndexedDB.

---

## 8. Known Technical Debt & Security Issues
-   **CORS**: Currently set to `allow_origins=["*"]` (Development mode).
-   **Auth**: Stateless backend relies on `X-API-Key` headers; no server-side session store.
-   **Database**: Heavy reliance on CSV files for session state (concurrency risk).
-   **Code Fragmentation**: Previous "Phases" have left some dead imports and shadowed functions.

---

## 9. Architecture Diagram (ASCII)
```text
[Browser (Next.js 14)] <--- HTTPS ---> [FastAPI Backend (Py 3.11)]
      |                                      |
      | (LocalStorage Keys)                  |--- [Supabase DB]
      |                                      |--- [Gemini/Groq API]
      |                                      |--- [Brevo SMTP]
      |--- [wa-server (Node)] <--- Socket ---> [WhatsApp Phone]
```

---

## 10. Immediate Action Plan (Next 5 Sessions)
1.  **Galactic Star UI**: Rebuild `web/` with the premium stars/bubble particles theme.
2.  **Portfolio Card**: Restore the "V1 Card" with photo and cinematic animations.
3.  **Auth Hardening**: Transition to a more robust middleware-based auth.
4.  **Service Sync**: Ensure all API endpoints match the new `/leados` route structure.
5.  **Production Gate**: Run full QA suite before Oracle Cloud deployment.

---

## 11. Complete File Tree
-   `server/`: FastAPI Backend.
-   `web/`: Next.js 14 Frontend.
-   `wa-server/`: Node.js WhatsApp Bridge.
-   `output/`: CSV Session Storage.
-   `tests/`: Phase-based test suites.
-   `deploy/`: Docker & Nginx configs.

---

## 12. Environment Variables Master List
-   `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, `GITHUB_ID`, `GOOGLE_ID`.
-   `DATABASE_URL`, `SUPABASE_KEY`, `SUPABASE_URL`.
-   `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENROUTER_API_KEY`.
-   `GOOGLE_MAPS_API_KEY`, `BREVO_API_KEY`.
-   `WA_SERVER_URL`, `NEXT_PUBLIC_API_URL`.
