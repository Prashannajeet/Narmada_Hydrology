# Stage 112 - Advanced Hydrology Analytics Webmap

Created: 2026-07-20 15:02

## Purpose

This stage creates a consolidated OpenLayers based hydrological command webmap for the Narmada HMS development lifecycle. It is intended as a public-launch showcase and internal QA surface.

## Included data layers

- HMS reviewed subbasin polygons: 51
- HMS reviewed reaches: 53
- Active HMS node connections: 107
- HMS topology nodes: 108
- GD/RWL sites, including active model and future extension points: 92
- Major dams/reservoirs with reviewed reach snapping QA: 10
- Rainfall stations from the SWDES/Narmada station package: 222
- Raw drainage segments for spatial context: 900
- LS04G selected model hydrographs linked to model elements: 13

## SB_Sub_54 emergency topology correction note

The webmap topology source has been switched from the stale Stage98 CSV to the corrected HMS basin file `Narmada_B1_LS04G_Combined_SB22_Corridor_Attenuation.basin`. This is critical because Stage98 still contained the old wrong route `SB_Sub_54 -> R_Sub_1`. The corrected HMS branch has `SB_Sub_54 -> R_Sub_14`, then `R_Sub_14 -> R_R_26 -> R_R_9`, which places it in the corridor between `SB_Sub_14` and `SB_Sub_45`.

Status table: `stage112_sb54_topology_status.csv`.

## Model intelligence attached to features

- Subbasins: area, HSG, CN-II, calibrated effective loss, baseflow share, LULC class, Manning n, rainfall QA, Thiessen station weight summary.
- GD sites: active/future status, observed period and row count, LS04G peak ratio where mapped.
- Dams/reservoirs: original location, snap distance, reviewed HMS reach, priority ranking, readiness/impact/data score, next routing data required.
- Reaches/nodes: downstream topology, Snyder/CWC transform parameters, routing status, LS04G peak, peak hour, and volume where available.

## Important use note

The webmap is a decision and QA dashboard, not a replacement for final HMS, QGIS, or field validation. Handia and Narmadapuram remain priority mapping/attenuation review controls. Barmanghat remains a mapping QA item until final gauge-to-reach alignment is locked.

## 2026-07-20 interaction fix

The click chart now searches downstream through the active HMS topology when an exact feature-level hydrograph is not exported. Subbasins, reservoirs, and intermediate nodes can therefore display the nearest available downstream LS04G hydrograph. For rainfall stations and unmapped future-extension GD sites, the chart shows a hydrology/profile summary rather than an empty hydrograph message.
