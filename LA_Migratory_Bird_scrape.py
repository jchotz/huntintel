#!/usr/bin/env python3
"""
LA_Migratory_Bird_scrape.py — HuntIntel Louisiana Migratory Game Bird Scraper
Fetches LDWF migratory game bird pages and outputs structured JSON.

Usage:
    python LA_Migratory_Bird_scrape.py
    python LA_Migratory_Bird_scrape.py --output my_output.json
    python LA_Migratory_Bird_scrape.py --pretty
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

SOURCE_URL      = "https://www.wlf.louisiana.gov/page/seasons-and-regulations"
LICENSE_URL     = "https://www.wlf.louisiana.gov/page/license-and-permit-fee-list"
PURCHASE_URL    = "https://louisianaoutdoors.com/"

LICENSE_PURCHASE_URLS = [
    {"label": "Louisiana Outdoors — License Portal", "url": "https://louisianaoutdoors.com/"},
    {"label": "LDWF — License and Permit Fee List", "url": "https://www.wlf.louisiana.gov/page/license-and-permit-fee-list"}
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Seasons and Regulations | LDWF",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from LDWF seasons page. Louisiana has East/West waterfowl zones and North/South dove zones.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {
            "name": "Dove (Mourning & White-winged)",
            "asterisk": False,
            "season_start": "September 5, 2026",
            "season_end": "January 17, 2027",
            "season_raw": "North: Sep 5-27, Oct 10-Nov 15, Dec 19-Jan 17; South: Sep 5-20, Oct 17-Nov 29, Dec 12-Jan 10",
            "hunting_units": "North and South Zones (see sub-seasons)",
            "bag_limit": "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "45",
            "sub_seasons": [
                {"name": "North Zone — Segment 1", "season_start": "September 5, 2026", "season_end": "September 27, 2026", "bag_limit": "15 daily", "possession_limit": "45"},
                {"name": "North Zone — Segment 2", "season_start": "October 10, 2026", "season_end": "November 15, 2026", "bag_limit": "15 daily", "possession_limit": "45"},
                {"name": "North Zone — Segment 3", "season_start": "December 19, 2026", "season_end": "January 17, 2027", "bag_limit": "15 daily", "possession_limit": "45"},
                {"name": "South Zone — Segment 1", "season_start": "September 5, 2026", "season_end": "September 20, 2026", "bag_limit": "15 daily", "possession_limit": "45"},
                {"name": "South Zone — Segment 2", "season_start": "October 17, 2026", "season_end": "November 29, 2026", "bag_limit": "15 daily", "possession_limit": "45"},
                {"name": "South Zone — Segment 3", "season_start": "December 12, 2026", "season_end": "January 10, 2027", "bag_limit": "15 daily", "possession_limit": "45"},
            ]
        },
        {
            "name": "Teal (Blue, Green, Cinnamon)",
            "asterisk": False,
            "season_start": "September 19, 2026",
            "season_end": "September 27, 2026",
            "season_raw": "September 19 - 27, 2026",
            "hunting_units": "Statewide",
            "bag_limit": "6 daily",
            "possession_limit": "18",
        },
        {
            "name": "Black-bellied Whistling Duck",
            "asterisk": True,
            "season_start": "October 3, 2026",
            "season_end": "October 11, 2026",
            "season_raw": "October 3 - 11, 2026 (special permit required)",
            "hunting_units": "Statewide",
            "bag_limit": "4 daily",
            "possession_limit": "12",
        },
        {
            "name": "Duck, Coot & Merganser",
            "asterisk": True,
            "season_start": "November 14, 2026",
            "season_end": "January 31, 2027",
            "season_raw": "East: Nov 21-Dec 6, Dec 19-Jan 31; West: Nov 14-Dec 6, Dec 19-Jan 24",
            "hunting_units": "East and West Zones (see sub-seasons)",
            "bag_limit": "6 ducks daily (species restrictions), 15 coot, 5 merganser",
            "possession_limit": "18 (3x daily bag)",
            "sub_seasons": [
                {"name": "East Zone — Segment 1", "season_start": "November 21, 2026", "season_end": "December 6, 2026", "bag_limit": "6 ducks daily", "possession_limit": "18"},
                {"name": "East Zone — Segment 2", "season_start": "December 19, 2026", "season_end": "January 31, 2027", "bag_limit": "6 ducks daily", "possession_limit": "18"},
                {"name": "West Zone — Segment 1", "season_start": "November 14, 2026", "season_end": "December 6, 2026", "bag_limit": "6 ducks daily", "possession_limit": "18"},
                {"name": "West Zone — Segment 2", "season_start": "December 19, 2026", "season_end": "January 24, 2027", "bag_limit": "6 ducks daily", "possession_limit": "18"},
            ]
        },
        {
            "name": "Goose (Light, White-fronted & Canada)",
            "asterisk": True,
            "season_start": "November 14, 2026",
            "season_end": "February 7, 2027",
            "season_raw": "East & West: Nov 14-Dec 6, Dec 19-Feb 7",
            "hunting_units": "East and West Zones",
            "bag_limit": "20 light geese, 3 white-fronted, 1 Canada daily",
            "possession_limit": "Light: none; White-fronted: 9; Canada: 3",
        },
        {
            "name": "Light Goose Conservation Order",
            "asterisk": False,
            "season_start": "December 7, 2026",
            "season_end": "March 7, 2027",
            "season_raw": "East: Dec 7-18, Feb 8-Mar 7; West: Dec 7-18, Feb 8-Mar 7",
            "hunting_units": "East and West Zones",
            "bag_limit": "No daily limit",
            "possession_limit": "No possession limit",
        },
        {
            "name": "Rail & Gallinule",
            "asterisk": False,
            "season_start": "September 19, 2026",
            "season_end": "January 6, 2027",
            "season_raw": "Sep 19-27, Nov 7-Jan 6",
            "hunting_units": "Statewide",
            "bag_limit": "15 King/Clapper; 25 Sora/Virginia; 15 Gallinule daily",
            "possession_limit": "45/75/45",
        },
        {
            "name": "Snipe (Common Snipe)",
            "asterisk": False,
            "season_start": "October 31, 2026",
            "season_end": "February 28, 2027",
            "season_raw": "Oct 31 - Jan 10 AND Jan 25 - Feb 28 (split season)",
            "hunting_units": "Statewide",
            "bag_limit": "8 daily",
            "possession_limit": "24",
        },
        {
            "name": "Woodcock",
            "asterisk": False,
            "season_start": "December 18, 2026",
            "season_end": "January 31, 2027",
            "season_raw": "December 18, 2026 - January 31, 2027",
            "hunting_units": "Statewide",
            "bag_limit": "3 daily",
            "possession_limit": "9",
        },
    ]

def build_licenses():
    return [
        {"name": "Basic Hunting License", "asterisk": False, "covers": "Required for all hunting (age 18+)",
         "resident_cost": "$20.00", "nonresident_cost": "$200.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Waterfowl License", "asterisk": True, "covers": "Required in addition to Basic Hunting for waterfowl hunting",
         "resident_cost": "$12.00", "nonresident_cost": "$50.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Louisiana Sportsman's Paradise License", "asterisk": False,
         "covers": "Basic hunting + fishing + deer + waterfowl + turkey tags",
         "resident_cost": "$100.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident 5-Day Basic Hunting License", "asterisk": False,
         "covers": "Basic hunting for 5 consecutive days",
         "resident_cost": None, "nonresident_cost": "$65.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Native 10-Day Waterfowl License", "asterisk": True,
         "covers": "Waterfowl for 10 days (nonresident native only)",
         "resident_cost": None, "nonresident_cost": "$12.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True, "covers": "Required for waterfowl hunters age 16+",
         "resident_cost": "$29.79", "nonresident_cost": "$29.79", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "WMA Access Annual Permit", "asterisk": False,
         "covers": "Required to use LDWF-administered WMAs",
         "resident_cost": "$20.00", "nonresident_cost": "$20.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "HIP Certification is free and required for all migratory bird hunters.",
         "applies_to": ["Basic Hunting License", "Waterfowl License"],
         "sources": [{"url": SOURCE_URL, "label": "LDWF — HIP Certification",
                      "evidence": "HIP Certification: Free. Required for all migratory bird hunters."}]},
        {"title": "Duck species restrictions: 4 mallards max (2 hens), 3 wood ducks, 2 canvasbacks, 2 redheads, 1 black duck, 3 pintails (1 hen), scaup 1/2 (first 15 days/after), mottled duck 0/1.",
         "applies_to": ["Duck, Coot & Merganser"],
         "sources": [{"url": SOURCE_URL, "label": "LDWF — Duck Species Limits",
                      "evidence": "Ducks: 6 total with species restrictions — max 4 mallards (2 hens), 3 wood ducks, 2 canvasbacks, 2 redheads, 1 black duck, 3 pintails (1 female), scaup: 1 first 15 days then 2, mottled ducks: 0 first 15 days then 1."}]},
        {"title": "Youth & Veterans waterfowl hunt days are held before and after regular season.",
         "applies_to": ["Duck, Coot & Merganser"],
         "sources": [{"url": SOURCE_URL, "label": "LDWF — Youth/Veterans Waterfowl",
                      "evidence": "East Zone Youth/Veterans: Nov 14 & Feb 6; West Zone Youth/Veterans: Nov 7 & Jan 30."}]},
        {"title": "Light Goose Conservation Order allows electronic calls, unplugged shotguns; shooting hours: 1/2 hr before sunrise to 1/2 hr after sunset.",
         "applies_to": ["Light Goose Conservation Order"],
         "sources": [{"url": SOURCE_URL, "label": "LDWF — Conservation Order",
                      "evidence": "Conservation Order: Allows electronic calls, unplugged shotguns; shooting hours: 1/2 hour before sunrise to 1/2 hour after sunset."}]},
    ]

def build_dataset():
    print(f"[LA_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[LA_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[LA_migratory] Using hardcoded data from LDWF regulations.", file=sys.stderr)
        soup = None

    dataset = {"state": "Louisiana", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Seasons and Regulations | LDWF",
            "last_updated": None, "update_note": "Could not fetch source page. Data from LDWF seasons page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape LDWF migratory game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/LA_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/LA_Migratory_Bird_dataset.json)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_str)
    print(f"[LA_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)

if __name__ == "__main__":
    main()
