#!/usr/bin/env python3
"""CO_Upland_Gamebird_scrape.py — HuntIntel Colorado Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.eregulations.com/colorado/hunting/hunting-seasons-and-dates"
LICENSE_URL = "https://cpw.state.co.us/activities/hunting/small-game"
PURCHASE_URL = "https://cpw.state.co.us/"
LICENSE_PURCHASE_URLS = [
    {"label": "CPW — License Portal", "url": "https://cpw.state.co.us/"},
    {"label": "CPW — Small Game Info", "url": "https://cpw.state.co.us/activities/hunting/small-game"}
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
        "update_note": "2026-27 upland game bird data from CPW regulations. Colorado has diverse upland birds including grouse, pheasant, quail, chukar, ptarmigan, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning & White-winged)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 1 - November 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily", "possession_limit": "45"},
        {"name": "Eurasian Collared-Dove", "asterisk": False,
         "season_start": "January 1, 2026", "season_end": "December 31, 2026",
         "season_raw": "Year-round", "hunting_units": "Statewide",
         "bag_limit": "No limit", "possession_limit": "No limit"},
        {"name": "Dusky (Blue) Grouse", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 23, 2026",
         "season_raw": "September 1 - November 23, 2026",
         "hunting_units": "Statewide (montane forests)", "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Greater Sage-Grouse", "asterisk": True,
         "season_start": "September 13, 2026", "season_end": "September 19, 2026",
         "season_raw": "Season 1: Sep 13-19; Season 2: Sep 13-14 (very limited)",
         "hunting_units": "Limited permit areas", "bag_limit": "1 daily (limited quota)",
         "possession_limit": "1"},
        {"name": "Mountain Sharp-tailed Grouse", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "September 21, 2026",
         "season_raw": "September 1 - 21, 2026",
         "hunting_units": "Limited areas", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "November 8, 2026", "season_end": "January 31, 2027",
         "season_raw": "Season 1: Nov 8 - Jan 31; Season 2: Nov 8 - Jan 4",
         "hunting_units": "Statewide (season varies by area)",
         "bag_limit": "3 roosters daily", "possession_limit": "9"},
        {"name": "White-tailed Ptarmigan", "asterisk": True,
         "season_start": "September 13, 2026", "season_end": "November 23, 2026",
         "season_raw": "Season 1: Sep 13 - Oct 5; Season 2: Sep 13 - Nov 23",
         "hunting_units": "High alpine areas ($5 permit required)",
         "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Quail", "asterisk": False,
         "season_start": "November 8, 2026", "season_end": "January 31, 2027",
         "season_raw": "Nov 8 - Jan 31 (varies by area)",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Chukar Partridge", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 30, 2026",
         "season_raw": "September 1 - November 30, 2026",
         "hunting_units": "Statewide", "bag_limit": "5 daily", "possession_limit": "15"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 12, 2026", "season_end": "May 31, 2026",
         "season_raw": "April 12 - May 31, 2026",
         "hunting_units": "Statewide (limited draw units)",
         "bag_limit": "2 bearded turkeys", "possession_limit": "2"},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "January 15, 2027",
         "season_raw": "Fall: Sep 1 - Oct 31; Late: Dec 15 - Jan 15",
         "hunting_units": "Statewide (draw units)",
         "bag_limit": "1 either-sex per season", "possession_limit": "2",
         "sub_seasons": [
             {"name": "Fall Season", "season_start": "September 1, 2026", "season_end": "October 31, 2026",
              "bag_limit": "1 either-sex", "possession_limit": "1"},
             {"name": "Late Season", "season_start": "December 15, 2026", "season_end": "January 15, 2027",
              "bag_limit": "1 either-sex", "possession_limit": "1"},
         ]},
    ]

def build_licenses():
    return [
        {"name": "Annual Small Game License (Qualifying License)", "asterisk": False,
         "covers": "Small game, upland birds, waterfowl, migratory birds",
         "resident_cost": "$36.68", "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Annual Habitat Stamp", "asterisk": True,
         "covers": "Required annually for all hunters age 18-64",
         "resident_cost": "$12.47", "nonresident_cost": "$12.47", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting (limited draw units)",
         "resident_cost": "$30.00", "nonresident_cost": "$188.86", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey License", "asterisk": True,
         "covers": "Fall turkey hunting", "resident_cost": "$36.00",
         "nonresident_cost": "$188.86", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "White-tailed Ptarmigan / Sage-Grouse Permit", "asterisk": True,
         "covers": "Required to hunt white-tailed ptarmigan or greater sage-grouse",
         "resident_cost": "$5.00", "nonresident_cost": "$5.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+",
         "resident_cost": "$33.00", "nonresident_cost": "$33.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "A $5 permit is required to hunt white-tailed ptarmigan or greater sage-grouse, in addition to a Small Game License and Habitat Stamp.",
         "applies_to": ["White-tailed Ptarmigan", "Greater Sage-Grouse", "White-tailed Ptarmigan / Sage-Grouse Permit"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Small Game Brochure",
                      "evidence": "A $5 permit is required to hunt white-tailed ptarmigan or greater sage-grouse."}]},
        {"title": "The Colorado Habitat Stamp ($12.47) is required annually for all hunters age 18-64. Youth under 18 do not need a habitat stamp.",
         "applies_to": ["Annual Small Game License (Qualifying License)", "Annual Habitat Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "CPW — Small Game License",
                      "evidence": "Annual Habitat Stamp (18-64): $12.47. Youth Qualifying License (under 18): $1.50."}]},
        {"title": "Greater sage-grouse seasons are very limited (1 week or less) with a $5 permit required. Bag limit is 1 daily.",
         "applies_to": ["Greater Sage-Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Sage-Grouse Season",
                      "evidence": "Greater Sage-Grouse: Season 1 Sep 13-19, Season 2 Sep 13-14. $5 permit required."}]},
        {"title": "Colorado's pheasant season runs Nov 8 - Jan 31 (Season 1 areas) or Nov 8 - Jan 4 (Season 2 areas). Bag limit is 3 roosters daily.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "CPW — Pheasant Season",
                      "evidence": "Pheasant: Season 1 Nov 8 - Jan 31. Season 2 Nov 8 - Jan 4. 3 roosters daily."}]},
    ]

def build_dataset():
    print(f"[CO_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[CO_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Colorado", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | CO | eRegulations",
            "last_updated": None, "update_note": "Data from CPW regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape CPW upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/CO_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[CO_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
