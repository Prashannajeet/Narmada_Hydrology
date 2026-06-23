CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'dam_status') THEN
    CREATE TYPE dam_status AS ENUM ('operational', 'under_maintenance', 'decommissioned', 'proposed');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'risk_class') THEN
    CREATE TYPE risk_class AS ENUM ('low', 'moderate', 'high', 'critical');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
    CREATE TYPE user_role AS ENUM ('admin', 'engineer', 'inspector', 'viewer');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role user_role NOT NULL DEFAULT 'viewer',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dams (
  dam_id TEXT PRIMARY KEY,
  dam_name TEXT NOT NULL,
  state TEXT NOT NULL,
  district TEXT,
  river_basin TEXT,
  river_name TEXT,
  owner_agency TEXT,
  dam_type TEXT,
  construction_year INT,
  status dam_status NOT NULL DEFAULT 'operational',
  risk_class risk_class NOT NULL DEFAULT 'moderate',
  safety_score NUMERIC(5,2) NOT NULL DEFAULT 70,
  last_inspection_date DATE,
  next_inspection_due DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dam_engineering (
  dam_id TEXT PRIMARY KEY REFERENCES dams(dam_id) ON DELETE CASCADE,
  height_m NUMERIC(10,2),
  length_m NUMERIC(10,2),
  crest_level_m NUMERIC(10,2),
  spillway_type TEXT,
  spillway_capacity_cumecs NUMERIC(12,2),
  design_flood_cumecs NUMERIC(12,2),
  foundation_type TEXT,
  seismic_zone TEXT,
  instrumentation JSONB NOT NULL DEFAULT '{}'::jsonb,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dam_reservoir (
  dam_id TEXT PRIMARY KEY REFERENCES dams(dam_id) ON DELETE CASCADE,
  reservoir_name TEXT,
  gross_storage_mcm NUMERIC(12,3),
  live_storage_mcm NUMERIC(12,3),
  current_storage_mcm NUMERIC(12,3),
  frl_m NUMERIC(10,2),
  mwl_m NUMERIC(10,2),
  catchment_area_sqkm NUMERIC(12,3),
  command_area_sqkm NUMERIC(12,3),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dam_geometry (
  dam_id TEXT PRIMARY KEY REFERENCES dams(dam_id) ON DELETE CASCADE,
  dam_point GEOMETRY(Point, 4326),
  reservoir_polygon GEOMETRY(MultiPolygon, 4326),
  source_file_name TEXT,
  source_format TEXT,
  uploaded_by UUID REFERENCES users(user_id),
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT dam_geometry_valid_point CHECK (dam_point IS NULL OR ST_IsValid(dam_point)),
  CONSTRAINT dam_geometry_valid_polygon CHECK (reservoir_polygon IS NULL OR ST_IsValid(reservoir_polygon))
);

CREATE TABLE IF NOT EXISTS dam_documents (
  document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dam_id TEXT NOT NULL REFERENCES dams(dam_id) ON DELETE CASCADE,
  document_type TEXT NOT NULL,
  title TEXT NOT NULL,
  file_url TEXT NOT NULL,
  file_name TEXT,
  mime_type TEXT,
  uploaded_by UUID REFERENCES users(user_id),
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(user_id),
  dam_id TEXT REFERENCES dams(dam_id) ON DELETE SET NULL,
  action TEXT NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id TEXT,
  ip_address INET,
  user_agent TEXT,
  before_state JSONB,
  after_state JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dams_search ON dams USING gin (to_tsvector('english', dam_name || ' ' || coalesce(state, '') || ' ' || coalesce(river_basin, '')));
CREATE INDEX IF NOT EXISTS idx_dams_filters ON dams(state, river_basin, risk_class, status);
CREATE INDEX IF NOT EXISTS idx_dam_geometry_point ON dam_geometry USING gist(dam_point);
CREATE INDEX IF NOT EXISTS idx_dam_geometry_reservoir ON dam_geometry USING gist(reservoir_polygon);
CREATE INDEX IF NOT EXISTS idx_dam_documents_dam_id ON dam_documents(dam_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_dam_id_created ON audit_log(dam_id, created_at DESC);

INSERT INTO users (email, full_name, password_hash, role)
VALUES
  ('admin@nita.ai', 'NITA Dam Registry Admin', crypt('nita-admin', gen_salt('bf')), 'admin')
ON CONFLICT (email) DO NOTHING;

INSERT INTO dams (dam_id, dam_name, state, district, river_basin, river_name, owner_agency, dam_type, construction_year, status, risk_class, safety_score, last_inspection_date, next_inspection_due)
VALUES
  ('DAM-MP-0001', 'Gandhi Sagar Dam', 'Madhya Pradesh', 'Mandsaur', 'Chambal', 'Chambal', 'Water Resources Department MP', 'Masonry Gravity', 1960, 'operational', 'high', 74.5, '2026-02-15', '2026-08-15'),
  ('DAM-MP-0002', 'Bargi Dam', 'Madhya Pradesh', 'Jabalpur', 'Narmada', 'Narmada', 'Narmada Valley Development Authority', 'Earthen', 1988, 'operational', 'moderate', 82.0, '2026-01-20', '2026-07-20'),
  ('DAM-MH-0001', 'Jayakwadi Dam', 'Maharashtra', 'Aurangabad', 'Godavari', 'Godavari', 'Government of Maharashtra', 'Earthen', 1976, 'under_maintenance', 'critical', 61.0, '2025-11-10', '2026-05-30')
ON CONFLICT (dam_id) DO NOTHING;

INSERT INTO dam_engineering (dam_id, height_m, length_m, crest_level_m, spillway_type, spillway_capacity_cumecs, design_flood_cumecs, foundation_type, seismic_zone, instrumentation)
VALUES
  ('DAM-MP-0001', 64.6, 514.0, 403.55, 'Ogee gated', 21238, 25500, 'Rock', 'III', '{"piezometers": 12, "uplift_cells": 8, "seepage_weirs": 3}'),
  ('DAM-MP-0002', 69.8, 5357.0, 425.7, 'Radial gated', 24500, 28600, 'Alluvial/Rock', 'III', '{"piezometers": 18, "seismic_sensors": 2}'),
  ('DAM-MH-0001', 41.3, 9998.0, 465.0, 'Gated spillway', 18300, 22000, 'Basalt', 'III', '{"piezometers": 20, "gate_position_sensors": 27}')
ON CONFLICT (dam_id) DO NOTHING;

INSERT INTO dam_reservoir (dam_id, reservoir_name, gross_storage_mcm, live_storage_mcm, current_storage_mcm, frl_m, mwl_m, catchment_area_sqkm, command_area_sqkm)
VALUES
  ('DAM-MP-0001', 'Gandhi Sagar Reservoir', 7746.0, 6920.0, 5110.0, 399.9, 402.3, 22584.0, 4270.0),
  ('DAM-MP-0002', 'Rani Avanti Bai Sagar', 3920.0, 3180.0, 2490.0, 422.76, 424.34, 14556.0, 2450.0),
  ('DAM-MH-0001', 'Nath Sagar', 2909.0, 2170.0, 1210.0, 462.23, 463.91, 21750.0, 1418.0)
ON CONFLICT (dam_id) DO NOTHING;

INSERT INTO dam_geometry (dam_id, dam_point, reservoir_polygon, source_file_name, source_format)
VALUES
  ('DAM-MP-0001', ST_SetSRID(ST_MakePoint(75.537, 24.701), 4326), ST_Multi(ST_GeomFromText('POLYGON((75.43 24.63,75.64 24.64,75.68 24.78,75.50 24.83,75.43 24.63))', 4326)), 'seed.sql', 'WKT'),
  ('DAM-MP-0002', ST_SetSRID(ST_MakePoint(79.927, 22.946), 4326), ST_Multi(ST_GeomFromText('POLYGON((79.74 22.86,80.06 22.88,80.12 23.03,79.84 23.07,79.74 22.86))', 4326)), 'seed.sql', 'WKT'),
  ('DAM-MH-0001', ST_SetSRID(ST_MakePoint(75.379, 19.483), 4326), ST_Multi(ST_GeomFromText('POLYGON((75.21 19.36,75.54 19.38,75.61 19.56,75.32 19.62,75.21 19.36))', 4326)), 'seed.sql', 'WKT')
ON CONFLICT (dam_id) DO NOTHING;
