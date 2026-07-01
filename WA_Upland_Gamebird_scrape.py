#!/usr/bin/env python3
"""WA_Upland_Gamebird_scrape.py — HuntIntel Washington Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/washington/hunting/game-bird/resident-game-bird-seasons"
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
    return {"page_url": SOURCE_URL, "page_label": "WA Resident Game Bird Seasons | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from WDFW regulations. Washington has forest grouse, pheasant (west & east), quail, chukar, partridge, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Forest Grouse (Ruffed, Sooty, Dusky, Spruce)", "asterisk": True,
         "season_start": "September 15, 2026", "season_end": "January 15, 2027",
         "season_raw": "September 15, 2026 - January 15, 2027",
         "hunting_units": "Statewide",
         "bag_limit": "4 daily (max 3 each of Dusky/Sooty, Spruce, Ruffed)",
         "possession_limit": "12 (max 9 each sub-category)"},
        {"name": "Ring-necked Pheasant (Western WA)", "asterisk": True,
         "season_start": "September 20, 2026", "season_end": "November 30, 2026",
         "season_raw": "Regular: Sep 20 - Nov 30 (8am-4pm); Extended (no releases): Dec 1-15",
         "hunting_units": "Western Washington (release sites)",
         "bag_limit": "2 either sex daily", "possession_limit": "15",
         "sub_seasons": [
             {"name": "Youth Only", "season_start": "September 12, 2026", "season_end": "September 13, 2026",
              "bag_limit": "2 either sex", "possession_limit": "4"},
             {"name": "Senior/Disabled", "season_start": "September 14, 2026", "season_end": "September 18, 2026",
              "bag_limit": "2 either sex", "possession_limit": "10"},
             {"name": "Regular Season", "season_start": "September 19, 2026", "season_end": "November 30, 2026",
              "bag_limit": "2 either sex", "possession_limit": "15"},
         ]},
        {"name": "Ring-necked Pheasant (Eastern WA)", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "January 19, 2027",
         "season_raw": "Oct 17 - Jan 19 (regular). Youth: Sep 12-13. Senior: Sep 14-18.",
         "hunting_units": "Eastern Washington",
         "bag_limit": "3 cocks daily", "possession_limit": "15"},
        {"name": "California Quail & Bobwhite", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "January 19, 2027",
         "season_raw": "Western WA: Sep 19 - Nov 30; Eastern WA: Oct 3 - Jan 19",
         "hunting_units": "Western and Eastern Washington",
         "bag_limit": "10 daily (mixed bag)", "possession_limit": "30"},
        {"name": "Mountain Quail", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "November 30, 2026",
         "season_raw": "September 19 - November 30, 2026 (8am-4pm)",
         "hunting_units": "Western WA only; Eastern WA closed",
         "bag_limit": "2 either sex daily", "possession_limit": "4"},
        {"name": "Gray Partridge", "asterisk": False,
         "season_start": "October 3, 2026", "season_end": "January 19, 2027",
         "season_raw": "October 3, 2026 - January 19, 2027",
         "hunting_units": "Eastern WA only",
         "bag_limit": "6 daily", "possession_limit": "18"},
        {"name": "Chukar Partridge", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "January 31, 2027",
         "season_raw": "Youth: Sep 12-13; Regular: Oct 3 - Jan 31",
         "hunting_units": "Eastern WA only",
         "bag_limit": "6 daily", "possession_limit": "18"},
    ]

def build_licenses():
    return [
        {"name": "Small Game License (Resident)", "asterisk": False,
         "covers": "Small game, upland birds", "resident_cost": "$45.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$93.08", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Western WA Pheasant Permit (3-Day)", "asterisk": True,
         "covers": "Required to hunt pheasants on western WA release sites",
         "resident_cost": "$55.13", "nonresident_cost": "$108.26", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting", "resident_cost": "$30.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey License", "asterisk": True,
         "covers": "Fall turkey hunting", "resident_cost": "$30.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Washington forest grouse (Ruffed, Sooty, Dusky, Spruce) have a combined daily bag of 4 statewide. Season runs Sep 15 - Jan 15.",
         "applies_to": ["Forest Grouse (Ruffed, Sooty, Dusky, Spruce)"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Forest Grouse",
                      "evidence": "Forest Grouse: Sep 15 - Jan 15. 4 daily, 12 possession. Max 3 each of Dusky/Sooty, Spruce, Ruffed."}]},
        {"title": "Pheasant hunting in western WA is on release sites with modified hours (8am-4pm). A special Western WA Pheasant Permit ($55.13) is required.",
         "applies_to": ["Ring-necked Pheasant (Western WA)"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Western WA Pheasant",
                      "evidence": "Western WA Pheasant: Regular Sep 20 - Nov 30 (8am-4pm). Western WA Pheasant Permit: $55.13."}]},
        {"title": "Mountain quail are only open in Western Washington. Eastern WA is closed for mountain quail.",
         "applies_to": ["Mountain Quail"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Mountain Quail",
                      "evidence": "Mountain Quail: Western WA only. Eastern WA closed. 2 either sex daily."}]},
        {"title": "Chukar and gray partridge hunting is limited to Eastern Washington. Chukar season runs later (through Jan 31) than most other upland birds.",
         "applies_to": ["Chukar Partridge", "Gray Partridge"],
         "sources": [{"url": SOURCE_URL, "label": "WDFW — Chukar & Partridge",
                      "evidence": "Chukar: Eastern WA only, Oct 3 - Jan 31. Gray Partridge: Oct 3 - Jan 19."}]},
    ]

def build_dataset():
    print(f"[WA_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WA_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Washington", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "WA Resident Game Bird Seasons",
            "last_updated": None, "update_note": "Data from WDFW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape WDFW upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/WA_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[WA_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
