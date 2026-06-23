ALTER TABLE dams
  ADD COLUMN IF NOT EXISTS source_registry TEXT,
  ADD COLUMN IF NOT EXISTS source_record_id TEXT,
  ADD COLUMN IF NOT EXISTS source_publication_year INT,
  ADD COLUMN IF NOT EXISTS source_url TEXT;

CREATE TABLE IF NOT EXISTS mpwrd_reservoir_levels (
  source_registry TEXT NOT NULL DEFAULT 'MPWRD',
  report_date DATE NOT NULL,
  reservoir_code TEXT NOT NULL,
  dam_id TEXT REFERENCES dams(dam_id) ON DELETE SET NULL,
  basin_office TEXT,
  reservoir_name TEXT NOT NULL,
  reading_time TIME,
  district TEXT,
  frl_m NUMERIC(10,2),
  live_capacity_at_frl_mcm NUMERIC(12,3),
  this_year_level_m NUMERIC(10,2),
  this_year_live_capacity_mcm NUMERIC(12,3),
  this_year_live_storage_percent NUMERIC(6,2),
  this_year_level_observed_date DATE,
  this_year_is_stale BOOLEAN NOT NULL DEFAULT FALSE,
  gate_count_open NUMERIC(10,2),
  gate_discharge_cumec NUMERIC(12,3),
  last_year_level_m NUMERIC(10,2),
  last_year_live_capacity_mcm NUMERIC(12,3),
  last_year_live_storage_percent NUMERIC(6,2),
  source_url TEXT NOT NULL,
  raw JSONB NOT NULL DEFAULT '{}'::jsonb,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_registry, report_date, reservoir_code)
);

CREATE INDEX IF NOT EXISTS idx_mpwrd_reservoir_levels_dam_id ON mpwrd_reservoir_levels(dam_id);
CREATE INDEX IF NOT EXISTS idx_mpwrd_reservoir_levels_report_date ON mpwrd_reservoir_levels(report_date DESC);
