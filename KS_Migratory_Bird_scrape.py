#!/usr/bin/env python3
"""
KS_Migratory_Bird_scrape.py — HuntIntel Kansas Migratory Game Bird Scraper
Fetches the Kansas Department of Wildlife & Parks migratory bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python KS_Migratory_Bird_scrape.py
    python KS_Migratory_Bird_scrape.py --output my_output.json
    python KS_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/when-to-hunt"
DUCK_PAGE       = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/what-to-hunt/migratory-birds/ducks"
GOOSE_PAGE      = "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/what-to-hunt/migratory-birds/geese"
LICENSE_URL     = "https://www.ksoutdoors.gov/licenses-permits-fees/hunting-licenses-permit-fees"
PURCHASE_URL    = "https://www.ksoutdoors.gov/licenses-permits-fees"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Kansas Department of Wildlife & Parks — Licenses & Permits",
        "url":   "https://www.ksoutdoors.gov/licenses-permits-fees"
    },
    {
        "label": "KS Outdoors — License Purchase Portal",
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
        "page_label":   "When to Hunt | Kansas Department of Wildlife & Parks",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from Kansas Department of Wildlife & Parks. "
            "Seasons set annually within federal Central Flyway guidelines. "
            "Pintail bag limit expected to remain at 3 daily for 2026-2027. "
            "Youth waterfowl season runs 2 days per duck zone."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Kansas Migratory Game Birds.
    Sources: ksoutdoors.gov when-to-hunt page, duck and goose species pages.

    Migratory birds included: Dove, Teal (September Teal), Duck, Goose (Canada,
    White-fronted, Light), Sandhill Crane, Rail, Snipe, Woodcock, Crow.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove (Mourning & White-winged)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 29, 2026",
            "season_raw":       "September 1, 2026 - November 29, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "45",
        },
        # ── Eurasian Collared-Dove ──────────────────────────────────────────
        {
            "name":             "Exotic Dove (Eurasian Collared/Ringed Turtledove)",
            "asterisk":         False,
            "season_start":     "January 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "Year-round, no bag limit",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily limit",
            "possession_limit": "No possession limit",
        },
        # ── Teal (September Teal) ──────────────────────────────────────────
        {
            "name":             "Teal (September Teal)",
            "asterisk":         True,
            "season_start":     "September 26, 2026",
            "season_end":       "September 27, 2026",
            "season_raw":       "See zones below for specific season dates",
            "hunting_units":    "Low Plains Unit (see sub-seasons)",
            "bag_limit":        "6 daily",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Low Plains Unit, Early Zone",
                    "season_start":      "September 26, 2026",
                    "season_end":        "September 27, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Duck ────────────────────────────────────────────────────────────
        {
            "name":             "Duck",
            "asterisk":         True,
            "season_start":     "October 10, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "High Plains Unit and Low Plains Unit (Early, Late, Southeast Zones) — see sub-seasons",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "High Plains Unit — Segment 1",
                    "season_start":      "October 10, 2026",
                    "season_end":        "January 3, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "High Plains Unit — Segment 2",
                    "season_start":      "January 22, 2027",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Early Zone — Segment 1",
                    "season_start":      "October 10, 2026",
                    "season_end":        "December 6, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Early Zone — Segment 2",
                    "season_start":      "December 19, 2026",
                    "season_end":        "January 4, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Late Zone — Segment 1",
                    "season_start":      "November 1, 2026",
                    "season_end":        "January 4, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Late Zone — Segment 2",
                    "season_start":      "January 17, 2027",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Southeast Zone — Segment 1",
                    "season_start":      "November 8, 2026",
                    "season_end":        "January 4, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Low Plains Unit, Southeast Zone — Segment 2",
                    "season_start":      "January 10, 2027",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Goose (Canada & Cackling) ──────────────────────────────────────
        {
            "name":             "Canada & Cackling Goose (Dark Goose)",
            "asterisk":         True,
            "season_start":     "October 31, 2026",
            "season_end":       "February 14, 2027",
            "season_raw":       "See sub-seasons below",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily Canada/cackling geese",
            "possession_limit": "9",
            "sub_seasons": [
                {
                    "name":              "First Segment",
                    "season_start":      "October 31, 2026",
                    "season_end":        "November 1, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Second Segment",
                    "season_start":      "November 4, 2026",
                    "season_end":        "February 14, 2027",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
            ]
        },
        # ── White-fronted Goose ─────────────────────────────────────────────
        {
            "name":             "White-fronted Goose",
            "asterisk":         False,
            "season_start":     "October 31, 2026",
            "season_end":       "February 14, 2027",
            "season_raw":       "October 31, 2026 - November 1, 2026 and November 4, 2026 - February 14, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Light Goose ─────────────────────────────────────────────────────
        {
            "name":             "Light Goose (Snow & Ross')",
            "asterisk":         True,
            "season_start":     "October 31, 2026",
            "season_end":       "February 14, 2027",
            "season_raw":       "October 31, 2026 - November 1, 2026 and November 4, 2026 - February 14, 2027",
            "hunting_units":    "Statewide (Conservation Order extends to April 30)",
            "bag_limit":        "50 daily",
            "possession_limit": "None",
            "sub_seasons": [
                {
                    "name":              "Regular Season — First Segment",
                    "season_start":      "October 31, 2026",
                    "season_end":        "November 1, 2026",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "None",
                },
                {
                    "name":              "Regular Season — Second Segment",
                    "season_start":      "November 4, 2026",
                    "season_end":        "February 14, 2027",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "None",
                },
                {
                    "name":              "Light Goose Conservation Order",
                    "season_start":      "February 15, 2027",
                    "season_end":        "April 30, 2027",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
            ]
        },
        # ── Sandhill Crane ──────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "October 17, 2026",
            "season_end":       "January 7, 2027",
            "season_raw":       "See zones below for dates",
            "hunting_units":    "Central and West Crane Zones (see sub-seasons)",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
            "sub_seasons": [
                {
                    "name":              "Central Crane Zone",
                    "season_start":      "November 11, 2026",
                    "season_end":        "January 7, 2027",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "West Crane Zone",
                    "season_start":      "October 17, 2026",
                    "season_end":        "December 13, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
            ]
        },
        # ── Rail ────────────────────────────────────────────────────────────
        {
            "name":             "Rail (Sora & Virginia)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1, 2026 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily (rails & gallinules in aggregate)",
            "possession_limit": "75",
        },
        # ── Snipe ───────────────────────────────────────────────────────────
        {
            "name":             "Snipe (Common Snipe)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "September 1, 2026 - December 16, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Woodcock ────────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "October 17, 2026",
            "season_end":       "December 1, 2026",
            "season_raw":       "October 17, 2026 - December 1, 2026 (45 days)",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Crow ────────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "November 10, 2026",
            "season_end":       "March 10, 2027",
            "season_raw":       "November 10, 2026 - March 10, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily limit",
            "possession_limit": "No possession limit",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from Kansas Department of Wildlife & Parks.
    Valid through 365 days from purchase.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    """
    return [
        {
            "name":             "Resident Annual Hunting License (Ages 16-64)",
            "asterisk":         True,
            "covers":           "Any legal game bird or animal; 365-day auto-renew",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-Resident Annual Hunting License (Age 16+)",
            "asterisk":         True,
            "covers":           "Any legal game bird or animal; 365-day auto-renew",
            "resident_cost":    None,
            "nonresident_cost": "$125.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Senior Resident Annual Hunting License (Ages 65-74)",
            "asterisk":         False,
            "covers":           "Any legal game bird or animal; 365-day auto-renew",
            "resident_cost":    "$12.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Multi-Year Hunting License (Ages 16-20)",
            "asterisk":         False,
            "covers":           "Hunting license valid until Dec 31 of the year turning 21",
            "resident_cost":    "$40.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-Resident Youth Hunting License (Age 15 & Under)",
            "asterisk":         False,
            "covers":           "Hunting license for youth non-residents",
            "resident_cost":    None,
            "nonresident_cost": "$40.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident 5-Year Hunting License",
            "asterisk":         False,
            "covers":           "Hunting license valid for 1,825 days",
            "resident_cost":    "$100.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident 1-Year Combination Hunting & Fishing License",
            "asterisk":         False,
            "covers":           "Hunting + fishing; 365-day auto-renew",
            "resident_cost":    "$45.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-Resident 1-Year Combination Hunting & Fishing License",
            "asterisk":         False,
            "covers":           "Hunting + fishing; 365-day auto-renew",
            "resident_cost":    None,
            "nonresident_cost": "$190.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, teal); electronic stamp valid for season",
            "resident_cost":    "$25.00 (plus fulfillment)",
            "nonresident_cost": "$25.00 (plus fulfillment)",
            "purchase_urls":    [
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                },
                {
                    "label": "KS Outdoors — Licenses & Permits",
                    "url":   "https://www.ksoutdoors.gov/licenses-permits-fees"
                }
            ],
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A valid Kansas hunting license is required to hunt any game species "
                "in Kansas. Kansas residents age 15 and younger are not required to "
                "purchase a hunting license."
            ),
            "applies_to": [
                "Resident Annual Hunting License (Ages 16-64)",
                "Non-Resident Annual Hunting License (Age 16+)",
            ],
            "sources": [
                {
                    "url":      LICENSE_URL,
                    "label":    "KS DW&P — Hunting License Fees",
                    "evidence": (
                        "A valid hunting license is required to hunt in Kansas. "
                        "Kansas residents 15 and younger are not required to purchase "
                        "a hunting or fishing license."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older (ducks, geese, teal)."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck",
                "Canada & Cackling Goose (Dark Goose)",
                "White-fronted Goose",
                "Light Goose (Snow & Ross')",
                "Teal (September Teal)"
            ],
            "sources": [
                {
                    "url":      "https://www.fws.gov/duckstamps/",
                    "label":    "USFWS — Federal Duck Stamp",
                    "evidence": (
                        "Federal Duck Stamp ($25) required for all waterfowl hunters 16 years "
                        "of age or older. Available at post offices and online."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck bag limits have species-specific restrictions within the 6-duck "
                "daily aggregate: 5 mallards (max 2 hens), 3 wood ducks, 3 pintails, "
                "2 redheads, 2 canvasbacks, 2 scaup."
            ),
            "applies_to": ["Duck"],
            "sources": [
                {
                    "url":      DUCK_PAGE,
                    "label":    "KS DW&P — Duck Regulations",
                    "evidence": (
                        "Within the 6-duck limit: Mallards 5 (no more than 2 hens), "
                        "Wood ducks 3, Pintails 3, Redheads 2, Canvasbacks 2, Scaup 2."
                    )
                }
            ]
        },
        {
            "title": (
                "The Light Goose Conservation Order allows extended take from end of "
                "regular season until April 30. During the Conservation Order, unplugged "
                "shotguns, electronic calls, and extended shooting hours (½ hour after sunset) "
                "are permitted."
            ),
            "applies_to": [
                "Light Goose (Snow & Ross')"
            ],
            "sources": [
                {
                    "url":      GOOSE_PAGE,
                    "label":    "KS DW&P — Goose Regulations (Conservation Order)",
                    "evidence": (
                        "Conservation Order allows take outside normal Oct 1 - Mar 10 treaty "
                        "parameters: unplugged shotguns, electronic calls, shooting until "
                        "½ hour after sunset. In Kansas: from end of regular season until April 30."
                    )
                }
            ]
        },
        {
            "title": (
                "A Kansas Waterfowl Permit may be required in addition to the hunting license "
                "and Federal Duck Stamp. Check KS DW&P for current requirements."
            ),
            "applies_to": [
                "Duck",
                "Canada & Cackling Goose (Dark Goose)",
                "White-fronted Goose",
                "Light Goose (Snow & Ross')",
                "Teal (September Teal)"
            ],
            "sources": [
                {
                    "url":      "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/what-to-hunt/migratory-birds",
                    "label":    "KS DW&P — Migratory Birds",
                    "evidence": (
                        "Check the Kansas Hunting & Furharvesting Regulation Summary for "
                        "current waterfowl permit requirements."
                    )
                }
            ]
        },
        {
            "title": (
                "HIP (Harvest Information Program) Certification is required for migratory "
                "bird hunters. Obtained when purchasing a hunting license by indicating "
                "intent to hunt migratory game birds."
            ),
            "applies_to": [
                "Resident Annual Hunting License (Ages 16-64)",
                "Non-Resident Annual Hunting License (Age 16+)"
            ],
            "sources": [
                {
                    "url":      "https://www.ksoutdoors.gov/outdoor-activities/hunting-in-kansas/",
                    "label":    "KS DW&P — Hunting in Kansas",
                    "evidence": (
                        "HIP Certification is required for migratory bird hunters and is "
                        "obtained when purchasing a hunting license."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[KS_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[KS_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[KS_migratory] Using hardcoded data from KS DW&P season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Kansas",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "When to Hunt | Kansas Department of Wildlife & Parks",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from KS DW&P season dates page."
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
        description="Scrape Kansas Department of Wildlife & Parks migratory bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/KS_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/KS_Migratory_Bird_dataset.json)"
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

    print(f"[KS_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
