from pathlib import Path
import sys
import json

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    PROJECT_ROOT
    / "model_artifacts"
    / "domain_classifier.joblib"
)

CAMPAIGNS_DIR = (
    PROJECT_ROOT
    / "ml"
    / "campaigns"
)
CAMPAIGN_PROFILES_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "campaign_profiles.json"
)


# ============================================================
# IMPORT CAMPAIGN MATCHER
# ============================================================

if str(CAMPAIGNS_DIR) not in sys.path:
    sys.path.insert(0, str(CAMPAIGNS_DIR))

from match_new_ioc import match_ioc


# ============================================================
# LOAD DOMAIN CLASSIFICATION MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

model = joblib.load(MODEL_PATH)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="APT Intelligence API",
    description="Domain classification and campaign matching API",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class DomainRequest(BaseModel):
    domain: str = Field(
        min_length=1,
        max_length=253
    )


class CampaignMatchRequest(BaseModel):
    IOC: str = Field(
        min_length=1
    )

    IP: str | None = None
    ASN: str | None = None
    Registrar: str | None = None
    Cert_Fingerprint: str | None = None
    Favicon_Hash: str | None = None
    Kit_Fuzzy_Hash: str | None = None

    HTML_Similarity_Score: float | None = None
    Domain_Age_Days: float | None = None

    Target_Sector: str | None = None
    Target_Region: str | None = None
    Lure_Theme: str | None = None
    Subdomain_Pattern: str | None = None


# ============================================================
# HOME ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "APT Intelligence API is running",
        "model_loaded": True,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }
# ============================================================
# CAMPAIGN PROFILES
# ============================================================

@app.get("/campaigns")
def get_campaigns():

    if not CAMPAIGN_PROFILES_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Campaign profiles file not found",
        )

    try:
        with open(
            CAMPAIGN_PROFILES_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            profiles = json.load(file)

        if not isinstance(profiles, list):
            raise ValueError(
                "Campaign profiles must contain a JSON list"
            )

        return {
            "total_profiles": len(profiles),
            "profiles": profiles,
        }

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Campaign profiles JSON is invalid",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# ============================================================
# DOMAIN CLASSIFICATION
# ============================================================

@app.post("/predict")
def predict(request: DomainRequest):

    domain = request.domain.strip().lower()

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="Domain cannot be empty",
        )

    prediction = model.predict([domain])[0]

    scores = {}

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([domain])[0]

        scores = {
            str(label): round(float(score), 4)
            for label, score in zip(
                model.classes_,
                probabilities
            )
        }

    return {
        "domain": domain,
        "predicted_label": str(prediction),
        "model_scores": scores,
        "warning": (
            "Baseline model output only. "
            "Not a verified maliciousness verdict."
        ),
    }


# ============================================================
# CAMPAIGN MATCHING
# ============================================================

@app.post("/campaign-match")
def campaign_match(request: CampaignMatchRequest):

    try:
        # Convert the incoming API request into a dictionary
        new_ioc = request.model_dump()

        # Run the existing campaign matching logic
        result = match_ioc(new_ioc)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Campaign matching failed: {str(error)}",
        )