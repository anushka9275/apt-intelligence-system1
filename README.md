# APT Intelligence System

An integrated threat intelligence platform for domain classification, phishing IOC analysis, campaign discovery, infrastructure correlation, and potential APT attribution.

The system combines machine learning, heuristic campaign matching, automated DNS enrichment, an investigation assistant, and PDF report generation through a web-based analyst dashboard.

## 1. Project Overview

The APT Intelligence System helps analysts investigate suspicious domains and phishing indicators by:

- Classifying domains as benign or suspicious using a machine learning model.
- Comparing incoming IOCs against discovered campaign profiles.
- Identifying shared infrastructure and campaign characteristics.
- Generating potential threat actor attribution candidates.
- Resolving domain DNS information for basic IOC enrichment.
- Producing structured investigation summaries and downloadable PDF reports.
- Maintaining an IOC prediction history using MongoDB Atlas.

The system is designed to support threat investigation and analyst decision-making. Its predictions and attribution results are preliminary indicators, not confirmed security verdicts.

## 2. Key Features

### IOC Search
- Domain classification through a trained machine learning model.
- Suspicious and benign prediction labels.
- Model confidence scores.
- Prediction history storage through MongoDB.

### Campaign Explorer
- Dynamically loads discovered campaign profiles.
- Displays campaign status, cluster size, and similarity threshold.
- Shows target sectors, regions, and lure themes.
- Displays shared infrastructure characteristics.
- Provides access to IOC members within discovered clusters.

### New Threat Analysis
- Accepts a new IOC and its available enrichment information.
- Compares the IOC against existing campaign profiles.
- Calculates similarity scores using available infrastructure and campaign evidence.
- Identifies potential campaign matches.
- Provides candidate threat actor attribution when sufficient evidence is available.
- Displays supporting evidence and attribution rationales.

### Relationship Graph
- Dynamically visualizes discovered campaign profiles and their associated IOCs.
- Shows IOC-to-campaign relationships.
- Supports campaign selection and investigation.

### Automated IOC Enrichment
- Performs DNS resolution for submitted domains.
- Retrieves resolved IP addresses and hostname information.
- Displays DNS enrichment status and limitations.

### Investigation Assistant
- Produces a structured, rule-based investigation summary.
- Highlights key findings, uncertainties, and recommended analyst actions.
- Explains why a candidate campaign match may or may not be reliable.

### PDF Investigation Reports
- Generates downloadable PDF reports.
- Includes IOC details, enrichment information, campaign analysis, attribution results, and analyst notes.

### IOC History
- Stores successful domain predictions in MongoDB Atlas.
- Retrieves recent investigation records.
- Supports searching, filtering, refreshing, and CSV export.

## 3. Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React 19, Vite 8, JavaScript, CSS |
| Icons | Lucide React |
| Backend | Node.js, Express 5 |
| Database | MongoDB Atlas |
| ML API | Python 3.14, FastAPI, Uvicorn |
| Machine Learning | Scikit-learn, TF-IDF, Logistic Regression |
| Data Processing | Pandas, NumPy |
| Model Persistence | Joblib |
| PDF Generation | ReportLab |
| Version Control | Git, GitHub |

## 4. System Architecture

The application consists of three main layers.

1. **React frontend:** Provides the analyst dashboard and investigation interface.
2. **Node.js backend:** Handles domain prediction requests, communicates with the Python API, and stores prediction history in MongoDB Atlas.
3. **Python FastAPI service:** Loads the trained model, processes IOC and campaign analysis requests, performs DNS enrichment, and generates investigation reports.

The frontend communicates with the Python API for campaign analysis, enrichment, investigation assistance, and report generation. The Express backend handles IOC prediction requests and MongoDB history operations.

### Architecture Flow

```text
                 ANALYST
                    |
                    v
             REACT FRONTEND
               (Vite :5173)
                    |
          +---------+----------+
          |                    |
          v                    v
    EXPRESS BACKEND       PYTHON FASTAPI
       (:5000)                (:8000)
          |                    |
          v                    +------------------+
    MONGODB ATLAS              |                  |
    IOC History                v                  v
                         DOMAIN CLASSIFIER   CAMPAIGN ENGINE
                                                  |
                                       +----------+----------+
                                       |          |          |
                                       v          v          v
                                  Attribution  Enrichment  Investigation
                                       |          |          |
                                       +----------+----------+
                                                  |
                                                  v
                                           PDF REPORT
```

