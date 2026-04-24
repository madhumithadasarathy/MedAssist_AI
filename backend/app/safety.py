from __future__ import annotations

from dataclasses import dataclass
import re


DISCLAIMER_TEXT = (
    "MedAssist AI is an educational symptom guidance tool and not a medical diagnosis service. "
    "Possible conditions shown here are informational only. Please consult a qualified healthcare "
    "professional for evaluation, diagnosis, and treatment."
)


@dataclass(slots=True)
class SafetyResult:
    emergency: bool
    matched_red_flags: list[str]
    warning_message: str | None


RED_FLAG_PATTERNS: dict[str, tuple[str, ...]] = {
    "chest pain": ("chest pain", "crushing chest pain", "tightness in chest"),
    "difficulty breathing": ("difficulty breathing", "cant breathe", "cannot breathe"),
    "shortness of breath": ("shortness of breath", "breathless", "trouble breathing"),
    "severe bleeding": ("severe bleeding", "bleeding heavily", "won't stop bleeding"),
    "unconscious": ("unconscious", "passed out", "not waking up"),
    "seizure": ("seizure", "convulsion", "fits"),
    "stroke symptoms": ("stroke symptoms", "face drooping", "slurred speech"),
    "sudden weakness": ("sudden weakness", "one-sided weakness", "sudden numbness"),
    "suicidal thoughts": ("suicidal thoughts", "want to kill myself", "self harm"),
    "severe allergic reaction": ("severe allergic reaction", "anaphylaxis", "swollen tongue"),
    "blue lips": ("blue lips", "bluish lips", "turning blue"),
    "severe abdominal pain": ("severe abdominal pain", "worst stomach pain", "rigid abdomen"),
    "pregnancy emergency symptoms": (
        "pregnancy emergency",
        "pregnant and bleeding",
        "severe pain while pregnant",
    ),
    "high fever in infant": ("high fever in infant", "baby has high fever", "newborn fever"),
}


def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def detect_red_flags(message: str) -> SafetyResult:
    normalized = normalize_text(message)
    matches: list[str] = []

    for label, phrases in RED_FLAG_PATTERNS.items():
        for phrase in phrases:
            if phrase in normalized:
                matches.append(label)
                break

    emergency = len(matches) > 0
    warning = None

    if emergency:
        warning = (
            "Some symptoms you mentioned can be medical red flags. Please seek immediate in-person "
            "medical care or contact local emergency services right away, especially if symptoms are "
            "severe, worsening, or sudden."
        )

    return SafetyResult(emergency=emergency, matched_red_flags=matches, warning_message=warning)
