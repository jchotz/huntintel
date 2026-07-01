#!/usr/bin/env python3
"""WI_Upland_Gamebird_scrape.py — HuntIntel Wisconsin Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://dnr.wisconsin.gov/topic/hunt/smgame"
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
    return {"page_url": SOURCE_URL, "page_label": "Small Game Hunting | Wisconsin DNR",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from WI DNR small game page. Wisconsin has ruffed grouse (2 zones), pheasant, quail, partridge, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Ruffed Grouse", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "January 3, 2027",
         "season_raw": "Zone A: Sep 12 - Jan 3; Zone B: Oct 17 - Dec 7",
         "hunting_units": "Zone A (northern) and Zone B (southern)",
         "bag_limit": "5 daily (Zone A), 3 daily (Zone B)", "possession_limit": "10",
         "sub_seasons": [
             {"name": "Zone A", "season_start": "September 12, 2026", "season_end": "January 3, 2027",
              "bag_limit": "5 daily", "possession_limit": "10"},
             {"name": "Zone B", "season_start": "October 17, 2026", "season_end": "December 7, 2026",
              "bag_limit": "3 daily", "possession_limit": "10"},
         ]},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "January 3, 2027",
         "season_raw": "October 17, 2026 - January 3, 2027 (9 a.m. start)",
         "hunting_units": "Statewide", "bag_limit": "2 cocks daily", "possession_limit": "6"},
        {"name": "Bobwhite Quail", "asterisk": False,
         "season_start": "October 17, 2026", "season_end": "December 9, 2026",
         "season_raw": "October 17, 2026 - December 9, 2026 (9 a.m. start)",
         "hunting_units": "Statewide", "bag_limit": "Limited", "possession_limit": "Limited"},
        {"name": "Hungarian Partridge", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "January 3, 2027",
         "season_raw": "October 17, 2026 - January 3, 2027 (9 a.m. start)",
         "hunting_units": "Statewide (closed in Clark, Marathon, Taylor counties)",
         "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 15, 2026", "season_end": "May 26, 2026",
         "season_raw": "Youth: Apr 11-12; Periods A-F: Apr 15 - May 26",
         "hunting_units": "Statewide (6 draw periods A-F)",
         "bag_limit": "1 bearded turkey per permit", "possession_limit": "2",
         "sub_seasons": [
             {"name": "Youth Hunt", "season_start": "April 11, 2026", "season_end": "April 12, 2026",
              "bag_limit": "1 bearded turkey", "possession_limit": "1"},
             {"name": "Period A", "season_start": "April 15, 2026", "season_end": "April 21, 2026",
              "bag_limit": "1 bearded turkey", "possession_limit": "1"},
             {"name": "Period B", "season_start": "April 22, 2026", "season_end": "April 28, 2026",
              "bag_limit": "1 bearded turkey", "possession_limit": "1"},
         ]},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "January 3, 2027",
         "season_raw": "September 12, 2026 - January 3, 2027",
         "hunting_units": "Statewide", "bag_limit": "2 either-sex", "possession_limit": "2"},
    ]

def build_licenses():
    return [
        {"name": "Resident Small Game License", "asterisk": False,
         "covers": "Small game including grouse, pheasant, quail, partridge, rabbit, squirrel",
         "resident_cost": "$25.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Pheasant Stamp", "asterisk": True,
         "covers": "Required in addition to Small Game license to hunt pheasants",
         "resident_cost": "$10.00", "nonresident_cost": "$10.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting (draw period system)", "resident_cost": "$15.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey License", "asterisk": True,
         "covers": "Fall turkey hunting", "resident_cost": "$15.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Ruffed grouse has two zones: Zone A (northern) runs Sep 12 - Jan 3 with 5 daily bag; Zone B (southern) runs Oct 17 - Dec 7 with 3 daily bag.",
         "applies_to": ["Ruffed Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "WI DNR — Ruffed Grouse Seasons",
                      "evidence": "Ruffed grouse Zone A: Sept. 12 - Jan. 3, 2027. Zone B: Oct. 17 - Dec. 7."}]},
        {"title": "A Pheasant Stamp ($10) is required in addition to a Small Game license to hunt pheasants in Wisconsin.",
         "applies_to": ["Ring-necked Pheasant", "Pheasant Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "WI DNR — License Fees",
                      "evidence": "Pheasant Stamp: $10. Required to hunt pheasants."}]},
        {"title": "Hungarian partridge is closed in Clark, Marathon, and Taylor counties.",
         "applies_to": ["Hungarian Partridge"],
         "sources": [{"url": SOURCE_URL, "label": "WI DNR — Partridge Season",
                      "evidence": "Hungarian partridge: Statewide (closed in Clark, Marathon, Taylor)."}]},
        {"title": "Spring turkey has 6 draw periods (A-F) running April 15 - May 26. Youth hunt is April 11-12.",
         "applies_to": ["Wild Turkey (Spring)"],
         "sources": [{"url": "https://dnr.wisconsin.gov/topic/hunt/dates", "label": "WI DNR — Turkey Dates",
                      "evidence": "Spring turkeys: Youth April 11-12. Periods A-F: April 15 - May 26."}]},
    ]

def build_dataset():
    print(f"[WI_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WI_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Wisconsin", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Small Game Hunting | WI DNR",
            "last_updated": None, "update_note": "Data from WI DNR small game page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape WI DNR upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/WI_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[WI_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
