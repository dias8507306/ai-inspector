# AI Inspector: multi-modal "is it AI-generated?" checker

A FastAPI backend and React frontend that estimate whether a **text, image or video** was AI-generated. It uses explainable heuristics (stylistic markers, sentence length, resolution, colour variance, file format and size), and includes an optional TF-IDF + logistic-regression text model.

## Features

- **Text**: counts typical "AI-style" phrases (Russian), measures average sentence length and returns AI / human probability with a confidence score
- **Image**: Pillow + NumPy analysis of resolution, format and colour standard deviation, with human-readable indicators
- **Video**: format and size heuristics (a placeholder for a future OpenCV analysis)
- `app/simple_model.py`: a small scikit-learn model (TF-IDF + LogisticRegression) trained on start-up and cached to `ai_model.pkl`, plus a heuristic fallback
- React UI with Text / Image / Video tabs, file preview, a probability bar and analysis details
- Docker Compose setup for both services; Swagger docs at `/docs`

## Tech stack

Python 3.11+ · FastAPI · Uvicorn · Pillow · NumPy · scikit-learn (optional) · React 18 (Create React App) · Axios · Docker Compose

## Project structure

```
backend/
  app/api.py            FastAPI app: /api/analyze/{text,image,video}, /health
  app/simple_model.py   optional ML text detector
  requirements.txt
  Dockerfile
frontend/
  src/App.js            UI (tabs, upload, result card)
  src/App.css
  public/index.html
  package.json
  Dockerfile
docker-compose.yml
```

## How to run

**Docker:**

```bash
docker compose up --build
# frontend: http://localhost:3000   backend: http://localhost:8000/docs
```

**Locally:**

```bash
# backend
cd backend
python -m venv .venv && .venv/Scripts/activate      # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.api:app --reload --port 8000

# frontend (second terminal)
cd frontend
npm install
npm start          # uses REACT_APP_API_URL or http://localhost:8000
```

No API keys or external services are needed; everything runs offline.

> All data in this repository is randomly generated; brand names are anonymized. The detector is heuristic and meant as a demo, not a reliable classifier.

Author: Dias Ayazbay.

## Қысқаша (KZ)

AI Inspector: мәтіннің, суреттің немесе видеоның жасанды интеллектпен жасалғанын бағалайтын қызмет.
Backend FastAPI-да жазылған, эвристикалар мен шағын scikit-learn моделін қолданады. Frontend React-та жазылған.
Docker Compose арқылы бір командамен іске қосылады, ешқандай API кілті қажет емес.
