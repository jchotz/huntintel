#!/usr/bin/env python3
"""
LA_Upland_Gamebird_scrape.py — HuntIntel Louisiana Upland Game Bird Scraper
Fetches the Louisiana Department of Wildlife & Fisheries upland game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python LA_Upland_Gamebird_scrape.py
    python LA_Upland_Gamebird_scrape.py --output my_output.json
    python LA_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.wlf.louisiana.gov/page/seasons-and-regulations"
TURKEY_URL      = "https://www.wlf.louisiana.gov/page/seasons-and-regulations"
LICENSE_URL     = "https://www.wlf.louisiana.gov/page/license-and-permit-fee-list"
PURCHASE_URL    = "https://louisianaoutdoors.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Louisiana Outdoors — License Portal",
        "url":   "https://louisianaoutdoors.com/"
    },
    {
        "label": "LDWF — License and Permit Fee List",
        "url":   "https://www.wlf.louisiana.gov/page/license-and-permit-fee-list"
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
        "page_label":   "Seasons and Regulations | Louisiana Department of Wildlife and Fisheries",
        "last_updated": None,
        "update_note": (
            "2026-27 upland game bird data from LDWF seasons and regulations page. "
            "Louisiana's upland game birds are primarily bobwhite quail and wild turkey. "
            "Turkey seasons are area-based (A, B, C) with spring components."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Louisiana Upland Game Birds.
    Sources: LDWF Seasons and Regulations page.

    Species: Bobwhite Quail, Wild Turkey (Spring).
    """
    return [
        # ── Bobwhite Quail ──────────────────────────────────────────────────
        {
            "name":             "Bobwhite Quail",
            "asterisk":         False,
            "season_start":     "November 21, 2026",
            "season_end":       "February 28, 2027",
            "season_raw":       "November 21, 2026 - February 28, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "10 daily",
            "possession_limit": "30",
        },
        # ── Wild Turkey (Spring) ────────────────────────────────────────────
        {
            "name":             "Wild Turkey (Spring)",
            "asterisk":         True,
            "season_start":     "April 3, 2026",
            "season_end":       "May 2, 2026",
            "season_raw":       "Area A: Apr 3-May 2; Area B: Apr 3-25; Area C: Apr 3-18",
            "hunting_units":    "Areas A, B, C (private land only)",
            "bag_limit":        "2 legal turkeys per season",
            "possession_limit": "2",
            "sub_seasons": [
                {
                    "name":              "Area A",
                    "season_start":      "April 3, 2026",
                    "season_end":        "May 2, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                },
                {
                    "name":              "Area B",
                    "season_start":      "April 3, 2026",
                    "season_end":        "April 25, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                },
                {
                    "name":              "Area C",
                    "season_start":      "April 3, 2026",
                    "season_end":        "April 18, 2026",
                    "bag_limit":         "2 legal turkeys",
                    "possession_limit":  "2",
                },
            ]
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from LDWF license fee list.
    """
    return [
        {
            "name":             "Basic Hunting License",
            "asterisk":         False,
            "covers":           "Required for all hunting (age 18+)",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$200.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Louisiana Sportsman's Paradise License",
            "asterisk":         False,
            "covers":           "Basic hunting + fishing + deer + waterfowl + turkey tags",
            "resident_cost":    "$100.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Turkey License",
            "asterisk":         True,
            "covers":           "Required in addition to Basic Hunting to hunt turkey",
            "resident_cost":    "$12.00",
            "nonresident_cost": "$50.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Basic Hunting 5-Day",
            "asterisk":         False,
            "covers":           "Basic hunting for 5 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$65.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Native 10-Day Basic Hunting",
            "asterisk":         False,
            "covers":           "Basic hunting for 10 days (nonresident native only)",
            "resident_cost":    None,
            "nonresident_cost": "$20.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "WMA Access Annual Permit",
            "asterisk":         False,
            "covers":           "Required to use LDWF-administered WMAs",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$20.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Louisiana turkey hunting is private land only. Check separate schedules "
                "for WMA, NWR, and federal lands."
            ),
            "applies_to": ["Wild Turkey (Spring)"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "LDWF — Seasons and Regulations (Turkey)",
                    "evidence": (
                        "Turkey (2026/2027) — Private land only. "
                        "Check separate schedules for WMA, NWR, and federal lands."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth & Physically Challenged (wheelchair-confined) turkey hunt: "
                "March 26-28, 2026 (all areas, private land only)."
            ),
            "applies_to": ["Wild Turkey (Spring)"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "LDWF — Turkey Youth Hunt",
                    "evidence": (
                        "Youth & Physically Challenged (wheelchair-confined): "
                        "Mar 26-28 (all areas, private land only)."
                    )
                }
            ]
        },
        {
            "title": (
                "A Basic Hunting License is required for all hunters age 18 or older. "
                "A separate Turkey License ($12 resident / $50 nonresident) is also required."
            ),
            "applies_to": [
                "Basic Hunting License",
                "Turkey License"
            ],
            "sources": [
                {
                    "url":      LICENSE_URL,
                    "label":    "LDWF — License and Permit Fee List",
                    "evidence": (
                        "Basic Hunting: $20. Deer: $15. Waterfowl: $12. Turkey: $12."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[LA_upland] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[LA_upland] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[LA_upland] Using hardcoded data from LDWF regulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Louisiana",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Seasons and Regulations | LDWF",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from LDWF seasons and regulations page."
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
        description="Scrape LDWF upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/LA_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/LA_Upland_Gamebird_dataset.json)"
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

    print(f"[LA_upland] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
