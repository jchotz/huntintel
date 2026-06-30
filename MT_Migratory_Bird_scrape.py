#!/usr/bin/env python3
"""
MT_Migratory_Bird_scrape.py — HuntIntel Montana Migratory Game Bird Scraper
Fetches the Montana FWP migratory bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python MT_Migratory_Bird_scrape.py
    python MT_Migratory_Bird_scrape.py --output my_output.json
    python MT_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://fwp.mt.gov/hunt/regulations/migratory-bird"
SEASONS_URL     = "https://fwp.mt.gov/hunt/seasons"
REGULATIONS_PDF = "https://fwp.mt.gov/binaries/content/assets/fwp/hunt/regulations/2026/2026-mig-bird--webless-final-for-web.pdf"
FWP_BUYANDPLY   = "https://fwp.mt.gov/buyandapply"
LICENSE_URL     = "https://fwp.mt.gov/buyandapply/hunting-licenses"
PURCHASE_URL    = "https://myfwp.mt.gov/fwpExtPortal/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Montana FWP — Buy and Apply",
        "url":   "https://myfwp.mt.gov/fwpExtPortal/"
    },
    {
        "label": "MT FWP — Hunting Licenses Info",
        "url":   "https://fwp.mt.gov/buyandapply/hunting-licenses"
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
        "page_label":   "Hunt By Species: Migratory Birds | Montana FWP",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory bird data from Montana FWP migratory bird page. "
            "Montana has three waterfowl flyways: Central Flyway Zone 1, "
            "Central Flyway Zone 2 (split season), and Pacific Flyway."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Montana Migratory Game Birds.
    Sources: Montana FWP Migratory Bird page, 2026 Migratory Bird Regulations PDF.

    Species: Dove, Snipe, Duck, Goose, Coot, Sandhill Crane.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Mourning Dove",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "October 30, 2026",
            "season_raw":       "September 1 - October 30, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Snipe ───────────────────────────────────────────────────────────
        {
            "name":             "Common (Wilson's) Snipe",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "September 1 - December 16, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Duck ────────────────────────────────────────────────────────────
        {
            "name":             "Duck (including Mergansers)",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "January 19, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "Central Flyway Zones 1, 2, and Pacific Flyway",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Central Flyway Zone 1",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 7, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway Zone 2 — Segment 1",
                    "season_start":      "October 4, 2026",
                    "season_end":        "October 11, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Central Flyway Zone 2 — Segment 2",
                    "season_start":      "October 24, 2026",
                    "season_end":        "January 19, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Pacific Flyway",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 15, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Goose ───────────────────────────────────────────────────────────
        {
            "name":             "Goose",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "January 27, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "Central Flyway Zones 1, 2, and Pacific Flyway",
            "bag_limit":        "5 daily Canada geese",
            "possession_limit": "15",
            "sub_seasons": [
                {
                    "name":              "Central Flyway Zone 1",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 15, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway Zone 2 — Segment 1",
                    "season_start":      "October 3, 2026",
                    "season_end":        "October 11, 2026",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Central Flyway Zone 2 — Segment 2",
                    "season_start":      "October 24, 2026",
                    "season_end":        "January 27, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Pacific Flyway",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 15, 2027",
                    "bag_limit":         "5 daily",
                    "possession_limit":  "15",
                },
            ]
        },
        # ── Coot ────────────────────────────────────────────────────────────
        {
            "name":             "Coot",
            "asterisk":         False,
            "season_start":     "October 3, 2026",
            "season_end":       "January 19, 2027",
            "season_raw":       "Same dates as ducks by zone",
            "hunting_units":    "Central Flyway Zones 1, 2, and Pacific Flyway",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Sandhill Crane ──────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "October 31, 2026",
            "season_raw":       "OTC mid-continent: Sept 28 – Oct 31; Special Permit (Rocky Mtn): Sept 1 – Oct 31",
            "hunting_units":    "Mid-continent (OTC) and Rocky Mountain (drawing) populations",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Swan (Tundra/Trumpeter) ────────────────────────────────────────
        {
            "name":             "Swan (Tundra/Trumpeter)",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "January 8, 2027",
            "season_raw":       "Central Flyway: Oct 3 – Jan 8; Pacific Flyway: Oct 10 – Dec 5",
            "hunting_units":    "Central Flyway and Pacific Flyway (drawing only)",
            "bag_limit":        "1 per season (special swan license required)",
            "possession_limit": "1",
            "sub_seasons": [
                {
                    "name":              "Central Flyway",
                    "season_start":      "October 3, 2026",
                    "season_end":        "January 8, 2027",
                    "bag_limit":         "1 per season",
                    "possession_limit":  "1",
                },
                {
                    "name":              "Pacific Flyway",
                    "season_start":      "October 10, 2026",
                    "season_end":        "December 5, 2026",
                    "bag_limit":         "1 per season",
                    "possession_limit":  "1",
                },
            ]
        },
        # ── Youth Waterfowl ─────────────────────────────────────────────────
        {
            "name":             "Youth Waterfowl",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "September 27, 2026",
            "season_raw":       "September 26-27, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "Same as regular season limits for ducks, geese, coots",
            "possession_limit": "Same as regular season",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from Montana FWP.
    Valid through season end.
    MT Migratory Bird License required for all migratory bird hunting.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    HIP certification required for all migratory bird hunters.
    """
    return [
        {
            "name":             "Montana Conservation License",
            "asterisk":         True,
            "covers":           "Required for all hunters (ages 12+); supports conservation programs",
            "resident_cost":    "$8.00",
            "nonresident_cost": "$10.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Base Hunting License",
            "asterisk":         True,
            "covers":           "Required for all hunters along with Conservation License",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$50.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Montana Migratory Bird License",
            "asterisk":         True,
            "covers":           "Required for all migratory bird hunting (doves, ducks, geese, swans, cranes, snipe, coots)",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$150.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp (Migratory Bird Hunting Stamp)",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, mergansers, swans, coots)",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    [
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                },
                {
                    "label": "Montana FWP Online License System",
                    "url":   "https://ols.fwp.mt.gov/"
                }
            ],
        },
        {
            "name":             "Sandhill Crane License (Drawing)",
            "asterisk":         True,
            "covers":           "Permit to hunt sandhill cranes (drawing, May 1 – June 1)",
            "resident_cost":    "$10.00 (application) + $10.00 (license if drawn)",
            "nonresident_cost": "$50.00 (application) + $75.00 (license if drawn)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Swan Hunting License (Drawing)",
            "asterisk":         True,
            "covers":           "Permit to hunt swans (drawing, May 1 – June 1)",
            "resident_cost":    "$10.00 (application) + $10.00 (license if drawn)",
            "nonresident_cost": "$50.00 (application) + $75.00 (license if drawn)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Migratory Bird License (Ages 12-17)",
            "asterisk":         False,
            "covers":           "Same as MT Migratory Bird License at reduced cost for youth",
            "resident_cost":    "$5.00",
            "nonresident_cost": "$75.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "All migratory bird hunters in Montana must complete HIP (Harvest Information Program) "
                "certification before purchasing a Montana Migratory Bird License."
            ),
            "applies_to": [
                "Montana Migratory Bird License",
                "Youth Migratory Bird License (Ages 12-17)",
            ],
            "sources": [
                {
                    "url":      "https://fwp.mt.gov/hunt/regulations/migratory-bird",
                    "label":    "Montana FWP — Migratory Bird Regulations",
                    "evidence": (
                        "HIP Requirement: All migratory bird hunters in Montana must complete a survey "
                        "(name, address, date of birth) before purchasing the Montana Migratory Bird License."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters age 16 or older "
                "(ducks, geese, mergansers, swans, coots). Not required during Spring Light Goose Conservation Order."
            ),
            "applies_to": [
                "Federal Duck Stamp (Migratory Bird Hunting Stamp)",
                "Duck (including Mergansers)",
                "Goose",
                "Coot",
                "Swan (Tundra/Trumpeter)",
            ],
            "sources": [
                {
                    "url":      "https://fwp.mt.gov/hunt/regulations/migratory-bird",
                    "label":    "Montana FWP — Migratory Bird Regulations",
                    "evidence": (
                        "Federal Migratory Bird Stamp required for individuals 16 and older "
                        "(both resident and nonresident). Available from USPS and all FWP offices."
                    )
                }
            ]
        },
        {
            "title": (
                "Central Flyway is divided into two zones. Zone 1 includes all Central Flyway counties "
                "except Zone 2. Zone 2 includes: Big Horn, Carbon, Custer, Prairie, Rosebud, "
                "Stillwater, Sweet Grass, Treasure, Yellowstone counties."
            ),
            "applies_to": [
                "Duck (including Mergansers)",
                "Goose",
                "Coot",
            ],
            "sources": [
                {
                    "url":      REGULATIONS_PDF,
                    "label":    "Montana FWP 2026 Migratory Bird Regulations (PDF)",
                    "evidence": (
                        "Central Flyway divided into two zones (map on page 8) with different season dates. "
                        "Zone 1: All other Central Flyway counties. "
                        "Zone 2: Big Horn, Carbon, Custer, Prairie, Rosebud, Stillwater, Sweet Grass, Treasure, Yellowstone."
                    )
                }
            ]
        },
        {
            "title": (
                "Sandhill crane and swan licenses are available through a drawing application "
                "process (May 1 – June 1). Must possess valid Conservation, Base Hunting, "
                "and MT Migratory Bird License to apply."
            ),
            "applies_to": [
                "Sandhill Crane",
                "Swan (Tundra/Trumpeter)",
            ],
            "sources": [
                {
                    "url":      REGULATIONS_PDF,
                    "label":    "Montana FWP 2026 Migratory Bird Regulations (PDF)",
                    "evidence": (
                        "Drawing Applications online at ols.fwp.mt.gov by 11:45 p.m. MDT: "
                        "Sandhill crane: May 1 – June 1; Swan: May 1 – June 1. "
                        "Application fees: $10 (resident), $50 (nonresident). "
                        "Must possess current Conservation, Base Hunting, and MT Migratory Bird License to apply."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck bag limits have species-specific restrictions: 6 daily in aggregate. "
                "Check FWP PDF for specific species limits (mallards, pintails, canvasbacks, etc.)."
            ),
            "applies_to": ["Duck (including Mergansers)"],
            "sources": [
                {
                    "url":      REGULATIONS_PDF,
                    "label":    "Montana FWP 2026 Migratory Bird Regulations (PDF)",
                    "evidence": (
                        "The daily bag limit is 6 ducks or mergansers. The daily bag "
                        "limit for coots is 15."
                    )
                }
            ]
        },
        {
            "title": (
                "72-hour swan reporting: Federal law requires hunters who shoot a swan in either "
                "flyway to complete and return a Swan Bill Measurement Card within 72 hours of harvest."
            ),
            "applies_to": ["Swan (Tundra/Trumpeter)"],
            "sources": [
                {
                    "url":      REGULATIONS_PDF,
                    "label":    "Montana FWP 2026 Migratory Bird Regulations (PDF)",
                    "evidence": (
                        "72-hour swan reporting: Federal law requires hunters who shoot a swan "
                        "in either flyway to complete and return a Swan Bill Measurement Card "
                        "within 72 hours of harvest."
                    )
                }
            ]
        },
        {
            "title": (
                "Authorized shooting hours: one-half hour before sunrise to sunset each day. "
                "Use official sunrise-sunset tables."
            ),
            "applies_to": [
                "Mourning Dove",
                "Common (Wilson's) Snipe",
                "Duck (including Mergansers)",
                "Goose",
                "Coot",
                "Sandhill Crane",
                "Swan (Tundra/Trumpeter)",
                "Youth Waterfowl",
            ],
            "sources": [
                {
                    "url":      REGULATIONS_PDF,
                    "label":    "Montana FWP 2026 Migratory Bird Regulations (PDF)",
                    "evidence": (
                        "Authorized shooting hours: one-half hour before sunrise to sunset each day. "
                        "Use official sunrise-sunset tables."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[MT_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[MT_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[MT_migratory] Using hardcoded data from MT FWP regulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Montana",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Hunt By Species: Migratory Birds | Montana FWP",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Montana FWP migratory bird page and regulations PDF."
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
        description="Scrape Montana FWP migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/MT_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/MT_Migratory_Bird_dataset.json)"
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

    print(f"[MT_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
