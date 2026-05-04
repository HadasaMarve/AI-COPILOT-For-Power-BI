import streamlit as st
import json
from typing import Any

def render_ai_panel(
    ai_response: dict[str, Any] | None,
    is_loading: bool,
    error_message: str | None,
) -> None:
    st.markdown("---")
    st.subheader("🤖 AI Explanation")

    if is_loading:
        with st.spinner("Analysing data — please wait…"):
            st.empty()
        return

    if error_message:
        st.error(f"⚠️ Could not retrieve AI analysis: {error_message}")
        return

    if ai_response is None:
        st.info("No AI response available yet.")
        return

    insights_dict = json.loads(ai_response["insights"])

    # ------------------------------------------------------------------ #
    # Summary
    # ------------------------------------------------------------------ #
    with st.expander("💡 Summary", expanded=True):
        summary = insights_dict["summary"] 
        st.markdown(summary if summary else "_No summary returned._")

    # ------------------------------------------------------------------ #
    # Trends
    # ------------------------------------------------------------------ #
    with st.expander("📈 Trends", expanded=True):
        trends = insights_dict["key_trends"]
        if isinstance(trends, list):
            for item in trends:
                st.markdown(f"- {item}")
        else:
            st.markdown("_No trend data returned._")

    # ------------------------------------------------------------------ #
    # Anomalies
    # ------------------------------------------------------------------ #
    with st.expander("❎ Anomalies", expanded=True):
        anomalies = insights_dict["anomalies"]
        if isinstance(anomalies, list):
            for item in anomalies:
                st.markdown(f"- {item}")
        else:
            st.markdown("_No anomalies returned._")

    # ------------------------------------------------------------------ #
    # Recommendations
    # ------------------------------------------------------------------ #
    with st.expander("✅ Recommendations", expanded=True):
        recommendations = insights_dict["recommendations"]
        if isinstance(recommendations, list):
            for item in recommendations:
                st.markdown(f"- {item}")
        else:
            st.markdown("_No recommendations returned._")

    # ------------------------------------------------------------------ #
    # Raw response (collapsed, for debugging)
    # ------------------------------------------------------------------ #
    with st.expander("🔍 Full Response (debug)", expanded=False):
        st.json(ai_response)
