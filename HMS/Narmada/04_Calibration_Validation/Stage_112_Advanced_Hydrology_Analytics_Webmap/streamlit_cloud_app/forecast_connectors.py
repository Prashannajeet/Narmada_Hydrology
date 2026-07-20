from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests


GEOGLOWS_BASE = "https://geoglows.ecmwf.int/api"


@dataclass
class ForecastResult:
    provider: str
    river_id: str
    data: pd.DataFrame
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
