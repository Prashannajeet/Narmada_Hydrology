-- PostgreSQL/PostGIS authoritative schema for the PMP Atlas conversion.
-- All source-derived measurements retain page/table provenance.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS pmp;

CREATE TABLE pmp.atlas_document (
  document_id          bigserial PRIMARY KEY,
  document_key         text UNIQUE NOT NULL,
  title                text NOT NULL,
  volume_label         text,
  source_path          text NOT NULL,
  sha256               text,
  pdf_page_count       integer NOT NULL CHECK (pdf_page_count > 0),
  printed_page_range    text,
  source_date           date,
  notes                text
);

CREATE TABLE pmp.atlas_page (
  page_id              bigserial PRIMARY KEY,
  document_id          bigint NOT NULL REFERENCES pmp.atlas_document,
  pdf_page_number      integer NOT NULL CHECK (pdf_page_number > 0),
  printed_page_number  integer,
  page_role             text NOT NULL CHECK (page_role IN ('text','table','map','figure','mixed','blank','unknown')),
  extraction_status     text NOT NULL DEFAULT 'pending',
  text_sha256           text,
  UNIQUE (document_id, pdf_page_number)
);

CREATE TABLE pmp.source_provenance (
  provenance_id        bigserial PRIMARY KEY,
  document_id          bigint REFERENCES pmp.atlas_document,
  page_id              bigint REFERENCES pmp.atlas_page,
  source_label         text,
  source_locator        text,
  extraction_method     text NOT NULL,
  extraction_run_id     text NOT NULL,
  validation_status     text NOT NULL DEFAULT 'unreviewed',
  reviewer_note         text
);

CREATE TABLE pmp.catchment (
  catchment_id         bigserial PRIMARY KEY,
  atlas_code            text UNIQUE NOT NULL,
  name                  text NOT NULL,
  parent_system         text,
  area_km2              numeric,
  geom                  geometry(MultiPolygon, 4326),
  geom_source_id        bigint REFERENCES pmp.source_provenance
);

CREATE TABLE pmp.rainfall_station (
  station_id            bigserial PRIMARY KEY,
  atlas_station_key     text UNIQUE NOT NULL,
  station_name          text NOT NULL,
  district_name         text,
  station_type          text,
  longitude_deg         numeric CHECK (longitude_deg BETWEEN -180 AND 180),
  latitude_deg          numeric CHECK (latitude_deg BETWEEN -90 AND 90),
  data_length_years     numeric,
  geom                  geometry(Point, 4326),
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance
);

CREATE TABLE pmp.station_catchment (
  station_id            bigint NOT NULL REFERENCES pmp.rainfall_station,
  catchment_id          bigint NOT NULL REFERENCES pmp.catchment,
  relationship_type     text NOT NULL DEFAULT 'atlas_assigned',
  source_id             bigint REFERENCES pmp.source_provenance,
  PRIMARY KEY (station_id, catchment_id)
);

CREATE TABLE pmp.station_extreme_rainfall (
  station_extreme_id    bigserial PRIMARY KEY,
  station_id            bigint NOT NULL REFERENCES pmp.rainfall_station,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  rainfall_mm           numeric NOT NULL CHECK (rainfall_mm >= 0),
  event_start_date      date,
  event_end_date        date,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (station_id, duration_hours, rainfall_mm, event_start_date)
);

CREATE TABLE pmp.rainfall_storm (
  storm_id              bigserial PRIMARY KEY,
  atlas_storm_key       text UNIQUE NOT NULL,
  storm_date_text       text NOT NULL,
  storm_start_date      date,
  storm_end_date        date,
  storm_centre_name     text,
  centre_longitude_deg  numeric,
  centre_latitude_deg   numeric,
  barrier_elevation_m   numeric,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance
);

CREATE TABLE pmp.storm_catchment_relation (
  storm_id              bigint NOT NULL REFERENCES pmp.rainfall_storm,
  catchment_id          bigint NOT NULL REFERENCES pmp.catchment,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  relation_type         text NOT NULL CHECK (relation_type IN ('affecting','contributing','envelope','other')),
  source_id             bigint REFERENCES pmp.source_provenance,
  PRIMARY KEY (storm_id, catchment_id, duration_hours, relation_type)
);

CREATE TABLE pmp.grid_point (
  grid_point_id         bigserial PRIMARY KEY,
  atlas_grid_id         text UNIQUE NOT NULL,
  catchment_id          bigint REFERENCES pmp.catchment,
  longitude_deg         numeric,
  latitude_deg          numeric,
  geom                  geometry(Point, 4326),
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance
);

CREATE TABLE pmp.grid_pmp_estimate (
  grid_pmp_id           bigserial PRIMARY KEY,
  grid_point_id         bigint NOT NULL REFERENCES pmp.grid_point,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  area_km2              numeric NOT NULL CHECK (area_km2 > 0),
  grid_rain_depth_mm    numeric,
  contributing_storm_id bigint REFERENCES pmp.rainfall_storm,
  taf                   numeric,
  sps_mm                numeric,
  mmf                   numeric,
  pmp_mm                numeric,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (grid_point_id, duration_hours, area_km2)
);

