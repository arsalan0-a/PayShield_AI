import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ==========================================
# 1. Load dataset
# ==========================================

data_file = "datasets/features.csv"
model_file = "datasets/best_model.pkl"

df = pd.read_csv(data_file)

print("=" * 60)
print("PAYSHIELD AI - MODEL EVALUATION")
print("=" * 60)

print("\nTotal samples:", len(df))


# ==========================================
# 2. Separate X and y
# ==========================================

X = df.drop("label", axis=1)

y = df["label"]


# ==========================================
# 3. Create SAME test split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("Test samples:", len(X_test))


# ==========================================
# 4. Load trained model
# ==========================================

model = joblib.load(model_file)


# ==========================================
# 5. Make predictions
# ==========================================

predictions = model.predict(X_test)

probabilities = model.predict_proba(X_test)[:, 1]


# ==========================================
# 6. Calculate metrics
# ==========================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions
)

recall = recall_score(
    y_test,
    predictions
)

f1 = f1_score(
    y_test,
    predictions
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)


# ==========================================
# 7. Display metrics
# ==========================================

print("\nMODEL PERFORMANCE")
print("-" * 60)

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")


# ==========================================
# 8. Confusion Matrix
# ==========================================

cm = confusion_matrix(
    y_test,
    predictions
)

print("\nCONFUSION MATRIX")
print("-" * 60)

print("                 Predicted")
print("                 Legit  Phishing")
print(f"Actual Legit     {cm[0][0]:5d}  {cm[0][1]:8d}")
print(f"Actual Phishing  {cm[1][0]:5d}  {cm[1][1]:8d}")


# ==========================================
# 9. Detailed report
# ==========================================

print("\nCLASSIFICATION REPORT")
print("-" * 60)

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Legitimate",
            "Phishing"
        ]
    )
)


# ==========================================
# 10. Explain errors
# ==========================================

true_negative = cm[0][0]
false_positive = cm[0][1]
false_negative = cm[1][0]
true_positive = cm[1][1]

print("\nERROR ANALYSIS")
print("-" * 60)

print("True Negatives :", true_negative)
print("False Positives:", false_positive)
print("False Negatives:", false_negative)
print("True Positives :", true_positive)


print("\nEvaluation completed.")