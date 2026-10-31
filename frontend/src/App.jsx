
import { useEffect, useState } from "react";
import {
  Activity, AlertTriangle, ArrowDownRight, ArrowUpRight,
  Bell, ChevronDown, ChevronRight, CircleHelp, Clock3,
  Command, Database, Download, ExternalLink, FileSearch,
  Filter, Globe2, LayoutDashboard, Menu, Network,
  Search, Settings, ShieldAlert, ShieldCheck, Target,
  TrendingUp, X, Zap
} from "lucide-react";
import "./App.css";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, group: "MAIN" },
  { label: "IOC Search", icon: Search, group: "MAIN" },
  { label: "Campaign Explorer", icon: Target, group: "INTELLIGENCE" },
  { label: "New Threat Analysis", icon: ShieldAlert, group: "INTELLIGENCE" },
  { label: "Relationship Graph", icon: Network, group: "INTELLIGENCE" },
];

const campaigns = [
  { id: "CAMP-01", name: "SideCopy", iocs: 5, confidence: "High", color: "purple" },
  { id: "CAMP-02", name: "Patchwork", iocs: 4, confidence: "Medium", color: "blue" },
  { id: "CAMP-03", name: "Transparent Tribe", iocs: 5, confidence: "High", color: "green" },
  { id: "CAMP-04", name: "DoNot Team", iocs: 4, confidence: "Low", color: "orange" },
  { id: "CAMP-05", name: "Unattributed", iocs: 5, confidence: "Unconfirmed", color: "gray" },
  { id: "CAMP-06", name: "Bitter APT", iocs: 5, confidence: "Medium", color: "blue" },
  { id: "CAMP-07", name: "Confucius", iocs: 3, confidence: "Medium", color: "purple" },
  { id: "CAMP-08", name: "Mustang Panda", iocs: 3, confidence: "Medium", color: "green" },
];

const sampleIOCs = [
  { value: "secure-mod-gov.in.example", type: "Domain", verdict: "Suspicious", campaign: "DISC-01", confidence: "High" },
  { value: "random-verify-8472.test", type: "Domain", verdict: "Suspicious", campaign: "No established match", confidence: "Low" },
  { value: "example-login-check.com", type: "Domain", verdict: "Needs review", campaign: "Unassigned", confidence: "Low" },
];

function Badge({ children, tone = "gray" }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

function StatCard({ label, value, note, icon: Icon, tone, trend }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className={`stat-icon icon-${tone}`}><Icon size={19} /></span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-bottom">
        <span className={`stat-trend ${trend === "up" ? "trend-up" : ""}`}>
          {trend === "up" ? <ArrowUpRight size={14} /> : null}{note}
        </span>
      </div>
    </article>
  );
}

