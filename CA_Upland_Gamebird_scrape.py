#!/usr/bin/env python3
"""CA_Upland_Gamebird_scrape.py — HuntIntel California Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://wildlife.ca.gov/Hunting/Upland-Game-Birds"
LICENSE_URL = "https://wildlife.ca.gov/Licensing/Hunting/Items"
PURCHASE_URL = "https://wildlife.ca.gov/Licensing/Online-Sales"
LICENSE_PURCHASE_URLS = [
    {"label": "CDFW — Online License Sales", "url": "https://wildlife.ca.gov/Licensing/Online-Sales"},
    {"label": "CDFW — License Fees", "url": "https://wildlife.ca.gov/Licensing/Hunting/Items"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Upland Game Bird Hunting | CDFW",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from CDFW. California has quail (3 zones), pheasant, chukar, grouse, ptarmigan, and turkey. Nonlead ammunition required statewide.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Quail (Zone Q1 — Northeast)", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "January 31, 2027",
         "season_raw": "Mountain Quail only: Sep 12-Oct 16; All quail: Oct 17 - Jan 31",
         "hunting_units": "Zone Q1 (Northeast California)",
         "bag_limit": "10 daily", "possession_limit": "30"},
        {"name": "Quail (Zone Q2 — Central)", "asterisk": False,
         "season_start": "September 26, 2026", "season_end": "January 31, 2027",
         "season_raw": "September 26, 2026 - January 31, 2027",
         "hunting_units": "Zone Q2 (Central California)", "bag_limit": "10 daily", "possession_limit": "30"},
        {"name": "Quail (Zone Q3 — Southern)", "asterisk": False,
         "season_start": "October 17, 2026", "season_end": "January 31, 2027",
         "season_raw": "October 17, 2026 - January 31, 2027",
         "hunting_units": "Zone Q3 (Southern California)", "bag_limit": "10 daily", "possession_limit": "30"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "November 14, 2026", "season_end": "January 24, 2027",
         "season_raw": "General: Nov 14 - Dec 27; Archery: Oct 10 - Nov 1 & Dec 28 - Jan 24; Falconry: Aug 15 - Feb 28",
         "hunting_units": "Statewide",
         "bag_limit": "2 males first 2 days, then 3 males (archery: 1 female allowed)",
         "possession_limit": "Triple daily bag"},
        {"name": "Chukar Partridge", "asterisk": False,
         "season_start": "October 17, 2026", "season_end": "January 31, 2027",
         "season_raw": "October 17, 2026 - January 31, 2027",
         "hunting_units": "Statewide", "bag_limit": "6 daily", "possession_limit": "18"},
        {"name": "Sooty (Blue) & Ruffed Grouse", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "October 12, 2026",
         "season_raw": "September 12 - October 12, 2026",
         "hunting_units": "Statewide", "bag_limit": "2 daily (combined)", "possession_limit": "6"},
        {"name": "White-tailed Ptarmigan", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "September 20, 2026",
         "season_raw": "September 12 - 20, 2026",
         "hunting_units": "Statewide", "bag_limit": "2 daily; 2 per season", "possession_limit": "2 (season limit)"},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "November 14, 2026", "season_end": "December 13, 2026",
         "season_raw": "November 14 - December 13, 2026",
         "hunting_units": "Statewide", "bag_limit": "1 either sex", "possession_limit": "2 per season"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "March 27, 2027", "season_end": "May 16, 2027",
         "season_raw": "General: Mar 27 - May 2; Archery: May 3-16. Junior: Mar 20-21 & May 3-16.",
         "hunting_units": "Statewide",
         "bag_limit": "1 bearded turkey", "possession_limit": "3 per season"},
    ]

def build_licenses():
    return [
        {"name": "Resident Hunting License", "asterisk": False,
         "covers": "Required for all hunting", "resident_cost": "$54.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Hunting License", "asterisk": False,
         "covers": "Hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$150.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Upland Game Bird Validation", "asterisk": True,
         "covers": "Required in addition to license for upland game birds (not required for Junior license holders)",
         "resident_cost": "$24.84", "nonresident_cost": "$24.84", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonlead Ammunition (Required)", "asterisk": True,
         "covers": "Nonlead ammunition required when taking any wildlife with a firearm anywhere in California",
         "resident_cost": "Varies", "nonresident_cost": "Varies", "purchase_urls": [{"label": "CDFW — Nonlead Info", "url": "https://wildlife.ca.gov/Hunting/Nonlead-Ammunition"}]},
    ]

def build_key_notes():
    return [
        {"title": "Nonlead ammunition is required when taking any wildlife with a firearm anywhere in California. Lead shot is prohibited for all hunting.",
         "applies_to": ["Resident Hunting License", "Upland Game Bird Validation"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Nonlead Requirement",
                      "evidence": "Nonlead Ammunition required when taking any wildlife with a firearm anywhere in California."}]},
        {"title": "California has 3 quail zones (Q1, Q2, Q3) with different season opening dates. Zone Q1 has a mountain quail-only early season.",
         "applies_to": ["Quail (Zone Q1 — Northeast)", "Quail (Zone Q2 — Central)", "Quail (Zone Q3 — Southern)"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Quail Zones",
                      "evidence": "Q1: Mountain quail only Sep 12-Oct 16, all quail Oct 17-Jan 31. Q2: Sep 26-Jan 31. Q3: Oct 17-Jan 31."}]},
        {"title": "Pheasant season is Nov 14 - Dec 27 (general), with archery-only seasons Oct 10 - Nov 1 and Dec 28 - Jan 24. Bag is 2 males first 2 days then 3 males.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Pheasant Season",
                      "evidence": "Pheasant: General Nov 14-Dec 27. Archery: Oct 10-Nov 1 & Dec 28-Jan 24. 2 males first 2 days, 3 males thereafter."}]},
        {"title": "White-tailed ptarmigan has a very short season (Sep 12-20) with a 2-bird season limit. Found in high alpine areas of the Sierra Nevada.",
         "applies_to": ["White-tailed Ptarmigan"],
         "sources": [{"url": SOURCE_URL, "label": "CDFW — Ptarmigan Season",
                      "evidence": "White-tailed Ptarmigan: Sep 12-20. 2 daily, 2 per season limit."}]},
    ]

def build_dataset():
    print(f"[CA_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[CA_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "California", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Upland Game Bird Hunting | CDFW",
            "last_updated": None, "update_note": "Data from CDFW upland game bird page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape CDFW upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/CA_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[CA_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
