import pandas as pd
import joblib
import sys

from feature_extraction import extract_features


# ==========================================
# 1. Load trained model
# ==========================================

model_file = "datasets/best_model.pkl"

model = joblib.load(model_file)

print("PayShield AI - Phishing URL Detector")
print("=" * 45)


# ==========================================
# 2. Get URL from user
# ==========================================

url = input("\nEnter URL: ").strip()


# ==========================================
# 3. Extract features
# ==========================================

features = extract_features(url)

# Remove label because we are predicting it
features.pop("label", None)

# Convert to DataFrame
features_df = pd.DataFrame([features])


# ==========================================
# 4. Make prediction
# ==========================================

prediction = model.predict(features_df)[0]

probability = model.predict_proba(features_df)[0]


# Probability of phishing
phishing_probability = probability[1] * 100


# ==========================================
# 5. Display result
# ==========================================

print("\n" + "=" * 45)

if prediction == 1:

    print("🚨 RESULT: POSSIBLE PHISHING")

else:

    print("✅ RESULT: LIKELY LEGITIMATE")


print(f"Phishing probability: {phishing_probability:.2f}%")

print("=" * 45)