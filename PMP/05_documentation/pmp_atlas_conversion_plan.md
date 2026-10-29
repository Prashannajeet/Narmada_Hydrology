# PMP Atlas conversion plan

## Phase 0 - Source registration

Register both PDFs by SHA-256, preserve their original paths, record page counts, and create `atlas_page` rows. The printed cover label is authoritative for volume identity because the two filenames are reversed.

## Phase 1 - Numeric table extraction

Extract and validate tables in this order:

1. station inventory and observed 1/2/3-day extremes;
2. catchments and grid point locations;
3. storm catalogue and storm-centre data;
4. catchment/grid PMP tables;
5. return-period rainfall and point PMP;
6. time-distribution coefficients;
7. area-reduction factors;
8. precipitable-water and MAF tables.

Each row receives a provenance ID. Numeric columns are normalized to SI-compatible units and retain source text for ambiguous dates, symbols, footnotes or missing values.

## Phase 2 - Spatial products

For each map page, retain the original page image, identify map frame/control points, assign and verify CRS, and digitize only the products needed for analysis. Start with basin/catchment boundaries, station/grid points, PMP grids, and storm isohyets. Store the digitization method and positional uncertainty.

## Phase 3 - Quality assurance

- Reconcile station counts, catchment codes, grid IDs and table totals with the source.
- Compare a sample of extracted rows against rendered PDF pages.
- Check latitude/longitude ranges and known landmarks.
- Check geometry validity and CRS consistency.
- Report rows in/out for every cleaning and join step.
- Re-run extraction to verify deterministic output.

## Phase 4 - Model-ready views

Create views for:

- `vw_station_extreme_rainfall`;
- `vw_return_period_rainfall`;
- `vw_grid_pmp_by_duration_area`;
- `vw_catchment_design_storm_parameters`;
- `vw_model_input_scenarios`.

These views should expose stable IDs, units in column names, provenance, validation status, and the difference between source and derived values.

Add a NITA adapter layer with versioned exports: GeoJSON/AOI, Shapefile ZIP plus keyed rainfall CSV where required by the flood-zone module, COG GeoTIFF plus sidecar metadata, CSV/NetCDF time series, and JSON compatibility payloads. The NITA package is an export target, not the canonical database model.

## Phase 5 - Query/map API

Expose filterable endpoints by basin/catchment, station/grid, duration, area, return period, storm, and scenario. Return both numeric values and source references. A map client can use the same IDs to request spatial products and popup metadata.

Keep the API host and service URLs configurable so the same database can feed NITA's authorized workspace, a separate map client, or a future OGC/ArcGIS service without schema changes.

## Phase 6 - Online inundation integration

Treat the rainfall database as an input service, not as a hydraulic solver. A published scenario should reference the basin/catchment, rainfall depth or hyetograph, temporal distribution, spatial rainfall product, loss/routing assumptions, DEM/roughness/boundaries, model version, and run status. The generated inundation raster/vector should link back to the input scenario and model run.

## First production milestone

Deliver a validated MVP containing station inventory, observed extremes, catchments, storms, grid PMP tables, time-distribution coefficients, ARFs, provenance, and NITA-compatible export packages. Then add georeferenced maps and online model orchestration.
