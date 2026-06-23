"""
Core outreach generation logic.
LangChain + Groq integration.
"""

import logging
import time
import streamlit as st
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from utils.prompts import (
    SYSTEM_PROMPT, OUTREACH_PROMPT, VARIATION_PROMPT,
    TONE_INSTRUCTIONS, PLATFORM_INSTRUCTIONS
)

logger = logging.getLogger(__name__)


@st.cache_resource
def build_model(api_key: str) -> ChatGroq:
    """Initialise and cache Groq LLM."""
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=1500,
        api_key=api_key
    )


def generate_outreach(
    api_key: str,
    candidate_name: str,
    current_role: str,
    current_company: str,
    skills: str,
    target_job: str,
    tone: str,
    platform: str
) -> Optional[str]:
    """
    Generate complete outreach package for one candidate.
    Returns generated text or None on failure.
    """
    try:
        model = build_model(api_key)

        prompt = OUTREACH_PROMPT.format(
            candidate_name=candidate_name,
            current_role=current_role,
            current_company=current_company,
            skills=skills,
            target_job=target_job,
            tone=tone,
            tone_instruction=TONE_INSTRUCTIONS.get(tone, "professional"),
            platform=platform,
            platform_instruction=PLATFORM_INSTRUCTIONS.get(platform, "")
        )

        response = model.invoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])

        return response.content

    except Exception as e:
        logger.error(f"Outreach generation failed: {e}")
        return None


def generate_variations(
    api_key: str,
    candidate_name: str,
    current_role: str,
    current_company: str,
    skills: str,
    target_job: str,
    tone: str,
    platform: str
) -> dict:
    """Generate A/B variations of the outreach package."""
    model = build_model(api_key)
    variations = {}

    for label in ["Version A", "Version B"]:
        try:
            time.sleep(1.5)
            prompt = VARIATION_PROMPT.format(
                variation_label=label,
                candidate_name=candidate_name,
                current_role=current_role,
                current_company=current_company,
                skills=skills,
                target_job=target_job,
                tone=tone,
                platform=platform
            )

            response = model.invoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])

            variations[label] = response.content

        except Exception as e:
            logger.error(f"Variation {label} failed: {e}")
            variations[label] = f"Could not generate {label}."

    return variations