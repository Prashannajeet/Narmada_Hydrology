"use client";

import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import {
  Activity,
  ArrowLeft,
  BarChart3,
  Database,
  Droplets,
  ExternalLink,
  Gauge,
  GitBranch,
  Search,
  Server,
  ShieldCheck,
  Waves
} from "lucide-react";
import { MpwrdOverview, MpwrdReading, apiFetch } from "../../lib/api";

export default function MpwrdPage() {
  const [data, setData] = useState<MpwrdOverview | null>(null);
  const [message, setMessage] = useState("Loading MPWRD data");
  const [query, setQuery] = useState("");
  const [activeBasin, setActiveBasin] = useState("");

  useEffect(() => {
    void loadMpwrd();
  }, []);

  async function loadMpwrd() {
    try {
      const overview = await apiFetch<MpwrdOverview>("/api/mpwrd", null);
      setData(overview);
      setMessage(overview.summary ? `${overview.summary.total_readings} MPWRD readings loaded` : "No MPWRD data found");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Could not load MPWRD data");
    }
  }

  const filteredReadings = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return (data?.readings ?? []).filter((reading) => {
      const basinMatch = !activeBasin || reading.basin_office === activeBasin;
      const textMatch =
        !needle ||
        [reading.reservoir_name, reading.reservoir_code, reading.dam_id, reading.district, reading.basin_office]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(needle));
      return basinMatch && textMatch;
    });
  }, [activeBasin, data?.readings, query]);

  const selectedBasin = data?.basins.find((basin) => basin.basin_office === activeBasin) ?? data?.basins[0] ?? null;
  const storagePercent = data?.summary?.total_live_capacity_mcm
    ? Math.round((data.summary.current_live_storage_mcm / data.summary.total_live_capacity_mcm) * 100)
    : 0;
  const stalePercent = data?.summary?.total_readings ? Math.round((data.summary.stale_readings / data.summary.total_readings) * 100) : 0;

  return (
    <main className="mpwrd-page">
      <header className="mpwrd-topbar">
        <a href="/" className="mpwrd-back"><ArrowLeft size={17} /> Registry</a>
        <div>
          <strong>MPWRD Reservoir Intelligence</strong>
          <span>{message}</span>
        </div>
        <button onClick={() => void loadMpwrd()}><Activity size={16} /> Refresh</button>
      </header>

      <section className="mpwrd-hero">
        <div className="mpwrd-hero-copy">
          <span className="mpwrd-source">Madhya Pradesh Water Resources Department</span>
          <h1>Live reservoir readings linked to the dam registry</h1>
          <p>
            MPWRD FCM rows are stored as dated readings, then connected to normalized dam and reservoir records through
            a generated `dam_id`. The view below shows that relationship from public source to database table.
          </p>
          <div className="mpwrd-flow" aria-label="MPWRD data relationship">
            <FlowNode icon={<ExternalLink size={18} />} title="MPWRD FCM" detail="Public source page" />
            <FlowNode icon={<Waves size={18} />} title="mpwrd_reservoir_levels" detail="Dated level readings" />
            <FlowNode icon={<Database size={18} />} title="dams / dam_reservoir" detail="Registry relation" />
          </div>
        </div>
        <div className="mpwrd-capacity">
          <div className="capacity-ring" style={{ "--value": `${storagePercent}%` } as CSSProperties}>
            <span>{storagePercent}%</span>
            <small>storage</small>
          </div>
          <dl>
            <div>
              <dt>Report date</dt>
              <dd>{formatDate(data?.summary?.report_date)}</dd>
            </div>
            <div>
              <dt>Current storage</dt>
              <dd>{formatNumber(data?.summary?.current_live_storage_mcm)} MCM</dd>
            </div>
            <div>
              <dt>Capacity at FRL</dt>
              <dd>{formatNumber(data?.summary?.total_live_capacity_mcm)} MCM</dd>
            </div>
          </dl>
        </div>
      </section>

      <section className="mpwrd-stats">
        <Stat icon={<Waves size={20} />} label="MPWRD readings" value={data?.summary?.total_readings ?? 0} />
        <Stat icon={<GitBranch size={20} />} label="Linked dam IDs" value={data?.summary?.linked_dams ?? 0} />
        <Stat icon={<Server size={20} />} label="Basin offices" value={data?.basins.length ?? 0} />
        <Stat icon={<Gauge size={20} />} label="Stale readings" value={`${stalePercent}%`} />
      </section>

      <section className="mpwrd-relation-grid">
        <article className="mpwrd-panel basin-panel">
          <header>
            <div>
              <strong>Basin relationship</strong>
              <span>Office grouping from MPWRD rows</span>
            </div>
            <BarChart3 size={20} />
          </header>
          <div className="basin-list">
            {(data?.basins ?? []).map((basin) => (
              <button
                key={basin.basin_office}
                className={basin.basin_office === activeBasin ? "active" : ""}
                onClick={() => setActiveBasin(basin.basin_office === activeBasin ? "" : basin.basin_office)}
              >
                <span>{basin.basin_office}</span>
                <strong>{basin.reservoir_count}</strong>
                <i style={{ width: `${Math.min(100, basin.avg_storage_percent ?? 0)}%` }} />
              </button>
            ))}
          </div>
        </article>

        <article className="mpwrd-panel basin-detail">
          <header>
            <div>
              <strong>{selectedBasin?.basin_office ?? "All basins"}</strong>
              <span>Storage summary</span>
            </div>
            <Droplets size={20} />
          </header>
          <div className="basin-metrics">
            <MiniMetric label="Reservoirs" value={selectedBasin?.reservoir_count ?? data?.summary?.total_readings ?? 0} />
            <MiniMetric label="Current MCM" value={formatNumber(selectedBasin?.current_storage_mcm ?? data?.summary?.current_live_storage_mcm)} />
            <MiniMetric label="FRL Capacity MCM" value={formatNumber(selectedBasin?.live_capacity_mcm ?? data?.summary?.total_live_capacity_mcm)} />
            <MiniMetric label="Avg storage" value={`${Math.round(selectedBasin?.avg_storage_percent ?? data?.summary?.avg_storage_percent ?? 0)}%`} />
          </div>
          <div className="relationship-card">
            <ShieldCheck size={22} />
            <div>
              <strong>Relation key</strong>
              <span>`mpwrd_reservoir_levels.dam_id` references `dams.dam_id`; reservoir facts update `dam_reservoir`.</span>
            </div>
          </div>
        </article>
      </section>

      <section className="mpwrd-panel readings-panel">
        <header>
          <div>
            <strong>Reservoir reading table</strong>
            <span>{filteredReadings.length} visible records</span>
          </div>
          <label className="mpwrd-search">
            <Search size={17} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search reservoir, code, dam ID, district..." />
          </label>
        </header>
        <div className="mpwrd-table-wrap">
          <table className="mpwrd-table">
            <thead>
              <tr>
                <th>MPWRD Code</th>
                <th>Registry Dam ID</th>
                <th>Reservoir</th>
                <th>District</th>
                <th>Level</th>
                <th>Storage</th>
                <th>Reading Date</th>
                <th>Relation</th>
              </tr>
            </thead>
            <tbody>
              {filteredReadings.map((reading) => <ReadingRow key={reading.dam_id} reading={reading} />)}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function FlowNode({ icon, title, detail }: { icon: ReactNode; title: string; detail: string }) {
  return (
    <div>
      <span>{icon}</span>
      <strong>{title}</strong>
      <small>{detail}</small>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value: string | number }) {
  return (
    <article>
      <span>{icon}</span>
      <div>
        <strong>{value}</strong>
        <small>{label}</small>
      </div>
    </article>
  );
}

function MiniMetric({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ReadingRow({ reading }: { reading: MpwrdReading }) {
  const percent = reading.this_year_live_storage_percent ?? 0;
  return (
    <tr>
      <td><code>{reading.reservoir_code}</code></td>
      <td><code>{reading.dam_id}</code></td>
      <td>
        <strong>{reading.reservoir_name}</strong>
        <span>{reading.basin_office}</span>
      </td>
      <td>{reading.district ?? "-"}</td>
      <td>{formatNumber(reading.this_year_level_m)} m</td>
      <td>
        <div className="storage-cell">
          <strong>{Math.round(percent)}%</strong>
          <i><span style={{ width: `${Math.min(100, percent)}%` }} /></i>
        </div>
      </td>
      <td>
        <strong>{formatDate(reading.this_year_level_observed_date)}</strong>
        {reading.this_year_is_stale ? <span className="stale">stale</span> : <span className="fresh">current</span>}
      </td>
      <td><span className="relation-pill">{`${reading.source_registry ?? "MPWRD"} -> dams`}</span></td>
    </tr>
  );
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 2 }).format(value);
}

function formatDate(value: string | null | undefined) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}
