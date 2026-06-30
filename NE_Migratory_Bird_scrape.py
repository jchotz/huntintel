#!/usr/bin/env python3
"""
NE_Migratory_Bird_scrape.py — HuntIntel Nebraska Migratory Game Bird Scraper
Fetches the Nebraska Game & Parks migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python NE_Migratory_Bird_scrape.py
    python NE_Migratory_Bird_scrape.py --output my_output.json
    python NE_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://outdoornebraska.gov/hunt/hunting-seasons/"
PRICING_URL     = "https://outdoornebraska.gov/permits/permit-pricing/"
NEWS_RELEASE    = "https://www.centralnebraskatoday.com/2026/03/23/379069/"
PURCHASE_URL    = "https://www.gooutdoorsne.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Go Outdoors Nebraska — License Portal",
        "url":   "https://www.gooutdoorsne.com/"
    },
    {
        "label": "Nebraska Game & Parks — Permits",
        "url":   "https://outdoornebraska.gov/permits/hunting-permits/"
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
        "page_label":   "Hunting Seasons | Nebraska Game & Parks Commission",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory bird data from Nebraska Game & Parks season pages "
            "and March 2026 Commission meeting (3-zone duck configuration approved)."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Nebraska Migratory Game Birds.
    Sources: NGPC Hunting Seasons, March 2026 Commission approval.

    Species: Dove, Teal, Duck/Coot, Dark Goose, White-fronted Goose,
    Light Goose, Crow.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove (Mourning & White-winged)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "October 30, 2026",
            "season_raw":       "September 1 - October 30, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "45",
        },
        # ── Teal ────────────────────────────────────────────────────────────
        {
            "name":             "Teal (Early Teal)",
            "asterisk":         False,
            "season_start":     "September 5, 2026",
            "season_end":       "September 13, 2026",
            "season_raw":       "September 5 - 13, 2026 (Low Plains & High Plains)",
            "hunting_units":    "Low Plains and High Plains",
            "bag_limit":        "6 daily (any teal species)",
            "possession_limit": "18",
        },
        # ── Duck & Coot ─────────────────────────────────────────────────────
        {
            "name":             "Duck & Coot",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "January 27, 2027",
            "season_raw":       "See zones below for split season dates (3-zone configuration)",
            "hunting_units":    "Zones 1, 2, and 3 (see sub-seasons)",
            "bag_limit":        "6 daily in aggregate (Tier 1); 3 daily (Tier 2)",
            "possession_limit": "18 (3x daily bag)",
            "sub_seasons": [
                {
                    "name":              "Zone 1 — Segment 1",
                    "season_start":      "October 24, 2026",
                    "season_end":        "December 6, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Zone 1 — Segment 2",
                    "season_start":      "December 19, 2026",
                    "season_end":        "January 17, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Zone 2 — Segment 1",
                    "season_start":      "October 3, 2026",
                    "season_end":        "December 15, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Zone 2 — Segment 2 (High Plains)",
                    "season_start":      "January 6, 2027",
                    "season_end":        "January 27, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Zone 3 — Segment 1",
                    "season_start":      "October 24, 2026",
                    "season_end":        "January 5, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Zone 3 — Segment 2 (High Plains)",
                    "season_start":      "January 6, 2027",
                    "season_end":        "January 27, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Dark Goose ──────────────────────────────────────────────────────
        {
            "name":             "Dark Goose (Canada Goose)",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "February 9, 2027",
            "season_raw":       "See units below for season dates",
            "hunting_units":    "Platte River, Niobrara, and North Central Units",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
            "sub_seasons": [
                {
                    "name":              "Platte River Unit",
                    "season_start":      "October 28, 2026",
                    "season_end":        "February 9, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Niobrara Unit",
                    "season_start":      "October 28, 2026",
                    "season_end":        "February 9, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "North Central Unit",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 15, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
            ]
        },
        # ── White-fronted Goose ─────────────────────────────────────────────
        {
            "name":             "White-fronted Goose",
            "asterisk":         False,
            "season_start":     "October 17, 2026",
            "season_end":       "February 9, 2027",
            "season_raw":       "October 17 - December 27, 2026 AND January 25 - February 9, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Light Goose ─────────────────────────────────────────────────────
        {
            "name":             "Light Goose",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "April 15, 2027",
            "season_raw":       "Regular: Oct 3-Dec 30 & Jan 25-Feb 9; Conservation Order: Feb 10-Apr 15",
            "hunting_units":    "Statewide (regular); East, West, Rainwater Basin (conservation order)",
            "bag_limit":        "50 daily (regular); no limit (conservation order)",
            "possession_limit": "No possession limit",
        },
        # ── Crow ────────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "October 10, 2026",
            "season_end":       "March 11, 2027",
            "season_raw":       "October 10 - December 10, 2026 AND January 9 - March 11, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily limit",
            "possession_limit": "No possession limit",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from Nebraska Game & Parks.
    """
    return [
        {
            "name":             "Hunt Permit (Resident age 16+)",
            "asterisk":         False,
            "covers":           "Small game hunting including migratory birds",
            "resident_cost":    "$20.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Hunt Permit (age 15 & under)",
            "asterisk":         False,
            "covers":           "Small game hunting for youth",
            "resident_cost":    "Free",
            "nonresident_cost": "Free",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Annual Hunt Permit",
            "asterisk":         False,
            "covers":           "Small game hunting including migratory birds",
            "resident_cost":    None,
            "nonresident_cost": "$128.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 2-Day Hunt Permit",
            "asterisk":         False,
            "covers":           "Small game hunting for 2 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$89.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Habitat Stamp",
            "asterisk":         True,
            "covers":           "Required for all hunters pursuing small game",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$10.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Waterfowl Stamp",
            "asterisk":         True,
            "covers":           "Required in addition to Habitat Stamp for waterfowl hunting",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$10.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese)",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Nebraska transitioned to a three duck-zone configuration for 2026-27, "
                "replacing the previous four-zone system."
            ),
            "applies_to": ["Duck & Coot"],
            "sources": [
                {
                    "url":      NEWS_RELEASE,
                    "label":    "Central Nebraska Today — March 2026 Commission Meeting",
                    "evidence": (
                        "Approved staff recommendations include a transition to a "
                        "three duck-zone configuration instead of four."
                    )
                }
            ]
        },
        {
            "title": (
                "The Nebraska Habitat Stamp ($10) is required for all hunters pursuing "
                "small game. Waterfowl hunters also need a Waterfowl Stamp ($10)."
            ),
            "applies_to": [
                "Hunt Permit (Resident age 16+)",
                "Nonresident Annual Hunt Permit",
                "Habitat Stamp",
                "Waterfowl Stamp"
            ],
            "sources": [
                {
                    "url":      PRICING_URL,
                    "label":    "Nebraska Game & Parks — Permit Pricing",
                    "evidence": (
                        "A Habitat Stamp is required of all hunters pursuing any small game. "
                        "Those hunting waterfowl will need a second stamp: the Waterfowl Stamp."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck & Coot",
                "Dark Goose (Canada Goose)",
                "Teal (Early Teal)"
            ],
            "sources": [
                {
                    "url":      "https://www.fws.gov/duckstamps/",
                    "label":    "USFWS — Federal Duck Stamp",
                    "evidence": (
                        "Federal Duck Stamp required for waterfowl hunters 16 years of age or older."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[NE_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NE_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[NE_migratory] Using hardcoded data from NGPC and news release.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Nebraska",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Hunting Seasons | Nebraska Game & Parks Commission",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Nebraska Game & Parks season pages and March 2026 Commission news."
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
        description="Scrape Nebraska Game & Parks migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/NE_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/NE_Migratory_Bird_dataset.json)"
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

    print(f"[NE_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