CREATE TABLE pmp.return_period_rainfall (
  return_rainfall_id    bigserial PRIMARY KEY,
  station_id            bigint NOT NULL REFERENCES pmp.rainfall_station,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  parameter_set         text NOT NULL,
  return_period_years   numeric NOT NULL,
  rainfall_mm           numeric NOT NULL,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (station_id, duration_hours, parameter_set, return_period_years)
);

CREATE TABLE pmp.point_pmp_estimate (
  point_pmp_id          bigserial PRIMARY KEY,
  station_id            bigint NOT NULL REFERENCES pmp.rainfall_station,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  pmp_mm                numeric NOT NULL,
  method                text,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (station_id, duration_hours)
);

CREATE TABLE pmp.time_distribution_coefficient (
  td_id                 bigserial PRIMARY KEY,
  catchment_id          bigint REFERENCES pmp.catchment,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (12,24,48,72)),
  subduration_hours     integer NOT NULL,
  population_class      text NOT NULL DEFAULT 'all_rainspells',
  coefficient_pct        numeric NOT NULL CHECK (coefficient_pct BETWEEN 0 AND 100),
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (catchment_id, duration_hours, subduration_hours, population_class)
);

CREATE TABLE pmp.area_reduction_factor (
  arf_id                bigserial PRIMARY KEY,
  catchment_id          bigint REFERENCES pmp.catchment,
  duration_hours        integer NOT NULL CHECK (duration_hours IN (24,48,72)),
  area_km2              numeric NOT NULL CHECK (area_km2 > 0),
  arf                   numeric NOT NULL CHECK (arf >= 0),
  arf_type              text NOT NULL CHECK (arf_type IN ('envelope','average','selected','other')),
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance,
  UNIQUE (catchment_id, duration_hours, area_km2, arf_type)
);

CREATE TABLE pmp.spatial_product (
  spatial_product_id   bigserial PRIMARY KEY,
  product_key           text UNIQUE NOT NULL,
  product_type          text NOT NULL CHECK (product_type IN ('isohyet','pmp_grid','storm_track','catchment','other')),
  duration_hours        integer,
  area_km2              numeric,
  crs                   text,
  geometry_source       text NOT NULL CHECK (geometry_source IN ('digitized','georeferenced_raster','source_vector','derived')),
  uncertainty_note      text,
  asset_uri             text,
  source_id             bigint NOT NULL REFERENCES pmp.source_provenance
);

CREATE TABLE pmp.model_scenario (
  scenario_id           bigserial PRIMARY KEY,
  scenario_key          text UNIQUE NOT NULL,
  scenario_name         text NOT NULL,
  catchment_id          bigint REFERENCES pmp.catchment,
  duration_hours        integer,
  status                text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','validated','published','retired')),
  derivation_method     text NOT NULL,
  created_at            timestamptz NOT NULL DEFAULT now(),
  approved_at           timestamptz
);

CREATE TABLE pmp.scenario_input (
  scenario_input_id     bigserial PRIMARY KEY,
  scenario_id           bigint NOT NULL REFERENCES pmp.model_scenario,
  input_type            text NOT NULL CHECK (input_type IN ('depth','hyetograph','spatial_rainfall','arf','td_curve','boundary_condition','other')),
  variable_name         text NOT NULL,
  value_numeric         numeric,
  units                 text,
  time_offset_hours     numeric,
  spatial_product_id    bigint REFERENCES pmp.spatial_product,
  source_table          text,
  source_row_key        text,
  derivation_method     text NOT NULL,
  UNIQUE (scenario_id, input_type, variable_name, time_offset_hours, spatial_product_id)
);

-- Versioned export layer for NITA GeoAI and other downstream consumers.
CREATE TABLE pmp.nita_export_manifest (
  export_id             bigserial PRIMARY KEY,
  scenario_id           bigint REFERENCES pmp.model_scenario,
  target_module         text NOT NULL,
  adapter_version       text NOT NULL,
  package_uri           text NOT NULL,
  package_format        text NOT NULL CHECK (package_format IN ('geojson','shapefile_zip','csv','netcdf','cog_geotiff','json','manifest')),
  crs                   text,
  row_or_feature_count  bigint,
  sha256                text,
  generated_at          timestamptz NOT NULL DEFAULT now(),
  validation_status     text NOT NULL DEFAULT 'unvalidated',
  validation_message    text
);

CREATE TABLE pmp.nita_field_mapping (
  mapping_id            bigserial PRIMARY KEY,
  target_module         text NOT NULL,
  adapter_version       text NOT NULL,
  source_table_name     text NOT NULL,
  source_column_name    text NOT NULL,
  target_field_name     text NOT NULL,
  target_type           text,
  target_units          text,
  required_flag         boolean NOT NULL DEFAULT false,
  notes                 text,
  UNIQUE (target_module, adapter_version, source_table_name, source_column_name, target_field_name)
);

CREATE INDEX rainfall_station_geom_gix ON pmp.rainfall_station USING gist (geom);
CREATE INDEX catchment_geom_gix ON pmp.catchment USING gist (geom);
CREATE INDEX grid_point_geom_gix ON pmp.grid_point USING gist (geom);
CREATE INDEX grid_pmp_lookup_ix ON pmp.grid_pmp_estimate (grid_point_id, duration_hours, area_km2);
CREATE INDEX return_period_lookup_ix ON pmp.return_period_rainfall (station_id, duration_hours, return_period_years);
