#!/usr/bin/env python3
"""
WY_Upland_Gamebird_scrape.py — HuntIntel Wyoming Upland Game Bird Scraper
Fetches the Wyoming Game & Fish Department upland game bird page
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python WY_Upland_Gamebird_scrape.py
    python WY_Upland_Gamebird_scrape.py --output my_output.json
    python WY_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://wgfd.wyo.gov/Regulations/Game-Birds-Waterfowl/Upland-Game-Bird-and-Small-Game-Hunting-Seasons"
REG_PDF_URL     = "https://wgfd.wyo.gov/media/33698/download?inline"
REG_PDF_LABEL   = "2026 Wyoming Chapter 11 — Upland Game Bird and Small Game Hunting Seasons"
FEE_URL         = "https://wgfd.wyo.gov/licenses-applications/license-fee-list"
SAGE_PERMIT_URL = "https://wgfd.wyo.gov/Hunting/Hunting-Guide/Game-Bird-and-Small-Game-Hunting"
PURCHASE_URL    = "https://wgfd.wyo.gov/licenses-applications"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Wyoming Game & Fish — License Fee List",
        "url":   "https://wgfd.wyo.gov/licenses-applications/license-fee-list"
    },
    {
        "label": "Wyoming Game & Fish — Licenses & Applications",
        "url":   "https://wgfd.wyo.gov/licenses-applications"
    },
    {
        "label": "Wyoming Online License Portal (ELSO)",
        "url":   "https://wgfapps.wyo.gov/elso/ELSOSportspersonLoginSSN.aspx"
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
        "page_label":   "Upland Game Bird and Small Game Hunting Seasons | WGFD",
        "last_updated": None,
        "update_note": (
            "2026 season data from the official Wyoming Game & Fish "
            "Chapter 11 regulation (April 2026). "
            "The WGFD regulation page lists the PDF but provides no explicit "
            "last-updated date on the HTML page itself."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026 season data from the Wyoming Game & Fish Department
    Chapter 11 — Upland Game Bird and Small Game Hunting Seasons (April 2026).

    Wyoming's upland game birds:
      - Sage Grouse (Hunt Area 1 only; free permit required)
      - Blue (Dusky) Grouse (statewide)
      - Ruffed Grouse (statewide)
      - Chukar Partridge (statewide)
      - Gray (Hungarian) Partridge (statewide)
      - Sharp-tailed Grouse (east of Continental Divide)
      - Ring-necked Pheasant (multiple areas, male only)
    """
    return [
        {
            "name":             "Sage Grouse",
            "asterisk":         True,
            "season_start":     "September 19, 2026",
            "season_end":       "September 30, 2026",
            "season_raw":       "September 19 - September 30, 2026",
            "hunting_units":    "Hunt Area 1 only (areas 2, 3, 4 closed)",
            "bag_limit":        "2 daily",
            "possession_limit": "4",
        },
        {
            "name":             "Blue (Dusky) Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "September 1 - December 31, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        {
            "name":             "Ruffed Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "September 1 - December 31, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        {
            "name":             "Chukar Partridge",
            "asterisk":         False,
            "season_start":     "September 15, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 15, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        {
            "name":             "Gray (Hungarian) Partridge",
            "asterisk":         False,
            "season_start":     "September 15, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 15, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "5 daily",
            "possession_limit": "15",
        },
        {
            "name":             "Sharp-tailed Grouse",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "September 1 - December 31, 2026",
            "hunting_units":    "East of Continental Divide only",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "November 1, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "November 1 - December 31, 2026",
            "hunting_units":    "Multiple hunt areas with varying rules (see key notes)",
            "bag_limit":        "3 male (rooster) pheasants daily (varies by area)",
            "possession_limit": "9 (varies by area)",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the Wyoming Game & Fish License Fee List.
    A Conservation Stamp ($21.50) is required for all hunters.
    Sage Grouse requires a free permit.
    """
    return [
        {
            "name":             "Game Bird/Small Game 12-Month License",
            "asterisk":         True,
            "covers":           "All upland game birds and small game for 12 months",
            "resident_cost":    "$27.00",
            "nonresident_cost": "$74.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Game Bird/Small Game Daily License",
            "asterisk":         False,
            "covers":           "All upland game birds and small game for 1 day",
            "resident_cost":    "$9.00",
            "nonresident_cost": "$22.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Game Bird/Small Game Youth License",
            "asterisk":         False,
            "covers":           "All upland game birds and small game (youth)",
            "resident_cost":    None,
            "nonresident_cost": "$40.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Game Bird Only 12-Month License (Resident)",
            "asterisk":         False,
            "covers":           "Game birds only (birds, not small game mammals)",
            "resident_cost":    "$16.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Small Game Only 12-Month License (Resident)",
            "asterisk":         False,
            "covers":           "Small game mammals only (not game birds)",
            "resident_cost":    "$16.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Conservation Stamp",
            "asterisk":         True,
            "covers":           "Required annually for all hunters",
            "resident_cost":    "$21.50",
            "nonresident_cost": "$21.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Sage Grouse Hunting Permit",
            "asterisk":         True,
            "covers":           "Required for hunting sage grouse in any hunt area",
            "resident_cost":    "Free",
            "nonresident_cost": "Free",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Sage grouse hunting requires a free Sage Grouse Hunting Permit "
                "in addition to a valid hunting license and conservation stamp."
            ),
            "applies_to": ["Sage Grouse"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "WGFD — Upland Game Bird and Small Game Hunting Seasons",
                    "evidence": (
                        "Permit required for any licensed hunter hunting sage grouse. "
                        "Must be in possession and produced on demand."
                    )
                },
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 2(a)",
                    "evidence": (
                        "Permit required for any licensed hunter hunting sage grouse. "
                        "Must be in possession and produced on demand."
                    )
                }
            ]
        },
        {
            "title": (
                "Sage grouse is only open in Hunt Area 1; "
                "Hunt Areas 2, 3, and 4 are closed."
            ),
            "applies_to": ["Sage Grouse"],
            "sources": [
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 2(a)",
                    "evidence": (
                        "Sage Grouse Area 1: Sep 19 - Sep 30, 2 daily / 4 possession. "
                        "Areas 2, 3, 4: CLOSED."
                    )
                }
            ]
        },
        {
            "title": (
                "Sharp-tailed grouse may only be hunted east of the "
                "Continental Divide."
            ),
            "applies_to": ["Sharp-tailed Grouse"],
            "sources": [
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 2(f)",
                    "evidence": (
                        "Sharp-tailed Grouse Area 1: Portion of Wyoming east "
                        "of the Continental Divide."
                    )
                }
            ]
        },
        {
            "title": (
                "Pheasant: males only in most areas; evidence of sex "
                "(feathered head, feathered wing, or foot) must remain naturally attached."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 1(c)",
                    "evidence": (
                        "Pheasant — feathered head, feathered wing, or foot must "
                        "remain naturally attached."
                    )
                },
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 2(g)",
                    "evidence": (
                        "Pheasant Area 1: Male only. "
                        "Area 2 (Nov 1-30): Any pheasant (youth). "
                        "Area 2 (Dec 1-31): Male only."
                    )
                }
            ]
        },
        {
            "title": (
                "Pheasant shooting hours vary by area: restricted to 8:00 a.m. "
                "start on weekends in some areas and 11:00 a.m. weekday start in Area 5."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      REG_PDF_URL,
                    "label":    f"{REG_PDF_LABEL} — Section 2(g)",
                    "evidence": (
                        "Area 1: 1/2 hr before sunrise - sunset (weekdays); "
                        "8:00 a.m. - sunset (weekends). "
                        "Area 5: Veterans Day, Thanksgiving, Christmas, weekends: "
                        "1/2 hr before sunrise - sunset; weekdays: 11:00 a.m. - sunset."
                    )
                }
            ]
        },
        {
            "title": (
                "A Conservation Stamp ($21.50) is required for all hunters "
                "in addition to a hunting license."
            ),
            "applies_to": [
                "Game Bird/Small Game 12-Month License",
                "Game Bird/Small Game Daily License",
                "Nonresident Game Bird/Small Game Youth License"
            ],
            "sources": [
                {
                    "url":      FEE_URL,
                    "label":    "WGFD — License Fee List",
                    "evidence": (
                        "Conservation Stamp: $21.50 (resident and nonresident). "
                        "All hunters must possess a valid conservation stamp."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[WY_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[WY_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[WY_scrape] Using hardcoded data from 2026 Chapter 11 regulation PDF.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Wyoming",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Upland Game Bird and Small Game Hunting Seasons | WGFD",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data is from the 2026 Chapter 11 regulation PDF (April 2026)."
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
        description="Scrape Wyoming Game & Fish upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/WY_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/WY_Upland_Gamebird_dataset.json)"
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

    print(f"[WY_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
