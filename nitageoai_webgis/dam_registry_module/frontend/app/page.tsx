"use client";

import dynamic from "next/dynamic";
import { ChangeEvent, useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, Dispatch, ReactNode, SetStateAction } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Building2,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  Database,
  ExternalLink,
  FileText,
  Filter,
  Gauge,
  HelpCircle,
  Layers,
  Lock,
  MapPinned,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Upload,
  Users,
  X
} from "lucide-react";
import { Analytics, Dam, DamCreatePayload, DamList, ImportantDamsOverview, RiskClass, apiFetch, login } from "../lib/api";

const DamMap = dynamic(() => import("../components/DamMap"), { ssr: false });

const riskOptions: Array<RiskClass | ""> = ["", "critical", "high", "moderate", "low"];
const statusOptions = ["", "operational", "under_maintenance", "decommissioned", "proposed"];
const TOKEN_STORAGE_KEY = "dam-registry-token";
const ROLE_STORAGE_KEY = "dam-registry-role";
const riskPalette: Record<string, string> = {
  critical: "#ef4444",
  high: "#f59e0b",
  moderate: "#facc15",
  low: "#22c55e",
  "not assessed": "#94a3b8"
};
const nrldSummaryRows = [
  { state: "Andaman & Nicobar (UT)", totalDams: 2, completedDams: 2, underConstructionDams: 0, grossStorageBcm: 0.015, completedGrossStorageBcm: 0.015, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.014, completedLiveStorageBcm: 0.014, underConstructionLiveStorageBcm: 0 },
  { state: "Andhra Pradesh", totalDams: 164, completedDams: 140, underConstructionDams: 24, grossStorageBcm: 21.505, completedGrossStorageBcm: 16.023, underConstructionGrossStorageBcm: 5.482, liveStorageBcm: 12.653, completedLiveStorageBcm: 8.445, underConstructionLiveStorageBcm: 4.208 },
  { state: "Arunachal Pradesh", totalDams: 4, completedDams: 1, underConstructionDams: 3, grossStorageBcm: 0.051, completedGrossStorageBcm: 0.006, underConstructionGrossStorageBcm: 0.045, liveStorageBcm: 0.015, completedLiveStorageBcm: 0.004, underConstructionLiveStorageBcm: 0.011 },
  { state: "Assam", totalDams: 5, completedDams: 3, underConstructionDams: 2, grossStorageBcm: 1.864, completedGrossStorageBcm: 0.388, underConstructionGrossStorageBcm: 1.476, liveStorageBcm: 0.704, completedLiveStorageBcm: 0.187, underConstructionLiveStorageBcm: 0.517 },
  { state: "Bihar", totalDams: 28, completedDams: 27, underConstructionDams: 1, grossStorageBcm: 0.758, completedGrossStorageBcm: 0.749, underConstructionGrossStorageBcm: 0.009, liveStorageBcm: 0.899, completedLiveStorageBcm: 0.892, underConstructionLiveStorageBcm: 0.007 },
  { state: "Chhattisgarh", totalDams: 346, completedDams: 339, underConstructionDams: 7, grossStorageBcm: 7.769, completedGrossStorageBcm: 7.75, underConstructionGrossStorageBcm: 0.019, liveStorageBcm: 6.961, completedLiveStorageBcm: 6.944, underConstructionLiveStorageBcm: 0.017 },
  { state: "Goa", totalDams: 5, completedDams: 5, underConstructionDams: 0, grossStorageBcm: 0.299, completedGrossStorageBcm: 0.299, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.288, completedLiveStorageBcm: 0.288, underConstructionLiveStorageBcm: 0 },
  { state: "Gujarat", totalDams: 491, completedDams: 487, underConstructionDams: 4, grossStorageBcm: 23.919, completedGrossStorageBcm: 23.821, underConstructionGrossStorageBcm: 0.098, liveStorageBcm: 18.945, completedLiveStorageBcm: 18.901, underConstructionLiveStorageBcm: 0.044 },
  { state: "Himachal Pradesh", totalDams: 29, completedDams: 23, underConstructionDams: 6, grossStorageBcm: 19.537, completedGrossStorageBcm: 19.497, underConstructionGrossStorageBcm: 0.04, liveStorageBcm: 14.987, completedLiveStorageBcm: 14.973, underConstructionLiveStorageBcm: 0.015 },
  { state: "Haryana", totalDams: 1, completedDams: 1, underConstructionDams: 0, grossStorageBcm: 0.014, completedGrossStorageBcm: 0.014, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.013, completedLiveStorageBcm: 0.013, underConstructionLiveStorageBcm: 0 },
  { state: "Jharkhand", totalDams: 79, completedDams: 55, underConstructionDams: 24, grossStorageBcm: 13.046, completedGrossStorageBcm: 5.882, underConstructionGrossStorageBcm: 7.164, liveStorageBcm: 7.166, completedLiveStorageBcm: 7.166, underConstructionLiveStorageBcm: 0 },
  { state: "Jammu & Kashmir (UT)", totalDams: 15, completedDams: 13, underConstructionDams: 2, grossStorageBcm: 0.819, completedGrossStorageBcm: 0.819, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.236, completedLiveStorageBcm: 0.236, underConstructionLiveStorageBcm: 0 },
  { state: "Karnataka", totalDams: 231, completedDams: 231, underConstructionDams: 0, grossStorageBcm: 35.257, completedGrossStorageBcm: 35.257, underConstructionGrossStorageBcm: 0, liveStorageBcm: 30.764, completedLiveStorageBcm: 30.764, underConstructionLiveStorageBcm: 0 },
  { state: "Kerala", totalDams: 61, completedDams: 61, underConstructionDams: 0, grossStorageBcm: 16.536, completedGrossStorageBcm: 16.536, underConstructionGrossStorageBcm: 0, liveStorageBcm: 12.68, completedLiveStorageBcm: 12.68, underConstructionLiveStorageBcm: 0 },
  { state: "Ladakh UT", totalDams: 2, completedDams: 2, underConstructionDams: 0, grossStorageBcm: 0.053, completedGrossStorageBcm: 0.053, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.01, completedLiveStorageBcm: 0.01, underConstructionLiveStorageBcm: 0 },
  { state: "Maharashtra", totalDams: 2374, completedDams: 2333, underConstructionDams: 41, grossStorageBcm: 37.758, completedGrossStorageBcm: 35.837, underConstructionGrossStorageBcm: 1.921, liveStorageBcm: 29.972, completedLiveStorageBcm: 28.267, underConstructionLiveStorageBcm: 1.705 },
  { state: "Meghalaya", totalDams: 9, completedDams: 8, underConstructionDams: 1, grossStorageBcm: 0.354, completedGrossStorageBcm: 0.354, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.285, completedLiveStorageBcm: 0.285, underConstructionLiveStorageBcm: 0.001 },
  { state: "Manipur", totalDams: 4, completedDams: 3, underConstructionDams: 1, grossStorageBcm: 0.275, completedGrossStorageBcm: 0.099, underConstructionGrossStorageBcm: 0.176, liveStorageBcm: 0.197, completedLiveStorageBcm: 0.072, underConstructionLiveStorageBcm: 0.125 },
  { state: "Madhya Pradesh", totalDams: 1354, completedDams: 1354, underConstructionDams: 0, grossStorageBcm: 52.763, completedGrossStorageBcm: 52.763, underConstructionGrossStorageBcm: 0, liveStorageBcm: 33.829, completedLiveStorageBcm: 33.829, underConstructionLiveStorageBcm: 0 },
  { state: "Mizoram", totalDams: 1, completedDams: 1, underConstructionDams: 0, grossStorageBcm: 1.4, completedGrossStorageBcm: 1.4, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.715, completedLiveStorageBcm: 0.715, underConstructionLiveStorageBcm: 0 },
  { state: "Nagaland", totalDams: 1, completedDams: 1, underConstructionDams: 0, grossStorageBcm: 0.565, completedGrossStorageBcm: 0.565, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.4, completedLiveStorageBcm: 0.4, underConstructionLiveStorageBcm: 0 },
  { state: "Odisha", totalDams: 210, completedDams: 210, underConstructionDams: 0, grossStorageBcm: 32.492, completedGrossStorageBcm: 32.492, underConstructionGrossStorageBcm: 0, liveStorageBcm: 23.401, completedLiveStorageBcm: 23.401, underConstructionLiveStorageBcm: 0 },
  { state: "Punjab", totalDams: 19, completedDams: 18, underConstructionDams: 1, grossStorageBcm: 3.593, completedGrossStorageBcm: 3.472, underConstructionGrossStorageBcm: 0.121, liveStorageBcm: 2.406, completedLiveStorageBcm: 2.397, underConstructionLiveStorageBcm: 0.01 },
  { state: "Rajasthan", totalDams: 314, completedDams: 310, underConstructionDams: 4, grossStorageBcm: 11.419, completedGrossStorageBcm: 11.094, underConstructionGrossStorageBcm: 0.324, liveStorageBcm: 10.643, completedLiveStorageBcm: 10.533, underConstructionLiveStorageBcm: 0.11 },
  { state: "Sikkim", totalDams: 2, completedDams: 2, underConstructionDams: 0, grossStorageBcm: 0.011, completedGrossStorageBcm: 0.011, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0.006, completedLiveStorageBcm: 0.006, underConstructionLiveStorageBcm: 0 },
  { state: "Telangana", totalDams: 174, completedDams: 161, underConstructionDams: 13, grossStorageBcm: 22.609, completedGrossStorageBcm: 22, underConstructionGrossStorageBcm: 0.609, liveStorageBcm: 16.648, completedLiveStorageBcm: 16.11, underConstructionLiveStorageBcm: 0.538 },
  { state: "Tamil Nadu", totalDams: 127, completedDams: 127, underConstructionDams: 0, grossStorageBcm: 7.856, completedGrossStorageBcm: 7.856, underConstructionGrossStorageBcm: 0, liveStorageBcm: 7.305, completedLiveStorageBcm: 7.305, underConstructionLiveStorageBcm: 0 },
  { state: "Tripura", totalDams: 1, completedDams: 1, underConstructionDams: 0, grossStorageBcm: 0, completedGrossStorageBcm: 0, underConstructionGrossStorageBcm: 0, liveStorageBcm: 0, completedLiveStorageBcm: 0, underConstructionLiveStorageBcm: 0 },
  { state: "Uttarakhand", totalDams: 37, completedDams: 32, underConstructionDams: 5, grossStorageBcm: 8.429, completedGrossStorageBcm: 7.484, underConstructionGrossStorageBcm: 0.946, liveStorageBcm: 6.392, completedLiveStorageBcm: 6.055, underConstructionLiveStorageBcm: 0.337 },
  { state: "Uttar Pradesh", totalDams: 155, completedDams: 151, underConstructionDams: 4, grossStorageBcm: 20.766, completedGrossStorageBcm: 20.434, underConstructionGrossStorageBcm: 0.333, liveStorageBcm: 18.361, completedLiveStorageBcm: 18.14, underConstructionLiveStorageBcm: 0.221 },
  { state: "West Bengal", totalDams: 36, completedDams: 36, underConstructionDams: 0, grossStorageBcm: 1.872, completedGrossStorageBcm: 1.872, underConstructionGrossStorageBcm: 0, liveStorageBcm: 1.612, completedLiveStorageBcm: 1.612, underConstructionLiveStorageBcm: 0 }
];
const nrldNationalSummary = {
  state: "India",
  totalDams: 6281,
  completedDams: 6138,
  underConstructionDams: 143,
  grossStorageBcm: 343.605,
  completedGrossStorageBcm: 324.842,
  underConstructionGrossStorageBcm: 18.763,
  liveStorageBcm: 258.509,
  completedLiveStorageBcm: 250.642,
  underConstructionLiveStorageBcm: 7.867
};
const createDefaults = {
  dam_id: "",
  dam_name: "",
  state: "",
  district: "",
  river_basin: "",
  river_name: "",
  owner_agency: "",
  dam_type: "",
  construction_year: "",
  longitude: "",
  latitude: "",
  risk_class: "moderate",
  status: "operational",
  safety_score: "70",
  height_m: "",
  length_m: "",
  spillway_type: "",
  spillway_capacity_cumecs: "",
  seismic_zone: "",
  reservoir_name: "",
  gross_storage_mcm: "",
  live_storage_mcm: "",
  current_storage_mcm: "",
  frl_m: "",
  catchment_area_sqkm: ""
};

