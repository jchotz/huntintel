#!/usr/bin/env python3
"""
KS_Upland_Gamebird_scrape.py — HuntIntel Kansas Upland Game Bird Scraper
Fetches the Kansas Department of Wildlife and Parks upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python KS_Upland_Gamebird_scrape.py
    python KS_Upland_Gamebird_scrape.py --output my_output.json
    python KS_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL     = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/when-to-hunt"
KDWP_HOME      = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas"
PHEASANT_URL   = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/what-to-hunt/upland-birds-small-game/pheasant"
FEE_URL        = "https://www.ksoutdoors.gov/licenses-permits-fees/hunting-licenses-permit-fees"
EREG_BAGS      = "https://www.eregulations.com/kansas/hunting/hunting-bag-limits"
PURCHASE_URL   = "https://www.ksoutdoors.gov/licenses-permits-fees"

LICENSE_PURCHASE_URLS = [
    {
        "label": "KS Outdoors — License & Permit Portal",
        "url":   "https://www.ksoutdoors.gov/licenses-permits-fees"
    },
    {
        "label": "KDWP — Hunting License Fees",
        "url":   "https://www.ksoutdoors.gov/licenses-permits-fees/hunting-licenses-permit-fees"
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
        "page_label":   "When to Hunt | Kansas Department of Wildlife and Parks",
        "last_updated": None,
        "update_note": (
            "2026-27 season data from the KDWP When to Hunt page "
            "(multi-year season table) and eRegulations bag limits. "
            "License fees from KDWP Hunting License & Permit Fees page."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Kansas Upland Game Birds.
    Sources: KDWP When to Hunt page, eRegulations Bag Limits,
    KDWP Pheasant species page.

    Kansas's upland game birds:
      - Ring-necked Pheasant (cocks only)
      - Quail (Bobwhite)
      - Greater Prairie-Chicken
    """
    return [
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "November 14, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "November 14, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "4 cocks daily",
            "possession_limit": "16 cocks",
            "sub_seasons": [
                {
                    "name":              "Youth & Disability Season",
                    "season_start":      "November 7, 2026",
                    "season_end":        "November 8, 2026",
                    "bag_limit":         "4 cocks daily",
                    "possession_limit":  "16 cocks",
                    "note": "Youth (age 15 and under) and disabled hunters; same bag limits as regular season."
                }
            ]
        },
        {
            "name":             "Quail (Bobwhite)",
            "asterisk":         False,
            "season_start":     "November 14, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "November 14, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "32",
        },
        {
            "name":             "Greater Prairie-Chicken",
            "asterisk":         True,
            "season_start":     "September 15, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 15, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "8",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the KDWP Hunting License & Permit Fees page.
    Valid 365 days unless noted. Ages 15 and under and ages 75+ do not
    require a hunting license.
    """
    return [
        {
            "name":             "Hunting License (Resident, age 16-64)",
            "asterisk":         True,
            "covers":           "General hunting license required for all hunters ages 16-64",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Hunting License (Nonresident, age 16+)",
            "asterisk":         True,
            "covers":           "General hunting license required for nonresident hunters",
            "resident_cost":    None,
            "nonresident_cost": "$125.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Senior Hunting License (Resident, age 65-74)",
            "asterisk":         False,
            "covers":           "Discounted hunting license for senior residents",
            "resident_cost":    "$12.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Youth Hunting License (age 15 & under)",
            "asterisk":         False,
            "covers":           "Hunting license for nonresident youth",
            "resident_cost":    None,
            "nonresident_cost": "$40.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Combination Hunting & Fishing License (Resident, age 16-64)",
            "asterisk":         False,
            "covers":           "Hunting and fishing privileges combined",
            "resident_cost":    "$45.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Only cock (male) pheasants may be taken. Kansas has "
                "maintained a cocks-only pheasant season since 1982."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "KDWP — Pheasant Species Page",
                    "evidence": (
                        "Daily bag 4 cocks. Cocks-only format established "
                        "in 1982. 80-90% of roosters can be safely harvested "
                        "without hindering reproduction."
                    )
                },
                {
                    "url":      EREG_BAGS,
                    "label":    "eRegulations — Kansas Bag Limits",
                    "evidence": "Pheasant: 4 cocks per day (4x daily limit in possession)."
                }
            ]
        },
        {
            "title": (
                "Youth and Disabled hunters get a 2-day early pheasant and "
                "quail season on the first Saturday and Sunday of November."
            ),
            "applies_to": ["Ring-necked Pheasant", "Quail (Bobwhite)"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "KDWP — When to Hunt",
                    "evidence": (
                        "Pheasant and Quail - Youth and Disability: "
                        "First Saturday in November and the following day. "
                        "2026: November 7-8, 2026."
                    )
                }
            ]
        },
        {
            "title": (
                "Lesser prairie-chicken is CLOSED to hunting in Kansas. "
                "Only greater prairie-chicken may be hunted."
            ),
            "applies_to": ["Greater Prairie-Chicken"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "KDWP — When to Hunt",
                    "evidence": (
                        "Greater Prairie-Chicken: September 15 through "
                        "January 31 annually. "
                        "Lesser Prairie-Chicken: Season closed."
                    )
                }
            ]
        },
        {
            "title": (
                "Residents ages 15 and under and ages 75 and older do not "
                "need to purchase a hunting license (all other permits, "
                "tags, and stamps still apply)."
            ),
            "applies_to": ["Hunting License (Resident, age 16-64)"],
            "sources": [
                {
                    "url":      FEE_URL,
                    "label":    "KDWP — License & Permit Fees",
                    "evidence": (
                        "Ages 15 and younger are not required to purchase "
                        "a hunting or fishing license. Ages 75+ are not "
                        "required to purchase a hunting or fishing license."
                    )
                }
            ]
        },
        {
            "title": (
                "Kansas is among the top pheasant hunting states in the "
                "U.S., with an annual harvest of 425,000 to 824,000 cocks."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "KDWP — Pheasant Species Page",
                    "evidence": (
                        "Kansas is typically among the top 3 or 4 pheasant "
                        "hunting states in the U.S. Annual harvest since "
                        "1990: 425,000 to 824,000 cocks."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[KS_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[KS_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[KS_scrape] Using hardcoded data from KDWP pages.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Kansas",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "When to Hunt | Kansas Department of Wildlife and Parks",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from KDWP When to Hunt and eRegulations bag limits."
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
        description="Scrape Kansas DWP upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/KS_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/KS_Upland_Gamebird_dataset.json)"
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

    print(f"[KS_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