function Overview({ setPage }) {
  const bars = [28, 44, 35, 56, 40, 68, 48, 62, 38, 75, 51, 66, 45, 82, 57, 71, 48, 63, 39, 88, 55, 74, 60, 94];
  return (
    <>
      <div className="page-heading">
        <div><div className="eyebrow">INTELLIGENCE OVERVIEW</div><h1>Dashboard</h1><p>Monitor indicators, campaigns and potential threats.</p></div>
        <button className="button button-secondary" onClick={() => window.print()}><Download size={16} /> Export view</button>
      </div>
      <div className="stats-grid">
        <StatCard label="IOC Records" value="625" note="Dataset records" icon={Database} tone="blue" />
        <StatCard label="Campaign Groups" value="8" note="Curated campaign labels" icon={Target} tone="purple" />
        <StatCard label="Unclustered IOCs" value="34" note="Require investigation" icon={AlertTriangle} tone="orange" />
        <StatCard label="System Status" value="Ready" note="Frontend demonstration" icon={Activity} tone="green" />
      </div>
      <div className="dashboard-grid">
        <section className="panel activity-panel">
          <div className="panel-heading"><div><h2>Threat intelligence activity</h2><p>Illustrative activity distribution</p></div><button className="icon-button" title="Activity information"><CircleHelp size={17} /></button></div>
          <div className="chart-legend"><span><i className="legend-dot blue-dot" /> IOC activity</span><span><i className="legend-dot purple-dot" /> Campaign investigations</span></div>
          <div className="chart">
            <div className="chart-y"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div>
            <div className="chart-plot">
              {[100, 75, 50, 25, 0].map(v => <div className="chart-gridline" key={v}><span /></div>)}
              <div className="chart-bars">{bars.map((h, i) => <div key={i} className="bar-group"><div className="bar bar-blue" style={{ height: `${h}%` }} /><div className="bar bar-purple" style={{ height: `${Math.max(8, h * (i % 3 === 0 ? 0.38 : 0.56))}%` }} /></div>)}</div>
            </div>
            <div className="chart-x"><span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span></div>
          </div>
          <p className="chart-footnote">Illustrative chart only. Live event history is not connected.</p>
        </section>
        <section className="panel distribution-panel">
          <div className="panel-heading"><div><h2>Campaign distribution</h2><p>Curated dataset groups</p></div><button className="text-link" onClick={() => setPage("Campaign Explorer")}>View all <ChevronRight size={14} /></button></div>
          <div className="distribution-total"><strong>8</strong><span>campaign labels</span></div>
          <div className="distribution-list">
            {[
              ["SideCopy", 5, "purple"], ["Transparent Tribe", 5, "blue"],
              ["Patchwork", 4, "green"], ["DoNot Team", 4, "orange"],
              ["Other groups", 10, "gray"]
            ].map(([name, n, tone]) => <div className="distribution-row" key={name}><div className="distribution-name"><span className={`legend-dot ${tone}-dot`} />{name}<span>{n}</span></div><div className="progress-track"><div className={`progress-fill fill-${tone}`} style={{ width: `${n / 10 * 100}%` }} /></div></div>)}
          </div>
          <p className="chart-footnote">Counts shown from the supplied project summary; verify against your current dataset.</p>
        </section>
      </div>
      <section className="panel recent-panel">
        <div className="panel-heading"><div><h2>Investigation queue</h2><p>Example records for interface testing</p></div><button className="text-link" onClick={() => setPage("IOC Search")}>Open IOC Search <ChevronRight size={14} /></button></div>
        <div className="table-wrap"><table><thead><tr><th>INDICATOR</th><th>TYPE</th><th>ASSESSMENT</th><th>CAMPAIGN</th><th>CONFIDENCE</th></tr></thead><tbody>{sampleIOCs.map((ioc) => <tr key={ioc.value}><td className="mono">{ioc.value}</td><td>{ioc.type}</td><td><Badge tone={ioc.verdict === "Suspicious" ? "red" : "orange"}>{ioc.verdict}</Badge></td><td>{ioc.campaign}</td><td><Badge tone={ioc.confidence === "High" ? "green" : "gray"}>{ioc.confidence}</Badge></td></tr>)}</tbody></table></div>
      </section>
    </>
  );
}
 
