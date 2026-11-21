
import json
from pathlib import Path

import pandas as pd


# Project paths
ROOT = Path(__file__).resolve().parents[2]

DATASET_PATH = (
    ROOT / "datasets" / "raw"
    / "phishing ioc dataset campaign labeled.xlsx"
)

MATCH_RESULT_PATH = (
    ROOT / "datasets" / "processed"
    / "new_ioc_match_result.json"
)

OUTPUT_PATH = (
    ROOT / "datasets" / "processed"
    / "new_ioc_attribution_result.json"
)


def is_missing(value):
    """Check for missing spreadsheet values."""
    return pd.isna(value) or str(value).strip() == ""


def clean(value, default=""):
    """Convert a spreadsheet value into clean text."""
    if is_missing(value):
        return default
    return str(value).strip()


def attribute_campaign(match_result):
    # 1. Load the existing campaign match result.

    ioc = match_result.get("IOC", "Unknown IOC")
    match_status = match_result.get("status", "")
    top_match = match_result.get("top_match") or {}

    # Default output: do not attribute without sufficient evidence.
    result = {
        "IOC": ioc,
        "campaign_match_status": match_status,
        "campaign_profile_id": top_match.get("campaign_profile_id"),
        "campaign_similarity_score": top_match.get("score"),
        "attribution_status": "Unknown",
        "candidate_actor": None,
        "dataset_attribution_confidence": None,
        "attribution_rationale": [],
        "matched_member": top_match.get("matched_member"),
        "warning": (
            "Attribution is a candidate assessment based on dataset labels, "
            "not independently verified actor identification."
        ),
    }

    # 2. A weak or absent campaign match must not produce actor attribution.
    if match_status != "Candidate campaign match":
        result["attribution_status"] = (
            "Insufficient Evidence — No Established Campaign Match"
        )
        result["attribution_rationale"] = [
            "The campaign matcher did not establish a campaign match.",
            "The top-ranked candidate, if present, is an unconfirmed lead.",
            "No APT actor has been attributed to this IOC.",
        ]
        return result

    # 3. Load the original labelled campaign dataset.
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Campaign dataset not found: {DATASET_PATH}"
        )

    data = pd.read_excel(DATASET_PATH)

    required_columns = [
        "IOC",
        "Campaign_ID",
        "Campaign_Label",
        "Attributed_Actor",
        "Attribution_Confidence",
        "Attribution_Rationale",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required dataset columns: {missing_columns}"
        )

    # The matcher provides a member IOC from the discovered profile.
    matched_member = clean(top_match.get("matched_member"))

    if not matched_member:
        result["attribution_status"] = (
            "Insufficient Evidence — Matched Member Missing"
        )
        result["attribution_rationale"] = [
            "The candidate match has no matched-member IOC to cross-reference."
        ]
        return result
     

    # 4. Find the corresponding labelled IOC in the source dataset.
    data["_IOC_NORMALIZED"] = (
        data["IOC"].fillna("").astype(str).str.strip().str.lower()
    )

    member_rows = data[
        data["_IOC_NORMALIZED"] == matched_member.lower()
    ]

    if member_rows.empty:
        result["attribution_status"] = (
            "Insufficient Evidence — No Labelled Reference"
        )
        result["attribution_rationale"] = [
            "The matched member was not found in the labelled source dataset.",
            "No actor attribution was made.",
        ]
        return result
     

    # Use the reference member's campaign label.
    reference = member_rows.iloc[0]
    campaign_id = clean(reference["Campaign_ID"])
    campaign_label = clean(reference["Campaign_Label"])

    result["reference_campaign_id"] = campaign_id
    result["reference_campaign_label"] = campaign_label

    # Unclustered records must never be attributed to a named actor.
    if not campaign_id or campaign_id.upper() == "UNCLUSTERED":
        result["attribution_status"] = (
            "Insufficient Evidence — Campaign Not Established"
        )
        result["attribution_rationale"] = [
            "The matched reference is labelled UNCLUSTERED.",
            "No named actor was assigned.",
        ]
        return result
       

    campaign_rows = data[
        data["Campaign_ID"].fillna("").astype(str).str.strip()
        == campaign_id
    ]

    actors = [
        clean(value)
        for value in campaign_rows["Attributed_Actor"].tolist()
        if not is_missing(value)
    ]

    # Do not guess if the campaign contains conflicting actor labels.
    unique_actors = set(actors)

    if len(unique_actors) != 1:
        result["attribution_status"] = (
            "Insufficient Evidence — Conflicting Actor Labels"
        )
        result["attribution_rationale"] = [
            "The source dataset does not provide one consistent actor label.",
            "Manual analyst review is required.",
        ]
        return result
    

    actor = next(iter(unique_actors))

    # Treat explicit unattributed/unknown labels as no attribution.
    if (
        "unattributed" in actor.lower()
        or actor.lower() in {"unknown", "none", "nan"}
    ):
        result["attribution_status"] = (
            "Unattributed Campaign — Actor Unknown"
        )
        result["attribution_rationale"] = [
            f"The reference campaign is labelled '{actor}'.",
            "Campaign membership does not establish APT identity.",
        ]
        return result
    

    # 5. Preserve the most conservative confidence label in this campaign.
    confidence_rank = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    confidence_values = [
        clean(value).lower()
        for value in campaign_rows["Attribution_Confidence"].tolist()
        if not is_missing(value)
    ]

    if confidence_values:
        lowest_confidence = min(
            confidence_values,
            key=lambda value: confidence_rank.get(value, 0),
        )
        confidence = lowest_confidence.title()
    else:
        confidence = None

    # Collect distinct dataset-provided rationale statements.
    rationales = []
    for value in campaign_rows["Attribution_Rationale"].tolist():
        text = clean(value)
        if text and text not in rationales:
            rationales.append(text)

    result["candidate_actor"] = actor
    result["dataset_attribution_confidence"] = confidence
    result["attribution_rationale"] = rationales[:5]

    # Always retain the candidate/review distinction.
    result["attribution_status"] = (
        "Candidate Attribution — Analyst Review Required"
    )

    return result

def main():
    if not MATCH_RESULT_PATH.exists():
        raise FileNotFoundError(
            f"Campaign match result not found: {MATCH_RESULT_PATH}"
        )

    with open(MATCH_RESULT_PATH, "r", encoding="utf-8") as file:
        match_result = json.load(file)

    result = attribute_campaign(match_result)
    save_result(result)

def save_result(result):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("\n=== APT ATTRIBUTION RESULT ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
