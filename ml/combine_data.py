import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
legitimate_file = base_dir / "datasets" / "legitimate_augmented.csv"
phishing_file = base_dir / "datasets" / "phishing.csv"
output_file = base_dir / "datasets" / "training_data.csv"

print("Loading datasets...")
legitimate = pd.read_csv(legitimate_file)
phishing = pd.read_csv(phishing_file)

legitimate = legitimate[["url", "label"]].dropna().drop_duplicates(subset=["url"])
phishing = phishing[["url", "label"]].dropna().drop_duplicates(subset=["url"])

# Balance the classes evenly
sample_count = min(len(legitimate), len(phishing))
print(f"Balancing dataset: selecting {sample_count:,} legitimate and {sample_count:,} phishing URLs...")

legitimate_sample = legitimate.sample(n=sample_count, random_state=42)
phishing_sample = phishing.sample(n=sample_count, random_state=42)

combined = pd.concat([legitimate_sample, phishing_sample], ignore_index=True)
combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

combined.to_csv(output_file, index=False)

print("\n========================================")
print("TRAINING DATASET CREATED")
print("========================================")
print(f"Legitimate URLs : {len(legitimate_sample):,}")
print(f"Phishing URLs   : {len(phishing_sample):,}")
print(f"Total samples   : {len(combined):,}")
print("\nClass distribution:")
print(combined["label"].value_counts())
print(f"\nSaved to: {output_file}")