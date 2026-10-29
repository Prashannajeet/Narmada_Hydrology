# NITA GeoAI integration contract

## Design decision

Keep PostgreSQL/PostGIS as the canonical store and add a versioned export/adapter layer for NITA GeoAI. Do not make NITA's current browser upload fields the authoritative schema because the public site exposes module-specific inputs and may evolve.

## NITA-facing packages

### 1. Basin and station context

- GeoJSON or zipped Shapefile for basin/catchment/AOI boundaries.
- GeoJSON or FeatureServer-compatible station/grid points.
- Stable keys: `catchment_code`, `station_key`, `grid_id`.
- Explicit CRS, preferably EPSG:4326 for web exchange.

### 2. Flood-zone rainfall package

- `rainfall_zones.zip`: polygon zones with a stable `zone_id`.
- `rainfall_timeseries.csv` with at minimum:

```text
zone_id,timestamp,rainfall_mm
103U,2026-10-16T00:00:00Z,0.0
103U,2026-10-16T01:00:00Z,12.5
```

- Manifest records the source scenario, duration, time zone, temporal step, rainfall definition, and derivation method.

### 3. Raster package

- COG GeoTIFF for spatial PMP/rainfall, HAND-supporting layers, terrain derivatives, or inundation outputs.
- Sidecar JSON with CRS, bounds, resolution, nodata, units, band meaning, source scenario, and checksum.
- Never export a PDF map image as a model raster without a georeferencing and uncertainty record.

### 4. Hydrology/model package

- CSV/NetCDF time series for rainfall or other continuous inputs.
- JSON arrays only as a compatibility export for module fields that explicitly request them.
- A machine-readable manifest links each input to scenario ID, catchment ID, units, time basis, and source provenance.

### 5. Optional service integration

- Publish read-only ArcGIS FeatureServer/OGC API endpoints for basin, station, grid, and scenario layers if the NITA workspace needs URL-based access.
- Keep URLs configurable in a deployment manifest; do not embed hostnames in the database.

## Adapter tables/views to add

- `nita_export_manifest`
- `nita_rainfall_zone_export`
- `nita_timeseries_export`
- `nita_spatial_asset_export`
- `nita_field_mapping`

Each export must record adapter version, target module, generated file checksum, CRS, schema version, row/feature count, and validation result.

## Compatibility rules

- Use ASCII field names, UTF-8 encoding, ISO-8601 timestamps, and units in field names where useful.
- Keep both human-readable names and stable machine keys.
- Do not rely on Shapefile as the canonical format; use it only for NITA modules that currently request a Shapefile ZIP.
- Avoid database-specific geometry types in exported JSON; use standard GeoJSON geometry.
- Export nulls explicitly or omit them according to the target module's contract; never convert missing values to zero.
- Validate zone-key uniqueness and ensure every rainfall record joins exactly once to a spatial zone.
- Validate timestamps, monotonic ordering, duplicate timestamps, missing intervals, and rainfall units before upload.
- Preserve source PDFs and page references in a manifest, not inside every large raster cell.

## Current limitation

The public NITA pages describe capabilities and input fields but do not provide a complete stable external API specification. Before production upload, confirm the authorized workspace's exact limits, accepted MIME types, maximum file sizes, authentication method, persistence behavior, and whether service URLs are supported for this project.
