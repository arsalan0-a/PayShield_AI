import pandas as pd

# PhishTank dataset
input_file = r"C:\Users\Amaan\OneDrive\Desktop\Project\PayShield_AI\datasets\online-valid.csv"

# Our new phishing dataset
output_file = r"C:\Users\Amaan\OneDrive\Desktop\Project\PayShield_AI\datasets\phishing.csv"

# Read the PhishTank CSV
df = pd.read_csv(input_file)

# Display the column names so we can verify the dataset
print("Columns in dataset:")
print(df.columns.tolist())

# Take the first 20,000 phishing URLs
df = df.head(20000)

# Keep only the URL column
df = df[["url"]]

# Add label
# 1 = phishing
df["label"] = 1

# Save the cleaned dataset
df.to_csv(output_file, index=False)

print("\nSuccessfully created phishing.csv")
print("Number of phishing URLs:", len(df))

print("\nFirst 10 rows:")
print(df.head(10))