"""
FastAPI application factory.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analysis import router as analysis_router

# ------------------------------------------------------------------ #
# Logging
# ------------------------------------------------------------------ #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# ------------------------------------------------------------------ #
# Application
# ------------------------------------------------------------------ #
app = FastAPI(
    title="AI Copilot for Power BI — Backend",
    description="Receives chart context, loads data, and returns AI insights.",
    version="1.0.0",
)

# Allow the Streamlit frontend to call the backend from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(analysis_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
