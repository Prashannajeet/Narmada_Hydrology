from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


APP_DIR = Path(__file__).resolve().parent
HTML_PATH = APP_DIR / "narmada-advanced-hydrology-analytics-webmap.html"


st.set_page_config(
    page_title="Nita AI & Geoanalytics - Narmada Hydrology",
    page_icon=":droplet:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }
    iframe { display: block; border: 0; }
    [data-testid="stAppViewContainer"] { overflow: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


if not HTML_PATH.exists():
    st.error(f"Dashboard HTML not found: {HTML_PATH.name}")
    st.stop()

components.html(HTML_PATH.read_text(encoding="utf-8"), height=980, scrolling=False)
