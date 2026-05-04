"""
Builds the request payload sent to the FastAPI backend.
"""

from typing import Any


def build_payload(chart_id: str, filters: dict[str, str]) -> dict[str, Any]:
    """
    Convert chart_id and dynamic filters into the backend request format.

    Args:
        chart_id: Identifier of the selected Power BI visualization.
        filters:  Key-value pairs of active filters (e.g. region, year).

    Returns:
        Serialisable dict ready to POST as JSON.
    """
    return {
        "chartId": chart_id,
        "filters": filters,
    }
