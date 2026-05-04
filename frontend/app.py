"""
AI Copilot for Power BI — main Streamlit entry point.

Flow
----
1. Parse URL query parameters.
2. Render Power BI dashboard iframe.
3. Automatically call backend AI service (once per unique chartId).
4. Display AI explanation panel.
"""

from typing import Any
import streamlit as st

from config import POWERBI_EMBED_URL, DEFAULT_HEIGHT
from services.query_parser import parse_query_params
from utils.payload_builder import build_payload
from api.backend_client import request_ai_analysis
#from components.dashboard_iframe import render_dashboard
from components.ai_panel import render_ai_panel

# ------------------------------------------------------------------ #
# Page configuration
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="AI Copilot for Power BI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------------ #
# Session-state defaults (run once per browser session)
# ------------------------------------------------------------------ #
if "last_chart_id" not in st.session_state:
    st.session_state.last_chart_id: str | None = None

if "ai_response" not in st.session_state:
    st.session_state.ai_response: dict[str, Any] | None = None

if "ai_error" not in st.session_state:
    st.session_state.ai_error: str | None = None

if "ai_loading" not in st.session_state:
    st.session_state.ai_loading: bool = False

# ------------------------------------------------------------------ #
# Title
# ------------------------------------------------------------------ #
st.title("🤖 AI Copilot for Power BI")

# ------------------------------------------------------------------ #
# Parse URL query parameters
# ------------------------------------------------------------------ #
context: dict[str, Any] = parse_query_params()
chart_id: str | None = context["chart_id"]
filters: dict[str, str] = context["filters"]

# ------------------------------------------------------------------ #
# Guard: no chartId present
# ------------------------------------------------------------------ #
if not chart_id:
    st.info(
        "📊 **Open this page from Power BI to view AI insights.**\n\n"
        "No chart context was detected in the URL.  "
        "Use the *Explain with AI* button inside your Power BI report to launch this page."
    )
    #st.stop()

# ------------------------------------------------------------------ #
# Show active context (collapsible)
# ------------------------------------------------------------------ #
with st.expander("🔗 Active context from Power BI", expanded=False):
    st.markdown(f"**Chart ID:** `{chart_id}`")
    if filters:
        st.markdown("**Filters:**")
        for k, v in filters.items():
            st.markdown(f"- `{k}` = `{v}`")
    else:
        st.markdown("_No additional filters._")

# ------------------------------------------------------------------ #
# Render Power BI dashboard
# ------------------------------------------------------------------ #
#render_dashboard(embed_url=POWERBI_EMBED_URL, height=DEFAULT_HEIGHT)

# ------------------------------------------------------------------ #
# Automatic AI analysis — only when chartId changes
# ------------------------------------------------------------------ #
chart_changed: bool = chart_id != st.session_state.last_chart_id

if chart_changed:
    # Reset previous results
    st.session_state.ai_response = None
    st.session_state.ai_error = None
    st.session_state.ai_loading = True
    st.session_state.last_chart_id = chart_id

    # Build and send payload
    payload: dict[str, Any] = build_payload(chart_id=chart_id, filters=filters)
    try:
        result: dict[str, Any] = request_ai_analysis(payload)
        st.session_state.ai_response = result
    except Exception as exc:
        st.session_state.ai_error = str(exc)
    finally:
        st.session_state.ai_loading = False

# ------------------------------------------------------------------ #
# Render AI explanation panel
# ------------------------------------------------------------------ #
render_ai_panel(
    ai_response=st.session_state.ai_response,
    is_loading=st.session_state.ai_loading,
    error_message=st.session_state.ai_error,
)
