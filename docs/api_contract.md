# API Contract

## `GET /`

Returns backend status.

## `GET /health`

Returns:

```json
{
  "status": "healthy",
  "model_loaded": true,
  "rag_loaded": true
}
```

## `POST /api/chat`

Input:

```json
{
  "message": "I have fever, headache and body pain"
}
```

Returns a safety-first combined payload with classifier results, MedQuAD knowledge summaries, suggested next steps, urgent-care reasons, and a disclaimer.

## `POST /api/predict`

Returns the top ranked possible conditions from the classifier only.

## `POST /api/search-medquad`

Returns semantic retrieval results from the MedQuAD vector index only.
