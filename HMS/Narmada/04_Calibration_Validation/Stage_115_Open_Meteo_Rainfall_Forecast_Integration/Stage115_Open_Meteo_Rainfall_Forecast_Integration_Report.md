# Stage115 Open-Meteo Rainfall Forecast Integration

Created: 2026-07-20 21:12

## Purpose

Stage115 adds Open-Meteo as a no-key rainfall/weather forecast source inside
the existing Narmada Streamlit forecast tab. This is not a replacement for
observed IMD/gauge rainfall used in HMS calibration. It is a live forecast
guidance layer for rainfall outlook at reservoir, gauge, or snapped reach nodes.

## Added To Streamlit

- Provider option: `Open-Meteo rainfall`
- Forecast period selector: 1 to 16 days
- Hourly forecast chart: precipitation and precipitation probability
- Daily forecast chart/table: precipitation sum and probability maximum
- Request URL expander for traceability

## Recommended Hydrology Use

Use Open-Meteo data in three stages:

1. Point forecast QA at dams/gauges.
2. Spatial rainfall weighting across subbasins using stations/grid points.
3. Bias-correction against IMD/CWC observed rainfall before HMS forecast forcing.

## Caution

Open-Meteo is useful for live public guidance, but HMS design/calibration should
still be based on observed rainfall, discharge, AEC curves, reservoir operations,
and validated local parameters.
