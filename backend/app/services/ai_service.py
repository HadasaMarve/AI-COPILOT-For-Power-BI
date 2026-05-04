"""
AI service — sends chart context + raw dataset to an LLM and returns insights.
"""

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Configuration (override via environment variables)
# ------------------------------------------------------------------ #
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "60"))

_SYSTEM_PROMPT: str = (
    "You are a senior business analyst with deep expertise in data analysis.\n"
    "You will receive a JSON dataset extracted from a business dashboard visualization.\n"
    "Analyze the raw data directly and provide:\n"
    "  1. Key Insights — the most important findings\n"
    "  2. Trends — patterns, growth or decline signals\n"
    "  3. Anomalies — anything unusual or unexpected in the data\n"
    "  4. Business Recommendations — actionable next steps\n\n"
    "Be concise, specific, and grounded in the numbers."
)


def _build_user_message(
    chart_id: str,
    filters: dict[str, Any],
    records: list[dict[str, Any]],
) -> str:
    context = {
        "chart_id": chart_id,
        "filters": filters,
        "dataset": records,
    }
    return (
        f"Please analyze the following business dataset.\n\n"
        f"```json\n{json.dumps(context, indent=2, default=str)}\n```"
    )


async def call_ai(
    chart_id: str,
    filters: dict[str, Any],
    records: list[dict[str, Any]],
) -> str:
    """
    Send dataset to OpenAI Chat Completions and return the AI response text.

    Args:
        chart_id: Visualization identifier (for prompt context).
        filters:  Active filters (for prompt context).
        records:  Serialised DataFrame rows.

    Returns:
        AI-generated insights as a plain string.

    Raises:
        RuntimeError: On HTTP error or timeout.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set."
        )

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(chart_id, filters, records)},
        ],
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("Calling AI — model=%s chart_id=%s rows=%d", OPENAI_MODEL, chart_id, len(records))

    try:
        async with httpx.AsyncClient(timeout=AI_TIMEOUT_SECONDS) as client:
            response = await client.post(OPENAI_API_URL, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError(f"AI service timed out after {AI_TIMEOUT_SECONDS}s") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"AI service HTTP error {exc.response.status_code}: {exc.response.text}"
        ) from exc

    data = response.json()
    insights: str = data["choices"][0]["message"]["content"]
    logger.info("AI call completed — chart_id=%s", chart_id)
    return insights
