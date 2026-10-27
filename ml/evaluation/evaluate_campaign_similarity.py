
from pathlib import Path
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "datasets" / "processed" / "campaign_pair_similarity.csv"

if not INPUT.exists():
    raise FileNotFoundError(f"Could not find: {INPUT}")

df = pd.read_csv(INPUT)

required = ["Similarity_Score", "Ground_Truth_Same_Campaign"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df.dropna(subset=required).copy()
y_true = df["Ground_Truth_Same_Campaign"].astype(int)

print("\nCAMPAIGN SIMILARITY EVALUATION")
print("=" * 45)
print(f"Pairs evaluated: {len(df)}")
print(f"Same-campaign pairs: {int(y_true.sum())}")
print(f"Different-campaign pairs: {int((y_true == 0).sum())}")

for threshold in [0.30, 0.50, 0.60, 0.70]:
    y_pred = (df["Similarity_Score"] >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true, y_pred, labels=[0, 1]
    ).ravel()

    print(f"\n--- Threshold: {threshold:.2f} ---")
    print(f"True positives:  {tp}")
    print(f"False positives: {fp}")
    print(f"True negatives:  {tn}")
    print(f"False negatives: {fn}")
    print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.3f}")
    print(f"Recall:    {recall_score(y_true, y_pred, zero_division=0):.3f}")
    print(f"F1-score:  {f1_score(y_true, y_pred, zero_division=0):.3f}")

print("\nEVALUATION COMPLETE")
print("These results measure agreement with existing dataset labels.")
print("They do not independently verify real-world campaign membership.")
