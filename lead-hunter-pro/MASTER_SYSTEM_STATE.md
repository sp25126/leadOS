# LEADOS MASTER SYSTEM STATE — GROUNDED SOURCE OF TRUTH
Generated on: 2026-03-20

## 📍 SYSTEM CORE STATUS
| Component | Status | Internal Port | Connectivity |
| :--- | :--- | :--- | :--- |
| FastAPI Backend | ACTIVE | 8000 | Healthy |
| WhatsApp Bridge | STOPPED | 3001 | Needs Restart |
| Next.js Frontend | STANDBY | 3000 | Under Reconstruction |
| Supabase DB | FAILED | 5432 | Auth/Project Unreachable |

## 🔑 API KEY INVENTORY (VERIFIED)
- **GEMINI_API_KEY**: 🔴 EXPIRED (403)
- **GROQ_API_KEY**: 🔴 INVALID (401 Auth)
- **GOOG_MAPS_KEY**: 🟢 VALID
- **BREVO_API_KEY**: 🔴 MISSING
- **INTERNAL_API_KEY**: 🟢 VALID (`saumyavishwam@gmail` in master.key)

## 🏗️ DATABASE STATE
- **Primary**: Supabase (postgresql+asyncpg). Currently failing to connect.
- **Secondary (Fallback)**: CSV files in `server/output/`. 
- **Migration Status**: Models and DB logic are implemented in `database.py` and `models.py`.

## 🔄 PIPELINE STATUS
- **Lead Discovery**: 🟢 STABLE (Multiple sources supported).
- **Lead Enrichment**: 🟡 PARTIAL (Web scrapers OK, OSINT Waterfall OK).
- **AI Scoring**: 🔴 FAILED (Defaulting to 5).
- **Outreach Ops**: 🟡 PARTIAL (Dry runs pass, live outreach requires keys).

## 📊 CURRENT DATA ASSETS
- `leads_restaurant_ahmedabad_1773991215.csv` (36 leads)
- `leads_cafe_pune_1773991241.csv` (36 leads)
- `leads_gym_ahmedabad_1773991591.csv` (36 leads - First session-id-enabled capture)

## 🛠️ REORGANIZATION REQS
1. **Restore AI**: Update `llm_gateway.py` with valid keys.
2. **Stable Storage**: Switch to SQLite if Supabase is not restored within 24h.
3. **UI Overlay**: Build the "Galaxy Stars" layout in `web/` using the verified components from the example repo.
