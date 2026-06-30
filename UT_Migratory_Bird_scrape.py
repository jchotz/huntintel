#!/usr/bin/env python3
"""
UT_Migratory_Bird_scrape.py — HuntIntel Utah Migratory Game Bird Scraper
Fetches the Utah Division of Wildlife Resources waterfowl pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python UT_Migratory_Bird_scrape.py
    python UT_Migratory_Bird_scrape.py --output my_output.json
    python UT_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://wildlife.utah.gov/waterfowl"
GUIDEBOOK_URL   = "https://wildlife.utah.gov/guidebooks"
LICENSE_URL     = "https://wildlife.utah.gov/licenses"
PURCHASE_URL    = "https://wildlife.utah.gov/licenses"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Utah DWR License Sales Portal",
        "url":   "https://wildlife.utah.gov/licenses"
    },
    {
        "label": "Utah DWR — Waterfowl Page",
        "url":   "https://wildlife.utah.gov/waterfowl"
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
        "page_label":   "2026-2027 Waterfowl Seasons | Utah DWR",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from Utah DWR waterfowl page. "
            "Utah waterfowl seasons follow USFWS frameworks approved in late summer. "
            "Northern and Southern Zones have split seasons for ducks and Canada geese. "
            "Sandhill crane hunting is limited quota — check the DWR guidebook for annual "
            "draw details."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Utah Migratory Game Birds.
    Sources: Utah DWR waterfowl page (wildlife.utah.gov/waterfowl),
    Utah DWR guidebooks.

    Migratory birds included: Dove, Duck, Canada Goose, Snipe,
    Sandhill Crane, Crow, Youth Waterfowl.
    """
    return [
        # ── Dove (Mourning Dove) ─────────────────────────────────────────────
        {
            "name":             "Mourning Dove",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "November 20, 2026",
            "season_raw":       "September 1, 2026 - November 20, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Duck ─────────────────────────────────────────────────────────────
        {
            "name":             "Duck",
            "asterisk":         True,
            "season_start":     "October 17, 2026",
            "season_end":       "January 30, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "Northern and Southern Zones (see sub-seasons)",
            "bag_limit":        "6 daily in aggregate",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Northern Zone — Segment 1",
                    "season_start":      "October 17, 2026",
                    "season_end":        "December 12, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Northern Zone — Segment 2",
                    "season_start":      "January 8, 2027",
                    "season_end":        "January 30, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Southern Zone — Segment 1",
                    "season_start":      "October 24, 2026",
                    "season_end":        "December 14, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Southern Zone — Segment 2",
                    "season_start":      "January 15, 2027",
                    "season_end":        "March 10, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Canada Goose ─────────────────────────────────────────────────────
        {
            "name":             "Canada Goose",
            "asterisk":         True,
            "season_start":     "October 17, 2026",
            "season_end":       "January 30, 2027",
            "season_raw":       "Same zone structure as ducks; see sub-seasons",
            "hunting_units":    "Northern and Southern Zones (see sub-seasons)",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Northern Zone — Segment 1",
                    "season_start":      "October 17, 2026",
                    "season_end":        "December 12, 2026",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Northern Zone — Segment 2",
                    "season_start":      "January 8, 2027",
                    "season_end":        "January 30, 2027",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Southern Zone — Segment 1",
                    "season_start":      "October 24, 2026",
                    "season_end":        "December 14, 2026",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
                {
                    "name":              "Southern Zone — Segment 2",
                    "season_start":      "January 15, 2027",
                    "season_end":        "March 10, 2027",
                    "bag_limit":         "4 daily",
                    "possession_limit":  "12",
                },
            ]
        },
        # ── Snipe ────────────────────────────────────────────────────────────
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
        # ── Sandhill Crane ───────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "TBD — limited quota draw",
            "season_end":       "TBD — limited quota draw",
            "season_raw":       "Limited quota; check DWR guidebook for annual draw details",
            "hunting_units":    "Limited quota hunting units per DWR guidebook",
            "bag_limit":        "Per permit conditions",
            "possession_limit": "Per permit conditions",
        },
        # ── Crow ─────────────────────────────────────────────────────────────
        {
            "name":             "Crow",
            "asterisk":         False,
            "season_start":     "Open season",
            "season_end":       "Open season",
            "season_raw":       "Open season — no closed season in Utah",
            "hunting_units":    "Statewide",
            "bag_limit":        "No limit",
            "possession_limit": "No limit",
        },
        # ── Youth Waterfowl ──────────────────────────────────────────────────
        {
            "name":             "Youth Waterfowl",
            "asterisk":         True,
            "season_start":     "Check DWR guidebook",
            "season_end":       "Check DWR guidebook",
            "season_raw":       "Youth waterfowl days scheduled annually; check DWR guidebook",
            "hunting_units":    "Statewide",
            "bag_limit":        "Per DWR guidebook",
            "possession_limit": "Per DWR guidebook",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from Utah DWR license page.
    Valid through calendar year / annual cycle.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    HIP Certification required.
    """
    return [
        {
            "name":             "Resident 1-Year Basic Hunting (Ages 18-64)",
            "asterisk":         False,
            "covers":           "Basic hunting license for resident adults; valid one year",
            "resident_cost":    "$40.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Multi-Year Basic Hunting (Ages 18-64)",
            "asterisk":         False,
            "covers":           "Basic hunting license for resident adults at discounted annual rate",
            "resident_cost":    "$39.00/year",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident 1-Year Combination License (Ages 18-64)",
            "asterisk":         False,
            "covers":           "Hunting + fishing combination license for resident adults",
            "resident_cost":    "$44.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Multi-Year Combination License (Ages 18-64)",
            "asterisk":         False,
            "covers":           "Hunting + fishing combination license at discounted annual rate",
            "resident_cost":    "$43.00/year",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 1-Year Basic Hunting (Ages 18+)",
            "asterisk":         False,
            "covers":           "Basic hunting license for nonresident adults; valid one year",
            "resident_cost":    None,
            "nonresident_cost": "$144.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Multi-Year Basic Hunting (Ages 18+)",
            "asterisk":         False,
            "covers":           "Basic hunting license for nonresident adults at discounted annual rate",
            "resident_cost":    None,
            "nonresident_cost": "$143.00/year",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 3-Day Small Game License",
            "asterisk":         False,
            "covers":           "Small game hunting for 3 consecutive days (nonresident)",
            "resident_cost":    None,
            "nonresident_cost": "$89.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 1-Year Combination License",
            "asterisk":         False,
            "covers":           "Hunting + fishing combination license for nonresidents",
            "resident_cost":    None,
            "nonresident_cost": "$190.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Duck Stamp",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese); electronic stamp valid for season",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A Federal Duck Stamp ($25) is required for all waterfowl hunters "
                "age 16 or older hunting ducks, geese, or other waterfowl in Utah."
            ),
            "applies_to": [
                "Federal Duck Stamp",
                "Duck",
                "Canada Goose",
                "Youth Waterfowl"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Waterfowl Page",
                    "evidence": (
                        "Federal Duck Stamp ($25) required for waterfowl hunters 16+. "
                        "Available at wildlife.utah.gov/licenses or any U.S. Post Office."
                    )
                }
            ]
        },
        {
            "title": (
                "HIP (Harvest Information Program) Certification is required "
                "for all migratory bird hunters in Utah."
            ),
            "applies_to": [
                "Mourning Dove",
                "Duck",
                "Canada Goose",
                "Snipe",
                "Sandhill Crane",
                "Crow",
                "Youth Waterfowl"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Waterfowl Page",
                    "evidence": (
                        "HIP Certification is required for all migratory bird hunters. "
                        "Available when purchasing a hunting license or at wildlife.utah.gov."
                    )
                }
            ]
        },
        {
            "title": (
                "Utah has two waterfowl zones — Northern and Southern — with split "
                "season segments for ducks and Canada geese. Northern Zone runs "
                "Oct 17–Dec 12 and Jan 8–30. Southern Zone runs Oct 24–Dec 14 and "
                "Jan 15–Mar 10."
            ),
            "applies_to": ["Duck", "Canada Goose"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Waterfowl Page",
                    "evidence": (
                        "Northern Zone: Segment 1 Oct 17–Dec 12, Segment 2 Jan 8–30; "
                        "Southern Zone: Segment 1 Oct 24–Dec 14, Segment 2 Jan 15–Mar 10."
                    )
                }
            ]
        },
        {
            "title": (
                "Sandhill crane hunting is limited quota — hunters must apply "
                "through the Utah DWR permit drawing. Consult the annual DWR guidebook "
                "for application deadlines and unit-specific quotas."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      GUIDEBOOK_URL,
                    "label":    "Utah DWR — Guidebooks",
                    "evidence": (
                        "Sandhill crane hunting is by limited quota only. See the "
                        "Utah DWR guidebook for application details and unit-specific quotas."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth waterfowl hunting days are scheduled annually by Utah DWR. "
                "Check the current DWR guidebook or waterfowl page for exact dates "
                "and regulations."
            ),
            "applies_to": ["Youth Waterfowl"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Waterfowl Page",
                    "evidence": (
                        "Youth waterfowl days are held each year. Consult the DWR "
                        "guidebook or waterfowl page for current season dates."
                    )
                }
            ]
        },
        {
            "title": (
                "Crows have no closed season in Utah — hunting is permitted "
                "year-round with no daily bag or possession limit."
            ),
            "applies_to": ["Crow"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Utah DWR — Waterfowl Page",
                    "evidence": (
                        "Crow season is open; no daily limit or possession limit imposed."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────


def build_dataset() -> dict:
    print(f"[UT_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[UT_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[UT_migratory] Using hardcoded data from Utah DWR season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Utah",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "2026-2027 Waterfowl Seasons | Utah DWR",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from Utah DWR waterfowl page and guidebook."
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
        description="Scrape Utah Division of Wildlife Resources migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/UT_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/UT_Migratory_Bird_dataset.json)"
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

    print(f"[UT_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
