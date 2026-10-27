
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[2]

DATASET = ROOT / "datasets" / "raw" / "phishing ioc dataset campaign labeled.xlsx"
OUTPUT = ROOT / "datasets" / "processed" / "heldout_campaign_evaluation.csv"

THRESHOLD = 0.50
MIN_STRONG_SIGNALS = 2

WEIGHTS = {
    "IP": 0.15,
    "ASN": 0.07,
    "Registrar": 0.03,
    "Cert_Fingerprint": 0.22,
    "Favicon_Hash": 0.18,
    "Kit_Fuzzy_Hash": 0.20,
    "Target_Sector": 0.03,
    "Target_Region": 0.03,
    "Lure_Theme": 0.04,
    "Subdomain_Pattern": 0.03,
}

STRONG_FIELDS = {
    "IP",
    "Cert_Fingerprint",
    "Favicon_Hash",
    "Kit_Fuzzy_Hash",
}


def valid(value):
    if value is None or pd.isna(value):
        return False

    text = str(value).strip()
    return text != "" and text.lower() not in {"nan", "none", "null"}


def same_value(a, b):
    if not valid(a) or not valid(b):
        return False

    return str(a).strip().casefold() == str(b).strip().casefold()


def compare_ioc(ioc, member):
    score = 0.0
    evidence = []
    strong_count = 0

    for field, weight in WEIGHTS.items():
        if same_value(ioc.get(field), member.get(field)):
            score += weight
            evidence.append(field)

            if field in STRONG_FIELDS:
                strong_count += 1

    # Small bonus for similar HTML similarity scores.
    a = ioc.get("HTML_Similarity_Score")
    b = member.get("HTML_Similarity_Score")

    if valid(a) and valid(b):
        try:
            a, b = float(a), float(b)
            score += 0.02 * max(0.0, 1.0 - abs(a - b))
        except (ValueError, TypeError):
            pass

    return score, evidence, strong_count


def main():
    if not DATASET.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET}")

    df = pd.read_excel(DATASET)

    required = {"IOC", "Campaign_ID"} | set(WEIGHTS)
    required.add("HTML_Similarity_Score")

    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.reset_index(drop=True)
    df["Campaign_ID"] = (
        df["Campaign_ID"].fillna("").astype(str).str.strip()
    )

    def has_campaign(campaign_id):
        return (
            campaign_id != ""
            and campaign_id.upper() != "UNCLUSTERED"
        )

    campaign_rows = df[df["Campaign_ID"].apply(has_campaign)]

    # Build reference profiles from the dataset's campaign labels.
    # For each campaign IOC, leave that IOC out of its own profile.
    profiles = {}

    for campaign_id, group in campaign_rows.groupby("Campaign_ID"):
        profiles[campaign_id] = [
            row.to_dict() for _, row in group.iterrows()
        ]

    results = []

    for idx, row in df.iterrows():
        ioc = row.to_dict()
        actual_id = str(row["Campaign_ID"]).strip()
        actual_positive = has_campaign(actual_id)

        candidates = []

        for campaign_id, members in profiles.items():
            best = {
                "score": 0.0,
                "evidence": [],
                "strong_count": 0,
                "member_ioc": "",
            }

            for member in members:
                # Prevent an IOC from matching itself.
                if str(member.get("IOC", "")).strip().casefold() == str(
                    ioc.get("IOC", "")
                ).strip().casefold():
                    continue

                score, evidence, strong_count = compare_ioc(ioc, member)

                if score > best["score"]:
                    best = {
                        "score": score,
                        "evidence": evidence,
                        "strong_count": strong_count,
                        "member_ioc": member.get("IOC", ""),
                    }

            candidates.append({
                "campaign_id": campaign_id,
                **best,
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = candidates[0] if candidates else {
            "campaign_id": "",
            "score": 0.0,
            "evidence": [],
            "strong_count": 0,
            "member_ioc": "",
        }

        predicted_match = (
            top["score"] >= THRESHOLD
            and top["strong_count"] >= MIN_STRONG_SIGNALS
        )

        predicted_id = top["campaign_id"] if predicted_match else ""

        results.append({
            "IOC": ioc.get("IOC", ""),
            "Actual_Campaign_ID": actual_id,
            "Actual_Campaign": int(actual_positive),
            "Predicted_Match": int(predicted_match),
            "Predicted_Campaign_ID": predicted_id,
            "Correct_Campaign_Assignment": int(
                actual_positive
                and predicted_match
                and predicted_id == actual_id
            ),
            "Top_Score": round(top["score"], 4),
            "Strong_Signals": top["strong_count"],
            "Matching_Evidence": ", ".join(top["evidence"]),
            "Matched_Profile_IOC": top["member_ioc"],
        })

    result = pd.DataFrame(results)
    y_true = result["Actual_Campaign"]
    y_pred = result["Predicted_Match"]

    print("\nHELD-OUT CAMPAIGN MATCHING EVALUATION")
    print("=" * 45)
    print(f"Total IOCs tested: {len(result)}")
    print(f"Campaign IOCs: {int(y_true.sum())}")
    print(f"Unclustered IOCs: {int((y_true == 0).sum())}")
    print(f"Predicted campaign matches: {int(y_pred.sum())}")

    print("\nBinary match-detection metrics:")
    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_true, y_pred, zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_true, y_pred, zero_division=0):.4f}")

    print("\nConfusion matrix [[TN, FP], [FN, TP]]:")
    print(confusion_matrix(y_true, y_pred, labels=[0, 1]))

    campaign_results = result[result["Actual_Campaign"] == 1]
    if len(campaign_results):
        assignment_rate = campaign_results[
            "Correct_Campaign_Assignment"
        ].mean()

        print(
            "\nCorrect campaign assignment rate among known campaign IOCs: "
            f"{assignment_rate:.4f}"
        )

    result.to_csv(OUTPUT, index=False)
    print(f"\nDetailed results saved to: {OUTPUT}")
    print(
        "\nNote: This is leave-one-out testing on a small, labelled dataset. "
        "It is more informative than profile coverage, but it is not "
        "independent validation on genuinely new campaigns."
    )


if __name__ == "__main__":
    main()
