"use client";

import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  Database,
  Download,
  Droplets,
  FileSearch,
  Gauge,
  Search,
  ShieldCheck,
  Lock,
  Upload,
  Waves
} from "lucide-react";
import seed from "../../data/floodSeason2026.json";

type RiverStation = {
  river_name: string;
  gauge_station: string;
  district: string;
  danger_or_max_water_level_m: number | null;
};

type Reservoir = {
  reservoir_name: string;
  district: string;
  lsl_m: number | null;
  frl_m: number | null;
  live_capacity_frl_mcm: number | null;
  total_no_of_gates: number | null;
};

type RiverObservation = RiverStation & {
  observed_at: string;
  water_level_m: number | null;
};

type ReservoirObservation = {
  reservoir_name: string;
  district: string;
  lsl_m: number | null;
  frl_m: number | null;
  live_capacity_frl_mcm: number | null;
  observed_at: string;
  water_level_m: number | null;
  current_live_capacity_mcm: number | null;
  filling_percent: number | null;
  rainfall_daily_mm: number | null;
  rainfall_total_mm: number | null;
};

type GateObservation = {
  reservoir_name: string;
  district: string;
  total_no_of_gates: number | null;
  gate_opened_count: number | null;
  opening_m: number | null;
  gate_opening_date: string | null;
  gate_opening_time: string | null;
  discharge_cumecs: number | null;
  discharge_cusec: number | null;
};

type FloodSeed = {
  report: {
    report_date: string;
    report_time: string;
    source_filename: string;
    extraction_method: string;
  };
  riverStations: RiverStation[];
  reservoirs: Reservoir[];
  riverObservations: RiverObservation[];
  reservoirObservations: ReservoirObservation[];
  gateObservations: GateObservation[];
};

const data = seed as FloodSeed;
const ROLE_STORAGE_KEY = "dam-registry-role";

