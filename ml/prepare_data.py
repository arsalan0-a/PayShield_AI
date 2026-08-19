import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
input_file = base_dir / "datasets" / "online-valid.csv"
output_file = base_dir / "datasets" / "phishing.csv"

print(f"Reading phishing dataset from {input_file}...")
df = pd.read_csv(input_file)

print("Columns in dataset:", df.columns.tolist())

# Filter for verified phishing records if available
if "verified" in df.columns:
    df = df[df["verified"].astype(str).str.lower() == "yes"]

# Clean URLs
df = df.dropna(subset=["url"])
df["url"] = df["url"].astype(str).str.strip()
df = df.drop_duplicates(subset=["url"])

# Take up to 35,000 unique phishing URLs
sample_size = min(35000, len(df))
df = df.head(sample_size)

# Keep only the URL column and add label 1
df_clean = pd.DataFrame({
    "url": df["url"],
    "label": 1
})

df_clean.to_csv(output_file, index=False)

print("\nSuccessfully created phishing.csv")
print("Number of phishing URLs:", len(df_clean))
print("\nFirst 5 rows:")
print(df_clean.head())