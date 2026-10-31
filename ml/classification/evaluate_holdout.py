
from pathlib import Path
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "datasets" / "raw" / "suspicious_domains_dataset first order.csv"

df = pd.read_csv(DATA_FILE)
df = df[["domain", "label", "category", "tld"]].dropna().copy()

for col in ["domain", "label", "category", "tld"]:
    df[col] = df[col].astype(str).str.strip().str.lower()

df = df[
    (df["domain"] != "") &
    (df["label"] != "")
].drop_duplicates(subset=["domain"])

X = df["domain"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

model = Pipeline([
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

model.fit(X_train, y_train)
pred = model.predict(X_test)

test = df.loc[X_test.index].copy()
test["predicted"] = pred

print("\nHOLDOUT CLASSIFICATION REPORT")
print(classification_report(y_test, pred, zero_division=0))

print("\nHOLDOUT CONFUSION MATRIX")
print(confusion_matrix(y_test, pred, labels=model.classes_))
print("Label order:", model.classes_)

print("\nHOLDOUT RESULTS BY CATEGORY")
print(pd.crosstab(
    test["category"], test["label"],
    margins=True
).to_string())

print("\nHOLDOUT PREDICTIONS BY TLD")
print(pd.crosstab(
    [test["tld"], test["label"]],
    test["predicted"]
).to_string())

print("\nMISCLASSIFIED TEST DOMAINS")
errors = test[test["label"] != test["predicted"]]
print(errors[["domain", "label", "predicted", "category", "tld"]].to_string(index=False))

print(f"\nHoldout records: {len(test)}")
print(f"Misclassified: {len(errors)}")
