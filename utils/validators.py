"""
Input validation layer.
All validation logic isolated here.
"""

from typing import Tuple


def validate_inputs(
    candidate_name: str,
    current_role: str,
    current_company: str,
    skills: str,
    target_job: str,
    tone: str,
    platform: str
) -> Tuple[bool, str]:
    """Validate all required form inputs."""

    if not candidate_name.strip():
        return False, "Please enter the candidate's name."
    if not current_role.strip():
        return False, "Please enter the candidate's current role."
    if not current_company.strip():
        return False, "Please enter the candidate's current company."
    if not skills.strip():
        return False, "Please provide at least one skill."
    if len(skills.strip()) < 3:
        return False, "Please provide more specific skills."
    if not target_job.strip():
        return False, "Tell us what role you're recruiting for."
    if not tone:
        return False, "Please select a tone."
    if not platform:
        return False, "Please select a platform."

    return True, ""


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """Validate Groq API key."""
    if not api_key:
        return False, "GROQ_API_KEY not found. Check your environment variables."
    if not api_key.startswith("gsk_"):
        return False, "Invalid API key format."
    return True, ""