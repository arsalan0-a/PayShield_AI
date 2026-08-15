import pandas as pd
import re
from urllib.parse import urlparse


# ==========================================
# FEATURE EXTRACTION FUNCTION
# ==========================================

def extract_features(url):

    # Make sure URL is a string
    url = str(url).strip()

    # Add https temporarily if the URL is only a domain
    if not url.startswith(("http://", "https://")):
        url_for_parse = "https://" + url
    else:
        url_for_parse = url

    # Parse URL
    parsed = urlparse(url_for_parse)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    # Check whether hostname is an IP address
    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    contains_ip = (
        1 if re.match(ip_pattern, hostname) else 0
    )

    # Suspicious words
    suspicious_words = [
        "login",
        "signin",
        "verify",
        "verification",
        "account",
        "update",
        "secure",
        "security",
        "confirm",
        "password",
        "credential",
        "bank",
        "banking",
        "payment",
        "pay",
        "wallet",
        "otp",
        "kyc",
        "bonus",
        "free",
        "claim"
    ]

    url_lower = url.lower()

    suspicious_word_count = sum(
        1 for word in suspicious_words
        if word in url_lower
    )

    # Count subdomains
    hostname_parts = hostname.split(".")

    subdomain_count = max(
        len(hostname_parts) - 2,
        0
    )

    # Count special characters
    special_characters = sum(
        1 for char in url
        if not char.isalnum()
    )

    # Return numerical features
    return {
        "url_length": len(url),

        "hostname_length": len(hostname),

        "path_length": len(path),

        "query_length": len(query),

        "dot_count": url.count("."),

        "hyphen_count": url.count("-"),

        "underscore_count": url.count("_"),

        "slash_count": url.count("/"),

        "question_mark_count": url.count("?"),

        "equal_count": url.count("="),

        "at_count": url.count("@"),

        "digit_count": sum(
            char.isdigit()
            for char in url
        ),

        "special_character_count": special_characters,

        "https": (
            1
            if url.lower().startswith("https://")
            else 0
        ),

        "contains_ip": contains_ip,

        "subdomain_count": subdomain_count,

        "suspicious_word_count":
            suspicious_word_count,

        "has_login":
            1 if "login" in url_lower else 0,

        "has_verify":
            1 if "verify" in url_lower else 0,

        "has_account":
            1 if "account" in url_lower else 0,

        "has_password":
            1 if "password" in url_lower else 0,

        "has_payment":
            1 if "payment" in url_lower else 0,

        "has_otp":
            1 if "otp" in url_lower else 0,

        "has_kyc":
            1 if "kyc" in url_lower else 0
    }


# ==========================================
# DATASET PROCESSING
# ==========================================

if __name__ == "__main__":

    input_file = "datasets/training_data.csv"

    output_file = "datasets/features.csv"

    # Load training data
    df = pd.read_csv(input_file)

    print("Training dataset loaded.")
    print("Total URLs:", len(df))

    # Store extracted features
    features = []

    # Process every URL
    for index, row in df.iterrows():

        url_features = extract_features(
            row["url"]
        )

        # Add the original label
        url_features["label"] = row["label"]

        features.append(url_features)

        # Show progress
        if (index + 1) % 5000 == 0:

            print(
                f"Processed {index + 1} URLs..."
            )

    # Convert to DataFrame
    features_df = pd.DataFrame(features)

    # Save features
    features_df.to_csv(
        output_file,
        index=False
    )

    print("\nFeature extraction completed.")

    print(
        "Total samples:",
        len(features_df)
    )

    print(
        "Number of features:",
        len(features_df.columns)
    )

    print("\nFirst 5 rows:")

    print(
        features_df.head()
    )