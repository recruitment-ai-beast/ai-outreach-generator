"""
Export utilities — TXT and CSV.
"""

import logging
from io import StringIO
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)


def export_as_txt(content: str, candidate_name: str) -> bytes:
    """Export outreach package as plain text."""
    header = f"Outreach Package — {candidate_name}\n{'=' * 50}\n\n"
    return (header + content).encode("utf-8")


def export_bulk_csv(results: list) -> Optional[bytes]:
    """
    Export bulk generation results as CSV.
    results: list of dicts with candidate info + generated content
    """
    try:
        df = pd.DataFrame(results)
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue().encode("utf-8")
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        return None


def export_bulk_txt(results: list) -> bytes:
    """Export bulk results as single TXT file."""
    output = []
    for r in results:
        output.append(f"Candidate: {r.get('candidate_name', 'Unknown')}")
        output.append("=" * 50)
        output.append(r.get("content", "Generation failed."))
        output.append("\n\n")
    return "\n".join(output).encode("utf-8")