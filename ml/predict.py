import sys
from pathlib import Path
import pandas as pd
import joblib

# Ensure ml package is in path
base_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(base_dir))

from ml.feature_extraction import extract_features, TARGET_BRANDS, HIGH_RISK_TLDS

model_file = base_dir / "datasets" / "best_model.pkl"
model = joblib.load(model_file)

def evaluate_url(url: str):
    features = extract_features(url)
    features.pop("label", None)
    df = pd.DataFrame([features])

    prediction = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]
    phishing_prob = float(probabilities[1] * 100)
    legit_prob = float(probabilities[0] * 100)

    # Determine risk factors
    risk_factors = []
    if features.get("brand_spoofed", 0) == 1:
        risk_factors.append("⚠️ Brand impersonation detected outside registered domain")
    if features.get("contains_ip", 0) == 1:
        risk_factors.append("⚠️ Raw IP address used instead of domain name")
    if features.get("is_suspicious_tld", 0) == 1:
        risk_factors.append("⚠️ Domain uses high-risk / abused TLD")
    if features.get("entropy_hostname", 0) >= 3.8:
        risk_factors.append("⚠️ High entropy / randomized hostname (possible DGA)")
    if features.get("subdomain_count", 0) >= 3:
        risk_factors.append(f"⚠️ Excessive subdomain depth ({features['subdomain_count']} levels)")
    if features.get("is_shortened", 0) == 1:
        risk_factors.append("⚠️ URL shortener service used")
    if features.get("has_custom_port", 0) == 1:
        risk_factors.append("⚠️ Non-standard port specified")
    if features.get("double_slash_path", 0) == 1:
        risk_factors.append("⚠️ Double slash redirection trick in URL path")
    if features.get("https", 0) == 0:
        risk_factors.append("ℹ️ Insecure HTTP connection (no SSL)")

    if phishing_prob >= 75:
        risk = "HIGH"
        verdict = "🚨 PHISHING / MALICIOUS"
    elif phishing_prob >= 40:
        risk = "MEDIUM"
        verdict = "⚠️ SUSPICIOUS"
    else:
        risk = "LOW"
        verdict = "✅ LEGITIMATE / SAFE"

    return {
        "url": url,
        "verdict": verdict,
        "risk": risk,
        "phishing_probability": round(phishing_prob, 2),
        "legitimate_probability": round(legit_prob, 2),
        "risk_factors": risk_factors
    }


if __name__ == "__main__":
    print("=" * 60)
    print("PAYSHIELD AI - PHISHING URL DETECTOR")
    print("=" * 60)

    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    else:
        test_url = input("\nEnter URL to inspect: ").strip()

    if not test_url:
        print("Error: No URL provided.")
        sys.exit(1)

    result = evaluate_url(test_url)

    print("\n" + "-" * 60)
    print(f"Target URL : {result['url']}")
    print(f"Verdict    : {result['verdict']}")
    print(f"Risk Level : {result['risk']}")
    print(f"Phishing Risk : {result['phishing_probability']}%")
    print(f"Legitimate    : {result['legitimate_probability']}%")
    
    if result["risk_factors"]:
        print("\nIdentified Risk Factors:")
        for factor in result["risk_factors"]:
            print(f"  • {factor}")
    else:
        print("\nNo anomalous risk indicators found.")
    print("-" * 60)