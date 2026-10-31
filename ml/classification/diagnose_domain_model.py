
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import classification_report

ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = ROOT / "model_artifacts" / "domain_classifier.joblib"
DATA_PATH = ROOT / "datasets" / "raw" / "suspicious_domains_dataset first order.csv"

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_PATH)

df = df[["domain", "label", "tld"]].dropna().copy()

for col in ["domain", "label", "tld"]:
    df[col] = df[col].astype(str).str.strip().str.lower()

df = df.drop_duplicates(subset=["domain"])
df["predicted"] = model.predict(df["domain"])

print("\nOVERALL REPORT")
print(classification_report(
    df["label"], df["predicted"], zero_division=0
))

print("\nCONFUSION MATRIX BY TLD")
print(pd.crosstab(
    [df["tld"], df["label"]], df["predicted"]
).to_string())

print("\nMISCLASSIFIED DOMAINS")
errors = df[df["label"] != df["predicted"]]
print(errors.to_string(index=False))

print(f"\nTotal records evaluated: {len(df)}")
print(f"Misclassified records: {len(errors)}")
