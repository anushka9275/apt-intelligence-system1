
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = (
    ROOT / "datasets" / "raw"
    / "phishing ioc dataset campaign labeled.xlsx"
)

df = pd.read_excel(DATA_FILE)

print("=" * 65)
print("CAMPAIGN DISCOVERY DATASET AUDIT")
print("=" * 65)

print("\n1. DATASET SHAPE")
print(df.shape)

print("\n2. AVAILABLE COLUMNS")
for col in df.columns:
    print("-", col)

print("\n3. CAMPAIGN LABEL COUNTS")
for col in ["Is_Campaign", "Campaign_Status", "Campaign_Label"]:
    if col in df.columns:
        print(f"\n{col}:")
        print(df[col].fillna("MISSING").value_counts().to_string())

print("\n4. UNIQUE CAMPAIGN IDS")
if "Campaign_ID" in df.columns:
    print("Unique IDs:", df["Campaign_ID"].nunique(dropna=True))
    print(df["Campaign_ID"].fillna("MISSING").value_counts().to_string())

print("\n5. CLUSTER DISTRIBUTION")
if "Cluster_ID" in df.columns:
    print(df["Cluster_ID"].fillna("UNCLUSTERED").value_counts().to_string())

print("\n6. APT ATTRIBUTION COUNTS")
if "Attributed_Actor" in df.columns:
    print(df["Attributed_Actor"].fillna("UNKNOWN").value_counts().to_string())

print("\n7. MISSING VALUES IN IMPORTANT COLUMNS")
important = [
    "IOC", "IP", "ASN", "Cert_Fingerprint",
    "Favicon_Hash", "HTML_Similarity_Score",
    "Kit_Fuzzy_Hash", "First_Seen",
    "Cluster_ID", "Is_Campaign", "Campaign_ID",
    "Campaign_Label", "Campaign_Basis",
    "Campaign_Confidence", "Attributed_Actor"
]

for col in important:
    if col in df.columns:
        print(f"{col}: {df[col].isna().sum()} missing")

print("\n8. DUPLICATE IOC VALUES")
if "IOC" in df.columns:
    print("Duplicate IOC rows:", df["IOC"].duplicated().sum())

print("\n9. SAMPLE IOC AND CAMPAIGN LABELS")
show = [
    c for c in [
        "IOC", "IP", "Cert_Fingerprint", "Favicon_Hash",
        "Cluster_ID", "Is_Campaign", "Campaign_ID",
        "Campaign_Label", "Campaign_Confidence",
        "Attributed_Actor"
    ] if c in df.columns
]
print(df[show].head(10).to_string(index=False))

print("\nAudit complete.")
