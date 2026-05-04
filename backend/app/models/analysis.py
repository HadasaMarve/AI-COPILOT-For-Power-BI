"""
Pydantic request and response models for the analysis endpoint.
"""

from typing import Any
from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Payload sent by the Streamlit frontend."""

    chartId: str = Field(..., description="Identifier of the Power BI visualization.")
    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic key-value filters selected in Power BI.",
    )


class AnalysisResponse(BaseModel):
    """Response returned to the frontend after AI analysis."""

    chartId: str
    filters: dict[str, Any]
    insights: str
    rows_analyzed: int
