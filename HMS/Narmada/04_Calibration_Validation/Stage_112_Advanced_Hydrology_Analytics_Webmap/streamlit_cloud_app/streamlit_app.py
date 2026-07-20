from pathlib import Path
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from forecast_connectors import (
    geoglows_forecast,
    geoglows_get_river_id,
    glofas_placeholder,
    google_flood_placeholder,
    google_flood_query_forecasts,
    google_flood_query_latest_status_by_gauge_ids,
    google_flood_search_gauges_by_area,
    google_flood_search_latest_status_by_area,
    open_meteo_forecast,
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



def read_secret(section: str, key: str, env_name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(section, {}).get(key, "")
    except Exception:
        value = ""
    return str(value or os.getenv(env_name, default) or "").strip()


def masked_status(value: str) -> str:
    return "Configured" if value else "Missing"


def read_nodes() -> pd.DataFrame:
    return pd.read_csv(RESERVOIR_NODES)


def node_coordinates(node: pd.Series) -> tuple[float, float]:
    lat = node["snapped_latitude"] if pd.notna(node.get("snapped_latitude")) else node["latitude"]
    lon = node["snapped_longitude"] if pd.notna(node.get("snapped_longitude")) else node["longitude"]
    return float(lat), float(lon)


def sorted_forecast_nodes() -> pd.DataFrame:
    nodes = read_nodes()
    return nodes.sort_values(["forecast_priority_rank", "reservoir"], na_position="last")


def render_main_forecast_bridge() -> None:
    priority_nodes = sorted_forecast_nodes()
    if priority_nodes.empty:
        st.warning("Forecast node table is empty.")
        return

    with st.expander("Live forecast bridge: Google Flood API, GloFAS, GEOGLOWS and rainfall", expanded=True):
        st.caption("Main-page API bridge. Secrets are read server-side only and are never displayed.")
        selected_main = st.selectbox(
            "Forecast control node",
            priority_nodes["reservoir"].tolist(),
            index=0,
            key="main_forecast_control_node",
        )
        node = priority_nodes.loc[priority_nodes["reservoir"] == selected_main].iloc[0]
        lat_default, lon_default = node_coordinates(node)

        api_key = read_secret("google_flood", "api_key", "GOOGLE_FLOOD_API_KEY")
        cloud_project_id = read_secret("google_flood", "cloud_project_id", "GOOGLE_CLOUD_PROJECT_ID")
        google_base_url = read_secret(
            "google_flood",
            "base_url",
            "GOOGLE_FLOOD_BASE_URL",
            "https://floodforecasting.googleapis.com",
        )
        include_non_qv = read_secret(
            "google_flood",
            "include_non_quality_verified",
            "GOOGLE_FLOOD_INCLUDE_NON_QV",
            "true",
        )
        glofas_url = read_secret("copernicus", "url", "COPERNICUS_URL", "https://ewds.climate.copernicus.eu/api")
        glofas_key = read_secret("copernicus", "key", "COPERNICUS_API_TOKEN")

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Node", str(selected_main))
        k2.metric("Google Flood", "Ready" if api_key and cloud_project_id else "Needs setup")
        k3.metric("GloFAS", "Ready" if glofas_url and glofas_key else "Credential pending")
        k4.metric("GEOGLOWS", "Public")
        k5.metric("Open-Meteo", "Public")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latitude", f"{lat_default:.4f}")
        c2.metric("Longitude", f"{lon_default:.4f}")
        c3.metric("HMS element", str(node.get("hms_element", "NA")))
        c4.metric("Upstream area", f"{float(node.get('upstream_area_sqkm', 0)):,.0f} sq.km")

        source = st.radio(
            "Main-page live source",
            ["Google Flood API", "GloFAS", "GEOGLOWS", "Open-Meteo rainfall"],
            horizontal=True,
            key="main_live_source",
        )

        if source == "Google Flood API":
            st.caption("Search Google Flood gauges/status around the selected Narmada control node.")
            g1, g2, g3 = st.columns([1, 1, 1])
            gf_latitude = g1.number_input("Latitude", value=lat_default, format="%.6f", key="main_gf_latitude")
            gf_longitude = g2.number_input("Longitude", value=lon_default, format="%.6f", key="main_gf_longitude")
            radius_deg = g3.slider(
                "Search radius",
                min_value=0.05,
                max_value=1.00,
                value=0.35,
                step=0.05,
                key="main_gf_radius_deg",
            )
            include_non_qv_bool = str(include_non_qv).lower() in ("1", "true", "yes", "y")
            ga, gb = st.columns(2)
            if ga.button("Find Google Flood gauges", key="main_find_google_flood_gauges"):
                try:
                    result = google_flood_search_gauges_by_area(
                        api_key,
                        gf_latitude,
                        gf_longitude,
                        radius_deg=radius_deg,
                        include_non_quality_verified=include_non_qv_bool,
                        base_url=google_base_url,
                    )
                    st.success(result.note)
                    st.dataframe(result.data.head(200), use_container_width=True)
                except Exception as exc:
                    st.error(f"Google Flood gauge search failed: {exc}")
            if gb.button("Latest Google Flood status", key="main_google_flood_status"):
                try:
                    result = google_flood_search_latest_status_by_area(
                        api_key,
                        gf_latitude,
                        gf_longitude,
                        radius_deg=radius_deg,
                        include_non_quality_verified=include_non_qv_bool,
                        base_url=google_base_url,
                    )
                    st.success(result.note)
                    st.dataframe(result.data.head(200), use_container_width=True)
                except Exception as exc:
                    st.error(f"Google Flood status search failed: {exc}")
            gauge_ids_text = st.text_input(
                "Gauge IDs for forecast",
                value="",
                placeholder="paste comma-separated Google Flood gauge IDs",
                key="main_google_flood_gauge_ids",
            )
            gauge_ids = [part.strip() for part in gauge_ids_text.split(",") if part.strip()]
            if st.button("Get Google Flood forecast", key="main_google_flood_forecast"):
                try:
                    result = google_flood_query_forecasts(api_key, gauge_ids, base_url=google_base_url)
                    st.success(result.note)
                    st.dataframe(result.data.head(500), use_container_width=True)
                    numeric_cols = result.data.select_dtypes(include="number").columns.tolist()
                    if numeric_cols:
                        st.line_chart(result.data[numeric_cols[: min(3, len(numeric_cols))]])
                except Exception as exc:
                    st.error(f"Google Flood forecast query failed: {exc}")

        elif source == "GloFAS":
            if glofas_key:
                st.success("GloFAS/Copernicus credentials are configured. Production retrieval should run as a cached backend job because EWDS downloads can be asynchronous and heavy.")
            else:
                st.warning("GloFAS/Copernicus credentials are not configured yet. The main page will show readiness, but live GloFAS downloads need EWDS/CDS credentials and dataset licence acceptance.")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "source": "GloFAS / CEMS EWDS",
                            "node": selected_main,
                            "latitude": lat_default,
                            "longitude": lon_default,
                            "status": "credential-ready" if glofas_key else "credential-pending",
                            "recommended_use": "independent river forecast comparison and reservoir inflow context",
                        }
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )

        elif source == "GEOGLOWS":
            river_id = st.text_input(
                "GEOGLOWS river ID",
                value=str(node.get("geoglows_river_id", "") or ""),
                key="main_geoglows_river_id",
            )
            ga, gb = st.columns(2)
            if ga.button("Find GEOGLOWS river ID", key="main_find_geoglows"):
                try:
                    river_id = geoglows_get_river_id(lat_default, lon_default)
                    st.success(f"Nearest GEOGLOWS river ID: {river_id}")
                except Exception as exc:
                    st.error(str(exc))
            if river_id and gb.button("Fetch GEOGLOWS forecast", key="main_fetch_geoglows"):
                try:
                    result = geoglows_forecast(river_id)
                    st.success(result.note)
                    st.dataframe(result.data.head(200), use_container_width=True)
                    numeric_cols = result.data.select_dtypes(include="number").columns.tolist()
                    if numeric_cols:
                        st.line_chart(result.data[numeric_cols[: min(3, len(numeric_cols))]])
                except Exception as exc:
                    st.error(f"GEOGLOWS forecast failed: {exc}")

        else:
            forecast_days = st.slider("Forecast days", min_value=1, max_value=16, value=7, key="main_open_meteo_days")
            if st.button("Fetch Open-Meteo rainfall", key="main_fetch_open_meteo"):
                try:
                    result = open_meteo_forecast(lat_default, lon_default, forecast_days=forecast_days)
                    st.success(result.note)
                    if not result.daily.empty:
                        daily_plot = result.daily.set_index("time")
                        st.line_chart(daily_plot[[col for col in ["precipitation_sum", "precipitation_probability_max"] if col in daily_plot.columns]])
                        st.dataframe(result.daily, use_container_width=True)
                except Exception as exc:
                    st.error(f"Open-Meteo rainfall fetch failed: {exc}")


