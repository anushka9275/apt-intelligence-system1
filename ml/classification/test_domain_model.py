
from pathlib import Path
import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_FILE = PROJECT_ROOT / "model_artifacts" / "domain_classifier.joblib"

# Load the saved model
model = joblib.load(MODEL_FILE)

# Test domains (examples only; predictions are not ground truth)
test_domains = [
    "google.com",
    "wikipedia.org",
    "myntra-secure-login.com",
    "secure-mod-gov.in.example",
    "random-login-verify-9281.xyz"
]

# Predict labels and class probabilities
predictions = model.predict(test_domains)
probabilities = model.predict_proba(test_domains)

results = []

for domain, prediction, probs in zip(
    test_domains, predictions, probabilities
):
    class_probabilities = dict(zip(model.classes_, probs))

    results.append({
        "Domain": domain,
        "Predicted_Label": prediction,
        "Benign_Score": round(
            float(class_probabilities.get("benign", 0)), 4
        ),
        "Suspicious_Score": round(
            float(class_probabilities.get("suspicious", 0)), 4
        )
    })

print("\nMODEL TEST RESULTS")
print(pd.DataFrame(results).to_string(index=False))

print("\nNote: These are model predictions, not verified threat verdicts.")
