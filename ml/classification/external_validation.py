
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "model_artifacts" / "domain_classifier.joblib"

model = joblib.load(MODEL_PATH)

# Known mainstream domains for a basic sanity check.
# Verify these labels before using this list in formal evaluation.
domains = [
    "google.com",
    "wikipedia.org",
    "microsoft.com",
    "apple.com",
    "amazon.com",
    "bbc.com",
    "github.com",
    "mit.edu",
    "gov.uk",
    "nic.in",
    "flipkart.com",
    "myntra.com",
    "linkedin.com",
    "youtube.com",
    "cloudflare.com",
]

predictions = model.predict(domains)
probabilities = model.predict_proba(domains)

rows = []

for domain, prediction, scores in zip(
    domains, predictions, probabilities
):
    score_map = dict(zip(model.classes_, scores))

    rows.append({
        "domain": domain,
        "predicted_label": prediction,
        "benign_score": round(
            float(score_map.get("benign", 0)), 4
        ),
        "suspicious_score": round(
            float(score_map.get("suspicious", 0)), 4
        ),
    })

results = pd.DataFrame(rows)
print(results.to_string(index=False))

output_path = ROOT / "reports" / "external_validation.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)
results.to_csv(output_path, index=False)

print(f"\nResults saved to: {output_path}")
