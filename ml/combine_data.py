import pandas as pd


# ==========================================
# FILE LOCATIONS
# ==========================================

legitimate_file = "datasets/legitimate_augmented.csv"
phishing_file = "datasets/phishing.csv"

output_file = "datasets/training_data.csv"


# ==========================================
# READ DATASETS
# ==========================================

print("Loading datasets...")

legitimate = pd.read_csv(legitimate_file)
phishing = pd.read_csv(phishing_file)


# ==========================================
# MAKE SURE COLUMNS ARE CORRECT
# ==========================================

legitimate = legitimate[["url", "label"]]
phishing = phishing[["url", "label"]]


# ==========================================
# BALANCE THE DATASET
# ==========================================

# We have 120,000 augmented legitimate URLs
# but only 20,000 phishing URLs.
#
# Use 20,000 legitimate URLs so both classes
# have equal representation.

legitimate = legitimate.sample(
    n=len(phishing),
    random_state=42
)


# ==========================================
# COMBINE DATA
# ==========================================

combined = pd.concat(
    [
        legitimate,
        phishing
    ],
    ignore_index=True
)


# ==========================================
# SHUFFLE DATA
# ==========================================

combined = combined.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


# ==========================================
# SAVE DATASET
# ==========================================

combined.to_csv(
    output_file,
    index=False
)


# ==========================================
# DISPLAY INFORMATION
# ==========================================

print()
print("========================================")
print("TRAINING DATASET CREATED")
print("========================================")

print("Legitimate URLs:", len(legitimate))
print("Phishing URLs:", len(phishing))
print("Total samples:", len(combined))

print()
print("Class distribution:")

print(combined["label"].value_counts())

print()
print("First 10 rows:")

print(combined.head(10))

print()
print("Saved to:")
print(output_file)