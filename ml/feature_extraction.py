import re
import math
from urllib.parse import urlparse
import tldextract
import pandas as pd
from pathlib import Path

# Pre-configure tldextract cache to avoid network delays
extractor = tldextract.TLDExtract(cache_dir=str(Path(__file__).resolve().parent / ".tld_cache"))

# Load top 20,000 domains for authority and whitelist feature
TOP_DOMAINS = set()
try:
    top_file = Path(__file__).resolve().parent.parent / "datasets" / "top-1m.csv"
    if top_file.exists():
        top_df = pd.read_csv(top_file, header=None, nrows=20000)
        TOP_DOMAINS = set(top_df[1].str.lower().str.strip().dropna())
except Exception:
    TOP_DOMAINS = set()

# Known high-abuse Top-Level Domains frequently used in phishing

HIGH_RISK_TLDS = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "club",
    "icu", "work", "rest", "cam", "vip", "fit", "surf", "stream",
    "cn", "pw", "cc", "ws", "info", "monster", "online", "site",
    "space", "fun", "uno", "link", "click", "live", "guru"
}

# Major target brands frequently spoofed
TARGET_BRANDS = {
    "paypal", "google", "apple", "microsoft", "amazon", "netflix",
    "facebook", "instagram", "whatsapp", "chase", "bankofamerica",
    "wellsfargo", "citibank", "citi", "binance", "coinbase", "metamask",
    "steam", "ebay", "walmart", "yahoo", "outlook", "icloud",
    "dropbox", "adobe", "linkedin", "twitter", "spotify", "telegram",
    "roblox", "usps", "dhl", "fedex", "ups", "irs"
}

# URL shorteners
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly",
    "ow.ly", "buff.ly", "rebrand.ly", "tiny.cc", "soo.gd", "s.id"
}

AUTH_WORDS = ["login", "signin", "auth", "oauth", "sso", "session", "credential", "password"]
FINANCIAL_WORDS = ["bank", "banking", "pay", "payment", "wallet", "crypto", "invoice", "billing", "card"]
URGENCY_WORDS = ["verify", "verification", "update", "secure", "security", "confirm", "alert", "suspend", "kyc", "otp"]
LURE_WORDS = ["bonus", "free", "reward", "gift", "claim", "prize", "winner", "giveaway"]


