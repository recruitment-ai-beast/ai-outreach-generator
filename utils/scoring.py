"""
Personalization scoring and spam risk detection.
Operates on generated message content.
"""

import re
from typing import Tuple


SPAM_PHRASES = [
    "exciting opportunity", "rockstar", "ninja", "superstar",
    "passionate", "game-changing", "i hope this finds you well",
    "amazing opportunity", "dream role", "perfect fit", "reach out",
    "touch base", "circle back", "synergy", "leverage"
]

SPAM_RISK_LEVELS = {
    (0, 1): ("Low Risk", "success"),
    (1, 3): ("Medium Risk", "warning"),
    (3, 100): ("High Risk", "error")
}


def calculate_personalization_score(
    content: str,
    candidate_name: str,
    current_company: str,
    skills: str
) -> Tuple[int, str]:
    """
    Score personalization quality of generated message.
    Returns (score, reasoning).
    """
    score = 0
    reasons = []

    if candidate_name.split()[0].lower() in content.lower():
        score += 25
        reasons.append("name referenced")

    if current_company.lower() in content.lower():
        score += 25
        reasons.append("company referenced")

    skill_list = [s.strip().lower() for s in skills.split(",")]
    matched_skills = [s for s in skill_list if s in content.lower()]
    if matched_skills:
        skill_score = min(30, len(matched_skills) * 10)
        score += skill_score
        reasons.append(f"{len(matched_skills)} skill(s) referenced")

    # Specificity — checks for non-generic language
    generic_count = sum(1 for phrase in SPAM_PHRASES if phrase in content.lower())
    specificity_score = max(0, 20 - (generic_count * 5))
    score += specificity_score
    if specificity_score == 20:
        reasons.append("no generic phrases detected")

    return min(score, 100), " · ".join(reasons) if reasons else "Low personalization"


def detect_spam_risk(content: str) -> Tuple[str, str, list]:
    """
    Detect spam/salesy language in generated content.
    Returns (risk_level, color, flagged_phrases).
    """
    found = [phrase for phrase in SPAM_PHRASES if phrase in content.lower()]

    for (low, high), (level, color) in SPAM_RISK_LEVELS.items():
        if low <= len(found) < high:
            return level, color, found

    return "High Risk", "error", found