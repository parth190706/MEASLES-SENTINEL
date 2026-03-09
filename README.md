# 🦠 Measles AI Sentinel
### AI-Powered Measles Outbreak Intelligence & Detection System
> Powered by **Google Gemini AI** + **FastAPI** + **Leaflet.js**

---

## 🚀 Quick Setup (3 Steps)

### Step 1 — Add Your Gemini API Key

1. Copy the env file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and replace the placeholder:
   ```
   GEMINI_API_KEY=AIzaSy...your_actual_key_here
   ```
   
   Get your free API key at: https://aistudio.google.com/app/apikey

---

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 3 — Run the Server

```bash
uvicorn backend.main:app --reload --port 8000
```

Then open your browser at: **http://localhost:8000**

---

## 🧠 AI Features (All Powered by Gemini)

| Feature | Gemini Model | What It Does |
|--------|-------------|--------------|
| **Risk Prediction** | gemini-1.5-flash | Analyzes vaccination/demographic data to predict outbreak probability |
| **Symptom Checker** | gemini-1.5-flash | Clinical assessment of symptoms with differential diagnosis |
| **Rash Image Scanner** | gemini-1.5-flash (Vision) | Visual classification of rash images into diagnostic categories |
| **Medical Guidance** | gemini-1.5-flash | Treatment protocols, isolation guidance, medication advice |
| **Outbreak Alerts** | gemini-1.5-flash | Dynamic AI-generated public health alert messages |

---

## 📁 Project Structure

```
measles-sentinel/
├── backend/
│   ├── __init__.py
│   ├── main.py          ← FastAPI app entry point
│   ├── routes.py        ← All API endpoint definitions
│   └── gemini_service.py ← All Gemini AI calls
├── frontend/
│   └── index.html       ← Complete single-file frontend
├── .env.example         ← Environment template
├── requirements.txt     ← Python dependencies
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ping` | Health check |
| POST | `/api/predict-risk` | Outbreak risk prediction |
| POST | `/api/analyze-symptoms` | Symptom probability analysis |
| POST | `/api/scan-rash` | Rash image classification (multipart) |
| POST | `/api/medical-guidance` | Treatment & isolation guidance |
| POST | `/api/generate-alert` | Dynamic alert generation |
| GET | `/api/regional-data` | Map & chart data |

---

## 🧪 Sample API Test

```bash
curl -X POST http://localhost:8000/api/predict-risk \
  -H "Content-Type: application/json" \
  -d '{
    "vaccination_rate": 65,
    "population_density": 1200,
    "recent_cases": 20,
    "season": "Winter (High Risk)",
    "region_type": "Urban Metro",
    "travel_activity": "High (International)"
  }'
```

---

## ⚙️ Replit Deployment

1. Create a new Replit with Python template
2. Upload all files
3. Add `GEMINI_API_KEY` in Replit **Secrets** tab
4. Set run command: `uvicorn backend.main:app --host 0.0.0.0 --port 8080`
5. In `frontend/index.html`, change `API_BASE` to your Replit URL:
   ```js
   const API_BASE = "https://your-repl-name.replit.app/api";
   ```

---

## ⚠️ Medical Disclaimer

This system provides **informational guidance only** and does not replace professional medical diagnosis. Always consult a licensed healthcare provider for medical decisions.
