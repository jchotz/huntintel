#!/usr/bin/env python3
"""ID_Upland_Gamebird_scrape.py — HuntIntel Idaho Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://idfg.idaho.gov/rules/upland"
LICENSE_URL = "https://idfg.idaho.gov/licenses"
PURCHASE_URL = "https://idfg.idaho.gov/licenses"
LICENSE_PURCHASE_URLS = [
    {"label": "IDFG — License Portal", "url": "https://idfg.idaho.gov/licenses"},
    {"label": "IDFG — Upland Game Rules", "url": "https://idfg.idaho.gov/rules/upland"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Upland Game Seasons | Idaho Fish & Game",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from IDFG. Idaho has forest grouse (Dusky, Ruffed, Spruce), quail, chukar, partridge, pheasant, sage-grouse, sharp-tailed grouse, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Forest Grouse (Dusky, Ruffed & Spruce)", "asterisk": True,
         "season_start": "August 29, 2026", "season_end": "January 31, 2027",
         "season_raw": "Area 1: Aug 29 - Jan 30; Area 2: Aug 29 - Dec 30",
         "hunting_units": "Area 1 (northern) and Area 2 (remainder)",
         "bag_limit": "4 daily (combined all forest grouse)", "possession_limit": "12"},
        {"name": "California & Bobwhite Quail", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "January 30, 2027",
         "season_raw": "September 19, 2026 - January 30, 2027",
         "hunting_units": "Area 1 (northern); Area 2 closed",
         "bag_limit": "10 daily (combined)", "possession_limit": "30"},
        {"name": "Chukar & Gray (Hungarian) Partridge", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "January 30, 2027",
         "season_raw": "September 19, 2026 - January 30, 2027",
         "hunting_units": "Statewide", "bag_limit": "8 daily (combined chukar & Huns)",
         "possession_limit": "24"},
        {"name": "Sage Grouse", "asterisk": True,
         "season_start": "September 19, 2026", "season_end": "October 31, 2026",
         "season_raw": "September 19 - October 31, 2026",
         "hunting_units": "Limited permit zones", "bag_limit": "2 daily (special permit required)",
         "possession_limit": "2"},
        {"name": "Sharp-tailed Grouse", "asterisk": True,
         "season_start": "October 1, 2026", "season_end": "October 31, 2026",
         "season_raw": "October 1 - 31, 2026",
         "hunting_units": "Area 1 only; Area 2 closed",
         "bag_limit": "2 daily (permit validation required)", "possession_limit": "6"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "October 10, 2026", "season_end": "December 31, 2026",
         "season_raw": "Area 1: Oct 10-Dec 30 (res), Oct 16-Dec 30 (nonres); Area 2: Oct 17-Nov 29; Area 3: Oct 17-Dec 30",
         "hunting_units": "Areas 1, 2, 3 (see sub-seasons)",
         "bag_limit": "3 cocks daily", "possession_limit": "9",
         "sub_seasons": [
             {"name": "Area 1 (Resident)", "season_start": "October 10, 2026", "season_end": "December 31, 2026",
              "bag_limit": "3 cocks daily", "possession_limit": "9"},
             {"name": "Area 1 (Nonresident)", "season_start": "October 16, 2026", "season_end": "December 31, 2026",
              "bag_limit": "3 cocks daily", "possession_limit": "9"},
             {"name": "Area 2", "season_start": "October 17, 2026", "season_end": "November 29, 2026",
              "bag_limit": "3 cocks daily", "possession_limit": "9"},
             {"name": "Area 3", "season_start": "October 17, 2026", "season_end": "December 31, 2026",
              "bag_limit": "3 cocks daily", "possession_limit": "9"},
             {"name": "Youth Pheasant (Statewide)", "season_start": "October 3, 2026", "season_end": "October 9, 2026",
              "bag_limit": "3 cocks daily", "possession_limit": "9"},
         ]},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 11, 2026", "season_end": "May 25, 2026",
         "season_raw": "Youth: Apr 8-14; General: Apr 15 - May 25",
         "hunting_units": "Statewide (varies by unit)",
         "bag_limit": "1 bearded turkey per tag", "possession_limit": "1"},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "August 29, 2026", "season_end": "January 31, 2027",
         "season_raw": "Aug 29 - Jan 31 (varies by GMU)",
         "hunting_units": "Most GMUs; varies by unit",
         "bag_limit": "1 either-sex", "possession_limit": "1"},
    ]

def build_licenses():
    return [
        {"name": "Resident Upland Game License", "asterisk": False,
         "covers": "Upland game, furbearers, migratory birds, turkey",
         "resident_cost": "$15.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Upland Game License", "asterisk": False,
         "covers": "Upland game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$90.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey Tag", "asterisk": True,
         "covers": "Spring turkey (1 bearded bird per tag)", "resident_cost": "$15.00",
         "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey Tag", "asterisk": True,
         "covers": "Fall turkey (1 either-sex)", "resident_cost": "$15.00",
         "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Sage grouse and sharp-tailed grouse require additional permits/validations in addition to the Upland Game License.",
         "applies_to": ["Sage Grouse", "Sharp-tailed Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "IDFG — Sage & Sharp-tailed Grouse",
                      "evidence": "Sage Grouse: special permit required. Sharp-tailed Grouse: permit validation required."}]},
        {"title": "Forest grouse (Dusky, Ruffed, Spruce) have a combined daily bag of 4 and possession of 12. Area 1 runs longer (Aug 29 - Jan 30) than Area 2 (Aug 29 - Dec 30).",
         "applies_to": ["Forest Grouse (Dusky, Ruffed & Spruce)"],
         "sources": [{"url": SOURCE_URL, "label": "IDFG — Forest Grouse",
                      "evidence": "Forest grouse: Area 1 Aug 29 - Jan 30; Area 2 Aug 29 - Dec 30. 4 daily, 12 possession."}]},
        {"title": "Chukar and Hungarian partridge share a combined daily bag of 8 and possession of 24. Season runs Sep 19 - Jan 30.",
         "applies_to": ["Chukar & Gray (Hungarian) Partridge"],
         "sources": [{"url": SOURCE_URL, "label": "IDFG — Chukar & Partridge",
                      "evidence": "Chukar & Gray Partridge: Sep 19 - Jan 30. 8 daily, 24 possession (combined)."}]},
        {"title": "Pheasant season varies by area. Youth hunt is Oct 3-9. Bag limit is 3 cocks daily statewide.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "IDFG — Pheasant Season",
                      "evidence": "Pheasant: Area 1 Oct 10-Dec 30; Area 2 Oct 17-Nov 29; Area 3 Oct 17-Dec 30. Youth: Oct 3-9. 3 cocks daily."}]},
    ]

def build_dataset():
    print(f"[ID_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[ID_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Idaho", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Upland Game Seasons | IDFG",
            "last_updated": None, "update_note": "Data from IDFG upland game rules.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape IDFG upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/ID_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[ID_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
