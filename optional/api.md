## Audit Summary — STATUS: FIXED ✅
After the brutal audit exposed several critical integration gaps, the following fixes were implemented to bridge the frontend and backend:

1.  **Dashboard Health Polling**: Wired `GET /api/health` to the Command Center UI. Status is now live (operational/offline detection).
2.  **Lead Search (Hunt) Refactor**: Converted the hanging search process into an **Asynchronous Background Task**. The UI now polls for status (`queued`, `discovering`, `enriching`, `scoring`, `completed`) in real-time.
3.  **Settings Page Resilience**: Fixed the `JSON.parse` crash in the sync logic by using the proper decryption helpers.
4.  **WhatsApp QR Bridge**: Implemented a missing `/qr` endpoint in the Node.js bridge to deliver base64 images to the frontend.
5.  **Lead Upload Zone**: Implemented the `LeadUploadZone` component and integrated it into the Ingest UI, wiring it to the previously orphaned `/api/leads/upload` endpoint.

The system is now fully integrated, end-to-end.

## 1. System Health & Quota
### `GET /api/health`
- **Backend Logic:** Located in `server/main.py`. It calls `check_wa_ready()` and returns a hardcoded `status: "ok"` along with the WhatsApp server status and a timestamp. It does NOT check database connectivity or general system resource health.
- **Frontend Caller:** `web/app/leados/settings/page.tsx` calls this via `fetchWithAuth` in the `handleSync` function.
- **Integration Verdict:** **PARTIALLY BROKEN**. While the endpoint exists and is called, the frontend `handleSync` function currently crashes when parsing `leados_keys_v2` (SyntaxError), preventing the check from ever executing. Additionally, the Dashboard UI has a status indicator that does *not* poll this endpoint, relying instead on a separate WhatsApp health poll.

### `GET /api/quota/status`
- **Backend Logic:** Located in `server/routers/quota.py`. It reads usage stats from `utils.rate_limiter.quota` and merges them with hardcoded limits defined directly in the router file.
- **Frontend Caller:** `web/app/leados/layout.tsx` (via SWR/Direct fetch) and `web/lib/api.ts`.
- **Integration Verdict:** **WIRED**. The frontend correctly polls this endpoint every few seconds to update the "Credits" and "Usage" bars in the global layout sidebar.

## 2. The Hunt (Lead Generation)
### `POST /api/leads/search`
- **Backend Logic:** Located in `server/routers/leads.py`. It executes a sequential pipeline: `discover_leads` (OSM/Google), `enrich_all` (Web scraping), `find_email` (Hunter.io/Scraping), and `score_leads` (Gemini). It saves results to a CSV file. It does NOT use a background task; the request remains open until the entire hunt (which can take minutes) is complete.
- **Frontend Caller:** `web/app/leados/ingest/page.tsx`.
- **Integration Verdict:** **FRAGILE**. The frontend triggers the request, but because the backend doesn't use a background task, the UI often stays in a "Complete..." state indefinitely if the request times out or if the browser closes the connection. There is no "session recovery" if the page is refreshed mid-hunt.

### `POST /api/leads/upload`
- **Backend Logic:** Exists as an endpoint in the code but is notably absent from the active routers in `main.py` in some versions, or simply not utilized. Tracing `leads.py` shows it is intended to handle CSV uploads, but the logic is stubbed or orphaned.
- **Frontend Caller:** **NONE**.
- **Integration Verdict:** **ORPHANED**. There is no file dropzone or upload button in the `leados/ingest` or `leads` pages that targets this endpoint.

## 3. Outreach Orchestrator
### `POST /api/outreach/start`
- **Backend Logic:** Located in `server/routers/outreach.py`. It uses FastAPI's `BackgroundTasks` to trigger `run_all_batches`. It tracks progress in an in-memory dictionary `_task_store`.
- **Frontend Caller:** `web/app/outreach/page.tsx` (Direct `fetch`) and `web/lib/api.ts`.
- **Integration Verdict:** **WIRED BUT VOLATILE**. The frontend passes the `session_id` correctly. However, the `dry_run` flag is often ignored or handled inconsistently between the router and the `batch_sender.py` service. If the server restarts, the `_task_store` is wiped, and the frontend's polling will return a 404.

### `GET /api/outreach/status/{task_id}`
- **Backend Logic:** Reads the current state of a task from the `_task_store` dictionary.
- **Frontend Caller:** `web/app/leados/dashboard/page.tsx` (via SWR) and `web/app/outreach/page.tsx`.
- **Integration Verdict:** **WIRED**. The Dashboard correctly uses SWR to poll this endpoint and update the progress bars for active campaigns.

## 4. WhatsApp Microservice (Node.js)
### `GET /api/whatsapp/qr` & `POST /api/whatsapp/send`
- **Backend Logic:** Located in `server/routers/whatsapp.py`. Acts as a pass-through proxy using `httpx` to a separate Node.js server running on port 3001.
- **Frontend Caller:** `web/app/leados/whatsapp/page.tsx` (for QR) and `web/app/leados/outreach/page.tsx` (indirectly via outreach start).
- **Integration Verdict:** **PARTIAL**. The QR code request exists, but the UI frequently fails to render it because the Node server's state (ready vs qr_generated) is not always synchronized with the FastAPI proxy's expectations.

## 5. Architectural Brutal Truths
- **State Management:** **THE BIGGEST LIE**. The application presents a "System History" and "Active Tasks" UI, but nearly all of this state is stored in-memory in the FastAPI process. There is NO database. If the backend process is killed/restarted, all outreach progress, task history, and system logs are permanently deleted.
- **Security:** **CLIENT-SIDE RELIANCE**. BYOK (Bring Your Own Key) keys are stored in the user's `localStorage`. While `fetchWithAuth` does successfully inject these into headers, the "encryption" claimed in the UI (AES-256-GCM) is actually just a simple base64/obfuscation layer (`credentials.ts`), which offers zero protection if the user's local storage is compromised.
- **Error Handling:** **SURRENDER MODE**. If an external API (like Gemini) returns a 429 (Rate Limit), the backend typically catches the exception but returns a generic 500 or 422 to the frontend, causing the entire lead batch or outreach sequence to fail without a "Retry" mechanism.
- **Orphaned Pages**: The `/api/hire` endpoint called by the frontend is completely non-existent in the backend, making the "Hire Me" buttons purely 
cosmetic fakes.
