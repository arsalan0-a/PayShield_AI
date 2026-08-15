import pandas as pd
import random

INPUT_FILE = "datasets/legitimate.csv"
OUTPUT_FILE = "datasets/legitimate_augmented.csv"

# Read legitimate domains
df = pd.read_csv(INPUT_FILE)

augmented = []

for _, row in df.iterrows():

    domain = str(row["domain"]).strip()

    # Original domain
    augmented.append({
        "url": "https://" + domain,
        "label": 0
    })

    # Legitimate URL with a normal path
    augmented.append({
        "url": "https://" + domain + "/home",
        "label": 0
    })

    # Legitimate URL with a normal page
    augmented.append({
        "url": "https://" + domain + "/about",
        "label": 0
    })

    # Legitimate URL with a search query
    augmented.append({
        "url": "https://" + domain + "/search?q=example",
        "label": 0
    })

    # Legitimate URL with a numeric parameter
    number = random.randint(1000, 999999)

    augmented.append({
        "url": f"https://{domain}/page?id={number}",
        "label": 0
    })

    # Legitimate URL with multiple parameters
    augmented.append({
        "url": f"https://{domain}/search?q=product&page=2",
        "label": 0
    })


result = pd.DataFrame(augmented)

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("========================================")
print("LEGITIMATE DATA AUGMENTATION COMPLETE")
print("========================================")
print("Original domains:", len(df))
print("Augmented URLs:", len(result))
print()
print("Saved to:")
print(OUTPUT_FILE)
print()
print(result.head(10))