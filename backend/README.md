# LeadOS Backend

FastAPI backend powering the 5-stage lead generation pipeline.

## Start
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

## API Docs
[http://localhost:8000/docs](http://localhost:8000/docs)

## Pipeline Stages
| Stage | File | Description |
| :--- | :--- | :--- |
| 0 | `enrichment/osm_fetcher.py` | OpenStreetMap discovery |
| 1 | `enrichment/junk_filter.py` | 50+ pattern junk removal |
| 2 | `enrichment/gmaps_enricher.py` | Google Places phone/rating |
| 3 | `enrichment/osint_hunter.py` | DuckDuckGo email OSINT |
| 4 | `enrichment/ai_scorer.py` | AI 1-10 score + hooks |
| 5 | `outreach/email_sender.py` | SMTP outreach |
