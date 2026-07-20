# Stage117 Google Flood API Live Connectors

Created: 2026-07-20 23:39

## Purpose

Stage117 converts the Google Flood API panel from secret-status only into live
REST connector actions using the official service endpoint:

`https://floodforecasting.googleapis.com`

## Added Connectors

- `gauges.searchGaugesByArea`
- `floodStatus.searchLatestFloodStatusByArea`
- `gauges.queryGaugeForecasts`
- `floodStatus.queryLatestFloodStatusByGaugeIds`

## Streamlit Workflow

1. Select a reservoir/forecast node.
2. Choose `Google Flood API`.
3. Confirm API key status is configured.
4. Search nearby Google Flood gauges using the selected node latitude/longitude.
5. Copy returned gauge IDs into the gauge ID input.
6. Query forecasts and latest flood status.

## Security

The API key is loaded only from `st.secrets` or environment variables. Request
URLs displayed in the UI redact the key.
