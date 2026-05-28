# Audit Evidence Analyser

A full-stack audit analytics tool that accepts CSV evidence files, runs statistical exception analysis, and returns risk-flagged rows — complete with a browser-based frontend and a self-documenting REST API.

Built to demonstrate Python · FastAPI · Pandas · statistical analysis skills, in the context of SOX ITGC and IT audit workflows.

---

## What it does

Upload any CSV of audit evidence (journal entries, access logs, transaction data). The analysis engine runs three checks on every numeric column:

| Check | Logic | Risk Points |
|---|---|---|
| **Null / Missing** | Any blank or null cell | +20 pts per missing field |
| **Z-score outlier** | `\|z\| > 3` — more than 3 std deviations from column mean | +up to 30 pts |
| **IQR range check** | Below Q1−1.5×IQR or above Q3+1.5×IQR | +15 pts |

**Risk bands**

| Score | Level | Meaning |
|---|---|---|
| 70 – 100 | 🔴 High | Likely exception — review immediately |
| 40 – 69  | 🟡 Medium | Anomaly present — review recommended |
| 1 – 39   | 🟢 Low | Minor deviation — log and monitor |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                     │
│  frontend/index.html  (vanilla HTML + CSS + JS SPA)      │
│  · Drag-and-drop CSV upload                              │
│  · Live API health indicator                             │
│  · Animated summary stats                               │
│  · Risk-level filter tabs                               │
│  · Expandable row details                               │
│  · Export results as JSON                               │
└────────────────────────┬────────────────────────────────┘
                         │  HTTP (multipart/form-data)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI  (main.py)                    │
│  GET  /        → health check                           │
│  POST /analyse → upload CSV, get flagged rows           │
│  GET  /ui      → serve frontend SPA                     │
│  GET  /docs    → Swagger UI                             │
│  GET  /redoc   → ReDoc                                  │
└────────────────────────┬────────────────────────────────┘
                         │  DataFrame
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Analysis Engine  (analyser.py)              │
│  · Null detection                                       │
│  · Z-score computation  (NumPy)                         │
│  · IQR fence calculation  (Pandas quantile)             │
│  · Risk scoring + sorting                               │
└─────────────────────────────────────────────────────────┘
```

---

## Project structure

```
P1/
├── main.py              # FastAPI app — endpoints, Pydantic models, frontend route
├── analyser.py          # Exception analysis engine (Pandas + NumPy)
├── requirements.txt     # Python dependencies
├── sample_evidence.csv  # Test data with intentional anomalies
├── frontend/
│   └── index.html       # Single-page frontend (no build step, no framework)
└── README.md
```

---

## Frontend features

| Feature | Detail |
|---|---|
| **Drag-and-drop upload** | Drop a CSV onto the zone or click to browse |
| **Live API status** | Polls `GET /` on load; green/red indicator in navbar |
| **Sample CSV download** | One-click download of `sample_evidence.csv` to test immediately |
| **Animated summary cards** | Total rows · Flagged rows · High risk · Clean rows |
| **Risk-level filter tabs** | All · High · Medium · Low — filter without re-uploading |
| **Score bar** | Visual progress bar for each row's risk score |
| **Expandable row details** | Click "View Row" to see every field value (nulls highlighted in red) |
| **JSON export** | Download the full analysis result as a `.json` file |
| **Toast notifications** | Success / error feedback for every user action |
| **Responsive layout** | Works on desktop and mobile |
| **API Docs links** | Direct links to Swagger UI (`/docs`) and ReDoc (`/redoc`) |

---

## Run locally

```bash
# 1. Clone and set up
git clone https://github.com/YOUR_USERNAME/audit-analyser-api
cd audit-analyser-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Start the API server
uvicorn main:app --reload

# 3. Open the frontend
open http://127.0.0.1:8000/ui

# Or use the auto-generated API docs
open http://127.0.0.1:8000/docs
```

---

## API endpoints

### `GET /`
Health check. Returns `{ "status": "ok", "message": "..." }`.

### `POST /analyse`
Upload a CSV file and receive exception-flagged rows.

**Request:** `multipart/form-data` with field `file` (`.csv` only)

**Response:**
```json
{
  "filename":       "sample_evidence.csv",
  "total_rows":     15,
  "flagged_rows":   5,
  "high_risk_rows": 2,
  "results": [
    {
      "row_index":  4,
      "risk_score": 85,
      "flags": [
        "Missing values in: approver",
        "'amount' = 150000.00 is a statistical outlier (|z| = 4.3)"
      ],
      "row_data": {
        "entry_id": "JE004",
        "date":     "2024-01-08",
        "amount":   150000.0,
        "approver": null,
        "gl_code":  "GL-4205",
        "department": "Finance",
        "description": "Manual journal - end of quarter"
      }
    }
  ]
}
```

**Error responses:**

| Status | Cause |
|---|---|
| 400 | File is not a `.csv` |
| 422 | CSV cannot be parsed, or is empty |

### `GET /ui`
Serves the frontend SPA (`frontend/index.html`).

### `GET /docs`
Auto-generated Swagger UI (FastAPI built-in).

### `GET /redoc`
Auto-generated ReDoc documentation.

---

## Test with curl

```bash
# Health check
curl http://127.0.0.1:8000/

# Upload sample CSV
curl -X POST "http://127.0.0.1:8000/analyse" \
     -F "file=@sample_evidence.csv"
```

---

## Sample data walkthrough

`sample_evidence.csv` contains 15 journal entries with three intentional anomalies:

| Row | Issue | Expected flag |
|---|---|---|
| JE004 | Amount = 150,000 (far above normal ~1,800) · Approver missing | Z-score outlier + null → High risk |
| JE007 | Amount missing · GL code missing · Description missing | 3 × null → High risk |
| JE011 | Amount missing | 1 × null → Medium risk |
| JE012 | Amount = −45,000 (large negative, unusual GL-9999) | IQR + Z-score → High risk |

---

## Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your repo and set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy — your public URL appears in the dashboard

Access the frontend at `https://your-app.onrender.com/ui`  
Access Swagger at `https://your-app.onrender.com/docs`

---

## Tech stack

| Layer | Technology |
|---|---|
| **API framework** | FastAPI — async, OpenAPI/Swagger auto-docs |
| **Statistical analysis** | Pandas + NumPy — z-score, IQR, null detection |
| **Data validation** | Pydantic v2 — typed request/response models |
| **Server** | Uvicorn (ASGI) |
| **Frontend** | Vanilla HTML5 + CSS3 + JavaScript (no build step) |
| **Deployment** | Render (free tier) |

---

## Workflow

```
User opens /ui
    │
    ├─ Drag & drop CSV  ─────────────────────────────────┐
    │                                                     │
    ▼                                                     ▼
POST /analyse                                   Download sample CSV
    │                                           (built-in test data)
    ▼
FastAPI validates file type + parses CSV
    │
    ▼
analyser.analyse(df)
    ├─ scan all columns for nulls        → +20 pts/field
    ├─ compute z-scores for numeric cols → +up to 30 pts
    └─ compute IQR fences               → +15 pts/violation
    │
    ▼
Sort flagged rows by risk_score descending
Return AnalysisResponse JSON
    │
    ▼
Frontend renders:
    ├─ Summary stat cards (animated)
    ├─ Filter tabs (All / High / Medium / Low)
    ├─ Results table with score bars + risk badges
    └─ Expandable row detail view
```

---

*Built by Om Dhede · KPMG IT Audit Analyst × B.Tech AI & Data Science*
