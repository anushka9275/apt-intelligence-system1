# DRDO APT Intelligence System

## Project Overview

The DRDO APT Intelligence System is a cybersecurity project focused on domain classification, phishing indicators, campaign discovery, and potential APT attribution.

The current work includes a trained domain-classification model, a React-based dashboard prototype, and Python scripts for campaign analysis. Integration between the frontend, backend, and machine-learning components is planned as a subsequent development step.

## Current Progress

- **Frontend:** React dashboard prototype with pages for IOC Search, Campaign Explorer, New Threat Analysis, and Relationship Graph.
- **Machine Learning:** Trained domain classifier saved as `model_artifacts/domain_classifier.joblib`.
- **Training and Testing:** Python scripts are available under `ml/classification/`.
- **Campaign Analysis:** Python scripts support campaign-profile construction, IOC matching, and conservative attribution checks.
- **Backend Integration:** Python API, Node.js backend, and MongoDB integration are pending.

## Domain Classification Model

The existing classifier uses character-level TF-IDF features and Logistic Regression to classify domain strings into two categories:

- `benign`
- `suspicious`

The trained pipeline is saved in Joblib format so it can be loaded for subsequent predictions without retraining.

### Dataset and Evaluation

The training dataset contains 625 labelled records:

| Label | Records |
|---|---:|
| Suspicious | 497 |
| Benign | 128 |
| Total | 625 |

The previously recorded test results reported 100% accuracy on a 125-record test split. However, subsequent manual tests incorrectly classified several legitimate, popular domains as suspicious. These results indicate that the model requires further validation and improvement before operational use.

**Important:** A model prediction is not a verified threat verdict. Predictions should be assessed alongside additional evidence and analyst review.

## Repository Structure

```text
drdo-apt-intelligence-system/
├── README.md
├── .gitignore
├── frontend/
├── ml/
│   ├── classification/
│   │   ├── train_domain_model.py
│   │   └── test_domain_model.py
│   ├── campaigns/
│   ├── attribution/
│   ├── common/
│   └── evaluation/
├── model_artifacts/
│   └── domain_classifier.joblib
└── reports/
```

Raw and processed datasets are intentionally excluded from this repository snapshot.

## Running the Existing Model

1. Install Python and create or activate a virtual environment.
2. Install the dependencies required by the project.
3. Ensure the saved model is present at `model_artifacts/domain_classifier.joblib`.
4. Use the existing testing script at `ml/classification/test_domain_model.py` to inspect predictions.

Run commands from the project root unless a script specifies otherwise.

## Planned Next Steps

1. Validate the classifier on representative benign and suspicious domains.
2. Investigate false positives and improve evaluation methodology.
3. Expose the existing model through a Python API.
4. Connect the React dashboard to the API.
5. Integrate campaign matching and evidence-based attribution.
6. Add a Node.js backend and MongoDB persistence.
7. Add appropriate logging, validation, and security controls.

## Data Handling

This repository does not include raw datasets. Project code, model artifacts, screenshots, and reports should only be shared with authorized reviewers and in accordance with applicable organizational requirements.