## 5. Project Structure

```text
apt_system/
│
├── api/
│   └── main.py
│
├── backend/
│   ├── server.js
│   ├── package.json
│   ├── package-lock.json
│   └── .env
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── ml/
│   ├── attribution/
│   ├── campaigns/
│   ├── classification/
│   ├── common/
│   └── evaluation/
│
├── datasets/
│   ├── external/
│   ├── processed/
│   │   ├── domain_classifier.joblib
│   │   └── campaign_profiles.json
│   └── raw/
│
├── model_artifacts/
│
├── reports/
│
├── requirements.txt
├── README.md
└── .gitignore
```

The `datasets/raw` and `datasets/external` directories contain local dataset material. Not all datasets and intermediate evaluation outputs are included in version control.

The trained domain classifier and campaign profile files are required by the API.

## 6. Prerequisites

Install the following before setting up the project:

- Python 3.14.0
- Node.js and npm
- Git
- A MongoDB Atlas account and database

MongoDB Atlas must be configured with a database user and an appropriate network access rule for the machine running the application.

## 7. Installation and Setup

Clone the repository:

```powershell
git clone https://github.com/anushka9275/apt-intelligence-system1.git
cd apt-intelligence-system1
```

### A. Python FastAPI Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the Python dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The Python dependencies include:

- FastAPI
- Uvicorn
- Joblib
- NumPy
- Pandas
- Scikit-learn

Verify that the trained model and campaign profiles are present:

```powershell
Test-Path .\datasets\processed\domain_classifier.joblib
Test-Path .\datasets\processed\campaign_profiles.json
```

Both commands should return `True`.

Start the Python API:

```powershell
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at:

`http://127.0.0.1:8000`

### B. Node.js and Express Backend Setup

Open a separate terminal:

```powershell
cd apt-intelligence-system1\backend
npm ci
```

Create a `.env` file inside the `backend` directory:

```env
MONGODB_URI=your_mongodb_atlas_connection_string
DB_NAME=drdo_apt_db
ML_API_URL=http://127.0.0.1:8000
PORT=5000
```

Replace the MongoDB connection string placeholder with your own Atlas connection string. Do not commit this file or share its credentials.

Start the backend:

```powershell
npm start
```

The backend will be available at:

`http://localhost:5000`

On successful startup, the terminal should display a MongoDB connection confirmation and the backend address.

### C. React Frontend Setup

Open another terminal:

```powershell
cd apt-intelligence-system1\frontend
npm ci
npm run dev
```

The frontend will be available at:

`http://localhost:5173`

### Running the Complete Application

Keep all three services running simultaneously:

| Service | Port | Command |
|---|---:|---|
| React frontend | 5173 | `npm run dev` |
| Express backend | 5000 | `npm start` |
| FastAPI service | 8000 | `python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000` |

Open `http://localhost:5173` in your browser.

## 8. API Endpoints

### Python FastAPI

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | API and model health status |
| GET | `/campaigns` | Retrieve discovered campaign profiles |
| GET | `/campaign-stats` | Retrieve campaign statistics |
| POST | `/predict` | Classify a domain |
| POST | `/campaign-match` | Match an IOC against campaign profiles |
| POST | `/enrich-ioc` | Perform basic IOC DNS enrichment |
| POST | `/generate-report` | Generate a PDF investigation report |
| POST | `/investigation-assistant` | Generate a structured investigation summary |

### Node.js Express Backend

Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend health information |
| GET | `/api/health` | Backend and FastAPI connectivity check |
| GET | `/api/ioc-history` | Retrieve saved IOC prediction history |
| POST | `/api/predict` | Forward domain prediction and save the result |

The Express health endpoint checks connectivity with the Python API. MongoDB connectivity is established separately during backend startup.

## 9. Machine Learning and Campaign Analysis

### Domain Classification

The domain classification component uses:

- Character-level TF-IDF feature extraction.
- Logistic Regression classification.
- A trained model persisted using Joblib.

