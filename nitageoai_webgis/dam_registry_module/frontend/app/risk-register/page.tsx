"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  Filter,
  Gauge,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Wrench
} from "lucide-react";
import { RiskClass, RiskRegisterItem, RiskRegisterList, RiskRegisterSummary, apiFetch, login } from "../../lib/api";

const TOKEN_STORAGE_KEY = "dam-registry-token";
const ROLE_STORAGE_KEY = "dam-registry-role";
const levels: Array<RiskClass | ""> = ["", "critical", "high", "moderate", "low"];
const statuses = ["", "open", "monitoring", "mitigating", "accepted", "closed"];
const levelColors: Record<string, string> = {
  critical: "#fb7185",
  high: "#f97316",
  moderate: "#facc15",
  low: "#22c55e"
};

const emptySummary: RiskRegisterSummary = {
  total: 0,
  critical: 0,
  high: 0,
  overdue: 0,
  due_soon: 0,
  open: 0,
  mitigating: 0,
  compliance_flags: 0,
  ai_flags: 0,
  maintenance_required: 0,
  by_level: [],
  by_category: [],
  by_state: []
};

export default function RiskRegisterPage() {
  const [token, setToken] = useState<string | null>(null);
  const [role, setRole] = useState("viewer");
  const [risks, setRisks] = useState<RiskRegisterItem[]>([]);
  const [summary, setSummary] = useState<RiskRegisterSummary>(emptySummary);
  const [selected, setSelected] = useState<RiskRegisterItem | null>(null);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState("");
  const [status, setStatus] = useState("");
  const [message, setMessage] = useState("Risk Register is ready for risk-engine sync");
  const [loading, setLoading] = useState(false);

  const categories = useMemo(() => summary.by_category.map((item) => item.key), [summary.by_category]);
  const topStates = useMemo(() => summary.by_state.slice(0, 6), [summary.by_state]);

  useEffect(() => {
    const storedToken = readStoredValue(TOKEN_STORAGE_KEY);
    const storedRole = readStoredValue(ROLE_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
      setRole(storedRole || "viewer");
      void loadRisks(storedToken);
    }
  }, []);

  useEffect(() => {
    if (token) void loadRisks(token);
  }, [query, level, status]);

  async function handleLogin() {
    const session = await login("admin@nita.ai", "nita-admin");
    setToken(session.access_token);
    setRole(session.user.role);
    writeStoredValue(TOKEN_STORAGE_KEY, session.access_token);
    writeStoredValue(ROLE_STORAGE_KEY, session.user.role);
    await loadRisks(session.access_token);
    setMessage(`Signed in as ${session.user.full_name}`);
  }

  async function loadRisks(authToken = token) {
    if (!authToken) return;
    try {
      const params = new URLSearchParams({ limit: "80" });
      if (query.trim()) params.set("q", query.trim());
      if (level) params.set("level", level);
      if (status) params.set("status", status);
      const data = await apiFetch<RiskRegisterList>(`/api/risk-register?${params.toString()}`, authToken);
      setRisks(data.items);
      setSummary(data.summary);
      setSelected((current) => current ? data.items.find((item) => item.risk_id === current.risk_id) ?? data.items[0] ?? null : data.items[0] ?? null);
      setMessage(`${data.total} risks loaded from the active register`);
    } catch (error) {
      setToken(null);
      setRole("viewer");
      removeStoredValue(TOKEN_STORAGE_KEY);
      removeStoredValue(ROLE_STORAGE_KEY);
      setMessage(error instanceof Error && error.message.includes("credentials") ? "Session expired. Use demo login to continue." : "Unable to load Risk Register.");
    }
  }

  async function syncRiskEngine() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await apiFetch<RiskRegisterList>("/api/risk-register/sync", token, { method: "POST", body: JSON.stringify({}) });
      setRisks(data.items);
      setSummary(data.summary);
      setSelected(data.items[0] ?? null);
      setMessage("Risk engine sync complete: dam baseline and field defects refreshed");
    } finally {
      setLoading(false);
    }
  }

  async function updateSelected(statusValue: "monitoring" | "mitigating" | "accepted" | "closed") {
    if (!token || !selected) return;
    const updated = await apiFetch<RiskRegisterItem>(`/api/risk-register/${selected.risk_id}`, token, {
      method: "PATCH",
      body: JSON.stringify({
        status: statusValue,
        mitigation_plan: statusValue === "mitigating" ? "Mitigation owner assigned. Track corrective action with maintenance module." : selected.mitigation_plan,
        review_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      })
    });
    setSelected(updated);
    await loadRisks(token);
  }

  return (
    <main className="risk-page">
      <header className="risk-topbar">
        <Link href="/" className="risk-back"><ArrowLeft size={18} /> Registry dashboard</Link>
        <div>
          <span>Activated module</span>
          <h1>Risk Register Module</h1>
          <p>Portfolio-level risk triage connected to dam safety score, inspection due dates, geo-tagged defects, AI review flags, compliance, and maintenance actions.</p>
        </div>
        <div className="risk-actions">
          <button onClick={token ? syncRiskEngine : handleLogin} className="risk-primary">
            {token ? <RefreshCw size={17} /> : <ShieldCheck size={17} />}
            {token ? (loading ? "Syncing..." : "Sync Risk Engine") : "Demo login"}
          </button>
        </div>
      </header>

      <section className="risk-commandbar">
        <label className="risk-search"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search dam, risk code, trigger..." /></label>
        <label><Filter size={16} /><select value={level} onChange={(event) => setLevel(event.target.value)}>{levels.map((item) => <option key={item} value={item}>{item || "All levels"}</option>)}</select></label>
        <label><ShieldAlert size={16} /><select value={status} onChange={(event) => setStatus(event.target.value)}>{statuses.map((item) => <option key={item} value={item}>{item ? item.replace("_", " ") : "All status"}</option>)}</select></label>
        <button onClick={() => loadRisks()}><RefreshCw size={16} /> Refresh</button>
      </section>

      <section className="risk-metrics">
        <Metric icon={<ClipboardList size={20} />} label="Active risks" value={summary.total} tone="#14b8a6" />
        <Metric icon={<AlertTriangle size={20} />} label="Critical / high" value={summary.critical + summary.high} tone="#fb7185" />
        <Metric icon={<Gauge size={20} />} label="Overdue" value={summary.overdue} tone="#f97316" />
        <Metric icon={<Sparkles size={20} />} label="AI flagged" value={summary.ai_flags} tone="#8b5cf6" />
        <Metric icon={<Wrench size={20} />} label="Maintenance" value={summary.maintenance_required} tone="#0ea5e9" />
      </section>

      <div className="risk-shell">
        <section className="risk-panel risk-register-panel">
          <div className="risk-panel-heading">
            <div><span>{message}</span><h2>Register</h2></div>
            <strong>{role}</strong>
          </div>
          <div className="risk-table-wrap">
            <table className="risk-table">
              <thead>
                <tr>
                  <th>Risk</th>
                  <th>Dam</th>
                  <th>Level</th>
                  <th>Score</th>
                  <th>Status</th>
                  <th>Due</th>
                  <th>Flags</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk) => (
                  <tr key={risk.risk_id} onClick={() => setSelected(risk)} className={selected?.risk_id === risk.risk_id ? "selected" : ""}>
                    <td><strong>{risk.risk_title}</strong><span>{risk.risk_code || risk.risk_category}</span></td>
                    <td><strong>{risk.dam_name}</strong><span>{risk.state} / {risk.district || "District pending"}</span></td>
                    <td><span className={`risk-level ${risk.risk_level}`}>{risk.risk_level}</span></td>
                    <td><strong>{risk.risk_score}</strong><span>L{risk.likelihood} x C{risk.consequence}</span></td>
                    <td><span className={`risk-status ${risk.status}`}>{risk.status}</span></td>
                    <td>{risk.due_date ? formatDate(risk.due_date) : "Not set"}</td>
                    <td><RiskFlags risk={risk} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <aside className="risk-side">
          <section className="risk-panel risk-detail-panel">
            {selected ? (
              <>
                <header>
                  <div><span>Selected risk</span><h2>{selected.dam_name}</h2></div>
                  <span className={`risk-level ${selected.risk_level}`}>{selected.risk_level}</span>
                </header>
                <h3>{selected.risk_title}</h3>
                <p>{selected.trigger_event || "No trigger narrative recorded."}</p>
                <div className="risk-detail-grid">
                  <span>Category<strong>{selected.risk_category.replaceAll("_", " ")}</strong></span>
                  <span>Source<strong>{selected.risk_source.replaceAll("_", " ")}</strong></span>
                  <span>Priority<strong>{selected.priority}</strong></span>
                  <span>Owner<strong>{selected.owner_role || "Unassigned"}</strong></span>
                </div>
                <div className="risk-plan">
                  <strong>Mitigation plan</strong>
                  <p>{selected.mitigation_plan || "Assign mitigation plan from dam safety review."}</p>
                </div>
                <div className="risk-workflow">
                  <button onClick={() => updateSelected("monitoring")}><Gauge size={15} /> Monitor</button>
                  <button onClick={() => updateSelected("mitigating")}><Wrench size={15} /> Mitigate</button>
                  <button onClick={() => updateSelected("closed")}><CheckCircle2 size={15} /> Close</button>
                </div>
              </>
            ) : (
              <div className="risk-empty"><ShieldAlert size={34} /><strong>No risks loaded</strong><span>Run the risk engine sync to populate the register.</span></div>
            )}
          </section>

          <section className="risk-panel risk-chart-panel">
            <header><span>Portfolio analytics</span><h2>Risk distribution</h2></header>
            <div className="risk-level-bars">
              {summary.by_level.map((item) => <Bar key={item.key} label={item.key} value={item.count} total={summary.total} color={levelColors[item.key] || "#94a3b8"} />)}
            </div>
            <div className="risk-mini-list">
              <strong>Top categories</strong>
              {categories.map((category) => <span key={category}>{category.replaceAll("_", " ")}</span>)}
            </div>
            <div className="risk-mini-list">
              <strong>Top states</strong>
              {topStates.map((state) => <span key={state.key}>{state.key}<i>{state.count}</i></span>)}
            </div>
          </section>
        </aside>
      </div>
    </main>
  );
}

function Metric({ icon, label, value, tone }: { icon: ReactNode; label: string; value: number; tone: string }) {
  return <article className="risk-metric" style={{ "--tone": tone } as CSSProperties}>{icon}<span>{label}</span><strong>{value.toLocaleString()}</strong></article>;
}

function Bar({ label, value, total, color }: { label: string; value: number; total: number; color: string }) {
  const width = total ? Math.max(6, Math.round((value / total) * 100)) : 0;
  return <div className="risk-bar"><span>{label}</span><i><b style={{ width: `${width}%`, background: color }} /></i><strong>{value}</strong></div>;
}

function RiskFlags({ risk }: { risk: RiskRegisterItem }) {
  return (
    <span className="risk-flags">
      {risk.compliance_flag ? <i>Compliance</i> : null}
      {risk.ai_flag ? <i>AI</i> : null}
      {risk.maintenance_required ? <i>Maintenance</i> : null}
    </span>
  );
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

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-IN", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(value));
}
