# 🛡️ PayShield AI - Intelligent Phishing & Payment Fraud Detector

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![LightGBM](https://img.shields.io/badge/Model-LightGBM_Calibrated-brightgreen.svg?style=flat)](https://lightgbm.readthedocs.io/)
[![Chrome Extension](https://img.shields.io/badge/Chrome_Extension-Manifest_V3-4285F4.svg?style=flat&logo=googlechrome&logoColor=white)](https://developer.chrome.com/docs/extensions/)
[![Accuracy](https://img.shields.io/badge/Accuracy-99.82%25-success.svg?style=flat)]()

**PayShield AI** is an AI-powered security solution designed to protect users against real-time phishing attacks, credential harvesting, brand impersonation, and payment fraud. It features a lightweight **Google Chrome Extension (Manifest V3)**, a high-performance **FastAPI REST backend**, and a **5-fold calibrated Machine Learning classification engine** trained on 70,000+ verified URLs.

---

## 🌟 Key Features

- **⚡ Real-Time Active Tab Protection**: Instant AI safety verdicts whenever you navigate to login portals or payment gateways.
- **🔍 40+ Lexical & Structural Signals**: Comprehensive URL inspection including Shannon entropy, brand impersonation heuristics, public-suffix parsing with `tldextract`, and high-abuse TLD scoring.
- **🎯 Calibrated Confidence Estimates**: Probability calibration via `CalibratedClassifierCV` ensures output percentages represent reliable empirical risk scores.
- **💡 Explainable Security Insights**: Granular breakdown of identified risk indicators (e.g., brand spoofing outside registered domain, raw IP addresses, high entropy slugs).
- **🛡️ Top Authority Whitelisting**: Memory-cached global authority lookups eliminate false positives on legitimate major services.

---

## 🏗️ Project Architecture

```
PayShield_AI/
├── backend/
│   └── app.py                     # FastAPI REST API service with CORS support
├── extension/
│   ├── manifest.json              # Chrome Extension Manifest V3 configuration
│   ├── popup.html                 # Extension toolbar popup interface
│   └── popup.js                   # Client script sending active tab URL to backend
├── ml/
│   ├── feature_extraction.py      # 40+ feature extractor with entropy & brand detection
│   ├── prepare_data.py            # PhishTank dataset filtering & normalization
│   ├── augment_data.py            # Realistic legitimate URL generation with auth paths
│   ├── combine_data.py            # Balanced 70,000-sample dataset merger
│   ├── train.py                   # Multi-model selection (LightGBM/XGBoost/RF) + Calibration
│   ├── evaluate.py                # Comprehensive test set evaluation & error analysis
│   └── predict.py                 # Standalone CLI prediction utility
└── datasets/
    ├── best_model.pkl             # Serialized 5-fold calibrated LightGBM model
    ├── features.csv               # Extracted features matrix (70,000 x 42)
    ├── phishing.csv               # 35,000 verified PhishTank samples
    ├── legitimate_augmented.csv   # Realistic legitimate URLs with auth & checkout paths
    └── training_data.csv          # Combined balanced dataset
```

---

## 📊 Model Performance & Benchmarks

Trained and evaluated on **70,000 balanced samples** (50% verified phishing from PhishTank, 50% legitimate domains from Tranco/Alexa Top 1M):

| Metric | Score |
| :--- | :--- |
| **Accuracy** | **99.82%** |
| **Precision** | **99.81%** |
| **Recall** | **99.83%** |
| **F1 Score** | **0.9982** |
| **ROC-AUC** | **1.0000** |

### Benchmark on Real-World Links

| Test Link | Type | Safety Verdict | Risk Score |
| :--- | :--- | :--- | :--- |
| `https://accounts.google.com/signin` | Google Auth | 🛡️ **LEGITIMATE** | **0.07%** |
| `https://www.paypal.com/signin` | PayPal Login | 🛡️ **LEGITIMATE** | **0.17%** |
| `https://github.com/login` | GitHub Login | 🛡️ **LEGITIMATE** | **0.30%** |
| `https://www.amazon.com/ap/signin` | Amazon Auth | 🛡️ **LEGITIMATE** | **0.02%** |
| `http://paypal-verification-security-update.xyz/login.php` | Brand Spoof Phish | 🚨 **PHISHING** | **99.94%** |
| `http://192.168.1.1/pay/bank-login.html` | Raw IP Phish | 🚨 **PHISHING** | **99.87%** |
| `http://appleid.apple.com.verify-account-security.top/login` | Subdomain Spoof | 🚨 **PHISHING** | **100.0%** |

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google Chrome (or Chromium-based browser)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/arsalan0-a/PayShield_AI.git
cd PayShield_AI

# Install required packages
pip install fastapi uvicorn joblib pandas scikit-learn lightgbm xgboost tldextract
```

### 3. Launching the Backend Server
```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```
- **API Health Check**: `http://127.0.0.1:8000/`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

### 4. Installing the Chrome Extension
1. Open Google Chrome and go to `chrome://extensions/`.
2. Toggle on **Developer mode** in the top right.
3. Click **Load unpacked** and select the `extension/` directory.
4. Pin PayShield AI to your browser toolbar to scan active tabs!

---

## 🧪 Testing & Predictions

### Run CLI Prediction
```bash
python ml/predict.py "https://accounts.google.com/signin"
python ml/predict.py "http://paypal-verification-security-update.xyz/login.php"
```

### Retrain & Evaluate Models
```bash
# Extract features
python ml/feature_extraction.py

# Train models and calibrate probabilities
python ml/train.py

# Run comprehensive test evaluation
python ml/evaluate.py
```

---

## 🔒 Security & Privacy Notice
PayShield AI analyzes URLs solely for heuristic threat detection and does not log personal browsing history or store sensitive credentials.
