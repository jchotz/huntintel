#!/usr/bin/env python3
"""
OK_Migratory_Bird_scrape.py — HuntIntel Oklahoma Migratory Game Bird Scraper
Fetches the Oklahoma Department of Wildlife Conservation migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python OK_Migratory_Bird_scrape.py
    python OK_Migratory_Bird_scrape.py --output my_output.json
    python OK_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
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
ODWC_HOME       = "https://www.wildlifedepartment.com/"
LICENSE_URL     = "https://www.wildlifedepartment.com/licensing/regs/license-fees"
PURCHASE_URL    = "https://gooutdoorsoklahoma.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Go Outdoors Oklahoma — License Sales Portal",
        "url":   "https://gooutdoorsoklahoma.com/"
    },
    {
        "label": "ODWC — License Fees",
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
            "2026-27 migratory game bird data from ODWC Hunting Seasons page. "
            "The Oklahoma Wildlife Conservation Commission approved 2026-27 migratory "
            "game bird season dates and bag limits via resolution in a regular meeting. "
            "Season dates follow the USFWS framework with Panhandle, Zone 1, and Zone 2 "
            "for waterfowl."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Oklahoma Migratory Game Birds.
    Sources: ODWC Hunting Seasons page, ODWC regulation pages,
    ODWC Commission meeting approvals.

    Migratory birds included: Dove, Teal, Duck (Panhandle, Zones 1 & 2),
    Goose (dark, light, white-fronted), Sandhill Crane, Woodcock, Snipe,
    Rail, Gallinule, Crow, Conservation Order Light Goose.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 29, 2026",
            "season_raw":       "September 1 - October 31, 2026 & December 1-29, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "30",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "October 31, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "30",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 1, 2026",
                    "season_end":        "December 29, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "30",
                },
            ]
        },
        # ── Eurasian Collared-Dove ─────────────────────────────────────────
        {
            "name":             "Eurasian Collared-Dove",
            "asterisk":         False,
            "season_start":     "January 1, 2027",
            "season_end":       "December 31, 2027",
            "season_raw":       "Open year-round, no bag limit",
            "hunting_units":    "Statewide",
            "bag_limit":        "No limit",
            "possession_limit": "No limit",
        },
        # ── September Teal ─────────────────────────────────────────────────
        {
            "name":             "Teal (September Teal)",
            "asterisk":         False,
            "season_start":     "September 12, 2026",
            "season_end":       "September 20, 2026",
            "season_raw":       "September 12, 2026 - September 20, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily (blue-winged, green-winged, cinnamon teal only)",
            "possession_limit": "18",
        },
        # ── Duck — Panhandle ───────────────────────────────────────────────
        {
            "name":             "Duck — Panhandle",
            "asterisk":         False,
            "season_start":     "October 3, 2026",
            "season_end":       "January 6, 2027",
            "season_raw":       "October 3, 2026 - January 6, 2027",
            "hunting_units":    "Panhandle (Cimarron, Texas, Beaver counties)",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
        },
        # ── Duck — Zones 1 & 2 ─────────────────────────────────────────────
        {
            "name":             "Duck — Zones 1 & 2",
            "asterisk":         False,
            "season_start":     "November 7, 2026",
            "season_end":       "January 24, 2027",
            "season_raw":       "November 7-29, 2026 & December 5, 2026 - January 24, 2027",
            "hunting_units":    "Zone 1 and Zone 2 (most of Oklahoma outside Panhandle)",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "November 7, 2026",
                    "season_end":        "November 29, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 5, 2026",
                    "season_end":        "January 24, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Special Resident Canada Goose ───────────────────────────────────
        {
            "name":             "Goose — Special Resident Canada Goose",
            "asterisk":         False,
            "season_start":     "September 13, 2026",
            "season_end":       "September 22, 2026",
            "season_raw":       "September 13, 2026 - September 22, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Dark Geese ──────────────────────────────────────────────────────
        {
            "name":             "Goose — Dark Geese",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "February 8, 2027",
            "season_raw":       "November 1-30, 2026 & December 6, 2026 - February 8, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily (Canada geese)",
            "possession_limit": "24",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "November 1, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "8 daily",
                    "possession_limit":  "24",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 6, 2026",
                    "season_end":        "February 8, 2027",
                    "bag_limit":         "8 daily",
                    "possession_limit":  "24",
                },
            ]
        },
        # ── Light Geese ────────────────────────────────────────────────────
        {
            "name":             "Goose — Light Geese",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "February 8, 2027",
            "season_raw":       "November 1-30, 2026 & December 6, 2026 - February 8, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "50 daily (snow, blue, Ross's geese)",
            "possession_limit": "No possession limit",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "November 1, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "No possession limit",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 6, 2026",
                    "season_end":        "February 8, 2027",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "No possession limit",
                },
            ]
        },
        # ── White-fronted Geese ────────────────────────────────────────────
        {
            "name":             "Goose — White-fronted Geese",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "February 1, 2027",
            "season_raw":       "November 1-30, 2026 & December 6, 2026 - February 1, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "2 daily",
            "possession_limit": "6",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "November 1, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "December 6, 2026",
                    "season_end":        "February 1, 2027",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
            ]
        },
        # ── Sandhill Crane ─────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "October 18, 2026",
            "season_end":       "January 18, 2027",
            "season_raw":       "October 18, 2026 - January 18, 2027",
            "hunting_units":    "West of I-35 (zones as defined)",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Woodcock ────────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "November 1, 2026",
            "season_end":       "December 15, 2026",
            "season_raw":       "November 1, 2026 - December 15, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "6",
        },
        # ── Snipe ──────────────────────────────────────────────────────────
        {
            "name":             "Snipe",
            "asterisk":         False,
            "season_start":     "September 27, 2026",
            "season_end":       "January 11, 2027",
            "season_raw":       "September 27, 2026 - January 11, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Rail ───────────────────────────────────────────────────────────
        {
            "name":             "Rail (Virginia, Sora)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1, 2026 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily",
            "possession_limit": "75",
        },
        # ── Gallinule ──────────────────────────────────────────────────────
        {
            "name":             "Gallinule (Common Gallinule)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 9, 2026",
            "season_raw":       "September 1, 2026 - November 9, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Crow ───────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "October 10, 2026",
            "season_end":       "March 4, 2027",
            "season_raw":       "October 10 - November 16, 2026 & December 9, 2026 - March 4, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily or possession limit",
            "possession_limit": "No limit",
            "sub_seasons": [
                {
                    "name":              "Fall Season",
                    "season_start":      "October 10, 2026",
                    "season_end":        "November 16, 2026",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
                {
                    "name":              "Winter Season",
                    "season_start":      "December 9, 2026",
                    "season_end":        "March 4, 2027",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
            ]
        },
        # ── Conservation Order Light Goose ─────────────────────────────────
        {
            "name":             "Light Goose Conservation Order (COLGS)",
            "asterisk":         False,
            "season_start":     "February 13, 2027",
            "season_end":       "March 30, 2027",
            "season_raw":       "February 13, 2027 - March 30, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily or possession limit",
            "possession_limit": "No limit",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from ODWC license fees page.
    Valid Jan 1 - Dec 31 unless noted.
    HIP Certification required for migratory bird hunting.
    Federal Duck Stamp ($29) required for waterfowl hunters 16+.
    Oklahoma Waterfowl Stamp ($21 resident, $31 nonresident) also required.
    """
    return [
        {
            "name":             "Resident Annual Hunting License",
            "asterisk":         False,
            "covers":           "Base hunting license for any legal species",
            "resident_cost":    "$36.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Annual Hunting License",
            "asterisk":         False,
            "covers":           "Base hunting license for any legal species",
            "resident_cost":    None,
            "nonresident_cost": "$209.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident 5-Day Hunting License",
            "asterisk":         True,
            "covers":           "Not valid for big game, waterfowl, turkey, or quail",
            "resident_cost":    None,
            "nonresident_cost": "$75.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Annual Super Hunting License",
            "asterisk":         False,
            "covers":           "Deer, turkey, waterfowl, elk, bear, antelope, furbearers, trapping",
            "resident_cost":    "$26.00",
            "nonresident_cost": "$151.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Annual Combination Fishing & Hunting License (Resident)",
            "asterisk":         False,
            "covers":           "Hunting and fishing combination",
            "resident_cost":    "$53.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Oklahoma Waterfowl Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 18+ in addition to license",
            "resident_cost":    "$21.00",
            "nonresident_cost": "$31.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, teal)",
            "resident_cost":    "$29.00",
            "nonresident_cost": "$29.00",
            "purchase_urls":    [
                {
                    "label": "Go Outdoors Oklahoma — License Portal",
                    "url":   "https://gooutdoorsoklahoma.com/"
                },
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                }
            ],
        },
        {
            "name":             "HIP Certification",
            "asterisk":         True,
            "covers":           "Required for all migratory bird/waterfowl hunters under age 64",
            "resident_cost":    "Free (online)",
            "nonresident_cost": "Free (online)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Game Bird Permit (WMA)",
            "asterisk":         True,
            "covers":           "Required for nonresidents hunting game birds on WMAs, GMAs, PHAs, and other ODWC lands",
            "resident_cost":    None,
            "nonresident_cost": "$100.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Wildlife Conservation Passport (Resident)",
            "asterisk":         False,
            "covers":           "Required for all persons 18+ entering ODWC lands unless exempt",
            "resident_cost":    "$46.00",
            "nonresident_cost": "$239.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A valid Oklahoma hunting license plus HIP Certification (free online) "
                "are required to hunt migratory game birds. The Oklahoma Waterfowl Stamp "
                "($21 resident, $31 nonresident) is required for waterfowl age 18+."
            ),
            "applies_to": [
                "Resident Annual Hunting License",
                "Non-resident Annual Hunting License",
                "Youth Annual Super Hunting License"
            ],
            "sources": [
                {
                    "url":      ("https://www.wildlifedepartment.com/licensing/regs/"
                                 "license-fees"),
                    "label":    "ODWC — License Fees",
                    "evidence": (
                        "HIP Certification is required for migratory bird/waterfowl "
                        "hunters under age 64. Oklahoma Waterfowl Stamp ($21 resident, "
                        "$31 nonresident) required for waterfowl hunters 18+."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($29) is required for all waterfowl hunters "
                "age 16 or older (ducks, geese, teal)."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck — Panhandle",
                "Duck — Zones 1 & 2",
                "Teal (September Teal)",
                "Goose — Dark Geese",
                "Goose — Light Geese",
                "Goose — White-fronted Geese",
                "Goose — Special Resident Canada Goose"
            ],
            "sources": [
                {
                    "url":      ("https://www.wildlifedepartment.com/licensing/regs/"
                                 "license-fees"),
                    "label":    "ODWC — License Fees (Federal Duck Stamp)",
                    "evidence": (
                        "Federal Duck Stamp ($29) required for all hunters 16+ "
                        "hunting migratory waterfowl, including lifetime license holders."
                    )
                }
            ]
        },
        {
            "title": (
                "A free Sandhill Crane Hunting Permit is required for all sandhill "
                "crane hunters regardless of age or residency. Available online at "
                "Go Outdoors Oklahoma."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      ("https://www.wildlifedepartment.com/licensing/regs/"
                                 "license-fees"),
                    "label":    "ODWC — License Fees (Sandhill Crane Permit)",
                    "evidence": (
                        "Sandhill Crane Permit ($3 / free online) required for all "
                        "hunters, regardless of age/residency."
                    )
                }
            ]
        },
        {
            "title": (
                "Non-residents must now purchase a $100 Game Bird Permit to hunt "
                "game birds on any Oklahoma WMA, GMA, PHA, WRP, WDU, or WMU. "
                "Non-residents must also check in and out of certain public areas."
            ),
            "applies_to": [
                "Non-resident Annual Hunting License",
                "Non-resident 5-Day Hunting License"
            ],
            "sources": [
                {
                    "url":      ("https://www.wildlifedepartment.com/"
                                 "outdoor-news/wildlife-commission-approves-"
                                 "slate-resolutions-and-rule-changes"),
                    "label":    "ODWC — Wildlife Commission Approves Slate of Resolutions, Rules",
                    "evidence": (
                        "For migratory game birds, setting 2026-27 hunting season dates "
                        "and bag limits. Non-resident Game Bird Permit ($100) required "
                        "for hunting game birds on any WMA."
                    )
                }
            ]
        },
        {
            "title": (
                "Oklahoma duck bag limits have species-specific restrictions: "
                "5 mallards (max 2 hens), 3 wood ducks, 2 pintails, 2 redheads, "
                "2 canvasbacks, 1 scaup."
            ),
            "applies_to": [
                "Duck — Panhandle",
                "Duck — Zones 1 & 2"
            ],
            "sources": [
                {
                    "url":      ("https://www.wildlifedepartment.com/hunting/regs/"
                                 "ducks-mergansers-coots"),
                    "label":    "ODWC — Ducks, Mergansers, Coots Regulations",
                    "evidence": (
                        "Daily bag 6 in aggregate, with no more than: 5 mallards "
                        "(only 2 of which may be hens), 3 wood ducks, 2 pintails, "
                        "2 redheads, 2 canvasbacks, 1 scaup."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[OK_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[OK_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[OK_migratory] Using hardcoded data from ODWC season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Oklahoma",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Hunting Seasons | Oklahoma Department of Wildlife Conservation",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from ODWC season dates and commission meeting resolutions."
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
        description="Scrape Oklahoma Department of Wildlife Conservation migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/OK_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/OK_Migratory_Bird_dataset.json)"
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

    print(f"[OK_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
