from pathlib import Path
import sys
import json
import socket
import ipaddress
import re
import os

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from io import BytesIO
from datetime import datetime, timezone

from fastapi.responses import StreamingResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from xml.sax.saxutils import escape


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

FRONTEND_URL = os.getenv("FRONTEND_URL", "")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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

class InvestigationReportRequest(BaseModel):
    ioc: str = Field(min_length=1, max_length=253)
    enrichment: dict = Field(default_factory=dict)
    analysis_result: dict = Field(default_factory=dict)
class InvestigationAssistantRequest(BaseModel):
    ioc: str = Field(min_length=1, max_length=253)
    analysis_result: dict = Field(default_factory=dict)
    enrichment: dict = Field(default_factory=dict)
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


# ============================================================
# PDF INVESTIGATION REPORT
# ============================================================

@app.post("/generate-report")
def generate_investigation_report(request: InvestigationReportRequest):

    buffer = BytesIO()

    try:
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontSize=19,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#183153"),
            spaceAfter=18,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#24558A"),
            spaceBefore=12,
            spaceAfter=7,
        )

        body_style = styles["BodyText"]

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch,
        )

        story = []

        def safe_text(value):
            if value is None or value == "":
                return "Not available"
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            return escape(str(value))

        def add_section(title, rows):
            story.append(Paragraph(escape(title), heading_style))

            table_data = [
                [
                    Paragraph("<b>Field</b>", body_style),
                    Paragraph("<b>Details</b>", body_style),
                ]
            ]

            for label, value in rows:
                table_data.append([
                    Paragraph(safe_text(label), body_style),
                    Paragraph(safe_text(value), body_style),
                ])

            table = Table(
                table_data,
                colWidths=[2.0 * inch, 4.8 * inch],
                repeatRows=1,
            )

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))

            story.append(table)
            story.append(Spacer(1, 8))

        enrichment = request.enrichment
        analysis = request.analysis_result
        attribution = analysis.get("attribution") or {}
        top_match = analysis.get("top_match") or analysis.get("top_candidate") or {}

        story.append(Paragraph("APT INTELLIGENCE SYSTEM", title_style))
        story.append(Paragraph("IOC Investigation Report", styles["Heading2"]))
        story.append(Spacer(1, 8))

        story.append(Paragraph(
            f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            body_style,
        ))

        add_section("1. IOC Details", [
            ("Indicator", request.ioc),
            ("IP address", enrichment.get("IP")),
            ("ASN", enrichment.get("ASN")),
            ("Registrar", enrichment.get("Registrar")),
        ])

        add_section("2. DNS Enrichment", [
            ("DNS status", enrichment.get("dns_status")),
            ("Resolved IP addresses", enrichment.get("ip_addresses")),
            ("Enrichment source", enrichment.get("enrichment_source")),
            ("DNS warning", enrichment.get("warning")),
        ])

        add_section("3. Campaign Analysis", [
            ("Match status", analysis.get("match_status")),
            ("Discovered campaign", top_match.get("campaign_profile_id")),
            ("Similarity score", analysis.get("similarity_score")),
            ("Strong evidence count", analysis.get("strong_evidence_count")),
            ("Matched IOC", top_match.get("matched_ioc")),
            ("Evidence", analysis.get("evidence")),
        ])

        add_section("4. Threat Actor Attribution", [
            ("Attribution status", attribution.get("attribution_status")),
            ("Candidate actor", attribution.get("candidate_actor")),
            ("Dataset attribution confidence", attribution.get("dataset_attribution_confidence")),
            ("Reference campaign", attribution.get("reference_campaign_id")),
            ("Reference label", attribution.get("reference_campaign_label")),
            ("Rationale", attribution.get("attribution_rationale")),
            ("Attribution warning", attribution.get("warning")),
        ])

        add_section("5. Analyst Notes", [
            (
                "Assessment limitation",
                "Campaign similarity and actor attribution are candidate assessments. "
                "They are not independently verified threat actor identifications.",
            ),
            (
                "Recommended action",
                "Review the underlying infrastructure evidence, validate indicators "
                "using trusted threat intelligence sources, and conduct analyst review "
                "before making an attribution decision.",
            ),
        ])

        doc.build(story)

        buffer.seek(0)

        filename = "APT_Investigation_Report.pdf"

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            },
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF report generation failed: {str(error)}",
        )

