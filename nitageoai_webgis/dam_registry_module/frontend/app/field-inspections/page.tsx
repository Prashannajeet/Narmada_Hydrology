"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  Camera,
  CheckCircle2,
  ClipboardCheck,
  CloudUpload,
  Compass,
  FileCheck2,
  Gauge,
  MapPin,
  QrCode,
  RefreshCw,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Wrench
} from "lucide-react";
import {
  AssetConditionPayload,
  Dam,
  DamList,
  FieldInspection,
  FieldInspectionCreatePayload,
  FieldInspectionDetail,
  FieldInspectionList,
  GeoTaggedDefectPayload,
  InspectionObservationPayload,
  InspectionPhotoPayload,
  RiskClass,
  apiFetch,
  login
} from "../../lib/api";

const TOKEN_STORAGE_KEY = "dam-registry-token";
const ROLE_STORAGE_KEY = "dam-registry-role";
const sections = [
  "General inspection",
  "Upstream face",
  "Downstream face",
  "Crest",
  "Spillway",
  "Gates and hoists",
  "Energy dissipation structure",
  "Seepage and drainage",
  "Instrumentation",
  "Downstream hazard",
  "Emergency readiness"
];
const severities: RiskClass[] = ["low", "moderate", "high", "critical"];
const conditions = ["satisfactory", "fair", "poor", "unsafe", "not_accessible"];
const defectTypes = ["crack", "seepage", "erosion", "settlement", "vegetation", "gate_malfunction", "spillway_damage", "instrument_fault"];
const today = new Date().toISOString().slice(0, 10);

const defaultObservation = (section: string): InspectionObservationPayload => ({
  section,
  condition_rating: "satisfactory",
  severity_rating: "low",
  finding_type: "",
  description: "",
  recommended_action: "",
  requires_maintenance: false
});

const defaultAsset: AssetConditionPayload = {
  asset_tag: "QR-GATE-01",
  asset_type: "gate",
  asset_name: "Primary gate and hoist",
  condition_rating: "fair",
  severity_rating: "moderate",
  operational_status: "operational",
  remarks: "",
  maintenance_priority: "routine"
};

const defaultDefect: GeoTaggedDefectPayload = {
  observation_section: "Spillway",
  defect_type: "crack",
  severity_rating: "moderate",
  description: "",
  latitude: null,
  longitude: null,
  chainage_m: null,
  size_estimate: "",
  status: "open"
};

const defaultPhoto: InspectionPhotoPayload = {
  observation_section: "General inspection",
  file_name: "mobile-photo-placeholder.jpg",
  mime_type: "image/jpeg",
  caption: "",
  latitude: null,
  longitude: null,
  captured_at: new Date().toISOString(),
  ai_labels: ["queued_for_ai_defect_detection"]
};

