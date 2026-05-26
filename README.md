# Audit Evidence Analyser API

A FastAPI application that accepts CSV audit evidence, runs statistical exception analysis using Pandas, and returns risk-flagged rows as JSON — with an auto-generated Swagger UI.

Built as a portfolio project to demonstrate Python/AI/ML skills aligned with the PwC Technology Consulting role.

---

## What it does

Upload any CSV of audit evidence (journal entries, access logs, transaction data).  
The engine runs three checks on every numeric column:

| Check | Description | Risk Score |
|---|---|---|
| **Null / Missing** | Any blank or null cell | +20 pts per missing field |
| **Z-score outlier** | Value > 3 std deviations from mean | +up to 30 pts |
| **IQR range** | Value outside Q1−1.5×IQR … Q3+1.5×IQR | +15 pts |

**Risk bands:** 70–100 = High · 40–69 = Medium · 1–39 = Low

---

## Project structure

```
audit-analyser-api/
├── main.py              # FastAPI app — endpoints, request/response models
├── analyser.py          # Exception analysis engine (Pandas + NumPy)
├── requirements.txt     # Python dependencies
├── sample_evidence.csv  # Test data with intentional anomalies
└── README.md
```

---

## Run locally

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/audit-analyser-api
cd audit-analyser-api
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open Swagger UI
# http://127.0.0.1:8000/docs
```

---

## Test with sample data

```bash
curl -X POST "http://127.0.0.1:8000/analyse" \
     -F "file=@sample_evidence.csv"
```

Expected output (abridged):
```json
{
  "filename": "sample_evidence.csv",
  "total_rows": 15,
  "flagged_rows": 3,
  "high_risk_rows": 0,
  "results": [
    {
      "row_index": 8,
      "risk_score": 60,
      "flags": ["Missing values in: amount, gl_code, description"],
      "row_data": { ... }
    }
  ]
}
```

---

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy — your public API URL appears in the dashboard

Add the live URL to your resume and LinkedIn.

---

## Resume bullet point

> Built and deployed an Audit Evidence Analyser REST API using FastAPI and Pandas; implements statistical exception detection (z-score, IQR analysis) on uploaded CSV evidence files, returning risk-scored anomalies as JSON — auto-documented via Swagger UI and deployed on Render.

---

## Tech stack

- **FastAPI** — modern Python web framework with automatic OpenAPI/Swagger docs
- **Pandas + NumPy** — statistical exception analysis
- **Pydantic** — request/response validation and schema generation
- **Uvicorn** — ASGI server
- **Render** — free cloud deployment

---

*Built by Om Dhede · KPMG IT Audit Analyst × B.Tech AI & Data Science*