export default function FloodSeason2026Page() {
  const [query, setQuery] = useState("");
  const [district, setDistrict] = useState("");
  const [view, setView] = useState<"reservoirs" | "rivers" | "gates">("reservoirs");
  const [role, setRole] = useState("viewer");

  useEffect(() => {
    setRole(window.localStorage.getItem(ROLE_STORAGE_KEY) ?? "viewer");
  }, []);

  const latestReservoirs = useMemo(() => latestBy(data.reservoirObservations, "reservoir_name"), []);
  const latestRivers = useMemo(() => latestBy(data.riverObservations, "gauge_station"), []);
  const openGates = useMemo(
    () => data.gateObservations.filter((row) => Number(row.gate_opened_count ?? 0) > 0),
    []
  );
  const districts = useMemo(
    () =>
      Array.from(new Set([...data.reservoirs.map((row) => row.district), ...data.riverStations.map((row) => row.district)]))
        .filter(Boolean)
        .sort(),
    []
  );

  const visibleReservoirs = useMemo(() => {
    return latestReservoirs
      .filter((row) => !district || row.district === district)
      .filter((row) => textMatch(query, [row.reservoir_name, row.district]))
      .sort((a, b) => Number(b.filling_percent ?? 0) - Number(a.filling_percent ?? 0));
  }, [district, latestReservoirs, query]);

  const visibleRivers = useMemo(() => {
    return latestRivers
      .filter((row) => !district || row.district === district)
      .filter((row) => textMatch(query, [row.river_name, row.gauge_station, row.district]))
      .sort((a, b) => a.river_name.localeCompare(b.river_name));
  }, [district, latestRivers, query]);

  const visibleGates = useMemo(() => {
    return data.gateObservations
      .filter((row) => !district || row.district === district)
      .filter((row) => textMatch(query, [row.reservoir_name, row.district]))
      .sort((a, b) => Number(b.gate_opened_count ?? 0) - Number(a.gate_opened_count ?? 0));
  }, [district, query]);

  const avgFilling = average(latestReservoirs.map((row) => row.filling_percent));
  const maxFilling = Math.max(...latestReservoirs.map((row) => Number(row.filling_percent ?? 0)));
  const dailyRainfall = sum(latestReservoirs.map((row) => row.rainfall_daily_mm));
  const totalLiveStorage = sum(latestReservoirs.map((row) => row.current_live_capacity_mcm));
  const highestReservoirs = visibleReservoirs.slice(0, 12);
  const canUpload = role === "admin";

  return (
    <main className="flood-season-page">
      <header className="flood-season-topbar">
        <a href="/" className="mpwrd-back">
          <ArrowLeft size={17} /> Registry
        </a>
        <div>
          <strong>Flood Season 2026 Dashboard</strong>
          <span>WRD Govt MP PDF capture and operational review</span>
        </div>
        <a className="flood-season-action" href="/mpwrd">
          <Database size={16} /> MPWRD Registry
        </a>
      </header>

      <section className="flood-season-hero">
        <div>
          <h1>Reservoir, river, rainfall, and gate operations from daily WRD PDF reports</h1>
          <p>
            The dashboard separates master assets from time-stamped observations, so repeated PDF readings become clean
            historical records while the current operating view remains one row per river gauge or reservoir.
          </p>
          <div className="flood-season-flow">
            <FlowStep icon={<Upload size={18} />} title="Upload PDF" detail="08, 12, 16, 20 hr reports" />
            <FlowStep icon={<FileSearch size={18} />} title="Extract Tables" detail="Text first, OCR fallback" />
            <FlowStep icon={<ShieldCheck size={18} />} title="Review Data" detail="Validate assets and readings" />
            <FlowStep icon={<Database size={18} />} title="Publish" detail="Dam registry dashboard" />
          </div>
        </div>
        <aside className="flood-season-report-card">
          <span>Current report</span>
          <strong>{formatDate(data.report.report_date)} at {formatTime(data.report.report_time)}</strong>
          <small>{data.report.source_filename}</small>
          <div>
            <i>{data.report.extraction_method}</i>
            <i>{data.reservoirObservations.length + data.riverObservations.length + data.gateObservations.length} rows</i>
          </div>
        </aside>
      </section>

      <section className="flood-season-kpis">
        <Kpi icon={<Waves size={20} />} label="River gauges" value={data.riverStations.length} />
        <Kpi icon={<Droplets size={20} />} label="Reservoirs" value={data.reservoirs.length} />
        <Kpi icon={<Gauge size={20} />} label="Average filling" value={`${Math.round(avgFilling)}%`} />
        <Kpi icon={<BarChart3 size={20} />} label="Max filling" value={`${Math.round(maxFilling)}%`} />
        <Kpi icon={<Activity size={20} />} label="Open gate sites" value={openGates.length} tone={openGates.length ? "amber" : "green"} />
        <Kpi icon={<AlertTriangle size={20} />} label="Daily rainfall" value={`${formatNumber(dailyRainfall)} mm`} />
      </section>

      <section className="flood-season-command">
        <label>
          <Search size={17} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search reservoir, river, gauge, district..." />
        </label>
        <select value={district} onChange={(event) => setDistrict(event.target.value)}>
          <option value="">All districts</option>
          {districts.map((item) => (
            <option key={item} value={item}>{item}</option>
          ))}
        </select>
        <div className="flood-season-tabs" role="tablist" aria-label="Flood dashboard views">
          <button className={view === "reservoirs" ? "active" : ""} onClick={() => setView("reservoirs")}>Reservoirs</button>
          <button className={view === "rivers" ? "active" : ""} onClick={() => setView("rivers")}>Rivers</button>
          <button className={view === "gates" ? "active" : ""} onClick={() => setView("gates")}>Gates</button>
        </div>
        <button type="button" className="flood-season-action muted"><Download size={16} /> Export CSV</button>
      </section>

      <section className={`flood-season-admin ${canUpload ? "enabled" : "locked"}`}>
        <div>
          <span>{canUpload ? <Upload size={20} /> : <Lock size={20} />}</span>
          <div>
            <strong>{canUpload ? "Administrator PDF import console" : "Administrator access required for PDF upload"}</strong>
            <p>
              {canUpload
                ? "Upload WRD PDF reports here after backend import API wiring. Parsed rows will enter review before publishing to the Dam Registry dashboard."
                : "Viewer, engineer, and inspector roles can review captured flood-season data, but only an administrator can upload or publish new WRD PDF reports."}
            </p>
          </div>
        </div>
        <label className={!canUpload ? "disabled" : ""}>
          <Upload size={17} />
          <input type="file" accept="application/pdf" disabled={!canUpload} />
          <span>Select WRD PDF</span>
        </label>
      </section>

      <section className="flood-season-grid">
        <article className="flood-season-panel chart-panel">
          <header>
            <div>
              <strong>Top reservoir filling levels</strong>
              <span>Latest snapshot, one row per reservoir</span>
            </div>
            <strong>{formatNumber(totalLiveStorage)} MCM</strong>
          </header>
          <div className="flood-season-bars">
            {highestReservoirs.map((row) => (
              <div key={`${row.reservoir_name}-${row.district}`}>
                <span>{row.reservoir_name}</span>
                <i><b style={{ width: `${Math.min(100, Number(row.filling_percent ?? 0))}%` }} /></i>
                <strong>{formatNumber(row.filling_percent)}%</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="flood-season-panel status-panel">
          <header>
            <div>
              <strong>Import health</strong>
              <span>Current extraction audit summary</span>
            </div>
            <ShieldCheck size={20} />
          </header>
          <dl>
            <div><dt>Master river gauges</dt><dd>{data.riverStations.length}</dd></div>
            <div><dt>River observation rows</dt><dd>{data.riverObservations.length}</dd></div>
            <div><dt>Master reservoirs</dt><dd>{data.reservoirs.length}</dd></div>
            <div><dt>Reservoir observation rows</dt><dd>{data.reservoirObservations.length}</dd></div>
            <div><dt>Gate position rows</dt><dd>{data.gateObservations.length}</dd></div>
          </dl>
          <p>
            Repeated asset names in observation history are expected because each PDF row contains multiple time columns.
          </p>
        </article>
      </section>

      <section className="flood-season-panel table-panel">
        <header>
          <div>
            <strong>{view === "reservoirs" ? "Reservoir latest snapshot" : view === "rivers" ? "River gauge latest snapshot" : "Reservoir gate positions"}</strong>
            <span>
              {view === "reservoirs" ? visibleReservoirs.length : view === "rivers" ? visibleRivers.length : visibleGates.length} visible records
            </span>
          </div>
        </header>
        {view === "reservoirs" && <ReservoirTable rows={visibleReservoirs} />}
        {view === "rivers" && <RiverTable rows={visibleRivers} />}
        {view === "gates" && <GateTable rows={visibleGates} />}
      </section>
    </main>
  );
}

function FlowStep({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <div>
      <span>{icon}</span>
      <strong>{title}</strong>
      <small>{detail}</small>
    </div>
  );
}

function Kpi({ icon, label, value, tone = "blue" }: { icon: ReactNode; label: string; value: string | number; tone?: string }) {
  return (
    <article className={`flood-season-kpi ${tone}`}>
      <span>{icon}</span>
      <div>
        <strong>{value}</strong>
        <small>{label}</small>
      </div>
    </article>
  );
}

function ReservoirTable({ rows }: { rows: ReservoirObservation[] }) {
  return (
    <div className="flood-season-table-wrap">
      <table className="flood-season-table">
        <thead>
          <tr>
            <th>Reservoir</th>
            <th>District</th>
            <th>Level</th>
            <th>FRL Gap</th>
            <th>Live Storage</th>
            <th>Filling</th>
            <th>Rainfall</th>
            <th>Observed</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const frlGap = row.frl_m !== null && row.water_level_m !== null ? row.frl_m - row.water_level_m : null;
            return (
              <tr key={`${row.reservoir_name}-${row.district}`}>
                <td><strong>{row.reservoir_name}</strong><span>LSL {formatNumber(row.lsl_m)} m</span></td>
                <td>{row.district}</td>
                <td>{formatNumber(row.water_level_m)} m</td>
                <td>{formatNumber(frlGap)} m</td>
                <td>{formatNumber(row.current_live_capacity_mcm)} MCM</td>
                <td><Progress value={row.filling_percent} /></td>
                <td>{formatNumber(row.rainfall_daily_mm)} mm</td>
                <td>{formatDateTime(row.observed_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function RiverTable({ rows }: { rows: RiverObservation[] }) {
  return (
    <div className="flood-season-table-wrap">
      <table className="flood-season-table">
        <thead>
          <tr>
            <th>River</th>
            <th>Gauge station</th>
            <th>District</th>
            <th>Water level</th>
            <th>Max level</th>
            <th>Margin</th>
            <th>Observed</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const margin =
              row.danger_or_max_water_level_m !== null && row.water_level_m !== null
                ? row.danger_or_max_water_level_m - row.water_level_m
                : null;
            return (
              <tr key={`${row.river_name}-${row.gauge_station}`}>
                <td><strong>{row.river_name}</strong></td>
                <td>{row.gauge_station}</td>
                <td>{row.district}</td>
                <td>{formatNumber(row.water_level_m)} m</td>
                <td>{formatNumber(row.danger_or_max_water_level_m)} m</td>
                <td>{formatNumber(margin)} m</td>
                <td>{formatDateTime(row.observed_at)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function GateTable({ rows }: { rows: GateObservation[] }) {
  return (
    <div className="flood-season-table-wrap">
      <table className="flood-season-table">
        <thead>
          <tr>
            <th>Reservoir</th>
            <th>District</th>
            <th>Total gates</th>
            <th>Open gates</th>
            <th>Opening</th>
            <th>Discharge</th>
            <th>Gate opening</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.reservoir_name}-${row.district}`}>
              <td><strong>{row.reservoir_name}</strong></td>
              <td>{row.district}</td>
              <td>{formatNumber(row.total_no_of_gates)}</td>
              <td><span className={Number(row.gate_opened_count ?? 0) > 0 ? "gate-open" : "gate-closed"}>{formatNumber(row.gate_opened_count)}</span></td>
              <td>{formatNumber(row.opening_m)} m</td>
              <td>{formatNumber(row.discharge_cumecs)} cumecs</td>
              <td>{row.gate_opening_date ? `${formatDate(row.gate_opening_date)} ${row.gate_opening_time ?? ""}` : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Progress({ value }: { value: number | null }) {
  const safe = Math.max(0, Math.min(100, Number(value ?? 0)));
  return (
    <div className="flood-season-progress">
      <strong>{formatNumber(value)}%</strong>
      <i><span style={{ width: `${safe}%` }} /></i>
    </div>
  );
}

function latestBy<T extends { observed_at: string }>(rows: T[], key: keyof T) {
  const map = new Map<string, T>();
  rows
    .slice()
    .sort((a, b) => new Date(a.observed_at).getTime() - new Date(b.observed_at).getTime())
    .forEach((row) => map.set(String(row[key]), row));
  return Array.from(map.values());
}

function textMatch(query: string, values: Array<string | null | undefined>) {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  return values.filter(Boolean).some((value) => String(value).toLowerCase().includes(needle));
}

function sum(values: Array<number | null | undefined>) {
  return values.reduce<number>((total, value) => total + Number(value ?? 0), 0);
}

function average(values: Array<number | null | undefined>) {
  const valid = values.map((value) => Number(value)).filter((value) => Number.isFinite(value));
  return valid.length ? valid.reduce<number>((total, value) => total + value, 0) / valid.length : 0;
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
}

function formatDate(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}

function formatTime(value: string | null | undefined) {
  if (!value) return "-";
  const [hour, minute] = value.split(":");
  return new Intl.DateTimeFormat("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true }).format(
    new Date(2026, 0, 1, Number(hour), Number(minute))
  );
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true
  }).format(new Date(value));
}