def calculate_entropy(text: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not text:
        return 0.0
    freq = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    entropy = 0.0
    length = len(text)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return float(round(entropy, 4))


def extract_features(url: str) -> dict:
    """
    Extract comprehensive lexical, structural, and semantic features from a URL.
    Returns a flat dictionary of numeric features suitable for ML inference.
    """
    url = str(url).strip()
    if not url.startswith(("http://", "https://")):
        url_for_parse = "https://" + url
    else:
        url_for_parse = url

    parsed = urlparse(url_for_parse)
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    url_lower = url.lower()

    # Extract domain components with tldextract
    ext = extractor(url_for_parse)
    subdomain = ext.subdomain.lower() if ext.subdomain else ""
    domain = ext.domain.lower() if ext.domain else ""
    suffix = ext.suffix.lower() if ext.suffix else ""
    registered_domain = f"{domain}.{suffix}" if (domain and suffix) else domain

    # 1. IP address in hostname (IPv4 / IPv6)
    ipv4_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"
    contains_ip = 1 if re.match(ipv4_pattern, hostname) else 0

    # 2. Port specification
    has_custom_port = 1 if (parsed.port and parsed.port not in [80, 443]) else 0

    # 3. High-risk TLD
    is_suspicious_tld = 1 if suffix in HIGH_RISK_TLDS else 0

    # 4. URL Shortener
    is_shortened = 1 if hostname in SHORTENERS or registered_domain in SHORTENERS else 0

    # 5. Brand Impersonation / Spoofing
    # Detect if a target brand name appears in subdomain, path, or query when the registered domain is NOT that brand
    brand_spoofed = 0
    for brand in TARGET_BRANDS:
        if brand != domain:
            if brand in subdomain or brand in path.lower() or f"-{brand}" in domain or f"{brand}-" in domain:
                brand_spoofed = 1
                break

    # 6. Sensitive keyword categories by context
    auth_words_subdomain = sum(1 for w in AUTH_WORDS if w in subdomain)
    auth_words_path = sum(1 for w in AUTH_WORDS if w in path.lower())
    financial_words_subdomain = sum(1 for w in FINANCIAL_WORDS if w in subdomain)
    financial_words_path = sum(1 for w in FINANCIAL_WORDS if w in path.lower())
    urgency_words_subdomain = sum(1 for w in URGENCY_WORDS if w in subdomain)
    urgency_words_path = sum(1 for w in URGENCY_WORDS if w in path.lower())
    lure_words_count = sum(1 for w in LURE_WORDS if w in url_lower)

    # 7. Subdomain depth and lengths
    subdomain_parts = [p for p in subdomain.split(".") if p] if subdomain else []
    subdomain_depth = len(subdomain_parts)

    # 8. Character & structural counts
    url_len = len(url)
    hostname_len = len(hostname)
    path_len = len(path)
    query_len = len(query)

    dot_count_hostname = hostname.count(".")
    dot_count_path = path.count(".")
    hyphen_count_hostname = hostname.count("-")
    hyphen_count_path = path.count("-")
    underscore_count = url.count("_")
    slash_count = url.count("/")
    question_mark_count = url.count("?")
    equal_count = url.count("=")
    at_count = url.count("@")
    percent_count = url.count("%")

    # 9. Digit counts and ratios
    digits_hostname = sum(c.isdigit() for c in hostname)
    digits_total = sum(c.isdigit() for c in url)
    digit_ratio_hostname = digits_hostname / max(hostname_len, 1)
    digit_ratio_url = digits_total / max(url_len, 1)

    # 10. Vowel / Consonant ratio in domain
    letters_domain = [c for c in domain if c.isalpha()]
    vowels_domain = sum(1 for c in letters_domain if c in "aeiou")
    vowel_ratio_domain = vowels_domain / max(len(letters_domain), 1)

    # 11. Entropies
    entropy_url = calculate_entropy(url)
    entropy_hostname = calculate_entropy(hostname)
    entropy_path = calculate_entropy(path)

    # 12. Double slash in path (redirect trick)
    double_slash_path = 1 if "//" in path else 0

    # 13. HTTPS usage
    is_https = 1 if url_lower.startswith("https://") else 0

    # 14. Query parameters count
    param_count = len(query.split("&")) if query else 0

    # 15. Directory depth
    dir_depth = len([p for p in path.split("/") if p])

    # 16. Top domain / authority check
    is_top_domain = 1 if (registered_domain in TOP_DOMAINS and brand_spoofed == 0 and contains_ip == 0) else 0

    # 17. Standard subdomain check (e.g. www or none vs complex deceptive subdomains)
    subdomain_is_standard = 1 if subdomain in ["", "www", "m"] else 0


    return {
        "url_length": url_len,
        "hostname_length": hostname_len,
        "path_length": path_len,
        "query_length": query_len,
        "dot_count_hostname": dot_count_hostname,
        "dot_count_path": dot_count_path,
        "hyphen_count_hostname": hyphen_count_hostname,
        "hyphen_count_path": hyphen_count_path,
        "underscore_count": underscore_count,
        "slash_count": slash_count,
        "question_mark_count": question_mark_count,
        "equal_count": equal_count,
        "at_count": at_count,
        "percent_count": percent_count,
        "digit_count_hostname": digits_hostname,
        "digit_ratio_hostname": round(digit_ratio_hostname, 4),
        "digit_ratio_url": round(digit_ratio_url, 4),
        "vowel_ratio_domain": round(vowel_ratio_domain, 4),
        "entropy_url": entropy_url,
        "entropy_hostname": entropy_hostname,
        "entropy_path": entropy_path,
        "subdomain_count": subdomain_depth,
        "subdomain_length": len(subdomain),
        "contains_ip": contains_ip,
        "has_custom_port": has_custom_port,
        "is_suspicious_tld": is_suspicious_tld,
        "is_shortened": is_shortened,
        "brand_spoofed": brand_spoofed,
        "auth_words_subdomain": auth_words_subdomain,
        "auth_words_path": auth_words_path,
        "financial_words_subdomain": financial_words_subdomain,
        "financial_words_path": financial_words_path,
        "urgency_words_subdomain": urgency_words_subdomain,
        "urgency_words_path": urgency_words_path,
        "lure_words_count": lure_words_count,
        "double_slash_path": double_slash_path,
        "https": is_https,
        "param_count": param_count,
        "dir_depth": dir_depth,
        "is_top_domain": is_top_domain,
        "subdomain_is_standard": subdomain_is_standard
    }



if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    input_file = base_dir / "datasets" / "training_data.csv"
    output_file = base_dir / "datasets" / "features.csv"

    print(f"Loading training data from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Total URLs: {len(df):,}")

    features = []
    total = len(df)
    for index, row in df.iterrows():
        url_feats = extract_features(str(row["url"]))
        url_feats["label"] = int(row["label"])
        features.append(url_feats)

        if (index + 1) % 5000 == 0 or (index + 1) == total:
            print(f"Processed {index + 1:,} / {total:,} URLs ({(index + 1)/total*100:.1f}%)...")

    features_df = pd.DataFrame(features)
    features_df.to_csv(output_file, index=False)
    print(f"\nFeature extraction completed and saved to {output_file}")
    print(f"Samples: {len(features_df):,}, Features: {len(features_df.columns)}")