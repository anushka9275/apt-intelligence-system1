
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "datasets" / "raw" / "phishing ioc dataset campaign labeled.xlsx"
PROFILES = ROOT / "datasets" / "processed" / "campaign_profiles.json"
OUTPUT = ROOT / "datasets" / "processed" / "campaign_evaluation_results.csv"

def main():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")

    if not PROFILES.exists():
        raise FileNotFoundError(f"Campaign profiles not found: {PROFILES}")

    df = pd.read_excel(DATASET)

    required = {"IOC", "Campaign_ID"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Ground truth: IOCs assigned to a campaign are positive;
    # UNCLUSTERED / blank campaign IDs are treated as not assigned.
    df["Campaign_ID"] = df["Campaign_ID"].fillna("").astype(str).str.strip()
    df["Actual_Campaign"] = (
        (df["Campaign_ID"] != "")
        & (df["Campaign_ID"].str.upper() != "UNCLUSTERED")
    )

    # Profile membership: IOCs present in the campaign profiles.
    import json
    profiles = json.loads(PROFILES.read_text(encoding="utf-8"))

    profile_iocs = set()
    for profile in profiles:
        for member in profile.get("members", []):
            ioc = str(member.get("IOC", "")).strip().lower()
            if ioc:
                profile_iocs.add(ioc)

    df["IOC_Normalized"] = df["IOC"].astype(str).str.strip().str.lower()
    df["In_Profile"] = df["IOC_Normalized"].isin(profile_iocs)

    # This measures profile coverage, NOT unseen-IOC matching accuracy.
    y_true = df["Actual_Campaign"].astype(int)
    y_pred = df["In_Profile"].astype(int)

    print("\nCAMPAIGN PROFILE COVERAGE EVALUATION")
    print("=" * 45)
    print(f"Dataset rows: {len(df)}")
    print(f"Ground-truth campaign IOCs: {int(y_true.sum())}")
    print(f"Ground-truth unclustered IOCs: {int((y_true == 0).sum())}")
    print(f"IOCs found in profiles: {int(y_pred.sum())}")
    print(f"IOCs not found in profiles: {int((y_pred == 0).sum())}")

    print("\nCoverage metrics:")
    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_true, y_pred, zero_division=0):.4f}")

    print("\nConfusion matrix [ [TN, FP], [FN, TP] ]:")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1]))

    print("\nClassification report:")
    print(classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["Unclustered", "Campaign"],
        zero_division=0,
    ))

    df.to_csv(OUTPUT, index=False)
    print(f"\nDetailed results saved to: {OUTPUT}")
    print(
        "\nIMPORTANT: These results measure profile coverage on the same "
        "dataset used to build profiles. They are not independent "
        "generalization metrics for genuinely new IOCs."
    )

if __name__ == "__main__":
    main()
