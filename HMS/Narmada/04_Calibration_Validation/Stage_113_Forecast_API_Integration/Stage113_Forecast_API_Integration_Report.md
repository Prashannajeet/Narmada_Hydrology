# Stage113 - Forecast API Integration

Created: 2026-07-20 15:41

## Objective

Add an operational-ready forecast integration path to the Narmada hydrology dashboard for reservoir inflow forecasting.

## Provider decision

- GEOGLOWS is the fastest implementable source because it has a public REST API and can provide streamflow forecasts and historical/return-period context by river ID.
- GloFAS/CEMS is valuable as an independent ensemble comparison source, but it requires Copernicus EWDS/CDS credentials and the service warns that CDS access is not advised as the sole time-critical operational route.
- Google Flood Forecasting API can add flood status and hydrologic forecast overlays, but access is currently via pilot approval/API key.

## Files created

- `forecast_reservoir_nodes.csv`
- `forecast_provider_matrix.csv`
- `forecast_data_contract.json`
- Streamlit connector: `../Stage_112_Advanced_Hydrology_Analytics_Webmap/streamlit_cloud_app/forecast_connectors.py`
- Streamlit forecast node table: `../Stage_112_Advanced_Hydrology_Analytics_Webmap/streamlit_cloud_app/forecast_reservoir_nodes.csv`
- Example secrets/config: `../Stage_112_Advanced_Hydrology_Analytics_Webmap/streamlit_cloud_app/forecast_config.example.toml`

## Next implementation steps

1. Validate GEOGLOWS nearest river IDs for Tawa, Barna, Indira Sagar, Kolar, Bargi, Omkareshwar, and other active reservoirs.
2. Compare GEOGLOWS forecast/reanalysis against observed reservoir inflow or nearby CWC discharge to estimate bias.
3. Build reservoir inflow forecast transformation from provider flow to HMS reservoir boundary hydrographs.
4. Add Streamlit secrets for Google Flood and Copernicus only after access is approved.
5. Promote forecast overlays into the OpenLayers map after provider IDs are field-verified.