function IOCSearch() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();

    const domain = query.trim();
    if (!domain) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ domain }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Prediction request failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot reach the Python API. Make sure FastAPI is running on port 8000."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  const suspicious = result?.predicted_label === "suspicious";

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">INDICATOR INVESTIGATION</div>
          <h1>IOC Search</h1>
          <p>Submit a domain to your trained baseline classification model.</p>
        </div>
      </div>

      <section className="panel search-panel">
        <div className="search-hero-icon"><FileSearch size={26} /></div>
        <h2>Investigate a domain</h2>
        <p>This endpoint classifies domain strings; it does not verify live threat intelligence.</p>

        <form className="ioc-form" onSubmit={submit}>
          <Search size={18} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. suspicious-domain.example"
            required
            maxLength={253}
          />
          <button className="button button-primary" type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Domain"}
          </button>
        </form>

        <div className="search-hints">
          <span>Try a sample:</span>
          {["google.com", "myntra-secure-login.com"].map((domain) => (
            <button
              type="button"
              key={domain}
              onClick={() => setQuery(domain)}
            >
              {domain}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <section className="panel result-panel">
          <div className="notice">
            <AlertTriangle size={18} />
            <div>
              <strong>Request failed</strong>
              <p>{error}</p>
            </div>
          </div>
        </section>
      )}

      {result && (
        <section className="panel result-panel">
          <div className="panel-heading">
            <div>
              <h2>Model prediction</h2>
              <p className="mono">{result.domain}</p>
            </div>
            <Badge tone={suspicious ? "red" : "green"}>
              {result.predicted_label}
            </Badge>
          </div>

          <div className="notice">
            <AlertTriangle size={18} />
            <div>
              <strong>Baseline model output</strong>
              <p>{result.warning}</p>
            </div>
          </div>

          <div className="result-grid">
            <div>
              <span>Predicted label</span>
              <strong>{result.predicted_label}</strong>
            </div>
            <div>
              <span>Benign score</span>
              <strong>{result.model_scores?.benign !== undefined
                ? `${(result.model_scores.benign * 100).toFixed(2)}%`
                : "Unavailable"}</strong>
            </div>
            <div>
              <span>Suspicious score</span>
              <strong>{result.model_scores?.suspicious !== undefined
                ? `${(result.model_scores.suspicious * 100).toFixed(2)}%`
                : "Unavailable"}</strong>
            </div>
          </div>

          <p className="chart-footnote">
            Scores are model outputs, not calibrated probabilities or proof of malicious activity.
            Campaign matching and APT attribution have not been performed.
          </p>
        </section>
      )}
    </>
  );
}


function CampaignExplorer() {
  const [filter, setFilter] = useState("");
  const filtered = campaigns.filter(c => `${c.id} ${c.name} ${c.confidence}`.toLowerCase().includes(filter.toLowerCase()));
  return <>
    <div className="page-heading"><div><div className="eyebrow">THREAT CLUSTERING</div><h1>Campaign Explorer</h1><p>Explore curated campaign groups and their current dataset labels.</p></div><button className="button button-secondary" onClick={() => setFilter("")}><Filter size={16} /> Reset filter</button></div>
    <div className="stats-grid compact-stats"><StatCard label="Campaign labels" value="8" note="Curated groups" icon={Target} tone="purple" /><StatCard label="Unclustered records" value="34" note="Unknown cluster" icon={Network} tone="orange" /><StatCard label="Attribution" value="Evidence-based" note="Analyst review needed" icon={ShieldCheck} tone="green" /></div>
    <section className="panel"><div className="panel-heading"><div><h2>Campaign catalogue</h2><p>Search by campaign ID, label or confidence</p></div><span className="record-count">{filtered.length} groups</span></div><div className="filter-input"><Search size={17} /><input value={filter} onChange={e => setFilter(e.target.value)} placeholder="Filter campaigns..." /></div><div className="campaign-grid">{filtered.map(c => <article className="campaign-card" key={c.id}><div className="campaign-card-top"><span className={`campaign-mark ${c.color}`}><Target size={19} /></span><Badge tone={c.confidence === "High" ? "green" : c.confidence === "Medium" ? "blue" : "gray"}>{c.confidence}</Badge></div><span className="campaign-id">{c.id}</span><h3>{c.name}</h3><div className="campaign-card-bottom"><span><Database size={14} /> {c.iocs} sample IOCs</span><ChevronRight size={16} /></div></article>)}</div><p className="chart-footnote">Displayed metadata is a frontend sample. Confirm group details against your source dataset.</p></section>
  </>;
}

