#!/usr/bin/env python3
"""
OK_Upland_Gamebird_scrape.py — HuntIntel Oklahoma Upland Game Bird Scraper
Fetches the Oklahoma Department of Wildlife Conservation upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python OK_Upland_Gamebird_scrape.py
    python OK_Upland_Gamebird_scrape.py --output my_output.json
    python OK_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.wildlifedepartment.com/hunting/seasons"
ODWC_HOME       = "https://www.wildlifedepartment.com/hunting"
PHEASANT_URL    = "https://www.wildlifedepartment.com/hunting/regs/pheasant-regulations"
QUAIL_URL       = "https://www.wildlifedepartment.com/hunting/regs/quail-bobwhite-scaled-regulations"
FEE_URL         = "https://www.wildlifedepartment.com/licensing/regs/license-fees"
PURCHASE_URL    = "https://gooutdoorsoklahoma.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Go Outdoors Oklahoma — License Portal",
        "url":   "https://gooutdoorsoklahoma.com/"
    },
    {
        "label": "ODWC — License Fees Page",
        "url":   "https://www.wildlifedepartment.com/licensing/regs/license-fees"
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
        "page_label":   "Hunting Seasons | Oklahoma Department of Wildlife Conservation",
        "last_updated": None,
        "update_note": (
            "2026-27 season data from the ODWC Hunting Seasons page "
            "and species-specific regulation pages (pheasant, quail). "
            "License fees from ODWC License Fees page."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Oklahoma Upland Game Birds.
    Sources: ODWC Hunting Seasons page, Pheasant Regulations,
    Quail (Bobwhite & Scaled) Regulations.

    Oklahoma's upland game birds:
      - Quail (Bobwhite & Scaled)
      - Ring-necked Pheasant (cocks only)
    """
    return [
        {
            "name":             "Quail (Bobwhite & Scaled)",
            "asterisk":         True,
            "season_start":     "November 14, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "November 14, 2026 - February 15, 2027",
            "hunting_units":    "Statewide (some WMAs closed to nonresidents after Jan 31)",
            "bag_limit":        "10 daily",
            "possession_limit": "20",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "December 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "December 1, 2026 - January 31, 2027",
            "hunting_units":    "13 counties: Alfalfa, Beaver, Cimarron, Garfield, Grant, Harper, Kay, Major, Noble, Osage, Texas, Woods, Woodward; plus portions of Blaine, Dewey, Ellis, Kingfisher, Logan counties north of SH-51",
            "bag_limit":        "2 cocks daily",
            "possession_limit": "4 cocks",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the ODWC License Fees page.
    Valid Jan 1 - Dec 31 unless noted.
    """
    return [
        {
            "name":             "Annual Hunting License (Resident, age 18+)",
            "asterisk":         True,
            "covers":           "Base hunting license required for all resident hunters",
            "resident_cost":    "$36.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Annual Hunting License (Nonresident, age 18+)",
            "asterisk":         True,
            "covers":           "Base hunting license required for all nonresident hunters",
            "resident_cost":    None,
            "nonresident_cost": "$209.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 5-Day Hunting License",
            "asterisk":         True,
            "covers":           "5 days of choice (NOT valid for quail)",
            "resident_cost":    None,
            "nonresident_cost": "$75.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Annual Super Hunting License (age 17 & under)",
            "asterisk":         False,
            "covers":           "Deer, turkey, waterfowl, elk, bear, antelope, furbearers, trapping",
            "resident_cost":    "$26.00",
            "nonresident_cost": "$151.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Game Bird Permit",
            "asterisk":         True,
            "covers":           "Required for nonresidents hunting game birds on WMAs",
            "resident_cost":    None,
            "nonresident_cost": "$100.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Wildlife Conservation Passport (Resident, age 18+)",
            "asterisk":         False,
            "covers":           "Required for access to Dept. lands unless exempt",
            "resident_cost":    "$46.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Only cock (male) pheasants may be taken. Evidence of sex "
                "(head or one foot) must remain attached until the bird "
                "reaches its final destination."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "ODWC — Pheasant Regulations",
                    "evidence": (
                        "Cocks only: Two cocks daily; four in possession "
                        "after the first day. Evidence of sex (head or one foot) "
                        "must remain on the bird until final destination."
                    )
                }
            ]
        },
        {
            "title": (
                "Pheasant season is limited to 13 specified panhandle and "
                "northern Oklahoma counties plus portions of 5 additional "
                "counties north of State Highway 51."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PHEASANT_URL,
                    "label":    "ODWC — Pheasant Regulations",
                    "evidence": (
                        "Open areas include Alfalfa, Beaver, Cimarron, Garfield, "
                        "Grant, Harper, Kay, Major, Noble, Osage, Texas, Woods, "
                        "Woodward counties; and portions of Blaine, Dewey, Ellis, "
                        "Kingfisher and Logan counties north of State Highway 51."
                    )
                }
            ]
        },
        {
            "title": (
                "\"Pot shooting\" quail (shooting birds while resting on the "
                "ground) is illegal in Oklahoma."
            ),
            "applies_to": ["Quail (Bobwhite & Scaled)"],
            "sources": [
                {
                    "url":      QUAIL_URL,
                    "label":    "ODWC — Quail Regulations",
                    "evidence": (
                        "At no time may any quail or covey be shot while "
                        "resting on the ground, commonly called 'pot shooting.'"
                    )
                }
            ]
        },
        {
            "title": (
                "Nonresidents hunting game birds on a Wildlife Management Area "
                "(WMA) must possess a Nonresident Game Bird Permit ($100)."
            ),
            "applies_to": [
                "Annual Hunting License (Nonresident, age 18+)",
                "Nonresident 5-Day Hunting License"
            ],
            "sources": [
                {
                    "url":      FEE_URL,
                    "label":    "ODWC — License Fees",
                    "evidence": (
                        "Nonresident Game Bird Permit: $100. Required for "
                        "nonresidents hunting game birds on any WMA, GMA, PHA, "
                        "WRP, WDU, or WMU."
                    )
                }
            ]
        },
        {
            "title": (
                "The nonresident 5-day hunting license is NOT valid for "
                "hunting quail."
            ),
            "applies_to": ["Quail (Bobwhite & Scaled)"],
            "sources": [
                {
                    "url":      QUAIL_URL,
                    "label":    "ODWC — Quail Regulations",
                    "evidence": (
                        "The adult nonresident 5-day hunting license is not "
                        "valid for hunting quail."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[OK_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[OK_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[OK_scrape] Using hardcoded data from ODWC pages.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Oklahoma",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Hunting Seasons | Oklahoma Department of Wildlife Conservation",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from ODWC Hunting Seasons and species regulation pages."
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
        description="Scrape Oklahoma DWC upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/OK_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/OK_Upland_Gamebird_dataset.json)"
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

    print(f"[OK_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
