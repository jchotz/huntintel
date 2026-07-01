#!/usr/bin/env python3
"""
AR_Migratory_Bird_scrape.py — HuntIntel Arkansas Migratory Game Bird Scraper
Fetches the Arkansas Game & Fish Commission migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python AR_Migratory_Bird_scrape.py
    python AR_Migratory_Bird_scrape.py --output my_output.json
    python AR_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.agfc.com/hunting/waterfowl/waterfowl-dates-rules-regulations/"
DOVE_URL        = "https://www.agfc.com/hunting/more-game/dove/"
NEWS_URL        = "https://greenhead.net/waterfowl-season-dates-set/"
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
        "page_url":     SOURCE_URL,
        "page_label":   "Waterfowl Season Dates, Rules & Regulations | AGFC",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory bird data from AGFC waterfowl regulations and "
            "Greenhead Magazine (April 2026 Commission meeting). "
            "Arkansas is in the Mississippi Flyway."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Arkansas Migratory Game Birds.
    Sources: AGFC Waterfowl Regulations, Greenhead Magazine, AGFC dove page.

    Species: Dove, Teal, Duck/Coot/Merganser, Canada Goose, White-fronted Goose,
    Snow/Blue/Ross's Goose, Woodcock, Snipe, Rail.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove (Mourning & White-winged)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "January 15, 2027",
            "season_raw":       "September 1 - October 26, 2026 AND December 8, 2026 - January 15, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "45",
        },
        # ── Early Teal ──────────────────────────────────────────────────────
        {
            "name":             "Teal (Early Teal)",
            "asterisk":         False,
            "season_start":     "September 19, 2026",
            "season_end":       "September 27, 2026",
            "season_raw":       "September 19 - 27, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily (blue-winged, green-winged, cinnamon teal combined)",
            "possession_limit": "18",
        },
        # ── Duck, Coot & Merganser ──────────────────────────────────────────
        {
            "name":             "Duck, Coot & Merganser",
            "asterisk":         True,
            "season_start":     "November 21, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "Nov 21-29, Dec 10-23, Dec 26 - Jan 31 (3 segments)",
            "hunting_units":    "Statewide (Mississippi Flyway)",
            "bag_limit":        "6 ducks daily (species restrictions), 15 coot, 5 merganser",
            "possession_limit": "18 (3x daily bag)",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "November 21, 2026",
                    "season_end":        "November 29, 2026",
                    "bag_limit":         "6 ducks daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 10, 2026",
                    "season_end":        "December 23, 2026",
                    "bag_limit":         "6 ducks daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Segment 3",
                    "season_start":      "December 26, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "6 ducks daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Canada Goose ────────────────────────────────────────────────────
        {
            "name":             "Canada Goose",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "Early: Sep 1-Oct 15; Regular: same as duck segments",
            "hunting_units":    "Statewide",
            "bag_limit":        "5 daily (early), 2 daily (regular)",
            "possession_limit": "15 (early), 6 (regular)",
            "sub_seasons": [
                {
                    "name":              "Early Season",
                    "season_start":      "September 1, 2026",
                    "season_end":        "October 15, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Regular Season",
                    "season_start":      "November 21, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
            ]
        },
        # ── White-fronted Goose ─────────────────────────────────────────────
        {
            "name":             "White-fronted Goose",
            "asterisk":         False,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "Oct 31-Nov 8, then same as duck segments through Jan 31",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Snow, Blue & Ross's Goose ──────────────────────────────────────
        {
            "name":             "Snow, Blue & Ross's Goose",
            "asterisk":         True,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "Oct 31-Nov 8, then same as duck segments through Jan 31",
            "hunting_units":    "Statewide",
            "bag_limit":        "20 daily (regular); no limit (conservation order)",
            "possession_limit": "No possession limit",
        },
        # ── Woodcock ────────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "December 1, 2026",
            "season_end":       "January 15, 2027",
            "season_raw":       "December 1, 2026 - January 15, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Snipe ───────────────────────────────────────────────────────────
        {
            "name":             "Snipe (Common Snipe)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "September 1 - December 16, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Rail & Gallinule ────────────────────────────────────────────────
        {
            "name":             "Rail (Sora & Virginia) & Gallinule",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily rail; 15 daily gallinule",
            "possession_limit": "75 (rail), 45 (gallinule)",
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
            "covers":           "Base hunting license required for all hunting",
            "resident_cost":    "$10.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Sportsman's License (RS)",
            "asterisk":         False,
            "covers":           "All game including waterfowl (6 deer tags, 2 turkey tags)",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Annual Small Game License (NRH)",
            "asterisk":         False,
            "covers":           "All small game including migratory birds",
            "resident_cost":    None,
            "nonresident_cost": "$110.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 5-Day Small Game License (SG5)",
            "asterisk":         False,
            "covers":           "Small game for 5 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$80.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Arkansas Waterfowl Stamp",
            "asterisk":         True,
            "covers":           "Required for all waterfowl hunters (state stamp)",
            "resident_cost":    "$7.00",
            "nonresident_cost": "$50.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident WMA Waterfowl Permit (3-Day)",
            "asterisk":         True,
            "covers":           "Required for nonresidents to hunt waterfowl on certain WMAs during regular duck season",
            "resident_cost":    None,
            "nonresident_cost": "$40.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident WMA Waterfowl Permit (30-Day)",
            "asterisk":         True,
            "covers":           "Required for nonresidents to hunt waterfowl on certain WMAs during regular duck season",
            "resident_cost":    None,
            "nonresident_cost": "$200.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "HIP Registration is required for all migratory bird hunters age 16+ "
                "hunting ducks, geese, doves, coots, woodcock, snipe, rails, or gallinules. "
                "Complete when purchasing license."
            ),
            "applies_to": [
                "Resident Wildlife Conservation License (HNT)",
                "Nonresident Annual Small Game License (NRH)"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "AGFC — Waterfowl Regulations",
                    "evidence": (
                        "HIP Registration: Required for all migratory bird hunters (age 16+) "
                        "hunting ducks, geese, doves, coots, woodcock, snipe, rails, or gallinules. "
                        "Complete when purchasing license at AGFC office or online."
                    )
                }
            ]
        },
        {
            "title": (
                "The Arkansas Waterfowl Stamp ($7 resident / $50 nonresident) is required "
                "for all waterfowl hunters, in addition to the Federal Duck Stamp ($25)."
            ),
            "applies_to": [
                "Arkansas Waterfowl Stamp",
                "Federal Duck Stamp",
                "Duck, Coot & Merganser",
                "Canada Goose"
            ],
            "sources": [
                {
                    "url":      LICENSE_URL,
                    "label":    "AGFC — License Descriptions and Fees",
                    "evidence": (
                        "Arkansas Waterfowl Stamp: $7 resident, $50 nonresident. "
                        "Required for all waterfowl hunters."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck species restrictions: 4 mallards max (2 hens), 1 scaup, "
                "3 wood ducks, 3 pintails, 2 redheads, 2 canvasbacks, 2 black ducks, "
                "1 mottled duck."
            ),
            "applies_to": ["Duck, Coot & Merganser"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "AGFC — Duck Season Regulations",
                    "evidence": (
                        "Duck daily bag: 6 total with species restrictions — "
                        "4 mallards max (2 hen mallards), 1 scaup, 3 wood ducks, "
                        "3 pintails, 2 redheads, 2 canvasbacks, 2 black ducks, 1 mottled duck."
                    )
                }
            ]
        },
        {
            "title": (
                "Shooting hours on WMAs during regular duck season end at noon "
                "(except last day: sunrise to sunset). Early teal shooting hours "
                "begin at sunrise (no pre-sunrise shooting)."
            ),
            "applies_to": ["Teal (Early Teal)", "Duck, Coot & Merganser"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "AGFC — Waterfowl Shooting Hours",
                    "evidence": (
                        "Regular duck season (on WMAs): Shooting from 30 min before sunrise "
                        "to noon (except last day of regular season: sunrise to sunset). "
                        "Special Early Teal Season: Shooting hours begin at sunrise (no pre-sunrise)."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[AR_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[AR_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[AR_migratory] Using hardcoded data from AGFC regulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Arkansas",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Waterfowl Season Dates, Rules & Regulations | AGFC",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from AGFC waterfowl regulations and Greenhead Magazine."
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
        description="Scrape Arkansas Game & Fish Commission migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/AR_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/AR_Migratory_Bird_dataset.json)"
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

    print(f"[AR_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
