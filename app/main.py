import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.schemas import HeartFeatures, PredictionResponse

FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal",
]

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "heart_model.joblib"
MODEL_PATH = Path(os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="Heart Disease Prediction API",
    description="Predicts whether a patient has heart disease from 13 clinical features.",
    version="1.0.0",
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "model_type": type(model.steps[-1][1]).__name__,
        "features": FEATURES,
        "target": "heart disease (1 = disease, 0 = no disease)",
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(features: HeartFeatures):
    row = pd.DataFrame([features.model_dump()], columns=FEATURES)
    probability = float(model.predict_proba(row)[0][1])
    prediction = int(model.predict(row)[0])
    return PredictionResponse(heart_disease=bool(prediction), probability=round(probability, 4))
