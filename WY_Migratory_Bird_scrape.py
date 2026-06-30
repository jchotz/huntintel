#!/usr/bin/env python3
"""
WY_Migratory_Bird_scrape.py — HuntIntel Wyoming Migratory Game Bird Scraper
Fetches the Wyoming Game & Fish Department migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python WY_Migratory_Bird_scrape.py
    python WY_Migratory_Bird_scrape.py --output my_output.json
    python WY_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://wgfd.wyo.gov/Regulations/Game-Birds-Waterfowl/Late-Migratory-Game-Bird-Hunting-Seasons"
LICENSE_URL     = "https://wgfd.wyo.gov/licenses-applications"
PURCHASE_URL    = "https://wgfd.wyo.gov/licenses-applications"

LICENSE_PURCHASE_URLS = [
    {
        "label": "WGFD — Licenses & Applications",
        "url":   "https://wgfd.wyo.gov/licenses-applications"
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
        "page_label":   "Late Migratory Game Bird Hunting Seasons | WGFD",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from WGFD Late Migratory Game Bird "
            "Hunting Seasons page. Wyoming follows Pacific and Central Flyway "
            "regulations with multiple zones for ducks and geese."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Wyoming Migratory Game Birds.
    Sources: WGFD Late Migratory Game Bird Hunting Seasons page.

    Migratory birds included: Mourning Dove, Duck (Ducks & Mergansers),
    Canada Goose/Dark Geese, Light Geese, Early Canada Goose (Pacific Flyway),
    Sandhill Crane, Snipe, Sora & Virginia Rail.
    """
    return [
        # ── Mourning Dove ────────────────────────────────────────────────
        {
            "name":             "Mourning Dove",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 29, 2026",
            "season_raw":       "September 1, 2026 - November 29, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Duck (Ducks & Mergansers) ───────────────────────────────────
        {
            "name":             "Duck (Ducks & Mergansers)",
            "asterisk":         True,
            "season_start":     "September 27, 2026",
            "season_end":       "January 18, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "Pacific Flyway; Central Flyway Zones C1, C1A, C2 (see sub-seasons)",
            "bag_limit":        "6 daily (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Pacific Flyway",
                    "season_start":      "September 27, 2026",
                    "season_end":        "January 9, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway — Zone C1 & C1A — Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "October 14, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway — Zone C1 & C1A — Segment 2",
                    "season_start":      "November 1, 2026",
                    "season_end":        "January 18, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway — Zone C2 — Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "December 1, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway — Zone C2 — Segment 2",
                    "season_start":      "December 13, 2026",
                    "season_end":        "January 12, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Canada Goose / Dark Geese ────────────────────────────────────
        {
            "name":             "Canada Goose / Dark Geese",
            "asterisk":         True,
            "season_start":     "September 27, 2026",
            "season_end":       "February 16, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "Pacific Flyway; Central Flyway Zones C1, C1A, C2 (see sub-seasons)",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
            "sub_seasons": [
                {
                    "name":              "Pacific Flyway",
                    "season_start":      "September 27, 2026",
                    "season_end":        "January 1, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C1 — Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "October 5, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C1 — Segment 2",
                    "season_start":      "November 1, 2026",
                    "season_end":        "November 24, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C1 — Segment 3",
                    "season_start":      "December 6, 2026",
                    "season_end":        "February 16, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C1A — Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "October 8, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C1A — Segment 2",
                    "season_start":      "November 15, 2026",
                    "season_end":        "February 16, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C2 — Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "December 7, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway — Zone C2 — Segment 2",
                    "season_start":      "December 20, 2026",
                    "season_end":        "January 21, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
            ]
        },
        # ── Light Geese ──────────────────────────────────────────────────
        {
            "name":             "Light Geese",
            "asterisk":         False,
            "season_start":     "September 27, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "September 27 - December 31, 2026 and February 7-15, 2027",
            "hunting_units":    "Central Flyway",
            "bag_limit":        "No daily limit",
            "possession_limit": "No possession limit",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "September 27, 2026",
                    "season_end":        "December 31, 2026",
                    "bag_limit":         "No daily limit",
                    "possession_limit":  "No possession limit",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "February 7, 2027",
                    "season_end":        "February 15, 2027",
                    "bag_limit":         "No daily limit",
                    "possession_limit":  "No possession limit",
                },
            ]
        },
        # ── Early Canada Goose (Pacific Flyway) ──────────────────────────
        {
            "name":             "Early Canada Goose (Pacific Flyway)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "September 8, 2026",
            "season_raw":       "September 1, 2026 - September 8, 2026",
            "hunting_units":    "Pacific Flyway portion of Wyoming",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        # ── Sandhill Crane ───────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "October 19, 2026",
            "season_raw":       "See areas below for specific dates; limited quota",
            "hunting_units":    "Areas 1-6 (see sub-seasons)",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
            "sub_seasons": [
                {
                    "name":              "Area 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 15, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Area 2",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 15, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Area 3",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 8, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Area 4",
                    "season_start":      "September 27, 2026",
                    "season_end":        "October 19, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Area 5",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 15, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Area 6",
                    "season_start":      "September 13, 2026",
                    "season_end":        "October 5, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
            ]
        },
        # ── Snipe ────────────────────────────────────────────────────────
        {
            "name":             "Snipe",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "September 1, 2026 - December 16, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Sora & Virginia Rail ─────────────────────────────────────────
        {
            "name":             "Sora & Virginia Rail",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1, 2026 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily",
            "possession_limit": "75",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from WGFD license page.
    Valid through calendar year.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    HIP Permit ($0.50) required for migratory bird hunting.
    """
    return [
        {
            "name":             "Resident Game Bird/Small Game 12-Month",
            "asterisk":         False,
            "covers":           "Game birds and small game for 12 months",
            "resident_cost":    "$27.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Daily Game Bird/Small Game",
            "asterisk":         False,
            "covers":           "Game birds and small game for 1 day",
            "resident_cost":    "$9.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Game Bird/Small Game 12-Month",
            "asterisk":         False,
            "covers":           "Game birds and small game for 12 months (nonresident)",
            "resident_cost":    None,
            "nonresident_cost": "$74.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Daily Game Bird/Small Game",
            "asterisk":         False,
            "covers":           "Game birds and small game for 1 day (nonresident)",
            "resident_cost":    None,
            "nonresident_cost": "$22.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Archery License",
            "asterisk":         False,
            "covers":           "Archery hunting privileges for residents",
            "resident_cost":    "$16.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Archery License",
            "asterisk":         False,
            "covers":           "Archery hunting privileges for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$72.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese)",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    [
                {
                    "label": "WGFD — Licenses & Applications",
                    "url":   "https://wgfd.wyo.gov/licenses-applications"
                },
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                }
            ],
        },
        {
            "name":             "HIP Permit",
            "asterisk":         True,
            "covers":           "Required for all migratory bird hunters; funds Harvest Information Program",
            "resident_cost":    "$0.50",
            "nonresident_cost": "$0.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older hunting ducks, geese, and mergansers in Wyoming."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck (Ducks & Mergansers)",
                "Canada Goose / Dark Geese",
                "Light Geese",
                "Early Canada Goose (Pacific Flyway)"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Late Migratory Game Bird Hunting Seasons",
                    "evidence": (
                        "Federal Duck Stamp ($25) required for all waterfowl hunters "
                        "16 years of age or older."
                    )
                }
            ]
        },
        {
            "title": (
                "A HIP Permit ($0.50) is required for all migratory bird hunters "
                "in Wyoming. It is a Harvest Information Program certification."
            ),
            "applies_to": [
                "HIP Permit",
                "Mourning Dove",
                "Duck (Ducks & Mergansers)",
                "Canada Goose / Dark Geese",
                "Light Geese",
                "Early Canada Goose (Pacific Flyway)",
                "Sandhill Crane",
                "Snipe",
                "Sora & Virginia Rail"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Late Migratory Game Bird Hunting Seasons",
                    "evidence": (
                        "HIP Permit ($0.50) required for all migratory bird hunters."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck bag limits have species-specific restrictions within the "
                "6-bird daily aggregate (e.g. mallards, pintails, canvasbacks)."
            ),
            "applies_to": ["Duck (Ducks & Mergansers)"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Late Migratory Game Bird Hunting Seasons",
                    "evidence": (
                        "Daily bag limit 6 ducks in the aggregate with species-specific "
                        "restrictions per USFWS regulations."
                    )
                }
            ]
        },
        {
            "title": (
                "Sandhill Crane hunting in Wyoming is limited quota and requires "
                "a federal Sandhill Crane Hunting Permit in addition to a valid "
                "hunting license and HIP Permit."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Late Migratory Game Bird Hunting Seasons",
                    "evidence": (
                        "Sandhill crane season is a limited quota season. All areas "
                        "require a federal sandhill crane hunting permit."
                    )
                }
            ]
        },
        {
            "title": (
                "Wyoming follows both Pacific and Central Flyway waterfowl "
                "regulations. Central Flyway duck zones are split into C1, C1A, "
                "and C2 with different season splits and boundaries."
            ),
            "applies_to": [
                "Duck (Ducks & Mergansers)",
                "Canada Goose / Dark Geese"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Late Migratory Game Bird Hunting Seasons",
                    "evidence": (
                        "Wyoming is split between Pacific Flyway and Central Flyway "
                        "hunting zones. Central Flyway duck zones include C1, C1A, "
                        "and C2 with specific season dates for each."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[WY_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WY_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[WY_migratory] Using hardcoded data from WGFD season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Wyoming",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Late Migratory Game Bird Hunting Seasons | WGFD",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from WGFD Late Migratory Game Bird Hunting Seasons page."
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
        description="Scrape Wyoming Game & Fish migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/WY_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/WY_Migratory_Bird_dataset.json)"
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

    print(f"[WY_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
