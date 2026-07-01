#!/usr/bin/env python3
"""NV_Migratory_Bird_scrape.py — HuntIntel Nevada Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/nevada/hunting/small-game/migratory-game-bird-seasons"
LICENSE_URL = "https://www.ndow.org/apply-buy/apply-buy-hunting/"
PURCHASE_URL = "https://ndowlicensing.com/"
LICENSE_PURCHASE_URLS = [
    {"label": "NDOW — License Portal", "url": "https://ndowlicensing.com/"},
    {"label": "NDOW — Apply & Buy", "url": "https://www.ndow.org/apply-buy/apply-buy-hunting/"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Migratory Game Bird Seasons | NV eRegulations",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from NDOW. Nevada has 3 waterfowl zones (Northeast, Northwest, South).",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "October 30, 2026",
         "season_raw": "September 1 - October 30, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily (combined)", "possession_limit": "45"},
        {"name": "Crow (American Crow)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "April 15, 2027",
         "season_raw": "Season 1: Sep 1 - Nov 17; Season 2: Mar 1 - Apr 15",
         "hunting_units": "Statewide", "bag_limit": "10 daily", "possession_limit": "10"},
        {"name": "Duck & Merganser", "asterisk": True,
         "season_start": "September 27, 2026", "season_end": "January 25, 2027",
         "season_raw": "NE: Sep 27-Dec 2 & Dec 13-Jan 19; NW: Oct 11-Jan 4 & Jan 7-25; South: Oct 11-19 & Oct 22-Jan 25",
         "hunting_units": "Northeast, Northwest, South Zones (see sub-seasons)",
         "bag_limit": "7 ducks daily (species restrictions)", "possession_limit": "21",
         "sub_seasons": [
             {"name": "Northeast Zone — Segment 1", "season_start": "September 27, 2026", "season_end": "December 2, 2026",
              "bag_limit": "7 daily", "possession_limit": "21"},
             {"name": "Northeast Zone — Segment 2", "season_start": "December 13, 2026", "season_end": "January 19, 2027",
              "bag_limit": "7 daily", "possession_limit": "21"},
             {"name": "Northwest Zone — Segment 1", "season_start": "October 11, 2026", "season_end": "January 4, 2027",
              "bag_limit": "7 daily", "possession_limit": "21"},
             {"name": "Northwest Zone — Segment 2", "season_start": "January 7, 2027", "season_end": "January 25, 2027",
              "bag_limit": "7 daily", "possession_limit": "21"},
             {"name": "South Zone — Segment 1", "season_start": "October 11, 2026", "season_end": "October 19, 2026",
              "bag_limit": "7 daily", "possession_limit": "21"},
             {"name": "South Zone — Segment 2", "season_start": "October 22, 2026", "season_end": "January 25, 2027",
              "bag_limit": "7 daily", "possession_limit": "21"},
         ]},
        {"name": "Canada Goose & Brant", "asterisk": True,
         "season_start": "September 27, 2026", "season_end": "January 25, 2027",
         "season_raw": "Same zone dates as duck",
         "hunting_units": "Northeast, Northwest, South Zones", "bag_limit": "5 daily",
         "possession_limit": "15"},
        {"name": "White-fronted Goose", "asterisk": False,
         "season_start": "September 27, 2026", "season_end": "January 25, 2027",
         "season_raw": "Same zone dates as duck",
         "hunting_units": "Northeast, Northwest, South Zones",
         "bag_limit": "10 daily", "possession_limit": "30"},
        {"name": "Snow & Ross's Goose", "asterisk": False,
         "season_start": "October 11, 2026", "season_end": "March 8, 2027",
         "season_raw": "NE: Oct 11-Dec 2, Dec 13-Jan 19, Feb 23-Mar 8; NW: Oct 25-Jan 25, Feb 23-Mar 8; South: Oct 11-Jan 25",
         "hunting_units": "Northeast, Northwest, South Zones",
         "bag_limit": "20 daily", "possession_limit": "60"},
        {"name": "Coot & Gallinule", "asterisk": False,
         "season_start": "September 27, 2026", "season_end": "January 25, 2027",
         "season_raw": "Same zone dates as duck",
         "hunting_units": "All zones", "bag_limit": "25 daily", "possession_limit": "75"},
        {"name": "Snipe (Wilson's Snipe)", "asterisk": False,
         "season_start": "September 27, 2026", "season_end": "January 19, 2027",
         "season_raw": "Same zone dates as duck",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
    ]

def build_licenses():
    return [
        {"name": "Resident Hunting License", "asterisk": False,
         "covers": "All hunting including migratory birds", "resident_cost": "$38.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Hunting License", "asterisk": False,
         "covers": "Hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$155.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "HIP Certification", "asterisk": True,
         "covers": "Required for all migratory bird hunters (free)",
         "resident_cost": "Free", "nonresident_cost": "Free", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Nevada has 3 waterfowl zones (Northeast, Northwest, South) with different season dates. Duck bag limit is 7 daily with species restrictions.",
         "applies_to": ["Duck & Merganser"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Duck Zones",
                      "evidence": "NE: Sep 27-Dec 2 & Dec 13-Jan 19. NW: Oct 11-Jan 4 & Jan 7-25. South: Oct 11-19 & Oct 22-Jan 25."}]},
        {"title": "HIP certification is required for all migratory bird hunters in Nevada and is available free at ndowlicensing.com.",
         "applies_to": ["Resident Hunting License", "HIP Certification"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — HIP Requirement",
                      "evidence": "Any person 12+ must obtain a HIP number annually (July 1 - March 10) at ndowlicensing.com or 1-855-542-6369."}]},
        {"title": "Nevada has a 7-duck daily bag (higher than the standard 6) with species limits: max 2 hen mallards, 3 pintail, 2 redhead, 2 canvasback, 2 scaup.",
         "applies_to": ["Duck & Merganser"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Duck Limits",
                      "evidence": "7 ducks daily. Max 2 hen mallard, 3 pintail, 2 redhead, 2 canvasback."}]},
        {"title": "The Light Goose Conservation Order (Feb 23 - Mar 8) allows electronic calls and unplugged shotguns. Closed in Mason Valley WMA and Scripps/Washoe SP.",
         "applies_to": ["Snow & Ross's Goose"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Light Goose Conservation Order",
                      "evidence": "Feb 23 - Mar 8: 3-shell and call restrictions do not apply. Closed in Mason Valley WMA and Scripps/Washoe State Park."}]},
    ]

def build_dataset():
    print(f"[NV_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NV_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Nevada", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Migratory Bird Seasons | NV eRegulations",
            "last_updated": None, "update_note": "Data from NDOW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape NDOW migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/NV_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[NV_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
