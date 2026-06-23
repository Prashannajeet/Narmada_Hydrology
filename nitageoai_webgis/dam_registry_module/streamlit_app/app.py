import json
import os
from datetime import date, timedelta
from html import escape
from typing import Any

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:18080").rstrip("/")
DEFAULT_EMAIL = os.getenv("DEMO_EMAIL", "admin@nita.ai")
DEFAULT_PASSWORD = os.getenv("DEMO_PASSWORD", "nita-admin")
MODULE_OPERATOR_NAME = os.getenv("MODULE_OPERATOR_NAME", "Risk Register Administrator")
MODULE_NAME = "Risk Register Module"
API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "120"))
ARCGIS_TOKEN = os.getenv("ARCGIS_TOKEN", "").strip()
ARCGIS_SECURED_FEATURE_URL = os.getenv("ARCGIS_SECURED_FEATURE_URL", "").strip()
ARCGIS_SECURED_FEATURE_NAME = os.getenv("ARCGIS_SECURED_FEATURE_NAME", "Secured ArcGIS Layer").strip()

LEVEL_ORDER = ["critical", "high", "moderate", "low"]
LEVEL_COLORS = {
    "critical": "#fb7185",
    "high": "#f97316",
    "moderate": "#facc15",
    "low": "#22c55e",
}


