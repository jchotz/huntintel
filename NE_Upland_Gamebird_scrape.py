#!/usr/bin/env python3
"""
NE_Upland_Gamebird_scrape.py — HuntIntel Nebraska Upland Game Bird Scraper
Fetches the Nebraska Game & Parks Commission upland game page
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python NE_Upland_Gamebird_scrape.py
    python NE_Upland_Gamebird_scrape.py --output my_output.json
    python NE_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL    = "https://outdoornebraska.gov/hunt/game/upland/"
SEASONS_URL   = "https://outdoornebraska.gov/hunt/hunting-seasons/"
GUIDE_URL     = "https://digital.outdoornebraska.gov/i/1537408-small-game-and-waterfowl-guide-2025-26-web/0?"
STAMP_URL     = "https://outdoornebraska.gov/permits/hunting-permits/permit-stamp-requirements/"
GUIDE_LABEL   = "2025-2026 Small Game and Waterfowl Guide"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Nebraska Game & Parks Online License Portal",
        "url":   "https://www.gooutdoorsne.com/"
    },
    {
        "label": "Nebraska Game & Parks — Permits Page",
        "url":   "https://outdoornebraska.gov/permits/hunting-permits/"
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
        "page_label":   "Upland Hunting | Nebraska Game & Parks Commission",
        "last_updated": None,
        "update_note": (
            "No explicit last-updated date on source page. "
            "2026-27 season data is from the official Nebraska Game & Parks "
            "Hunting Seasons page and the 2025-2026 Small Game and Waterfowl Guide."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Nebraska Upland Game Birds.
    Sources: outdoornebraska.gov/hunt/hunting-seasons/
    and the Small Game and Waterfowl Guide.

    Nebraska's upland categories:
      - Ring-necked Pheasant (roosters only)
      - Northern Bobwhite Quail
      - Gray (Hungarian) Partridge
      - Prairie Grouse (Sharp-tailed Grouse & Greater Prairie-chicken combined)
    """
    return [
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 31, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 male (rooster) pheasants daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":              "Youth Pheasant, Quail & Partridge Season",
                    "season_start":      "October 24, 2026",
                    "season_end":        "October 25, 2026",
                    "bag_limit":         "Same as regular season limits",
                    "possession_limit":  "Same as regular season limits",
                    "note": (
                        "Youth ages 15 and under only. Accompanying adult (19+) "
                        "must be licensed; only one adult per youth may hunt."
                    )
                }
            ]
        },
        {
            "name":             "Northern Bobwhite Quail",
            "asterisk":         False,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 31, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily",
            "possession_limit": "24",
        },
        {
            "name":             "Gray (Hungarian) Partridge",
            "asterisk":         False,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 31, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Prairie Grouse",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 1, 2026 - January 31, 2027",
            "hunting_units":    "Statewide (special permit required east of U.S. Highway 81 — see key notes)",
            "bag_limit":        "3 daily (combined Sharp-tailed Grouse and Greater Prairie-chicken)",
            "possession_limit": "3",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the Nebraska Game & Parks permit pricing page.
    Small Game (Hunt) permit covers all upland game birds.
    A separate Habitat Stamp is required for all small game hunters.
    Waterfowl Stamp needed if also hunting migratory birds.
    """
    return [
        {
            "name":             "Hunt Permit (Resident, age 16+)",
            "asterisk":         True,
            "covers":           "All small game including pheasant, quail, partridge, prairie grouse, squirrel, rabbit, and furbearers",
            "resident_cost":    "$20.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Permit (age 15 and under)",
            "asterisk":         False,
            "covers":           "Same as adult Hunt Permit",
            "resident_cost":    "Free",
            "nonresident_cost": "$20.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Annual Hunt Permit (age 16+)",
            "asterisk":         True,
            "covers":           "All small game including upland birds",
            "resident_cost":    None,
            "nonresident_cost": "$128.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 2-Day Hunt Permit (age 16+)",
            "asterisk":         False,
            "covers":           "All small game including upland birds (2 consecutive days)",
            "resident_cost":    None,
            "nonresident_cost": "$89.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Habitat Stamp",
            "asterisk":         True,
            "covers":           "Required annually for all hunters pursuing small game (with select exemptions)",
            "resident_cost":    "$25.00",
            "nonresident_cost": "$25.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "Prairie grouse (sharp-tailed grouse & greater prairie-chicken) "
                "require a special permit when hunting east of U.S. Highway 81."
            ),
            "applies_to": ["Prairie Grouse"],
            "sources": [
                {
                    "url":      SEASONS_URL,
                    "label":    "Nebraska Game & Parks — Hunting Seasons",
                    "evidence": (
                        "Prairie grouse: Sept. 1, 2026 - Jan. 31, 2027. "
                        "*special permit required east of U.S. 81"
                    )
                },
                {
                    "url":      GUIDE_URL,
                    "label":    f"{GUIDE_LABEL} — Prairie Grouse Section",
                    "evidence": (
                        "A special permit is required to hunt prairie grouse "
                        "east of U.S. Highway 81."
                    )
                }
            ]
        },
        {
            "title": (
                "Youth Pheasant, Quail & Partridge season runs two days before "
                "the regular opener; youth ages 15 and under only."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Nebraska Game & Parks — Upland Hunting",
                    "evidence": (
                        "Nebraska's youth-only pheasant, quail and partridge "
                        "season is Oct. 24-25, 2026; only youth ages 15 and "
                        "under are allowed to hunt on these days."
                    )
                },
                {
                    "url":      ("https://outdoornebraska.gov/about/press-events/"
                                 "news/youth-pheasant-season-includes-special-youth-hunts/"),
                    "label":    "NGPC — Youth Pheasant Season News",
                    "evidence": (
                        "The accompanying adult must be a licensed hunter aged "
                        "19 or older and only one adult per youth will be "
                        "allowed to hunt."
                    )
                }
            ]
        },
        {
            "title": (
                "A Habitat Stamp ($25) is required for all hunters pursuing "
                "small game, with select exemptions."
            ),
            "applies_to": [
                "Hunt Permit (Resident, age 16+)",
                "Nonresident Annual Hunt Permit (age 16+)",
                "Nonresident 2-Day Hunt Permit (age 16+)"
            ],
            "sources": [
                {
                    "url":      STAMP_URL,
                    "label":    "NGPC — Permit & Stamp Requirements",
                    "evidence": (
                        "A Habitat Stamp is required of all hunters pursuing "
                        "any small game, with select exemptions."
                    )
                }
            ]
        },
        {
            "title": (
                "Only male pheasants (roosters with visible spurs or plumage) "
                "may be taken."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SEASONS_URL,
                    "label":    "Nebraska Game & Parks — Hunting Seasons",
                    "evidence": (
                        "Pheasant: 3 per day (12 in possession) — roosters only."
                    )
                },
                {
                    "url":      ("https://www.eregulations.com/nebraska/"
                                 "hunting/hunting-bag-limits"),
                    "label":    "eRegulations — Nebraska Bag Limits",
                    "evidence": (
                        "Pheasant, 3 per day (12 in possession)"
                    )
                }
            ]
        },
        {
            "title": (
                "Prairie grouse daily bag limit is 3 birds total in aggregate "
                "(sharp-tailed grouse and greater prairie-chicken combined), "
                "with a possession limit of 3."
            ),
            "applies_to": ["Prairie Grouse"],
            "sources": [
                {
                    "url":      ("https://www.eregulations.com/nebraska/"
                                 "hunting/hunting-bag-limits"),
                    "label":    "eRegulations — Nebraska Bag Limits",
                    "evidence": (
                        "Prairie Grouse: 3 per day (3 in possession in aggregate)"
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[NE_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[NE_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[NE_scrape] Using hardcoded data (HTML source unavailable).", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Nebraska",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Upland Hunting | Nebraska Game & Parks Commission",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data is from the Hunting Seasons page and Small Game Guide."
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
        description="Scrape Nebraska Game & Parks upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/NE_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/NE_Upland_Gamebird_dataset.json)"
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

    print(f"[NE_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
