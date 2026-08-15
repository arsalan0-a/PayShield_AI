from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

from ml.feature_extraction import extract_features


# ==========================================
# Load trained model
# ==========================================

MODEL_PATH = "datasets/best_model.pkl"

model = joblib.load(MODEL_PATH)


# ==========================================
# Create FastAPI application
# ==========================================

app = FastAPI(
    title="PayShield AI",
    description="AI-powered phishing URL detection API",
    version="1.0"
)


# ==========================================
# Request format
# ==========================================

class URLRequest(BaseModel):
    url: str


# ==========================================
# Home / Health check
# ==========================================

@app.get("/")
def home():

    return {
        "message": "PayShield AI backend is running",
        "status": "online"
    }


# ==========================================
# URL prediction
# ==========================================

@app.post("/predict")
def predict_url(request: URLRequest):

    # Get URL
    url = request.url.strip()

    # Extract URL features
    features = extract_features(url)

    # Convert features to DataFrame
    features_df = pd.DataFrame([features])

    # Make prediction
    prediction = model.predict(features_df)[0]

    # Get probabilities
    probabilities = model.predict_proba(features_df)[0]

    legitimate_probability = float(
        probabilities[0] * 100
    )

    phishing_probability = float(
        probabilities[1] * 100
    )


    # ======================================
    # Determine result
    # ======================================

    if prediction == 1:
        result = "PHISHING"
    else:
        result = "LEGITIMATE"


    # ======================================
    # Determine risk
    # ======================================

    if phishing_probability >= 80:

        risk = "HIGH"

    elif phishing_probability >= 40:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    # ======================================
    # Return response
    # ======================================

    return {
        "url": url,
        "result": result,
        "risk": risk,
        "phishing_probability": round(
            phishing_probability,
            2
        ),
        "legitimate_probability": round(
            legitimate_probability,
            2
        )
    }