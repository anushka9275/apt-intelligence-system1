import { useEffect, useState } from "react";
import {
  Activity, AlertTriangle, ArrowUpRight, Bell, ChevronDown,
  ChevronRight, CircleHelp, Database, Download, Filter, History,
  LayoutDashboard, Menu, Network, Search, Settings,
  ShieldAlert, ShieldCheck, Target, X
} from "lucide-react";
import "./App.css";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, group: "MAIN" },
  { label: "IOC Search", icon: Search, group: "MAIN" },
  { label: "IOC History", icon: History, group: "MAIN" },
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

function StatCard({ label, value, note, icon: Icon, tone = "blue" }) {
  return (
    <article className="stat-card">
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className={`stat-icon icon-${tone}`}><Icon size={19} /></span>
      </div>
      <div className="stat-value">{value}</div>
      <div className="stat-bottom"><span className="stat-trend"><ArrowUpRight size={14} />{note}</span></div>
    </article>
  );
}

function Overview({ setPage }) {
  const [campaignStats, setCampaignStats] = useState({
  total_iocs: 0,
  clustered_iocs: 0,
  unclustered_iocs: 0,
});

const [statsLoading, setStatsLoading] = useState(true);
const [statsError, setStatsError] = useState("");

useEffect(() => {
  async function fetchCampaignStats() {
    try {
      const response = await fetch(
        "http://localhost:8000/campaign-stats"
      );

      if (!response.ok) {
        throw new Error("Unable to load campaign statistics.");
      }

      const data = await response.json();
      setCampaignStats(data);
    } catch (error) {
      setStatsError(error.message);
    } finally {
      setStatsLoading(false);
    }
  }

  fetchCampaignStats();
}, []);
    const [campaignData, setCampaignData] = useState({
    total_profiles: 0,
    profiles: [],
  });

  const [campaignLoading, setCampaignLoading] = useState(true);
  const [campaignError, setCampaignError] = useState("");
  const [recentIOCs, setRecentIOCs] = useState([]);
const [historyLoading, setHistoryLoading] = useState(true);
const [historyError, setHistoryError] = useState("");

useEffect(() => {
  async function fetchRecentIOCs() {
    try {
      const response = await fetch(
        "http://localhost:5000/api/ioc-history"
      );

      if (!response.ok) {
        throw new Error("Unable to load IOC history.");
      }

      const data = await response.json();
      setRecentIOCs(data.records || []);
    } catch (error) {
      setHistoryError(error.message);
    } finally {
      setHistoryLoading(false);
    }
  }

  fetchRecentIOCs();
}, []);

  useEffect(() => {
    async function fetchCampaigns() {
      try {
        const response = await fetch("http://localhost:8000/campaigns");

        if (!response.ok) {
          throw new Error("Unable to load campaign data.");
        }

        const data = await response.json();
        setCampaignData(data);
      } catch (error) {
        setCampaignError(error.message);
      } finally {
        setCampaignLoading(false);
      }
    }

    fetchCampaigns();
  }, []);
  const distribution = campaignData.profiles.map((profile, index) => ({
  name: profile.campaign_profile_id,
  count: profile.member_count,
  tone: ["purple", "blue", "green", "orange", "gray"][index % 5],
}));

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">THREAT INTELLIGENCE OVERVIEW</div>
          <h1>Dashboard</h1>
          <p>Monitor indicators, campaign clusters and emerging threats.</p>
        </div>
        <Badge tone="green">Local workspace</Badge>
      </div>

       <div className="stats-grid">
        <StatCard
  label="Discovered profiles"
  value={campaignLoading ? "..." : campaignData.total_profiles}
  note="Live campaign profiles"
  icon={Target}
  tone="purple"
/>

<StatCard
  label="Clustered IOCs"
  value={
  statsLoading
    ? "..."
    : statsError
      ? "—"
      : campaignStats.clustered_iocs
}
  note="Across discovered groups"
  icon={Database}
  tone="blue"
/>

<StatCard
  label="Unclustered IOCs"
  value={
    statsLoading
      ? "..."
      : statsError
        ? "—"
        : campaignStats.unclustered_iocs
  }
  note={
    statsError || "No match above campaign threshold"
  }
  icon={Activity}
  tone="orange"
/>

<StatCard
  label="Attribution"
  value="Candidate only"
  note="Analyst validation required"
  icon={ShieldCheck}
  tone="green"
/>
      </div>

       <div className="dashboard-grid">
        <section className="panel distribution-panel">
          <div className="panel-heading">
            <div><h2>Campaign distribution</h2><p>Curated dataset groups</p></div>
            <button className="text-link" onClick={() => setPage("Campaign Explorer")}>View all <ChevronRight size={14} /></button>
          </div>
          <div className="distribution-total"><strong>8</strong><span>campaign labels</span></div>
          <div className="distribution-list">
            {distribution.map(({ name, count, tone }) => (
              <div className="distribution-row" key={name}>
                <div className="distribution-name">
                  <span className={`legend-dot ${tone}-dot`} />{name}<span>{count}</span>
                </div>
                <div className="progress-track">
                  <div className={`progress-fill fill-${tone}`} style={{ width: `${(count / 10) * 100}%` }} />
                </div>
              </div>
            ))}
             </div>
          <p className="chart-footnote">Live counts from discovered campaign profiles.</p>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div><h2>Quick actions</h2><p>Start an investigation</p></div>
          </div>
          <div className="quick-actions">
            <button className="button button-secondary" onClick={() => setPage("IOC Search")}><Search size={16} /> Search an IOC</button>
            <button className="button button-secondary" onClick={() => setPage("New Threat Analysis")}><ShieldAlert size={16} /> Analyze a new threat</button>
            <button className="button button-secondary" onClick={() => setPage("Relationship Graph")}><Network size={16} /> Open relationship graph</button>
          </div>
        </section>
      </div>

      <section className="panel recent-panel">
        <div className="panel-heading">
          <div><h2>Investigation queue</h2><p>Latest IOC analyses from MongoDB</p></div>
          <button className="text-link" onClick={() => setPage("IOC Search")}>Open IOC Search <ChevronRight size={14} /></button>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>INDICATOR</th><th>TYPE</th><th>ASSESSMENT</th><th>CAMPAIGN</th><th>CONFIDENCE</th></tr></thead>
              <tbody>
  {historyLoading ? (
    <tr>
      <td colSpan="5">Loading IOC history...</td>
    </tr>
  ) : historyError ? (
    <tr>
      <td colSpan="5">{historyError}</td>
    </tr>
  ) : recentIOCs.length === 0 ? (
    <tr>
      <td colSpan="5">No IOC records found.</td>
    </tr>
  ) : (
    recentIOCs.slice(0, 5).map((ioc) => (
      <tr key={ioc._id}>
        <td className="mono">{ioc.domain}</td>
        <td>Domain</td>
        <td>
          <Badge
            tone={
              ioc.predicted_label?.toLowerCase() === "suspicious"
                ? "red"
                : "gray"
            }
          >
            {ioc.predicted_label}
          </Badge>
        </td>
        <td>Not checked</td>
        <td>Not supplied</td>
      </tr>
    ))
  )}
</tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function IOCSearch() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

   async function analyzeDomain(event) {
    event.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
       const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: query.trim() }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Domain prediction request failed.");
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

  const suspicious = String(result?.predicted_label || "").toLowerCase().includes("suspicious");

  return (
    <>
      <div className="page-heading">
        <div><div className="eyebrow">INDICATOR INVESTIGATION</div><h1>IOC Search</h1><p>Run the domain-classification model against an indicator.</p></div>
      </div>

       <section className="panel search-panel">
        <div className="search-hero-icon"><Search size={26} /></div>
        <h2>Search a domain</h2>
        <p>Enter a domain to obtain the baseline model assessment.</p>
        <form className="ioc-form" onSubmit={analyzeDomain}>
          <Search size={18} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Enter a domain, e.g. example.com" required />
          <button className="button button-primary" type="submit" disabled={loading}>{loading ? "Analyzing..." : "Analyze Domain"}</button>
        </form>
        <div className="search-hints">
          <span>Try a sample:</span>
          {["google.com", "myntra-secure-login.com"].map((domain) => (
            <button type="button" key={domain} onClick={() => setQuery(domain)}>{domain}</button>
          ))}
        </div>
      </section>

      {error && <section className="panel result-panel"><div className="notice"><AlertTriangle size={18} /><div><strong>Request failed</strong><p>{error}</p></div></div></section>}

      {result && (
        <section className="panel result-panel">
          <div className="panel-heading">
            <div><h2>Model prediction</h2><p className="mono">{result.domain || query}</p></div>
            <Badge tone={suspicious ? "red" : "green"}>{result.predicted_label || "Result returned"}</Badge>
          </div>
          <div className="notice"><AlertTriangle size={18} /><div><strong>Baseline model output</strong><p>{result.warning || "This model output is an initial assessment and requires analyst verification."}</p></div></div>
          <div className="result-grid">
            <div><span>Predicted label</span><strong>{result.predicted_label || "Unavailable"}</strong></div>
            <div><span>Benign score</span><strong>{result.model_scores?.benign !== undefined ? `${(result.model_scores.benign * 100).toFixed(2)}%` : "Unavailable"}</strong></div>
            <div><span>Suspicious score</span><strong>{result.model_scores?.suspicious !== undefined ? `${(result.model_scores.suspicious * 100).toFixed(2)}%` : "Unavailable"}</strong></div>
          </div>
          <p className="chart-footnote">Scores are model outputs, not calibrated probabilities or proof of malicious activity. Campaign matching and APT attribution have not been performed.</p>
        </section>
      )}
    </>
  );
}


