"""
Renders the Power BI dashboard inside an HTML iframe component.
"""

import streamlit as st
import streamlit.components.v1 as components

from config import POWERBI_EMBED_URL, DEFAULT_HEIGHT


def render_dashboard(embed_url: str = POWERBI_EMBED_URL, height: int = DEFAULT_HEIGHT) -> None:
    """
    Embed a Power BI report in a responsive iframe.

    Uses st.components.v1.html so the iframe is rendered once without
    causing unnecessary Streamlit reruns.

    Args:
        embed_url: The Power BI embed URL.
        height:    Iframe height in pixels (default from config).
    """
    iframe_html: str = f"""
    <style>
        .pbi-wrapper {{
            width: 100%;
            border: none;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        iframe.pbi-frame {{
            width: 100%;
            height: {height}px;
            border: none;
            display: block;
        }}
    </style>
    <div class="pbi-wrapper">
        <iframe
            class="pbi-frame"
            src="{embed_url}"
            allowfullscreen="true"
            loading="lazy"
        ></iframe>
    </div>
    """

    components.html(iframe_html, height=height + 20, scrolling=False)