dashboard_tab, forecast_tab = st.tabs(["Command webmap", "Reservoir inflow forecast"])

with dashboard_tab:
    if not HTML_PATH.exists():
        st.error(f"Dashboard HTML not found: {HTML_PATH.name}")
        st.stop()
    render_main_forecast_bridge()
    components.html(HTML_PATH.read_text(encoding="utf-8"), height=860, scrolling=False)

with forecast_tab:
    st.markdown("### Nita AI & Geoanalytics - Reservoir inflow forecast integration")
    st.caption("Server-side forecast connectors for GEOGLOWS now, with Google Flood and GloFAS credential slots ready.")

    nodes = read_nodes()
    priority_nodes = sorted_forecast_nodes()
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

    provider = st.radio("Provider", ["GEOGLOWS", "Open-Meteo rainfall", "Google Flood API", "GloFAS"], horizontal=True)

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

    elif provider == "Open-Meteo rainfall":
        st.info("Open-Meteo provides point rainfall/weather forecasts without an API key. Use this as forecast guidance, then spatially weight or bias-correct before HMS forcing.")
        lat_default = float(node["snapped_latitude"] if pd.notna(node["snapped_latitude"]) else node["latitude"])
        lon_default = float(node["snapped_longitude"] if pd.notna(node["snapped_longitude"]) else node["longitude"])
        c_lat, c_lon, c_days = st.columns([1, 1, 1])
        latitude = c_lat.number_input("Forecast latitude", value=lat_default, format="%.6f")
        longitude = c_lon.number_input("Forecast longitude", value=lon_default, format="%.6f")
        forecast_days = c_days.slider("Forecast days", min_value=1, max_value=16, value=7)
        if st.button("Fetch Open-Meteo rainfall forecast"):
            try:
                result = open_meteo_forecast(latitude, longitude, forecast_days=forecast_days)
                st.success(result.note)
                st.caption(f"Matched grid/location: {result.location_id}")
                if not result.daily.empty:
                    st.markdown("#### Daily forecast rainfall")
                    daily_plot = result.daily.set_index("time")
                    chart_cols = [col for col in ["precipitation_sum", "precipitation_probability_max"] if col in daily_plot.columns]
                    st.dataframe(result.daily, use_container_width=True)
                    if chart_cols:
                        st.line_chart(daily_plot[chart_cols])
                if not result.hourly.empty:
                    st.markdown("#### Hourly forecast rainfall")
                    hourly_plot = result.hourly.set_index("time")
                    chart_cols = [col for col in ["precipitation", "precipitation_probability"] if col in hourly_plot.columns]
                    if chart_cols:
                        st.line_chart(hourly_plot[chart_cols])
                    st.dataframe(result.hourly.head(240), use_container_width=True)
                with st.expander("Open-Meteo request URL", expanded=False):
                    st.code(result.source_url, language="text")
            except Exception as exc:
                st.error(f"Open-Meteo forecast fetch failed: {exc}")

    elif provider == "Google Flood API":
        st.warning(google_flood_placeholder())
        api_key = read_secret("google_flood", "api_key", "GOOGLE_FLOOD_API_KEY")
        cloud_project_id = read_secret("google_flood", "cloud_project_id", "GOOGLE_CLOUD_PROJECT_ID")
        base_url = read_secret("google_flood", "base_url", "GOOGLE_FLOOD_BASE_URL", "https://floodforecasting.googleapis.com")
        include_non_qv = read_secret("google_flood", "include_non_quality_verified", "GOOGLE_FLOOD_INCLUDE_NON_QV", "true")

        s1, s2, s3 = st.columns(3)
        s1.metric("API key", masked_status(api_key))
        s2.metric("Cloud project", masked_status(cloud_project_id))
        s3.metric("Base URL", masked_status(base_url))

        if api_key and cloud_project_id:
            st.success("Google Flood API credentials are loaded from Streamlit secrets or environment variables. The key value is hidden.")
        else:
            st.error("Google Flood API secrets are not fully configured yet.")

        lat_default = float(node["snapped_latitude"] if pd.notna(node["snapped_latitude"]) else node["latitude"])
        lon_default = float(node["snapped_longitude"] if pd.notna(node["snapped_longitude"]) else node["longitude"])
        g_lat, g_lon, g_radius = st.columns([1, 1, 1])
        gf_latitude = g_lat.number_input("Google Flood search latitude", value=lat_default, format="%.6f")
        gf_longitude = g_lon.number_input("Google Flood search longitude", value=lon_default, format="%.6f")
        radius_deg = g_radius.slider("Search loop radius (degrees)", min_value=0.05, max_value=1.00, value=0.35, step=0.05)
        include_non_qv_bool = str(include_non_qv).lower() in ("1", "true", "yes", "y")

        col_a, col_b = st.columns(2)
        if col_a.button("Search nearby Google Flood gauges"):
            try:
                result = google_flood_search_gauges_by_area(
                    api_key,
                    gf_latitude,
                    gf_longitude,
                    radius_deg=radius_deg,
                    include_non_quality_verified=include_non_qv_bool,
                    base_url=base_url,
                )
                st.success(result.note)
                st.caption(f"{result.query_type} | rows: {len(result.data)}")
                st.dataframe(result.data.head(500), use_container_width=True)
                with st.expander("Redacted request URL", expanded=False):
                    st.code(result.source_url, language="text")
            except Exception as exc:
                st.error(f"Google Flood gauge search failed: {exc}")

        if col_b.button("Search latest flood status in area"):
            try:
                result = google_flood_search_latest_status_by_area(
                    api_key,
                    gf_latitude,
                    gf_longitude,
                    radius_deg=radius_deg,
                    include_non_quality_verified=include_non_qv_bool,
                    base_url=base_url,
                )
                st.success(result.note)
                st.caption(f"{result.query_type} | rows: {len(result.data)}")
                st.dataframe(result.data.head(500), use_container_width=True)
                with st.expander("Redacted request URL", expanded=False):
                    st.code(result.source_url, language="text")
            except Exception as exc:
                st.error(f"Google Flood status search failed: {exc}")

        gauge_ids_text = st.text_input("Google Flood gauge IDs for forecast/status", value="", placeholder="comma-separated gauge IDs from search result")
        gauge_ids = [part.strip() for part in gauge_ids_text.split(",") if part.strip()]
        col_c, col_d = st.columns(2)
        if col_c.button("Query gauge forecasts"):
            try:
                result = google_flood_query_forecasts(api_key, gauge_ids, base_url=base_url)
                st.success(result.note)
                st.caption(f"{result.query_type} | rows: {len(result.data)}")
                st.dataframe(result.data.head(1000), use_container_width=True)
                numeric_cols = result.data.select_dtypes(include="number").columns.tolist()
                if numeric_cols:
                    st.line_chart(result.data[numeric_cols[: min(3, len(numeric_cols))]])
            except Exception as exc:
                st.error(f"Google Flood forecast query failed: {exc}")

        if col_d.button("Query latest status by gauge IDs"):
            try:
                result = google_flood_query_latest_status_by_gauge_ids(api_key, gauge_ids, base_url=base_url)
                st.success(result.note)
                st.caption(f"{result.query_type} | rows: {len(result.data)}")
                st.dataframe(result.data.head(1000), use_container_width=True)
            except Exception as exc:
                st.error(f"Google Flood status query failed: {exc}")
    else:
        st.warning(glofas_placeholder())
        st.code("Add Copernicus EWDS/CDS credentials in Streamlit secrets before live retrieval.", language="text")

    with st.expander("Forecast node table", expanded=False):
        st.dataframe(nodes, use_container_width=True)