The current dataset contains 625 labelled domain records:

| Category | Records |
|---|---:|
| Benign | 128 |
| Suspicious | 497 |
| Total | 625 |

The reported test evaluation achieved 100% accuracy on its 125-record test split. However, this result should not be interpreted as guaranteed real-world accuracy. Manual checks have identified false-positive predictions on legitimate popular domains.

Predictions should therefore be treated as preliminary risk indicators requiring additional verification.

### Campaign Discovery and Matching

The campaign analysis component uses available IOC and infrastructure characteristics, including:

- IP address and ASN
- Registrar
- Certificate fingerprint and issuer
- Domain age
- Favicon hash
- HTML similarity
- Kit fuzzy hash
- Subdomain patterns
- Target sector and region
- Lure theme

Campaign matching uses weighted evidence comparisons against discovered campaign profiles.

The current campaign dataset contains 68 records and produces eight discovered campaign profiles, with 34 records clustered and 34 left unclustered.

A similarity score is a heuristic evidence score, not a calibrated probability that two IOCs belong to the same campaign.

### Potential APT Attribution

The attribution component uses campaign matching results and available dataset attribution information to identify a candidate threat actor.

Attribution output includes:

- Candidate actor
- Reference campaign
- Attribution confidence from the source dataset
- Supporting evidence and rationales
- Analyst review warnings

An attribution candidate is not proof of actor identity or campaign ownership. Dataset labels are not independently verified attribution findings.

## 10. Automated Enrichment and Investigation Assistant

### IOC Enrichment

The current automated enrichment functionality performs system DNS resolution and retrieves resolved IP addresses and related hostname information.

It does not yet provide comprehensive automated ASN, WHOIS, certificate, passive DNS, or threat-feed enrichment.

### Investigation Assistant

The investigation assistant is a deterministic, rule-based component. It organizes campaign matching and enrichment results into:

- Investigation summary
- Key findings
- Uncertainties and limitations
- Recommended analyst actions

It is not an LLM-based autonomous agent. Its output is grounded in the information already available to the system.

## 11. Testing

After starting all three services, verify the following:

1. Open the dashboard and confirm that the backend connection is healthy.
2. Submit a domain through IOC Search and verify the classification result.
3. Open IOC History and confirm that successful predictions are saved.
4. Open Campaign Explorer and verify that campaign profiles load.
5. Open Relationship Graph and test campaign selection.
6. Submit an IOC through New Threat Analysis and inspect its matching evidence.
7. Test automated DNS enrichment with a valid domain.
8. Generate an investigation summary and inspect its findings and limitations.
9. Download and open a PDF investigation report.

For a production-quality assessment, additional testing with independent datasets and broader edge cases is required.

## 12. Limitations and Responsible Use

- The domain classifier has been trained and evaluated on a relatively small labelled dataset.
- A high test-split score does not guarantee reliable predictions on unseen real-world domains.
- Campaign matching uses heuristic similarity scores and should not be interpreted as a probability.
- The campaign dataset includes sample and synthetic/test-style indicators, including `.example` domains and reserved documentation IP addresses.
- Campaign and threat actor labels reflect the supplied dataset and are not independent confirmation of real-world attribution.
- DNS resolution alone does not establish whether an IOC is malicious.
- A missing campaign match does not mean that an IOC is benign.
- Shared infrastructure is supporting evidence, not proof of common ownership.
- Attribution and investigation outputs require analyst validation.
- The application is a research and demonstration platform, not a replacement for a production threat intelligence or incident response system.

## 13. Future Enhancements

Potential future improvements include:

- Integration with external threat intelligence feeds.
- Automated ASN, WHOIS, certificate, and passive DNS enrichment.
- Larger and independently validated datasets.
- Improved campaign similarity evaluation and calibration.
- More advanced graph exploration and relationship analysis.
- Analyst authentication and role-based access control.
- Audit logging and investigation case management.
- Production deployment, monitoring, and security hardening.

## 14. Author

Developed as part of a cybersecurity and APT threat intelligence project.

**Project:** APT Intelligence System

**Focus Areas:** Cybersecurity, Threat Intelligence, Machine Learning, IOC Analysis, Campaign Correlation, and APT Attribution.