function IOCHistory() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [filter, setFilter] = useState("All");

  async function fetchHistory() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:5000/api/ioc-history");

      if (!response.ok) {
        throw new Error("Unable to load IOC history.");
      }

      const data = await response.json();
      setRecords(data.records || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchHistory();
  }, []);
  const filteredRecords = records.filter((record) => {
  const matchesSearch = record.domain
    ?.toLowerCase()
    .includes(searchTerm.toLowerCase());

  const matchesFilter =
    filter === "All" ||
    record.predicted_label?.toLowerCase() === filter.toLowerCase();

  return matchesSearch && matchesFilter;
});

function exportCSV() {
  const headers = [
    "Domain",
    "Prediction",
    "Analyzed Date",
    "Warning"
  ];

  const escapeCSV = (value) =>
    `"${String(value ?? "").replace(/"/g, '""')}"`;

  const rows = filteredRecords.map((record) => [
    record.domain,
    record.predicted_label,
    record.createdAt
      ? new Date(record.createdAt).toLocaleString()
      : "",
    record.warning
  ]);

  const csvContent = [
    headers.map(escapeCSV).join(","),
    ...rows.map((row) => row.map(escapeCSV).join(","))
  ].join("\n");

  const blob = new Blob([csvContent], {
    type: "text/csv;charset=utf-8;"
  });

  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "ioc-history.csv";
  link.click();

  URL.revokeObjectURL(url);
}

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">INDICATOR INVESTIGATION</div>
          <h1>IOC History</h1>
          <p>View previously analyzed indicators stored in the database.</p>
        </div>

        <button
          className="button button-secondary"
          onClick={fetchHistory}
          disabled={loading}
        >
          {loading ? "Loading..." : "Refresh History"}
        </button>
      </div>

      <section className="panel">
        <div className="history-controls">
  <input
    type="text"
    placeholder="Search domain..."
    value={searchTerm}
    onChange={(event) => setSearchTerm(event.target.value)}
  />

  <select
    value={filter}
    onChange={(event) => setFilter(event.target.value)}
  >
    <option value="All">All predictions</option>
    <option value="Suspicious">Suspicious</option>
    <option value="Benign">Benign</option>
  </select>
