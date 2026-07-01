#!/usr/bin/env python3
"""NM_Migratory_Bird_scrape.py — HuntIntel New Mexico Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/newmexico/hunting/hunting-seasons-and-dates"
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
    return {"page_url": SOURCE_URL, "page_label": "Hunting Seasons and Dates | New Mexico | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from NM DGF regulation pages. New Mexico is in the Central Flyway with North and South duck zones.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "January 1, 2027",
         "season_raw": "North Zone: Sep 1-Nov 29; South Zone: Sep 1-Oct 28 & Dec 1-Jan 1",
         "hunting_units": "North and South Zones (see sub-seasons)",
         "bag_limit": "15 daily (combined mourning & white-winged)", "possession_limit": "45",
         "sub_seasons": [
             {"name": "North Zone", "season_start": "September 1, 2026", "season_end": "November 29, 2026",
              "bag_limit": "15 daily", "possession_limit": "45"},
             {"name": "South Zone — Segment 1", "season_start": "September 1, 2026", "season_end": "October 28, 2026",
              "bag_limit": "15 daily", "possession_limit": "45"},
             {"name": "South Zone — Segment 2", "season_start": "December 1, 2026", "season_end": "January 1, 2027",
              "bag_limit": "15 daily", "possession_limit": "45"},
         ]},
        {"name": "Band-tailed Pigeon", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "October 14, 2026",
         "season_raw": "Regular: Sep 1-14; Southwest: Oct 1-14",
         "hunting_units": "Statewide (regular); Southwest Zone (Oct)",
         "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Teal (September Teal)", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "September 20, 2026",
         "season_raw": "September 12 - 20, 2026",
         "hunting_units": "Statewide", "bag_limit": "6 daily", "possession_limit": "18"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "October 10, 2026", "season_end": "January 31, 2027",
         "season_raw": "North Zone: Oct 10-Jan 13; South Zone: Oct 27-Jan 30",
         "hunting_units": "North and South Zones",
         "bag_limit": "6 ducks daily (species restrictions), 15 coot daily",
         "possession_limit": "18 duck, 45 coot",
         "sub_seasons": [
             {"name": "North Zone", "season_start": "October 10, 2026", "season_end": "January 13, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone", "season_start": "October 27, 2026", "season_end": "January 30, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Dark Goose (Canada & White-fronted)", "asterisk": True,
         "season_start": "October 16, 2026", "season_end": "January 31, 2027",
         "season_raw": "Regular: Oct 16-Jan 30; MRGV: Dec 19-Jan 31",
         "hunting_units": "Statewide (regular); Middle Rio Grande Valley (MRGV)",
         "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Light Goose (Snow, Blue, Ross's)", "asterisk": False,
         "season_start": "October 16, 2026", "season_end": "January 31, 2027",
         "season_raw": "October 16 - January 31, 2027",
         "hunting_units": "Statewide", "bag_limit": "20 daily", "possession_limit": "60"},
        {"name": "Sandhill Crane", "asterisk": True,
         "season_start": "October 25, 2026", "season_end": "January 22, 2027",
         "season_raw": "Eastern: Oct 25-Jan 22; Estancia Valley: Nov 1-9; Southwestern: Nov 1-9 & Jan 3-4",
         "hunting_units": "Eastern, Estancia Valley, Southwestern, MRGV Zones",
         "bag_limit": "3 daily (limited quota)", "possession_limit": "9"},
        {"name": "Snipe", "asterisk": False,
         "season_start": "October 10, 2026", "season_end": "January 24, 2027",
         "season_raw": "October 10, 2026 - January 24, 2027",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Rail (Sora & Virginia) & Gallinule", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "November 20, 2026",
         "season_raw": "September 12 - November 20, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 rail daily; 1 gallinule daily",
         "possession_limit": "75 rail; 3 gallinule"},
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
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$25.00",
         "nonresident_cost": "$25.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Sandhill Crane Permit", "asterisk": True,
         "covers": "Required to hunt sandhill crane (drawing required in most zones)",
         "resident_cost": "$10.00", "nonresident_cost": "$50.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "New Mexico has North and South duck zones. The South Zone opens later (Oct 27) and runs longer (Jan 30).",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Duck Zones",
                      "evidence": "North Zone: Oct 10 - Jan 13. South Zone: Oct 27 - Jan 30."}]},
        {"title": "Sandhill crane hunting is by permit in multiple zones (Eastern, Estancia Valley, Southwestern, MRGV). A Sandhill Crane Permit is required.",
         "applies_to": ["Sandhill Crane"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Sandhill Crane",
                      "evidence": "Sandhill Crane: Eastern Oct 25-Jan 22; Estancia Valley Nov 1-9; Southwestern Nov 1-9 & Jan 3-4."}]},
        {"title": "The New Mexico Habitat Stamp ($5) is required annually for all hunters, in addition to a Game Hunting License.",
         "applies_to": ["Resident Game Hunting License", "Habitat Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "NMDGF — License Fees",
                      "evidence": "Habitat Stamp: $5. Required annually for all hunters."}]},
        {"title": "Band-tailed pigeon has a short season (Sep 1-14 statewide, Oct 1-14 in Southwest Zone). Bag limit is 5 daily.",
         "applies_to": ["Band-tailed Pigeon"],
         "sources": [{"url": SOURCE_URL, "label": "NMDGF — Band-tailed Pigeon",
                      "evidence": "Band-tailed Pigeon: Regular Sep 1-14. Southwest: Oct 1-14. 5 daily."}]},
    ]

def build_dataset():
    print(f"[NM_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NM_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "New Mexico", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | NM | eRegulations",
            "last_updated": None, "update_note": "Data from NM DGF regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape NMDGF migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/NM_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[NM_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
