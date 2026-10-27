
from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)

# 1. Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "datasets"
    / "raw"
    / "suspicious_domains_dataset first order.csv"
)

MODEL_DIR = PROJECT_ROOT / "model_artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILE = MODEL_DIR / "domain_classifier.joblib"

# 2. Load dataset
df = pd.read_csv(DATA_FILE)

required_columns = {"domain", "label"}
if not required_columns.issubset(df.columns):
    raise ValueError(
        f"Missing required columns. Found: {df.columns.tolist()}"
    )

df = df[["domain", "label"]].dropna()
df["domain"] = df["domain"].astype(str).str.strip().str.lower()
df["label"] = df["label"].astype(str).str.strip().str.lower()

# Remove invalid/empty domain or label values
df = df[
    (df["domain"] != "")
    & (df["label"] != "")
].copy()

# Check the labels before training
print("\nLABEL COUNTS:")

print("\nLABEL DISTRIBUTION:")
print(df["label"].value_counts())

print("\nLABEL PROPORTIONS:")
print(df["label"].value_counts(normalize=True).round(3))

print(df["label"].value_counts())

expected_labels = {"benign", "suspicious"}
actual_labels = set(df["label"].unique())

if actual_labels != expected_labels:
    raise ValueError(
        f"Expected labels {expected_labels}, "
        f"but found {actual_labels}. Inspect the labels first."
    )

# 3. Remove exact duplicate domain entries
df = df.drop_duplicates(subset=["domain"])

X = df["domain"]
y = df["label"]

# Each class needs enough records for a stratified split
if y.value_counts().min() < 2:
    raise ValueError("Not enough examples in one of the classes.")

# 4. Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"\nTotal records: {len(df)}")
print(f"Training records: {len(X_train)}")
print(f"Testing records: {len(X_test)}")

# 5. Build the baseline model
model = Pipeline([
    (
        "vectorizer",
        TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 5),
            min_df=1,
            sublinear_tf=True
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42
        )
    )
])

# 6. Train
model.fit(X_train, y_train)

# 7. Evaluate on held-out test data
predictions = model.predict(X_test)

print("\nACCURACY:")
print(round(accuracy_score(y_test, predictions), 4))

print("\nCLASSIFICATION REPORT:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

print("\nCONFUSION MATRIX:")
print("Label order:", model.classes_)
print(confusion_matrix(
    y_test,
    predictions,
    labels=model.classes_
))

# 8. Save the trained model and its preprocessing pipeline
joblib.dump(model, MODEL_FILE)

print(f"\nModel saved to: {MODEL_FILE}")
