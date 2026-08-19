import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier


# ==========================================
# 1. Load feature dataset
# ==========================================

base_dir = Path(__file__).resolve().parent.parent
input_file = base_dir / "datasets" / "features.csv"
model_file = base_dir / "datasets" / "best_model.pkl"

print(f"Loading features from {input_file}...")
df = pd.read_csv(input_file)

print(f"Dataset loaded: {len(df):,} samples, {df.shape[1] - 1} features.")

X = df.drop("label", axis=1)
y = df["label"]

# Split into Train (70%), Calibrate (15%), Test (15%)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.30, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp
)

print(f"\nSplits -> Train: {len(X_train):,}, Validation/Calibration: {len(X_val):,}, Test: {len(X_test):,}")


# ==========================================
# 2. Evaluate Models
# ==========================================

candidate_models = {
    "LightGBM": LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=8,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1,
        n_jobs=-1
    ),
    "XGBoost": XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=7,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        n_jobs=-1
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=250,
        max_depth=16,
        min_samples_split=4,
        random_state=42,
        n_jobs=-1
    )
}

trained_models = {}

for name, model in candidate_models.items():
    print("\n" + "=" * 60)
    print(f"Training & Evaluating: {name}")
    print("=" * 60)

    model.fit(X_train, y_train)

    val_preds = model.predict(X_val)
    val_probs = model.predict_proba(X_val)[:, 1]

    acc = accuracy_score(y_val, val_preds)
    prec = precision_score(y_val, val_preds)
    rec = recall_score(y_val, val_preds)
    f1 = f1_score(y_val, val_preds)
    auc = roc_auc_score(y_val, val_probs)

    print(f"Validation Metrics for {name}:")
    print(f"  Accuracy : {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall   : {rec:.4f}")
    print(f"  F1 Score : {f1:.4f}")
    print(f"  ROC-AUC  : {auc:.4f}")

    trained_models[name] = {
        "model": model,
        "f1": f1,
        "auc": auc
    }

# Select top performer based on F1 Score
best_name = max(trained_models, key=lambda k: trained_models[k]["f1"])
best_raw_model = trained_models[best_name]["model"]

print("\n" + "=" * 60)
print(f"TOP MODEL SELECTED: {best_name}")
print("=" * 60)


# ==========================================
# 3. Probability Calibration with 5-Fold CV
# ==========================================

print(f"\nCalibrating output probabilities for {best_name} using 5-fold cross-validation...")
X_train_full = pd.concat([X_train, X_val], ignore_index=True)
y_train_full = pd.concat([y_train, y_val], ignore_index=True)

# Clone or re-instantiate the best model for cross-validated calibration
if best_name == "LightGBM":
    estimator = LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=63, max_depth=8,
        subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=-1, n_jobs=-1
    )
elif best_name == "XGBoost":
    estimator = XGBClassifier(
        n_estimators=300, learning_rate=0.05, max_depth=7,
        subsample=0.8, colsample_bytree=0.8, random_state=42, eval_metric="logloss", n_jobs=-1
    )
else:
    estimator = RandomForestClassifier(
        n_estimators=250, max_depth=16, min_samples_split=4, random_state=42, n_jobs=-1
    )

calibrated_model = CalibratedClassifierCV(
    estimator=estimator,
    method="sigmoid",
    cv=5
)
calibrated_model.fit(X_train_full, y_train_full)



# ==========================================
# 4. Final Evaluation on Held-Out Test Set
# ==========================================

test_preds = calibrated_model.predict(X_test)
test_probs = calibrated_model.predict_proba(X_test)[:, 1]

final_acc = accuracy_score(y_test, test_preds)
final_prec = precision_score(y_test, test_preds)
final_rec = recall_score(y_test, test_preds)
final_f1 = f1_score(y_test, test_preds)
final_auc = roc_auc_score(y_test, test_probs)

print("\n" + "=" * 60)
print(f"FINAL TEST SET EVALUATION ({best_name} + CalibratedClassifierCV)")
print("=" * 60)
print(f"Accuracy : {final_acc:.4f} ({final_acc*100:.2f}%)")
print(f"Precision: {final_prec:.4f} ({final_prec*100:.2f}%)")
print(f"Recall   : {final_rec:.4f} ({final_rec*100:.2f}%)")
print(f"F1 Score : {final_f1:.4f}")
print(f"ROC-AUC  : {final_auc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, test_preds, target_names=["Legitimate", "Phishing"]))


# ==========================================
# 5. Save Calibrated Model
# ==========================================

# Set feature names on calibrated model if needed for DataFrame inference
calibrated_model.feature_names_in_ = np.array(X.columns.tolist())

joblib.dump(calibrated_model, model_file)
print(f"Calibrated best model saved to: {model_file}")