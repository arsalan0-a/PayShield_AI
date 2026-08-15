import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from lightgbm import LGBMClassifier

import joblib


# ==========================================
# 1. Load feature dataset
# ==========================================

input_file = "C:\\Users\\Amaan\\OneDrive\\Desktop\\Project\\PayShield_AI\\datasets\\features.csv"

df = pd.read_csv(input_file)

print("Dataset loaded.")
print("Total samples:", len(df))


# ==========================================
# 2. Separate features and target
# ==========================================

X = df.drop("label", axis=1)

y = df["label"]


print("Number of input features:", X.shape[1])


# ==========================================
# 3. Split dataset
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# 4. Function to evaluate models
# ==========================================

def evaluate_model(model, name):

    print("\n" + "=" * 50)
    print(name)
    print("=" * 50)

    # Train
    model.fit(X_train, y_train)

    # Predict
    predictions = model.predict(X_test)

    # Metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)

    print("Accuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1 Score :", round(f1, 4))

    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    return model, f1


# ==========================================
# 5. Logistic Regression
# ==========================================

logistic_model = LogisticRegression(
    max_iter=1000
)

logistic_model, logistic_f1 = evaluate_model(
    logistic_model,
    "Logistic Regression"
)


# ==========================================
# 6. Random Forest
# ==========================================

random_forest_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

random_forest_model, random_forest_f1 = evaluate_model(
    random_forest_model,
    "Random Forest"
)


# ==========================================
# 7. LightGBM
# ==========================================

lightgbm_model = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42,
    verbosity=-1
)

lightgbm_model, lightgbm_f1 = evaluate_model(
    lightgbm_model,
    "LightGBM"
)


# ==========================================
# 8. Select best model
# ==========================================

models = {
    "Logistic Regression": (logistic_model, logistic_f1),
    "Random Forest": (random_forest_model, random_forest_f1),
    "LightGBM": (lightgbm_model, lightgbm_f1)
}

best_name = max(
    models,
    key=lambda name: models[name][1]
)

best_model = models[best_name][0]

print("\n" + "=" * 50)
print("BEST MODEL")
print("=" * 50)

print("Selected:", best_name)
print("F1 Score:", models[best_name][1])


# ==========================================
# 9. Save best model
# ==========================================

model_file = "datasets/best_model.pkl"

joblib.dump(best_model, model_file)

print("\nModel saved to:")
print(model_file)