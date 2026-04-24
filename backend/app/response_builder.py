from __future__ import annotations

from .classifier import Prediction
from .rag import RetrievedDocument
from .safety import DISCLAIMER_TEXT, SafetyResult


def build_assistant_response(
    message: str,
    predictions: list[Prediction],
    docs: list[RetrievedDocument],
    safety: SafetyResult,
) -> tuple[str, list[str], list[str]]:
    condition_names = ", ".join(item.condition for item in predictions[:3]) or "general viral illness"

    lines: list[str] = []
    next_steps: list[str] = [
        "Monitor symptom duration, severity, and any new changes.",
        "Arrange a medical review if symptoms persist, worsen, or you have underlying health conditions.",
        "Use this information as preparation for speaking with a doctor, not as a final diagnosis.",
    ]
    urgent_reasons = ["Seek urgent care for any severe, sudden, or worsening symptoms."]

    if safety.emergency and safety.warning_message:
        lines.append(safety.warning_message)
        urgent_reasons = [
            "You mentioned red-flag symptoms that may require emergency evaluation.",
            "Call local emergency services or go to the nearest emergency department now if symptoms are active.",
        ]
        next_steps = [
            "Do not rely on the chatbot alone when red-flag symptoms are present.",
            "Seek immediate in-person evaluation.",
            "Share the exact symptoms and timeline with a clinician or emergency responder.",
        ]
    else:
        lines.append(
            f"Based on the symptoms you shared, possible conditions may include {condition_names}. "
            "This is not a medical diagnosis, but it may help you discuss the situation with a clinician."
        )

    if predictions:
        top = predictions[0]
        lines.append(
            f"The strongest pattern match in the symptom classifier was {top.condition} at {top.confidence:.2f}% confidence, "
            "but confidence is only a ranking signal and not proof of disease."
        )

    if docs:
        top_doc = docs[0]
        lines.append(
            f"Helpful medical information from MedQuAD suggests reviewing '{top_doc.question}', "
            "which may provide context on symptoms, risk factors, or common care guidance."
        )

    lines.append(
        "Please consult a qualified healthcare professional for diagnosis, especially if symptoms are new, severe, or not improving."
    )

    return ("\n\n".join(lines), next_steps, urgent_reasons)


def build_disclaimer() -> str:
    return DISCLAIMER_TEXT
