
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    ROOT / "datasets" / "raw"
    / "phishing ioc dataset campaign labeled.xlsx"
)
CLUSTER_FILE = (
    ROOT / "datasets" / "processed"
    / "discovered_campaign_clusters.csv"
)
OUTPUT_DIR = ROOT / "datasets" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "IP",
    "ASN",
    "Registrar",
    "Cert_Fingerprint",
    "Favicon_Hash",
    "Kit_Fuzzy_Hash",
    "HTML_Similarity_Score",
    "Target_Sector",
    "Target_Region",
    "Lure_Theme",
    "Subdomain_Pattern",
    "Domain_Age_Days",
]

def clean(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    if value.lower() in {"", "-", "—", "unknown", "none", "nan", "n/a"}:
        return None
    return value

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

if not CLUSTER_FILE.exists():
    raise FileNotFoundError(f"Cluster file not found: {CLUSTER_FILE}")

df = pd.read_excel(DATA_FILE)
df.columns = df.columns.str.strip()
clusters = pd.read_csv(CLUSTER_FILE)

required = ["IOC"] + FEATURES
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing dataset columns: {missing}")

df["IOC"] = df["IOC"].astype(str).str.strip()
clusters["IOC"] = clusters["IOC"].astype(str).str.strip()

df = df.merge(
    clusters[["IOC", "Discovered_Cluster_ID", "Status"]],
    on="IOC",
    how="left",
    validate="one_to_one",
)

if df["Discovered_Cluster_ID"].isna().any():
    raise ValueError("Some IOCs have no discovered cluster assignment.")

profiles = []

candidate_rows = df[df["Status"] == "Candidate campaign"]

for cluster_id, group in candidate_rows.groupby(
    "Discovered_Cluster_ID"
):
    members = []

    for _, row in group.iterrows():
        record = {"IOC": row["IOC"]}

        for feature in FEATURES:
            value = clean(row[feature])

            if value is not None:
                if feature == "HTML_Similarity_Score":
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        value = None

                elif feature == "Domain_Age_Days":
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        value = None

            record[feature] = value

        members.append(record)

    profiles.append({
        "campaign_profile_id": cluster_id,
        "member_count": len(members),
        "members": members,
    })

json_path = OUTPUT_DIR / "campaign_profiles.json"
csv_path = OUTPUT_DIR / "campaign_profiles_summary.csv"

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(profiles, f, indent=2, ensure_ascii=False)

summary = []

for profile in profiles:
    row = {
        "Campaign_Profile_ID": profile["campaign_profile_id"],
        "Member_Count": profile["member_count"],
    }

    for feature in FEATURES:
        values = {
            str(member[feature])
            for member in profile["members"]
            if member.get(feature) is not None
        }
        row[f"{feature}_Unique_Values"] = len(values)

    summary.append(row)

pd.DataFrame(summary).to_csv(csv_path, index=False)

print("\nCAMPAIGN PROFILES CREATED")
print("=" * 40)
print(f"Profiles created: {len(profiles)}")
print(f"Campaign members included: {sum(p['member_count'] for p in profiles)}")
print(f"Unclustered IOCs excluded from profiles: "
      f"{(df['Status'] == 'No match above threshold').sum()}")
print(f"\nJSON profiles: {json_path}")
print(f"CSV summary:   {csv_path}")