function NewThreatAnalysis() {
  return <>
    <div className="page-heading"><div><div className="eyebrow">EMERGING THREATS</div><h1>New Threat Analysis</h1><p>Review indicators that do not have an established campaign match.</p></div><Badge tone="orange">Analyst review</Badge></div>
    <section className="notice notice-wide"><ShieldAlert size={22} /><div><strong>Unknown does not automatically mean malicious.</strong><p>Campaign matching and maliciousness classification are separate decisions. Review evidence before assigning an actor.</p></div></section>
    <section className="panel"><div className="panel-heading"><div><h2>Unmatched indicator examples</h2><p>Illustrative records for workflow testing</p></div><Badge>Demo data</Badge></div><div className="table-wrap"><table><thead><tr><th>INDICATOR</th><th>CAMPAIGN STATUS</th><th>ATTRIBUTION STATUS</th><th>NEXT ACTION</th></tr></thead><tbody><tr><td className="mono">random-verify-8472.test</td><td><Badge tone="orange">No established match</Badge></td><td><Badge>Insufficient evidence</Badge></td><td>Enrich and review</td></tr><tr><td className="mono">unclustered-sample.example</td><td><Badge tone="gray">Unclustered</Badge></td><td><Badge>Not assessed</Badge></td><td>Compare behaviour</td></tr></tbody></table></div></section>
    <section className="panel workflow-panel"><h2>Suggested investigation workflow</h2><div className="workflow-steps">{[{n:"01",title:"Enrich",desc:"Collect DNS, IP, ASN, certificate and URL context."},{n:"02",title:"Compare",desc:"Compare behaviour and infrastructure with known campaigns."},{n:"03",title:"Review",desc:"Record supporting and conflicting evidence."},{n:"04",title:"Attribute",desc:"Suggest an actor only when evidence supports it."}].map(s => <div className="workflow-step" key={s.n}><span>{s.n}</span><h3>{s.title}</h3><p>{s.desc}</p></div>)}</div></section>
  </>;
}

function RelationshipGraph() {
  const nodes = [{x:50,y:12,label:"IOC",tone:"node-blue"},{x:22,y:42,label:"CAMP-01",tone:"node-purple"},{x:78,y:42,label:"CAMP-03",tone:"node-green"},{x:22,y:76,label:"SideCopy",tone:"node-purple"},{x:78,y:76,label:"Transparent Tribe",tone:"node-green"}];
  return <>
    <div className="page-heading"><div><div className="eyebrow">LINK ANALYSIS</div><h1>Relationship Graph</h1><p>Explore how indicators, campaigns and actors may be related.</p></div><Badge>Illustrative graph</Badge></div>
    <section className="panel graph-panel"><div className="panel-heading"><div><h2>IOC relationship map</h2><p>Example structure — not calculated from live evidence</p></div><button className="button button-secondary" onClick={() => window.print()}><Download size={16} /> Export</button></div><div className="graph-canvas"><svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><line x1="50" y1="15" x2="22" y2="42" /><line x1="50" y1="15" x2="78" y2="42" /><line x1="22" y1="46" x2="22" y2="76" /><line x1="78" y1="46" x2="78" y2="76" /></svg>{nodes.map(n => <div key={n.label} className={`graph-node ${n.tone}`} style={{left:`${n.x}%`,top:`${n.y}%`}}>{n.label}</div>)}</div><div className="graph-legend"><span><i className="legend-dot blue-dot" /> Indicator</span><span><i className="legend-dot purple-dot" /> Campaign</span><span><i className="legend-dot green-dot" /> Potential actor</span></div><div className="notice"><CircleHelp size={18} /><div><strong>Relationship is not proof of attribution.</strong><p>Edges in the production graph should be based on documented evidence and confidence.</p></div></div></section>
  </>;
}