@app.post("/investigation-assistant")
def investigation_assistant(request: InvestigationAssistantRequest):
    try:
        analysis = request.analysis_result or {}
        enrichment = request.enrichment or {}

        top_match = (
            analysis.get("top_match")
            or analysis.get("top_candidate")
            or {}
        )

        attribution = analysis.get("attribution") or {}

        match_status = analysis.get("status", "Unknown")
        campaign_id = top_match.get("campaign_profile_id")
        matched_ioc = top_match.get("matched_member")
        score = top_match.get("score", 0)
        strong_evidence = top_match.get("strong_evidence_count", 0)
        evidence = top_match.get("evidence") or []

        findings = []
        uncertainties = []
        recommended_actions = []

        candidate_found = (
            match_status == "Candidate campaign match"
            and bool(campaign_id)
            and strong_evidence >= 2
        )

        if candidate_found:
            summary = (
                f"The IOC {request.ioc} meets the current heuristic "
                f"candidate-matching criteria for discovered profile "
                f"{campaign_id}. The similarity score is {score}, "
                f"with {strong_evidence} strong evidence signal(s). "
                "This is a candidate match requiring analyst validation."
            )

            findings.append(f"Candidate campaign profile: {campaign_id}")

            if matched_ioc:
                findings.append(f"Matched reference IOC: {matched_ioc}")

            if evidence:
                findings.append(f"Supporting evidence fields: {evidence}")

            recommended_actions.extend([
                "Validate the matched IP, certificate, favicon, or kit indicators against trusted sources.",
                "Compare the observed phishing behaviour, lure theme, target sector, and infrastructure.",
                "Review the reference campaign and supporting IOC records before accepting the match.",
            ])

        else:
            summary = (
                f"No established campaign match was identified for "
                f"{request.ioc} under the current matching rules. "
                "This does not establish that the IOC is benign."
            )

            findings.append("No candidate campaign met the current matching criteria.")

            if campaign_id:
                findings.append(
                    f"Closest discovered profile: {campaign_id} "
                    f"(similarity score: {score})"
                )

            recommended_actions.extend([
                "Collect additional infrastructure and campaign characteristics.",
                "Compare the IOC against trusted threat intelligence sources.",
                "Re-run campaign analysis when additional evidence becomes available.",
            ])

        candidate_actor = attribution.get("candidate_actor")

        if candidate_actor:
            findings.append(
                f"Dataset-derived candidate actor: {candidate_actor}"
            )
            findings.append(
                "Attribution status: "
                + str(attribution.get("attribution_status", "Not specified"))
            )

            uncertainties.append(
                "The candidate actor label comes from the reference dataset "
                "and is not an independently verified attribution."
            )

        uncertainties.extend([
            "Similarity scores are heuristic scores, not probabilities.",
            "A candidate campaign match does not prove common ownership or actor identity.",
            "A missing campaign match does not mean the IOC is safe or benign.",
            "Available enrichment may be incomplete or change over time.",
        ])

        if enrichment.get("dns_status"):
            uncertainties.append(
                "DNS resolution provides infrastructure information only; "
                "it does not establish maliciousness."
            )

        recommended_actions.extend([
            "Preserve the IOC, enrichment results, timestamps, and relevant logs.",
            "Require analyst review before making a threat actor attribution decision.",
        ])

        return {
            "assistant_type": "Evidence-grounded investigation assistant (rule-based)",
            "ioc": request.ioc,
            "summary": summary,
            "findings": findings,
            "uncertainties": uncertainties,
            "recommended_actions": recommended_actions,
            "disclaimer": (
                "This assistant generates a rule-based summary from the "
                "system's analysis results. It does not independently verify "
                "threat intelligence or identify threat actors."
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation assistant failed: {str(error)}",
        )
