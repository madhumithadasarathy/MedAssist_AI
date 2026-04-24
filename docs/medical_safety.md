# Medical Safety

## Product Positioning

MedAssist AI is an educational clinical decision-support assistant. It does not provide a final diagnosis, treatment plan, or emergency triage clearance.

## Required Safety Behaviors

- Never say the user definitely has a condition.
- Always present outputs as possible conditions or informational context.
- Always include a disclaimer encouraging professional medical evaluation.
- Immediately escalate red-flag symptoms such as chest pain, shortness of breath, severe bleeding, seizure, stroke symptoms, unconsciousness, or self-harm risk.

## Frontend Safety UX

- Landing page contains a prominent medical disclaimer.
- Chat page includes emergency-use warnings near the composer.
- Assistant cards show an emergency warning banner whenever red flags are detected.

## Known Gaps

- The baseline classifier is only a starting point and depends heavily on the dataset quality.
- Model probabilities are ranking aids, not calibrated clinical risk estimates.
- The symptom dataset included in this repository is a small starter sample for local setup and should be replaced with a full curated dataset for serious experimentation.
