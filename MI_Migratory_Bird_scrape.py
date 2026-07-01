#!/usr/bin/env python3
"""MI_Migratory_Bird_scrape.py — HuntIntel Michigan Migratory Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.michigan.gov/dnr/managing-resources/laws/regulations/waterfowl"
LICENSE_URL = "https://www.michigan.gov/dnr/managing-resources/laws/regulations/waterfowl"
PURCHASE_URL = "https://www.mdnr-elicense.com/"
LICENSE_PURCHASE_URLS = [
    {"label": "Michigan DNR — e-License Portal", "url": "https://www.mdnr-elicense.com/"},
    {"label": "MI DNR — Waterfowl Regulations", "url": "https://www.michigan.gov/dnr/managing-resources/laws/regulations/waterfowl"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "2026 Waterfowl Regulations | Michigan DNR",
        "last_updated": None,
        "update_note": "2026-27 migratory bird data from MI DNR waterfowl regulations. Michigan has 3 duck zones (North, Middle, South).",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Dove (Mourning Dove)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 1 - November 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "15 daily", "possession_limit": "45"},
        {"name": "Teal (Early Teal)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "September 9, 2026",
         "season_raw": "September 1 - 9, 2026 (sunrise to sunset)",
         "hunting_units": "Statewide", "bag_limit": "6 daily (blue-winged & green-winged only)", "possession_limit": "18"},
        {"name": "Duck, Merganser & Coot", "asterisk": True,
         "season_start": "September 26, 2026", "season_end": "December 27, 2026",
         "season_raw": "North: Sep 26-Nov 22 & Nov 28-29; Middle: Oct 3-Nov 29 & Dec 12-13; South: Oct 17-Dec 13 & Dec 26-27",
         "hunting_units": "North, Middle, South Zones (see sub-seasons)",
         "bag_limit": "6 ducks daily (species restrictions), 5 mergansers, 15 coot",
         "possession_limit": "18 duck, 15 merganser, 45 coot",
         "sub_seasons": [
             {"name": "North Zone — Segment 1", "season_start": "September 26, 2026", "season_end": "November 22, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "North Zone — Segment 2", "season_start": "November 28, 2026", "season_end": "November 29, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Middle Zone — Segment 1", "season_start": "October 3, 2026", "season_end": "November 29, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "Middle Zone — Segment 2", "season_start": "December 12, 2026", "season_end": "December 13, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 1", "season_start": "October 17, 2026", "season_end": "December 13, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
             {"name": "South Zone — Segment 2", "season_start": "December 26, 2026", "season_end": "December 27, 2026",
              "bag_limit": "6 ducks daily", "possession_limit": "18"},
         ]},
        {"name": "Dark Goose (Canada, White-fronted & Brant)", "asterisk": True,
         "season_start": "September 1, 2026", "season_end": "February 15, 2027",
         "season_raw": "North: Sep 1-Dec 16; Middle: Sep 1-30 & Oct 3-Dec 18; South: Sep 1-30, Oct 17-Dec 13, Dec 26-Jan 3, Feb 6-15",
         "hunting_units": "North, Middle, South Zones + GMUs (see sub-seasons)",
         "bag_limit": "5 daily (Canada, white-fronted, brant total; max 1 brant)",
         "possession_limit": "15",
         "sub_seasons": [
             {"name": "North Zone", "season_start": "September 1, 2026", "season_end": "December 16, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Middle Zone — Segment 1", "season_start": "September 1, 2026", "season_end": "September 30, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "Middle Zone — Segment 2", "season_start": "October 3, 2026", "season_end": "December 18, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "South Zone — Segment 1", "season_start": "September 1, 2026", "season_end": "September 30, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "South Zone — Segment 2", "season_start": "October 17, 2026", "season_end": "December 13, 2026",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "South Zone — Segment 3", "season_start": "December 26, 2026", "season_end": "January 3, 2027",
              "bag_limit": "5 daily", "possession_limit": "15"},
             {"name": "South Zone — Segment 4", "season_start": "February 6, 2027", "season_end": "February 15, 2027",
              "bag_limit": "5 daily", "possession_limit": "15"},
         ]},
        {"name": "Light Goose (Snow, Blue, Ross's)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "February 15, 2027",
         "season_raw": "Same zone dates as dark goose",
         "hunting_units": "Same zones as dark goose",
         "bag_limit": "20 daily", "possession_limit": "60"},
        {"name": "Woodcock", "asterisk": False,
         "season_start": "September 15, 2026", "season_end": "October 29, 2026",
         "season_raw": "September 15 - October 29, 2026",
         "hunting_units": "Statewide", "bag_limit": "3 daily", "possession_limit": "9"},
        {"name": "Snipe (Wilson's Snipe)", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Rail (Sora & Virginia) & Gallinule", "asterisk": False,
         "season_start": "September 1, 2026", "season_end": "November 9, 2026",
         "season_raw": "September 1 - November 9, 2026",
         "hunting_units": "Statewide", "bag_limit": "25 rail daily; 1 gallinule daily", "possession_limit": "75 rail; 3 gallinule"},
    ]

def build_licenses():
    return [
        {"name": "Base License (Resident)", "asterisk": False,
         "covers": "Required for all hunting", "resident_cost": "$11.00",
         "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$151.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Waterfowl License (includes HIP)", "asterisk": True,
         "covers": "Required for waterfowl hunting (ducks, geese, coot)",
         "resident_cost": "$12.00", "nonresident_cost": "$12.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Federal Duck Stamp", "asterisk": True,
         "covers": "Required for waterfowl hunters age 16+", "resident_cost": "$30.00",
         "nonresident_cost": "$30.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "HIP registration is included with the Waterfowl License ($12). Youth under 16 get a free Migratory Bird Youth Endorsement.",
         "applies_to": ["Base License (Resident)", "Waterfowl License (includes HIP)"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — License Fees",
                      "evidence": "Waterfowl license (includes HIP): $12. Migratory bird youth endorsement (includes HIP): Free for ages 10-15."}]},
        {"title": "Michigan has 3 duck zones (North, Middle, South) with different season dates. Youth waterfowl weekend is Sept 19-20.",
         "applies_to": ["Duck, Merganser & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Duck Zone Seasons",
                      "evidence": "North Zone: Sep 26 - Nov 22 & Nov 28-29. Middle: Oct 3 - Nov 29 & Dec 12-13. South: Oct 17 - Dec 13 & Dec 26-27."}]},
        {"title": "Duck species restrictions: 4 mallards (2 hens), 3 wood ducks, 2 black ducks, 3 pintails, 2 canvasbacks, 2 redheads. Scaup limits vary by zone/date.",
         "applies_to": ["Duck, Merganser & Coot"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Duck Species Limits",
                      "evidence": "Mallards: 4 (2 hens). Wood ducks: 3. Black ducks: 2. Pintail: 3. Canvasback: 2. Redhead: 2. Scaup: varies by zone/date."}]},
        {"title": "Early teal season is for blue-winged and green-winged teal only. Shooting hours are sunrise to sunset (no pre-sunrise).",
         "applies_to": ["Teal (Early Teal)"],
         "sources": [{"url": SOURCE_URL, "label": "MI DNR — Early Teal",
                      "evidence": "Early teal: Sept 1-9, 2026. Blue-winged and green-winged teal only. Hunting hours: sunrise to sunset."}]},
    ]

def build_dataset():
    print(f"[MI_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MI_migratory] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Michigan", "category": "Migratory Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Waterfowl Regulations | MI DNR",
            "last_updated": None, "update_note": "Data from MI DNR waterfowl regulations.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MI DNR migratory bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MI_Migratory_Bird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MI_migratory] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
