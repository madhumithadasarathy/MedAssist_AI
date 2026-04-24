# Dataset Notes

## Symptom2Disease

- Expected file: `backend/data/Symptom2Disease.csv`
- Required columns:
  - `label`
  - `text`
- The repository currently includes a small starter CSV so the training script can run locally.
- Replace it with the full Symptom2Disease dataset for better performance.

## MedQuAD

- Source files should live in `backend/data/medquad/`.
- `parse_medquad.py` is written for XML MedQuAD files and also accepts CSV input for convenience.
- The current workspace already included a `medquad.csv`, which has been copied into the backend data folder as a starter source and processed CSV.

## Important Usage Rule

MedQuAD must not be used as the direct diagnosis classifier. It is only used for semantic retrieval of explanatory medical information.
