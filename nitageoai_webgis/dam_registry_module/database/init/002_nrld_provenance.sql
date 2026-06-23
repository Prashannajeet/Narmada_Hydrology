ALTER TABLE dams
  ADD COLUMN IF NOT EXISTS source_registry TEXT,
  ADD COLUMN IF NOT EXISTS source_record_id TEXT,
  ADD COLUMN IF NOT EXISTS source_publication_year INT,
  ADD COLUMN IF NOT EXISTS source_url TEXT;

CREATE INDEX IF NOT EXISTS idx_dams_source_registry ON dams(source_registry, source_publication_year);
