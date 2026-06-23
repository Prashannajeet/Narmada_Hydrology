export type Role = "admin" | "engineer" | "inspector" | "viewer";
export type RiskClass = "low" | "moderate" | "high" | "critical";
export type DamStatus = "operational" | "under_maintenance" | "decommissioned" | "proposed";

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  role: Role;
}

export interface Dam {
  dam_id: string;
  dam_name: string;
  state: string;
  district?: string | null;
  river_basin?: string | null;
  river_name?: string | null;
  owner_agency?: string | null;
  dam_type?: string | null;
  construction_year?: number | null;
  status: DamStatus;
  risk_class: RiskClass;
  safety_score: number;
  last_inspection_date?: string | null;
  next_inspection_due?: string | null;
  longitude?: number | null;
  latitude?: number | null;
  reservoir_area_sqkm?: number | null;
  engineering?: Record<string, unknown> | null;
  reservoir?: Record<string, unknown> | null;
  documents: Array<Record<string, unknown>>;
}

export interface DamList {
  items: Dam[];
  total: number;
  limit: number;
  offset: number;
}

export interface DamCreatePayload {
  dam_id: string;
  dam_name: string;
  state: string;
  district?: string | null;
  river_basin?: string | null;
  river_name?: string | null;
  owner_agency?: string | null;
  dam_type?: string | null;
  construction_year?: number | null;
  status: DamStatus;
  risk_class: RiskClass;
  safety_score: number;
  longitude?: number | null;
  latitude?: number | null;
  engineering: {
    height_m?: number | null;
    length_m?: number | null;
    spillway_type?: string | null;
    spillway_capacity_cumecs?: number | null;
    seismic_zone?: string | null;
  };
  reservoir: {
    reservoir_name?: string | null;
    gross_storage_mcm?: number | null;
    live_storage_mcm?: number | null;
    current_storage_mcm?: number | null;
    frl_m?: number | null;
    catchment_area_sqkm?: number | null;
  };
}

export interface Analytics {
  total_dams: number;
  critical_dams: number;
  high_risk_dams: number;
  overdue_inspections: number;
  total_live_storage_mcm: number;
  by_risk: Array<{ key: string; count: number }>;
  by_status: Array<{ key: string; count: number }>;
  by_state: Array<{ key: string; count: number }>;
}

export interface ImportantDamItem {
  dam_id: string;
  dam_name: string;
  state: string;
  district: string | null;
  river_basin: string | null;
  river_name: string | null;
  dam_type: string | null;
  construction_year: number | null;
  height_m: number;
  length_m: number;
  spillway_capacity_cumecs: number;
  gross_storage_mcm: number;
  live_storage_mcm: number;
  wims_current_storage_mcm: number | null;
  wims_storage_percent: number | null;
  wims_level_m: number | null;
  wims_observed_at: string | null;
  wims_report_date: string | null;
  wims_source_url: string | null;
  wims_lookup_url: string | null;
  wims_reservoir_code: string | null;
  wims_source_registry: string | null;
  wims_is_stale: boolean;
}

export interface ImportantDamsOverview {
  source: string;
  criteria: string;
  total: number;
  height_qualified: number;
  storage_qualified: number;
  both_qualified: number;
  gross_storage_mcm: number;
  live_storage_mcm: number;
  max_height_m: number;
  max_gross_storage_mcm: number;
  wims_linked_count: number;
  by_state: Array<{ key: string; count: number }>;
  by_basin: Array<{ key: string; count: number }>;
  items: ImportantDamItem[];
}

export interface MpwrdSummary {
  report_date: string;
  total_readings: number;
  linked_dams: number;
  stale_readings: number;
  total_live_capacity_mcm: number;
  current_live_storage_mcm: number;
  avg_storage_percent: number | null;
  fetched_at: string;
}

export interface MpwrdBasin {
  basin_office: string;
  reservoir_count: number;
  live_capacity_mcm: number;
  current_storage_mcm: number;
  avg_storage_percent: number | null;
  stale_count: number;
}

export interface MpwrdReading {
  reservoir_code: string;
  dam_id: string;
  reservoir_name: string;
  basin_office: string | null;
  district: string | null;
  reading_time: string | null;
  frl_m: number | null;
  live_capacity_at_frl_mcm: number | null;
  this_year_level_m: number | null;
  this_year_live_capacity_mcm: number | null;
  this_year_live_storage_percent: number | null;
  this_year_level_observed_date: string | null;
  this_year_is_stale: boolean;
  gate_count_open: number | null;
  gate_discharge_cumec: number | null;
  risk_class: RiskClass | null;
  safety_score: number | null;
  source_registry: string | null;
}

export interface MpwrdOverview {
  summary: MpwrdSummary | null;
  basins: MpwrdBasin[];
  readings: MpwrdReading[];
}

