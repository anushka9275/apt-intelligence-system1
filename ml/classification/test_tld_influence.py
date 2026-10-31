
from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "datasets" / "raw" / "suspicious_domains_dataset first order.csv"

df = pd.read_csv(DATA_FILE)[["domain", "label"]].dropna().copy()
df["domain"] = df["domain"].astype(str).str.strip().str.lower()
df["label"] = df["label"].astype(str).str.strip().str.lower()
df = df[(df["domain"] != "") & (df["label"] != "")]
df = df.drop_duplicates(subset="domain")

X_train, X_test, y_train, y_test = train_test_split(
    df["domain"],
    df["label"],
    test_size=0.20,
    random_state=42,
    stratify=df["label"]
)

def build_model():
    return Pipeline([
        ("vectorizer", TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 5),
            min_df=1,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        ))
    ])

# Baseline: original domains
baseline = build_model()
baseline.fit(X_train, y_train)
baseline_pred = baseline.predict(X_test)

# Diagnostic: replace the final DNS label with .com
def normalize_tld(domain):
    parts = domain.split(".")
    if len(parts) < 2:
        return domain
    return ".".join(parts[:-1]) + ".com"

X_train_normalized = X_train.map(normalize_tld)
X_test_normalized = X_test.map(normalize_tld)

normalized_model = build_model()
normalized_model.fit(X_train_normalized, y_train)
normalized_pred = normalized_model.predict(X_test_normalized)

print("BASELINE ACCURACY:", round(
    accuracy_score(y_test, baseline_pred), 4
))
print("TLD-NORMALIZED ACCURACY:", round(
    accuracy_score(y_test, normalized_pred), 4
))

print("\nTLD-NORMALIZED REPORT")
print(classification_report(
    y_test, normalized_pred, zero_division=0
))

print("\nCHANGED PREDICTIONS AFTER NORMALIZATION")
results = pd.DataFrame({
    "domain": X_test,
    "true_label": y_test,
    "baseline_prediction": baseline_pred,
    "normalized_prediction": normalized_pred
})
changed = results[
    results["baseline_prediction"] != results["normalized_prediction"]
]
print(changed.to_string(index=False))
print("\nChanged predictions:", len(changed))
