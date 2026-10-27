
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FILE = ROOT / "datasets" / "raw" / "suspicious_domains_dataset first order.csv"

df = pd.read_csv(FILE)
df["domain"] = df["domain"].astype(str).str.lower().str.strip()
df["label"] = df["label"].astype(str).str.lower().str.strip()
df = df.drop_duplicates(subset=["domain"])

print("\n1. LABEL COUNTS")
print(df["label"].value_counts())

for col in ["category", "technique", "tld"]:
    print(f"\n2. LABEL DISTRIBUTION BY {col.upper()}")
    print(pd.crosstab(df[col], df["label"], margins=True))

print("\n3. EXAMPLE BENIGN DOMAINS")
print(
    df.loc[df["label"] == "benign", "domain"]
    .head(15).to_string(index=False)
)

print("\n4. EXAMPLE SUSPICIOUS DOMAINS")
print(
    df.loc[df["label"] == "suspicious", "domain"]
    .head(15).to_string(index=False)
)

print("\n5. SUSPICIOUS LABELS BY TECHNIQUE")
print(
    df.loc[df["label"] == "suspicious", "technique"]
    .value_counts(dropna=False)
)

print("\n6. DOMAIN LABELS BY TLD")
print(
    df.groupby("tld")["label"]
    .value_counts(normalize=True)
    .round(3)
)
