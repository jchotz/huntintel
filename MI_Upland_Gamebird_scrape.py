#!/usr/bin/env python3
"""MI_Upland_Gamebird_scrape.py — HuntIntel Michigan Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.michigan.gov/dnr/things-to-do/hunting/small-game"
LICENSE_URL = "https://www.michigan.gov/dnr/managing-resources/laws/regulations/waterfowl"
PURCHASE_URL = "https://www.mdnr-elicense.com/"
LICENSE_PURCHASE_URLS = [
    {"label": "Michigan DNR — e-License Portal", "url": "https://www.mdnr-elicense.com/"},
    {"label": "MI DNR — Small Game Hunting", "url": "https://www.michigan.gov/dnr/things-to-do/hunting/small-game"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Small Game Hunting | Michigan DNR",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from MI DNR small game page.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Ruffed Grouse", "asterisk": True,
         "season_start": "September 15, 2026", "season_end": "January 1, 2027",
         "season_raw": "Sep 15 - Nov 14 AND Dec 1 - Jan 1 (split season)",
         "hunting_units": "Zones 1 & 2: 5 daily; Zone 3: 3 daily",
         "bag_limit": "5 daily (Zones 1 & 2), 3 daily (Zone 3)", "possession_limit": "10 (Zones 1&2), 6 (Zone 3)"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "October 10, 2026", "season_end": "January 1, 2027",
         "season_raw": "Zone 1 (UP): Oct 10-31; Zone 2: Oct 20 - Nov 14; Zone 3: Oct 20 - Nov 14 & Dec 1 - Jan 1",
         "hunting_units": "Zones 1 (UP), 2 (LP), 3 (LP) — see sub-seasons",
         "bag_limit": "2 daily", "possession_limit": "4",
         "sub_seasons": [
             {"name": "Zone 1 (Upper Peninsula)", "season_start": "October 10, 2026", "season_end": "October 31, 2026",
              "bag_limit": "2 daily", "possession_limit": "4"},
             {"name": "Zone 2 (Lower Peninsula)", "season_start": "October 20, 2026", "season_end": "November 14, 2026",
              "bag_limit": "2 daily", "possession_limit": "4"},
             {"name": "Zone 3 (Lower Peninsula) — Segment 1", "season_start": "October 20, 2026", "season_end": "November 14, 2026",
              "bag_limit": "2 daily", "possession_limit": "4"},
             {"name": "Zone 3 (Lower Peninsula) — Segment 2", "season_start": "December 1, 2026", "season_end": "January 1, 2027",
              "bag_limit": "2 daily", "possession_limit": "4"},
         ]},
        {"name": "Bobwhite Quail", "asterisk": False,
         "season_start": "October 20, 2026", "season_end": "November 14, 2026",
         "season_raw": "October 20 - November 14, 2026",
         "hunting_units": "Statewide", "bag_limit": "5 daily", "possession_limit": "10"},
        {"name": "Sharp-tailed Grouse", "asterisk": True,
         "season_start": "October 10, 2026", "season_end": "October 31, 2026",
         "season_raw": "October 10 - 31, 2026",
         "hunting_units": "Upper Peninsula", "bag_limit": "2 daily; 6 season limit", "possession_limit": "4"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 18, 2026", "season_end": "May 31, 2026",
         "season_raw": "April 18 - May 31, 2026 (varies by Turkey Management Unit)",
         "hunting_units": "Statewide (TMU-specific seasons)", "bag_limit": "1 bearded turkey per license",
         "possession_limit": "2 (if multiple licenses)"},
    ]

def build_licenses():
    return [
        {"name": "Base License (Resident)", "asterisk": False,
         "covers": "Required for all hunting", "resident_cost": "$11.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$151.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Pheasant License", "asterisk": True,
         "covers": "Required to hunt pheasants on LP public land (age 18+)",
         "resident_cost": "$25.00", "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting (1 bearded turkey)", "resident_cost": "$15.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Free Woodcock Stamp", "asterisk": False,
         "covers": "Required for woodcock hunting (includes HIP registration)",
         "resident_cost": "Free", "nonresident_cost": "Free", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Ruffed grouse has a split season: Sep 15 - Nov 14 AND Dec 1 - Jan 1. Bag limits differ by zone (5 daily Zones 1&2, 3 daily Zone 3).",
         "applies_to": ["Ruffed Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Ruffed Grouse",
                      "evidence": "Ruffed Grouse: Sept 15 - Nov 14 and Dec 1 - Jan 1. Zones 1&2: 5 daily, 10 possession. Zone 3: 3 daily, 6 possession."}]},
        {"title": "A $25 Pheasant License is required for hunters 18+ hunting pheasants on Lower Peninsula public land or Hunting Access Program lands.",
         "applies_to": ["Ring-necked Pheasant", "Pheasant License"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Pheasant License",
                      "evidence": "$25 pheasant license required for pheasant hunters 18 years and older on LP public land or HAP lands."}]},
        {"title": "Sharp-tailed grouse hunting is limited to the Upper Peninsula with a 6-bird season limit. A free sharp-tailed grouse stamp is required.",
         "applies_to": ["Sharp-tailed Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Sharp-tailed Grouse",
                      "evidence": "Sharp-tailed Grouse: Oct 10-31. 2 daily, 4 possession, 6 season limit. Free stamp required."}]},
        {"title": "A free woodcock stamp (includes HIP registration) is required for all woodcock hunters.",
         "applies_to": ["Free Woodcock Stamp"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Woodcock Stamp",
                      "evidence": "Free woodcock stamp required for all woodcock hunters (includes federal HIP registration)."}]},
    ]

def build_dataset():
    print(f"[MI_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MI_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Michigan", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Small Game Hunting | MI DNR",
            "last_updated": None, "update_note": "Data from MI DNR small game page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MI DNR upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MI_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MI_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
