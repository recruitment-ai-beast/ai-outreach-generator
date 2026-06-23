"""
Bulk CSV processing for outreach generation.
"""

import logging
import time
import pandas as pd
from typing import Tuple, List
from io import BytesIO

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {
    "candidate_name", "current_role",
    "current_company", "skills", "target_job"
}


def validate_csv(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate uploaded CSV has required columns."""
    missing = REQUIRED_COLUMNS - set(df.columns.str.lower())
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"
    return True, ""


def process_bulk(
    df: pd.DataFrame,
    api_key: str,
    tone: str,
    platform: str,
    generate_fn
) -> Tuple[List[dict], int, int]:
    """
    Process each CSV row and generate outreach.
    Returns (results, success_count, failure_count).
    """
    results = []
    success = 0
    failure = 0

    for _, row in df.iterrows():
        try:
            time.sleep(1.0)  # rate limit protection

            content = generate_fn(
                api_key=api_key,
                candidate_name=str(row.get("candidate_name", "")),
                current_role=str(row.get("current_role", "")),
                current_company=str(row.get("current_company", "")),
                skills=str(row.get("skills", "")),
                target_job=str(row.get("target_job", "")),
                tone=tone,
                platform=platform
            )

            if content:
                results.append({
                    "candidate_name": row.get("candidate_name"),
                    "current_role": row.get("current_role"),
                    "target_job": row.get("target_job"),
                    "content": content,
                    "status": "Success"
                })
                success += 1
            else:
                raise ValueError("Empty response")

        except Exception as e:
            logger.error(f"Bulk row failed: {e}")
            results.append({
                "candidate_name": row.get("candidate_name", "Unknown"),
                "current_role": row.get("current_role", ""),
                "target_job": row.get("target_job", ""),
                "content": "",
                "status": "Failed"
            })
            failure += 1

    return results, success, failure