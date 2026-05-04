"""
Global configuration for the AI Copilot for Power BI Streamlit app.
"""

# Backend FastAPI service URL
BACKEND_URL: str = "http://localhost:8000/api/v1/analyze-sales"

# Power BI embedded report URL — replace with your actual embed URL
POWERBI_EMBED_URL: str = (
    "https://app.powerbi.com/reportEmbed"
    "?reportId=YOUR_REPORT_ID"
    "&autoAuth=true"
    "&ctid=YOUR_TENANT_ID"
)

# Default iframe height in pixels
DEFAULT_HEIGHT: int = 700
