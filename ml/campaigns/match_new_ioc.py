
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROFILE_FILE = ROOT / "datasets" / "processed" / "campaign_profiles.json"
INPUT_FILE = ROOT / "datasets" / "processed" / "new_ioc.json"
OUTPUT_FILE = ROOT / "datasets" / "processed" / "new_ioc_match_result.json"

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

NUMERIC_FEATURES = {"HTML_Similarity_Score", "Domain_Age_Days"}

def clean(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None

    value = str(value).strip()
    if value.lower() in {
        "", "-", "—", "unknown", "none", "nan", "n/a"
    }:
        return None
    return value.lower()

def numeric(value):
    try:
        result = float(value)
        if pd.isna(result):
            return None
        return result
    except (TypeError, ValueError):
        return None

def compare_member(new_ioc, member):
    score = 0.0
    evidence = []
    strong_evidence_count = 0

    for feature, weight in WEIGHTS.items():
        new_value = clean(new_ioc.get(feature))
        old_value = clean(member.get(feature))

        if new_value is None or old_value is None:
            continue

        if new_value == old_value:
            score += weight
            evidence.append(feature)

            if feature in {
                "IP",
                "Cert_Fingerprint",
                "Favicon_Hash",
                "Kit_Fuzzy_Hash",
            }:
                strong_evidence_count += 1

    new_html = numeric(new_ioc.get("HTML_Similarity_Score"))
    old_html = numeric(member.get("HTML_Similarity_Score"))

    if new_html is not None and old_html is not None:
        # Assumes HTML similarity scores are normalized to 0–1.
        closeness = max(0.0, 1.0 - abs(new_html - old_html))
        score += 0.02 * closeness

        if closeness >= 0.90:
            evidence.append("HTML_Similarity_Score")

    return {
        "score": round(min(score, 1.0), 4),
        "evidence": evidence,
        "strong_evidence_count": strong_evidence_count,
    }

def main():
    if not PROFILE_FILE.exists():
        raise FileNotFoundError(
            f"Campaign profiles not found: {PROFILE_FILE}"
        )

    # Create an input template on the first run.
    if not INPUT_FILE.exists():
        template = {
            "IOC": "replace-with-domain-or-url",
            "IP": None,
            "ASN": None,
            "Registrar": None,
            "Cert_Fingerprint": None,
            "Favicon_Hash": None,
            "Kit_Fuzzy_Hash": None,
            "HTML_Similarity_Score": None,
            "Domain_Age_Days": None,
            "Target_Sector": None,
            "Target_Region": None,
            "Lure_Theme": None,
            "Subdomain_Pattern": None,
        }

        INPUT_FILE.write_text(
            json.dumps(template, indent=2),
            encoding="utf-8",
        )

        print(f"Input template created: {INPUT_FILE}")
        print("Fill in the available IOC enrichment values,")
        print("save the file, and run this script again.")
        return

    new_ioc = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    if not new_ioc.get("IOC") or new_ioc["IOC"] == "replace-with-domain-or-url":
        raise ValueError("Set IOC to the domain or URL being investigated.")

    with open(PROFILE_FILE, encoding="utf-8") as file:
        profiles = json.load(file)

    results = []

    for profile in profiles:
        best_member = None

        for member in profile["members"]:
            comparison = compare_member(new_ioc, member)

            if (
                best_member is None
                or comparison["score"] > best_member["score"]
            ):
                best_member = {
                    **comparison,
                    "matched_member": member["IOC"],
                }

        if best_member is not None:
            results.append({
                "campaign_profile_id": profile["campaign_profile_id"],
                **best_member,
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    if not results:
        raise ValueError("No campaign profiles were available for comparison.")

    best = results[0]

    # Conservative initial rule; this is not a calibrated probability.
    if best["score"] >= 0.50 and best["strong_evidence_count"] >= 2:
        status = "Candidate campaign match"
    else:
        status = "No established campaign match"

    output = {
        "IOC": new_ioc["IOC"],
        "status": status,
        "threshold": 0.50,
        "note": (
            "Similarity scores are heuristic, not probabilities. "
            "A candidate match requires review; no match does not mean benign."
        ),
        "top_match": best,
        "ranked_candidates": results,
    }

    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nNEW IOC CAMPAIGN MATCH")
    print("=" * 45)
    print(f"IOC: {output['IOC']}")
    print(f"Result: {status}")
    print(f"Top candidate: {best['campaign_profile_id']}")
    print(f"Similarity score: {best['score']:.4f}")
    print(f"Matched profile IOC: {best['matched_member']}")
    print(f"Matching evidence: {best['evidence']}")
    print(f"Strong matching signals: {best['strong_evidence_count']}")

    print("\nTOP 3 CANDIDATES")
    for item in results[:3]:
        print(
            f"{item['campaign_profile_id']}: "
            f"score={item['score']:.4f}, "
            f"evidence={item['evidence']}"
        )

    print(f"\nFull result saved to: {OUTPUT_FILE}")

def match_ioc(new_ioc):
    if not PROFILE_FILE.exists():
        raise FileNotFoundError(
            f"Campaign profiles not found: {PROFILE_FILE}"
        )

    if not new_ioc.get("IOC"):
        raise ValueError("Set IOC to the domain or URL being investigated.")

    with open(PROFILE_FILE, encoding="utf-8") as file:
        profiles = json.load(file)

    results = []

    for profile in profiles:
        best_member = None

        for member in profile["members"]:
            comparison = compare_member(new_ioc, member)

            if (
                best_member is None
                or comparison["score"] > best_member["score"]
            ):
                best_member = {
                    **comparison,
                    "matched_member": member["IOC"],
                }

        if best_member is not None:
            results.append({
                "campaign_profile_id": profile["campaign_profile_id"],
                **best_member,
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    if not results:
        raise ValueError(
            "No campaign profiles were available for comparison."
        )

    best = results[0]

    if (
        best["score"] >= 0.50
        and best["strong_evidence_count"] >= 2
    ):
        status = "Candidate campaign match"
    else:
        status = "No established campaign match"

    return {
        "IOC": new_ioc["IOC"],
        "status": status,
        "threshold": 0.50,
        "note": (
            "Similarity scores are heuristic, not probabilities. "
            "A candidate match requires review; no match does not mean benign."
        ),
        "top_match": best,
        "ranked_candidates": results,
    }


if __name__ == "__main__":
    main()