export default function FieldInspectionPage() {
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState("viewer");
  const [dams, setDams] = useState<Dam[]>([]);
  const [inspections, setInspections] = useState<FieldInspection[]>([]);
  const [selectedInspection, setSelectedInspection] = useState<FieldInspectionDetail | null>(null);
  const [selectedDamId, setSelectedDamId] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [message, setMessage] = useState("Module ready for mobile inspection sync");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    inspection_type: "routine",
    inspection_date: today,
    severity_rating: "moderate" as RiskClass,
    gps_latitude: "",
    gps_longitude: "",
    gps_accuracy_m: "",
    gps_timestamp: new Date().toISOString(),
    offline_created: true,
    device_id: "NITA-MOBILE-01",
    qr_asset_tag: "QR-GATE-01",
    emergency_readiness: "sirens tested; access route open",
    engineer_remarks: ""
  });
  const [observations, setObservations] = useState<InspectionObservationPayload[]>(() => sections.map(defaultObservation));
  const [asset, setAsset] = useState<AssetConditionPayload>(defaultAsset);
  const [defect, setDefect] = useState<GeoTaggedDefectPayload>(defaultDefect);
  const [photo, setPhoto] = useState<InspectionPhotoPayload>(defaultPhoto);

  const selectedDam = useMemo(() => dams.find((dam) => dam.dam_id === selectedDamId), [dams, selectedDamId]);
  const summary = useMemo(() => {
    const totalDefects = inspections.reduce((sum, item) => sum + item.defect_count, 0);
    const pending = inspections.filter((item) => ["draft", "submitted", "requires_action"].includes(item.status)).length;
    const critical = inspections.filter((item) => item.severity_rating === "critical" || item.severity_rating === "high").length;
    return { total: inspections.length, pending, critical, totalDefects };
  }, [inspections]);

  useEffect(() => {
    const storedToken = readStoredValue(TOKEN_STORAGE_KEY);
    const storedRole = readStoredValue(ROLE_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
      setRole(storedRole || "viewer");
      void loadModule(storedToken);
    }
  }, []);

  useEffect(() => {
    if (token) void loadModule(token);
  }, [statusFilter]);

  async function handleLogin() {
    const session = await login("admin@nita.ai", "nita-admin");
    setToken(session.access_token);
    setRole(session.user.role);
    writeStoredValue(TOKEN_STORAGE_KEY, session.access_token);
    writeStoredValue(ROLE_STORAGE_KEY, session.user.role);
    await loadModule(session.access_token);
    setMessage(`Signed in as ${session.user.full_name}`);
  }

  async function loadModule(authToken = token) {
    if (!authToken) return;
    try {
      const params = new URLSearchParams({ limit: "30" });
      if (statusFilter) params.set("status", statusFilter);
      const [damList, inspectionList] = await Promise.all([
        apiFetch<DamList>("/api/dams?limit=100", authToken),
        apiFetch<FieldInspectionList>(`/api/field-inspections?${params.toString()}`, authToken)
      ]);
      setDams(damList.items);
      setInspections(inspectionList.items);
      if (!selectedDamId && damList.items[0]) setSelectedDamId(damList.items[0].dam_id);
      setMessage(`${inspectionList.total} field inspections linked to registry dams`);
    } catch (error) {
      setToken(null);
      setRole("viewer");
      removeStoredValue(TOKEN_STORAGE_KEY);
      removeStoredValue(ROLE_STORAGE_KEY);
      setMessage(error instanceof Error && error.message.includes("credentials") ? "Session expired. Use demo login to continue." : "Unable to load field inspections.");
    }
  }

  async function useCurrentLocation() {
    if (!navigator.geolocation) {
      setMessage("GPS is not available in this browser session");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const next = {
          lat: position.coords.latitude.toFixed(7),
          lon: position.coords.longitude.toFixed(7),
          acc: Math.round(position.coords.accuracy).toString(),
          time: new Date(position.timestamp).toISOString()
        };
        setForm((current) => ({ ...current, gps_latitude: next.lat, gps_longitude: next.lon, gps_accuracy_m: next.acc, gps_timestamp: next.time }));
        setDefect((current) => ({ ...current, latitude: Number(next.lat), longitude: Number(next.lon) }));
        setPhoto((current) => ({ ...current, latitude: Number(next.lat), longitude: Number(next.lon), captured_at: next.time }));
        setMessage("GPS timestamp and coordinates attached to this inspection");
      },
      () => setMessage("GPS permission was not granted")
    );
  }

  async function createInspection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || !selectedDamId) return;
    setSaving(true);
    try {
      const payload: FieldInspectionCreatePayload = {
        dam_id: selectedDamId,
        inspection_type: form.inspection_type,
        inspection_date: form.inspection_date,
        severity_rating: form.severity_rating,
        gps_latitude: numberOrNull(form.gps_latitude),
        gps_longitude: numberOrNull(form.gps_longitude),
        gps_accuracy_m: numberOrNull(form.gps_accuracy_m),
        gps_timestamp: form.gps_timestamp || null,
        offline_created: form.offline_created,
        device_id: emptyToNull(form.device_id),
        qr_asset_tag: emptyToNull(form.qr_asset_tag),
        emergency_readiness: emptyToNull(form.emergency_readiness),
        engineer_remarks: emptyToNull(form.engineer_remarks),
        observations,
        asset_conditions: asset.asset_tag ? [asset] : [],
        defects: defect.description || defect.defect_type ? [defect] : [],
        photos: photo.file_name || photo.caption ? [photo] : []
      };
      const created = await apiFetch<FieldInspectionDetail>("/api/field-inspections", token, { method: "POST", body: JSON.stringify(payload) });
      setSelectedInspection(created);
      await loadModule(token);
      setMessage(`${created.inspection_id} synced and shared with connected modules`);
    } finally {
      setSaving(false);
    }
  }

  async function openInspection(inspectionId: string) {
    if (!token) return;
    const detail = await apiFetch<FieldInspectionDetail>(`/api/field-inspections/${inspectionId}`, token);
    setSelectedInspection(detail);
  }

  async function updateWorkflow(status: "submitted" | "approved" | "rejected" | "requires_action") {
    if (!token || !selectedInspection) return;
    const detail = await apiFetch<FieldInspectionDetail>(`/api/field-inspections/${selectedInspection.inspection_id}/workflow`, token, {
      method: "PATCH",
      body: JSON.stringify({ status, reviewer_remarks: status === "approved" ? "Reviewed and approved for registry reporting." : "Workflow updated from Module 3 dashboard." })
    });
    setSelectedInspection(detail);
    await loadModule(token);
  }

  function updateObservation(index: number, patch: Partial<InspectionObservationPayload>) {
    setObservations((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, ...patch } : item));
  }

  return (
    <main className="field-page">
      <header className="field-topbar">
        <Link href="/" className="field-back"><ArrowLeft size={18} /> Registry dashboard</Link>
        <div>
          <span>Module 3</span>
          <h1>Geo-Tagged Field Inspection Module</h1>
          <p>Structured mobile inspections with offline capture, GPS evidence, QR assets, workflow approvals, and downstream intelligence sharing.</p>
        </div>
        <button onClick={token ? () => loadModule() : handleLogin} className="field-primary">
          {token ? <RefreshCw size={17} /> : <ShieldCheck size={17} />}
          {token ? "Refresh" : "Demo login"}
        </button>
      </header>

      <section className="field-metrics">
        <Metric icon={<ClipboardCheck size={20} />} label="Inspections" value={summary.total} tone="#14b8a6" />
        <Metric icon={<AlertTriangle size={20} />} label="High priority" value={summary.critical} tone="#fb7185" />
        <Metric icon={<MapPin size={20} />} label="Geo defects" value={summary.totalDefects} tone="#f59e0b" />
        <Metric icon={<FileCheck2 size={20} />} label="Pending workflow" value={summary.pending} tone="#8b5cf6" />
      </section>

      <section className="field-share-strip">
        {[
          ["Risk engine", <Gauge size={16} key="risk" />],
          ["AI defect detection", <Sparkles size={16} key="ai" />],
          ["Compliance module", <ShieldCheck size={16} key="compliance" />],
          ["Report module", <FileCheck2 size={16} key="report" />],
          ["Maintenance module", <Wrench size={16} key="maintenance" />]
        ].map(([label, icon]) => <span key={label as string}>{icon}{label}</span>)}
      </section>

      <div className="field-shell">
        <section className="field-panel field-form-panel">
          <div className="field-panel-heading">
            <div>
              <span>Mobile form</span>
              <h2>Inspection capture</h2>
            </div>
            <strong>{role}</strong>
          </div>
          <form onSubmit={createInspection} className="field-form">
            <div className="field-grid two">
              <label>
                <span>Dam / Reservoir</span>
                <select value={selectedDamId} onChange={(event) => setSelectedDamId(event.target.value)} required>
                  {dams.map((dam) => <option key={dam.dam_id} value={dam.dam_id}>{dam.dam_name} - {dam.state}</option>)}
                </select>
              </label>
              <label>
                <span>Inspection type</span>
                <select value={form.inspection_type} onChange={(event) => setForm({ ...form, inspection_type: event.target.value })}>
                  <option value="routine">Routine inspection</option>
                  <option value="detailed">Detailed inspection</option>
                  <option value="special">Special inspection</option>
                  <option value="post_monsoon">Post-monsoon inspection</option>
                  <option value="emergency">Emergency inspection</option>
                </select>
              </label>
            </div>

            <div className="field-context">
              <strong>{selectedDam?.dam_name || "Select a dam"}</strong>
              <span>{selectedDam?.district || "District pending"} / {selectedDam?.river_basin || "Basin pending"}</span>
            </div>

            <div className="field-grid four">
              <label><span>Date</span><input type="date" value={form.inspection_date} onChange={(event) => setForm({ ...form, inspection_date: event.target.value })} /></label>
              <label><span>Severity</span><select value={form.severity_rating} onChange={(event) => setForm({ ...form, severity_rating: event.target.value as RiskClass })}>{severities.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label><span>Device ID</span><input value={form.device_id} onChange={(event) => setForm({ ...form, device_id: event.target.value })} /></label>
              <label className="field-check"><input type="checkbox" checked={form.offline_created} onChange={(event) => setForm({ ...form, offline_created: event.target.checked })} /><span>Offline form</span></label>
            </div>

            <div className="field-gps-card">
              <div><Compass size={18} /><strong>GPS timestamp</strong><span>{form.gps_timestamp ? new Date(form.gps_timestamp).toLocaleString() : "Not attached"}</span></div>
              <button type="button" onClick={useCurrentLocation}><MapPin size={16} /> Use GPS</button>
              <label><span>Latitude</span><input value={form.gps_latitude} onChange={(event) => setForm({ ...form, gps_latitude: event.target.value })} /></label>
              <label><span>Longitude</span><input value={form.gps_longitude} onChange={(event) => setForm({ ...form, gps_longitude: event.target.value })} /></label>
              <label><span>Accuracy m</span><input value={form.gps_accuracy_m} onChange={(event) => setForm({ ...form, gps_accuracy_m: event.target.value })} /></label>
            </div>

            <div className="field-grid two">
              <label><span><QrCode size={15} /> QR asset tag</span><input value={form.qr_asset_tag} onChange={(event) => setForm({ ...form, qr_asset_tag: event.target.value })} /></label>
              <label><span>Emergency readiness</span><input value={form.emergency_readiness} onChange={(event) => setForm({ ...form, emergency_readiness: event.target.value })} /></label>
            </div>

            <section className="inspection-sections">
              {observations.map((observation, index) => (
                <article className="inspection-section-card" key={observation.section}>
                  <header>
                    <strong>{observation.section}</strong>
                    <label><input type="checkbox" checked={observation.requires_maintenance} onChange={(event) => updateObservation(index, { requires_maintenance: event.target.checked })} /> Maintenance</label>
                  </header>
                  <div className="field-grid three">
                    <label><span>Condition</span><select value={observation.condition_rating} onChange={(event) => updateObservation(index, { condition_rating: event.target.value })}>{conditions.map((item) => <option key={item}>{item}</option>)}</select></label>
                    <label><span>Severity</span><select value={observation.severity_rating} onChange={(event) => updateObservation(index, { severity_rating: event.target.value as RiskClass })}>{severities.map((item) => <option key={item}>{item}</option>)}</select></label>
                    <label><span>Finding</span><input value={observation.finding_type || ""} onChange={(event) => updateObservation(index, { finding_type: event.target.value })} placeholder="crack, seepage, erosion..." /></label>
                  </div>
                  <textarea value={observation.description || ""} onChange={(event) => updateObservation(index, { description: event.target.value })} placeholder="Engineer observation" />
                  <input value={observation.recommended_action || ""} onChange={(event) => updateObservation(index, { recommended_action: event.target.value })} placeholder="Recommended action" />
                </article>
              ))}
            </section>

            <div className="field-grid three">
              <label><span>Defect type</span><select value={defect.defect_type} onChange={(event) => setDefect({ ...defect, defect_type: event.target.value })}>{defectTypes.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label><span>Defect section</span><select value={defect.observation_section || ""} onChange={(event) => setDefect({ ...defect, observation_section: event.target.value })}>{sections.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label><span>Size estimate</span><input value={defect.size_estimate || ""} onChange={(event) => setDefect({ ...defect, size_estimate: event.target.value })} placeholder="2m x 15mm" /></label>
            </div>
            <textarea value={defect.description || ""} onChange={(event) => setDefect({ ...defect, description: event.target.value })} placeholder="Geo-tagged defect description" />

            <div className="field-grid three">
              <label><span>Asset tag</span><input value={asset.asset_tag} onChange={(event) => setAsset({ ...asset, asset_tag: event.target.value })} /></label>
              <label><span>Asset type</span><input value={asset.asset_type} onChange={(event) => setAsset({ ...asset, asset_type: event.target.value })} /></label>
              <label><span>Asset condition</span><select value={asset.condition_rating} onChange={(event) => setAsset({ ...asset, condition_rating: event.target.value })}>{conditions.map((item) => <option key={item}>{item}</option>)}</select></label>
            </div>

            <div className="field-photo-row">
              <Camera size={18} />
              <label><span>Geo-tagged photo</span><input value={photo.file_name || ""} onChange={(event) => setPhoto({ ...photo, file_name: event.target.value })} /></label>
              <label><span>Caption</span><input value={photo.caption || ""} onChange={(event) => setPhoto({ ...photo, caption: event.target.value })} placeholder="Photo note for AI review" /></label>
            </div>

            <textarea value={form.engineer_remarks} onChange={(event) => setForm({ ...form, engineer_remarks: event.target.value })} placeholder="Engineer remarks and inspection conclusion" />
            <button className="field-submit" disabled={!token || saving || !selectedDamId}>
              <CloudUpload size={18} /> {saving ? "Syncing..." : "Sync inspection"}
            </button>
          </form>
        </section>

        <aside className="field-panel field-list-panel">
          <div className="field-panel-heading">
            <div><span>Linked dashboard</span><h2>Inspection register</h2></div>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="">All status</option>
              <option value="draft">Draft</option>
              <option value="submitted">Submitted</option>
              <option value="approved">Approved</option>
              <option value="requires_action">Requires action</option>
            </select>
          </div>
          <p className="field-message">{message}</p>
          <div className="inspection-list">
            {inspections.map((inspection) => (
              <button key={inspection.inspection_id} onClick={() => openInspection(inspection.inspection_id)} className={selectedInspection?.inspection_id === inspection.inspection_id ? "selected" : ""}>
                <span><strong>{inspection.dam_name}</strong><i>{inspection.inspection_id}</i></span>
                <span className={`status-pill ${inspection.status}`}>{inspection.status.replace("_", " ")}</span>
                <small>{inspection.defect_count} defects / {inspection.photo_count} photos / {inspection.asset_count} assets</small>
              </button>
            ))}
          </div>

          {selectedInspection ? (
            <section className="inspection-detail">
              <header>
                <div><span>Selected inspection</span><h3>{selectedInspection.dam_name}</h3></div>
                <strong className={`severity ${selectedInspection.severity_rating}`}>{selectedInspection.severity_rating}</strong>
              </header>
              <div className="detail-grid">
                <span>Date<strong>{formatDate(selectedInspection.inspection_date)}</strong></span>
                <span>Status<strong>{selectedInspection.status.replace("_", " ")}</strong></span>
                <span>GPS<strong>{selectedInspection.gps_latitude ? "attached" : "pending"}</strong></span>
                <span>Engineer<strong>{selectedInspection.engineer_name || "Assigned"}</strong></span>
              </div>
              <div className="workflow-actions">
                <button onClick={() => updateWorkflow("submitted")}><CloudUpload size={15} /> Submit</button>
                <button onClick={() => updateWorkflow("approved")}><CheckCircle2 size={15} /> Approve</button>
                <button onClick={() => updateWorkflow("requires_action")}><AlertTriangle size={15} /> Action</button>
              </div>
              <div className="detail-counts">
                <span>{selectedInspection.observations.length}<small>sections</small></span>
                <span>{selectedInspection.defects.length}<small>defects</small></span>
                <span>{selectedInspection.photos.length}<small>photos</small></span>
                <span>{selectedInspection.asset_conditions.length}<small>assets</small></span>
              </div>
            </section>
          ) : (
            <section className="inspection-empty"><Smartphone size={32} /><strong>Select or sync an inspection</strong><span>Mobile records appear here with approval workflow and linked evidence.</span></section>
          )}
        </aside>
      </div>
    </main>
  );
}

function Metric({ icon, label, value, tone }: { icon: ReactNode; label: string; value: number; tone: string }) {
  return <article className="field-metric" style={{ "--tone": tone } as CSSProperties}>{icon}<span>{label}</span><strong>{value.toLocaleString()}</strong></article>;
}

function readStoredValue(key: string): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(key);
}

function writeStoredValue(key: string, value: string) {
  if (typeof window !== "undefined") window.localStorage.setItem(key, value);
}

function removeStoredValue(key: string) {
  if (typeof window !== "undefined") window.localStorage.removeItem(key);
}

function emptyToNull(value: string | null | undefined) {
  return value?.trim() ? value.trim() : null;
}

function numberOrNull(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && value.trim() ? parsed : null;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}
