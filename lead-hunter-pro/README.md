# LeadOS — AI-Powered Lead Generation & Outreach Engine

LeadOS is a professional-grade, multi-channel lead discovery and engagement platform. It combines automated lead hunting, AI-driven scoring (Gemini/Groq), and integrated outreach via Email and WhatsApp.

## 🚀 Key Features

- **Multi-Source Discovery:** High-precision lead hunting via Google Maps, Foursquare, and HERE APIs.
- **AI Scoring Engine:** Real-time ICP (Ideal Customer Profile) matching using LLMs.
- **Rich Enrichment:** Automated extraction of emails, phone numbers, and business pain points.
- **Integrated Outreach:** Built-in support for Brevo (Email) and dedicated WhatsApp Automation.
- **BYOK Architecture:** Secure "Bring Your Own Key" model with client-side encryption.

## 📁 Repository Structure

- `server/`: FastAPI backend (Python). Handles discovery, enrichment, and AI scoring.
- `web/`: Next.js 14 frontend. A premium, reactive dashboard for lead management.
- `wa-server/`: Dedicated Node.js server for WhatsApp session management.
- `archives/`: Historical documentation, legacy tests, and project specifications.

## 🛠️ Quick Start

### 1. Requirements
- Python 3.10+
- Node.js 18+
- Docker (Optional, for easy deployment)

### 2. Backend Setup
```bash
cd server
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python main.py
```

### 3. Frontend Setup
```bash
cd web
npm install
npm run dev
```

### 4. WhatsApp Server Setup
```bash
cd wa-server
npm install
node index.js
```

## 🔒 Security
- All sensitive API keys are handled via environment variables.
- Client-side keys are stored using AES-encrypted `localStorage`.
- Production-ready `INTERNAL_API_KEY` authentication for all backend routes.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
