# Stage118 Main Page Forecast API Bridge

Created: 2026-07-20 23:54

## Purpose

Stage118 integrates live forecast sources into the main Narmada command page.
The detailed `Reservoir inflow forecast` tab remains available, but the first
page now presents Google Flood, GloFAS, GEOGLOWS, and Open-Meteo readiness and
actions above the hydrological webmap.

## Main Page Additions

- Forecast control node selector.
- API readiness strip for Google Flood, GloFAS, GEOGLOWS, and Open-Meteo.
- Google Flood gauge search, flood status search, and forecast query.
- GloFAS credential/readiness card for EWDS/CDS-based integration.
- GEOGLOWS river ID lookup and forecast fetch.
- Open-Meteo rainfall fetch for the selected node.

## Security

Google Flood and GloFAS credentials are read server-side from Streamlit secrets
or environment variables. No key or token is rendered into the embedded HTML.

## Source References

- Google Flood Forecasting REST endpoint: https://floodforecasting.googleapis.com
- GloFAS access path: Copernicus CEMS EWDS/CDS API