export default function Page() {
  const [token, setToken] = useState<string | null>(null);
  const autoLoginAttempted = useRef(false);
  const [role, setRole] = useState("viewer");
  const [dams, setDams] = useState<Dam[]>([]);
  const [selected, setSelected] = useState<Dam | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [importantDams, setImportantDams] = useState<ImportantDamsOverview | null>(null);
  const [query, setQuery] = useState("");
  const [stateFilter, setStateFilter] = useState("");
  const [stateOptions, setStateOptions] = useState<string[]>([]);
  const [riskFilter, setRiskFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [message, setMessage] = useState("Loading registry access...");
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState(createDefaults);
  const [documentTitle, setDocumentTitle] = useState("");
  const [documentType, setDocumentType] = useState("inspection_report");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const saved = readStoredValue(TOKEN_STORAGE_KEY);
    const savedRole = readStoredValue(ROLE_STORAGE_KEY);
    if (saved) {
      setToken(saved);
      setRole(savedRole ?? "viewer");
      return;
    }
    if (!autoLoginAttempted.current) {
      autoLoginAttempted.current = true;
      void handleLogin();
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    const handle = window.setTimeout(() => {
      void loadRegistry(token);
    }, 250);
    return () => window.clearTimeout(handle);
  }, [token, query, stateFilter, riskFilter, statusFilter]);

  const states = useMemo(
    () => Array.from(new Set([...stateOptions, ...dams.map((dam) => dam.state), stateFilter].filter(Boolean))).sort(),
    [dams, stateFilter, stateOptions]
  );
  const writable = ["admin", "engineer", "inspector"].includes(role);

  async function handleLogin() {
    setMessage("Connecting to Dam Safety registry...");
    for (let attempt = 1; attempt <= 2; attempt += 1) {
      try {
        const result = await login("admin@nita.ai", "nita-admin");
        setToken(result.access_token);
        setRole(result.user.role);
        writeStoredValue(TOKEN_STORAGE_KEY, result.access_token);
        writeStoredValue(ROLE_STORAGE_KEY, result.user.role);
        setMessage(`Signed in as ${result.user.full_name}`);
        return;
      } catch (error) {
        if (attempt === 1) {
          setMessage("Waking the registry service...");
          await wait(2500);
          continue;
        }
        setMessage(error instanceof Error ? error.message : "Login failed");
      }
    }
  }

  async function loadRegistry(authToken = token) {
    if (!authToken) return;
    try {
      const listParams = buildFilterParams();
      listParams.set("limit", "50");
      const analyticsParams = buildFilterParams();
      const [damList, stats, importantStats] = await Promise.all([
        apiFetch<DamList>(`/api/dams?${listParams.toString()}`, authToken),
        apiFetch<Analytics>(`/api/analytics/dams?${analyticsParams.toString()}`, authToken),
        apiFetch<ImportantDamsOverview>(`/api/analytics/dams/important-dams?${analyticsParams.toString()}`, authToken)
      ]);
      setDams(damList.items);
      setAnalytics(stats);
      setImportantDams(importantStats);
      setStateOptions((current) =>
        Array.from(new Set([...current, ...stats.by_state.map((item) => item.key), ...damList.items.map((dam) => dam.state)])).sort()
      );
      setSelected((current) => damList.items.find((dam) => dam.dam_id === current?.dam_id) ?? damList.items[0] ?? null);
      setMessage(`${damList.total} dams loaded`);
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Registry load failed";
      if (detail.toLowerCase().includes("credential")) {
        setToken(null);
        setRole("viewer");
        removeStoredValue(TOKEN_STORAGE_KEY);
        removeStoredValue(ROLE_STORAGE_KEY);
        setMessage("Session expired. Use demo login to reload the registry.");
        return;
      }
      setMessage(detail);
    }
  }

  function buildFilterParams() {
    const params = new URLSearchParams();
    if (query) params.set("q", query);
    if (stateFilter) params.set("state", stateFilter);
    if (riskFilter) params.set("risk", riskFilter);
    if (statusFilter) params.set("status", statusFilter);
    return params;
  }

  async function uploadPolygon(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !selected || !token) return;
    const form = new FormData();
    form.append("file", file);
    try {
      await apiFetch(`/api/dams/${selected.dam_id}/reservoir-polygon`, token, { method: "POST", body: form });
      setMessage(`Reservoir polygon uploaded for ${selected.dam_id}`);
      await loadRegistry();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed");
    } finally {
      event.target.value = "";
    }
  }

  async function createDamRecord() {
    if (!token) return;
    if (!createForm.dam_id || !createForm.dam_name || !createForm.state) {
      setMessage("dam_id, dam name, and state are required");
      return;
    }
    const payload: DamCreatePayload = {
      dam_id: createForm.dam_id.trim(),
      dam_name: createForm.dam_name.trim(),
      state: createForm.state.trim(),
      district: emptyToNull(createForm.district),
      river_basin: emptyToNull(createForm.river_basin),
      river_name: emptyToNull(createForm.river_name),
      owner_agency: emptyToNull(createForm.owner_agency),
      dam_type: emptyToNull(createForm.dam_type),
      construction_year: numberOrNull(createForm.construction_year),
      longitude: numberOrNull(createForm.longitude),
      latitude: numberOrNull(createForm.latitude),
      risk_class: createForm.risk_class as RiskClass,
      status: createForm.status as DamCreatePayload["status"],
      safety_score: numberOrDefault(createForm.safety_score, 70),
      engineering: {
        height_m: numberOrNull(createForm.height_m),
        length_m: numberOrNull(createForm.length_m),
        spillway_type: emptyToNull(createForm.spillway_type),
        spillway_capacity_cumecs: numberOrNull(createForm.spillway_capacity_cumecs),
        seismic_zone: emptyToNull(createForm.seismic_zone)
      },
      reservoir: {
        reservoir_name: emptyToNull(createForm.reservoir_name),
        gross_storage_mcm: numberOrNull(createForm.gross_storage_mcm),
        live_storage_mcm: numberOrNull(createForm.live_storage_mcm),
        current_storage_mcm: numberOrNull(createForm.current_storage_mcm),
        frl_m: numberOrNull(createForm.frl_m),
        catchment_area_sqkm: numberOrNull(createForm.catchment_area_sqkm)
      }
    };
    try {
      setBusy(true);
      const created = await apiFetch<Dam>("/api/dams", token, { method: "POST", body: JSON.stringify(payload) });
      setCreateOpen(false);
      setCreateForm(createDefaults);
      setSelected(created);
      setMessage(`${created.dam_id} created`);
      await loadRegistry();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Create dam failed");
    } finally {
      setBusy(false);
    }
  }

  async function uploadDocument(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !selected || !token) return;
    const form = new FormData();
    form.append("document_type", documentType);
    form.append("title", documentTitle || file.name);
    form.append("file", file);
    try {
      setBusy(true);
      await apiFetch(`/api/dams/${selected.dam_id}/documents`, token, { method: "POST", body: form });
      setMessage(`Document uploaded for ${selected.dam_id}`);
      setDocumentTitle("");
      await loadRegistry();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Document upload failed");
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  const riskBreakdown = analytics?.by_risk.length
    ? analytics.by_risk
    : riskOptions.filter(Boolean).map((risk) => ({ key: risk, count: dams.filter((dam) => dam.risk_class === risk).length }));
  const typeBreakdown = getTopCounts(dams.map((dam) => dam.dam_type || "Not classified"), 5);
  const storageBands = getStorageBands(dams);
  const overduePercent = analytics?.total_dams ? Math.round(((analytics.overdue_inspections || 0) / analytics.total_dams) * 100) : 0;
  const liveStorage = numberValue(selected?.reservoir?.live_storage_mcm);
  const grossStorage = numberValue(selected?.reservoir?.gross_storage_mcm);
  const storagePercent = grossStorage ? Math.min(100, Math.round((liveStorage / grossStorage) * 100)) : 0;
  const selectedHeight = numberValue(selected?.engineering?.height_m);
  const selectedLength = numberValue(selected?.engineering?.length_m);
  const selectedSpillway = numberValue(selected?.engineering?.spillway_capacity_cumecs);
  const selectedDocs = selected?.documents ?? [];
  const selectedSummary =
    nrldSummaryRows.find((row) => normalizeSummaryName(row.state) === normalizeSummaryName(stateFilter)) ?? nrldNationalSummary;
  const completedPercent = selectedSummary.totalDams
    ? Math.round((selectedSummary.completedDams / selectedSummary.totalDams) * 100)
    : 0;
  const liveStoragePercent = selectedSummary.grossStorageBcm
    ? Math.round((selectedSummary.liveStorageBcm / selectedSummary.grossStorageBcm) * 100)
    : 0;
  const topDamStates = [...nrldSummaryRows]
    .sort((a, b) => b.totalDams - a.totalDams)
    .slice(0, 5)
    .map((row, index) => ({ label: row.state, value: row.totalDams, color: ["#14b8a6", "#38bdf8", "#60a5fa", "#a78bfa", "#f9a8d4"][index] }));
  const topStorageStates = [...nrldSummaryRows]
    .sort((a, b) => b.liveStorageBcm - a.liveStorageBcm)
    .slice(0, 5)
    .map((row) => ({ label: row.state, value: row.liveStorageBcm }));
  const importantHeightShare = importantDams?.total ? Math.round((importantDams.height_qualified / importantDams.total) * 100) : 0;
  const importantStorageShare = importantDams?.total ? Math.round((importantDams.storage_qualified / importantDams.total) * 100) : 0;
  const importantTopStates = importantDams?.by_state.map((item, index) => ({
    label: titleCase(item.key),
    value: item.count,
    color: ["#f97316", "#fb7185", "#facc15", "#2dd4bf", "#60a5fa", "#a78bfa"][index] ?? "#94a3b8"
  })) ?? [];
  const importantTopBasins = importantDams?.by_basin.map((item) => ({ label: titleCase(item.key), value: item.count })) ?? [];

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark"><ShieldCheck size={24} /></span>
          <div>
            <strong>NITA AI</strong>
            <span>Dam Safety Intelligence Registry</span>
          </div>
        </div>
        <button className="jurisdiction-switch">
          <span><ShieldCheck size={18} /></span>
          <strong>State Engineer</strong>
          <small>{stateFilter || "National Registry"}</small>
          <ChevronDown size={16} />
        </button>
        <nav>
          <a className="active"><Activity size={18} /> Overview</a>
          <a><MapPinned size={18} /> Map</a>
          <a><Building2 size={18} /> Dams</a>
          <a><Layers size={18} /> Reservoirs</a>
          <a href="/flood-season-2026"><Database size={18} /> Flood Season 2026</a>
          <a href="/field-inspections"><ClipboardCheck size={18} /> Inspections</a>
          <a><ShieldCheck size={18} /> Surveillance</a>
          <a href="/risk-register"><AlertTriangle size={18} /> Risk Register</a>
          <a><FileText size={18} /> Documents</a>
          <a><BarChart3 size={18} /> Analytics</a>
          <a><Users size={18} /> Users & Roles</a>
          <a><Settings size={18} /> Settings</a>
        </nav>
        <div className="role-panel">
          <span><HelpCircle size={16} /> Help</span>
          <strong>{role}</strong>
          <button onClick={handleLogin}><Lock size={16} /> Demo login</button>
        </div>
      </aside>

      <section className="workspace">
        <section className="filters commandbar">
          <label className="search">
            <Search size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search dams, reservoirs, basins, districts..." />
          </label>
          <label className="select-control">
            <span>State</span>
            <Filter size={16} />
            <select value={stateFilter} onChange={(event) => setStateFilter(event.target.value)}>
              <option value="">All states</option>
              {states.map((state) => <option key={state}>{state}</option>)}
            </select>
          </label>
          <label className="select-control">
            <span>Basin</span>
            <Database size={16} />
            <select value="" disabled>
              <option>All</option>
            </select>
          </label>
          <label className="select-control">
            <span>Risk Class</span>
            <Gauge size={16} />
            <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}>
              {riskOptions.map((risk) => <option key={risk} value={risk}>{risk || "All risk"}</option>)}
            </select>
          </label>
          <label className="select-control">
            <span>Status</span>
            <Activity size={16} />
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {statusOptions.map((status) => <option key={status} value={status}>{status || "All status"}</option>)}
            </select>
          </label>
          <button className="ghost-action" onClick={() => void loadRegistry()} disabled={!token}><SlidersHorizontal size={16} /> More Filters</button>
          {!token ? <button className="ghost-action" onClick={handleLogin}><Lock size={16} /> Demo login</button> : null}
          <label className={`toolbar-upload ${writable ? "" : "disabled"}`}>
            <Upload size={16} />
            <span>Upload Reservoir Polygon</span>
            <input type="file" accept=".geojson,application/geo+json,application/json" onChange={uploadPolygon} disabled={!writable || !selected} />
          </label>
          <button className="primary-action" onClick={() => setCreateOpen(true)} disabled={!writable}><Plus size={16} /> Create Dam</button>
        </section>

        <section className="holistic-overview">
          <header>
            <div>
              <span>OCR source: Reports/Summary.pdf</span>
              <h1>National Large Dam Summary</h1>
            </div>
            <strong>{selectedSummary.state === "India" ? "All India" : selectedSummary.state}</strong>
          </header>
          <div className="holistic-metrics">
            <SummaryMetric label="Total large dams" value={formatNumber(selectedSummary.totalDams)} accent="#14b8a6" />
            <SummaryMetric label="Completed" value={formatNumber(selectedSummary.completedDams)} accent="#22c55e" />
            <SummaryMetric label="Under construction" value={formatNumber(selectedSummary.underConstructionDams)} accent="#f59e0b" />
            <SummaryMetric label="Gross storage" value={`${formatDecimal(selectedSummary.grossStorageBcm)} BCM`} accent="#3b82f6" />
            <SummaryMetric label="Live storage" value={`${formatDecimal(selectedSummary.liveStorageBcm)} BCM`} accent="#a855f7" />
          </div>
          <div className="holistic-charts">
            <article className="holistic-card compact">
              <div>
                <strong>Completion Status</strong>
                <span>{formatNumber(selectedSummary.completedDams)} of {formatNumber(selectedSummary.totalDams)} dams completed</span>
              </div>
              <DonutChart value={completedPercent} tone="#22c55e" label={`${completedPercent}%`} />
              <ChartLegend rows={[
                { label: "Completed", value: selectedSummary.completedDams, color: "#22c55e" },
                { label: "Under construction", value: selectedSummary.underConstructionDams, color: "#f59e0b" }
              ]} total={selectedSummary.totalDams} />
            </article>
            <article className="holistic-card">
              <div>
                <strong>Top States by Dams</strong>
                <span>Highest dam counts from the OCR summary</span>
              </div>
              <HorizontalBars rows={topDamStates} />
            </article>
            <article className="holistic-card">
              <div>
                <strong>Top Live Storage States</strong>
                <span>BCM, ranked nationally</span>
              </div>
              <VerticalBars rows={topStorageStates} />
            </article>
            <article className="holistic-card compact">
              <div>
                <strong>Storage Utilization</strong>
                <span>Live storage as share of gross storage</span>
              </div>
              <DonutChart value={liveStoragePercent} tone="#0ea5e9" label={`${liveStoragePercent}%`} />
              <ChartLegend rows={[
                { label: "Live storage BCM", value: selectedSummary.liveStorageBcm, color: "#0ea5e9" },
                { label: "Gross storage BCM", value: selectedSummary.grossStorageBcm, color: "#c4b5fd" }
              ]} total={selectedSummary.grossStorageBcm} />
            </article>
          </div>
        </section>

        <section className="main-grid">
          <div className="map-panel">
            {token ? (
              <DamMap dams={dams} selectedDamId={selected?.dam_id} stateFilter={stateFilter} onSelect={setSelected} />
            ) : (
              <div className="locked-map">Loading protected dam assets...</div>
            )}
            <div className="map-legend">
              <strong>Legend</strong>
              {["critical", "high", "moderate", "low", "not assessed"].map((risk) => (
                <span key={risk}><i style={{ background: riskPalette[risk] }} /> {risk === "critical" ? "Extreme" : titleCase(risk)}</span>
              ))}
              <em><Layers size={16} /> Reservoir</em>
              <em><MapPinned size={16} /> Dam</em>
              <em><span className="line-swatch state-line" /> State boundary</em>
              <em><span className="line-swatch district-line" /> District boundary</em>
            </div>
          </div>
          <aside className="inspector">
            {selected ? (
              <>
                <div className="drawer-actions">
                  <button><ArrowLeft size={14} /> Back to Results</button>
                  <span><ChevronLeft size={14} /> Prev</span>
                  <span>Next <ChevronRight size={14} /></span>
                  <ExternalLink size={16} />
                  <X size={16} />
                </div>
                <div className="inspector-head">
                  <div>
                    <h2>{selected.dam_name}</h2>
                    <span>{selected.dam_id} - {selected.district ?? selected.state}</span>
                  </div>
                  <strong className={`risk ${selected.risk_class}`}>{selected.risk_class}</strong>
                </div>
                <div className="tabs">
                  <span className="active">Overview</span>
                  <span>Engineering</span>
                  <span>Safety</span>
                  <span>Documents</span>
                  <span>History</span>
                </div>
                <dl className="facts">
                  <div><dt>Dam Type</dt><dd>{selected.dam_type ? titleCase(selected.dam_type) : "Not set"}</dd></div>
                  <div><dt>Year of Completion</dt><dd>{selected.construction_year ?? "Unknown"}</dd></div>
                  <div><dt>Height (m)</dt><dd>{formatNumber(selectedHeight)}</dd></div>
                  <div><dt>Length (m)</dt><dd>{formatNumber(selectedLength)}</dd></div>
                  <div><dt>Gross Storage (MCM)</dt><dd>{formatNumber(grossStorage)}</dd></div>
                  <div><dt>Live Storage (MCM)</dt><dd>{formatNumber(liveStorage)}</dd></div>
                  <div><dt>River Basin</dt><dd>{selected.river_basin ?? "Not set"}</dd></div>
                  <div><dt>Operating Agency</dt><dd>{selected.owner_agency ?? "Not set"}</dd></div>
                  <div><dt>Spillway Capacity</dt><dd>{formatNumber(selectedSpillway)}</dd></div>
                  <div><dt>Safety score</dt><dd>{selected.safety_score}</dd></div>
                </dl>
                <section className="safety-card">
                  <div>
                    <strong>Safety Status</strong>
                    <span className={`risk ${selected.risk_class}`}>{selected.risk_class}</span>
                  </div>
                  <dl>
                    <div><dt>Last Safety Review</dt><dd>{selected.last_inspection_date ?? "Not recorded"}</dd></div>
                    <div><dt>Next Review Due</dt><dd>{selected.next_inspection_due ?? "Not scheduled"}</dd></div>
                    <div><dt>Dam Safety Rating</dt><dd>{selected.risk_class === "low" ? "A" : selected.risk_class === "moderate" ? "B" : "C"}</dd></div>
                  </dl>
                </section>
                <div className="storage-card">
                  <div>
                    <strong>Reservoir - Live Storage</strong>
                    <small>Updated: registry import</small>
                  </div>
                  <DonutChart value={storagePercent} tone="#159aa0" label={`${storagePercent}%`} />
                  <dl>
                    <div><dt>Live Storage</dt><dd>{formatNumber(liveStorage)} MCM</dd></div>
                    <div><dt>Gross Storage</dt><dd>{formatNumber(grossStorage)} MCM</dd></div>
                    <div><dt>FRL</dt><dd>{formatNumber(numberValue(selected.reservoir?.frl_m))} m</dd></div>
                  </dl>
                </div>
                <div className="document-upload">
                  <div className="section-title">
                    <FileText size={16} />
                    <strong>Documents</strong>
                    <span>{selectedDocs.length}</span>
                  </div>
                  {(selectedDocs.length ? selectedDocs.slice(0, 3) : [
                    { title: "O&M Manual", document_type: "PDF", file_name: "Pending upload" },
                    { title: "Structural Health Report", document_type: "PDF", file_name: "Pending upload" },
                    { title: "Hydrological Monograph", document_type: "PDF", file_name: "Pending upload" }
                  ]).map((doc, index) => (
                    <div className="document-row" key={`${String(doc.title)}-${index}`}>
                      <FileText size={16} />
                      <strong>{String(doc.title ?? "Registry document")}</strong>
                      <span>{String(doc.document_type ?? "PDF")}</span>
                      <small>{String(doc.file_name ?? "Registry file")}</small>
                    </div>
                  ))}
                  <input value={documentTitle} onChange={(event) => setDocumentTitle(event.target.value)} placeholder="Document title" disabled={!writable || busy} />
                  <label className={`upload secondary ${writable ? "" : "disabled"}`}>
                    <Upload size={18} />
                    <span>Attach document</span>
                    <input type="file" onChange={uploadDocument} disabled={!writable || busy} />
                  </label>
                </div>
              </>
            ) : (
              <div className="empty">Select a dam marker or row.</div>
            )}
          </aside>
        </section>

        <section className="important-dams-dashboard">
          <header>
            <div>
              <h2>Important Dams - Height 100m+ or Gross Storage 1 BCM+</h2>
            </div>
            <strong>{importantDams?.criteria ?? "Height >= 100 m or gross storage >= 1 BCM"}</strong>
          </header>
          <div className="important-layout">
            <div className="important-metrics">
              <SummaryMetric label="Important dams" value={formatNumber(importantDams?.total)} accent="#f97316" />
              <SummaryMetric label="Height qualified" value={formatNumber(importantDams?.height_qualified)} accent="#fb7185" />
              <SummaryMetric label="Storage qualified" value={formatNumber(importantDams?.storage_qualified)} accent="#3b82f6" />
              <SummaryMetric label="Both criteria" value={formatNumber(importantDams?.both_qualified)} accent="#14b8a6" />
              <SummaryMetric label="Max height" value={`${formatNumber(importantDams?.max_height_m)} m`} accent="#8b5cf6" />
              <SummaryMetric label="WIMS live links" value={formatNumber(importantDams?.wims_linked_count)} accent="#0ea5e9" />
            </div>
            <div className="important-charts">
              <article className="holistic-card compact">
                <div>
                  <strong>Qualification Mix</strong>
                  <span>Linked to active dashboard filters</span>
                </div>
                <DonutChart value={importantHeightShare} tone="#fb7185" label={`${importantHeightShare}%`} />
                <ChartLegend rows={[
                  { label: "Height >= 100m", value: importantDams?.height_qualified ?? 0, color: "#fb7185" },
                  { label: "Storage >= 1 BCM", value: importantDams?.storage_qualified ?? 0, color: "#3b82f6" }
                ]} total={importantDams?.total ?? 0} />
              </article>
              <article className="holistic-card">
                <div>
                  <strong>Top States</strong>
                  <span>Important dam concentration</span>
                </div>
                <HorizontalBars rows={importantTopStates} />
              </article>
              <article className="holistic-card">
                <div>
                  <strong>Top Basins</strong>
                  <span>Ranked by important dam count</span>
                </div>
                <VerticalBars rows={importantTopBasins.slice(0, 5)} />
              </article>
              <article className="holistic-card compact">
                <div>
                  <strong>Storage Rule Share</strong>
                  <span>1 BCM gross storage threshold</span>
                </div>
                <DonutChart value={importantStorageShare} tone="#3b82f6" label={`${importantStorageShare}%`} />
                <ChartLegend rows={[
                  { label: "Storage qualified", value: importantDams?.storage_qualified ?? 0, color: "#3b82f6" },
                  { label: "Other important", value: Math.max(0, (importantDams?.total ?? 0) - (importantDams?.storage_qualified ?? 0)), color: "#e2e8f0" }
                ]} total={importantDams?.total ?? 0} />
              </article>
            </div>
          </div>
          <div className="important-table-wrap">
            <table className="important-table">
              <thead>
                <tr>
                  <th>Dam</th>
                  <th>State</th>
                  <th>Height</th>
                  <th>Gross Storage</th>
                  <th>Live Storage</th>
                  <th>WIMS Live Storage</th>
                  <th>Basin</th>
                </tr>
              </thead>
              <tbody>
                {(importantDams?.items ?? []).map((item) => (
                  <tr key={item.dam_id} onClick={() => setSelected(dams.find((dam) => dam.dam_id === item.dam_id) ?? selected)}>
                    <td>
                      <strong>{item.dam_name}</strong>
                      <span>{item.dam_id} - {item.district ?? "District not set"}</span>
                    </td>
                    <td>{item.state}</td>
                    <td>{formatNumber(item.height_m)} m</td>
                    <td>{formatNumber(item.gross_storage_mcm)} MCM</td>
                    <td>{formatNumber(item.live_storage_mcm)} MCM</td>
                    <td>
                      {item.wims_current_storage_mcm !== null ? (
                        <span className="wims-live-cell">
                          <strong>{formatNumber(item.wims_current_storage_mcm)} MCM</strong>
                          <em>
                            {formatNumber(item.wims_storage_percent)}%
                            {item.wims_level_m !== null ? ` at ${formatNumber(item.wims_level_m)} m` : ""}
                            {item.wims_is_stale ? " - stale" : ""}
                          </em>
                          {item.wims_lookup_url ? (
                            <a href={item.wims_lookup_url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                              Open WIMS
                            </a>
                          ) : null}
                        </span>
                      ) : (
                        <span className="wims-live-cell muted">
                          <em>No live reading</em>
                          {item.wims_lookup_url ? (
                            <a href={item.wims_lookup_url} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>
                              Lookup in WIMS
                            </a>
                          ) : null}
                        </span>
                      )}
                    </td>
                    <td>{item.river_basin ?? "Not set"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="insight-grid">
          <ChartCard title="Dams by Risk Class" subtitle={`Total: ${formatNumber(analytics?.total_dams)}`} action="View full report">
            <div className="split-chart">
              <DonutChart value={analytics?.total_dams ? Math.round(((analytics.high_risk_dams + analytics.critical_dams) / analytics.total_dams) * 100) : 0} tone="#f59e0b" label={`${analytics?.high_risk_dams ?? 0}`} />
              <ChartLegend rows={riskBreakdown.map((item) => ({ label: titleCase(item.key), value: item.count, color: riskPalette[item.key] ?? "#8b9bb0" }))} total={analytics?.total_dams ?? 0} />
            </div>
          </ChartCard>
          <ChartCard title="Dams by Type" subtitle={`Visible sample: ${dams.length}`} action="View full report">
            <HorizontalBars rows={typeBreakdown.map((item, index) => ({ label: titleCase(item.key), value: item.count, color: ["#3b82f6", "#60a5fa", "#93c5fd", "#38bdf8", "#7dd3fc"][index] }))} />
          </ChartCard>
          <ChartCard title="Storage Capacity (Live Storage)" subtitle={`Total: ${formatNumber(analytics?.total_live_storage_mcm)} MCM`} action="View full report">
            <VerticalBars rows={storageBands} />
          </ChartCard>
          <ChartCard title="Inspections Overdue" subtitle={`Total: ${formatNumber(analytics?.total_dams)}`} action="View full report">
            <div className="split-chart">
              <DonutChart value={overduePercent} tone="#22c55e" label={`${overduePercent}%`} />
              <ChartLegend rows={[
                { label: "Overdue > 1 year", value: Math.round((analytics?.overdue_inspections ?? 0) * 0.22), color: "#ef4444" },
                { label: "Overdue 6-12 months", value: Math.round((analytics?.overdue_inspections ?? 0) * 0.34), color: "#f59e0b" },
                { label: "Overdue < 6 months", value: Math.round((analytics?.overdue_inspections ?? 0) * 0.44), color: "#facc15" },
                { label: "Not Overdue", value: Math.max(0, (analytics?.total_dams ?? 0) - (analytics?.overdue_inspections ?? 0)), color: "#22c55e" }
              ]} total={analytics?.total_dams ?? 0} />
            </div>
          </ChartCard>
        </section>
      </section>
      {createOpen ? (
        <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="Create dam">
          <section className="modal">
            <header className="modal-head">
              <div>
                <span>Registry intake</span>
                <h2>Create Dam Record</h2>
              </div>
              <button aria-label="Close create dam" onClick={() => setCreateOpen(false)}><X size={18} /></button>
            </header>
            <div className="form-grid">
              <Field label="Dam ID" name="dam_id" value={createForm.dam_id} onChange={setCreateForm} required />
              <Field label="Dam name" name="dam_name" value={createForm.dam_name} onChange={setCreateForm} required />
              <Field label="State" name="state" value={createForm.state} onChange={setCreateForm} required />
              <Field label="District" name="district" value={createForm.district} onChange={setCreateForm} />
              <Field label="River basin" name="river_basin" value={createForm.river_basin} onChange={setCreateForm} />
              <Field label="River" name="river_name" value={createForm.river_name} onChange={setCreateForm} />
              <Field label="Owner agency" name="owner_agency" value={createForm.owner_agency} onChange={setCreateForm} />
              <Field label="Dam type" name="dam_type" value={createForm.dam_type} onChange={setCreateForm} />
              <Field label="Year" name="construction_year" value={createForm.construction_year} onChange={setCreateForm} />
              <label><span>Risk</span><select value={createForm.risk_class} onChange={(event) => setCreateForm((current) => ({ ...current, risk_class: event.target.value }))}>{riskOptions.filter(Boolean).map((risk) => <option key={risk}>{risk}</option>)}</select></label>
              <label><span>Status</span><select value={createForm.status} onChange={(event) => setCreateForm((current) => ({ ...current, status: event.target.value }))}>{statusOptions.filter(Boolean).map((status) => <option key={status}>{status}</option>)}</select></label>
              <Field label="Safety score" name="safety_score" value={createForm.safety_score} onChange={setCreateForm} />
              <Field label="Longitude" name="longitude" value={createForm.longitude} onChange={setCreateForm} />
              <Field label="Latitude" name="latitude" value={createForm.latitude} onChange={setCreateForm} />
              <Field label="Height m" name="height_m" value={createForm.height_m} onChange={setCreateForm} />
              <Field label="Length m" name="length_m" value={createForm.length_m} onChange={setCreateForm} />
              <Field label="Spillway" name="spillway_type" value={createForm.spillway_type} onChange={setCreateForm} />
              <Field label="Spillway cumecs" name="spillway_capacity_cumecs" value={createForm.spillway_capacity_cumecs} onChange={setCreateForm} />
              <Field label="Seismic zone" name="seismic_zone" value={createForm.seismic_zone} onChange={setCreateForm} />
              <Field label="Reservoir" name="reservoir_name" value={createForm.reservoir_name} onChange={setCreateForm} />
              <Field label="Gross MCM" name="gross_storage_mcm" value={createForm.gross_storage_mcm} onChange={setCreateForm} />
              <Field label="Live MCM" name="live_storage_mcm" value={createForm.live_storage_mcm} onChange={setCreateForm} />
              <Field label="Current MCM" name="current_storage_mcm" value={createForm.current_storage_mcm} onChange={setCreateForm} />
              <Field label="FRL m" name="frl_m" value={createForm.frl_m} onChange={setCreateForm} />
              <Field label="Catchment sq km" name="catchment_area_sqkm" value={createForm.catchment_area_sqkm} onChange={setCreateForm} />
            </div>
            <footer className="modal-actions">
              <button onClick={() => setCreateOpen(false)} disabled={busy}>Cancel</button>
              <button onClick={() => void createDamRecord()} disabled={busy}>{busy ? "Creating..." : "Create record"}</button>
            </footer>
          </section>
        </div>
      ) : null}
    </main>
  );
}

function readStoredValue(key: string): string | null {
  try {
    return typeof window !== "undefined" && window.localStorage ? window.localStorage.getItem(key) : null;
  } catch {
    return null;
  }
}

function writeStoredValue(key: string, value: string) {
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      window.localStorage.setItem(key, value);
    }
  } catch {
    // Some embedded browsers disable persistent storage; in-memory React state still keeps the session active.
  }
}

function removeStoredValue(key: string) {
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      window.localStorage.removeItem(key);
    }
  } catch {
    // Storage cleanup is best-effort in embedded browser contexts.
  }
}