export type InspectionStatus = "draft" | "submitted" | "approved" | "rejected" | "requires_action";
export type InspectionCondition = "satisfactory" | "fair" | "poor" | "unsafe" | "not_accessible";

export interface InspectionObservationPayload {
  section: string;
  condition_rating: InspectionCondition | string;
  severity_rating: RiskClass;
  finding_type?: string | null;
  description?: string | null;
  recommended_action?: string | null;
  requires_maintenance: boolean;
}

export interface InspectionPhotoPayload {
  observation_section?: string | null;
  file_url?: string | null;
  file_name?: string | null;
  mime_type?: string | null;
  caption?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  captured_at?: string | null;
  ai_labels: string[];
}

export interface AssetConditionPayload {
  asset_tag: string;
  asset_type: string;
  asset_name?: string | null;
  condition_rating: InspectionCondition | string;
  severity_rating: RiskClass;
  operational_status?: string | null;
  remarks?: string | null;
  maintenance_priority?: string | null;
}

export interface GeoTaggedDefectPayload {
  observation_section?: string | null;
  defect_type: string;
  severity_rating: RiskClass;
  description?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  chainage_m?: number | null;
  size_estimate?: string | null;
  status: string;
}

export interface FieldInspectionCreatePayload {
  dam_id: string;
  inspection_type: string;
  inspection_date?: string | null;
  severity_rating: RiskClass;
  gps_latitude?: number | null;
  gps_longitude?: number | null;
  gps_accuracy_m?: number | null;
  gps_timestamp?: string | null;
  offline_created: boolean;
  device_id?: string | null;
  qr_asset_tag?: string | null;
  emergency_readiness?: string | null;
  engineer_remarks?: string | null;
  observations: InspectionObservationPayload[];
  photos: InspectionPhotoPayload[];
  asset_conditions: AssetConditionPayload[];
  defects: GeoTaggedDefectPayload[];
}

export interface FieldInspection {
  inspection_id: string;
  dam_id: string;
  dam_name?: string | null;
  state?: string | null;
  district?: string | null;
  inspection_type: string;
  inspection_date: string;
  status: InspectionStatus;
  severity_rating: RiskClass;
  engineer_name?: string | null;
  gps_latitude?: number | null;
  gps_longitude?: number | null;
  gps_timestamp?: string | null;
  offline_created: boolean;
  qr_asset_tag?: string | null;
  emergency_readiness?: string | null;
  engineer_remarks?: string | null;
  reviewer_remarks?: string | null;
  submitted_at?: string | null;
  approved_at?: string | null;
  observation_count: number;
  defect_count: number;
  photo_count: number;
  asset_count: number;
}

export interface FieldInspectionDetail extends FieldInspection {
  observations: Array<Record<string, unknown>>;
  photos: Array<Record<string, unknown>>;
  asset_conditions: Array<Record<string, unknown>>;
  defects: Array<Record<string, unknown>>;
}

export interface FieldInspectionList {
  items: FieldInspection[];
  total: number;
  limit: number;
  offset: number;
}

export type RiskRegisterStatus = "open" | "monitoring" | "mitigating" | "closed" | "accepted";
export type RiskPriority = "low" | "medium" | "high" | "urgent";

export interface RiskRegisterItem {
  risk_id: string;
  dam_id: string;
  dam_name?: string | null;
  state?: string | null;
  district?: string | null;
  risk_code?: string | null;
  risk_title: string;
  risk_category: string;
  risk_source: string;
  trigger_event?: string | null;
  likelihood: number;
  consequence: number;
  risk_score: number;
  risk_level: RiskClass;
  status: RiskRegisterStatus;
  priority: RiskPriority;
  owner_role?: string | null;
  mitigation_plan?: string | null;
  due_date?: string | null;
  review_date?: string | null;
  compliance_flag: boolean;
  ai_flag: boolean;
  maintenance_required: boolean;
  inspection_id?: string | null;
  defect_id?: string | null;
  defect_type?: string | null;
  inspection_status?: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskRegisterSummary {
  total: number;
  critical: number;
  high: number;
  overdue: number;
  due_soon: number;
  open: number;
  mitigating: number;
  compliance_flags: number;
  ai_flags: number;
  maintenance_required: number;
  by_level: Array<{ key: string; count: number }>;
  by_category: Array<{ key: string; count: number }>;
  by_state: Array<{ key: string; count: number }>;
}

export interface RiskRegisterList {
  items: RiskRegisterItem[];
  total: number;
  limit: number;
  offset: number;
  summary: RiskRegisterSummary;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:18080";

export async function apiFetch<T>(path: string, token: string | null, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  return apiFetch<{ access_token: string; user: User }>("/api/auth/login", null, {
    method: "POST",
    body: JSON.stringify({ email, password })
  });
}
