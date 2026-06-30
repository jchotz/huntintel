#!/usr/bin/env python3
"""
OR_Migratory_Bird_scrape.py — HuntIntel Oregon Migratory Game Bird Scraper
Fetches the ODFW migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python OR_Migratory_Bird_scrape.py
    python OR_Migratory_Bird_scrape.py --output my_output.json
    python OR_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = ("https://www.eregulations.com/oregon/hunting/game-bird/"
                   "migratory-game-bird-seasons")
ODFW_HOME       = "https://myodfw.com/"
LICENSE_URL     = "https://www.eregulations.com/oregon/hunting/game-bird/license-tag-permit-fees"
PURCHASE_URL    = "https://odfw.huntfishoregon.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "ODFW — Hunt Fish Oregon Portal",
        "url":   "https://odfw.huntfishoregon.com/"
    },
    {
        "label": "ODFW — License, Tag, & Permit Fees",
        "url":   "https://www.eregulations.com/oregon/hunting/game-bird/license-tag-permit-fees"
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
        "page_label":   "Migratory Game Bird Seasons | Oregon eRegulations",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from ODFW eRegulations and Game Bird "
            "Program Staff Summary (April 24, 2026 Commission meeting). The Oregon "
            "Fish and Wildlife Commission considered adoption of the 2026-27 Game Bird "
            "Hunting Regulations in April 2026. Season dates follow the Pacific Flyway "
            "framework with Zone 1 and Zone 2 for most species."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Oregon Migratory Game Birds.
    Sources: ODFW eRegulations, Game Bird Program Staff Summary (April 2026),
    ODFW Commission action on 2026-27 season dates.

    Migratory birds included: Mourning Dove (2 zones), Band-tailed Pigeon,
    Duck (2 zones), Goose (multiple zones), Coot, Snipe (2 zones), Crow,
    Brant, Youth Waterfowl.
    """
    return [
        # ── Mourning Dove — Zone 1 ─────────────────────────────────────────
        {
            "name":             "Dove — Zone 1",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 14, 2026",
            "season_raw":       "September 1-30, 2026 & November 15 - December 14, 2026",
            "hunting_units":    "Zone 1",
            "bag_limit":        "15 daily (mourning dove)",
            "possession_limit": "45",
            "sub_seasons": [
                {
                    "name":              "Zone 1 — Segment 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "September 30, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "Zone 1 — Segment 2",
                    "season_start":      "November 15, 2026",
                    "season_end":        "December 14, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
            ]
        },
        # ── Mourning Dove — Zone 2 ─────────────────────────────────────────
        {
            "name":             "Dove — Zone 2",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "October 30, 2026",
            "season_raw":       "September 1, 2026 - October 30, 2026",
            "hunting_units":    "Zone 2",
            "bag_limit":        "15 daily (mourning dove)",
            "possession_limit": "45",
        },
        # ── Band-tailed Pigeon ─────────────────────────────────────────────
        {
            "name":             "Band-tailed Pigeon",
            "asterisk":         True,
            "season_start":     "September 15, 2026",
            "season_end":       "September 23, 2026",
            "season_raw":       "September 15, 2026 - September 23, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Duck (including Merganser) — Zone 1 ────────────────────────────
        {
            "name":             "Duck — Zone 1",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11-26, 2026 & October 30, 2026 - January 25, 2027",
            "hunting_units":    "Zone 1",
            "bag_limit":        "7 daily in aggregate (species restrictions apply)",
            "possession_limit": "21",
            "sub_seasons": [
                {
                    "name":              "Zone 1 — Segment 1",
                    "season_start":      "October 11, 2026",
                    "season_end":        "October 26, 2026",
                    "bag_limit":         "7 daily",
                    "possession_limit":  "21",
                },
                {
                    "name":              "Zone 1 — Segment 2",
                    "season_start":      "October 30, 2026",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "7 daily",
                    "possession_limit":  "21",
                },
            ]
        },
        # ── Duck (including Merganser) — Zone 2 ────────────────────────────
        {
            "name":             "Duck — Zone 2",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11 - November 30, 2026 & December 4, 2026 - January 25, 2027",
            "hunting_units":    "Zone 2",
            "bag_limit":        "7 daily in aggregate (species restrictions apply)",
            "possession_limit": "21",
            "sub_seasons": [
                {
                    "name":              "Zone 2 — Segment 1",
                    "season_start":      "October 11, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "7 daily",
                    "possession_limit":  "21",
                },
                {
                    "name":              "Zone 2 — Segment 2",
                    "season_start":      "December 4, 2026",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "7 daily",
                    "possession_limit":  "21",
                },
            ]
        },
        # ── Coot ───────────────────────────────────────────────────────────
        {
            "name":             "Coot",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "Concurrent with duck seasons by zone",
            "hunting_units":    "Statewide (concurrent with duck zones)",
            "bag_limit":        "25 daily",
            "possession_limit": "75",
        },
        # ── September Canada Goose ─────────────────────────────────────────
        {
            "name":             "Goose — September Canada Goose",
            "asterisk":         False,
            "season_start":     "September 6, 2026",
            "season_end":       "September 20, 2026",
            "season_raw":       "September 6-20, 2026 (Northwest Permit Zone); Sep 6-10 (other zones)",
            "hunting_units":    "Northwest Permit, Southwest, High Desert/Blue Mtn, Mid-Columbia zones; South Coast Closed",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        # ── Regular Canada Goose — Northwest Permit Zone ───────────────────
        {
            "name":             "Goose — Canada Goose (Northwest Permit Zone)",
            "asterisk":         True,
            "season_start":     "October 18, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "Oct 18-26, Nov 22-Jan 9, Jan 31-Feb 15, 2027",
            "hunting_units":    "Northwest Permit Zone",
            "bag_limit":        "2 daily (dusky Canada geese closed)",
            "possession_limit": "6",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "October 18, 2026",
                    "season_end":        "October 26, 2026",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "November 22, 2026",
                    "season_end":        "January 9, 2027",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
                {
                    "name":              "Segment 3",
                    "season_start":      "January 31, 2027",
                    "season_end":        "February 15, 2027",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
            ]
        },
        # ── Regular Canada Goose — Southwest Zone ──────────────────────────
        {
            "name":             "Goose — Canada Goose (Southwest Zone)",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11-26, 2026 & November 4, 2026 - January 25, 2027",
            "hunting_units":    "Southwest Zone",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "October 11, 2026",
                    "season_end":        "October 26, 2026",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "November 4, 2026",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
            ]
        },
        # ── Regular Canada Goose — South Coast Zone ────────────────────────
        {
            "name":             "Goose — Canada Goose (South Coast Zone)",
            "asterisk":         False,
            "season_start":     "October 4, 2026",
            "season_end":       "March 10, 2027",
            "season_raw":       "Oct 4-Dec 7, Dec 20-Jan 9, Feb 21-Mar 10, 2027",
            "hunting_units":    "South Coast Zone",
            "bag_limit":        "6 daily",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "October 4, 2026",
                    "season_end":        "December 7, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 20, 2026",
                    "season_end":        "January 9, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Segment 3",
                    "season_start":      "February 21, 2027",
                    "season_end":        "March 10, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Regular Canada Goose — High Desert & Blue Mtn ──────────────────
        {
            "name":             "Goose — Canada Goose (High Desert & Blue Mountain Zone)",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11 - November 30, 2026 & December 9, 2026 - January 25, 2027",
            "hunting_units":    "High Desert & Blue Mountain Zone",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "October 11, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 9, 2026",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
            ]
        },
        # ── Regular Canada Goose — Mid-Columbia Zone ───────────────────────
        {
            "name":             "Goose — Canada Goose (Mid-Columbia Zone)",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11-26, 2026 & November 4, 2026 - January 25, 2027",
            "hunting_units":    "Mid-Columbia Zone",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "October 11, 2026",
                    "season_end":        "October 26, 2026",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "November 4, 2026",
                    "season_end":        "January 25, 2027",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
            ]
        },
        # ── White-fronted & White Goose (Representative — SW Zone) ────────
        {
            "name":             "Goose — White-fronted & White Goose",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "See zone-specific sub-seasons (varies by zone)",
            "hunting_units":    "Varies by zone (Northwest Permit, SW, South Coast, High Desert, Mid-Columbia)",
            "bag_limit":        "10 white-fronted & 20 white geese daily",
            "possession_limit": "30 white-fronted & 60 white geese",
        },
        # ── Brant ──────────────────────────────────────────────────────────
        {
            "name":             "Brant",
            "asterisk":         True,
            "season_start":     "November 29, 2026",
            "season_end":       "December 14, 2026",
            "season_raw":       "November 29, 2026 - December 14, 2026",
            "hunting_units":    "Statewide (permit required)",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
        },
        # ── Wilson's Snipe — Zone 1 ────────────────────────────────────────
        {
            "name":             "Snipe — Zone 1",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "February 15, 2027",
            "season_raw":       "November 1, 2026 - February 15, 2027",
            "hunting_units":    "Zone 1",
            "bag_limit":        "8 daily (Wilson's snipe)",
            "possession_limit": "24",
        },
        # ── Wilson's Snipe — Zone 2 ────────────────────────────────────────
        {
            "name":             "Snipe — Zone 2",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 25, 2027",
            "season_raw":       "October 11, 2026 - January 25, 2027",
            "hunting_units":    "Zone 2",
            "bag_limit":        "8 daily (Wilson's snipe)",
            "possession_limit": "24",
        },
        # ── Crow ───────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "October 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 1, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily or possession limit",
            "possession_limit": "No limit",
        },
        # ── Youth Waterfowl ────────────────────────────────────────────────
        {
            "name":             "Youth Waterfowl",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "September 27, 2026",
            "season_raw":       "September 26-27, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "See youth regulations",
            "possession_limit": "See youth regulations",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from ODFW license fee page.
    Valid July 1 - June 30 (game bird license year).
    HIP Validation (free) required for all game bird hunters.
    Upland Game Bird Validation ($10) and Waterfowl Validation ($13.50) required.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    """
    return [
        {
            "name":             "Resident Hunting License",
            "asterisk":         False,
            "covers":           "Base hunting license",
            "resident_cost":    "$34.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Hunting License",
            "asterisk":         False,
            "covers":           "Base hunting license",
            "resident_cost":    None,
            "nonresident_cost": "$172.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident 3-Day Game Bird & Crow Hunting License",
            "asterisk":         True,
            "covers":           "Game birds and crows for 3 consecutive days; not valid for controlled hunts",
            "resident_cost":    None,
            "nonresident_cost": "$32.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Upland Game Bird Validation",
            "asterisk":         True,
            "covers":           "Required for upland game bird hunting (age 18+)",
            "resident_cost":    "$10.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Waterfowl Validation",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunting (age 18+)",
            "resident_cost":    "$13.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Game Bird Validation",
            "asterisk":         True,
            "covers":           "Required for nonresident game bird hunting (age 18+)",
            "resident_cost":    None,
            "nonresident_cost": "$44.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "HIP Validation",
            "asterisk":         True,
            "covers":           "Harvest Information Program — required for all game bird hunters",
            "resident_cost":    "Free",
            "nonresident_cost": "Free",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Sports Pac (Resident)",
            "asterisk":         False,
            "covers":           "Hunting, Angling, Shellfish Licenses; Combined Angling Harvest Tag; Upland Game Bird & Waterfowl Validations; Deer, Elk, Cougar, Bear, and Turkey tags",
            "resident_cost":    "$196.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, teal)",
            "resident_cost":    "$25.00 (plus fulfillment)",
            "nonresident_cost": "$25.00 (plus fulfillment)",
            "purchase_urls":    [
                {
                    "label": "ODFW — Hunt Fish Oregon Portal",
                    "url":   "https://odfw.huntfishoregon.com/"
                },
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                }
            ],
        },
        {
            "name":             "Northwest Oregon Goose Permit",
            "asterisk":         True,
            "covers":           "Required to hunt geese in the Northwest Permit Zone",
            "resident_cost":    "$2.00",
            "nonresident_cost": "$2.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "All Oregon game bird hunters need a valid hunting license, "
                "HIP Validation (free), plus the appropriate game bird validation: "
                "Upland Bird ($10 resident) and/or Waterfowl Validation ($13.50 resident). "
                "Nonresidents need the Nonresident Game Bird Validation ($44.50)."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident Hunting License",
                "Non-resident 3-Day Game Bird & Crow Hunting License"
            ],
            "sources": [
                {
                    "url":      ("https://www.eregulations.com/oregon/hunting/game-bird/"
                                 "license-tag-permit-fees"),
                    "label":    "ODFW — License, Tag, & Permit Fees",
                    "evidence": (
                        "HIP Validation (free, valid July 1 - June 30). Upland Game Bird "
                        "Validation ($10, age 18+). Waterfowl Validation ($13.50, age 18+). "
                        "Nonresident Game Bird Validation ($44.50, age 18+)."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older (ducks, geese, teal, brant)."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck — Zone 1",
                "Duck — Zone 2",
                "Goose — September Canada Goose",
                "Goose — Canada Goose (Northwest Permit Zone)",
                "Goose — Canada Goose (Southwest Zone)",
                "Goose — Canada Goose (South Coast Zone)",
                "Goose — Canada Goose (High Desert & Blue Mountain Zone)",
                "Goose — Canada Goose (Mid-Columbia Zone)",
                "Goose — White-fronted & White Goose",
                "Brant",
                "Coot",
                "Youth Waterfowl"
            ],
            "sources": [
                {
                    "url":      ("https://www.eregulations.com/oregon/hunting/game-bird/"
                                 "license-tag-permit-fees"),
                    "label":    "ODFW — License, Tag, & Permit Fees (Duck Stamp)",
                    "evidence": (
                        "Federal Duck Stamp ($29) required for all hunters 16+ "
                        "hunting migratory waterfowl."
                    )
                }
            ]
        },
        {
            "title": (
                "A Northwest Oregon Goose Permit ($2) is required to hunt geese "
                "in the Northwest Permit Zone. Dusky Canada geese are closed "
                "during the regular season in this zone."
            ),
            "applies_to": [
                "Goose — Canada Goose (Northwest Permit Zone)",
                "Northwest Oregon Goose Permit"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "ODFW — Migratory Game Bird Seasons",
                    "evidence": (
                        "Northwest Oregon Goose Permit ($2) required. During regular "
                        "season, dusky Canada geese are closed in the Northwest Permit Zone."
                    )
                }
            ]
        },
        {
            "title": (
                "Oregon duck bag limits have species-specific restrictions: "
                "3 pintails, 2 hen mallards, 2 redheads, 2 canvasbacks, "
                "2 scaup (during open season), 1 harlequin duck."
            ),
            "applies_to": [
                "Duck — Zone 1",
                "Duck — Zone 2"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "ODFW — Migratory Game Bird Seasons",
                    "evidence": (
                        "Within the 7-duck daily bag limit, you may not have more than: "
                        "3 pintails, 2 hen mallards, 2 redheads, 2 canvasbacks, "
                        "2 scaup (during open season), and 1 harlequin duck."
                    )
                }
            ]
        },
        {
            "title": (
                "A free Band-tailed Pigeon Permit ($2) and Brant Permit ($2) "
                "are required for hunting those species. Permits available at "
                "any license agent or online."
            ),
            "applies_to": [
                "Band-tailed Pigeon",
                "Brant"
            ],
            "sources": [
                {
                    "url":      ("https://www.eregulations.com/oregon/hunting/game-bird/"
                                 "license-tag-permit-fees"),
                    "label":    "ODFW — License, Tag, & Permit Fees",
                    "evidence": (
                        "Band-tailed Pigeon Permit ($2), Brant Permit ($2) required "
                        "for hunting those species."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[OR_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[OR_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[OR_migratory] Using hardcoded data from ODFW eRegulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Oregon",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Migratory Game Bird Seasons | Oregon eRegulations",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from ODFW eRegulations and Game Bird Program Staff Summary."
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
        description="Scrape ODFW migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/OR_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/OR_Migratory_Bird_dataset.json)"
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

    print(f"[OR_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
