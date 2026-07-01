#!/usr/bin/env python3
"""
MO_Upland_Gamebird_scrape.py — HuntIntel Missouri Upland Game Bird Scraper
"""
import argparse, json, re, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

SOURCE_URL = "https://mdc.mo.gov/hunting-trapping/seasons"
LICENSE_URL = "https://mdc.mo.gov/permits/hunting-permits"
PURCHASE_URL = "https://mdc.mo.gov/epermits"

LICENSE_PURCHASE_URLS = [
    {"label": "MDC e-Permits System", "url": "https://mdc.mo.gov/epermits"},
    {"label": "MDC — Hunting Permits", "url": "https://mdc.mo.gov/permits/hunting-permits"}
]

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; +https://huntintel.io)"}

def fetch_html(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def scrape_source_meta(soup):
    return {"page_url": SOURCE_URL, "page_label": "Hunting Seasons | Missouri Department of Conservation",
        "last_updated": None,
        "update_note": "2026-27 upland game bird data from MDC seasons page. Missouri has quail, pheasant, and turkey.",
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

def build_species():
    return [
        {"name": "Bobwhite Quail", "asterisk": False,
         "season_start": "November 1, 2026", "season_end": "January 15, 2027",
         "season_raw": "November 1, 2026 - January 15, 2027",
         "hunting_units": "Statewide", "bag_limit": "8 daily", "possession_limit": "24"},
        {"name": "Ring-necked Pheasant", "asterisk": True,
         "season_start": "November 1, 2026", "season_end": "January 15, 2027",
         "season_raw": "November 1, 2026 - January 15, 2027",
         "hunting_units": "Limited areas (primarily northern MO)", "bag_limit": "2 cocks daily", "possession_limit": "6"},
        {"name": "Wild Turkey (Spring)", "asterisk": True,
         "season_start": "April 20, 2026", "season_end": "May 10, 2026",
         "season_raw": "April 20 - May 10, 2026 (Youth: Apr 11-12)",
         "hunting_units": "Statewide", "bag_limit": "2 bearded turkeys (resident), 1 (nonresident)",
         "possession_limit": "2",
         "sub_seasons": [
             {"name": "Youth Season (ages 6-15)", "season_start": "April 11, 2026", "season_end": "April 12, 2026",
              "bag_limit": "1 bearded turkey", "possession_limit": "1"},
             {"name": "Regular Season", "season_start": "April 20, 2026", "season_end": "May 10, 2026",
              "bag_limit": "2 bearded turkeys (res), 1 (nonres)", "possession_limit": "2"}
         ]},
        {"name": "Wild Turkey (Fall)", "asterisk": True,
         "season_start": "October 1, 2026", "season_end": "January 15, 2027",
         "season_raw": "Fall Firearms: Oct 1-31; Fall Archery: Sep 15-Nov 13 & Nov 25-Jan 15",
         "hunting_units": "Statewide (firearms restricted in 7 counties)",
         "bag_limit": "2 either-sex (archery + firearms combined)",
         "possession_limit": "2"},
    ]

def build_licenses():
    return [
        {"name": "Small Game Hunting Permit", "asterisk": False, "covers": "Quail, pheasant, rabbit, squirrel, and other small game",
         "resident_cost": "$12.50", "nonresident_cost": "$102.00", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Spring Turkey Hunting Permit", "asterisk": True, "covers": "Spring turkey season (1 or 2 bearded turkeys)",
         "resident_cost": "$19.50", "nonresident_cost": "$304.50", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Fall Turkey Hunting Permit", "asterisk": True, "covers": "Fall turkey season (2 either-sex)",
         "resident_cost": "$15.00", "nonresident_cost": "$176.50", "purchase_urls": LICENSE_PURCHASE_URLS},
        {"name": "Archer's Hunting Permit", "asterisk": False,
         "covers": "Deer archery + small game + furbearers; includes fall turkey archery",
         "resident_cost": "$22.00", "nonresident_cost": "$360.00", "purchase_urls": LICENSE_PURCHASE_URLS},
    ]

def build_key_notes():
    return [
        {"title": "Missouri residents and resident landowners may harvest 2 male/bearded turkeys in spring. Nonresidents may harvest 1. Only 1 in the first week.",
         "applies_to": ["Wild Turkey (Spring)"],
         "sources": [{"url": LICENSE_URL, "label": "MDC — Spring Turkey Permits",
                      "evidence": "Missouri residents and nonresident landowners may harvest two male turkeys or turkeys with visible beard. Nonresident hunters may harvest one bearded turkey. Only one turkey may be taken during the first week."}]},
        {"title": "Fall turkey firearms season is not allowed in Dunklin, McDonald, Mississippi, New Madrid, Newton, Pemiscot, and Scott counties. Archery is statewide.",
         "applies_to": ["Wild Turkey (Fall)"],
         "sources": [{"url": LICENSE_URL, "label": "MDC — Fall Turkey Permits",
                      "evidence": "During the firearms portion of fall turkey season, you may hunt turkeys with firearms except in Dunklin, McDonald, Mississippi, New Madrid, Newton, Pemiscot, and Scott counties."}]},
        {"title": "Pheasant hunting is limited primarily to northern Missouri. Only cock (male) pheasants may be taken.",
         "applies_to": ["Ring-necked Pheasant"],
         "sources": [{"url": SOURCE_URL, "label": "MDC — Pheasant Season",
                      "evidence": "Pheasant: Nov 1, 2026 - Jan 15, 2027. Daily limit: 2 cocks."}]},
    ]

def build_dataset():
    print(f"[MO_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try: soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MO_upland] WARNING: Could not fetch: {e}", file=sys.stderr)
        print("[MO_upland] Using hardcoded data.", file=sys.stderr)
        soup = None
    dataset = {"state": "Missouri", "category": "Upland Game Birds",
        "source": scrape_source_meta(soup) if soup else {"page_url": SOURCE_URL,
            "page_label": "Hunting Seasons | MDC", "last_updated": None,
            "update_note": "Could not fetch source page. Data from MDC seasons page.",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "species": build_species(), "licenses": build_licenses(), "key_notes": build_key_notes()}
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Scrape MDC upland game bird data into JSON.")
    parser.add_argument("--output", "-o", default="data/MO_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/MO_Upland_Gamebird_dataset.json)")
    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty-print")
    args = parser.parse_args()
    dataset = build_dataset()
    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)
    with open(args.output, "w", encoding="utf-8") as f: f.write(output_str)
    print(f"[MO_upland] Wrote {args.output}", file=sys.stderr); print(output_str)

if __name__ == "__main__":
    main()
