import pandas as pd
import joblib
from pathlib import Path

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

base_dir = Path(__file__).resolve().parent.parent
data_file = base_dir / "datasets" / "features.csv"
model_file = base_dir / "datasets" / "best_model.pkl"

df = pd.read_csv(data_file)

print("=" * 60)
print("PAYSHIELD AI - MODEL EVALUATION")
print("=" * 60)
print(f"\nTotal samples: {len(df):,}")

X = df.drop("label", axis=1)
y = df["label"]

# Evaluate on a 20% test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Test samples: {len(X_test):,}")

model = joblib.load(model_file)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)
roc_auc = roc_auc_score(y_test, probabilities)

print("\nMODEL PERFORMANCE")
print("-" * 60)
print(f"Accuracy : {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f} ({precision*100:.2f}%)")
print(f"Recall   : {recall:.4f} ({recall*100:.2f}%)")
print(f"F1 Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

cm = confusion_matrix(y_test, predictions)

print("\nCONFUSION MATRIX")
print("-" * 60)
print("                 Predicted")
print("                 Legit  Phishing")
print(f"Actual Legit     {cm[0][0]:5d}  {cm[0][1]:8d}")
print(f"Actual Phishing  {cm[1][0]:5d}  {cm[1][1]:8d}")

print("\nCLASSIFICATION REPORT")
print("-" * 60)
print(classification_report(y_test, predictions, target_names=["Legitimate", "Phishing"]))

print("\nERROR ANALYSIS")
print("-" * 60)
print("True Negatives :", cm[0][0])
print("False Positives:", cm[0][1])
print("False Negatives:", cm[1][0])
print("True Positives :", cm[1][1])

print("\nEvaluation completed successfully.")