
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

LABEL_FILE = ROOT / "datasets" / "raw" / "phishing ioc dataset campaign labeled.xlsx"
CLUSTER_FILE = ROOT / "datasets" / "processed" / "discovered_campaign_clusters.csv"

labels = pd.read_excel(LABEL_FILE)
clusters = pd.read_csv(CLUSTER_FILE)

labels.columns = labels.columns.str.strip()

required_labels = ["IOC", "Campaign_ID", "Campaign_Label"]
required_clusters = ["IOC", "Discovered_Cluster_ID", "Status"]

for col in required_labels:
    if col not in labels.columns:
        raise ValueError(f"Missing label column: {col}")

for col in required_clusters:
    if col not in clusters.columns:
        raise ValueError(f"Missing cluster column: {col}")

# Normalize IOC strings for matching.
labels["IOC"] = labels["IOC"].astype(str).str.strip()
clusters["IOC"] = clusters["IOC"].astype(str).str.strip()

merged = labels[required_labels].merge(
    clusters[required_clusters],
    on="IOC",
    how="outer",
    indicator=True
)

if not (merged["_merge"] == "both").all():
    print("WARNING: Some IOCs did not match between the two files.")
    print(merged.loc[merged["_merge"] != "both", ["IOC", "_merge"]].to_string(index=False))

matched = merged[merged["_merge"] == "both"].copy()

print("\nDISCOVERED CLUSTER VALIDATION")
print("=" * 55)

# Compare each discovered candidate cluster with the original campaign IDs.
candidate = matched[matched["Status"] == "Candidate campaign"]

for cluster_id, group in candidate.groupby("Discovered_Cluster_ID"):
    campaign_counts = group["Campaign_ID"].value_counts().to_dict()
    label_counts = group["Campaign_Label"].value_counts().to_dict()

    print(f"\n{cluster_id}")
    print(f"IOC count: {len(group)}")
    print(f"Original campaign IDs: {campaign_counts}")
    print(f"Original campaign labels: {label_counts}")

    if len(campaign_counts) == 1 and "UNCLUSTERED" not in campaign_counts:
        print("Assessment: All members share one existing campaign ID.")
    else:
        print("Assessment: Review required; cluster spans multiple labels or includes unclustered data.")

print("\nUNCLUSTERED IOC CHECK")
unclustered = matched[matched["Status"] == "No match above threshold"]
print(f"Unclustered IOC count: {len(unclustered)}")
print("Original campaign ID counts:")
print(unclustered["Campaign_ID"].value_counts(dropna=False).to_string())

print("\nValidation report complete.")
