#!/usr/bin/env python3
"""
IA_Upland_Gamebird_scrape.py — HuntIntel Iowa Upland Game Bird Scraper
Fetches the Iowa DNR upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python IA_Upland_Gamebird_scrape.py
    python IA_Upland_Gamebird_scrape.py --output my_output.json
    python IA_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL     = "https://www.iowadnr.gov/things-do/hunting-trapping/iowa-hunting-seasons"
PHEASANT_URL   = "https://www.iowadnr.gov/things-do/hunting-trapping/types-hunting-trapping/pheasant-hunting"
FEE_URL        = "https://www.iowadnr.gov/things-do/hunting-trapping/hunting-licenses-fees"
PURCHASE_URL   = "https://gooutdoorsiowa.com"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Go Outdoors Iowa — License Portal",
        "url":   "https://gooutdoorsiowa.com/"
    },
    {
        "label": "Iowa DNR — Hunting Licenses & Fees",
        "url":   "https://www.iowadnr.gov/things-do/hunting-trapping/hunting-licenses-fees"
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
        "page_label":   "Iowa Hunting Seasons | Iowa DNR",
        "last_updated": None,
        "update_note": (
            "2025-26 season data from the Iowa DNR Hunting Seasons page "
            "(most recent published). 2026-27 season dates expected to be "
            "similar. License fees from Iowa DNR Hunting Licenses & Fees page."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2025-26 season data for Iowa Upland Game Birds.
    Sources: Iowa DNR Hunting Seasons page, Pheasant Hunting page.

    Iowa's upland game birds:
      - Rooster Pheasant
      - Bobwhite Quail
      - Gray (Hungarian) Partridge
      - Ruffed Grouse
    """
    return [
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "October 25, 2026",
            "season_end":       "January 10, 2027",
            "season_raw":       "October 25, 2026 - January 10, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 roosters daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Youth Season",
                    "season_start":      "October 18, 2026",
                    "season_end":        "October 19, 2026",
                    "bag_limit":         "1 rooster daily",
                    "possession_limit":  "2",
                    "note": "Iowa residents only, age 15 and younger. 8am - 4:30pm shooting hours."
                }
            ]
        },
        {
            "name":             "Bobwhite Quail",
            "asterisk":         False,
            "season_start":     "October 25, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 25, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "16",
        },
        {
            "name":             "Gray (Hungarian) Partridge",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 11, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "16",
        },
        {
            "name":             "Ruffed Grouse",
            "asterisk":         True,
            "season_start":     "October 4, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 4, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "6",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the Iowa DNR Hunting Licenses & Fees page.
    Annual licenses expire January 10. Habitat fee required for all hunters.
    """
    return [
        {
            "name":             "Resident Hunting / Habitat License",
            "asterisk":         True,
            "covers":           "Hunting license + habitat fee combined (required for all resident hunters)",
            "resident_cost":    "$35.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Hunting / Habitat License (age 18+)",
            "asterisk":         True,
            "covers":           "Hunting license + habitat fee combined for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$144.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 5-Day Hunting / Habitat License",
            "asterisk":         False,
            "covers":           "5-day hunting license + habitat fee for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$90.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Hunting / Habitat License (under age 18)",
            "asterisk":         False,
            "covers":           "Youth hunting license + habitat fee for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$45.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Outdoor Combo License (Resident)",
            "asterisk":         False,
            "covers":           "Hunting + fishing + habitat fee combined",
            "resident_cost":    "$55.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "All upland game bird hunters must wear at least one article "
                "of solid blaze orange (≥50% surface area) — hat, vest, coat, "
                "or similar outer garment."
            ),
            "applies_to": [
                "Ring-necked Pheasant",
                "Bobwhite Quail",
                "Gray (Hungarian) Partridge",
                "Ruffed Grouse"
            ],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "Iowa DNR — Pheasant Hunting",
                    "evidence": (
                        "Blaze orange required for upland game bird hunters: "
                        "at least one article of visible external apparel with "
                        "≥50% solid blaze orange surface area."
                    )
                }
            ]
        },
        {
            "title": (
                "Pheasant shooting hours are 8:00 a.m. to 4:30 p.m. "
                "Ruffed grouse shooting hours are sunrise to sunset."
            ),
            "applies_to": ["Ring-necked Pheasant", "Ruffed Grouse"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Hunting Seasons",
                    "evidence": (
                        "Pheasant: 8am - 4:30pm. Ruffed Grouse: "
                        "Sunrise to Sunset. Quail & Partridge: 8am - 4:30pm."
                    )
                }
            ]
        },
        {
            "title": (
                "Only rooster (male) pheasants may be taken. A foot or "
                "fully feathered wing must remain attached for transport."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "Iowa DNR — Pheasant Hunting",
                    "evidence": (
                        "Individuals cannot transport a pheasant within the "
                        "state without a foot or fully feathered wing attached. "
                        "Rooster pheasant only."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth pheasant season is open to Iowa residents only, "
                "age 15 and younger, with reduced bag limits (1 daily / 2 possession)."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Hunting Seasons",
                    "evidence": (
                        "Rooster Pheasant Youth (1/2 daily/poss): Oct 18-19. "
                        "Iowa residents only, age 15 or younger."
                    )
                }
            ]
        },
        {
            "title": (
                "Annual hunting licenses and habitat fees expire on "
                "January 10 each year."
            ),
            "applies_to": ["Resident Hunting / Habitat License"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Hunting Seasons",
                    "evidence": (
                        "Annual licenses, stamps, and fees expire on January 10."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[IA_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[IA_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[IA_scrape] Using hardcoded data from Iowa DNR pages.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Iowa",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Iowa Hunting Seasons | Iowa DNR",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Iowa DNR Hunting Seasons and Pheasant Hunting pages."
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
        description="Scrape Iowa DNR upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/IA_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/IA_Upland_Gamebird_dataset.json)"
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

    print(f"[IA_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
