"""
Crunchbase → companies.py sync script
--------------------------------------
Run once (or periodically) to pull private/startup companies from Crunchbase
and overwrite the COMPANIES list in companies.py.

Setup:
  1. Sign up at https://data.crunchbase.com and get a free API key
  2. Set your key:  export CRUNCHBASE_API_KEY=your_key_here
  3. pip install requests
  4. python sync_crunchbase.py

The script fetches companies in batches, maps Crunchbase categories → game
sectors, deduplicates, and rewrites the COMPANIES block in companies.py.
"""

import os
import re
import json
import time
import requests

API_KEY  = os.environ.get("CRUNCHBASE_API_KEY", "")
BASE_URL = "https://api.crunchbase.com/api/v4"

# ── How many companies to pull (Basic tier: keep this low to save quota) ──────
TARGET_COUNT = 300

# ── Map Crunchbase category slugs → game sector names ─────────────────────────
CATEGORY_MAP = {
    "artificial-intelligence":      "Gen AI",
    "generative-ai":                "Gen AI",
    "machine-learning":             "Gen AI",
    "natural-language-processing":  "Gen AI",
    "computer-vision":              "Gen AI",
    "large-language-models":        "Gen AI",
    "machine-learning-platform":    "AI Infra",
    "mlops":                        "AI Infra",
    "data-infrastructure":          "AI Infra",
    "cloud-computing":              "AI Infra",
    "cybersecurity":                "Cybersecurity",
    "network-security":             "Cybersecurity",
    "information-security":         "Cybersecurity",
    "fintech":                      "Fintech",
    "payments":                     "Fintech",
    "banking":                      "Fintech",
    "insurance":                    "Fintech",
    "developer-tools":              "Dev Tools",
    "devops":                       "Dev Tools",
    "developer-apis":               "Dev Tools",
    "open-source":                  "Dev Tools",
    "productivity-tools":           "Productivity",
    "collaboration":                "Productivity",
    "project-management":           "Productivity",
    "health-care":                  "Healthcare AI",
    "medical":                      "Healthcare AI",
    "digital-health":               "Healthcare AI",
    "biotechnology":                "Healthcare AI",
    "robotics":                     "Robotics",
    "autonomous-vehicles":          "Autonomous Vehicles",
    "space-technology":             "Space",
    "cleantech":                    "Climate Tech",
    "climate-change":               "Climate Tech",
    "renewable-energy":             "Climate Tech",
    "e-commerce":                   "E-Commerce",
    "retail":                       "E-Commerce",
    "gaming":                       "Gaming",
    "video-games":                  "Gaming",
    "social-media":                 "Social",
    "social-network":               "Social",
    "human-resources":              "HR Tech",
    "recruiting":                   "HR Tech",
    "design":                       "Design",
    "graphic-design":               "Design",
}

DEFAULT_SECTOR = "Other"


def category_to_sector(categories: list[dict]) -> str:
    """Return the best-matching game sector for a list of CB category objects."""
    for cat in categories:
        slug = cat.get("value", "").lower()
        if slug in CATEGORY_MAP:
            return CATEGORY_MAP[slug]
    return DEFAULT_SECTOR


def country_name(location_identifiers: list[dict]) -> str:
    """Extract country from Crunchbase location_identifiers."""
    for loc in location_identifiers:
        if loc.get("location_type") == "country":
            return loc.get("value", "Unknown")
    return "Unknown"


