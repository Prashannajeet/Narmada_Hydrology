from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from forecast_connectors import (
    geoglows_forecast,
    geoglows_get_river_id,
    glofas_placeholder,
    google_flood_placeholder,
)


APP_DIR = Path(__file__).resolve().parent
HTML_PATH = APP_DIR / "narmada-advanced-hydrology-analytics-webmap.html"
RESERVOIR_NODES = APP_DIR / "forecast_reservoir_nodes.csv"


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


def read_nodes() -> pd.DataFrame:
    return pd.read_csv(RESERVOIR_NODES)


dashboard_tab, forecast_tab = st.tabs(["Command webmap", "Reservoir inflow forecast"])

with dashboard_tab:
    if not HTML_PATH.exists():
        st.error(f"Dashboard HTML not found: {HTML_PATH.name}")
        st.stop()
    components.html(HTML_PATH.read_text(encoding="utf-8"), height=980, scrolling=False)

with forecast_tab:
    st.markdown("### Nita AI & Geoanalytics - Reservoir inflow forecast integration")
    st.caption("Server-side forecast connectors for GEOGLOWS now, with Google Flood and GloFAS credential slots ready.")

    nodes = read_nodes()
    priority_nodes = nodes.sort_values(["forecast_priority_rank", "reservoir"], na_position="last")
    selected = st.selectbox(
        "Reservoir / forecast node",
        priority_nodes["reservoir"].tolist(),
        index=0 if len(priority_nodes) else None,
    )
    node = priority_nodes.loc[priority_nodes["reservoir"] == selected].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("HMS element", str(node.get("hms_element", "NA")))
    c2.metric("Upstream area", f"{float(node.get('upstream_area_sqkm', 0)):,.0f} sq.km")
    c3.metric("Snap distance", f"{float(node.get('snap_distance_m', 0)):,.0f} m")
    c4.metric("Priority", str(node.get("forecast_priority_rank", "review")))

    provider = st.radio("Provider", ["GEOGLOWS", "Google Flood API", "GloFAS"], horizontal=True)

    if provider == "GEOGLOWS":
        st.info("Use the snapped dam/reach point for river ID lookup, then validate the returned river against HMS/QGIS.")
        default_id = str(node.get("geoglows_river_id", "") or "")
        river_id = st.text_input("GEOGLOWS river ID", value=default_id)
        if st.button("Find nearest GEOGLOWS river ID"):
            lat = float(node["snapped_latitude"] if pd.notna(node["snapped_latitude"]) else node["latitude"])
            lon = float(node["snapped_longitude"] if pd.notna(node["snapped_longitude"]) else node["longitude"])
            try:
                river_id = geoglows_get_river_id(lat, lon)
                st.success(f"Nearest GEOGLOWS river ID: {river_id}")
            except Exception as exc:
                st.error(str(exc))
        if river_id and st.button("Fetch GEOGLOWS forecast"):
            try:
                result = geoglows_forecast(river_id)
                st.success(result.note)
                st.dataframe(result.data.head(200), use_container_width=True)
                numeric_cols = result.data.select_dtypes(include="number").columns.tolist()
                if numeric_cols:
                    st.line_chart(result.data[numeric_cols[: min(3, len(numeric_cols))]])
            except Exception as exc:
                st.error(f"Forecast fetch failed: {exc}")

    elif provider == "Google Flood API":
        st.warning(google_flood_placeholder())
        st.code("Add GOOGLE_FLOOD_API_KEY in Streamlit secrets after pilot approval.", language="text")
    else:
        st.warning(glofas_placeholder())
        st.code("Add Copernicus EWDS/CDS credentials in Streamlit secrets before live retrieval.", language="text")

    with st.expander("Forecast node table", expanded=False):
        st.dataframe(nodes, use_container_width=True)