st.set_page_config(
    page_title="NITA AI Risk Register",
    page_icon="!",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_state() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("user", {})
    st.session_state.setdefault("selected_risk_id", None)


def api_request(method: str, path: str, token: str | None = None, **kwargs: Any) -> Any:
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.request(method, f"{API_BASE_URL}{path}", headers=headers, timeout=API_TIMEOUT_SECONDS, **kwargs)
    if response.status_code >= 400:
        raise requests.HTTPError(response.text, response=response)
    if response.status_code == 204 or not response.content:
        return None
    return response.json()


def login(email: str, password: str) -> None:
    api_request("GET", "/health")
    data = api_request("POST", "/api/auth/login", json={"email": email, "password": password})
    st.session_state.token = data["access_token"]
    st.session_state.user = data["user"]


def risk_params(query: str, level: str, status: str, limit: int = 100) -> dict[str, str | int]:
    params: dict[str, str | int] = {"limit": limit}
    if query.strip():
        params["q"] = query.strip()
    if level != "All":
        params["level"] = level
    if status != "All":
        params["status"] = status
    return params


def load_risks(query: str, level: str, status: str) -> dict[str, Any]:
    return api_request("GET", "/api/risk-register", st.session_state.token, params=risk_params(query, level, status))


def load_dams(query: str = "", state: str = "", limit: int = 500) -> list[dict[str, Any]]:
    dams: list[dict[str, Any]] = []
    offset = 0
    page_size = 100
    while len(dams) < limit:
        params: dict[str, str | int] = {"limit": page_size, "offset": offset}
        if query.strip():
            params["q"] = query.strip()
        if state and state != "All":
            params["state"] = state
        data = api_request("GET", "/api/dams", st.session_state.token, params=params)
        items = data.get("items", [])
        dams.extend(items)
        if len(items) < page_size or len(dams) >= data.get("total", 0):
            break
        offset += page_size
    return dams[:limit]


def sync_risks() -> dict[str, Any]:
    return api_request("POST", "/api/risk-register/sync", st.session_state.token, json={})


def update_risk(risk_id: str, status: str, mitigation_plan: str) -> dict[str, Any]:
    return api_request(
        "PATCH",
        f"/api/risk-register/{risk_id}",
        st.session_state.token,
        json={
            "status": status,
            "mitigation_plan": mitigation_plan,
            "review_date": (date.today() + timedelta(days=30)).isoformat(),
        },
    )


def risks_frame(items: list[dict[str, Any]]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame()
    frame = pd.DataFrame(items)
    visible_columns = [
        "risk_code",
        "risk_title",
        "dam_name",
        "state",
        "risk_level",
        "risk_score",
        "status",
        "priority",
        "due_date",
        "risk_source",
        "ai_flag",
        "maintenance_required",
        "compliance_flag",
    ]
    existing = [column for column in visible_columns if column in frame.columns]
    return frame[existing].rename(
        columns={
            "risk_code": "Risk Code",
            "risk_title": "Risk",
            "dam_name": "Dam",
            "risk_level": "Level",
            "risk_score": "Score",
            "risk_source": "Source",
            "ai_flag": "AI",
            "maintenance_required": "Maintenance",
            "compliance_flag": "Compliance",
            "due_date": "Due Date",
            "state": "State",
            "status": "Status",
            "priority": "Priority",
        }
    )


def render_metric_cards(summary: dict[str, Any]) -> None:
    cols = st.columns(5)
    metrics = [
        ("Active risks", summary.get("total", 0), "Portfolio register"),
        ("Critical / high", summary.get("critical", 0) + summary.get("high", 0), "Escalation queue"),
        ("Overdue", summary.get("overdue", 0), "Past due date"),
        ("AI flagged", summary.get("ai_flags", 0), "From defect intelligence"),
        ("Maintenance", summary.get("maintenance_required", 0), "Action required"),
    ]
    for col, (label, value, help_text) in zip(cols, metrics):
        col.metric(label, f"{value:,}", help=help_text)


def render_charts(summary: dict[str, Any]) -> None:
    left, middle, right = st.columns([1, 1, 1])
    by_level = pd.DataFrame(summary.get("by_level", []))
    by_category = pd.DataFrame(summary.get("by_category", []))
    by_state = pd.DataFrame(summary.get("by_state", []))

    with left:
        st.subheader("Risk Levels")
        if not by_level.empty:
            by_level["sort"] = by_level["key"].apply(lambda value: LEVEL_ORDER.index(value) if value in LEVEL_ORDER else 99)
            by_level = by_level.sort_values("sort").drop(columns=["sort"])
            st.bar_chart(by_level.set_index("key")["count"], color="#fb7185")
        else:
            st.info("No risk level data.")

    with middle:
        st.subheader("Categories")
        if not by_category.empty:
            st.bar_chart(by_category.set_index("key")["count"], color="#14b8a6")
        else:
            st.info("No category data.")

    with right:
        st.subheader("States")
        if not by_state.empty:
            st.bar_chart(by_state.set_index("key")["count"], color="#38bdf8")
        else:
            st.info("No state data.")


def render_leaflet_map(dams: list[dict[str, Any]], secured_layer_enabled: bool) -> None:
    mapped_dams = [
        dam
        for dam in dams
        if isinstance(dam.get("latitude"), (int, float)) and isinstance(dam.get("longitude"), (int, float))
    ]
    dam_payload = [
        {
            "dam_id": dam.get("dam_id"),
            "dam_name": dam.get("dam_name"),
            "state": dam.get("state"),
            "district": dam.get("district"),
            "risk_class": dam.get("risk_class") or "not assessed",
            "status": dam.get("status"),
            "safety_score": dam.get("safety_score"),
            "latitude": dam.get("latitude"),
            "longitude": dam.get("longitude"),
            "river_basin": dam.get("river_basin"),
            "dam_type": dam.get("dam_type"),
        }
        for dam in mapped_dams
    ]
    secured_layer = {
        "enabled": secured_layer_enabled and bool(ARCGIS_SECURED_FEATURE_URL),
        "name": ARCGIS_SECURED_FEATURE_NAME,
        "url": ARCGIS_SECURED_FEATURE_URL,
        "token": ARCGIS_TOKEN,
    }
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
          html, body, #map {{ height: 100%; margin: 0; }}
          #map {{ border-radius: 10px; background: #e5edf3; }}
          .legend {{
            background: rgba(255,255,255,.94);
            padding: 10px 12px;
            border-radius: 8px;
            box-shadow: 0 8px 22px rgba(15,23,42,.14);
            font: 12px/1.35 system-ui, -apple-system, Segoe UI, sans-serif;
            color: #172033;
          }}
          .legend strong {{ display: block; margin-bottom: 6px; }}
          .legend span {{ display: flex; align-items: center; gap: 7px; margin: 4px 0; }}
          .legend i {{ width: 10px; height: 10px; border-radius: 999px; display: inline-block; }}
          .leaflet-popup-content {{ font: 13px/1.35 system-ui, -apple-system, Segoe UI, sans-serif; }}
          .leaflet-popup-content strong {{ display: block; margin-bottom: 4px; color: #0f172a; }}
          .popup-grid {{ display: grid; grid-template-columns: auto 1fr; gap: 3px 10px; min-width: 190px; }}
          .popup-grid b {{ color: #526171; }}
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script>
          const dams = {json.dumps(dam_payload)};
          const securedLayer = {json.dumps(secured_layer)};
          const tokenSuffix = securedLayer.token ? "?token=" + encodeURIComponent(securedLayer.token) : "";
          const map = L.map("map", {{ zoomControl: true }}).setView([22.8, 78.8], 5);
          const basemaps = {{
            "ArcGIS Topographic": L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{{z}}/{{y}}/{{x}}", {{
              maxZoom: 18,
              attribution: "Tiles &copy; Esri, USGS, NOAA"
            }}),
            "ArcGIS Imagery": L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}", {{
              maxZoom: 18,
              attribution: "Tiles &copy; Esri, Maxar, Earthstar Geographics"
            }}),
            "ArcGIS Streets": L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{{z}}/{{y}}/{{x}}", {{
              maxZoom: 18,
              attribution: "Tiles &copy; Esri"
            }}),
            "ArcGIS Light Gray": L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}", {{
              maxZoom: 16,
              attribution: "Tiles &copy; Esri"
            }}),
            "OpenStreetMap": L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
              maxZoom: 19,
              attribution: "&copy; OpenStreetMap contributors"
            }})
          }};
          basemaps["ArcGIS Topographic"].addTo(map);

          const colors = {{
            critical: "#dc2626",
            high: "#f97316",
            moderate: "#facc15",
            low: "#22c55e",
            "not assessed": "#94a3b8"
          }};
          const damLayer = L.layerGroup();
          const bounds = [];
          const safe = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({{
            "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\"": "&quot;", "'": "&#039;"
          }}[char]));

          dams.forEach((dam) => {{
            const color = colors[dam.risk_class] || colors["not assessed"];
            const marker = L.circleMarker([dam.latitude, dam.longitude], {{
              radius: 7,
              color: "#0f172a",
              weight: 1.2,
              fillColor: color,
              fillOpacity: 0.88
            }});
            marker.bindPopup(`
              <strong>${{safe(dam.dam_name || "Dam")}}</strong>
              <div class="popup-grid">
                <b>ID</b><span>${{safe(dam.dam_id)}}</span>
                <b>State</b><span>${{safe(dam.state)}}</span>
                <b>District</b><span>${{safe(dam.district)}}</span>
                <b>Risk</b><span>${{safe(dam.risk_class)}}</span>
                <b>Status</b><span>${{safe(dam.status)}}</span>
                <b>Score</b><span>${{safe(dam.safety_score)}}</span>
                <b>Basin</b><span>${{safe(dam.river_basin)}}</span>
                <b>Type</b><span>${{safe(dam.dam_type)}}</span>
              </div>
            `);
            marker.addTo(damLayer);
            bounds.push([dam.latitude, dam.longitude]);
          }});
          damLayer.addTo(map);

          const overlays = {{ "Dam Registry Points": damLayer }};
          if (securedLayer.enabled) {{
            const separator = securedLayer.url.includes("?") ? "&" : "?";
            const securedUrl = securedLayer.url + (securedLayer.token ? separator + "token=" + encodeURIComponent(securedLayer.token) : "");
            overlays[securedLayer.name] = L.tileLayer(securedUrl, {{
              maxZoom: 19,
              opacity: 0.72,
              attribution: "Secured ArcGIS"
            }});
          }}
          L.control.layers(basemaps, overlays, {{ collapsed: false }}).addTo(map);

          if (bounds.length) {{
            map.fitBounds(bounds, {{ padding: [24, 24], maxZoom: 8 }});
          }}

          const legend = L.control({{ position: "bottomright" }});
          legend.onAdd = function() {{
            const div = L.DomUtil.create("div", "legend");
            div.innerHTML = "<strong>Dam Risk Class</strong>" +
              Object.entries(colors).map(([label, color]) => `<span><i style="background:${{color}}"></i>${{label}}</span>`).join("");
            return div;
          }};
          legend.addTo(map);
        </script>
      </body>
    </html>
    """
    components.html(html, height=620)


def render_map_tab(query: str) -> None:
    st.subheader("Dam Safety Map")
    controls = st.columns([1.2, 1.2, 1.2, 2])
    with controls[0]:
      state = st.text_input("State filter", value="", placeholder="Example: Maharashtra")
    with controls[1]:
      max_records = st.slider("Max dams", min_value=50, max_value=500, value=300, step=50)
    with controls[2]:
      secured_layer_enabled = st.checkbox("Secured ArcGIS layer", value=False, disabled=not bool(ARCGIS_SECURED_FEATURE_URL))
    with controls[3]:
      if ARCGIS_SECURED_FEATURE_URL:
          st.caption(f"ArcGIS secured layer configured: {escape(ARCGIS_SECURED_FEATURE_NAME)}")
      else:
          st.caption("Optional secured ArcGIS layer: set ARCGIS_SECURED_FEATURE_URL and ARCGIS_TOKEN.")

    try:
        dams = load_dams(query=query, state=state.strip() or "All", limit=max_records)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load dam locations: {exc}")
        return

    mapped_count = sum(1 for dam in dams if isinstance(dam.get("latitude"), (int, float)) and isinstance(dam.get("longitude"), (int, float)))
    st.caption(f"{mapped_count:,} mapped dams from {len(dams):,} registry records.")
    render_leaflet_map(dams, secured_layer_enabled)


def render_detail(items: list[dict[str, Any]]) -> None:
    st.subheader("Workflow")
    if not items:
        st.info("No risk selected.")
        return

    options = {f"{item.get('risk_code') or item['risk_id']} - {item.get('dam_name', 'Dam')}": item for item in items}
    labels = list(options.keys())
    current_index = 0
    if st.session_state.selected_risk_id:
        for index, item in enumerate(options.values()):
            if item["risk_id"] == st.session_state.selected_risk_id:
                current_index = index
                break

    selected_label = st.selectbox("Select risk", labels, index=current_index)
    selected = options[selected_label]
    st.session_state.selected_risk_id = selected["risk_id"]

    st.markdown(f"**{selected.get('risk_title', 'Risk')}**")
    st.caption(f"{selected.get('dam_name', '')} | {selected.get('state', '')} | Score {selected.get('risk_score', 0)}")
    st.write(selected.get("trigger_event") or "No trigger narrative recorded.")

    status = st.selectbox(
        "Workflow status",
        ["open", "monitoring", "mitigating", "accepted", "closed"],
        index=["open", "monitoring", "mitigating", "accepted", "closed"].index(selected.get("status", "open")),
    )
    plan = st.text_area("Mitigation plan", value=selected.get("mitigation_plan") or "", height=120)

    if st.button("Update Risk Workflow", type="primary"):
        updated = update_risk(selected["risk_id"], status, plan)
        st.session_state.selected_risk_id = updated["risk_id"]
        st.success(f"Risk updated to {updated['status']}.")
        st.rerun()


def render_badge_legend() -> None:
    st.markdown(
        """
        <style>
          .nita-header {
            padding: 1.15rem 1.25rem;
            border-radius: 0.5rem;
            background: linear-gradient(135deg, rgba(190,18,60,.12), rgba(15,118,110,.14));
            border: 1px solid rgba(15,118,110,.18);
            margin-bottom: 1rem;
          }
          .nita-header h1 { margin: 0 0 .35rem 0; }
          .nita-header p { margin: 0; color: #526171; }
          .risk-pill {
            display: inline-flex;
            padding: .25rem .5rem;
            margin-right: .35rem;
            border-radius: .45rem;
            font-weight: 700;
            font-size: .8rem;
          }
        </style>
        <div class="nita-header">
          <h1>NITA AI Risk Register</h1>
          <p>Streamlit operational view for the Risk Register Module, connected to the live Dam Safety Intelligence backend.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    legend_html = " ".join(
        f"<span class='risk-pill' style='background:{color}22;color:{color}'>{level.title()}</span>"
        for level, color in LEVEL_COLORS.items()
    )
    st.markdown(legend_html, unsafe_allow_html=True)


def main() -> None:
    init_state()
    render_badge_legend()

    with st.sidebar:
        st.header(MODULE_NAME)
        st.caption(API_BASE_URL)
        email = st.text_input("Email", value=DEFAULT_EMAIL)
        password = st.text_input("Password", value=DEFAULT_PASSWORD, type="password")
        if st.button("Login", use_container_width=True):
            try:
                login(email, password)
                st.success(f"Signed in as {MODULE_OPERATOR_NAME}")
            except requests.Timeout:
                st.error("Backend is still waking up on Render. Wait one minute, then click Login again.")
            except Exception as exc:  # noqa: BLE001 - show API text in admin tool
                st.error(f"Login failed: {exc}")

        if st.session_state.token:
            st.success(f"Module role: {st.session_state.user.get('role', 'viewer')}")
        else:
            st.warning("Login to load the Risk Register.")

        st.divider()
        query = st.text_input("Search", placeholder="Dam, risk code, trigger...")
        level = st.selectbox("Risk level", ["All", "critical", "high", "moderate", "low"], index=0)
        status = st.selectbox("Status", ["All", "open", "monitoring", "mitigating", "accepted", "closed"], index=0)

    if not st.session_state.token:
        st.info("Use the demo credentials in the sidebar to connect to the live backend.")
        return

    top_actions = st.columns([1, 1, 4])
    with top_actions[0]:
        if st.button("Refresh", use_container_width=True):
            st.rerun()
    with top_actions[1]:
        if st.button("Sync Risk Engine", type="primary", use_container_width=True):
            try:
                sync_risks()
                st.success("Risk engine sync complete.")
            except Exception as exc:  # noqa: BLE001
                st.error(f"Sync failed: {exc}")

    try:
        data = load_risks(query, level, status)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Unable to load Risk Register: {exc}")
        return

    summary = data.get("summary", {})
    items = data.get("items", [])

    render_metric_cards(summary)
    st.divider()
    render_charts(summary)
    st.divider()

    table_col, detail_col = st.columns([1.8, 1])
    with table_col:
        st.subheader("Register")
        frame = risks_frame(items)
        if frame.empty:
            st.info("No risks match the current filters.")
        else:
            st.dataframe(frame, use_container_width=True, hide_index=True)

    with detail_col:
        render_detail(items)

    st.divider()
    render_map_tab(query)


if __name__ == "__main__":
    main()
