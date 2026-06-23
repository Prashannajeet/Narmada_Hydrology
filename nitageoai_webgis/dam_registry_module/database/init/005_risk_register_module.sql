CREATE TABLE IF NOT EXISTS risk_register (
  risk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dam_id TEXT NOT NULL REFERENCES dams(dam_id) ON DELETE CASCADE,
  inspection_id TEXT REFERENCES field_inspections(inspection_id) ON DELETE SET NULL,
  defect_id UUID REFERENCES geo_tagged_defects(defect_id) ON DELETE SET NULL,
  risk_code TEXT UNIQUE,
  risk_title TEXT NOT NULL,
  risk_category TEXT NOT NULL,
  risk_source TEXT NOT NULL DEFAULT 'risk_engine',
  trigger_event TEXT,
  likelihood INTEGER NOT NULL DEFAULT 3,
  consequence INTEGER NOT NULL DEFAULT 3,
  risk_score INTEGER GENERATED ALWAYS AS (likelihood * consequence) STORED,
  risk_level TEXT NOT NULL DEFAULT 'moderate',
  status TEXT NOT NULL DEFAULT 'open',
  priority TEXT NOT NULL DEFAULT 'medium',
  owner_role TEXT,
  mitigation_plan TEXT,
  due_date DATE,
  review_date DATE,
  compliance_flag BOOLEAN NOT NULL DEFAULT FALSE,
  ai_flag BOOLEAN NOT NULL DEFAULT FALSE,
  maintenance_required BOOLEAN NOT NULL DEFAULT FALSE,
  created_by UUID REFERENCES users(user_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT risk_register_likelihood_chk CHECK (likelihood BETWEEN 1 AND 5),
  CONSTRAINT risk_register_consequence_chk CHECK (consequence BETWEEN 1 AND 5),
  CONSTRAINT risk_register_level_chk CHECK (risk_level IN ('low', 'moderate', 'high', 'critical')),
  CONSTRAINT risk_register_status_chk CHECK (status IN ('open', 'monitoring', 'mitigating', 'closed', 'accepted')),
  CONSTRAINT risk_register_priority_chk CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

CREATE INDEX IF NOT EXISTS idx_risk_register_dam_status ON risk_register(dam_id, status);
CREATE INDEX IF NOT EXISTS idx_risk_register_level ON risk_register(risk_level, priority);
CREATE INDEX IF NOT EXISTS idx_risk_register_due_date ON risk_register(due_date);

INSERT INTO risk_register (
  dam_id, risk_code, risk_title, risk_category, risk_source, trigger_event,
  likelihood, consequence, risk_level, status, priority, owner_role,
  mitigation_plan, due_date, review_date, compliance_flag, maintenance_required
)
SELECT
  dams.dam_id,
  concat('RR-', dams.dam_id, '-BASELINE'),
  concat(dams.dam_name, ' baseline dam safety risk'),
  CASE
    WHEN dams.next_inspection_due < CURRENT_DATE THEN 'inspection_overdue'
    WHEN dams.safety_score < 55 THEN 'structural_safety'
    ELSE 'portfolio_risk'
  END,
  'registry_baseline',
  concat('Risk class ', dams.risk_class::text, '; safety score ', dams.safety_score::text),
  CASE dams.risk_class::text WHEN 'critical' THEN 5 WHEN 'high' THEN 4 WHEN 'moderate' THEN 3 ELSE 2 END,
  CASE WHEN dams.safety_score < 50 THEN 5 WHEN dams.safety_score < 65 THEN 4 WHEN dams.safety_score < 80 THEN 3 ELSE 2 END,
  dams.risk_class::text,
  'open',
  CASE dams.risk_class::text WHEN 'critical' THEN 'urgent' WHEN 'high' THEN 'high' WHEN 'moderate' THEN 'medium' ELSE 'low' END,
  'State Dam Safety Engineer',
  'Confirm latest inspection evidence, review instrumentation trend, and assign mitigation owner.',
  COALESCE(dams.next_inspection_due, CURRENT_DATE + INTERVAL '90 days')::date,
  (CURRENT_DATE + INTERVAL '30 days')::date,
  COALESCE(dams.next_inspection_due < CURRENT_DATE, false),
  COALESCE(dams.status::text = 'under_maintenance', false)
FROM dams
WHERE dams.risk_class IN ('critical', 'high')
ON CONFLICT (risk_code) DO NOTHING;
