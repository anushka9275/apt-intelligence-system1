
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "datasets" / "processed" / "campaign_pair_similarity.csv"
OUTPUT = ROOT / "datasets" / "processed" / "discovered_campaign_clusters.csv"

THRESHOLD = 0.50

if not INPUT.exists():
    raise FileNotFoundError(f"Missing similarity file: {INPUT}")

pairs = pd.read_csv(INPUT)

required = ["IOC_A", "IOC_B", "Similarity_Score"]
if any(c not in pairs.columns for c in required):
    raise ValueError(f"Input must contain columns: {required}")

# Union-Find: connect IOCs whose similarity meets the threshold.
parent = {}

def find(x):
    parent.setdefault(x, x)
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(a, b):
    root_a = find(a)
    root_b = find(b)
    if root_a != root_b:
        parent[root_b] = root_a

for _, row in pairs.iterrows():
    a, b = str(row["IOC_A"]), str(row["IOC_B"])
    find(a)
    find(b)

    if float(row["Similarity_Score"]) >= THRESHOLD:
        union(a, b)

# Collect connected components.
groups = {}
for ioc in parent:
    groups.setdefault(find(ioc), []).append(ioc)

# Give names only to groups with at least two IOCs.
clusters = []
cluster_number = 0

for members in sorted(groups.values(), key=lambda g: (-len(g), sorted(g)[0])):
    if len(members) >= 2:
        cluster_number += 1
        cluster_id = f"DISC-{cluster_number:02d}"
        status = "Candidate campaign"
    else:
        cluster_id = "UNCLUSTERED"
        status = "No match above threshold"

    for ioc in sorted(members):
        clusters.append({
            "IOC": ioc,
            "Discovered_Cluster_ID": cluster_id,
            "Cluster_Size": len(members),
            "Status": status,
            "Similarity_Threshold": THRESHOLD,
        })

result = pd.DataFrame(clusters).sort_values(
    ["Discovered_Cluster_ID", "IOC"]
)
result.to_csv(OUTPUT, index=False)

summary = (
    result.groupby(["Discovered_Cluster_ID", "Status", "Cluster_Size"])
    .size()
    .reset_index(name="IOC_Count")
)

print("\nDISCOVERED CAMPAIGN CLUSTERS")
print("=" * 45)
print(summary.to_string(index=False))
print(f"\nTotal IOCs: {len(result)}")
print(f"Candidate clusters: {cluster_number}")
print(f"Unclustered IOCs: {(result['Status'] == 'No match above threshold').sum()}")
print(f"Saved to: {OUTPUT}")
