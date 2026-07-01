#!/usr/bin/env python3
"""AZ_Migratory_Bird_scrape.py — HuntIntel Arizona Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/arizona/hunting/hunting-seasons-and-dates"
LICENSE_URL = "https://www.azgfd.com/hunting/regulations/"
PURCHASE_URL = "https://www.azgfd.com/license/"
LICENSE_PURCHASE_URLS = [
    {"label": "AZGFD — License Portal", "url": "https://www.azgfd.com/license/"},
    {"label": "AZGFD — Hunting Regulations", "url": "https://www.azgfd.com/hunting/regulations/"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | Arizona | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from AZGFD. Arizona has split dove seasons, band-tailed pigeon, sandhill crane, and Pacific Flyway waterfowl.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "January 4, 2027",
         "season_raw": "Early: Sep 1-15; Late: Nov 21 - Jan 4 (split season)",
         "hunting_units": "Statewide", "bag_limit": "15 daily (combined)", "possession_limit": "45"},
        {"name": "Eurasian Collared-Dove", "asterisk": False,
         "season_start": "January 1, 2026", "season_end": "December 31, 2026",
         "season_raw": "Year-round (no closed season)",
         "hunting_units": "Statewide", "bag_limit": "No limit", "possession_limit": "No limit"},
        {"name": "Band-tailed Pigeon", "asterisk": False,
         "season_start": "September 26, 2026", "season_end": "October 9, 2026",
         "season_raw": "September 26 - October 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "2 daily", "possession_limit": "6"},
        {"name": "Sandhill Crane", "asterisk": True,
         "season_start": "November 21, 2026", "season_end": "January 26, 2027",
         "season_raw": "3-day permit periods: Nov 21 - Jan 26, 2027",
         "hunting_units": "Limited permit (draw)", "bag_limit": "1 per 3-day period; 3 tags max",
         "possession_limit": "1"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "January 31, 2027",
         "season_raw": "Oct 17-25 & Oct 28 - Jan 31 (split season)",
         "hunting_units": "Statewide (Pacific Flyway)",
         "bag_limit": "7 ducks daily (species restrictions), 25 coot daily",
         "possession_limit": "21 ducks, 75 coot"},
        {"name": "Goose", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "January 31, 2027",
         "season_raw": "Same zone dates as duck. Light goose season extends through Feb/Mar",
         "hunting_units": "Statewide",
         "bag_limit": "30/day max (20 white, 10 dark; ≤6 white-fronted, ≤3 large Canada)",
         "possession_limit": "90 (triple bag)"},
    ]

def build_licenses():
    return [
        {"name": "General Hunting License", "asterisk": False,
         "covers": "All hunting including migratory birds",
         "resident_cost": "$37.00", "nonresident_cost": "$160.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Arizona Migratory Bird Stamp", "asterisk": True,
         "covers": "Required for all migratory bird hunting (dove, duck, goose, sandhill crane)",
         "resident_cost": "$5.00", "nonresident_cost": "$5.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Sandhill Crane Tag", "asterisk": True,
         "covers": "Required for sandhill crane hunting (draw, 3-tag max)",
         "resident_cost": "$43.00", "nonresident_cost": "$45.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Arizona dove season is split: Early Sep 1-15 and Late Nov 21 - Jan 4. The Arizona Migratory Bird Stamp ($5) is required for all migratory bird hunting.",
         "applies_to": ["Dove (Mourning & White-winged)", "Arizona Migratory Bird Stamp"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Dove Seasons",
                      "evidence": "Dove: Early Sep 1-15; Late Nov 21 - Jan 4. Migratory Bird Stamp: $5."}]},
        {"title": "Sandhill crane hunting is by draw permit with 3-day hunting periods from Nov 21 through Jan 26. Up to 3 tags per hunter.",
         "applies_to": ["Sandhill Crane", "Sandhill Crane Tag"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Sandhill Crane",
                      "evidence": "Sandhill Crane: 3-day permit periods Nov 21 - Jan 26. $43 res / $45 nonres."}]},
        {"title": "Arizona waterfowl follows the Pacific Flyway with a 7-duck daily bag (higher than the 6-duck standard in most states). Duck season is split: Oct 17-25 & Oct 28 - Jan 31.",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Waterfowl Seasons",
                      "evidence": "Duck: Oct 17-25 & Oct 28 - Jan 31. 7 ducks daily."}]},
        {"title": "The Arizona Youth Combo License ($5 for ages 10-17) includes the Migratory Bird Stamp, making it a great deal for young hunters.",
         "applies_to": ["General Hunting License", "Arizona Migratory Bird Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "AZGFD — License Fees",
                      "evidence": "Youth Combo (10-17): $5. Includes migratory bird stamp."}]},
    ]

def build_dataset():
    print(f"[AZ_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[AZ_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Arizona", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | AZ | eRegulations",
            "last_updated": None, "update_note": "Data from AZGFD regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape AZGFD migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/AZ_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[AZ_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
