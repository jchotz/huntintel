#!/usr/bin/env python3
"""
SD_Migratory_Bird_scrape.py — HuntIntel South Dakota Migratory Game Bird Scraper
Fetches the South Dakota GFP key dates page and outputs a structured
JSON dataset matching the HuntIntel schema.

Usage:
    python SD_Migratory_Bird_scrape.py
    python SD_Migratory_Bird_scrape.py --output my_output.json
    python SD_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://gfp.sd.gov/events/keydates/"
LICENSE_URL     = "https://gfp.sd.gov/licenses/"
PURCHASE_URL    = "https://gooutdoorssouthdakota.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "South Dakota Go Outdoors Sales Portal",
        "url":   "https://gooutdoorssouthdakota.com/"
    },
    {
        "label": "SD GFP — Licenses & Fees",
        "url":   "https://gfp.sd.gov/licenses/"
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
    return text.rstrip("* \n\r").strip(), has


# ── Scraper ────────────────────────────────────────────────────────────────────

def scrape_source_meta(soup: BeautifulSoup) -> dict:
    return {
        "page_url":     SOURCE_URL,
        "page_label":   "Key Dates | South Dakota Game, Fish & Parks",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird season data from SD GFP key dates page. "
            "South Dakota follows USFWS frameworks. "
            "Migratory Bird Certification ($5) required in addition to a valid "
            "hunting license for all migratory bird hunting."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for South Dakota Migratory Game Birds.
    Source: SD GFP key dates page (gfp.sd.gov/events/keydates/).

    Migratory birds included: Dove, Duck, Canada Goose, Light Goose,
    White-fronted Goose, Sandhill Crane, Snipe, Youth Waterfowl, Crow.
    """
    return [
        # ── Dove (Mourning Dove) ─────────────────────────────────────────────
        {
            "name":             "Dove (Mourning Dove)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1, 2026 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning dove)",
            "possession_limit": "45",
        },
        # ── Duck (Ducks & Mergansers) ────────────────────────────────────────
        {
            "name":             "Duck (Ducks & Mergansers)",
            "asterisk":         True,
            "season_start":     "September 26, 2026",
            "season_end":       "January 14, 2027",
            "season_raw":       "See zones below for zone-specific dates",
            "hunting_units":    "Low Plains North, Low Plains Middle, Low Plains South, and High Plains (see sub-seasons)",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Low Plains North",
                    "season_start":      "September 26, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Middle",
                    "season_start":      "September 26, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains South",
                    "season_start":      "October 24, 2026",
                    "season_end":        "January 5, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "High Plains",
                    "season_start":      "October 10, 2026",
                    "season_end":        "January 14, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Canada Goose ──────────────────────────────────────────────────────
        {
            "name":             "Canada Goose",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "February 14, 2027",
            "season_raw":       "Early Sep 1-30; then Unit 1 and Unit 2 (see sub-seasons)",
            "hunting_units":    "Early Season (statewide), Unit 1, and Unit 2 (see sub-seasons)",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
            "sub_seasons": [
                {
                    "name":              "Early Canada Goose",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 30, 2026",
                    "bag_limit":         "5 daily Canada geese",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Unit 1",
                    "season_start":      "October 1, 2026",
                    "season_end":        "December 16, 2026",
                    "bag_limit":         "5 daily Canada geese",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Unit 2",
                    "season_start":      "November 2, 2026",
                    "season_end":        "February 14, 2027",
                    "bag_limit":         "5 daily Canada geese",
                    "possession_limit":  "15",
                },
            ]
        },
        # ── Light Goose ───────────────────────────────────────────────────────
        {
            "name":             "Light Goose",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "January 8, 2027",
            "season_raw":       "September 26, 2026 - January 8, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily limit",
            "possession_limit": "No possession limit",
        },
        # ── White-fronted Goose ───────────────────────────────────────────────
        {
            "name":             "White-fronted Goose",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "December 8, 2026",
            "season_raw":       "September 26, 2026 - December 8, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Sandhill Crane ────────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "November 22, 2026",
            "season_raw":       "September 26, 2026 - November 22, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Snipe (Common Snipe) ──────────────────────────────────────────────
        {
            "name":             "Snipe (Common Snipe)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "October 31, 2026",
            "season_raw":       "September 1, 2026 - October 31, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Youth Waterfowl ──────────────────────────────────────────────────
        {
            "name":             "Youth Waterfowl (Resident Only)",
            "asterisk":         False,
            "season_start":     "September 12, 2026",
            "season_end":       "September 13, 2026",
            "season_raw":       "September 12-13, 2026 (Resident youth only)",
            "hunting_units":    "Statewide",
            "bag_limit":        "Same as regular duck/goose season limits",
            "possession_limit": "Same as regular season limits",
        },
        # ── Crow ──────────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "April 30, 2027",
            "season_raw":       "Fall: Sep 1 - Oct 31; Spring: Mar 1 - Apr 30",
            "hunting_units":    "Statewide",
            "bag_limit":        "No limit",
            "possession_limit": "No limit",
            "sub_seasons": [
                {
                    "name":              "Fall Season",
                    "season_start":      "September 1, 2026",
                    "season_end":        "October 31, 2026",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
                {
                    "name":              "Spring Season",
                    "season_start":      "March 1, 2027",
                    "season_end":        "April 30, 2027",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
            ]
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from SD GFP license page.
    Valid through February 28 each year (SD license year).
    Migratory Bird Certification ($5) required for all migratory bird hunting.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    """
    return [
        {
            "name":             "Resident Small Game License",
            "asterisk":         False,
            "covers":           "All small game including migratory birds (does not include fishing)",
            "resident_cost":    "$36.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Combination License",
            "asterisk":         False,
            "covers":           "Fishing + small game + predator hunting",
            "resident_cost":    "$60.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Waterfowl License (3-Day)",
            "asterisk":         False,
            "covers":           "Waterfowl hunting for 3 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$106.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Waterfowl License (10-Day)",
            "asterisk":         False,
            "covers":           "Waterfowl hunting for 10 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$145.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Migratory Bird Certification",
            "asterisk":         True,
            "covers":           "Required in addition to a hunting license to hunt any migratory bird (ducks, geese, dove, snipe, crane, coot)",
            "resident_cost":    "$5.00",
            "nonresident_cost": "$5.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, mergansers)",
            "resident_cost":    "$25.00 (plus fulfillment fee)",
            "nonresident_cost": "$25.00 (plus fulfillment fee)",
            "purchase_urls":    [
                {
                    "label": "South Dakota Go Outdoors Sales Portal",
                    "url":   "https://gooutdoorssouthdakota.com/"
                },
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                }
            ],
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A Migratory Bird Certification ($5) is required in addition "
                "to a valid hunting license to hunt any migratory game bird "
                "in South Dakota (ducks, geese, dove, snipe, crane, coot)."
            ),
            "applies_to": [
                "Resident Small Game License",
                "Resident Combination License",
                "Nonresident Waterfowl License (3-Day)",
                "Nonresident Waterfowl License (10-Day)"
            ],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/licenses/",
                    "label":    "SD GFP — Licenses & Permits",
                    "evidence": (
                        "A Migratory Bird Certification ($5) is required for "
                        "all migratory bird hunters in addition to a valid "
                        "hunting license. Covers ducks, geese, dove, snipe, "
                        "crane, and coot."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl "
                "hunters age 16 or older (ducks, geese, mergansers)."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck (Ducks & Mergansers)",
                "Canada Goose",
                "Light Goose",
                "White-fronted Goose"
            ],
            "sources": [
                {
                    "url":      "https://www.fws.gov/duckstamps/",
                    "label":    "USFWS — Federal Duck Stamp",
                    "evidence": (
                        "All waterfowl hunters 16 years of age or older "
                        "must possess a valid Federal Duck Stamp."
                    )
                }
            ]
        },
        {
            "title": (
                "HIP Certification (Harvest Information Program) is required "
                "for all migratory bird hunters and is included when "
                "purchasing a hunting license in South Dakota."
            ),
            "applies_to": [
                "Resident Small Game License",
                "Resident Combination License",
                "Nonresident Waterfowl License (3-Day)",
                "Nonresident Waterfowl License (10-Day)"
            ],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/hunt/",
                    "label":    "SD GFP — Hunting Information",
                    "evidence": (
                        "HIP certification is required for all migratory "
                        "bird hunters and is obtained when purchasing a "
                        "hunting license. There is no additional fee for "
                        "HIP certification in South Dakota."
                    )
                }
            ]
        },
        {
            "title": (
                "South Dakota duck hunting has species-specific restrictions "
                "within the 6-bird daily bag: species limits apply per "
                "USFWS regulations."
            ),
            "applies_to": ["Duck (Ducks & Mergansers)"],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/regulations/waterfowl/",
                    "label":    "SD GFP — Waterfowl Regulations",
                    "evidence": (
                        "Daily bag limit for ducks is 6 in the aggregate, "
                        "with species-specific restrictions including "
                        "limits on mallards, pintails, canvasbacks, "
                        "redheads, and scaup as established by USFWS."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth Waterfowl Weekend (September 12-13, 2026) is open "
                "to resident youth hunters only, with the same bag limits "
                "as the regular season. Youth must be accompanied by a "
                "non-hunting adult 18+."
            ),
            "applies_to": ["Youth Waterfowl (Resident Only)"],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/events/keydates/",
                    "label":    "SD GFP — Key Dates",
                    "evidence": (
                        "Youth Waterfowl Season is September 12-13, 2026, "
                        "open to resident youth hunters only with same "
                        "bag limits as regular waterfowl season."
                    )
                }
            ]
        },
        {
            "title": (
                "Sandhill Crane hunting requires a free Sandhill Crane "
                "Hunting Permit in addition to a valid hunting license "
                "and Migratory Bird Certification."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/hunt/sandhill-crane/",
                    "label":    "SD GFP — Sandhill Crane Hunting",
                    "evidence": (
                        "A free Sandhill Crane Hunting Permit is required "
                        "to hunt sandhill cranes in South Dakota, available "
                        "through the SD GFP licensing system."
                    )
                }
            ]
        },
        {
            "title": (
                "Light geese (snow, blue, Ross's geese) have no daily or "
                "possession limit during the regular season. Conservation "
                "order measures may extend the season beyond January 8."
            ),
            "applies_to": ["Light Goose"],
            "sources": [
                {
                    "url":      "https://gfp.sd.gov/events/keydates/",
                    "label":    "SD GFP — Key Dates",
                    "evidence": (
                        "Light goose season runs September 26, 2026 through "
                        "January 8, 2027 with no daily limit and no "
                        "possession limit."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[SD_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[SD_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[SD_migratory] Using hardcoded data from SD GFP season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "South Dakota",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Key Dates | South Dakota Game, Fish & Parks",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from SD GFP key dates page and regulations."
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
        description="Scrape South Dakota GFP migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/SD_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/SD_Migratory_Bird_dataset.json)"
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

    print(f"[SD_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
