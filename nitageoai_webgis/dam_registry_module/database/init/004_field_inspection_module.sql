CREATE TABLE IF NOT EXISTS field_inspections (
  inspection_id TEXT PRIMARY KEY,
  dam_id TEXT NOT NULL REFERENCES dams(dam_id) ON DELETE CASCADE,
  inspection_type TEXT NOT NULL DEFAULT 'routine',
  inspection_date DATE NOT NULL DEFAULT CURRENT_DATE,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ,
  submitted_at TIMESTAMPTZ,
  approved_at TIMESTAMPTZ,
  approved_by UUID REFERENCES users(user_id),
  engineer_id UUID REFERENCES users(user_id),
  engineer_name TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  severity_rating TEXT NOT NULL DEFAULT 'moderate',
  gps_latitude NUMERIC(10,7),
  gps_longitude NUMERIC(10,7),
  gps_accuracy_m NUMERIC(10,2),
  gps_timestamp TIMESTAMPTZ,
  offline_created BOOLEAN NOT NULL DEFAULT FALSE,
  device_id TEXT,
  qr_asset_tag TEXT,
  emergency_readiness TEXT,
  engineer_remarks TEXT,
  reviewer_remarks TEXT,
  synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT field_inspections_status_chk CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'requires_action')),
  CONSTRAINT field_inspections_severity_chk CHECK (severity_rating IN ('low', 'moderate', 'high', 'critical'))
);

CREATE TABLE IF NOT EXISTS inspection_observations (
  observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inspection_id TEXT NOT NULL REFERENCES field_inspections(inspection_id) ON DELETE CASCADE,
  section TEXT NOT NULL,
  condition_rating TEXT NOT NULL DEFAULT 'satisfactory',
  severity_rating TEXT NOT NULL DEFAULT 'low',
  finding_type TEXT,
  description TEXT,
  recommended_action TEXT,
  requires_maintenance BOOLEAN NOT NULL DEFAULT FALSE,
  ai_detection_status TEXT NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inspection_photos (
  photo_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inspection_id TEXT NOT NULL REFERENCES field_inspections(inspection_id) ON DELETE CASCADE,
  observation_id UUID REFERENCES inspection_observations(observation_id) ON DELETE SET NULL,
  file_url TEXT,
  file_name TEXT,
  mime_type TEXT,
  caption TEXT,
  latitude NUMERIC(10,7),
  longitude NUMERIC(10,7),
  captured_at TIMESTAMPTZ,
  ai_defect_score NUMERIC(5,2),
  ai_labels JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS asset_condition (
  asset_condition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inspection_id TEXT NOT NULL REFERENCES field_inspections(inspection_id) ON DELETE CASCADE,
  asset_tag TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  asset_name TEXT,
  condition_rating TEXT NOT NULL DEFAULT 'satisfactory',
  severity_rating TEXT NOT NULL DEFAULT 'low',
  operational_status TEXT,
  remarks TEXT,
  maintenance_priority TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS geo_tagged_defects (
  defect_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inspection_id TEXT NOT NULL REFERENCES field_inspections(inspection_id) ON DELETE CASCADE,
  observation_id UUID REFERENCES inspection_observations(observation_id) ON DELETE SET NULL,
  defect_type TEXT NOT NULL,
  severity_rating TEXT NOT NULL DEFAULT 'moderate',
  description TEXT,
  latitude NUMERIC(10,7),
  longitude NUMERIC(10,7),
  location GEOMETRY(Point, 4326),
  chainage_m NUMERIC(12,2),
  size_estimate TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  risk_engine_status TEXT NOT NULL DEFAULT 'queued',
  maintenance_status TEXT NOT NULL DEFAULT 'queued',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_field_inspections_dam_status ON field_inspections(dam_id, status);
CREATE INDEX IF NOT EXISTS idx_field_inspections_date ON field_inspections(inspection_date DESC);
CREATE INDEX IF NOT EXISTS idx_inspection_observations_inspection ON inspection_observations(inspection_id);
CREATE INDEX IF NOT EXISTS idx_inspection_photos_inspection ON inspection_photos(inspection_id);
CREATE INDEX IF NOT EXISTS idx_asset_condition_inspection ON asset_condition(inspection_id);
CREATE INDEX IF NOT EXISTS idx_geo_tagged_defects_inspection ON geo_tagged_defects(inspection_id);
CREATE INDEX IF NOT EXISTS idx_geo_tagged_defects_location ON geo_tagged_defects USING gist(location);
