from pathlib import Path
import sys
import json
import socket
import ipaddress
import re

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
DISCOVERED_CLUSTERS_PATH = (
    PROJECT_ROOT
    / "datasets"
    / "processed"
    / "discovered_campaign_clusters.csv"
)


# ============================================================
# IMPORT CAMPAIGN MATCHER
# ============================================================

if str(CAMPAIGNS_DIR) not in sys.path:
    sys.path.insert(0, str(CAMPAIGNS_DIR))

from match_new_ioc import match_ioc
from attribute_campaign import attribute_campaign


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

class IOCEnrichmentRequest(BaseModel):
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

    if not DISCOVERED_CLUSTERS_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Discovered campaign clusters file not found",
        )

    try:
        import csv

        # Load campaign profiles
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

        # Load cluster metadata
        with open(
            DISCOVERED_CLUSTERS_PATH,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:
            records = list(csv.DictReader(file))

        cluster_metadata = {}

        for record in records:
            cluster_id = record.get(
                "Discovered_Cluster_ID", ""
            ).strip()

            if not cluster_id or cluster_id == "UNCLUSTERED":
                continue

            if cluster_id not in cluster_metadata:
                cluster_metadata[cluster_id] = {
                    "status": record.get("Status", "").strip(),
                    "similarity_threshold": float(
                        record.get("Similarity_Threshold", 0)
                    ),
                    "cluster_size": int(
                        record.get("Cluster_Size", 0)
                    ),
                }

        # Attach metadata and characteristics
        for profile in profiles:

            profile_id = profile.get("campaign_profile_id")
            members = profile.get("members") or []

            metadata = cluster_metadata.get(profile_id)

            if metadata:
                profile.update(metadata)

            def get_unique_values(field):
                return sorted({
                    str(member.get(field, "")).strip()
                    for member in members
                    if member.get(field) is not None
                    and str(member.get(field, "")).strip()
                })

            # Campaign targeting characteristics
            profile["target_sectors"] = get_unique_values(
                "Target_Sector"
            )

            profile["target_regions"] = get_unique_values(
                "Target_Region"
            )

            profile["lure_themes"] = get_unique_values(
                "Lure_Theme"
            )

            # Infrastructure shared by all cluster members
            shared_fields = [
                "ASN",
                "Cert_Fingerprint",
                "Favicon_Hash",
                "Subdomain_Pattern",
            ]

            profile["shared_infrastructure"] = {}

            for field in shared_fields:
                values = get_unique_values(field)

                if len(values) == 1 and len(members) > 0:
                    profile["shared_infrastructure"][field] = (
                        values[0]
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

    except (OSError, csv.Error, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load campaign data: {error}",
        )


# ============================================================
# CAMPAIGN STATISTICS
# ============================================================

@app.get("/campaign-stats")
def get_campaign_stats():

    if not DISCOVERED_CLUSTERS_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail="Discovered campaign clusters file not found",
        )

    try:
        import csv

        with open(
            DISCOVERED_CLUSTERS_PATH,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            records = list(csv.DictReader(file))

        clustered_count = sum(
            1 for record in records
            if record.get("Discovered_Cluster_ID", "").strip()
            and record.get("Discovered_Cluster_ID", "").strip() != "UNCLUSTERED"
        )

        unclustered_count = sum(
            1 for record in records
            if record.get("Discovered_Cluster_ID", "").strip() == "UNCLUSTERED"
        )

        return {
            "total_iocs": len(records),
            "clustered_iocs": clustered_count,
            "unclustered_iocs": unclustered_count,
        }

    except (OSError, csv.Error) as error:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read campaign statistics: {error}",
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
        # Convert incoming request into a dictionary
        new_ioc = request.model_dump()

        # Step 1: Find the closest discovered campaign
        campaign_result = match_ioc(new_ioc)

        # Step 2: Attribute the matched campaign
        attribution_result = attribute_campaign(campaign_result)

        # Step 3: Combine both results
        return {
            **campaign_result,
            "attribution": attribution_result,
        }

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
            detail=f"Campaign analysis failed: {str(error)}",
        )

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

    
# ============================================================
# IOC ENRICHMENT
# ============================================================

@app.post("/enrich-ioc")
def enrich_ioc(request: IOCEnrichmentRequest):

    domain = request.domain.strip().lower()

    # Validate domain format
    if not domain or "://" in domain or "/" in domain:
        raise HTTPException(
            status_code=400,
            detail="Enter a domain name without a URL scheme or path"
        )

    try:
        domain = domain.encode("idna").decode("ascii")
    except UnicodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid domain name"
        )

    if len(domain) > 253 or not re.fullmatch(
        r"(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}",
        domain
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid domain format"
        )

    result = {
        "domain": domain,
        "ip_addresses": [],
        "hostname": domain,
        "dns_status": "unavailable",
        "enrichment_source": "System DNS resolver",
        "warning": (
            "DNS results are observations from the current resolver. "
            "They do not establish whether a domain is malicious."
        )
    }

    try:
        records = socket.getaddrinfo(
            domain,
            None,
            type=socket.SOCK_STREAM
        )

        ip_addresses = sorted({
            record[4][0]
            for record in records
        })

        result["ip_addresses"] = ip_addresses
        result["dns_status"] = "resolved"

    except socket.gaierror:
        result["dns_status"] = "resolution_failed"
        result["warning"] = (
            "The domain could not be resolved using the current system "
            "DNS resolver. This does not prove that the domain is inactive."
        )

    return result
