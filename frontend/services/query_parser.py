"""
Parses Streamlit URL query parameters into a structured context object.
"""

from typing import Any
import streamlit as st


def parse_query_params() -> dict[str, Any]:
    """
    Read all URL query parameters from Streamlit and return a structured dict.

    Returns:
        {
            "chart_id": str | None,
            "filters": dict[str, str]   # all remaining params
        }
    """
    try:
        params: dict[str, Any] = dict(st.query_params)
    except Exception:
        params = {}

    chart_id: str | None = params.pop("chartId", None)

    # Normalise list values (Streamlit may wrap single values in a list)
    filters: dict[str, str] = {}
    for key, value in params.items():
        if isinstance(value, list):
            filters[key] = value[0] if value else ""
        else:
            filters[key] = str(value)

    if isinstance(chart_id, list):
        chart_id = chart_id[0] if chart_id else None

    return {
        "chart_id": chart_id,
        "filters": filters,
    }
