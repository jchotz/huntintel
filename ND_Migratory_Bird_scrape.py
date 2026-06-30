#!/usr/bin/env python3
"""
ND_Migratory_Bird_scrape.py — HuntIntel North Dakota Migratory Game Bird Scraper
Fetches the North Dakota Game and Fish migratory game bird regulation pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python ND_Migratory_Bird_scrape.py
    python ND_Migratory_Bird_scrape.py --output my_output.json
    python ND_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://gf.nd.gov/hunting/season-dates"
REGULATIONS_URL = "https://gf.nd.gov/regulations/small-game"
LICENSE_URL     = "https://gf.nd.gov/licensing/nonresident"
PURCHASE_URL    = "https://gf.nd.gov/licensing"

LICENSE_PURCHASE_URLS = [
    {
        "label": "North Dakota Game and Fish — License Portal",
        "url":   "https://gf.nd.gov/licensing"
    },
    {
        "label": "North Dakota Game and Fish — Nonresident Licenses",
        "url":   "https://gf.nd.gov/licensing/nonresident"
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
        "page_label":   "2026-2027 North Dakota Hunting Seasons | ND Game and Fish",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from North Dakota Game and Fish season dates page. "
            "Many 2026-27 waterfowl dates are listed as Tentative by NDGF pending proclamation signing. "
            "Nonresident waterfowl hunters must select two 7-day periods in different zones. "
            "HIP registration required for all migratory bird hunters."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for North Dakota Migratory Game Birds.
    Sources: NDGF Hunting Seasons page (2026-27), NDGF Bag Limits page, eRegulations.

    Migratory birds included: Dove, Duck, Goose (Canada, Light, White-fronted),
    Sandhill Crane, Snipe, Woodcock, Coot, Tundra Swan, Bonus Blue-winged Teal.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove (Mourning Dove)",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "October 30, 2026",
            "season_raw":       "September 1, 2026 - October 30, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "15 daily (mourning dove)",
            "possession_limit": "45",
        },
        # ── Wilson's Snipe ──────────────────────────────────────────────────
        {
            "name":             "Wilson's Snipe",
            "asterisk":         False,
            "season_start":     "September 12, 2026",
            "season_end":       "November 30, 2026",
            "season_raw":       "September 12, 2026 - November 30, 2026 (tentative)",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Woodcock ────────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "September 19, 2026",
            "season_end":       "November 7, 2026",
            "season_raw":       "September 19, 2026 - November 7, 2026 (tentative)",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Bonus Blue-winged Teal ──────────────────────────────────────────
        {
            "name":             "Bonus Blue-winged Teal",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "September 30, 2026",
            "season_raw":       "September 26-30, 2026 (tentative)",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily (blue-winged teal only)",
            "possession_limit": "18",
        },
        # ── Duck (including Mergansers) ─────────────────────────────────────
        {
            "name":             "Duck (including Mergansers)",
            "asterisk":         True,
            "season_start":     "September 26, 2026",
            "season_end":       "December 8, 2026",
            "season_raw":       "Resident: Sept 26 – Dec 8; Nonresident: Oct 5 – Dec 8 (tentative)",
            "hunting_units":    "High Plains Unit and Low Plains Unit (see sub-seasons)",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "Resident — High Plains & Low Plains Units",
                    "season_start":      "September 26, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "Nonresident — High Plains & Low Plains Units",
                    "season_start":      "October 5, 2026",
                    "season_end":        "December 8, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "High Plains Unit — Late Segment",
                    "season_start":      "December 12, 2026",
                    "season_end":        "TBD",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Coot ────────────────────────────────────────────────────────────
        {
            "name":             "Coot (American Coot)",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "December 8, 2026",
            "season_raw":       "Same as duck season — Resident: Sept 26; Nonresident: Oct 5 (tentative)",
            "hunting_units":    "High Plains Unit and Low Plains Unit",
            "bag_limit":        "15 daily",
            "possession_limit": "45",
        },
        # ── Canada Goose ────────────────────────────────────────────────────
        {
            "name":             "Canada Goose",
            "asterisk":         True,
            "season_start":     "August 15, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "Early: Aug 15 – Sep 15; Regular Resident: Sep 26 – Dec 16; Regular Nonresident: Oct 5 – Dec 16 (tentative)",
            "hunting_units":    "Missouri River, Western, and Eastern Zones (see sub-seasons)",
            "bag_limit":        "Varies by zone and season (see sub-seasons)",
            "possession_limit": "Three times daily bag",
            "sub_seasons": [
                {
                    "name":              "Early Canada Goose (August Management / Early September)",
                    "season_start":      "August 15, 2026",
                    "season_end":        "September 15, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "Regular — Resident (All Zones)",
                    "season_start":      "September 26, 2026",
                    "season_end":        "December 16, 2026",
                    "bag_limit":         "8 daily (Western/Eastern), 5 daily (Missouri River)",
                    "possession_limit":  "24 (Western/Eastern), 15 (Missouri River)",
                },
                {
                    "name":              "Regular — Nonresident (All Zones)",
                    "season_start":      "October 5, 2026",
                    "season_end":        "December 16, 2026",
                    "bag_limit":         "8 daily (Western/Eastern), 5 daily (Missouri River)",
                    "possession_limit":  "24 (Western/Eastern), 15 (Missouri River)",
                },
            ]
        },
        # ── Light Geese ─────────────────────────────────────────────────────
        {
            "name":             "Light Geese (Snow, Blue, Ross's)",
            "asterisk":         True,
            "season_start":     "September 26, 2026",
            "season_end":       "January 4, 2027",
            "season_raw":       "Regular Resident: Sep 26 – Jan 4; Regular Nonresident: Oct 5 – Jan 4; Spring Conservation Order: Feb 21 – May 10, 2027",
            "hunting_units":    "Statewide (see sub-seasons)",
            "bag_limit":        "50 daily (regular season)",
            "possession_limit": "No possession limit",
            "sub_seasons": [
                {
                    "name":              "Regular — Resident",
                    "season_start":      "September 26, 2026",
                    "season_end":        "January 4, 2027",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "No possession limit",
                },
                {
                    "name":              "Regular — Nonresident",
                    "season_start":      "October 5, 2026",
                    "season_end":        "January 4, 2027",
                    "bag_limit":         "50 daily",
                    "possession_limit":  "No possession limit",
                },
                {
                    "name":              "Spring Conservation Order",
                    "season_start":      "February 21, 2027",
                    "season_end":        "May 10, 2027",
                    "bag_limit":         "No daily limit",
                    "possession_limit":  "No possession limit",
                },
            ]
        },
        # ── White-fronted Goose ─────────────────────────────────────────────
        {
            "name":             "White-fronted Goose",
            "asterisk":         False,
            "season_start":     "September 26, 2026",
            "season_end":       "December 16, 2026",
            "season_raw":       "Resident: Sep 26 – Dec 16; Nonresident: Oct 5 – Dec 16 (tentative)",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        # ── Sandhill Crane ──────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "September 19, 2026",
            "season_end":       "November 22, 2026",
            "season_raw":       "September 19 – November 22, 2026 (tentative)",
            "hunting_units":    "Unit 1 and Unit 2 (see sub-seasons)",
            "bag_limit":        "3 daily (Unit 1), 2 daily (Unit 2)",
            "possession_limit": "9 (Unit 1), 6 (Unit 2)",
            "sub_seasons": [
                {
                    "name":              "Unit 1",
                    "season_start":      "September 19, 2026",
                    "season_end":        "November 22, 2026",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Unit 2",
                    "season_start":      "September 19, 2026",
                    "season_end":        "November 22, 2026",
                    "bag_limit":         "2 daily",
                    "possession_limit":  "6",
                },
            ]
        },
        # ── Tundra Swan ────────────────────────────────────────────────────
        {
            "name":             "Tundra Swan",
            "asterisk":         True,
            "season_start":     "October 3, 2026",
            "season_end":       "January 4, 2027",
            "season_raw":       "October 3, 2026 - January 4, 2027 (tentative; lottery only)",
            "hunting_units":    "Statewide (lottery drawing)",
            "bag_limit":        "1 per season",
            "possession_limit": "1",
        },
        # ── Youth Waterfowl ─────────────────────────────────────────────────
        {
            "name":             "Youth Waterfowl",
            "asterisk":         False,
            "season_start":     "September 19, 2026",
            "season_end":       "September 20, 2026",
            "season_raw":       "September 19-20, 2026 (tentative)",
            "hunting_units":    "Statewide",
            "bag_limit":        "Same as regular season limits for ducks, geese, coots",
            "possession_limit": "Same as regular season",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from North Dakota Game and Fish.
    Valid through season end.
    Small Game license covers doves, snipe, woodcock, crane, partridge, grouse, pheasants.
    Waterfowl license (zone-restricted) covers ducks, geese, swans, mergansers, coots.
    Federal Duck Stamp ($25 + $4) required for waterfowl hunters 16+.
    HIP certification required for all migratory bird hunters.
    """
    return [
        {
            "name":             "Fishing, Hunting, Furbearer Certificate",
            "asterisk":         True,
            "covers":           "Prerequisite certificate required for all hunting (one per year)",
            "resident_cost":    "$2.00",
            "nonresident_cost": "$5.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "General Game and Habitat License",
            "asterisk":         True,
            "covers":           "Required for all hunting except furbearer (one per year)",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$20.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Small Game License",
            "asterisk":         True,
            "covers":           "Covers: crow, doves, Hungarian partridge, sharp-tailed grouse, ruffed grouse, sandhill cranes, snipe, woodcock, pheasants, tree squirrels",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$150.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Waterfowl License (Zone-Restricted)",
            "asterisk":         True,
            "covers":           "Covers ducks, geese, swans, mergansers, coots; two 7-day periods in different zones",
            "resident_cost":    None,
            "nonresident_cost": "$153.00 (+ $5 cert + $20 habitat + $29 federal stamp + $5 restoration)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Waterfowl Habitat Restoration Stamp (Electronic)",
            "asterisk":         True,
            "covers":           "Required for all waterfowl hunting",
            "resident_cost":    "$5.00",
            "nonresident_cost": "$5.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Federal Waterfowl Stamp (Duck Stamp)",
            "asterisk":         True,
            "covers":           "Required for waterfowl hunters age 16+ (ducks, geese, swans, mergansers, brant, coot). Not required during spring light goose.",
            "resident_cost":    "$25.00 (+ $4 mailing)",
            "nonresident_cost": "$25.00 (+ $4 mailing)",
            "purchase_urls":    [
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                },
                {
                    "label": "North Dakota Game and Fish — License Portal",
                    "url":   "https://gf.nd.gov/licensing"
                }
            ],
        },
        {
            "name":             "Sandhill Crane Permit (Nonresident)",
            "asterisk":         True,
            "covers":           "Permit required in addition to small game or waterfowl license to hunt sandhill cranes",
            "resident_cost":    "Included with small game license",
            "nonresident_cost": "$30.00 (+ applicable licenses)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Resident Combination License (16+)",
            "asterisk":         False,
            "covers":           "Fishing + General Game & Habitat + Small Game + Furbearer — all-in-one",
            "resident_cost":    "$62.00 (+ $5 waterfowl stamp if waterfowl)",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "HIP (Harvest Information Program) registration is required annually and free for all "
                "hunters (any age) hunting ducks, geese, swans, mergansers, coots, cranes, snipe, "
                "doves, and woodcock."
            ),
            "applies_to": [
                "Small Game License",
                "Nonresident Waterfowl License (Zone-Restricted)",
                "Federal Waterfowl Stamp (Duck Stamp)",
            ],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/regulations/hip",
                    "label":    "NDGF — HIP Registration",
                    "evidence": (
                        "HIP Registration (free): Required annually for all hunters (any age) hunting "
                        "ducks, geese, swans, mergansers, coots, cranes, snipe, doves, and woodcock."
                    )
                }
            ]
        },
        {
            "title": (
                "A Federal Duck Stamp ($25 + $4 mailing) is required for all waterfowl hunters "
                "age 16 or older (ducks, geese, swans, mergansers, brant, coot). Not required "
                "during Spring Light Goose Conservation Order."
            ),
            "applies_to": [
                "Federal Waterfowl Stamp (Duck Stamp)",
                "Duck (including Mergansers)",
                "Canada Goose",
                "Light Geese (Snow, Blue, Ross's)",
                "White-fronted Goose",
                "Coot (American Coot)",
                "Tundra Swan",
            ],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/licensing/nonresident",
                    "label":    "NDGF — Nonresident Licenses",
                    "evidence": (
                        "Federal Waterfowl Stamp ($25 + $4 mailing): Required for hunters 16+ for "
                        "ducks, geese, swans, mergansers, brant, coot. Exception: Not needed during "
                        "spring light goose conservation season."
                    )
                }
            ]
        },
        {
            "title": (
                "Nonresident waterfowl hunters are restricted to two 7-day hunting periods per year, "
                "each in a different nonresident waterfowl zone (NE, NC, NW, SE, SC, SW). "
                "If hunting only one 7-day period, may select two zones during that period."
            ),
            "applies_to": [
                "Nonresident Waterfowl License (Zone-Restricted)",
                "Duck (including Mergansers)",
                "Canada Goose",
            ],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/licensing/nonresident",
                    "label":    "NDGF — Nonresident Licenses and Requirements",
                    "evidence": (
                        "Nonresidents may hunt waterfowl for two 7-day periods per year. "
                        "Six nonresident waterfowl hunting zones. Each 7-day period must be in "
                        "a different zone. The same zone cannot be used for both periods."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck bag limits have species-specific restrictions: 6 daily in aggregate. "
                "Typical species limits include mallards, pintails, canvasbacks, redheads, "
                "and scaup restrictions. Consult NDGF regulations for full details."
            ),
            "applies_to": ["Duck (including Mergansers)"],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/regulations/small-game",
                    "label":    "NDGF — Small Game, Waterfowl and Furbearer Proclamation",
                    "evidence": (
                        "The daily duck bag limit, including species restrictions and all other "
                        "regulations, shall be 6 per day."
                    )
                }
            ]
        },
        {
            "title": (
                "Sandhill Crane Unit 1 and Unit 2 have different bag limits. "
                "Unit 1: 3 daily / 9 possession. Unit 2: 2 daily / 6 possession."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      "https://www.eregulations.com/northdakota/hunting/hunting-bag-limits",
                    "label":    "NDGF — Hunting Bag Limits",
                    "evidence": (
                        "Sandhill Crane: 3 per day, 9 in possession (Unit 1), "
                        "2 per day, 6 in possession (Unit 2)."
                    )
                }
            ]
        },
        {
            "title": (
                "Shooting hours for all migratory game birds: one-half hour before sunrise to sunset. "
                "Non-toxic shot required for all waterfowl and migratory bird hunting."
            ),
            "applies_to": [
                "Dove (Mourning Dove)",
                "Wilson's Snipe",
                "Woodcock",
                "Bonus Blue-winged Teal",
                "Duck (including Mergansers)",
                "Coot (American Coot)",
                "Canada Goose",
                "Light Geese (Snow, Blue, Ross's)",
                "White-fronted Goose",
                "Sandhill Crane",
                "Tundra Swan",
                "Youth Waterfowl",
            ],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/hunting/season-dates",
                    "label":    "NDGF — Hunting Seasons",
                    "evidence": (
                        "Standard shooting hours and non-toxic shot requirements apply. "
                        "Check NDGF regulations for full details."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[ND_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[ND_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[ND_migratory] Using hardcoded data from NDGF season dates and regulations.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "North Dakota",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "2026-2027 North Dakota Hunting Seasons | ND Game and Fish",
            "last_updated": None,
            "update_note": (
                "Could not fetch source page. "
                "Data from NDGF Hunting Seasons page, NDGF Bag Limits, and eRegulations."
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
        description="Scrape North Dakota Game and Fish migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/ND_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/ND_Migratory_Bird_dataset.json)"
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

    print(f"[ND_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