</div>
        <div className="panel-heading">
          <div>
            <h2>Saved IOC Records</h2>
            <p>{filteredRecords.length} matching indicators</p>
          </div>
          <div className="history-actions">
  <button
    className="button button-secondary"
    onClick={exportCSV}
    disabled={filteredRecords.length === 0}
  >
    <Download size={16} />
    Export CSV
  </button>

  <Badge tone="blue">MongoDB Atlas</Badge>
</div>
        </div>

        {loading && <p>Loading IOC history...</p>}

        {error && <p className="error-message">{error}</p>}

        {!loading && !error && filteredRecords.length === 0 && (
          <p>No IOC records found. Analyze a domain to get started.</p>
        )}

        {!loading && !error && filteredRecords.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>DOMAIN</th>
                  <th>PREDICTION</th>
                  <th>DATE ANALYZED</th>
                </tr>
              </thead>

              <tbody>
                {filteredRecords.map((record) => (
                  <tr key={record._id}>
                    <td>{record.domain}</td>
                    <td>
                      <Badge
                        tone={
                          record.predicted_label?.toLowerCase() === "suspicious"
                            ? "red"
                            : "green"
                        }
                      >
                        {record.predicted_label}
                      </Badge>
                    </td>
                    <td>
                      {record.createdAt
                        ? new Date(record.createdAt).toLocaleString()
                        : "Unknown"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}

function CampaignExplorer() {
  const [filter, setFilter] = useState("");
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [campaignStats, setCampaignStats] = useState(null);
const [statsLoading, setStatsLoading] = useState(true);
const [statsError, setStatsError] = useState("");
const [expandedProfiles, setExpandedProfiles] = useState({});

    // Fetch campaign statistics
  useEffect(() => {
    async function fetchCampaignStats() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/campaign-stats"
        );

        if (!response.ok) {
          throw new Error("Failed to load campaign statistics.");
        }

        const data = await response.json();
        setCampaignStats(data);
      } catch (err) {
        setStatsError(err.message);
      } finally {
        setStatsLoading(false);
      }
    }

    fetchCampaignStats();
  }, []);

  // Fetch campaign profiles
  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          "http://127.0.0.1:8000/campaigns"
        );

        if (!response.ok) {
          throw new Error("Failed to load campaign profiles.");
        }

        const data = await response.json();
        setProfiles(data.profiles || []);
      } catch (err) {
        setError(err.message || "Unable to connect to the API.");
      } finally {
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  const filtered = profiles.filter((campaign) => {
    const memberNames = (campaign.members || [])
      .map((member) => member.IOC || "")
      .join(" ");

    const searchText =
      `${campaign.campaign_profile_id} ${memberNames}`.toLowerCase();

    return searchText.includes(filter.toLowerCase());
  });

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">THREAT CLUSTERING</div>
          <h1>Campaign Explorer</h1>
          <p>
            Explore discovered campaign profiles and their associated IOCs.
          </p>
        </div>

        <button
          className="button button-secondary"
          onClick={() => setFilter("")}
        >
          <Filter size={16} /> Reset filter
        </button>
      </div>

      <div className="stats-grid compact-stats">
        <StatCard
          label="Discovered profiles"
          value={profiles.length}
          note="Loaded from campaign dataset"
          icon={Target}
          tone="purple"
        />

        <StatCard
  label="Unclustered records"
  value={
    statsLoading
      ? "..."
      : statsError
        ? "—"
        : campaignStats?.unclustered_iocs ?? "—"
  }
  note={statsError || "No match above campaign threshold"}
  icon={Network}
  tone="orange"
/>

        <StatCard
          label="Attribution"
          value="Analyst review"
          note="Requires supporting evidence"
          icon={ShieldCheck}
          tone="green"
        />
      </div>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Campaign catalogue</h2>
            <p>Search by profile ID or associated IOC</p>
          </div>

          <span className="record-count">
            {filtered.length} profiles
          </span>
        </div>

        <div className="filter-input">
          <Search size={17} />

          <input
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
            placeholder="Filter profiles or IOCs..."
          />
        </div>

        {loading && (
          <p>Loading campaign profiles...</p>
        )}

        {error && (
          <p className="chart-footnote">
            Error: {error}
          </p>
        )}

        {!loading && !error && filtered.length === 0 && (
          <p>No matching campaign profiles found.</p>
        )}

        {!loading && !error && (
          <div className="campaign-grid">
            {filtered.map((campaign) => (
              <article
                className="campaign-card"
                key={campaign.campaign_profile_id}
              >
                <div className="campaign-card-top">
                  <span className="campaign-mark purple">
                    <Target size={19} />
                  </span>

                  <Badge tone="blue">
                    Discovered
                  </Badge>
                </div>

                
<span className="campaign-id">
  {campaign.campaign_profile_id}
</span>

<h3>Discovered Campaign Profile</h3>

<div className="campaign-detail-grid">
  <div className="campaign-detail-item">
    <span>Cluster status</span>
    <strong>{campaign.status || "Unavailable"}</strong>
  </div>

  <div className="campaign-detail-item">
    <span>Similarity threshold</span>
    <strong>
      {typeof campaign.similarity_threshold === "number"
        ? campaign.similarity_threshold.toFixed(2)
        : "Unavailable"}
    </strong>
  </div>

  <div className="campaign-detail-item">
    <span>Cluster size</span>
    <strong>{campaign.cluster_size ?? campaign.member_count}</strong>
  </div>
</div>
<div className="campaign-intelligence">
  <h4>Campaign Intelligence</h4>

  <div className="campaign-intelligence-item">
    <span>Target sectors</span>
    <strong>
      {campaign.target_sectors?.length
        ? campaign.target_sectors.join(", ")
        : "Unavailable"}
    </strong>
  </div>

  <div className="campaign-intelligence-item">
    <span>Target regions</span>
    <strong>
      {campaign.target_regions?.length
        ? campaign.target_regions.join(", ")
        : "Unavailable"}
    </strong>
  </div>

  <div className="campaign-intelligence-item">
    <span>Lure themes</span>
    <div className="campaign-theme-list">
      {campaign.lure_themes?.length
        ? campaign.lure_themes.map((theme, index) => (
            <span key={`${theme}-${index}`}>{theme}</span>
          ))
        : <span>Unavailable</span>}
    </div>
  </div>

  <div className="campaign-intelligence-item">
    <span>Shared infrastructure</span>
    <div className="campaign-infrastructure-list">
      {campaign.shared_infrastructure &&
      Object.keys(campaign.shared_infrastructure).length > 0 ? (
        Object.entries(campaign.shared_infrastructure).map(
          ([field, value]) => (
            <p key={field}>
              <strong>{field.replaceAll("_", " ")}</strong>
              {value}
            </p>
          )
        )
      ) : (
        <p>No shared infrastructure identified</p>
      )}
    </div>
  </div>
</div>


                <div className="campaign-card-bottom">
                  <span>
                    <Database size={14} />
                    {campaign.member_count} associated IOCs
                  </span>

                  <ChevronRight size={16} />
                </div>

                <div className="campaign-members">
  {(campaign.members || [])
    .slice(
      0,
      expandedProfiles[campaign.campaign_profile_id]
        ? undefined
        : 3
    )
    .map((member, index) => (
      <p key={`${member.IOC}-${index}`}>
        {member.IOC}
      </p>
    ))}

  {campaign.members?.length > 3 && (
    <button
      className="campaign-members-toggle"
      onClick={() =>
        setExpandedProfiles((previous) => ({
          ...previous,
          [campaign.campaign_profile_id]:
            !previous[campaign.campaign_profile_id],
        }))
      }
    >
      {expandedProfiles[campaign.campaign_profile_id]
        ? "Show less"
        : `View all ${campaign.members.length} IOCs`}
    </button>
  )}
</div>
              </article>
            ))}
          </div>
        )}

        <p className="chart-footnote">
          Profiles are loaded from the campaign_profiles.json dataset.
          Profile similarity does not independently establish APT attribution.
        </p>
      </section>
    </>
  );
}

