
from pathlib import Path
from itertools import combinations

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "datasets" / "raw"
OUTPUT_DIR = ROOT / "datasets" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Locate the audited campaign-labelled dataset.
matches = list(DATA_DIR.glob("phishing ioc dataset campaign labeled.xlsx"))

if not matches:
    raise FileNotFoundError(
        f"Dataset not found in {DATA_DIR}\n"
        "Check the filename and datasets/raw folder."
    )

df = pd.read_excel(matches[0])
df.columns = df.columns.str.strip()

required = [
    "IOC", "IP", "ASN", "Registrar", "Cert_Fingerprint",
    "Favicon_Hash", "Kit_Fuzzy_Hash", "HTML_Similarity_Score",
    "Target_Sector", "Target_Region", "Lure_Theme",
    "Subdomain_Pattern"
]

missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")


def clean(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in {"", "-", "—", "unknown", "none", "nan", "n/a"}:
        return ""
    return value.lower()


# Feature weights: these are initial heuristic weights, not trained weights.
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

pairs = []

for i, j in combinations(range(len(df)), 2):
    a = df.iloc[i]
    b = df.iloc[j]

    score = 0.0
    evidence = []

    for column, weight in WEIGHTS.items():
        left = clean(a[column])
        right = clean(b[column])

        # Missing values are not treated as a match.
        if left and right and left == right:
            score += weight
            evidence.append(column)

    # HTML similarity is a numeric feature.
    # Similarity scores closer to one another add limited evidence.
    try:
        html_a = float(a["HTML_Similarity_Score"])
        html_b = float(b["HTML_Similarity_Score"])

        if pd.notna(html_a) and pd.notna(html_b):
            html_similarity = max(
                0.0, 1.0 - abs(html_a - html_b)
            )
            score += 0.02 * html_similarity

            if html_similarity >= 0.90:
                evidence.append("HTML_Similarity_Score")
    except (TypeError, ValueError):
        pass

    score = min(score, 1.0)

    if score >= 0.50:
        initial_assessment = "Strong candidate"
    elif score >= 0.30:
        initial_assessment = "Review candidate"
    else:
        initial_assessment = "Weak candidate"

    pairs.append({
        "IOC_A": str(a["IOC"]),
        "IOC_B": str(b["IOC"]),
        "Similarity_Score": round(score, 4),
        "Assessment": initial_assessment,
        "Matching_Evidence": ", ".join(evidence) if evidence else "None",
        "Ground_Truth_Same_Campaign": (
            int(
                clean(a.get("Campaign_ID", ""))
                == clean(b.get("Campaign_ID", ""))
                and clean(a.get("Campaign_ID", "")) != "unclustered"
            )
            if "Campaign_ID" in df.columns else None
        )
    })

result = pd.DataFrame(pairs)

# Highest-scoring pairs first.
result = result.sort_values(
    "Similarity_Score", ascending=False
)

output_file = OUTPUT_DIR / "campaign_pair_similarity.csv"
result.to_csv(output_file, index=False)

print("\nCAMPAIGN SIMILARITY ENGINE")
print("-" * 45)
print(f"IOCs analysed: {len(df)}")
print(f"IOC pairs compared: {len(result)}")
print(f"Strong candidates (score >= 0.50): "
      f"{(result['Similarity_Score'] >= 0.50).sum()}")
print(f"Review candidates (0.30–0.49): "
      f"{((result['Similarity_Score'] >= 0.30) & (result['Similarity_Score'] < 0.50)).sum()}")
print(f"Output saved to: {output_file}")

print("\nTOP 15 IOC PAIRS")
print(result.head(15).to_string(index=False))
