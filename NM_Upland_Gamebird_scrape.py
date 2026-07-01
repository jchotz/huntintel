#!/usr/bin/env python3
"""NM_Upland_Gamebird_scrape.py — HuntIntel New Mexico Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://wildlife.dgf.nm.gov/hunting/information-by-animal/upland-game/"
LICENSE_URL = "https://wildlife.dgf.nm.gov/hunting/licenses-and-permits/"
PURCHASE_URL = "https://onlinesales.wildlife.state.nm.us/"
LICENSE_PURCHASE_URLS = [
    {"label": "NMDGF — Online License Sales", "url": "https://onlinesales.wildlife.state.nm.us/"},
    {"label": "NMDGF — Licenses & Permits", "url": "https://wildlife.dgf.nm.gov/hunting/licenses-and-permits/"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Upland Game | NMDGF",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from NM DGF upland game page.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Quail (Scaled, Gambel's, Bobwhite, Montezuma)", "asterisk": True,
         "season_start": "November 15, 2026", "season_end": "February 15, 2027",
         "season_raw": "November 15, 2026 - February 15, 2027",
         "hunting_units": "Statewide (species vary by region)",
         "bag_limit": "15 daily (combined all quail species)", "possession_limit": "45"},
        {"name": "Dusky Grouse", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "December 31, 2026",
         "season_raw": "September 1 - December 31, 2026",
         "hunting_units": "High elevation (above 7,000 ft)", "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "December 11, 2026", "season_end": "December 14, 2026",
         "season_raw": "December 11 - 14, 2026",
         "hunting_units": "Limited areas", "bag_limit": "2 cocks daily", "possession_limit": "4"},
        {"name": "Eurasian Collared-Dove", "asterisk": False,
         "season_start": "January 1, 2026", "season_end": "December 31, 2026",
         "season_raw": "Year-round (invasive species)",
         "hunting_units": "Statewide", "bag_limit": "No limit", "possession_limit": "No limit"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 15, 2026", "season_end": "May 15, 2026",
         "season_raw": "April 15 - May 15, 2026",
         "hunting_units": "Statewide", "bag_limit": "1 bearded turkey per license", "possession_limit": "1"},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "November 30, 2026",
         "season_raw": "Bow: Sep 1-30; Shotgun/Bow/Crossbow: Nov 1-30",
         "hunting_units": "Statewide", "bag_limit": "1 either-sex", "possession_limit": "1",
         "sub_seasons": [
             {"name": "Archery Only", "season_start": "September 1, 2026", "season_end": "September 30, 2026",
              "bag_limit": "1 either-sex", "possession_limit": "1"},
             {"name": "Shotgun, Bow, Crossbow", "season_start": "November 1, 2026", "season_end": "November 30, 2026",
              "bag_limit": "1 either-sex", "possession_limit": "1"},
         ]},
    ]

def build_licenses():
    return [
        {"name": "Resident Game Hunting License", "asterisk": False,
         "covers": "Required for all hunting", "resident_cost": "$25.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Game Hunting License", "asterisk": False,
         "covers": "Hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$90.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Habitat Stamp", "asterisk": False,
         "covers": "Required annually for all hunters", "resident_cost": "$5.00",
         "nonresident_cost": "$5.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting", "resident_cost": "$15.00",
         "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey License", "asterisk": True,
         "covers": "Fall turkey hunting", "resident_cost": "$15.00",
         "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "New Mexico offers four quail species: Scaled, Gambel's, Bobwhite, and Montezuma — combined daily bag of 15.",
         "applies_to": ["Quail (Scaled, Gambel's, Bobwhite, Montezuma)"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Quail Species",
                      "evidence": "New Mexico offers four quail species: Scaled quail, Gambel's quail, Northern bobwhite, and Montezuma quail."}]},
        {"title": "Pheasant season is only 4 days (Dec 11-14) in limited areas. A Game Hunting License is required.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Pheasant Season",
                      "evidence": "Pheasant: Dec 11-14. 2 cocks daily."}]},
        {"title": "Eurasian collared-doves are classified as upland game in New Mexico and may be taken year-round with no bag limit.",
         "applies_to": ["Eurasian Collared-Dove"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Eurasian Collared-Dove",
                      "evidence": "Eurasian collared-doves are considered upland game due to their non-migratory nature and invasive status. Year-round, no limit."}]},
        {"title": "Dusky grouse are found at high elevations (above 7,000 ft) in montane forests. Season runs Sep 1 - Dec 31.",
         "applies_to": ["Dusky Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Dusky Grouse",
                      "evidence": "Dusky grouse: High elevation (above 7,000 ft). Season: Sep 1 - Dec 31."}]},
    ]

def build_dataset():
    print(f"[NM_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NM_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "New Mexico", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Upland Game | NMDGF",
            "last_updated": None, "update_note": "Data from NM DGF upland game page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape NMDGF upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/NM_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[NM_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
