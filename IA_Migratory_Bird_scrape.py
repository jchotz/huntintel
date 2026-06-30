#!/usr/bin/env python3
"""
IA_Migratory_Bird_scrape.py — HuntIntel Iowa Migratory Game Bird Scraper
Fetches the Iowa DNR migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python IA_Migratory_Bird_scrape.py
    python IA_Migratory_Bird_scrape.py --output my_output.json
    python IA_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = ("https://www.iowadnr.gov/things-do/hunting-trapping/"
                   "types-hunting-trapping/migratory-game-bird-hunting")
IOWA_DNR_HOME   = "https://www.iowadnr.gov/"
LICENSE_URL     = "https://www.iowadnr.gov/things-do/hunting-trapping/hunting-licenses-fees"
PURCHASE_URL    = "https://gooutdoorsiowa.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Go Outdoors Iowa — License Sales Portal",
        "url":   "https://gooutdoorsiowa.com/"
    },
    {
        "label": "Iowa DNR — Hunting Licenses & Fees",
        "url":   "https://www.iowadnr.gov/things-do/hunting-trapping/hunting-licenses-fees"
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
        "page_label":   "2026-2027 Migratory Game Bird Hunting Seasons | Iowa DNR",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from Iowa DNR Migratory Game Bird "
            "Hunting page. The Iowa Natural Resources Commission approved 2026-27 "
            "migratory bird seasons in spring 2026. Season dates follow the standard "
            "USFWS framework with North, Central, and South Zones for waterfowl."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Iowa Migratory Game Birds.
    Sources: Iowa DNR Migratory Game Bird Hunting page, Iowa Hunting Seasons page.

    Migratory birds included: Dove, Teal, Duck (3 zones), Goose (3 zones),
    Woodcock, Snipe, Rail, Crow, Youth Waterfowl.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 29, 2026",
            "season_raw":       "September 1, 2026 - November 29, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning dove)",
            "possession_limit": "45",
        },
        # ── Special September Teal ──────────────────────────────────────────
        {
            "name":             "Teal (Special September Teal)",
            "asterisk":         False,
            "season_start":     "September 5, 2026",
            "season_end":       "September 13, 2026",
            "season_raw":       "September 5, 2026 - September 13, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily (blue-winged, green-winged, cinnamon teal only)",
            "possession_limit": "18",
        },
        # ── Duck — North Zone ──────────────────────────────────────────────
        {
            "name":             "Duck — North Zone",
            "asterisk":         False,
            "season_start":     "October 3, 2026",
            "season_end":       "December 8, 2026",
            "season_raw":       "October 3-9, 2026 & October 17 - December 8, 2026",
            "hunting_units":    "North Zone",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "North Zone — Segment 1",
                    "season_start":      "October 3, 2026",
                    "season_end":        "October 9, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "North Zone — Segment 2",
                    "season_start":      "October 17, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Duck — Central Zone ────────────────────────────────────────────
        {
            "name":             "Duck — Central Zone",
            "asterisk":         False,
            "season_start":     "October 10, 2026",
            "season_end":       "December 15, 2026",
            "season_raw":       "October 10-16, 2026 & October 24 - December 15, 2026",
            "hunting_units":    "Central Zone",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Central Zone — Segment 1",
                    "season_start":      "October 10, 2026",
                    "season_end":        "October 16, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Zone — Segment 2",
                    "season_start":      "October 24, 2026",
                    "season_end":        "December 15, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Duck — South Zone ──────────────────────────────────────────────
        {
            "name":             "Duck — South Zone",
            "asterisk":         False,
            "season_start":     "October 17, 2026",
            "season_end":       "December 22, 2026",
            "season_raw":       "October 17-23, 2026 & October 31 - December 22, 2026",
            "hunting_units":    "South Zone",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "South Zone — Segment 1",
                    "season_start":      "October 17, 2026",
                    "season_end":        "October 23, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "South Zone — Segment 2",
                    "season_start":      "October 31, 2026",
                    "season_end":        "December 22, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Goose — North Zone ─────────────────────────────────────────────
        {
            "name":             "Goose — North Zone",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "January 9, 2027",
            "season_raw":       "Sep 26-Oct 11, Oct 17-Dec 8, Dec 12-Jan 9",
            "hunting_units":    "North Zone",
            "bag_limit":        "Varies (dark geese & light geese)",
            "possession_limit": "Three times daily bag",
            "sub_seasons": [
                {
                    "name":              "North Zone — Early Season",
                    "season_start":      "September 26, 2026",
                    "season_end":        "October 11, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "North Zone — Mid Season",
                    "season_start":      "October 17, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "North Zone — Late Season",
                    "season_start":      "December 12, 2026",
                    "season_end":        "January 9, 2027",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
            ]
        },
        # ── Goose — Central Zone ───────────────────────────────────────────
        {
            "name":             "Goose — Central Zone",
            "asterisk":         False,
            "season_start":     "October 3, 2026",
            "season_end":       "January 16, 2027",
            "season_raw":       "Oct 3-18, Oct 24-Dec 15, Dec 19-Jan 16",
            "hunting_units":    "Central Zone",
            "bag_limit":        "Varies (dark geese & light geese)",
            "possession_limit": "Three times daily bag",
            "sub_seasons": [
                {
                    "name":              "Central Zone — Early Season",
                    "season_start":      "October 3, 2026",
                    "season_end":        "October 18, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "Central Zone — Mid Season",
                    "season_start":      "October 24, 2026",
                    "season_end":        "December 15, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "Central Zone — Late Season",
                    "season_start":      "December 19, 2026",
                    "season_end":        "January 16, 2027",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
            ]
        },
        # ── Goose — South Zone ─────────────────────────────────────────────
        {
            "name":             "Goose — South Zone",
            "asterisk":         False,
            "season_start":     "October 10, 2026",
            "season_end":       "January 23, 2027",
            "season_raw":       "Oct 10-25, Oct 31-Dec 22, Dec 26-Jan 23",
            "hunting_units":    "South Zone",
            "bag_limit":        "Varies (dark geese & light geese)",
            "possession_limit": "Three times daily bag",
            "sub_seasons": [
                {
                    "name":              "South Zone — Early Season",
                    "season_start":      "October 10, 2026",
                    "season_end":        "October 25, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "South Zone — Mid Season",
                    "season_start":      "October 31, 2026",
                    "season_end":        "December 22, 2026",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
                {
                    "name":              "South Zone — Late Season",
                    "season_start":      "December 26, 2026",
                    "season_end":        "January 23, 2027",
                    "bag_limit":         "See regulation booklet",
                    "possession_limit":  "See regulation booklet",
                },
            ]
        },
        # ── Metropolitan Canada Goose ──────────────────────────────────────
        {
            "name":             "Metropolitan Canada Goose",
            "asterisk":         False,
            "season_start":     "September 12, 2026",
            "season_end":       "September 20, 2026",
            "season_raw":       "September 12, 2026 - September 20, 2026",
            "hunting_units":    "Des Moines, Cedar Rapids/Iowa City, Waterloo/Cedar Falls zones",
            "bag_limit":        "5 daily Canada geese",
            "possession_limit": "15",
        },
        # ── Woodcock ───────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "October 3, 2026",
            "season_end":       "November 16, 2026",
            "season_raw":       "October 3, 2026 - November 16, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Snipe ──────────────────────────────────────────────────────────
        {
            "name":             "Snipe",
            "asterisk":         False,
            "season_start":     "September 5, 2026",
            "season_end":       "November 30, 2026",
            "season_raw":       "September 5, 2026 - November 30, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Rail ───────────────────────────────────────────────────────────
        {
            "name":             "Rail (Virginia & Sora)",
            "asterisk":         False,
            "season_start":     "September 5, 2026",
            "season_end":       "November 13, 2026",
            "season_raw":       "September 5, 2026 - November 13, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily (rails & gallinules in aggregate)",
            "possession_limit": "75",
        },
        # ── Crow ───────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "October 15, 2026",
            "season_end":       "March 31, 2027",
            "season_raw":       "October 15 - November 30, 2026 & January 14 - March 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily or possession limit",
            "possession_limit": "No limit",
            "sub_seasons": [
                {
                    "name":              "Fall Season",
                    "season_start":      "October 15, 2026",
                    "season_end":        "November 30, 2026",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
                {
                    "name":              "Winter Season",
                    "season_start":      "January 14, 2027",
                    "season_end":        "March 31, 2027",
                    "bag_limit":         "No limit",
                    "possession_limit":  "No limit",
                },
            ]
        },
        # ── Light Goose Conservation Order ─────────────────────────────────
        {
            "name":             "Light Goose Conservation Order",
            "asterisk":         False,
            "season_start":     "January 24, 2027",
            "season_end":       "May 1, 2027",
            "season_raw":       "January 24, 2027 - May 1, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "No daily or possession limit",
            "possession_limit": "No limit",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from Iowa DNR hunting license page.
    Valid through December 31 (annual) or as noted.
    Migratory Bird Fee ($11.50) required for all migratory bird hunting.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    """
    return [
        {
            "name":             "Resident Hunting License",
            "asterisk":         False,
            "covers":           "Hunting license valid for any legal species",
            "resident_cost":    "$22.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Hunting & Habitat License",
            "asterisk":         False,
            "covers":           "Hunting license plus habitat fee",
            "resident_cost":    "$35.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Hunting License (18+)",
            "asterisk":         False,
            "covers":           "Hunting license valid for any legal species",
            "resident_cost":    None,
            "nonresident_cost": "$131.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Hunting License (under 18)",
            "asterisk":         False,
            "covers":           "Hunting license valid for any legal species",
            "resident_cost":    None,
            "nonresident_cost": "$32.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident 5-Day Hunting & Habitat License",
            "asterisk":         False,
            "covers":           "5-day hunting license plus habitat fee",
            "resident_cost":    None,
            "nonresident_cost": "$90.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Migratory Bird Fee",
            "asterisk":         True,
            "covers":           "Required in addition to hunting license to hunt any migratory game bird (dove, duck, goose, teal, woodcock, rail, snipe)",
            "resident_cost":    "$11.50",
            "nonresident_cost": "$11.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Habitat Fee",
            "asterisk":         False,
            "covers":           "Required access fee for Iowa DNR lands and waters",
            "resident_cost":    "$15.00",
            "nonresident_cost": "$15.00",
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
                    "label": "Go Outdoors Iowa — License Portal",
                    "url":   "https://gooutdoorsiowa.com/"
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
                "The Iowa Migratory Bird Fee ($11.50) is required in addition "
                "to a valid hunting license to hunt any migratory game bird in Iowa."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident Hunting License (18+)",
                "Non-resident Hunting License (under 18)"
            ],
            "sources": [
                {
                    "url":      ("https://www.iowadnr.gov/things-do/hunting-trapping/"
                                 "hunting-licenses-fees"),
                    "label":    "Iowa DNR — Hunting Licenses & Fees",
                    "evidence": (
                        "Resident Migratory Bird Fee: $11.50. Required for hunting "
                        "migratory game birds. Nonresidents also pay the same fee."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older (ducks, geese, teal). An E-Stamp is valid for the "
                "entire hunting season."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck — North Zone",
                "Duck — Central Zone",
                "Duck — South Zone",
                "Goose — North Zone",
                "Goose — Central Zone",
                "Goose — South Zone",
                "Teal (Special September Teal)"
            ],
            "sources": [
                {
                    "url":      ("https://www.iowadnr.gov/things-do/hunting-trapping/"
                                 "types-hunting-trapping/migratory-game-bird-hunting"),
                    "label":    "Iowa DNR — Migratory Game Bird Hunting (Duck Stamp Info)",
                    "evidence": (
                        "Iowa migratory bird hunters can purchase an E-Stamp through "
                        "any license vendor or the Go Outdoors Iowa portal. The E-Stamp "
                        "is valid for the entire hunting season."
                    )
                }
            ]
        },
        {
            "title": (
                "HIP (Harvest Information Program) certification is required for all "
                "migratory game bird hunters annually. Obtained when purchasing a "
                "hunting license or via the Go Outdoors Iowa portal."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident Hunting License (18+)",
                "Non-resident Hunting License (under 18)"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Migratory Game Bird Hunting",
                    "evidence": (
                        "HIP Certification is required annually for all migratory "
                        "game bird hunters in Iowa."
                    )
                }
            ]
        },
        {
            "title": (
                "Iowa duck bag limits have species-specific restrictions: 4 mallards "
                "(max 2 females), 3 wood ducks, 2 pintails, 2 redheads, 2 canvasbacks, "
                "1 scaup, 1 black duck."
            ),
            "applies_to": [
                "Duck — North Zone",
                "Duck — Central Zone",
                "Duck — South Zone"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Migratory Game Bird Hunting",
                    "evidence": (
                        "Daily bag 6 in aggregate, with species-specific restrictions "
                        "including 4 mallards (max 2 hens), 3 wood ducks, 2 pintails, "
                        "2 redheads, 2 canvasbacks, 1 scaup, 1 black duck."
                    )
                }
            ]
        },
        {
            "title": (
                "Light Goose Conservation Order (Jan 24 - May 1, 2027) allows "
                "unlimited take of light geese (snow, blue, Ross's geese) with "
                "expanded methods including electronic calls and unplugged shotguns."
            ),
            "applies_to": ["Light Goose Conservation Order"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Iowa DNR — Migratory Game Bird Hunting",
                    "evidence": (
                        "Light Goose Conservation Order runs January 24 through "
                        "May 1, 2027, statewide, with no daily or possession limit."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[IA_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[IA_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[IA_migratory] Using hardcoded data from Iowa DNR season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Iowa",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "2026-2027 Migratory Game Bird Hunting Seasons | Iowa DNR",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Iowa DNR Migratory Game Bird page and regulation booklet."
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
        description="Scrape Iowa DNR migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/IA_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/IA_Migratory_Bird_dataset.json)"
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

    print(f"[IA_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
