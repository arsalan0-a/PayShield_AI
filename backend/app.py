import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd

# Add root directory to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from ml.feature_extraction import extract_features

# ==========================================
# Load trained model
# ==========================================

MODEL_PATH = base_dir / "datasets" / "best_model.pkl"
model = joblib.load(MODEL_PATH)


# ==========================================
# Create FastAPI application
# ==========================================

app = FastAPI(
    title="PayShield AI",
    description="AI-powered phishing URL detection API",
    version="2.0"
)

# Enable CORS for browser extensions and frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        "status": "online",
        "version": "2.0"
    }


# ==========================================
# URL prediction endpoint
# ==========================================

@app.post("/predict")
def predict_url(request: URLRequest):
    url = request.url.strip()
    if not url:
        return {
            "url": "",
            "result": "INVALID",
            "risk": "UNKNOWN",
            "phishing_probability": 0.0,
            "legitimate_probability": 100.0,
            "risk_factors": ["Empty URL provided"]
        }

    # 1. Handle internal browser pages (edge://, chrome://, about:, etc.)
    internal_schemes = ("edge://", "chrome://", "about:", "brave://", "opera://", "chrome-extension://", "edge-extension://", "devtools://", "view-source:", "file://")
    if any(url.startswith(s) for s in internal_schemes):
        return {
            "url": url,
            "result": "LEGITIMATE",
            "risk": "LOW",
            "phishing_probability": 0.0,
            "legitimate_probability": 100.0,
            "risk_factors": ["Internal browser system page"]
        }

    # 2. Handle localhost / development servers
    if any(url.startswith(p) for p in ["http://localhost", "https://localhost", "http://127.0.0.1", "https://127.0.0.1"]):
        return {
            "url": url,
            "result": "LEGITIMATE",
            "risk": "LOW",
            "phishing_probability": 0.0,
            "legitimate_probability": 100.0,
            "risk_factors": ["Local development server"]
        }

    # Extract URL features
    features = extract_features(url)
    features.pop("label", None)


    # Convert features to DataFrame
    features_df = pd.DataFrame([features])

    # Make prediction & probabilities
    prediction = int(model.predict(features_df)[0])
    probabilities = model.predict_proba(features_df)[0]

    legitimate_probability = float(round(probabilities[0] * 100, 2))
    phishing_probability = float(round(probabilities[1] * 100, 2))

    # Determine risk factors for explainability
    risk_factors = []
    if features.get("brand_spoofed", 0) == 1:
        risk_factors.append("Brand impersonation detected outside registered domain")
    if features.get("contains_ip", 0) == 1:
        risk_factors.append("Raw IP address used instead of domain name")
    if features.get("is_suspicious_tld", 0) == 1:
        risk_factors.append("Domain uses high-risk / abused TLD")
    if features.get("entropy_hostname", 0) >= 3.8:
        risk_factors.append("High entropy / randomized hostname (possible DGA)")
    if features.get("subdomain_count", 0) >= 3:
        risk_factors.append(f"Excessive subdomain depth ({features['subdomain_count']} levels)")
    if features.get("is_shortened", 0) == 1:
        risk_factors.append("URL shortener service used")
    if features.get("has_custom_port", 0) == 1:
        risk_factors.append("Non-standard port specified")
    if features.get("double_slash_path", 0) == 1:
        risk_factors.append("Double slash redirection in URL path")
    if features.get("https", 0) == 0:
        risk_factors.append("Insecure HTTP connection (no SSL)")

    # Result & Risk assignment
    if phishing_probability >= 70 or prediction == 1:
        result = "PHISHING"
    else:
        result = "LEGITIMATE"

    if phishing_probability >= 70:
        risk = "HIGH"
    elif phishing_probability >= 35:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "url": url,
        "result": result,
        "risk": risk,
        "phishing_probability": phishing_probability,
        "legitimate_probability": legitimate_probability,
        "risk_factors": risk_factors
    }