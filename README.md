<div align="center">

# ⚡ LeadOS

**AI-Powered Lead Generation & Outreach Intelligence Platform**

[![Next.js 15](https://img.shields.io/badge/Next.js-15.1-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=flat-square)](https://lead-os.vercel.app)

[Live Demo](https://lead-os.vercel.app) · [Report Bug](https://github.com/sp25126/leadOS/issues) · [Hire Me](mailto:saumyavishwam@gmail.com)

> ⚠️ **Demo Product** — Showcases architecture and pipeline design.
> For production-grade custom systems, contact me.

</div>

***

## 🌌 What Is LeadOS?

LeadOS is a **5-stage AI lead generation pipeline** that discovers local businesses in any city worldwide, enriches them with phones, emails, social profiles, and AI-generated outreach scores — then fires personalized email/WhatsApp campaigns automatically.

**OSM Discovery** → **Junk Filter** → **Google Maps Enrichment** → **OSINT Email Hunt** → **AI Scoring** → **Outreach**

***

## ✨ Features

| Feature | Description |
|---|---|
| 🌍 **Global Business Discovery** | OpenStreetMap Overpass API — any city, any business type |
| 🛡️ **Smart Junk Filter** | 50+ patterns to remove chains, canteens, duplicates |
| 📞 **Phone Enrichment** | Google Places BYOK — coverage jumps to ~65% |
| 📧 **OSINT Email Hunt** | DuckDuckGo scraper + website parser |
| 🧠 **AI Scoring** | Groq / Gemini BYOK — 1-10 score + personalized opening lines |
| 📬 **Outreach Automation** | SMTP email + WhatsApp gateway integration |
| 🎨 **Multi-Theme UI** | Cosmic Dark · Nord Ice · Cyber Terminal |
| 📱 **Mobile Responsive** | Bottom tab nav, safe-area aware, touch optimized |

***

## 🏗️ Architecture

```text
leadOS/
├── web/                   # Next.js 15 Frontend
│   ├── app/               # Main app routes (hunt, leads, outreach, etc.)
│   ├── components/        # Hero, Pipeline visuals, Design system
│   ├── lib/               # Theme engine & BYOK store
│   └── public/            # Assets & Videos
│
└── backend/               # Python FastAPI
    ├── api/               # Endpoint handlers
    ├── enrichment/        # The 5-stage pipeline logic
    ├── outreach/          # Email & WhatsApp senders
    └── requirements.txt
```

***

## 🎨 Theme System

LeadOS ships with **3 complete visual identities** — each changes colors, typography, 3D scene geometry, micro-interaction physics, nav position, border radii, and special effects:

| | Cosmic Dark | Nord Ice | Cyber Terminal |
|---|---|---|---|
| **Palette** | Violet + Cyan + Pink | Arctic Blue + Aurora | Phosphor Green |
| **Font** | Inter | DM Sans | JetBrains Mono |
| **Cards** | 16px rounded | 20px soft | **0px sharp** |
| **Nav** | Top center pill | Top left bar | Bottom center |
| **3D Scene** | Violet sphere cloud | DNA helix | Matrix rain |
| **Special FX** | Noise overlay | Dot grid | CRT scanlines |

***

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+
- (Optional) Google Maps API key
- (Optional) Groq or Gemini API key

### Frontend
```bash
cd web
pnpm install
cp .env.example .env.local
pnpm dev
# → http://localhost:3000/leados
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs
```

***

## ⚙️ Environment Variables

### Frontend (`web/.env.local`)
```text
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_EMAILJS_SERVICE_ID=your_service_id
NEXT_PUBLIC_EMAILJS_TEMPLATE_ID=your_template_id
NEXT_PUBLIC_EMAILJS_PUBLIC_KEY=your_public_key
```

### Backend (`backend/.env`)
```text
GOOGLE_MAPS_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
```

> **BYOK Philosophy**: LeadOS is built on Bring-Your-Own-Key. API keys are stored in the browser (localStorage) and sent per-request. The server never stores your keys.

***

## 📬 Contact
This is a demo product built to showcase AI automation architecture.

For custom-built, production-grade systems:

| Channel | Link |
|---|---|
| 📧 Email | saumyavishwam@gmail.com |
| 💬 WhatsApp | +91 88665 53976 |
| 🐙 GitHub | [@sp25126](https://github.com/sp25126) |

***

<div align="center"> Built with ⚡ by <a href="https://github.com/sp25126">sp25126</a> </div>
