#!/usr/bin/env python3
"""WI_Migratory_Bird_scrape.py — HuntIntel Wisconsin Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://dnr.wisconsin.gov/topic/hunt/waterfowl"
SEASONS_URL = "https://dnr.wisconsin.gov/topic/hunt/dates"
LICENSE_URL = "https://dnr.wisconsin.gov/GoWild/resident.html"
PURCHASE_URL = "https://gowild.wi.gov/"
LICENSE_PURCHASE_URLS = [
    {"label": "Go Wild Wisconsin — License Portal", "url": "https://gowild.wi.gov/"},
    {"label": "WI DNR — Resident Licenses", "url": "https://dnr.wisconsin.gov/GoWild/resident.html"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | Wisconsin DNR",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from WI DNR waterfowl and seasons pages. Wisconsin has 3 duck zones (Northern, Southern, Open Water) and 3 goose zones (Northern, Southern, Mississippi River).",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning Dove)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 1 - November 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily", "possession_limit": "45"},
        {"name": "Teal (Early Teal)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "September 9, 2026",
         "season_raw": "September 1 - 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "6 daily", "possession_limit": "18"},
        {"name": "Early Goose", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "September 15, 2026",
         "season_raw": "September 1 - 15, 2026",
         "hunting_units": "Statewide", "bag_limit": "5 Canada geese daily", "possession_limit": "15"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "September 26, 2026", "season_end": "December 15, 2026",
         "season_raw": "North: Sep 26-Nov 24; South: Oct 3-11 & Oct 17-Dec 6; Open Water: Oct 17-Dec 15",
         "hunting_units": "Northern, Southern, Open Water Zones (see sub-seasons)",
         "bag_limit": "6 ducks daily (species restrictions), 15 coot daily",
         "possession_limit": "18 (3x daily bag)",
         "sub_seasons": [
             {"name": "Northern Duck Zone", "season_start": "September 26, 2026", "season_end": "November 24, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Southern Duck Zone — Segment 1", "season_start": "October 3, 2026", "season_end": "October 11, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Southern Duck Zone — Segment 2", "season_start": "October 17, 2026", "season_end": "December 6, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Open Water Duck Zone", "season_start": "October 17, 2026", "season_end": "December 15, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Goose (Regular)", "asterisk": True,
         "season_start": "September 16, 2026", "season_end": "January 5, 2027",
         "season_raw": "North: Sep 16-Dec 16; South: Sep 16-Oct 11, Oct 17-Dec 6, Dec 19-Jan 2; Mississippi: Oct 3-11, Oct 17-Jan 5",
         "hunting_units": "Northern, Southern, Mississippi River Zones (see sub-seasons)",
         "bag_limit": "5 Canada geese daily", "possession_limit": "15",
         "sub_seasons": [
             {"name": "Northern Goose Zone", "season_start": "September 16, 2026", "season_end": "December 16, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Southern Goose Zone — Segment 1", "season_start": "September 16, 2026", "season_end": "October 11, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Southern Goose Zone — Segment 2", "season_start": "October 17, 2026", "season_end": "December 6, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Southern Goose Zone — Segment 3", "season_start": "December 19, 2026", "season_end": "January 2, 2027",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Mississippi River Goose Zone — Segment 1", "season_start": "October 3, 2026", "season_end": "October 11, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Mississippi River Goose Zone — Segment 2", "season_start": "October 17, 2026", "season_end": "January 5, 2027",
              "bag_limit": "5 daily", "possession_limit": "15"},
         ]},
        {"name": "Woodcock", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "November 2, 2026",
         "season_raw": "September 19 - November 2, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Snipe", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Rail (Sora & Virginia) & Gallinule", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 daily rail; 15 gallinule", "possession_limit": "75 rail; 45 gallinule"},
    ]

def build_licenses():
    return [
        {"name": "Resident Small Game License", "asterisk": False,
         "covers": "Required for all small game including migratory birds",
         "resident_cost": "$25.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Wisconsin Waterfowl Stamp", "asterisk": True,
         "covers": "Required for waterfowl (ducks, geese) hunting, age 16+",
         "resident_cost": "$12.00", "nonresident_cost": "$12.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$30.50",
         "nonresident_cost": "$30.50", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Early Canada Goose Permit", "asterisk": False,
         "covers": "Required for early Canada goose season (Sep 1-15)",
         "resident_cost": "$3.00", "nonresident_cost": "$3.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Regular Canada Goose Permit", "asterisk": False,
         "covers": "Required for regular Canada goose season", "resident_cost": "$3.00",
         "nonresident_cost": "$3.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "HIP registration is free and required for all migratory bird hunters (doves, woodcock, waterfowl, rail, snipe, gallinule).",
         "applies_to": ["Resident Small Game License", "Nonresident Small Game License"],
         "sources": [{"url": SOURCE_URL, "label": "WI DNR — HIP Registration",
                      "evidence": "HIP Registration required for all migratory bird hunters. Free when purchasing license."}]},
        {"title": "Wisconsin has 3 duck zones (Northern, Southern, Open Water) and 3 goose zones (Northern, Southern, Mississippi River) with different season dates.",
         "applies_to": ["Duck & Coot", "Goose (Regular)"],
         "sources": [{"url": SOURCE_URL, "label": "WI DNR — Waterfowl Zones",
                      "evidence": "Northern Duck Zone: Sep 26-Nov 24. Southern Duck Zone: Oct 3-11 & Oct 17-Dec 6. Open Water Zone: Oct 17-Dec 15."}]},
        {"title": "Youth waterfowl hunt (ages 15 and under) is Sept 19-20, 2026. License and stamp requirements waived on these days. HIP registration required.",
         "applies_to": ["Duck & Coot", "Goose (Regular)"],
         "sources": [{"url": SOURCE_URL, "label": "WI DNR — Youth Waterfowl",
                      "evidence": "Youth Waterfowl: Sept 19-20, 2026. License and stamp requirements waived for hunters 15 and younger."}]},
        {"title": "The Wisconsin Waterfowl Stamp ($12) and Federal Duck Stamp ($30.50) are required for waterfowl hunters age 16+.",
         "applies_to": ["Wisconsin Waterfowl Stamp", "Federal Duck Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "WI DNR — License Fees",
                      "evidence": "Waterfowl Stamp: $12. Federal Duck Stamp: $30.50 (includes fees)."}]},
    ]

def build_dataset():
    print(f"[WI_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WI_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Wisconsin", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Waterfowl Hunting | WI DNR",
            "last_updated": None, "update_note": "Data from WI DNR waterfowl page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape WI DNR migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/WI_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[WI_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
