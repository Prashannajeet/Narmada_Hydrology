from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests


GEOGLOWS_BASE = "https://geoglows.ecmwf.int/api"
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"
GOOGLE_FLOOD_BASE = "https://floodforecasting.googleapis.com"


@dataclass
class ForecastResult:
    provider: str
    river_id: str
    data: pd.DataFrame
    note: str


@dataclass
class WeatherForecastResult:
    provider: str
    location_id: str
    hourly: pd.DataFrame
    daily: pd.DataFrame
    source_url: str
    note: str


@dataclass
class GoogleFloodResult:
    provider: str
    query_type: str
    data: pd.DataFrame
    raw: dict[str, Any]
    source_url: str
    note: str


def _as_dataframe(payload: Any) -> pd.DataFrame:
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        for key in ("data", "forecast", "values", "results"):
            if isinstance(payload.get(key), list):
                return pd.DataFrame(payload[key])
        return pd.json_normalize(payload)
    return pd.DataFrame()


def geoglows_get_river_id(lat: float, lon: float, timeout: int = 20) -> str:
    """Return nearest GEOGLOWS river ID for a latitude/longitude point.

    The public service has used both lat/lon and latitude/longitude parameter
    names across examples, so the function tries both safely.
    """
    attempts = (
        {"lat": lat, "lon": lon},
        {"latitude": lat, "longitude": lon},
    )
    last_error = None
    for params in attempts:
        try:
            response = requests.get(f"{GEOGLOWS_BASE}/v2/getriverid", params=params, timeout=timeout)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                for key in ("river_id", "riverId", "reach_id", "LINKNO", "linkno", "id"):
                    if key in payload:
                        return str(payload[key])
            if isinstance(payload, (str, int)):
                return str(payload)
        except Exception as exc:  # pragma: no cover - surfaced in Streamlit
            last_error = exc
    raise RuntimeError(f"GEOGLOWS river ID lookup failed: {last_error}")


def geoglows_forecast(river_id: str, timeout: int = 30) -> ForecastResult:
    response = requests.get(f"{GEOGLOWS_BASE}/v2/forecast/{river_id}", timeout=timeout)
    response.raise_for_status()
    df = _as_dataframe(response.json())
    return ForecastResult("GEOGLOWS", str(river_id), df, "Average forecast flow from GEOGLOWS public API")


def geoglows_hydroviewer(river_id: str, timeout: int = 30) -> ForecastResult:
    response = requests.get(f"{GEOGLOWS_BASE}/v2/hydroviewer/{river_id}", timeout=timeout)
    response.raise_for_status()
    df = _as_dataframe(response.json())
    return ForecastResult("GEOGLOWS", str(river_id), df, "Forecast records, stats, and return-period context where available")


def google_flood_placeholder() -> str:
    return (
        "Google Flood Forecasting API integration requires pilot approval, "
        "a Google Cloud project with Flood Forecasting API enabled, and an API key."
    )


def glofas_placeholder() -> str:
    return (
        "GloFAS integration requires Copernicus EWDS/CDS credentials and licence acceptance. "
        "Use it as an independent forecast comparison source, not the only time-critical path."
    )