function NewThreatAnalysis() {
  const [ioc, setIoc] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [enriching, setEnriching] = useState(false);
const [enrichmentMessage, setEnrichmentMessage] = useState("");
  const [showEnrichment, setShowEnrichment] = useState(false);
  const [enrichment, setEnrichment] = useState({
    IP: "", ASN: "", Registrar: "", Cert_Fingerprint: "",
    Favicon_Hash: "", Kit_Fuzzy_Hash: "", HTML_Similarity_Score: "",
    Domain_Age_Days: "", Target_Sector: "", Target_Region: "",
    Lure_Theme: "", Subdomain_Pattern: "",
  });

  const infrastructureFields = [
    ["IP", "IP address", "e.g. 192.0.2.10"],
    ["ASN", "ASN", "e.g. AS12345"],
    ["Registrar", "Registrar", "Domain registrar"],
    ["Cert_Fingerprint", "Certificate fingerprint", "SHA1 or SHA256 fingerprint"],
    ["Favicon_Hash", "Favicon hash", "Website favicon hash"],
    ["Kit_Fuzzy_Hash", "Kit fuzzy hash", "Phishing kit fuzzy hash"],
  ];

  const campaignFields = [
    ["HTML_Similarity_Score", "HTML similarity score", "Value from 0 to 1"],
    ["Domain_Age_Days", "Domain age (days)", "e.g. 30"],
    ["Target_Sector", "Target sector", "e.g. Defence"],
    ["Target_Region", "Target region", "e.g. South Asia"],
    ["Lure_Theme", "Lure theme", "e.g. Government notification"],
    ["Subdomain_Pattern", "Subdomain pattern", "e.g. login-*"],
  ];

  function updateEnrichment(field, value) {
    setEnrichment((previous) => ({ ...previous, [field]: value }));
  }
  async function autoEnrichIOC() {
  if (!ioc.trim()) {
    setEnrichmentMessage("Enter a domain first.");
    return;
  }

  setEnriching(true);
  setEnrichmentMessage("Resolving domain...");

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/enrich-ioc",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          domain: ioc.trim(),
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "IOC enrichment failed."
      );
    }

    if (data.ip_addresses?.length > 0) {
      setShowEnrichment(true);

      updateEnrichment("IP", data.ip_addresses[0]);

      setEnrichmentMessage(
        `DNS resolved. Found ${data.ip_addresses.length} IP address(es): ${data.ip_addresses.join(", ")}. First IP populated in the field.`
      );
    } else {
      setEnrichmentMessage(
        data.warning || "No IP addresses found."
      );
    }
  } catch (err) {
    setEnrichmentMessage(err.message);
  } finally {
    setEnriching(false);
  }
}

  function clearEnrichment() {
    setEnrichment({
      IP: "", ASN: "", Registrar: "", Cert_Fingerprint: "",
      Favicon_Hash: "", Kit_Fuzzy_Hash: "", HTML_Similarity_Score: "",
      Domain_Age_Days: "", Target_Sector: "", Target_Region: "",
      Lure_Theme: "", Subdomain_Pattern: "",
    });
  }

  function buildRequestPayload() {
    const payload = { IOC: ioc.trim() };
    Object.entries(enrichment).forEach(([field, rawValue]) => {
      const value = rawValue.trim();
      if (!value) return;

      if (field === "HTML_Similarity_Score" || field === "Domain_Age_Days") {
        const numericValue = Number(value);
        if (!Number.isFinite(numericValue)) {
          throw new Error(`${field.replaceAll("_", " ")} must be a valid number.`);
        }
        if (numericValue < 0) {
          throw new Error(`${field.replaceAll("_", " ")} cannot be negative.`);
        }
        if (field === "HTML_Similarity_Score" && numericValue > 1) {
          throw new Error("HTML Similarity Score must be between 0 and 1.");
        }
        payload[field] = numericValue;
      } else {
        payload[field] = value;
      }
    });
    return payload;
  }

  async function analyzeThreat(event) {
    event.preventDefault();
    if (!ioc.trim()) return;

    let payload;
    try {
      payload = buildRequestPayload();
    } catch (validationError) {
      setError(validationError.message);
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/campaign-match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Campaign matching request failed.");
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

   const topMatch = result?.top_match;
   const attribution = result?.attribution;
  const rankedCandidates = Array.isArray(result?.ranked_candidates) ? result.ranked_candidates : [];

  return (
    <>
      <style>{`
       .nta-enrichment { margin-top: 22px; text-align: left; }
        .nta-enrichment-toggle { display: flex; align-items: center; gap: 8px; margin: 0 auto; }
        .nta-enrichment-content { margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--border, rgba(128,128,128,.25)); }
        .nta-enrichment-content h3 { margin: 16px 0 12px; font-size: 14px; }
        .nta-enrichment-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
        .nta-enrichment-field { display: flex; flex-direction: column; gap: 7px; min-width: 0; }
        .nta-enrichment-field label { font-size: 12px; font-weight: 600; }
        .nta-enrichment-field input { box-sizing: border-box; width: 100%; min-width: 0; padding: 11px 12px; border: 1px solid var(--border, rgba(128,128,128,.35)); border-radius: 7px; background: var(--background, transparent); color: inherit; font: inherit; font-size: 13px; }
        .nta-enrichment-field input:focus { outline: 2px solid var(--accent, #4f8cff); outline-offset: 1px; }
        .nta-enrichment-note { margin: 14px 0 0; color: var(--text-muted, #888); font-size: 11px; line-height: 1.5; }
        .nta-enrichment-actions { display: flex; justify-content: flex-end; margin-top: 12px; }
        @media (max-width: 650px) { .nta-enrichment-grid { grid-template-columns: 1fr; } }
      `}</style>

 <div className="page-heading">
        <div><div className="eyebrow">EMERGING THREATS</div><h1>New Threat Analysis</h1><p>Compare a new indicator against established campaign profiles.</p></div>
        <Badge tone="orange">Analyst review</Badge>
      </div>

      <section className="notice notice-wide">
        <ShieldAlert size={22} />
        <div><strong>Campaign matching is evidence-based.</strong><p>A match does not prove attribution. Review the supporting infrastructure and behavioural evidence.</p></div>
      </section>

       <section className="panel search-panel">
        <div className="search-hero-icon"><Target size={26} /></div>
        <h2>Analyze a new IOC</h2>
        <p>Submit an IOC and, if available, its enrichment details to compare it against discovered campaign profiles.</p>

        <form className="ioc-form" onSubmit={analyzeThreat}>
          <Search size={18} />
          <input value={ioc} onChange={(event) => setIoc(event.target.value)} placeholder="e.g. secure-mod-gov.in.example" required />
          <button className="button button-primary" type="submit" disabled={loading}>{loading ? "Matching..." : "Analyze Threat"}</button>
        </form>

         <div className="search-hints">
          <span>Try a sample:</span>
          {["secure-mod-gov.in.example", "random-verify-8472.test"].map((sample) => (
            <button type="button" key={sample} onClick={() => setIoc(sample)}>{sample}</button>
          ))}
        </div>

        <div className="nta-enrichment">
          <div className="nta-auto-enrich">
  <button
    type="button"
    className="button button-secondary"
    onClick={() => {
      setShowEnrichment(true);
      autoEnrichIOC();
    }}
    disabled={enriching || !ioc.trim()}
  >
    {enriching ? "Enriching..." : "Auto Enrich IOC"}
  </button>

  {enrichmentMessage && (
    <p className="nta-enrichment-note">
      {enrichmentMessage}
    </p>
  )}
</div>
          <button type="button" className="button button-secondary nta-enrichment-toggle" onClick={() => setShowEnrichment((current) => !current)}>
            {showEnrichment ? "Hide enrichment fields" : "Add enrichment details"}
            <ChevronDown size={16} />
          </button>

           {showEnrichment && (
            <div className="nta-enrichment-content">
              <h3>Infrastructure details</h3>
              <div className="nta-enrichment-grid">
                {infrastructureFields.map(([field, label, placeholder]) => (
                  <div className="nta-enrichment-field" key={field}>
                    <label htmlFor={`nta-${field}`}>{label}</label>
                    <input id={`nta-${field}`} type="text" value={enrichment[field]} onChange={(event) => updateEnrichment(field, event.target.value)} placeholder={placeholder} />
                  </div>
                ))}
              </div>

               <h3>Campaign characteristics</h3>
              <div className="nta-enrichment-grid">
                {campaignFields.map(([field, label, placeholder]) => (
                  <div className="nta-enrichment-field" key={field}>
                    <label htmlFor={`nta-${field}`}>{label}</label>
                    <input
                      id={`nta-${field}`}
                      type={field === "HTML_Similarity_Score" || field === "Domain_Age_Days" ? "number" : "text"}
                      min="0"
                      max={field === "HTML_Similarity_Score" ? "1" : undefined}
                      step="any"
                      value={enrichment[field]}
                      onChange={(event) => updateEnrichment(field, event.target.value)}
                      placeholder={placeholder}
                    />
                  </div>
                ))}
              </div>
              <p className="nta-enrichment-note">Only enter values obtained from a reliable enrichment source. HTML similarity is expected to be between 0 and 1. Empty fields are omitted from the API request.</p>
              <div className="nta-enrichment-actions"><button type="button" className="button button-secondary" onClick={clearEnrichment}>Clear enrichment</button></div>
            </div>
          )}
        </div>
      </section>

{error && <section className="panel result-panel"><div className="notice"><AlertTriangle size={18} /><div><strong>Request failed</strong><p>{error}</p></div></div></section>}

      {result && (
        <section className="panel result-panel">
          <div className="panel-heading">
            <div><h2>Campaign matching result</h2><p className="mono">{result.IOC || ioc}</p></div>
            <Badge tone={result.status === "Candidate campaign match" ? "green" : "orange"}>{result.status || "Result returned"}</Badge>
          </div>

          <div className="result-grid">
            <div><span>Top campaign</span><strong>{topMatch?.campaign_profile_id || "Unavailable"}</strong></div>
            <div><span>Similarity score</span><strong>{typeof topMatch?.score === "number" ? `${(topMatch.score * 100).toFixed(2)}%` : "Unavailable"}</strong></div>
            <div><span>Strong evidence signals</span><strong>{topMatch?.strong_evidence_count ?? "0"}</strong></div>
          </div>
          {topMatch && (
  <div className="campaign-match-details">
    <h3>Best matching profile details</h3>

    <p>
      <strong>Matched IOC: </strong>
      <span className="mono">
        {topMatch.matched_member || "Unavailable"}
      </span>
    </p>

    <p>
      <strong>Matching evidence: </strong>
      {Array.isArray(topMatch.evidence) && topMatch.evidence.length > 0
        ? topMatch.evidence.join(", ")
        : "No evidence details returned"}
    </p>

    <p>
      <strong>Matching threshold: </strong>
      {typeof result.threshold === "number"
        ? `${(result.threshold * 100).toFixed(0)}%`
        : "Unavailable"}
    </p>
  </div>
)}
{attribution && (
  <div className="campaign-match-details">
    <h3>Threat Actor Attribution</h3>

    <p>
      <strong>Attribution status: </strong>
      {attribution.attribution_status || "Unavailable"}
    </p>

    <p>
      <strong>Candidate actor: </strong>
      {attribution.candidate_actor || "No actor attributed"}
    </p>

    <p>
      <strong>Dataset attribution confidence: </strong>
      {attribution.dataset_attribution_confidence || "Unavailable"}
    </p>

    <p>
      <strong>Reference campaign: </strong>
      {attribution.reference_campaign_id || "Unavailable"}
    </p>

    <p>
      <strong>Campaign label: </strong>
      {attribution.reference_campaign_label || "Unavailable"}
    </p>

    {Array.isArray(attribution.attribution_rationale) &&
      attribution.attribution_rationale.length > 0 && (
        <div>
          <strong>Attribution rationale:</strong>
          <ul>
            {attribution.attribution_rationale.map((reason, index) => (
              <li key={index}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

    {attribution.warning && (
      <p className="chart-footnote">
        {attribution.warning}
      </p>
    )}
  </div>
)}
<p className="chart-footnote">
  {result.note || "Similarity scores require analyst review."}
</p>

           {rankedCandidates.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead><tr><th>CAMPAIGN</th><th>SCORE</th><th>MATCHED IOC</th><th>EVIDENCE</th></tr></thead>
                <tbody>
                  {rankedCandidates.slice(0, 3).map((candidate, index) => (
                    <tr key={`${candidate.campaign_profile_id || "candidate"}-${index}`}>
                      <td>{candidate.campaign_profile_id || "Unavailable"}</td>
                      <td>{typeof candidate.score === "number" ? `${(candidate.score * 100).toFixed(2)}%` : "Unavailable"}</td>
                      <td className="mono">{candidate.matched_member || "Unavailable"}</td>
                      <td>{Array.isArray(candidate.evidence) && candidate.evidence.length ? candidate.evidence.join(", ") : "None"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="chart-footnote">Similarity indicates resemblance to a stored profile; it is not proof that the IOC belongs to that campaign or actor.</p>
        </section>
      )}

      <section className="panel workflow-panel">
        <h2>Suggested investigation workflow</h2>
        <div className="workflow-steps">
          {[
            { n: "01", title: "Enrich", desc: "Collect DNS, IP, ASN, certificate and URL context." },
            { n: "02", title: "Compare", desc: "Compare infrastructure with known campaign profiles." },
            { n: "03", title: "Review", desc: "Record supporting and conflicting evidence." },
            { n: "04", title: "Attribute", desc: "Suggest an actor only when evidence supports it." },
          ].map((step) => (
            <div className="workflow-step" key={step.n}><span>{step.n}</span><h3>{step.title}</h3><p>{step.desc}</p></div>
          ))}
        </div>
      </section>
    </>
  );
}


function RelationshipGraph() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedCampaign, setSelectedCampaign] = useState(null);

  useEffect(() => {
    let active = true;

    async function fetchCampaigns() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch("http://127.0.0.1:8000/campaigns");

        if (!response.ok) {
          throw new Error("Unable to load campaign profiles.");
        }

        const data = await response.json();

        if (active) {
          setProfiles(Array.isArray(data.profiles) ? data.profiles : []);
        }
      } catch (err) {
        if (active) setError(err.message || "Failed to load graph data.");
      } finally {
        if (active) setLoading(false);
      }
    }

    fetchCampaigns();

    return () => {
      active = false;
    };
  }, []);

  const graphWidth = Math.max(900, profiles.length * 230);
  const graphHeight = 600;

  const campaignPositions = profiles.map((profile, index) => ({
    x: 120 + index * 230,
    y: 100,
    profile,
  }));

  const selectedProfile = profiles.find(
    (profile) => profile.campaign_profile_id === selectedCampaign
  );

  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">LINK ANALYSIS</div>
          <h1>Relationship Graph</h1>
          <p>Explore discovered campaigns, their indicators and shared infrastructure.</p>
        </div>
        <Badge>Live campaign data</Badge>
      </div>

      <section className="panel graph-panel">
        <div className="panel-heading">
          <div>
            <h2>IOC relationship map</h2>
            <p>Connections are derived from discovered campaign profile membership.</p>
          </div>
          <button
            className="button button-secondary"
            onClick={() => window.print()}
          >
            <Download size={16} /> Export
          </button>
        </div>

        {loading && <p>Loading campaign relationships...</p>}

        {error && (
          <div className="notice">
            <CircleHelp size={18} />
            <div>
              <strong>Unable to load graph</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {!loading && !error && profiles.length === 0 && (
          <p>No campaign profiles are available.</p>
        )}

        {!loading && !error && profiles.length > 0 && (
          <>
            <div style={{ overflowX: "auto", padding: "12px 0" }}>
              <svg
                viewBox={`0 0 ${graphWidth} ${graphHeight}`}
                style={{ width: "100%", minWidth: "900px", height: "600px" }}
                role="img"
                aria-label="Campaign and IOC relationship graph"
              >
                {campaignPositions.map(({ x, y, profile }) => {
                  const members = profile.members || [];
                  const memberSpacing = Math.min(
                    65,
                    300 / Math.max(members.length, 1)
                  );

                  const infrastructure = Object.entries(
                    profile.shared_infrastructure || {}
                  ).filter(([, value]) => value);

                  return (
                    <g key={profile.campaign_profile_id}>
                      {members.map((member, index) => {
                        const memberY =
                          245 + index * memberSpacing;

                        return (
                          <g key={member.IOC}>
                            <line
                              x1={x}
                              y1={y + 25}
                              x2={x}
                              y2={memberY - 12}
                              stroke="#94a3b8"
                              strokeWidth="1.5"
                            />
                            <rect
                              x={x - 90}
                              y={memberY - 12}
                              width="180"
                              height="28"
                              rx="6"
                              fill="#dbeafe"
                              stroke="#3b82f6"
                            />
                            <text
                              x={x}
                              y={memberY + 6}
                              textAnchor="middle"
                              fontSize="10"
                              fill="#1e3a8a"
                            >
                              {member.IOC.length > 27
                                ? `${member.IOC.slice(0, 24)}...`
                                : member.IOC}
                            </text>
                          </g>
                        );
                      })}

                      <rect
                        x={x - 85}
                        y={y - 25}
                        width="170"
                        height="50"
                        rx="9"
                        fill="#ede9fe"
                        stroke="#8b5cf6"
                        strokeWidth="2"
                      />
                      <text
                        x={x}
                        y={y + 5}
                        textAnchor="middle"
                        fontSize="14"
                        fontWeight="bold"
                        fill="#5b21b6"
                      >
                        {profile.campaign_profile_id}
                      </text>

                      {infrastructure.slice(0, 4).map(
                        ([key, value], index) => (
                          <text
                            key={key}
                            x={x}
                            y={525 + index * 17}
                            textAnchor="middle"
                            fontSize="10"
                            fill="#475569"
                          >
                            {key}: {String(value).slice(0, 22)}
                          </text>
                        )
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="graph-legend">
              <span>
                <i className="legend-dot blue-dot" /> IOC
              </span>
              <span>
                <i className="legend-dot purple-dot" /> Campaign
              </span>
            </div>

            <div className="campaign-detail-grid">
              {profiles.map((profile) => (
                <button
                  type="button"
                  key={profile.campaign_profile_id}
                  className="button button-secondary"
                  onClick={() =>
                    setSelectedCampaign(
                      selectedCampaign === profile.campaign_profile_id
                        ? null
                        : profile.campaign_profile_id
                    )
                  }
                >
                  {profile.campaign_profile_id} · {profile.member_count} IOCs
                </button>
              ))}
            </div>

            {selectedProfile && (
              <div className="campaign-match-details">
                <h3>{selectedProfile.campaign_profile_id} details</h3>
                <p>
                  <strong>Status: </strong>
                  {selectedProfile.status}
                </p>
                <p>
                  <strong>Target sectors: </strong>
                  {(selectedProfile.target_sectors || []).join(", ") || "Unavailable"}
                </p>
                <p>
                  <strong>Target regions: </strong>
                  {(selectedProfile.target_regions || []).join(", ") || "Unavailable"}
                </p>
                <p><strong>Campaign IOCs:</strong></p>
                <ul>
                  {(selectedProfile.members || []).map((member) => (
                    <li key={member.IOC}>{member.IOC}</li>
                  ))}
                </ul>
                <p><strong>Shared infrastructure:</strong></p>
                <ul>
                  {Object.entries(selectedProfile.shared_infrastructure || {}).map(
                    ([key, value]) => (
                      <li key={key}>
                        {key}: {String(value)}
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}
          </>
        )}

        <div className="notice">
          <CircleHelp size={18} />
          <div>
            <strong>Relationship is not proof of attribution.</strong>
            <p>
              IOC-to-campaign links represent discovered profile membership.
              Shared infrastructure is supporting similarity evidence, not
              proof of common ownership or threat actor identity.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}


export default function App() {
  const [backendConnected, setBackendConnected] = useState(false);
  const [page, setPage] = useState("Dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [globalSearch, setGlobalSearch] = useState("");
  const [notificationsOpen, setNotificationsOpen] = useState(false);

   useEffect(() => {
    let active = true;

    async function checkBackend() {
      try {
        const response = await fetch("http://127.0.0.1:8000/health");
        const data = await response.json();
        if (active) {
          setBackendConnected(response.ok && data.status === "healthy" && data.model_loaded === true);
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
    "IOC History": <IOCHistory />,
    "Campaign Explorer": <CampaignExplorer />,
    "New Threat Analysis": <NewThreatAnalysis />,
    "Relationship Graph": <RelationshipGraph />,
  };

   return (
    <div className="app-shell">
      {sidebarOpen && <button className="mobile-overlay" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={23} /></div>
          <div><strong>APT<span>INTEL</span></strong><small>THREAT INTELLIGENCE</small></div>
          <button className="mobile-close icon-button" onClick={() => setSidebarOpen(false)} aria-label="Close navigation"><X size={18} /></button>
        </div>
        <div className="workspace-label">WORKSPACE <ChevronDown size={13} /></div>
        <div className="workspace-card"><div className="workspace-avatar">DR</div><div><strong>APT Research</strong><span>Threat Analysis Unit</span></div><ChevronDown size={15} /></div>
        <nav className="sidebar-nav">
          {["MAIN", "INTELLIGENCE"].map((group) => (
            <div className="nav-group" key={group}>
              <div className="nav-group-label">{group}</div>
              {navItems.filter((item) => item.group === group).map((item) => {
                const Icon = item.icon;
                return (
                  <button key={item.label} onClick={() => { setPage(item.label); setSidebarOpen(false); }} className={`nav-item ${page === item.label ? "nav-active" : ""}`}>
                    <Icon size={18} strokeWidth={1.8} /><span>{item.label}</span>{item.label === "New Threat Analysis" && <span className="nav-indicator" />}
                  </button>
                );
              })}
              </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="system-status">
            <span className={`status-dot ${backendConnected ? "status-online" : "status-offline"}`} />
            <div><strong>Interface ready</strong><small>{backendConnected ? "Backend connected" : "Backend unavailable"}</small></div>
          </div>
          <button className="nav-item" onClick={() => window.alert("Settings will be added in a later stage.")}><Settings size={18} /><span>Settings</span></button>
          <div className="user-profile"><div className="user-avatar">AI</div><div><strong>Analyst Workspace</strong><span>Local development</span></div><ChevronDown size={15} /></div>
        </div>
        </aside>

         <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu icon-button" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
            <div className="breadcrumb">Workspace <ChevronRight size={14} /><strong>{page}</strong></div>
          </div>
          <div className="topbar-actions">
            <div className="global-search">
              <Search size={16} />
              <input value={globalSearch} onChange={(event) => setGlobalSearch(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && globalSearch.trim()) { setPage("IOC Search"); } }} placeholder="Search anything..." />
              <kbd>↵</kbd>
            </div>
            <div className="topbar-divider" />
            <button className="icon-button notification-button" onClick={() => setNotificationsOpen((current) => !current)} aria-label="Notifications"><Bell size={18} /><span /></button>
            {notificationsOpen && <div className="notification-popover"><strong>Notifications</strong><p>No live notifications. Backend integration is pending.</p></div>}
            <div className="topbar-avatar">DR</div>
          </div>
        </header>
        <div className="content-area">{pageComponents[page] || pageComponents.Dashboard}</div>
        <footer className="app-footer"><span><ShieldCheck size={14} /> APT Intelligence System</span><span>Frontend prototype <i /> Data is illustrative until connected</span></footer>
      </main>
    </div>
  );
}
