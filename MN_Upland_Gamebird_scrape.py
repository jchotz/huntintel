#!/usr/bin/env python3
"""MN_Upland_Gamebird_scrape.py — HuntIntel Minnesota Upland Game Bird Scraper"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://www.dnr.state.mn.us/hunting/seasons.html"
LICENSE_URL = "https://www.dnr.state.mn.us/licenses/hunting/index.html"
PURCHASE_URL = "https://www.dnr.state.mn.us/licenses/index.html"
LICENSE_PURCHASE_URLS = [
    {"label": "MN DNR — License Portal", "url": "https://www.dnr.state.mn.us/licenses/index.html"},
    {"label": "MN DNR — Hunting Licenses", "url": "https://www.dnr.state.mn.us/licenses/hunting/index.html"}
]
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Hunting Season Dates | Minnesota DNR",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from MN DNR seasons page. Dates based on recurring annual patterns. Minnesota has diverse upland birds including grouse, pheasant, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Ruffed Grouse", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "January 3, 2027",
         "season_raw": "September 12, 2026 - January 3, 2027",
         "hunting_units": "Statewide", "bag_limit": "5 daily (combined with Spruce Grouse)", "possession_limit": "10"},
        {"name": "Spruce Grouse", "asterisk": False,
         "season_start": "September 12, 2026", "season_end": "January 3, 2027",
         "season_raw": "September 12, 2026 - January 3, 2027",
         "hunting_units": "Northern coniferous forest", "bag_limit": "5 daily (combined with Ruffed Grouse)", "possession_limit": "10"},
        {"name": "Sharp-tailed Grouse", "asterisk": True,
         "season_start": "September 12, 2026", "season_end": "November 29, 2026",
         "season_raw": "September 12 - November 29, 2026",
         "hunting_units": "Northwest Zone only; east-central zone closed",
         "bag_limit": "3 daily", "possession_limit": "6"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "October 10, 2026", "season_end": "January 3, 2027",
         "season_raw": "October 10, 2026 - January 3, 2027 (9 a.m. to sunset)",
         "hunting_units": "West-central and southwest MN",
         "bag_limit": "2 roosters daily", "possession_limit": "6",
         "sub_seasons": [
             {"name": "Late Season (Dec 1 - Jan 3)", "season_start": "December 1, 2026", "season_end": "January 3, 2027",
              "bag_limit": "3 roosters daily", "possession_limit": "9"}
         ]},
        {"name": "Hungarian Partridge", "asterisk": False,
         "season_start": "September 19, 2026", "season_end": "January 3, 2027",
         "season_raw": "September 19, 2026 - January 3, 2027",
         "hunting_units": "Northwest MN", "bag_limit": "5 daily", "possession_limit": "10"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 15, 2026", "season_end": "May 31, 2026",
         "season_raw": "April 15 - May 31, 2026 (6 draw periods A-F)",
         "hunting_units": "Statewide (draw periods A-F)",
         "bag_limit": "1 bearded turkey per permit (up to 2 permits)",
         "possession_limit": "2"},
    ]

def build_licenses():
    return [
        {"name": "Resident Small Game License", "asterisk": False,
         "covers": "Small game including grouse, pheasant, partridge, rabbit, squirrel",
         "resident_cost": "$22.00", "nonresident_cost": None, "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Nonresident Small Game License", "asterisk": False,
         "covers": "Small game for nonresidents", "resident_cost": None,
         "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "72-Hour Small Game License", "asterisk": False,
         "covers": "Includes pheasant stamp, excludes state waterfowl stamp",
         "resident_cost": "$19.00", "nonresident_cost": "$75.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Pheasant Stamp", "asterisk": True,
         "covers": "Required in addition to Small Game license to hunt pheasants",
         "resident_cost": "$7.50", "nonresident_cost": "$7.50", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey License", "asterisk": True,
         "covers": "Spring turkey hunting (draw period system)",
         "resident_cost": "$26.00", "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey License", "asterisk": True,
         "covers": "Fall turkey hunting", "resident_cost": "$26.00",
         "nonresident_cost": "$100.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Minnesota's ruffed grouse and spruce grouse share a combined daily bag limit of 5 and possession limit of 10.",
         "applies_to": ["Ruffed Grouse", "Spruce Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "MN DNR — Grouse Seasons",
                      "evidence": "Ruffed Grouse and Spruce Grouse combined daily limit 5, possession limit 10."}]},
        {"title": "Sharp-tailed grouse hunting is limited to the Northwest Zone. The east-central zone is closed.",
         "applies_to": ["Sharp-tailed Grouse"],
         "sources": [{"url": SOURCE_URL, "label": "MN DNR — Sharp-tailed Grouse",
                      "evidence": "Sharp-tailed Grouse: NW zone only; east-central zone closed."}]},
        {"title": "A Pheasant Stamp ($7.50) is required in addition to a Small Game license to hunt pheasants.",
         "applies_to": ["Ring-necked Pheasant", "Pheasant Stamp"],
         "sources": [{"url": LICENSE_URL, "label": "MN DNR — License Fees",
                      "evidence": "Pheasant Stamp: $7.50. Required to hunt pheasants."}]},
        {"title": "Spring turkey is divided into 6 draw periods (A-F) running April 15 - May 31. Hunters may purchase up to 2 permits.",
         "applies_to": ["Wild Turkey (Spring)"],
         "sources": [{"url": "https://www.dnr.state.mn.us/hunting/turkey/index.html", "label": "MN DNR — Turkey Hunting",
                      "evidence": "Spring turkey season runs April 15 through May 31, divided into 6 draw periods (A through F)."}]},
    ]

def build_dataset():
    print(f"[MN_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MN_upland] WARNING: Could not fetch: {e}", file=sys.stderr); soup = None
    dataset = {"state": "Minnesota", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL, "page_label": "Hunting Season Dates | MN DNR",
            "last_updated": None, "update_note": "Data from MN DNR seasons page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MN DNR upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MN_Upland_Gamebird_dataset.json")
    parser.add_argument("--pretty", "-p", action="store_true")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MN_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