function ChartCard({ title, subtitle, action, children }: { title: string; subtitle: string; action: string; children: ReactNode }) {
  return (
    <article className="chart-card">
      <header>
        <div>
          <strong>{title}</strong>
          <span>{subtitle}</span>
        </div>
      </header>
      {children}
      <button>{action} <ChevronRight size={14} /></button>
    </article>
  );
}

function SummaryMetric({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <article className="summary-metric" style={{ "--accent": accent } as CSSProperties}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function DonutChart({ value, tone, label }: { value: number; tone: string; label: string }) {
  return (
    <div className="donut" style={{ "--value": `${Math.max(0, Math.min(100, value))}%`, "--tone": tone } as CSSProperties}>
      <span>{label}</span>
    </div>
  );
}

function ChartLegend({ rows, total }: { rows: Array<{ label: string; value: number; color: string }>; total: number }) {
  return (
    <div className="chart-legend">
      {rows.map((row) => (
        <span key={row.label}>
          <i style={{ background: row.color }} />
          <strong>{row.label}</strong>
          <em>{formatNumber(row.value)} ({total ? Math.round((row.value / total) * 100) : 0}%)</em>
        </span>
      ))}
    </div>
  );
}

function HorizontalBars({ rows }: { rows: Array<{ label: string; value: number; color: string }> }) {
  const max = Math.max(1, ...rows.map((row) => row.value));
  return (
    <div className="hbars">
      {rows.map((row) => (
        <span key={row.label}>
          <strong>{row.label}</strong>
          <i><b style={{ width: `${(row.value / max) * 100}%`, background: row.color }} /></i>
          <em>{formatNumber(row.value)}</em>
        </span>
      ))}
    </div>
  );
}

function VerticalBars({ rows }: { rows: Array<{ label: string; value: number }> }) {
  const max = Math.max(1, ...rows.map((row) => row.value));
  return (
    <div className="vbars">
      {rows.map((row) => (
        <span key={row.label}>
          <i style={{ height: `${Math.max(12, (row.value / max) * 100)}%` }} />
          <strong>{formatNumber(row.value)}</strong>
          <em>{row.label}</em>
        </span>
      ))}
    </div>
  );
}

function Metric({ label, value, tone }: { label: string; value: string | number; tone?: "danger" | "warn" }) {
  return (
    <div className={`metric ${tone ?? ""}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function getTopCounts(values: string[], limit: number) {
  const counts = values.reduce<Record<string, number>>((acc, value) => {
    acc[value] = (acc[value] ?? 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts)
    .map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

function getStorageBands(dams: Dam[]) {
  const bands = [
    { label: "0-10", min: 0, max: 10, value: 0 },
    { label: "10-100", min: 10, max: 100, value: 0 },
    { label: "100-500", min: 100, max: 500, value: 0 },
    { label: "500-1000", min: 500, max: 1000, value: 0 },
    { label: ">1000", min: 1000, max: Infinity, value: 0 }
  ];
  dams.forEach((dam) => {
    const storage = numberValue(dam.reservoir?.live_storage_mcm);
    const band = bands.find((item) => storage >= item.min && storage < item.max);
    if (band) band.value += 1;
  });
  return bands.map(({ label, value }) => ({ label, value }));
}

function numberValue(value: unknown) {
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return "-";
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: value < 10 ? 2 : 0 }).format(value);
}

function formatDecimal(value: number) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 3 }).format(value);
}

function titleCase(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function wait(milliseconds: number) {
  return new Promise((resolve) => window.setTimeout(resolve, milliseconds));
}

function normalizeSummaryName(value: string) {
  return value
    .toLowerCase()
    .replace(/\(ut\)|ut|\*/g, "")
    .replace(/&/g, "and")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function Field({
  label,
  name,
  value,
  required,
  onChange
}: {
  label: string;
  name: keyof typeof createDefaults;
  value: string;
  required?: boolean;
  onChange: Dispatch<SetStateAction<typeof createDefaults>>;
}) {
  return (
    <label>
      <span>{label}{required ? " *" : ""}</span>
      <input value={value} onChange={(event) => onChange((current) => ({ ...current, [name]: event.target.value }))} />
    </label>
  );
}

function emptyToNull(value: string) {
  return value.trim() ? value.trim() : null;
}

function numberOrNull(value: string) {
  return value.trim() ? Number(value) : null;
}

function numberOrDefault(value: string, fallback: number) {
  return value.trim() ? Number(value) : fallback;
}
