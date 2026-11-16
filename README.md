# APT Intelligence System

## Project Overview

The **APT Intelligence System** is a cybersecurity platform designed to support domain classification, phishing IOC analysis, campaign discovery, IOC correlation, and potential Advanced Persistent Threat (APT) attribution.

The system combines machine learning, campaign-profile matching, and an interactive React dashboard to help analysts investigate suspicious indicators and identify possible relationships with previously observed campaigns.

## Key Features

- **IOC Search:** Analyse domain indicators using the trained domain-classification model.
- **Campaign Explorer:** Explore discovered campaign profiles and their associated IOCs.
- **New Threat Analysis:** Submit a new IOC with enrichment information and compare it against existing campaign profiles.
- **Relationship Graph:** Visualise relationships between threat indicators and campaigns.
- **Domain Classification:** Classify domain strings as benign or suspicious.
- **Campaign Matching:** Identify potential campaign matches using IOC enrichment and similarity-based evidence.
- **Potential APT Attribution:** Present candidate threat-actor associations with supporting evidence.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend API | Python, FastAPI |
| Machine Learning | Scikit-learn |
| Model Storage | Joblib |
| Data Processing | Pandas, NumPy |
| Frontend Package Management | npm |

## Project Structure

```text
apt-intelligence-system/
│
├── api/
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── ml/
│   ├── classification/
│   ├── campaigns/
│   │   └── match_new_ioc.py
│   ├── attribution/
│   ├── common/
│   └── evaluation/
│
├── model_artifacts/
│   └── domain_classifier.joblib
│
├── datasets/
│   └── processed/
│       └── campaign_profiles.json
│
├── requirements.txt
├── .gitignore
└── README.md
```

Some training datasets, intermediate results, and evaluation files are excluded from the repository. The campaign profile JSON and trained domain-classification model required by the current API are included.

## Prerequisites

Install the following software before running the project:

- Python 3.14
- Node.js and npm
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/anushka9275/apt-intelligence-system1.git
```

Navigate into the project:

```bash
cd apt-intelligence-system1
```

### 2. Set Up the Python Backend

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start the backend from the project root:

```bash
python -m uvicorn api.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### 3. Set Up the React Frontend

Open a second terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm ci
```

Start the development server:

```bash
npm run dev
```

Open the URL displayed by Vite, usually:

```text
http://localhost:5173
```

Keep both terminals running while using the application.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API home |
| GET | `/health` | Backend health check |
| GET | `/campaigns` | Retrieve campaign profiles |
| POST | `/predict` | Domain classification |
| POST | `/campaign-match` | Match a new IOC against campaign profiles |

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Machine Learning Components

### Domain Classification

The domain-classification component uses character-level TF-IDF features and Logistic Regression.

It classifies domain strings into:

- `benign`
- `suspicious`

The trained model is stored at:

```text
model_artifacts/domain_classifier.joblib
```

The current dataset contains 625 labelled records:

| Label | Records |
|---|---:|
| Suspicious | 497 |
| Benign | 128 |
| Total | 625 |

The previously recorded evaluation reported 100% accuracy on a 125-record test split. However, subsequent manual testing identified false positives involving legitimate popular domains.

**Important:** Predictions are preliminary indicators, not verified threat verdicts. The model requires further validation before operational deployment.

### Campaign Discovery and Matching

The campaign-analysis component uses IOC enrichment and similarity-based comparisons to identify potential relationships between new indicators and existing campaign profiles.

Enrichment attributes include:

- IP address and ASN
- Registrar
- Certificate fingerprint
- Domain age
- Favicon hash
- HTML similarity
- Kit fuzzy hash
- Target sector and region
- Lure theme
- Subdomain patterns

The API compares submitted indicators against available campaign profiles and returns ranked candidates with similarity scores and supporting evidence.

Similarity scores are heuristic measures, not probabilities. A candidate match does not establish confirmed campaign membership or threat-actor attribution. Analyst verification is required.

## Testing the Application

1. Start the backend.
2. Start the frontend.
3. Open the React dashboard.
4. Test domain classification through IOC Search.
5. Open Campaign Explorer to inspect campaign profiles.
6. Submit an IOC through New Threat Analysis.
7. Review ranked campaign candidates and supporting evidence.
8. Use `/docs` to test backend endpoints independently.

## Current Limitations

- The domain classifier requires additional validation and false-positive reduction.
- Campaign matching relies on available campaign profiles and enrichment attributes.
- Campaign similarity is heuristic and should not be interpreted as a probability.
- A missing campaign match does not establish that an IOC is benign.
- APT attribution is tentative and requires independent threat-intelligence evidence.
- Relationship Graph functionality may be subject to further development.

## Future Enhancements

1. Improve domain-classification accuracy and generalisation.
2. Expand and validate campaign datasets.
3. Integrate automated IOC enrichment.
4. Improve campaign correlation and attribution.
5. Develop interactive relationship visualisation.
6. Add persistent storage and database integration.
7. Introduce additional validation, logging, and security controls.
8. Evaluate the system against independent threat-intelligence datasets.

## Data Handling

Raw datasets and intermediate analysis files are excluded from this repository. Only files required for the current application setup are included.

Project code, model artifacts, and reports should be shared only with authorised reviewers and in accordance with applicable organisational requirements.

## Author

Developed as a cybersecurity and threat-intelligence project focused on APT investigation, phishing campaign discovery, IOC correlation, and machine-learning-assisted threat analysis.