export default function App() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [page, setPage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [globalSearch, setGlobalSearch] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  useEffect(() => {
  let active = true;

  async function checkBackend() {
    try {
      const response = await fetch("http://localhost:5000/api/health");
      const data = await response.json();

      if (active) {
        setBackendConnected(
          response.ok &&
          data.backend === "healthy" &&
          data.ml_api?.status === "healthy" &&
          data.ml_api?.model_loaded === true
        );
      }
    } catch {
      if (active) setBackendConnected(false);
    }
  }

  checkBackend();
  const interval = setInterval(checkBackend, 10000);

  return () => {
    active = false;
    clearInterval(interval);
  };
}, []);

  const pageComponents = {
    Dashboard: <Overview setPage={setPage} />,
    "IOC Search": <IOCSearch />,
    "Campaign Explorer": <CampaignExplorer />,
    "New Threat Analysis": <NewThreatAnalysis />,
    "Relationship Graph": <RelationshipGraph />,
  };

  return <div className="app-shell">
    {sidebarOpen && <button className="mobile-overlay" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}
    <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
      <div className="brand"><div className="brand-mark"><ShieldCheck size={23} /></div><div><strong>APT<span>INTEL</span></strong><small>THREAT INTELLIGENCE</small></div><button className="mobile-close icon-button" onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
      <div className="workspace-label">WORKSPACE <ChevronDown size={13} /></div>
      <div className="workspace-card"><div className="workspace-avatar">DR</div><div><strong>APT Research</strong><span>Threat Analysis Unit</span></div><ChevronDown size={15} /></div>
      <nav className="sidebar-nav">{["MAIN","INTELLIGENCE"].map(group => <div className="nav-group" key={group}><div className="nav-group-label">{group}</div>{navItems.filter(n => n.group === group).map(item => <button key={item.label} onClick={() => {setPage(item.label);setSidebarOpen(false);}} className={`nav-item ${page === item.label ? "nav-active" : ""}`}><item.icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.label === "New Threat Analysis" && <span className="nav-indicator" />}</button>)}</div>)}</nav>
      <div className="sidebar-bottom"><div className="system-status">
  <span
    className={`status-dot ${backendConnected ? "status-online" : "status-offline"}`}
  />
  <div>
    <strong>Interface ready</strong>
    <small>
      {backendConnected ? "Backend connected" : "Backend unavailable"}
    </small>
  </div>
</div><button className="nav-item" onClick={() => alert("Settings will be added in a later stage.")}><Settings size={18} /><span>Settings</span></button><div className="user-profile"><div className="user-avatar">AI</div><div><strong>Analyst Workspace</strong><span>Local development</span></div><ChevronDown size={15} /></div></div>
    </aside>

    <main className="main-area">
      <header className="topbar"><div className="topbar-left"><button className="mobile-menu icon-button" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={20} /></button><div className="breadcrumb">Workspace <ChevronRight size={14} /><strong>{page}</strong></div></div><div className="topbar-actions"><div className={`global-search ${searchOpen ? "global-search-open" : ""}`}><Search size={16} /><input value={globalSearch} onFocus={() => setSearchOpen(true)} onChange={e => setGlobalSearch(e.target.value)} onKeyDown={e => {if(e.key === "Enter" && globalSearch.trim()){setPage("IOC Search");setSearchOpen(false);}}} placeholder="Search anything..." /><kbd>↵</kbd></div><div className="topbar-divider" /><button className="icon-button notification-button" onClick={() => setNotificationsOpen(v => !v)} aria-label="Notifications"><Bell size={18} /><span /></button>{notificationsOpen && <div className="notification-popover"><strong>Notifications</strong><p>No live notifications. Backend integration is pending.</p></div>}<div className="topbar-avatar">DR</div></div></header>
      <div className="content-area">{pageComponents[page]}</div>
      <footer className="app-footer"><span><ShieldCheck size={14} /> APT Intelligence System</span><span>Frontend prototype <i /> Data is illustrative until connected</span></footer>
    </main>
  </div>;
}
