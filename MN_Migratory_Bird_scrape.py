#!/usr/bin/env python3
"""MN_Migratory_Bird_scrape.py — HuntIntel Minnesota Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.dnr.state.mn.us/hunting/waterfowl/index.html"
SEASONS_URL = "https://www.dnr.state.mn.us/hunting/seasons.html"
LICENSE_URL = "https://www.dnr.state.mn.us/licenses/hunting/index.html"
PURCHASE_URL = "https://www.dnr.state.mn.us/licenses/index.html"
LICENSE_PURCHASE_URLS = [
    {"label": "MN DNR — License Portal", "url": "https://www.dnr.state.mn.us/licenses/index.html"},
    {"label": "MN DNR — Hunting Licenses", "url": "https://www.dnr.state.mn.us/licenses/hunting/index.html"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | Minnesota DNR",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from MN DNR waterfowl and seasons pages. 3 duck/goose zones: North, Central, South. 2026-27 dates based on recurring annual patterns.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning Dove)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 1 - November 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily", "possession_limit": "45"},
        {"name": "Teal (Early Teal)", "asterisk": False,
         "season_start": "September 5, 2026", "season_end": "September 9, 2026",
         "season_raw": "September 5 - 9, 2026 (sunrise to sunset)",
         "hunting_units": "Statewide", "bag_limit": "6 daily (blue-winged, green-winged, cinnamon)", "possession_limit": "18"},
        {"name": "Duck, Coot & Merganser", "asterisk": True,
         "season_start": "September 27, 2026", "season_end": "December 7, 2026",
         "season_raw": "North: Sep 27-Nov 25; Central: Sep 27-Oct 5 & Oct 11-Nov 30; South: Sep 27-Oct 5 & Oct 18-Dec 7",
         "hunting_units": "North, Central, South Zones (see sub-seasons)",
         "bag_limit": "6 ducks daily (species restrictions), 15 coot daily, 5 merganser daily",
         "possession_limit": "18 (3x daily bag)",
         "sub_seasons": [
             {"name": "North Zone", "season_start": "September 27, 2026", "season_end": "November 25, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Zone — Segment 1", "season_start": "September 27, 2026", "season_end": "October 5, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Zone — Segment 2", "season_start": "October 11, 2026", "season_end": "November 30, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 1", "season_start": "September 27, 2026", "season_end": "October 5, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 2", "season_start": "October 18, 2026", "season_end": "December 7, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Goose", "asterisk": True,
         "season_start": "September 6, 2026", "season_end": "January 7, 2027",
         "season_raw": "Early: Sep 6-21; Regular: North Sep 27-Dec 26; Central Sep 27-Oct 5 & Oct 11-Dec 31; South Sep 27-Oct 5 & Oct 18-Jan 7",
         "hunting_units": "North, Central, South Zones (see sub-seasons)",
         "bag_limit": "5 Canada/white-fronted/brant daily, 20 light geese daily",
         "possession_limit": "15 Canada, none light geese",
         "sub_seasons": [
             {"name": "Early Goose (Statewide)", "season_start": "September 6, 2026", "season_end": "September 21, 2026",
              "bag_limit": "5 Canada/white-fronted/brant; 20 light geese", "possession_limit": "15"},
             {"name": "North Zone Regular", "season_start": "September 27, 2026", "season_end": "December 26, 2026",
              "bag_limit": "5 Canada/brant; 20 light geese", "possession_limit": "15"},
             {"name": "Central Zone — Segment 1", "season_start": "September 27, 2026", "season_end": "October 5, 2026",
              "bag_limit": "5 Canada/brant; 20 light geese", "possession_limit": "15"},
             {"name": "Central Zone — Segment 2", "season_start": "October 11, 2026", "season_end": "December 31, 2026",
              "bag_limit": "5 Canada/brant; 20 light geese", "possession_limit": "15"},
             {"name": "South Zone — Segment 1", "season_start": "September 27, 2026", "season_end": "October 5, 2026",
              "bag_limit": "5 Canada/brant; 20 light geese", "possession_limit": "15"},
             {"name": "South Zone — Segment 2", "season_start": "October 18, 2026", "season_end": "January 7, 2027",
              "bag_limit": "5 Canada/brant; 20 light geese", "possession_limit": "15"},
         ]},
        {"name": "Woodcock", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "November 2, 2026",
         "season_raw": "September 19 - November 2, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Common Snipe", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 3, 2026",
         "season_raw": "September 1 - November 3, 2026",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Sora & Virginia Rail", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 3, 2026",
         "season_raw": "September 1 - November 3, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 daily (combined)", "possession_limit": "75"},
    ]

def build_licenses():
    return [
        {"name": "Resident Small Game License", "asterisk": False,
         "covers": "Small game including dove, snipe, rail, woodcock",
         "resident_cost": "$22.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Resident Migratory Waterfowl Stamp", "asterisk": True,
         "covers": "Required in addition to Small Game license for waterfowl (ducks, geese)",
         "resident_cost": "$7.50", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Migratory Waterfowl Stamp", "asterisk": True,
         "covers": "Required for nonresidents to hunt waterfowl",
         "resident_cost": None, "nonresident_cost": "$7.50", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "72-Hour Small Game License", "asterisk": False,
         "covers": "Includes pheasant stamp and waterfowl stamp; 72-hour duration",
         "resident_cost": "$19.00", "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "A Minnesota Migratory Waterfowl Stamp ($7.50) is required in addition to a Small Game license to hunt waterfowl. HIP certification is free and required.",
         "applies_to": ["Resident Small Game License", "Resident Migratory Waterfowl Stamp", "Nonresident Migratory Waterfowl Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "MN DNR — License Fees",
                      "evidence": "Migratory Waterfowl Stamp: $7.50. Required to hunt waterfowl. HIP certification required for all migratory bird hunters."}]},
        {"title": "Minnesota has 3 waterfowl zones (North, Central, South) with different duck and goose season dates.",
         "applies_to": ["Duck, Coot & Merganser", "Goose"],
         "sources": [{"url": SOURCE_URL, "label": "MN DNR — Waterfowl Zones",
                      "evidence": "Three zones: North, Central, South with different season dates."}]},
        {"title": "Early teal season shooting hours begin at sunrise (no pre-sunrise shooting). Regular waterfowl: 1/2 hr before sunrise to sunset.",
         "applies_to": ["Teal (Early Teal)", "Duck, Coot & Merganser", "Goose"],
         "sources": [{"url": SOURCE_URL, "label": "MN DNR — Shooting Hours",
                      "evidence": "Early teal season: shooting begins at sunrise. Regular waterfowl: 1/2 hour before sunrise to sunset."}]},
        {"title": "Duck species restrictions: 4 mallards max (2 hens), 3 wood ducks, 2 redheads, 2 canvasbacks, 2 black ducks, 2 pintails. Scaup limits vary by zone/date.",
         "applies_to": ["Duck, Coot & Merganser"],
         "sources": [{"url": SOURCE_URL, "label": "MN DNR — Duck Limits",
                      "evidence": "Mallard: 4 (max 2 hens). Wood duck: 3. Redhead: 2. Canvasback: 2. Black duck: 2. Pintail: 2. Scaup limits vary by zone and date."}]},
    ]

def build_dataset():
    print(f"[MN_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MN_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Minnesota", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | MN DNR",
            "last_updated": None, "update_note": "Data from MN DNR waterfowl page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MN DNR migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MN_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MN_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
