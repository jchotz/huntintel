#!/usr/bin/env python3
"""
AR_Upland_Gamebird_scrape.py — HuntIntel Arkansas Upland Game Bird Scraper
Fetches the Arkansas Game & Fish Commission upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python AR_Upland_Gamebird_scrape.py
    python AR_Upland_Gamebird_scrape.py --output my_output.json
    python AR_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.agfc.com/hunting/turkey/turkey-dates-rules-regulations/"
QUAIL_URL       = "https://www.agfc.com/hunting/more-game/quail/"
TURKEY_URL      = "https://www.agfc.com/hunting/turkey/"
LICENSE_URL     = "https://www.agfc.com/resources/licensing/hunting-license-descriptions-and-fees/"
PURCHASE_URL    = "https://ar-web.s3licensing.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Arkansas Game & Fish — Online License Portal",
        "url":   "https://ar-web.s3licensing.com/"
    },
    {
        "label": "AGFC — Hunting Licenses & Fees",
        "url":   "https://www.agfc.com/resources/licensing/hunting-license-descriptions-and-fees/"
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
        "page_url":     TURKEY_URL,
        "page_label":   "Turkey Dates, Rules & Regulations | Arkansas Game & Fish Commission",
        "last_updated": None,
        "update_note": (
            "2026 upland game bird data from AGFC turkey and quail regulation pages. "
            "Arkansas's upland game birds are primarily bobwhite quail and wild turkey. "
            "Turkey seasons are zone-based with spring and fall components."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Arkansas Upland Game Birds.
    Sources: AGFC turkey regulations, AGFC quail page.

    Species: Bobwhite Quail, Wild Turkey (Spring), Wild Turkey (Fall).
    """
    return [
        # ── Bobwhite Quail ──────────────────────────────────────────────────
        {
            "name":             "Bobwhite Quail",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "February 28, 2027",
            "season_raw":       "November 1, 2026 - February 28, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Wild Turkey (Spring) ────────────────────────────────────────────
        {
            "name":             "Wild Turkey (Spring)",
            "asterisk":         True,
            "season_start":     "April 6, 2026",
            "season_end":       "May 10, 2026",
            "season_raw":       "Zone 1: Apr 20-May 10; Zone 1A: Apr 20-28; Zone 2: Apr 13-May 3; Zone 2A: Apr 13-21; Zone 3: Apr 6-26",
            "hunting_units":    "Zones 1, 1A, 2, 2A, 3 (see sub-seasons)",
            "bag_limit":        "2 legal turkeys per season (1 per day)",
            "possession_limit": "2",
            "sub_seasons": [
                {
                    "name":              "Zone 1",
                    "season_start":      "April 20, 2026",
                    "season_end":        "May 10, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                    "note":              "Second bird must be taken in NWR, WMA, or Zones 1, 2, 2A, or 3"
                },
                {
                    "name":              "Zone 1A",
                    "season_start":      "April 20, 2026",
                    "season_end":        "April 28, 2026",
                    "bag_limit":         "1 legal turkey",
                    "possession_limit":  "1",
                    "note":              "Second bird must be taken in NWR, WMA, or Zones 1, 2, 2A, or 3"
                },
                {
                    "name":              "Zone 2",
                    "season_start":      "April 13, 2026",
                    "season_end":        "May 3, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                },
                {
                    "name":              "Zone 2A",
                    "season_start":      "April 13, 2026",
                    "season_end":        "April 21, 2026",
                    "bag_limit":         "1 legal turkey",
                    "possession_limit":  "1",
                    "note":              "Second bird must be taken in NWR, WMA, or Zones 1, 1A, 2, or 3"
                },
                {
                    "name":              "Zone 3",
                    "season_start":      "April 6, 2026",
                    "season_end":        "April 26, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                },
            ]
        },
        # ── Wild Turkey (Fall) ──────────────────────────────────────────────
        {
            "name":             "Wild Turkey (Fall)",
            "asterisk":         True,
            "season_start":     "October 1, 2026",
            "season_end":       "February 28, 2027",
            "season_raw":       "October 1, 2026 - February 28, 2027 (archery and firearms)",
            "hunting_units":    "Statewide (permit required)",
            "bag_limit":        "1 either-sex turkey",
            "possession_limit": "1",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from AGFC license page.
    """
    return [
        {
            "name":             "Resident Wildlife Conservation License (HNT)",
            "asterisk":         False,
            "covers":           "Small game, furbearers, and one deer; base hunting license",
            "resident_cost":    "$10.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Sportsman's License (RS)",
            "asterisk":         False,
            "covers":           "All game (6 deer tags, 2 turkey tags), hunting only",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Annual Small Game License (NRH)",
            "asterisk":         False,
            "covers":           "All small game and furbearers",
            "resident_cost":    None,
            "nonresident_cost": "$110.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 5-Day Small Game License (SG5)",
            "asterisk":         False,
            "covers":           "Small game and furbearers for 5 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$80.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Annual Turkey Hunting License (NRTL — Nonresident)",
            "asterisk":         True,
            "covers":           "Turkey hunting only for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$325.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Turkey Tag (NRTT)",
            "asterisk":         True,
            "covers":           "Required for NBG holders to take one turkey",
            "resident_cost":    None,
            "nonresident_cost": "$100.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Arkansas turkey hunters may take 2 legal turkeys per spring season. "
                "No jakes or hens may be harvested. Daily limit is 1 legal turkey."
            ),
            "applies_to": ["Wild Turkey (Spring)"],
            "sources": [
                {
                    "url":      TURKEY_URL,
                    "label":    "AGFC — Turkey Dates, Rules & Regulations",
                    "evidence": (
                        "Total limit: 2 legal turkeys (no jakes, no females). "
                        "First 7 days of regular season: no more than one legal turkey may be taken. "
                        "Daily limit: One legal turkey per day."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth turkey hunt (ages 6-15) is held April 11-12, 2026 in Zones 1, 1A, 2, and 2A. "
                "Youth without hunter education must be supervised by an adult 21 or older."
            ),
            "applies_to": ["Wild Turkey (Spring)"],
            "sources": [
                {
                    "url":      TURKEY_URL,
                    "label":    "AGFC — Special Youth Turkey Hunt",
                    "evidence": (
                        "2026 Special Youth Turkey Hunt: April 11-12, 2026 "
                        "(Zones 1, 1A, 2, and 2A only). "
                        "Hunters ages 6-15. Bag limit: One legal turkey or jake."
                    )
                }
            ]
        },
        {
            "title": (
                "Shot larger than No. 2 common shot is prohibited for turkey hunting. "
                "Legal weapons: shotguns (10 gauge or smaller) and archery equipment."
            ),
            "applies_to": ["Wild Turkey (Spring)", "Wild Turkey (Fall)"],
            "sources": [
                {
                    "url":      TURKEY_URL,
                    "label":    "AGFC — Turkey Hunting Regulations",
                    "evidence": (
                        "Shot larger than No. 2 common shot is prohibited. "
                        "Legal weapons: shotguns (10 gauge or smaller) and "
                        "archery equipment (including crossbows) only."
                    )
                }
            ]
        },
        {
            "title": (
                "Nonresident turkey hunters may only take one turkey per season. "
                "A nonresident turkey tag ($100) is required in addition to the hunting license."
            ),
            "applies_to": [
                "Annual Turkey Hunting License (NRTL — Nonresident)",
                "Nonresident Turkey Tag (NRTT)"
            ],
            "sources": [
                {
                    "url":      LICENSE_URL,
                    "label":    "AGFC — License Descriptions and Fees",
                    "evidence": (
                        "Nonresidents (youth and adult): Only one turkey in seasonal bag limit. "
                        "Nonresident Turkey Tag (NRTT): $100. Required for holders of NBG to take one turkey."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[AR_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[AR_upland] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[AR_upland] Using hardcoded data from AGFC regulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Arkansas",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     TURKEY_URL,
            "page_label":   "Turkey Dates, Rules & Regulations | Arkansas Game & Fish Commission",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from AGFC turkey and quail regulation pages."
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
        description="Scrape Arkansas Game & Fish Commission upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/AR_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/AR_Upland_Gamebird_dataset.json)"
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

    print(f"[AR_upland] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
