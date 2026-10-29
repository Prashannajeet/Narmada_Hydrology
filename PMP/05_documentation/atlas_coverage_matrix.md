# PMP Atlas coverage matrix

This matrix distinguishes source coverage from analysis-ready digitization. A source product is considered captured when its page, label, raw table cells or figure reference is retained with provenance. A product is considered model-ready only after semantic validation, spatial/temporal digitization and hydrologist review.

| Atlas product | Current capture | Database/app surface | Model-ready status |
|---|---|---|---|
| Station inventory and highest 1/2/3-day rainfall | Structured | Station extremes, map and CSV export | Source-linked; review joins before operational use |
| Station climatology: elevation, record period, monsoon/annual mean, SD and CV | Structured, 647 rows | Station climatology workspace | Source-linked; station matching to the wider 1,165-row extreme inventory remains explicit |
| Historical rainstorm catalogue | Structured, 288 rows | Storm catalogue, map and analytics | Source-linked |
| Gumbel parameters and return-period rainfall | Structured, 37,110 rows, EST/LL/UL | Return-period rainfall and station analytics | Source-linked estimates; confidence rows retained |
| DAD storm tables | Structured, 3,635 points | DAD storm evidence and DAD/PMP analytics | Source-linked; verify row continuity and standard areas |
| Grid points and grid PMP/SPS/MMF/TAF values | Structured, 40 grid points and 1,379 estimates | Grid PMP workspace and exports | Source-linked; model use requires basin-specific selection |
| Catchment transposed rainfall | Raw table evidence and page references | Source atlas / raw evidence | Requires semantic extraction and review |
| Time-distribution curves | Figure/table/page references retained | Source atlas | Requires curve digitization into temporal coefficients |
| Area-reduction-factor curves | Figure/table/page references retained | Source atlas | Requires curve digitization and selected/average/envelope classification |
| Precipitable-water lookup tables | Raw table evidence and page references retained | Source atlas | Requires normalized lookup schema and unit checks |
| MAF computation tables | Raw table evidence and page references retained | Source atlas | Requires normalized factor schema and formula validation |
| Basin, station, storm-centre and isohyetal maps | Figure references and page text retained | Source atlas | Requires georeferencing/digitization with CRS and uncertainty |
| Grid areal PMP maps and return-period maps | Figure references and page text retained | Source atlas | Requires georeferencing/digitization; do not infer exact raster values from screenshots |

## Retrieval contract

Every structured record carries a stable key, source document key, PDF page and table label where available. Raw table evidence is retained as JSON cell arrays for audit and future NITA retrieval. Figure/map assets remain source references until their geometry or raster values have been independently digitized and QA-checked.

## Next controlled extraction stages

1. Normalize the raw MAF and precipitable-water tables into typed lookup tables.
2. Digitize time-distribution and area-reduction curves with curve-point uncertainty and method metadata.
3. Georeference and digitize isohyetal, return-period and grid-PMP map plates into GeoPackage/GeoParquet or COG assets.
4. Reconcile all digitized products against printed tables, control points and the source page catalogue before publishing model-input scenarios.
