
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = (
    PROJECT_ROOT
    / "model_artifacts"
    / "domain_classifier.joblib"
)

# Load the existing trained model
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="DRDO APT Intelligence API",
    description="Baseline domain classification API",
    version="1.0.0",
)

# Allow the local React/Vite frontend to call the API
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


class DomainRequest(BaseModel):
    domain: str = Field(min_length=1, max_length=253)


@app.get("/")
def home():
    return {
        "message": "DRDO APT Intelligence API is running",
        "model_loaded": True,
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }


@app.post("/predict")
def predict(request: DomainRequest):
    domain = request.domain.strip().lower()

    if not domain:
        raise HTTPException(
            status_code=400,
            detail="Domain cannot be empty",
        )

    # This baseline model expects domain strings.
    prediction = model.predict([domain])[0]

    scores = {}
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([domain])[0]
        scores = {
            str(label): round(float(score), 4)
            for label, score in zip(model.classes_, probabilities)
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