def _frame_from_time_series(section: dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame(section or {})
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


def open_meteo_forecast(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    timeout: int = 30,
) -> WeatherForecastResult:
    """Fetch point rainfall/weather forecast from Open-Meteo.

    Use as forcing guidance or public forecast context. For HMS calibration,
    observed gauge/IMD rainfall remains authoritative.
    """
    days = max(1, min(int(forecast_days), 16))
    params = {
        "latitude": float(latitude),
        "longitude": float(longitude),
        "hourly": ",".join(
            [
                "precipitation",
                "precipitation_probability",
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "soil_moisture_9_27cm",
            ]
        ),
        "daily": ",".join(
            [
                "precipitation_sum",
                "precipitation_probability_max",
                "temperature_2m_max",
                "temperature_2m_min",
            ]
        ),
        "timezone": "Asia/Kolkata",
        "forecast_days": days,
        "precipitation_unit": "mm",
        "wind_speed_unit": "kmh",
    }
    response = requests.get(OPEN_METEO_BASE, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo forecast request failed"))
    hourly = _frame_from_time_series(payload.get("hourly", {}))
    daily = _frame_from_time_series(payload.get("daily", {}))
    location_id = f"{payload.get('latitude', latitude):.5f},{payload.get('longitude', longitude):.5f}"
    return WeatherForecastResult(
        provider="Open-Meteo",
        location_id=location_id,
        hourly=hourly,
        daily=daily,
        source_url=response.url,
        note="Point rainfall/weather forecast from Open-Meteo public API; no API key required.",
    )



def _google_flood_url(base_url: str, path: str) -> str:
    base = (base_url or GOOGLE_FLOOD_BASE).rstrip("/")
    return f"{base}{path}"


def _google_flood_loop(latitude: float, longitude: float, radius_deg: float = 0.35) -> dict[str, Any]:
    lat = float(latitude)
    lon = float(longitude)
    d = max(0.02, min(float(radius_deg), 2.0))
    return {
        "vertices": [
            {"latitude": lat - d, "longitude": lon - d},
            {"latitude": lat - d, "longitude": lon + d},
            {"latitude": lat + d, "longitude": lon + d},
            {"latitude": lat + d, "longitude": lon - d},
        ]
    }


def _google_flood_post(
    api_key: str,
    path: str,
    body: dict[str, Any],
    base_url: str = GOOGLE_FLOOD_BASE,
    timeout: int = 30,
) -> tuple[dict[str, Any], str]:
    if not api_key:
        raise RuntimeError("Google Flood API key is not configured.")
    url = _google_flood_url(base_url, path)
    response = requests.post(url, params={"key": api_key}, json=body, timeout=timeout)
    response.raise_for_status()
    return response.json(), response.url


def _google_flood_get(
    api_key: str,
    path: str,
    params: dict[str, Any],
    base_url: str = GOOGLE_FLOOD_BASE,
    timeout: int = 30,
) -> tuple[dict[str, Any], str]:
    if not api_key:
        raise RuntimeError("Google Flood API key is not configured.")
    url = _google_flood_url(base_url, path)
    merged = {"key": api_key, **params}
    response = requests.get(url, params=merged, timeout=timeout)
    response.raise_for_status()
    return response.json(), response.url


def google_flood_search_gauges_by_area(
    api_key: str,
    latitude: float,
    longitude: float,
    radius_deg: float = 0.35,
    include_non_quality_verified: bool = True,
    include_gauges_without_hydro_model: bool = False,
    page_size: int = 200,
    base_url: str = GOOGLE_FLOOD_BASE,
) -> GoogleFloodResult:
    body = {
        "loop": _google_flood_loop(latitude, longitude, radius_deg),
        "includeNonQualityVerified": bool(include_non_quality_verified),
        "includeGaugesWithoutHydroModel": bool(include_gauges_without_hydro_model),
        "pageSize": int(page_size),
    }
    payload, source_url = _google_flood_post(api_key, "/v1/gauges:searchGaugesByArea", body, base_url=base_url)
    rows = payload.get("gauges", [])
    return GoogleFloodResult(
        provider="Google Flood API",
        query_type="gauges.searchGaugesByArea",
        data=pd.json_normalize(rows),
        raw=payload,
        source_url=source_url.replace(api_key, "<REDACTED_API_KEY>"),
        note="Searched Google Flood gauges within a bounding loop around the selected node.",
    )


def google_flood_search_latest_status_by_area(
    api_key: str,
    latitude: float,
    longitude: float,
    radius_deg: float = 0.35,
    include_non_quality_verified: bool = True,
    page_size: int = 200,
    base_url: str = GOOGLE_FLOOD_BASE,
) -> GoogleFloodResult:
    body = {
        "loop": _google_flood_loop(latitude, longitude, radius_deg),
        "includeNonQualityVerified": bool(include_non_quality_verified),
        "pageSize": int(page_size),
    }
    payload, source_url = _google_flood_post(api_key, "/v1/floodStatus:searchLatestFloodStatusByArea", body, base_url=base_url)
    rows = payload.get("floodStatuses", [])
    return GoogleFloodResult(
        provider="Google Flood API",
        query_type="floodStatus.searchLatestFloodStatusByArea",
        data=pd.json_normalize(rows),
        raw=payload,
        source_url=source_url.replace(api_key, "<REDACTED_API_KEY>"),
        note="Searched latest Google Flood statuses for gauges inside the selected area.",
    )


def google_flood_query_forecasts(
    api_key: str,
    gauge_ids: list[str],
    base_url: str = GOOGLE_FLOOD_BASE,
) -> GoogleFloodResult:
    clean_ids = [str(g).strip() for g in gauge_ids if str(g).strip()]
    if not clean_ids:
        raise RuntimeError("At least one Google Flood gauge ID is required.")
    params: dict[str, Any] = [("gaugeIds", gid) for gid in clean_ids]
    payload, source_url = _google_flood_get(api_key, "/v1/gauges:queryGaugeForecasts", params, base_url=base_url)
    forecasts = payload.get("forecasts", {})
    rows: list[dict[str, Any]] = []
    for gauge_id, forecast_set in forecasts.items():
        for forecast in forecast_set.get("forecasts", []):
            for value in forecast.get("forecastValues", []):
                row = {"gaugeId": gauge_id, "issuedTime": forecast.get("issuedTime")}
                row.update(value)
                rows.append(row)
    return GoogleFloodResult(
        provider="Google Flood API",
        query_type="gauges.queryGaugeForecasts",
        data=pd.json_normalize(rows),
        raw=payload,
        source_url=source_url.replace(api_key, "<REDACTED_API_KEY>"),
        note="Queried hydrologic forecasts for selected Google Flood gauge IDs.",
    )


def google_flood_query_latest_status_by_gauge_ids(
    api_key: str,
    gauge_ids: list[str],
    base_url: str = GOOGLE_FLOOD_BASE,
) -> GoogleFloodResult:
    clean_ids = [str(g).strip() for g in gauge_ids if str(g).strip()]
    if not clean_ids:
        raise RuntimeError("At least one Google Flood gauge ID is required.")
    params: dict[str, Any] = [("gaugeIds", gid) for gid in clean_ids]
    payload, source_url = _google_flood_get(api_key, "/v1/floodStatus:queryLatestFloodStatusByGaugeIds", params, base_url=base_url)
    rows = payload.get("floodStatuses", [])
    return GoogleFloodResult(
        provider="Google Flood API",
        query_type="floodStatus.queryLatestFloodStatusByGaugeIds",
        data=pd.json_normalize(rows),
        raw=payload,
        source_url=source_url.replace(api_key, "<REDACTED_API_KEY>"),
        note="Queried latest flood statuses for selected Google Flood gauge IDs.",
    )
