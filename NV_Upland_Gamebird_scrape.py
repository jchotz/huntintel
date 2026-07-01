#!/usr/bin/env python3
"""NV_Upland_Gamebird_scrape.py — HuntIntel Nevada Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/nevada/hunting/small-game/upland-game-bird-rabbit-dove-crow"
LICENSE_URL = "https://www.ndow.org/apply-buy/apply-buy-hunting/"
PURCHASE_URL = "https://ndowlicensing.com/"
LICENSE_PURCHASE_URLS = [
    {"label": "NDOW — License Portal", "url": "https://ndowlicensing.com/"},
    {"label": "NDOW — Apply & Buy", "url": "https://www.ndow.org/apply-buy/apply-buy-hunting/"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Upland Game Bird | Nevada eRegulations",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from NDOW. Nevada has chukar, quail, grouse, pheasant, snowcock, and sage-grouse.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Blue (Dusky & Sooty) & Ruffed Grouse", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "December 31, 2026",
         "season_raw": "September 1 - December 31, 2026",
         "hunting_units": "Designated counties (Carson City, Douglas, Elko, Washoe, etc.)",
         "bag_limit": "3 daily (singly or aggregate)", "possession_limit": "9"},
        {"name": "Sage Grouse", "asterisk": True,
         "season_start": "September 19, 2026", "season_end": "September 27, 2026",
         "season_raw": "Most units: Sep 19-27; some units: Sep 19-20; Sheldon NWR: Sep 26-27 (draw)",
         "hunting_units": "Limited hunt units; closed to nonresidents except Sheldon NWR draw",
         "bag_limit": "2 daily", "possession_limit": "4"},
        {"name": "Chukar & Hungarian (Gray) Partridge", "asterisk": False,
         "season_start": "October 10, 2026", "season_end": "February 7, 2027",
         "season_raw": "October 10, 2026 - February 7, 2027",
         "hunting_units": "Statewide",
         "bag_limit": "6 daily (combined chukar & Huns)", "possession_limit": "18"},
        {"name": "California & Gambel's Quail", "asterisk": False,
         "season_start": "October 10, 2026", "season_end": "February 7, 2027",
         "season_raw": "October 10, 2026 - February 7, 2027",
         "hunting_units": "Statewide", "bag_limit": "10 daily (combined)", "possession_limit": "30"},
        {"name": "Mountain Quail", "asterisk": False,
         "season_start": "October 10, 2026", "season_end": "February 7, 2027",
         "season_raw": "October 10, 2026 - February 7, 2027",
         "hunting_units": "Statewide", "bag_limit": "2 daily", "possession_limit": "6"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "November 1, 2026", "season_end": "November 30, 2026",
         "season_raw": "November 1 - 30, 2026",
         "hunting_units": "Statewide", "bag_limit": "2 roosters daily", "possession_limit": "6"},
        {"name": "Himalayan Snowcock", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "November 30, 2026",
         "season_raw": "September 1 - November 30, 2026",
         "hunting_units": "Elko and White Pine counties (Ruby Mountains)",
         "bag_limit": "2 daily; 2 season limit", "possession_limit": "2",
         "key_note": "Free-use permit required"},
    ]

def build_licenses():
    return [
        {"name": "Resident Hunting License", "asterisk": False,
         "covers": "All hunting including upland birds", "resident_cost": "$38.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Hunting License", "asterisk": False,
         "covers": "Hunting for nonresidents", "resident_cost": None,
         "nonresident_cost": "$155.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Himalayan Snowcock Free-Use Permit", "asterisk": True,
         "covers": "Required to hunt Himalayan snowcock (free)",
         "resident_cost": "Free", "nonresident_cost": "Free", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Sage grouse hunting is limited to specific hunt units and is closed to nonresidents except for the Sheldon National Wildlife Refuge draw.",
         "applies_to": ["Sage Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Sage Grouse",
                      "evidence": "Sage Grouse: Most units Sep 19-27. Closed to nonresidents except Sheldon NWR draw."}]},
        {"title": "Himalayan snowcock is unique to Nevada (Ruby Mountains) and requires a free-use permit. Daily limit 2, season limit 2.",
         "applies_to": ["Himalayan Snowcock", "Himalayan Snowcock Free-Use Permit"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Snowcock",
                      "evidence": "Himalayan Snowcock: Elko and White Pine counties. Sep 1 - Nov 30. Free-use permit required."}]},
        {"title": "Chukar and Hungarian partridge share a combined daily bag of 6. Quail (California & Gambel's) also have a combined bag of 10. Mountain quail is limited to 2 daily.",
         "applies_to": ["Chukar & Hungarian (Gray) Partridge", "California & Gambel's Quail", "Mountain Quail"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Quail & Chukar Limits",
                      "evidence": "Chukar/Huns: 6 daily. California/Gambel's quail: 10 daily. Mountain quail: 2 daily."}]},
        {"title": "Pheasant season is limited to November 1-30 statewide. Bag limit is 2 roosters daily.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "NDOW — Pheasant",
                      "evidence": "Pheasant: Nov 1-30. 2 roosters daily."}]},
    ]

def build_dataset():
    print(f"[NV_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NV_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Nevada", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Upland Game Bird | NV eRegulations",
            "last_updated": None, "update_note": "Data from NDOW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape NDOW upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/NV_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[NV_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
