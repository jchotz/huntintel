#!/usr/bin/env python3
"""
UT_Upland_Gamebird_scrape.py — HuntIntel Utah Upland Game Bird Scraper
Fetches the Utah Division of Wildlife Resources upland game page
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python UT_Upland_Gamebird_scrape.py
    python UT_Upland_Gamebird_scrape.py --output my_output.json
    python UT_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL       = "https://wildlife.utah.gov/uplandgame"
GUIDEBOOK_URL    = "https://wildlife.utah.gov/guidebooks/waterfowl-upland-game-turkey-guidebook.pdf"
GUIDEBOOK_LABEL  = "2026 Utah Waterfowl, Upland Game and Turkey Guidebook"
FEE_URL          = "https://wildlife.utah.gov/fees"
LICENSE_URL      = "https://wildlife.utah.gov/licenses"
PURCHASE_URL     = "https://wildlifelicense.utah.gov/hflo"
DRAW_URL         = "https://utahdraws.com"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Utah DWR — License & Permit Portal",
        "url":   "https://wildlifelicense.utah.gov/hflo"
    },
    {
        "label": "Utah DWR — Drawing Applications",
        "url":   "https://utahdraws.com"
    }
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; HuntIntel-Scraper/1.0; "
        "+https://huntintel.io)"
    )
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def fetch_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_cost(raw: str):
    raw = clean(raw)
    if not raw or raw in ("—", "–", "-", "N/A", "n/a"):
        return None
    return raw


def strip_asterisk(text: str) -> tuple[str, bool]:
    has = text.rstrip().endswith("*")
    return text.rstrip("* ").strip(), has


# ── Scraper ────────────────────────────────────────────────────────────────────

def scrape_source_meta(soup: BeautifulSoup) -> dict:
    return {
        "page_url":     SOURCE_URL,
        "page_label":   "Hunting Upland Game and Turkey | Utah DWR",
        "last_updated": None,
        "update_note": (
            "2026-27 season data compiled from the Utah DWR Upland Game page "
            "(last updated June 26, 2026) and the 2025-26 Utah Upland Game and "
            "Turkey Guidebook. Where 2026-27 dates were unavailable, 2025-26 "
            "dates from the guidebook and Project Upland reference were used."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2025-26 / 2026-27 season data for Utah Upland Game Birds.
    Sources: Utah DWR Upland Game page, Utah Waterfowl/Upland Game/Turkey
    Guidebook (2026.0, published June 2026), Project Upland reference.

    Utah's upland game birds:
      - Dusky (Blue) Grouse
      - Ruffed Grouse
      - Sharp-tailed Grouse (permit required)
      - Greater Sage Grouse (permit required)
      - White-tailed Ptarmigan (free permit required)
      - Gambel's Quail
      - California (Valley) Quail
      - Chukar Partridge
      - Gray (Hungarian) Partridge
      - Ring-necked Pheasant (roosters only)
    """
    return [
        {
            "name":             "Dusky (Blue) Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "September 1 - December 31, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "4 daily (combined with ruffed grouse)",
            "possession_limit": "12 (combined with ruffed grouse)",
        },
        {
            "name":             "Ruffed Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "September 1 - December 31, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "4 daily (combined with dusky grouse)",
            "possession_limit": "12 (combined with dusky grouse)",
        },
        {
            "name":             "Sharp-tailed Grouse",
            "asterisk":         True,
            "season_start":     "September 27, 2026",
            "season_end":       "October 19, 2026",
            "season_raw":       "September 27 - October 19, 2026",
            "hunting_units":    "Box Elder and Cache counties only",
            "bag_limit":        "2 per season (permit required)",
            "possession_limit": "2 per season",
        },
        {
            "name":             "Greater Sage Grouse",
            "asterisk":         True,
            "season_start":     "September 27, 2026",
            "season_end":       "October 19, 2026",
            "season_raw":       "September 27 - October 19, 2026",
            "hunting_units":    "Diamond/Blue Mountain, Parker Mountain, Rich County, West Box Elder areas",
            "bag_limit":        "2 per season (permit required)",
            "possession_limit": "2 per season",
        },
        {
            "name":             "White-tailed Ptarmigan",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "October 31, 2026",
            "season_raw":       "September 1 - October 31, 2026",
            "hunting_units":    "Uinta Mountains",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Gambel's Quail",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "November 1 - December 31, 2026",
            "hunting_units":    "Southwestern Utah (Washington County)",
            "bag_limit":        "5 daily (combined with California quail)",
            "possession_limit": "15 (combined with California quail)",
        },
        {
            "name":             "California (Valley) Quail",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "November 1 - December 31, 2026",
            "hunting_units":    "Statewide (except Washington County for Gambel's range)",
            "bag_limit":        "5 daily (combined with Gambel's quail)",
            "possession_limit": "15 (combined with Gambel's quail)",
        },
        {
            "name":             "Chukar Partridge",
            "asterisk":         True,
            "season_start":     "September 27, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "September 27, 2026 - February 15, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        {
            "name":             "Gray (Hungarian) Partridge",
            "asterisk":         False,
            "season_start":     "September 27, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "September 27, 2026 - February 15, 2027",
            "hunting_units":    "Box Elder and Cache counties primarily",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "November 1, 2026",
            "season_end":       "December 7, 2026",
            "season_raw":       "November 1 - December 7, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 male (rooster) pheasants daily",
            "possession_limit": "6",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the Utah DWR Fees page.
    A valid hunting license is required for all hunters.
    Some species require additional permits (sage grouse, sharp-tailed grouse, ptarmigan).
    """
    return [
        {
            "name":             "Basic Hunting License (Resident, age 18-64)",
            "asterisk":         True,
            "covers":           "Required for all resident hunters; 365-day license",
            "resident_cost":    "$40.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Basic Hunting License (Nonresident, age 18+)",
            "asterisk":         True,
            "covers":           "Required for all nonresident hunters; 365-day license",
            "resident_cost":    None,
            "nonresident_cost": "$144.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 3-Day Small Game License",
            "asterisk":         False,
            "covers":           "Small game and upland game birds for 3 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$89.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Hunting License (Resident, age 14-17)",
            "asterisk":         False,
            "covers":           "Basic hunting license for youth; 365-day",
            "resident_cost":    "$16.00",
            "nonresident_cost": "$44.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Senior Hunting License (Resident, age 65+)",
            "asterisk":         False,
            "covers":           "Basic hunting license for seniors; 365-day",
            "resident_cost":    "$31.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Sage Grouse / Sharp-tailed Grouse Permit",
            "asterisk":         True,
            "covers":           "Required to hunt sage grouse or sharp-tailed grouse",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$16.00 (before Sept 1) / $21.00 (after Sept 1)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "White-tailed Ptarmigan / Band-tailed Pigeon Permit",
            "asterisk":         True,
            "covers":           "Free permit required to hunt ptarmigan or band-tailed pigeon",
            "resident_cost":    "Free",
            "nonresident_cost": "$16.00 (before Sept 1) / $21.00 (after Sept 1)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A valid hunting license is required for all hunters. "
                "Credit/debit card transactions incur a 2.2% fee."
            ),
            "applies_to": [
                "Basic Hunting License (Resident, age 18-64)",
                "Basic Hunting License (Nonresident, age 18+)"
            ],
            "sources": [
                {
                    "url":      FEE_URL,
                    "label":    "Utah DWR — Fees Page",
                    "evidence": (
                        "A 2.2% transaction fee applies for all online and "
                        "in-person credit/debit card transactions."
                    )
                }
            ]
        },
        {
            "title": (
                "Sage grouse and sharp-tailed grouse require a $10 permit "
                "(resident) in addition to a hunting license. Seasons are "
                "limited to approximately 3 weeks in fall."
            ),
            "applies_to": ["Greater Sage Grouse", "Sharp-tailed Grouse"],
            "sources": [
                {
                    "url":      "https://projectupland.com/rules-regulations-and-seasons/bird-hunting-opportunities-in-utah/",
                    "label":    "Project Upland — Utah Bird Hunting Guide",
                    "evidence": (
                        "Sharp-tailed Grouse: Permit required ($10). "
                        "Sage Grouse: Permit required ($10). "
                        "Both: 2 birds per season, Sept 27 - Oct 19."
                    )
                }
            ]
        },
        {
            "title": (
                "White-tailed ptarmigan requires a free permit in addition "
                "to a hunting license. Found only in the Uinta Mountains."
            ),
            "applies_to": ["White-tailed Ptarmigan"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Ptarmigan Information",
                    "evidence": (
                        "White-tailed Ptarmigan: Free permit required. "
                        "Season Sept 1 - Oct 31. Uinta Mountains only."
                    )
                }
            ]
        },
        {
            "title": (
                "Scaled (blue) quail are closed to hunting in Utah. "
                "Hunters must be able to distinguish them from Gambel's "
                "and California quail."
            ),
            "applies_to": ["Gambel's Quail", "California (Valley) Quail"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Upland Game Page",
                    "evidence": (
                        "Scaled (Blue) Quail: Closed statewide. "
                        "Hunters must be able to identify them."
                    )
                }
            ]
        },
        {
            "title": (
                "Only rooster (male) pheasants may be taken. "
                "Youth pheasant days run before the regular season."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      "https://projectupland.com/rules-regulations-and-seasons/bird-hunting-opportunities-in-utah/",
                    "label":    "Project Upland — Utah Bird Hunting Guide",
                    "evidence": (
                        "Ring-necked Pheasant: 2/6 (roosters only). "
                        "Youth Pheasant Days: Oct 25-30."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth quail and partridge days run in late October "
                "before the regular November 1 opener."
            ),
            "applies_to": [
                "Chukar Partridge",
                "Gray (Hungarian) Partridge",
                "Gambel's Quail",
                "California (Valley) Quail"
            ],
            "sources": [
                {
                    "url":      "https://projectupland.com/rules-regulations-and-seasons/bird-hunting-opportunities-in-utah/",
                    "label":    "Project Upland — Utah Bird Hunting Guide",
                    "evidence": (
                        "Youth Quail Days: Oct 25-27. "
                        "Youth Chukar/Hun: Sept 20-22."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[UT_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[UT_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[UT_scrape] Using hardcoded data from Utah DWR guidebook.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Utah",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Hunting Upland Game and Turkey | Utah DWR",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Utah DWR guidebook and Project Upland reference."
            ),
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "species":   build_species(),
        "licenses":  build_licenses(),
        "key_notes": build_key_notes(),
    }
    return dataset


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Utah DWR upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/UT_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/UT_Upland_Gamebird_dataset.json)"
    )
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        help="Pretty-print the JSON output"
    )
    args = parser.parse_args()

    dataset = build_dataset()

    indent = 2 if args.pretty else None
    output_str = json.dumps(dataset, ensure_ascii=False, indent=indent)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output_str)

    print(f"[UT_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
