#!/usr/bin/env python3
"""CA_Migratory_Bird_scrape.py — HuntIntel California Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://wildlife.ca.gov/Hunting/Waterfowl"
LICENSE_URL = "https://wildlife.ca.gov/Licensing/Hunting/Items"
PURCHASE_URL = "https://wildlife.ca.gov/Licensing/Online-Sales"
LICENSE_PURCHASE_URLS = [
    {"label": "CDFW — Online License Sales", "url": "https://wildlife.ca.gov/Licensing/Online-Sales"},
    {"label": "CDFW — License Fees", "url": "https://wildlife.ca.gov/Licensing/Hunting/Items"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | CDFW",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from CDFW. California has 5 duck zones (Northeastern, SSJV, SoCal, Colorado River, Balance of State) and multiple goose zones.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "December 28, 2026",
         "season_raw": "Sep 1-15 & Nov 14 - Dec 28 (split season)",
         "hunting_units": "Statewide", "bag_limit": "15 daily (max 10 white-winged)",
         "possession_limit": "45"},
        {"name": "Band-tailed Pigeon", "asterisk": True,
         "season_start": "September 19, 2026", "season_end": "September 27, 2026",
         "season_raw": "Northern Zone: Sep 19-27; Southern Zone: Sep 26 - Oct 4",
         "hunting_units": "Northern and Southern Zones", "bag_limit": "2 daily",
         "possession_limit": "6"},
        {"name": "Duck (Northeastern Zone)", "asterisk": True,
         "season_start": "October 3, 2026", "season_end": "January 13, 2027",
         "season_raw": "Oct 3 - Jan 13. Scaup: Oct 3-Nov 29 & Dec 17-Jan 13.",
         "hunting_units": "Northeastern Zone",
         "bag_limit": "7 ducks daily (max 7 mallards ≤2 females, 3 pintail, 2 canvasback, 2 redhead, 2 scaup)",
         "possession_limit": "21 (triple bag)"},
        {"name": "Duck (Southern Zones)", "asterisk": True,
         "season_start": "October 24, 2026", "season_end": "January 31, 2027",
         "season_raw": "SSJV, SoCal, Colorado River, Balance of State: Oct 24 - Jan 31. Scaup: Nov 7 - Jan 31.",
         "hunting_units": "SSJV, SoCal, Colorado River, Balance of State",
         "bag_limit": "7 ducks daily (same species limits as NE zone)",
         "possession_limit": "21",
         "sub_seasons": [
             {"name": "Southern San Joaquin Valley", "season_start": "October 24, 2026", "season_end": "January 31, 2027",
              "bag_limit": "7 ducks daily", "possession_limit": "21"},
             {"name": "Southern California", "season_start": "October 24, 2026", "season_end": "January 31, 2027",
              "bag_limit": "7 ducks daily", "possession_limit": "21"},
             {"name": "Colorado River", "season_start": "October 23, 2026", "season_end": "January 31, 2027",
              "bag_limit": "7 ducks daily (max 2 Mexican ducks)", "possession_limit": "21"},
             {"name": "Balance of State", "season_start": "October 24, 2026", "season_end": "January 31, 2027",
              "bag_limit": "7 ducks daily", "possession_limit": "21"},
         ]},
        {"name": "Coot & Moorhen (Gallinule)", "asterisk": False,
         "season_start": "October 3, 2026", "season_end": "January 31, 2027",
         "season_raw": "Concurrent with duck season in each zone",
         "hunting_units": "Statewide", "bag_limit": "25 daily", "possession_limit": "75"},
        {"name": "Goose", "asterisk": True,
         "season_start": "October 3, 2026", "season_end": "March 10, 2027",
         "season_raw": "Varies by zone. NE: Oct 3-Jan 10 (Canada), Oct 3-Nov 29 & Jan 1-13 (white/w-front). Balance of State: Oct 24-Jan 31. Late season Feb-Mar.",
         "hunting_units": "Multiple zones (NE, SSJV, SoCal, Colorado River, Balance of State)",
         "bag_limit": "30/day max (20 white geese, 10 dark geese; ≤6 white-fronted, ≤3 large Canada)",
         "possession_limit": "90 (triple bag)"},
        {"name": "Brant (Black Brant)", "asterisk": True,
         "season_start": "November 29, 2026", "season_end": "December 14, 2026",
         "season_raw": "Northern Zone: Nov 29 - Dec 14; Balance of State: Nov 30 - Dec 15",
         "hunting_units": "Coastal areas", "bag_limit": "2 daily", "possession_limit": "6"},
    ]

def build_licenses():
    return [
        {"name": "Resident Hunting License", "asterisk": False,
         "covers": "Required for all hunting", "resident_cost": "$54.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Hunting License", "asterisk": False,
         "covers": "Hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$150.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "California Duck Validation", "asterisk": True,
         "covers": "Required for waterfowl hunting (not required for Junior license holders)",
         "resident_cost": "$39.96", "nonresident_cost": "$39.96", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "HIP Validation", "asterisk": True,
         "covers": "Required for all migratory bird hunters (free)",
         "resident_cost": "Free", "nonresident_cost": "Free", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "California has 5 duck zones (Northeastern, SSJV, Southern California, Colorado River, Balance of State) with different opening dates. The NE zone opens Oct 3; southern zones open Oct 24.",
         "applies_to": ["Duck (Northeastern Zone)", "Duck (Southern Zones)"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Duck Zones",
                      "evidence": "NE Zone: Oct 3 - Jan 13. SSJV, SoCal, Balance: Oct 24 - Jan 31. Colorado River: Oct 23 - Jan 31."}]},
        {"title": "The California Duck Validation ($39.96) is required for waterfowl hunting. The Upland Game Bird Validation ($24.84) is separate. HIP validation is free.",
         "applies_to": ["California Duck Validation", "HIP Validation"],
         "sources": [{"url": LICENSE_URL, "label": "CDFW — License Fees",
                      "evidence": "California Duck Validation: $39.96. Upland Game Bird Validation: $24.84. HIP: Free."}]},
        {"title": "Dove season is split: Sep 1-15 and Nov 14 - Dec 28. Bag limit is 15 daily (max 10 white-winged). Eurasian collared-doves are year-round with no limit.",
         "applies_to": ["Dove (Mourning & White-winged)"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Dove Season",
                      "evidence": "Dove: Sep 1-15 & Nov 14 - Dec 28. 15 daily (10 white-winged max)."}]},
        {"title": "Nonlead ammunition is required for all hunting in California. HIP registration is free and required for all migratory bird hunters.",
         "applies_to": ["Resident Hunting License", "HIP Validation"],
         "sources": [{"url": "https://wildlife.ca.gov/Hunting/Nonlead-Ammunition", "label": "CDFW — Nonlead",
                      "evidence": "Nonlead ammunition required when taking any wildlife with a firearm anywhere in California."}]},
    ]

def build_dataset():
    print(f"[CA_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[CA_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "California", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | CDFW",
            "last_updated": None, "update_note": "Data from CDFW waterfowl page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape CDFW migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/CA_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[CA_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