def fetch_batch(after_cursor: str | None, limit: int = 100) -> dict:
    """POST to /searches/organizations and return raw JSON."""
    url = f"{BASE_URL}/searches/organizations"
    payload = {
        "field_ids": [
            "identifier",
            "categories",
            "location_identifiers",
            "funding_stage",
            "num_employees_enum",
        ],
        "limit": limit,
        "query": [
            # Only private companies (startups/unicorns)
            {
                "type": "predicate",
                "field_id": "facet_ids",
                "operator_id": "includes",
                "values": ["company"],
            },
            # Has raised at least a Series A
            {
                "type": "predicate",
                "field_id": "funding_stage",
                "operator_id": "includes",
                "values": [
                    "series_a", "series_b", "series_c",
                    "series_d", "series_e", "series_f",
                    "late_stage_vc", "private_equity",
                ],
            },
        ],
        "order": [{"field_id": "rank_org", "sort": "asc"}],
    }
    if after_cursor:
        payload["after_id"] = after_cursor

    headers = {"X-cb-user-key": API_KEY}
    resp = requests.post(url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def pull_companies(target: int) -> list[dict]:
    """Pull up to `target` companies from Crunchbase, return game-formatted list."""
    companies = []
    seen_names = set()
    cursor = None
    batch_size = min(100, target)

    print(f"Pulling up to {target} companies from Crunchbase...")

    while len(companies) < target:
        remaining = target - len(companies)
        data = fetch_batch(cursor, limit=min(batch_size, remaining))

        entities = data.get("entities", [])
        if not entities:
            print("No more results.")
            break

        for entity in entities:
            props = entity.get("properties", {})
            name = props.get("identifier", {}).get("value", "").strip()
            if not name or name in seen_names:
                continue

            categories = props.get("categories", [])
            locations  = props.get("location_identifiers", [])

            companies.append({
                "name":    name,
                "sector":  category_to_sector(categories),
                "country": country_name(locations),
            })
            seen_names.add(name)

        # Crunchbase pagination uses the last entity's uuid as cursor
        cursor = entities[-1].get("identifier", {}).get("uuid")
        if not cursor:
            break

        print(f"  Fetched {len(companies)} so far...")
        time.sleep(0.5)  # be polite to the API

    print(f"Done. {len(companies)} companies fetched.")
    return companies


def rewrite_companies_py(companies: list[dict]):
    """Overwrite the COMPANIES list in companies.py."""
    path = os.path.join(os.path.dirname(__file__), "companies.py")

    with open(path, "r") as f:
        source = f.read()

    # Build new COMPANIES block
    lines = ["COMPANIES = [\n"]
    by_sector: dict[str, list[dict]] = {}
    for c in companies:
        by_sector.setdefault(c["sector"], []).append(c)

    for sector, items in sorted(by_sector.items()):
        lines.append(f"    # ── {sector} {'─' * max(1, 60 - len(sector))}─\n")
        for c in items:
            name    = c["name"].replace('"', '\\"')
            sector_ = c["sector"].replace('"', '\\"')
            country = c["country"].replace('"', '\\"')
            lines.append(
                f'    {{"name": "{name}", "sector": "{sector_}", "country": "{country}"}},\n'
            )

    lines.append("]\n")
    new_block = "".join(lines)

    # Replace existing COMPANIES = [ ... ] block
    pattern = r"COMPANIES\s*=\s*\[.*?\n\]\n"
    if re.search(pattern, source, re.DOTALL):
        new_source = re.sub(pattern, new_block, source, flags=re.DOTALL)
    else:
        # Fallback: append if pattern not found
        new_source = source + "\n" + new_block

    with open(path, "w") as f:
        f.write(new_source)

    print(f"companies.py updated with {len(companies)} companies.")


def save_json_backup(companies: list[dict]):
    """Save a JSON backup so you don't have to re-fetch."""
    path = os.path.join(os.path.dirname(__file__), "crunchbase_companies.json")
    with open(path, "w") as f:
        json.dump(companies, f, indent=2)
    print(f"Backup saved to crunchbase_companies.json")


if __name__ == "__main__":
    if not API_KEY:
        print("ERROR: Set your Crunchbase API key first:")
        print("  export CRUNCHBASE_API_KEY=your_key_here")
        exit(1)

    companies = pull_companies(TARGET_COUNT)

    if not companies:
        print("No companies returned. Check your API key and quota.")
        exit(1)

    save_json_backup(companies)
    rewrite_companies_py(companies)
    print("\nDone! Restart your Flask app to pick up the new company list.")
    print("NOTE: Delete game_state.json if you want prices to reset to $10.")
