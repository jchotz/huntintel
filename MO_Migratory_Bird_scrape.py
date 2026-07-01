#!/usr/bin/env python3
"""MO_Migratory_Bird_scrape.py — HuntIntel Missouri Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://mdc.mo.gov/hunting-trapping/species/waterfowl"
SEASONS_URL = "https://mdc.mo.gov/hunting-trapping/seasons"
LICENSE_URL = "https://mdc.mo.gov/permits/hunting-permits"
PURCHASE_URL = "https://mdc.mo.gov/epermits"
LICENSE_PURCHASE_URLS = [
    {"label": "MDC e-Permits System", "url": "https://mdc.mo.gov/epermits"},
    {"label": "MDC — Hunting Permits", "url": "https://mdc.mo.gov/permits/hunting-permits"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Waterfowl | Missouri Department of Conservation",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from MDC waterfowl and seasons pages. Missouri has 3 duck zones: North, Middle, South.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 1 - November 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily (all dove species combined)", "possession_limit": "45"},
        {"name": "Teal (Blue, Green, Cinnamon)", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "September 20, 2026",
         "season_raw": "September 12 - 20, 2026 (sunrise to sunset)",
         "hunting_units": "Statewide", "bag_limit": "6 daily (combined)", "possession_limit": "18"},
        {"name": "Early Canada Goose & Brant", "asterisk": False,
         "season_start": "October 3, 2026", "season_end": "October 10, 2026",
         "season_raw": "October 3 - 10, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily (Canada and brant combined)", "possession_limit": "9"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "October 24, 2026", "season_end": "January 31, 2027",
         "season_raw": "North: Oct 31-Dec 29; Middle: Nov 7-Dec 13 & Dec 19-Jan 10; South: Nov 26-29 & Dec 7-Jan 31",
         "hunting_units": "North, Middle, and South Zones (see sub-seasons)",
         "bag_limit": "6 ducks daily (species restrictions), 15 coot daily",
         "possession_limit": "18 duck, 45 coot",
         "sub_seasons": [
             {"name": "North Zone", "season_start": "October 31, 2026", "season_end": "December 29, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Middle Zone — Segment 1", "season_start": "November 7, 2026", "season_end": "December 13, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Middle Zone — Segment 2", "season_start": "December 19, 2026", "season_end": "January 10, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 1", "season_start": "November 26, 2026", "season_end": "November 29, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 2", "season_start": "December 7, 2026", "season_end": "January 31, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Goose (Regular Season)", "asterisk": True,
         "season_start": "November 11, 2026", "season_end": "February 6, 2027",
         "season_raw": "November 11, 2026 - February 6, 2027",
         "hunting_units": "Statewide",
         "bag_limit": "3 Canada/brant, 2 white-fronted, 20 light geese daily",
         "possession_limit": "9 Canada, 6 white-fronted, none light geese"},
        {"name": "Light Goose Conservation Order", "asterisk": False,
         "season_start": "February 7, 2027", "season_end": "April 30, 2027",
         "season_raw": "February 7 - April 30, 2027",
         "hunting_units": "Statewide",
         "bag_limit": "No daily limit", "possession_limit": "No possession limit"},
        {"name": "Common Snipe", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "December 16, 2026",
         "season_raw": "September 1 - December 16, 2026",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Woodcock", "asterisk": False,
         "season_start": "October 15, 2026", "season_end": "November 28, 2026",
         "season_raw": "October 15 - November 28, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Sora & Virginia Rail", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 daily (combined)", "possession_limit": "75"},
    ]

def build_licenses():
    return [
        {"name": "Small Game Hunting Permit", "asterisk": False,
         "covers": "Small game including dove, quail, pheasant, rabbit, squirrel",
         "resident_cost": "$12.50", "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Resident Migratory Bird Hunting Permit", "asterisk": True,
         "covers": "Required in addition to Small Game permit for waterfowl and migratory birds",
         "resident_cost": "$7.50", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Migratory Bird Hunting Permit", "asterisk": True,
         "covers": "Required in addition to Nonresident Small Game permit for waterfowl and migratory birds",
         "resident_cost": None, "nonresident_cost": "$60.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Archer's Hunting Permit", "asterisk": False,
         "covers": "Deer archery + small game + furbearers",
         "resident_cost": "$22.00", "nonresident_cost": "$360.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+",
         "resident_cost": "$25.00", "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "The Missouri Migratory Bird Hunting Permit ($7.50 resident / $60 nonresident) is required in addition to a Small Game permit to hunt waterfowl and migratory birds.",
         "applies_to": ["Small Game Hunting Permit", "Resident Migratory Bird Hunting Permit", "Nonresident Migratory Bird Hunting Permit"],
         "sources": [{"url": LICENSE_URL, "label": "MDC — Hunting Permits",
                      "evidence": "Resident Migratory Bird Hunting Permit: $7.50. Nonresident Migratory Bird Hunting Permit: $60.00."}]},
        {"title": "Duck species restrictions: 4 mallards max (2 hens), 3 wood ducks, 2 canvasbacks, 2 redheads, 2 black ducks, 3 pintails, 1 mottled duck. Scaup: 2 first 45 days, 1 last 15 days.",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "MDC — Waterfowl Season Limits",
                      "evidence": "Mallards: 4 (no more than 2 females). Scaup: 2 (first 45 days), 1 (last 15 days). Wood ducks: 3. Redheads: 2. Canvasback: 2. Black duck: 2. Mottled duck: 1. Pintails: 3."}]},
        {"title": "Missouri has 3 duck zones (North, Middle, South) with different season dates and youth waterfowl days.",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "MDC — Duck Zone Seasons",
                      "evidence": "North Zone: Oct 31-Dec 29. Middle Zone: Nov 7-Dec 13 AND Dec 19-Jan 10. South Zone: Nov 26-29 AND Dec 7-Jan 31."}]},
        {"title": "Teal season shooting hours are sunrise to sunset (no pre-sunrise shooting). Regular duck season: 1/2 hr before sunrise to sunset.",
         "applies_to": ["Teal (Blue, Green, Cinnamon)", "Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "MDC — Waterfowl Shooting Hours",
                      "evidence": "Teal: Sunrise to sunset. Regular duck season: One-half hour before sunrise to sunset."}]},
    ]

def build_dataset():
    print(f"[MO_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MO_migratory] WARNING: Could not fetch: {e}", file=sys.stderr)
        print("[MO_migratory] Using hardcoded data.", file=sys.stderr)
        soup = None
    dataset = {"state": "Missouri", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL,
            "page_label": "Waterfowl | MDC", "last_updated": None,
            "update_note": "Could not fetch source page. Data from MDC waterfowl and seasons pages.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MDC migratory game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MO_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/MO_Migratory_Bird_dataset.json)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MO_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
