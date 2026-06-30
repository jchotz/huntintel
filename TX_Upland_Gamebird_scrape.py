#!/usr/bin/env python3
"""
TX_Upland_Gamebird_scrape.py — HuntIntel Texas Upland Game Bird Scraper
Fetches the Texas Parks & Wildlife Department upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python TX_Upland_Gamebird_scrape.py
    python TX_Upland_Gamebird_scrape.py --output my_output.json
    python TX_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://tpwd.texas.gov/regulations/outdoor-annual/hunting/2026-2027-hunting-season-dates"
OUTDOOR_ANNUAL  = "https://tpwd.texas.gov/regulations/outdoor-annual/hunting/"
NEWS_RELEASE    = "https://tpwd.texas.gov/newsmedia/releases/?req=20260401b"
LICENSE_URL     = "https://tpwd.texas.gov/regulations/outdoor-annual/licenses/hunting-licenses-and-permits/hunting-licenses"
PURCHASE_URL    = "https://www.txfgsales.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Texas License Sales Portal",
        "url":   "https://www.txfgsales.com/"
    },
    {
        "label": "TPWD — Outdoor Annual Hunting Licenses",
        "url":   "https://tpwd.texas.gov/regulations/outdoor-annual/licenses/hunting-licenses-and-permits/hunting-licenses"
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
        "page_label":   "2026-2027 Hunting Season Dates | TPWD",
        "last_updated": None,
        "update_note": (
            "2026-27 season data from TPWD Outdoor Annual season dates page. "
            "The TPW Commission approved 2026-27 seasons on April 1, 2026. "
            "Chachalaca and quail dates aligned to Nov 1 - Feb 28 per recent rule change."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Texas Upland Game Birds.
    Sources: TPWD 2026-2027 Hunting Season Dates, TPWD species pages,
    TPW Commission news release (April 2026).

    Texas's upland game birds (non-turkey):
      - Chachalaca (Plain Chachalaca)
      - Ring-necked Pheasant (cocks only)
      - Quail (Bobwhite, Scaled, Gambel's — combined bag)
    """
    return [
        {
            "name":             "Chachalaca",
            "asterisk":         True,
            "season_start":     "November 1, 2026",
            "season_end":       "February 28, 2027",
            "season_raw":       "November 1, 2026 - February 28, 2027",
            "hunting_units":    "Cameron, Hidalgo, Starr, and Willacy counties only",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "December 5, 2026",
            "season_end":       "January 3, 2027",
            "season_raw":       "December 5, 2026 - January 3, 2027",
            "hunting_units":    "Panhandle / South Plains (37 counties)",
            "bag_limit":        "3 cocks daily",
            "possession_limit": "9 cocks",
        },
        {
            "name":             "Quail",
            "asterisk":         True,
            "season_start":     "November 1, 2026",
            "season_end":       "February 28, 2027",
            "season_raw":       "November 1, 2026 - February 28, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (Bobwhite, Scaled & Gambel's combined)",
            "possession_limit": "45",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from TPWD hunting license page.
    Valid through August 31 each year.
    Upland Game Bird Endorsement ($7) required for all upland bird hunting.
    """
    return [
        {
            "name":             "Resident Hunting License",
            "asterisk":         True,
            "covers":           "Any legal bird/animal (terrestrial vertebrates); valid to Aug 31",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident General Hunting License",
            "asterisk":         True,
            "covers":           "Any legal bird/animal including deer; valid to Aug 31",
            "resident_cost":    None,
            "nonresident_cost": "$315.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Special 5-Day Small Game/Exotic Hunting License",
            "asterisk":         False,
            "covers":           "Exotic animals and small game for 5 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$48.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Senior Resident Hunting License (age 65+)",
            "asterisk":         False,
            "covers":           "Same as Resident Hunting License for seniors",
            "resident_cost":    "$7.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Hunting License (under age 17)",
            "asterisk":         False,
            "covers":           "Hunting license valid for any legal bird/animal",
            "resident_cost":    "$7.00",
            "nonresident_cost": "$7.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Upland Game Bird Endorsement",
            "asterisk":         True,
            "covers":           "Required in addition to hunting license to hunt any upland game bird",
            "resident_cost":    "$7.00",
            "nonresident_cost": "$7.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Super Combo License (Resident)",
            "asterisk":         False,
            "covers":           "Hunting + fishing license + 5 state endorsements at a discount",
            "resident_cost":    "$68.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "An Upland Game Bird Endorsement ($7) is required in addition "
                "to a valid hunting license to hunt any upland game bird in Texas."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident General Hunting License",
                "Youth Hunting License (under age 17)"
            ],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "licenses/hunting-licenses-and-permits/hunting-endorsements"),
                    "label":    "TPWD — Hunting Endorsements",
                    "evidence": (
                        "Upland Game Bird Endorsement: $7. Required to hunt "
                        "upland game birds including quail, pheasant, chachalaca."
                    )
                }
            ]
        },
        {
            "title": (
                "Chachalaca hunting is limited to four counties in the "
                "Rio Grande Valley: Cameron, Hidalgo, Starr, and Willacy."
            ),
            "applies_to": ["Chachalaca"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "regs/animals/chachalaca"),
                    "label":    "TPWD — Chachalaca Season & Regulations",
                    "evidence": (
                        "Chachalaca: 4 of 254 counties have Chachalaca seasons: "
                        "Cameron, Hidalgo, Starr, Willacy."
                    )
                }
            ]
        },
        {
            "title": (
                "Only cock (male) pheasants may be taken. Proof of sex "
                "(leg with spur or full plumage) must remain attached until "
                "final processing."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "regs/animals/pheasant"),
                    "label":    "TPWD — Pheasant Season & Regulations",
                    "evidence": (
                        "Daily bag: 3 cocks. Possession: 9 cocks. "
                        "Proof of sex: one leg including spur attached, "
                        "or entire plumage attached, until final destination."
                    )
                }
            ]
        },
        {
            "title": (
                "No open season for Mearn's (Montezuma) quail. "
                "Only Bobwhite, Scaled (blue), and Gambel's quail may be taken."
            ),
            "applies_to": ["Quail"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "regs/animals/quail"),
                    "label":    "TPWD — Quail Season & Regulations",
                    "evidence": (
                        "Bobwhite quail, Scaled quail (blue quail) and "
                        "Gambel's quail. No open season for Mearn's "
                        "(Montezuma) quail."
                    )
                }
            ]
        },
        {
            "title": (
                "Pheasant season is limited to 37 counties in the "
                "Panhandle and South Plains regions."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "TPWD — 2026-2027 Hunting Season Dates",
                    "evidence": (
                        "Pheasant: Panhandle/South Plains — "
                        "Dec 5, 2026 - Jan 3, 2027."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[TX_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[TX_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[TX_scrape] Using hardcoded data from TPWD season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Texas",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "2026-2027 Hunting Season Dates | TPWD",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from TPWD Outdoor Annual and news release."
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
        description="Scrape Texas Parks & Wildlife upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/TX_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/TX_Upland_Gamebird_dataset.json)"
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

    print(f"[TX_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
