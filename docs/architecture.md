# Architecture

MedAssist AI uses a two-stage backend pipeline and a lightweight chat frontend.

## Request Flow

1. The Next.js frontend sends a symptom message to FastAPI.
2. The safety layer scans for emergency red-flag symptoms.
3. The symptom classifier ranks likely conditions with TF-IDF plus Logistic Regression.
4. The retrieval layer searches MedQuAD passages using sentence-transformer embeddings and FAISS similarity search.
5. The response builder merges safety guidance, predictions, and retrieved medical explanations into a clinician-safe answer.

## Components

- `frontend/`: Next.js App Router, Tailwind CSS, TypeScript UI.
- `backend/app/main.py`: FastAPI app and route definitions.
- `backend/app/classifier.py`: Model loading and top-k prediction logic.
- `backend/app/rag.py`: Embedding index loading and semantic retrieval.
- `backend/app/safety.py`: Red-flag symptom detection and disclaimer text.
- `backend/app/response_builder.py`: Human-readable response assembly.
- `backend/scripts/`: Training, parsing, indexing, and evaluation helpers.

## Safety Constraints

- The classifier ranks possibilities instead of confirming diagnoses.
- MedQuAD is used only for educational retrieval, not direct diagnosis classification.
- Red-flag symptoms override the normal conversational tone and elevate urgent-care messaging.
