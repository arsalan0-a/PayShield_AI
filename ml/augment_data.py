import pandas as pd
import random
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
INPUT_FILE = base_dir / "datasets" / "legitimate.csv"
OUTPUT_FILE = base_dir / "datasets" / "legitimate_augmented.csv"

# Read legitimate domains
df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df):,} legitimate domains from {INPUT_FILE}")

# Diverse realistic templates for legitimate URLs
SUBDOMAINS = [
    "", "www", "app", "login", "accounts", "auth", "my", "secure",
    "portal", "m", "api", "docs", "help", "support", "dashboard"
]

PATHS_AND_QUERIES = [
    "",
    "/",
    "/home",
    "/about",
    "/about-us",
    "/contact",
    "/features",
    "/pricing",
    "/terms",
    "/privacy",
    "/login",
    "/signin",
    "/ap/signin",
    "/ap/register",
    "/users/sign_in",
    "/session/new",
    "/auth/login",
    "/auth/v2/signin",
    "/oauth2/v1/authorize?client_id={num}&response_type=code",
    "/account",
    "/account/overview",
    "/account/security",
    "/security",
    "/security/settings",
    "/security/mfa/verify",
    "/dashboard",
    "/portal/user",
    "/portal/auth",
    "/checkout",
    "/checkout/pay",
    "/pay/confirm",
    "/wallet/balance",
    "/billing/invoice/{num}",
    "/verify/email?token=sec_{num}",
    "/help/center",
    "/docs/quickstart",
    "/wiki/Computer_security",
    "/search?q=documentation",
    "/search?q=security+update&sort=desc",
    "/products/category/item?id={num}&lang=en",
    "/api/v1/status",
    "/download/latest",
    "/blog/news-2026",
    "/faq?ref=footer"
]


augmented = []
random.seed(42)

for _, row in df.iterrows():
    domain = str(row["domain"]).strip().lower()
    if not domain or domain == "nan":
        continue

    # 1. Base domain (https)
    augmented.append({"url": f"https://{domain}", "label": 0})

    # 2. www subdomain
    augmented.append({"url": f"https://www.{domain}", "label": 0})

    # 3. Random realistic subdomains & paths
    # Pick 2-4 realistic patterns per domain
    sample_subdomains = random.sample(SUBDOMAINS, k=random.randint(2, 4))
    for sub in sample_subdomains:
        prefix = f"{sub}.{domain}" if sub and sub != "www" else domain
        path_template = random.choice(PATHS_AND_QUERIES)
        num = random.randint(1000, 999999)
        formatted_path = path_template.format(num=num)
        protocol = "https" if random.random() > 0.05 else "http"
        augmented.append({
            "url": f"{protocol}://{prefix}{formatted_path}",
            "label": 0
        })

result = pd.DataFrame(augmented).drop_duplicates(subset=["url"])
result.to_csv(OUTPUT_FILE, index=False)

print("========================================")
print("LEGITIMATE DATA AUGMENTATION COMPLETE")
print("========================================")
print(f"Original domains : {len(df):,}")
print(f"Augmented URLs   : {len(result):,}")
print(f"Saved to         : {OUTPUT_FILE}")
print("\nSample Augmented URLs:")
print(result.head(10))