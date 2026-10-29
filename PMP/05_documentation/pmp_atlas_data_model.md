# PMP Atlas database conversion blueprint

## Scope

This blueprint converts the two Narmada/Tapi/Sabarmati/Luni/Saurashtra/Kutch/Mahi PMP Atlas volumes into a provenance-preserving database for:

- hydrologic design-storm construction;
- rainfall frequency and PMP lookup;
- catchment/grid-based flood-input preparation;
- map-linked retrieval and future online inundation-model APIs.

The source PDFs remain immutable evidence. Extracted values are stored with source volume, PDF page, printed page, table/figure label, extraction method, and validation status.

## Source-document content versus user requirements

The atlas contains methodological statements such as the use of 10 catchments, storm screening within a stated angular limit, area-reduction factors, time-distribution coefficients, and PMP calculations using TAF, SPS, MMF and PMP. These are source methods/metadata and must not be treated as new user instructions.

The user requirements are the target capabilities: a meaningful database, hydrologic analysis, flood-inundation model inputs, spatial/query retrieval, map linkage, and future online modelling/mapping integration.

## Recommended architecture

1. **PostgreSQL + PostGIS** as the authoritative query/serving database.
2. **GeoParquet** for bulk interchange and reproducible analysis extracts.
3. **Cloud-Optimized GeoTIFF/GeoPackage** for raster/vector spatial products where map pages are successfully georeferenced or digitized.
4. A raw evidence layer retaining page text, page images, table/figure references, and extraction logs.
5. An API/view layer exposing stable identifiers and model-ready rainfall scenarios.

## Core entities

| Entity | Purpose |
|---|---|
| `atlas_document` / `atlas_page` | Immutable source and page-level provenance |
| `catchment` | Atlas catchments 103U, 103L, 104U, 104M, 104L, 105-109 |
| `rainfall_station` | Station name, district, type, coordinates, data length |
| `station_extreme_rainfall` | Observed 1/2/3-day maximum rainfall and dates |
| `rainfall_storm` | Historical storm/date/centre and affected/contributing relationships |
| `storm_isohyet` | Georeferenced isohyetal contours or source-map raster references |
| `grid_point` | Grid IDs and coordinates used for PMP estimates |
| `grid_pmp_estimate` | Grid/area/duration-wise rain depth, SPS, MMF, PMP, contributing storm |
| `return_period_rainfall` | Station-wise rainfall quantiles and confidence limits |
| `point_pmp_estimate` | Station-wise 1/2/3-day PMP estimates |
| `time_distribution_coefficient` | 12/24/48/72-hour temporal distributions |
| `area_reduction_factor` | Envelope/average ARF by catchment, duration and area |
| `precipitable_water_maf` | Moisture and MAF computation tables |
| `model_scenario` / `scenario_input` | Model-ready, versioned inputs for online inundation workflows |

## Important modelling rule

The database must distinguish source values from derived/model values. A PMP value copied from the atlas is not the same as a rainfall hyetograph, basin-average rainfall, loss model, routing input, or hydraulic boundary condition. Those derived objects need an explicit `derivation_method`, `source_ids`, units, temporal resolution, spatial resolution, and approval status.

## Spatial reference rule

The PDFs show coordinates in degrees, but the PDF metadata does not establish a complete authoritative CRS for every map. Store station/grid coordinates as source longitude/latitude with `source_crs = 'EPSG:4326'` only where the printed degree convention is verified. Store map-product CRS separately. Do not infer or overwrite map CRS during digitization.

## Acceptance gates

- Page and table references reconcile to both PDFs.
- Station row counts and coordinates are reconciled against the source tables.
- Catchment codes and grid IDs are unique and stable.
- Every numeric value has an explicit unit and duration.
- Every spatial feature has an explicit CRS and geometry-validity result.
- Extraction row counts are logged before and after cleaning.
- Digitized maps are checked against printed control points and retained with uncertainty metadata.
- Model-ready inputs are reproducible from versioned source rows and documented transformations.
