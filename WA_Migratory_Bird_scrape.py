#!/usr/bin/env python3
"""WA_Migratory_Bird_scrape.py — HuntIntel Washington Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/washington/hunting/game-bird/migratory-game-bird-seasons"
LICENSE_URL = "https://wdfw.wa.gov/licenses/hunting/small-game"
PURCHASE_URL = "https://wdfw.wa.gov/licenses/hunting"
LICENSE_PURCHASE_URLS = [
    {"label": "WDFW — License Portal", "url": "https://wdfw.wa.gov/licenses/hunting"},
    {"label": "WDFW — Small Game Licenses", "url": "https://wdfw.wa.gov/licenses/hunting/small-game"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "WA Migratory Game Bird Seasons | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from WDFW regulations. Washington is in the Pacific Flyway with complex goose management areas.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning Dove)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "October 30, 2026",
         "season_raw": "September 1 - October 30, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily", "possession_limit": "45"},
        {"name": "Band-tailed Pigeon", "asterisk": False,
         "season_start": "September 15, 2026", "season_end": "September 23, 2026",
         "season_raw": "September 15 - 23, 2026",
         "hunting_units": "Statewide", "bag_limit": "2 daily", "possession_limit": "6"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "October 11, 2026", "season_end": "January 25, 2027",
         "season_raw": "Oct 11-19 & Oct 22 - Jan 25 (split season). Youth days: Sep 20 (west), Sep 27 (east).",
         "hunting_units": "Statewide (Pacific Flyway)",
         "bag_limit": "7 ducks daily (species restrictions), 25 coot daily",
         "possession_limit": "21 ducks, 75 coot"},
        {"name": "Snipe (Wilson's Snipe)", "asterisk": False,
         "season_start": "October 11, 2026", "season_end": "January 25, 2027",
         "season_raw": "Oct 11-19 & Oct 22 - Jan 25 (split season)",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Goose (Canada & White-fronted)", "asterisk": True,
         "season_start": "September 6, 2026", "season_end": "January 25, 2027",
         "season_raw": "Early Canada: Sep 6-14 (GMAs 1-3). Regular: Oct 11 - Jan 25 (varies by GMA).",
         "hunting_units": "Goose Management Areas 1-3 (see sub-seasons)",
         "bag_limit": "3 Canada daily (GMA 1&3), 2 Canada (GMA 2); 10 white-fronted; 6-10 white geese",
         "possession_limit": "9 Canada, 30 white-fronted, 18-30 white geese",
         "sub_seasons": [
             {"name": "Early Canada Goose (GMAs 1-3)", "season_start": "September 6, 2026", "season_end": "September 14, 2026",
              "bag_limit": "5 Canada daily", "possession_limit": "15"},
             {"name": "GMA 1 Regular", "season_start": "October 11, 2026", "season_end": "January 25, 2027",
              "bag_limit": "3 Canada, 10 w-front, 6 white daily", "possession_limit": "9/30/18"},
             {"name": "GMA 3 Regular", "season_start": "October 11, 2026", "season_end": "January 25, 2027",
              "bag_limit": "3 Canada, 10 w-front, 10 white daily", "possession_limit": "9/30/30"},
         ]},
    ]

def build_licenses():
    return [
        {"name": "Small Game License (Resident)", "asterisk": False,
         "covers": "Required for all hunting including migratory birds",
         "resident_cost": "$45.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$93.08", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Migratory Bird Permit", "asterisk": True,
         "covers": "Required for all migratory bird hunting (includes HIP)",
         "resident_cost": "$23.27", "nonresident_cost": "$23.27", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "The Washington Migratory Bird Permit ($23.27) is required for all migratory bird hunting in addition to the Small Game License. Includes HIP registration.",
         "applies_to": ["Small Game License (Resident)", "Migratory Bird Permit"],
         "sources": [{"url": LICENSE_URL, "label": "WDFW — License Fees",
                      "evidence": "Migratory Bird Permit: $23.27. Required for all migratory bird hunting."}]},
        {"title": "Washington has a 7-duck daily bag limit (higher than the standard 6 in most states). Species restrictions apply: 2 hen mallards, 3 pintail, 2 scaup, 2 canvasback, 2 redhead.",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Duck Limits",
                      "evidence": "7 ducks daily. Max 2 hen mallard, 3 pintail, 2 scaup, 2 canvasback, 2 redhead."}]},
        {"title": "Washington has 3 Goose Management Areas (GMAs) with different Canada goose bag limits and season dates. Dusky Canada goose is closed.",
         "applies_to": ["Goose (Canada & White-fronted)"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Goose Management Areas",
                      "evidence": "GMA 1&3: 3 Canada daily. GMA 2: 2 Canada daily. Dusky Canada goose closed."}]},
        {"title": "Band-tailed pigeon has a very short season (Sep 15-23) with a 2-bird daily bag limit. Hunters must report band-tailed pigeon harvest.",
         "applies_to": ["Band-tailed Pigeon"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Band-tailed Pigeon",
                      "evidence": "Band-tailed Pigeon: Sep 15-23. 2 daily, 6 possession. Reporting required."}]},
    ]

def build_dataset():
    print(f"[WA_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WA_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Washington", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "WA Migratory Bird Seasons",
            "last_updated": None, "update_note": "Data from WDFW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape WDFW migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/WA_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[WA_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
