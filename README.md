# MedAssist AI

MedAssist AI is a full-stack medical symptom-checking chatbot built with Next.js, FastAPI, scikit-learn, sentence-transformers, and FAISS. It is designed as an educational clinical decision-support assistant, not a diagnosis tool.

## Medical Safety Disclaimer

- MedAssist AI does not provide a final diagnosis.
- Results are educational and should be reviewed with a qualified healthcare professional.
- If a user reports chest pain, difficulty breathing, blue lips, severe bleeding, stroke symptoms, seizures, unconsciousness, or suicidal thoughts, they should seek immediate emergency care.

## Project Overview

- `frontend/`: Next.js App Router client with a responsive chatbot UI.
- `backend/`: FastAPI service with a safety layer, symptom classifier, and MedQuAD retrieval.
- `docs/`: Architecture, safety, dataset, and API documentation.
- `docker-compose.yml`: Local development orchestration.

## Dataset Usage

- `backend/data/Symptom2Disease.csv` is the classifier dataset. This repository includes a tiny starter dataset so the pipeline can run locally, but you should replace it with the full dataset for meaningful results.
- `backend/data/medquad/` stores raw MedQuAD source files.
- `backend/data/medquad_processed.csv` stores parsed and normalized Q&A records.

## Setup Instructions

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd medassist-ai
```

If you are using this exact workspace, the project root is already the current folder.

### 2. Backend setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
copy backend\.env.example backend\.env
```

### 3. Frontend setup

```bash
cd frontend
npm install
copy .env.example .env.local
cd ..
```

## Training the Classifier

```bash
python backend/scripts/train_classifier.py
python backend/scripts/evaluate_model.py
```

## Parsing MedQuAD

```bash
python backend/scripts/parse_medquad.py
```

## Building the Vector Index

```bash
python backend/scripts/build_vector_index.py
```

## Running the Backend

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## Running the Frontend

```bash
cd frontend
npm run dev
```

The app will be available at `http://localhost:3000` and the backend at `http://localhost:8000`.

## Docker

```bash
docker compose up --build
```

## Git Workflow

```bash
git init
git add .
git commit -m "Initial full-stack MedAssist AI setup"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

## Production Configuration (.env)

The backend uses `python-dotenv` for configuration. Create a `.env` file in the `backend/` directory:

```env
MODEL_PATH=./app/models/symptom_classifier.joblib
LABEL_ENCODER_PATH=./app/models/label_encoder.joblib
FAISS_PATH=./app/models/medquad_index
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
```

## Running with Docker (Recommended)

To launch the full production-ready stack (Frontend + Backend + Rate Limiting):

```bash
docker compose up --build
```

## Deployment Steps

### Backend (Render / Railway)
1. Set the **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
2. Add all environment variables from `backend/.env.example`.
3. Ensure `python 3.11+` is selected.

### Frontend (Vercel)
1. Import the `frontend` folder.
2. Set `NEXT_PUBLIC_API_URL` to your deployed backend URL.

## Technical Architecture & Stability
- **Calibrated SVC:** LinearSVC wrapped in `CalibratedClassifierCV` to provide reliable probability metrics.
- **Rate Limiting:** Built-in in-memory middleware restricts IPs to 30 requests per minute.
- **Explainability:** TF-IDF weight extraction highlights "Why" the model made a specific prediction.
- **RAG:** Context-aware medical knowledge retrieval via FAISS and sentence-transformers.

## Medical Disclaimer

**MedAssist AI is an educational clinical decision-support tool. It does NOT provide medical diagnoses.** 
Always verify findings with a licensed healthcare professional. In case of a medical emergency, contact local emergency services immediately.
