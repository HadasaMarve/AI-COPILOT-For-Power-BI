"""
FastAPI route — POST /api/v1/analyze-sales
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.services.data_service import fetch_dataframe
from app.services.ai_service import call_ai
from app.utils.dataframe_serializer import dataframe_to_records

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post(
    "/analyze-sales",
    response_model=AnalysisResponse,
    summary="Analyse a Power BI visualisation using AI",
)
async def analyze_sales(request: AnalysisRequest) -> AnalysisResponse:
    """
    Receive chart context → load data → send to AI → return insights.
    """
    chart_id: str = request.chartId
    filters: dict[str, Any] = request.filters

    logger.info("Received analysis request — chartId=%s filters=%s", chart_id, filters)

    # ------------------------------------------------------------------ #
    # 1. Fetch data via script.get_data()
    # ------------------------------------------------------------------ #
    try:
        df = await fetch_dataframe(chart_id=chart_id, filters=filters)
    except RuntimeError as exc:
        logger.error("Data fetch failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Data retrieval error: {exc}",
        )

    if df.empty:
        logger.warning("Empty DataFrame returned for chartId=%s", chart_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No data found for the given chartId and filters.",
        )

    logger.info("DataFrame rows=%d for chartId=%s", len(df), chart_id)

    # ------------------------------------------------------------------ #
    # 2. Serialise DataFrame
    # ------------------------------------------------------------------ #
    try:
        records = dataframe_to_records(df)
    except Exception as exc:
        logger.error("Serialisation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data serialisation error: {exc}",
        )

    # ------------------------------------------------------------------ #
    # 3. Call AI service
    # ------------------------------------------------------------------ #
    logger.info("AI call started — chartId=%s rows=%d", chart_id, len(records))
    try:
        insights = await call_ai(chart_id=chart_id, filters=filters, records=records)
    except RuntimeError as exc:
        logger.error("AI call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service error: {exc}",
        )
    logger.info("AI call completed — chartId=%s", chart_id)

    return AnalysisResponse(
        chartId=chart_id,
        filters=filters,
        insights=insights,
        rows_analyzed=len(records),
    )
