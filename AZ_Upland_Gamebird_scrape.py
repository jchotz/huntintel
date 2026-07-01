#!/usr/bin/env python3
"""AZ_Upland_Gamebird_scrape.py — HuntIntel Arizona Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/arizona/hunting/hunting-seasons-and-dates"
LICENSE_URL = "https://www.azgfd.com/hunting/regulations/"
PURCHASE_URL = "https://www.azgfd.com/license/"
LICENSE_PURCHASE_URLS = [
    {"label": "AZGFD — License Portal", "url": "https://www.azgfd.com/license/"},
    {"label": "AZGFD — Hunting Regulations", "url": "https://www.azgfd.com/hunting/regulations/"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | Arizona | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from AZGFD. Arizona has quail (3 species), chukar, grouse, pheasant, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Quail (Gambel's, Scaled & Mearns')", "asterisk": True,
         "season_start": "October 17, 2026", "season_end": "February 8, 2027",
         "season_raw": "Gambel's & Scaled: Oct 17 - Feb 8; Mearns': Dec 5 - Feb 8",
         "hunting_units": "Statewide (Mearns' has later start)",
         "bag_limit": "15 daily (combined all quail species)", "possession_limit": "45"},
        {"name": "Chukar Partridge", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "February 8, 2027",
         "season_raw": "September 1, 2026 - February 8, 2027",
         "hunting_units": "Statewide", "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Grouse (Blue/Sooty & Ruffed)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "February 8, 2027",
         "season_raw": "Limited Weapon: Sep 1-15; Archery: Oct 17 - Feb 8",
         "hunting_units": "Statewide", "bag_limit": "2 cocks daily (limited weapon); 2 either sex (archery)",
         "possession_limit": "6"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 25, 2026", "season_end": "May 22, 2026",
         "season_raw": "Merriam's: Apr 25 - May 22 (varies by hunt); Gould's: May 9-22",
         "hunting_units": "Statewide (permit/draw zones)",
         "bag_limit": "1 bearded turkey per tag", "possession_limit": "1"},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "August 22, 2026", "season_end": "October 9, 2026",
         "season_raw": "Archery: Aug 22 - Sep 11; Shotgun: Oct 3-9; Youth: Oct 3-13",
         "hunting_units": "Statewide (permit/draw zones)",
         "bag_limit": "1 either sex", "possession_limit": "1"},
    ]

def build_licenses():
    return [
        {"name": "General Hunting License", "asterisk": False,
         "covers": "Small game, upland birds, furbearers",
         "resident_cost": "$37.00", "nonresident_cost": "$160.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Combination Hunt & Fish License", "asterisk": False,
         "covers": "All hunting and fishing", "resident_cost": "$57.00",
         "nonresident_cost": "$160.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey Tag", "asterisk": True,
         "covers": "Spring turkey (draw permit)", "resident_cost": "$38.00",
         "nonresident_cost": "$105.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey Tag", "asterisk": True,
         "covers": "Fall turkey", "resident_cost": "$38.00",
         "nonresident_cost": "$105.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Arizona has 3 quail species: Gambel's, Scaled (blue), and Mearns' (Montezuma). Mearns' quail season starts later (Dec 5) than other quail (Oct 17). Combined bag is 15 daily.",
         "applies_to": ["Quail (Gambel's, Scaled & Mearns')"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Quail Seasons",
                      "evidence": "Gambel's & Scaled: Oct 17 - Feb 8. Mearns': Dec 5 - Feb 8. 15 daily combined."}]},
        {"title": "Pheasant has two seasons: Limited Weapon (shotgun) Sep 1-15 with 2 cocks daily, and Archery Oct 17 - Feb 8 with 2 either sex.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Pheasant Season",
                      "evidence": "Pheasant: Limited Weapon Sep 1-15. Archery Oct 17-Feb 8."}]},
        {"title": "Arizona has both Merriam's and Gould's wild turkey subspecies with different spring season dates. Spring turkey is by draw permit.",
         "applies_to": ["Wild Turkey (Spring)"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Turkey Seasons",
                      "evidence": "Spring turkey: Merriam's Apr 25 - May 22; Gould's May 9-22. Draw required."}]},
        {"title": "Grouse season runs Sep 1 - Nov 9 with a 3-bird daily bag. Chukar runs longer (Sep 1 - Feb 8) with a 5-bird daily bag.",
         "applies_to": ["Grouse (Blue/Sooty & Ruffed)", "Chukar Partridge"],
         "sources": [{"url": SOURCE_URL, "label": "AZGFD — Grouse & Chukar",
                      "evidence": "Grouse: Sep 1-Nov 9, 3 daily. Chukar: Sep 1-Feb 8, 5 daily."}]},
    ]

def build_dataset():
    print(f"[AZ_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[AZ_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Arizona", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | AZ | eRegulations",
            "last_updated": None, "update_note": "Data from AZGFD regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape AZGFD upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/AZ_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[AZ_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
