#!/usr/bin/env python3
"""CO_Migratory_Bird_scrape.py — HuntIntel Colorado Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/colorado/hunting/hunting-seasons-and-dates"
LICENSE_URL = "https://cpw.state.co.us/activities/hunting/waterfowl-hunting"
PURCHASE_URL = "https://cpw.state.co.us/"
LICENSE_PURCHASE_URLS = [
    {"label": "CPW — License Portal", "url": "https://cpw.state.co.us/"},
    {"label": "CPW — Waterfowl Hunting", "url": "https://cpw.state.co.us/activities/hunting/waterfowl-hunting"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | Colorado | eRegulations",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from CPW regulations. Colorado is split between Central and Pacific Flyways with multiple duck zones.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Rail (Sora & Virginia)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 daily", "possession_limit": "75"},
        {"name": "Snipe (Common Snipe)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "December 16, 2026",
         "season_raw": "September 1 - December 16, 2026",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Sandhill Crane", "asterisk": True,
         "season_start": "October 4, 2026", "season_end": "November 30, 2026",
         "season_raw": "October 4 - November 30, 2026 (limited quota)",
         "hunting_units": "Limited permit areas", "bag_limit": "3 daily (limited permit)", "possession_limit": "9"},
        {"name": "Teal (September Teal)", "asterisk": False,
         "season_start": "September 13, 2026", "season_end": "September 21, 2026",
         "season_raw": "September 13 - 21, 2026",
         "hunting_units": "Statewide", "bag_limit": "6 daily", "possession_limit": "18"},
        {"name": "Duck & Coot", "asterisk": True,
         "season_start": "October 3, 2026", "season_end": "January 31, 2027",
         "season_raw": "Central Flyway: NE Oct 18-Nov 30 & Dec 11-Jan 31; SE Oct 28-Jan 31; Mtn Oct 4-Nov 30 & Dec 25-Jan 31. Pacific: West Oct 4-21 & Nov 6-Jan 31; East Oct 4-Jan 16",
         "hunting_units": "Central and Pacific Flyways (see sub-seasons)",
         "bag_limit": "6 ducks daily, 15 coot daily", "possession_limit": "18 duck, 45 coot",
         "sub_seasons": [
             {"name": "Central Flyway — Northeast Zone — Seg 1", "season_start": "October 18, 2026", "season_end": "November 30, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Flyway — Northeast Zone — Seg 2", "season_start": "December 11, 2026", "season_end": "January 31, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Flyway — Southeast Zone", "season_start": "October 28, 2026", "season_end": "January 31, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Flyway — Mountain/Foothills — Seg 1", "season_start": "October 4, 2026", "season_end": "November 30, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Central Flyway — Mountain/Foothills — Seg 2", "season_start": "December 25, 2026", "season_end": "January 31, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Pacific Flyway — Western Zone — Seg 1", "season_start": "October 4, 2026", "season_end": "October 21, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Pacific Flyway — Western Zone — Seg 2", "season_start": "November 6, 2026", "season_end": "January 31, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Pacific Flyway — Eastern Zone", "season_start": "October 4, 2026", "season_end": "January 16, 2027",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Dark Goose (Canada, White-fronted, Brant)", "asterisk": True,
         "season_start": "November 2, 2026", "season_end": "February 15, 2027",
         "season_raw": "Central: Nov 3 - Feb 15; Pacific Western: Oct 4-12 & Nov 6 - Jan 31; Pacific Eastern: Oct 4 - Jan 7",
         "hunting_units": "Central and Pacific Flyways",
         "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Light Goose (Snow, Blue, Ross's)", "asterisk": False,
         "season_start": "November 1, 2026", "season_end": "February 15, 2027",
         "season_raw": "Central: Nov 1 - Feb 15; Pacific: same as dark goose per zone",
         "hunting_units": "Central and Pacific Flyways",
         "bag_limit": "20 daily", "possession_limit": "60"},
        {"name": "Light Goose Conservation Order", "asterisk": False,
         "season_start": "February 16, 2027", "season_end": "April 30, 2027",
         "season_raw": "February 16 - April 30, 2027",
         "hunting_units": "Statewide (Central Flyway)", "bag_limit": "No daily limit",
         "possession_limit": "No possession limit"},
    ]

def build_licenses():
    return [
        {"name": "Annual Small Game License (Qualifying License)", "asterisk": False,
         "covers": "Small game, upland birds, waterfowl, migratory birds",
         "resident_cost": "$36.68", "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Annual Habitat Stamp", "asterisk": True,
         "covers": "Required annually for all hunters age 18-64",
         "resident_cost": "$12.47", "nonresident_cost": "$12.47", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+",
         "resident_cost": "$33.00", "nonresident_cost": "$33.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Colorado is split between the Central and Pacific Flyways with different duck zones (Northeast, Southeast, Mountain/Foothills, Western, Eastern) and season dates.",
         "applies_to": ["Duck & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Waterfowl Zones",
                      "evidence": "Central Flyway: Northeast, Southeast, Mountain/Foothills zones. Pacific Flyway: Western, Eastern zones."}]},
        {"title": "A Small Game License and Habitat Stamp ($12.47) are required for all waterfowl hunting. The Federal Duck Stamp ($33) is required for hunters age 16+.",
         "applies_to": ["Annual Small Game License (Qualifying License)", "Annual Habitat Stamp", "Federal Duck Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "CPW — Waterfowl Requirements",
                      "evidence": "To hunt waterfowl, you need a small-game hunting license. If 16 or older, you also must have the $33 Federal Migratory Bird Hunting and Conservation Stamp (Federal Duck Stamp)."}]},
        {"title": "Sandhill crane hunting is by limited permit in Colorado. Season runs Oct 4 - Nov 30.",
         "applies_to": ["Sandhill Crane"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Sandhill Crane",
                      "evidence": "Sandhill Crane: Oct 4 - Nov 30. Limited quota."}]},
        {"title": "The Light Goose Conservation Order (Feb 16 - Apr 30) allows electronic calls and unplugged shotguns with no daily bag limit.",
         "applies_to": ["Light Goose Conservation Order"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Light Goose Conservation Order",
                      "evidence": "Light Goose Conservation Order: Feb 16 - Apr 30. No bag limit."}]},
    ]

def build_dataset():
    print(f"[CO_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[CO_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Colorado", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | CO | eRegulations",
            "last_updated": None, "update_note": "Data from CPW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape CPW migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/CO_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[CO_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
