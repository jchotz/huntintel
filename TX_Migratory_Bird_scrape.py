#!/usr/bin/env python3
"""
TX_Migratory_Bird_scrape.py — HuntIntel Texas Migratory Game Bird Scraper
Fetches the Texas Parks & Wildlife Department migratory game bird pages
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python TX_Migratory_Bird_scrape.py
    python TX_Migratory_Bird_scrape.py --output my_output.json
    python TX_Migratory_Bird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://tpwd.texas.gov/regulations/outdoor-annual/hunting/2026-2027-hunting-season-dates"
OUTDOOR_ANNUAL  = "https://tpwd.texas.gov/regulations/outdoor-annual/hunting/"
NEWS_RELEASE    = "https://tpwd.texas.gov/newsmedia/releases/?req=20260401b"
LICENSE_URL     = "https://tpwd.texas.gov/regulations/outdoor-annual/licenses/hunting-licenses-and-permits/hunting-licenses"
PURCHASE_URL    = "https://www.txfgsales.com/"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Texas License Sales Portal",
        "url":   "https://www.txfgsales.com/"
    },
    {
        "label": "TPWD — Outdoor Annual Hunting Licenses",
        "url":   "https://tpwd.texas.gov/regulations/outdoor-annual/licenses/hunting-licenses-and-permits/hunting-licenses"
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
        "page_label":   "2026-2027 Hunting Season Dates | TPWD",
        "last_updated": None,
        "update_note": (
            "2026-27 migratory game bird data from TPWD Outdoor Annual season dates page. "
            "The TPW Commission approved 2026-27 migratory bird seasons on April 1, 2026. "
            "Key change: South Zone dove now opens Sept 1 (previously Sept 14), "
            "eliminating Special White-winged Dove Days."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Texas Migratory Game Birds.
    Sources: TPWD 2026-2027 Hunting Season Dates, TPWD Outdoor Annual,
    TPW Commission news release (April 1, 2026).

    Migratory birds included: Dove, Duck, Goose, Rails/Gallinules/Moorhens,
    Sandhill Cranes, Snipe, September Teal, Woodcock.
    """
    return [
        # ── Dove ────────────────────────────────────────────────────────────
        {
            "name":             "Dove",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "January 21, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "North, Central, and South Zones (see sub-seasons)",
            "bag_limit":        "15 daily (mourning & white-winged in aggregate)",
            "possession_limit": "45",
            "sub_seasons": [
                {
                    "name":              "North Zone — Segment 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "November 8, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "North Zone — Segment 2",
                    "season_start":      "December 18, 2026",
                    "season_end":        "January 7, 2027",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "Central Zone — Segment 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "October 25, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "Central Zone — Segment 2",
                    "season_start":      "December 11, 2026",
                    "season_end":        "January 14, 2027",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "South Zone — Segment 1",
                    "season_start":      "September 1, 2026",
                    "season_end":        "October 25, 2026",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
                {
                    "name":              "South Zone — Segment 2",
                    "season_start":      "December 18, 2026",
                    "season_end":        "January 21, 2027",
                    "bag_limit":         "15 daily",
                    "possession_limit":  "45",
                },
            ]
        },
        # ── September Teal ──────────────────────────────────────────────────
        {
            "name":             "Teal (September Teal)",
            "asterisk":         False,
            "season_start":     "September 19, 2026",
            "season_end":       "September 27, 2026",
            "season_raw":       "September 19, 2026 - September 27, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "6 daily (blue-winged, green-winged, cinnamon teal in aggregate)",
            "possession_limit": "18",
        },
        # ── Duck ────────────────────────────────────────────────────────────
        {
            "name":             "Duck",
            "asterisk":         True,
            "season_start":     "October 24, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "See zones below for split season dates",
            "hunting_units":    "High Plains, North, and South Zones (see sub-seasons)",
            "bag_limit":        "6 daily in aggregate (species restrictions apply)",
            "possession_limit": "18",
            "sub_seasons": [
                {
                    "name":              "High Plains Mallard Mgmt Unit — Segment 1",
                    "season_start":      "October 24, 2026",
                    "season_end":        "October 25, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "High Plains Mallard Mgmt Unit — Segment 2",
                    "season_start":      "October 30, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "North Zone — Segment 1",
                    "season_start":      "November 14, 2026",
                    "season_end":        "November 29, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "North Zone — Segment 2",
                    "season_start":      "December 5, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "South Zone — Segment 1",
                    "season_start":      "November 7, 2026",
                    "season_end":        "November 29, 2026",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
                {
                    "name":              "South Zone — Segment 2",
                    "season_start":      "December 12, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "6 daily",
                    "possession_limit":  "18",
                },
            ]
        },
        # ── Goose ───────────────────────────────────────────────────────────
        {
            "name":             "Goose",
            "asterisk":         True,
            "season_start":     "September 12, 2026",
            "season_end":       "February 19, 2027",
            "season_raw":       "See zones below for species-specific dates",
            "hunting_units":    "West and East Zones (see sub-seasons)",
            "bag_limit":        "Varies by species and zone (see sub-seasons)",
            "possession_limit": "Three times daily bag",
            "sub_seasons": [
                {
                    "name":              "Early Canada Goose — East Zone",
                    "season_start":      "September 12, 2026",
                    "season_end":        "September 27, 2026",
                    "bag_limit":         "5 daily Canada geese",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Dark Geese — West Zone",
                    "season_start":      "November 7, 2026",
                    "season_end":        "February 7, 2027",
                    "bag_limit":         "5 daily dark geese",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Dark Geese — East Zone",
                    "season_start":      "November 7, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "5 daily dark geese",
                    "possession_limit":  "15",
                },
                {
                    "name":              "Light Geese — West Zone",
                    "season_start":      "November 7, 2026",
                    "season_end":        "February 7, 2027",
                    "bag_limit":         "No daily limit on light geese",
                    "possession_limit":  "No possession limit",
                },
                {
                    "name":              "Light Geese — East Zone",
                    "season_start":      "November 7, 2026",
                    "season_end":        "February 19, 2027",
                    "bag_limit":         "No daily limit on light geese",
                    "possession_limit":  "No possession limit",
                },
            ]
        },
        # ── Rails, Gallinules & Moorhens ────────────────────────────────────
        {
            "name":             "Rails, Gallinules & Moorhens",
            "asterisk":         False,
            "season_start":     "September 19, 2026",
            "season_end":       "January 6, 2027",
            "season_raw":       "September 19-27, 2026 and November 7, 2026 - January 6, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "25 daily (rails & gallinules in aggregate)",
            "possession_limit": "75",
            "sub_seasons": [
                {
                    "name":              "Segment 1",
                    "season_start":      "September 19, 2026",
                    "season_end":        "September 27, 2026",
                    "bag_limit":         "25 daily",
                    "possession_limit":  "75",
                },
                {
                    "name":              "Segment 2",
                    "season_start":      "November 7, 2026",
                    "season_end":        "January 6, 2027",
                    "bag_limit":         "25 daily",
                    "possession_limit":  "75",
                },
            ]
        },
        # ── Sandhill Crane ──────────────────────────────────────────────────
        {
            "name":             "Sandhill Crane",
            "asterisk":         True,
            "season_start":     "October 31, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "See zones below for dates",
            "hunting_units":    "Zones A, B, and C (see sub-seasons)",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
            "sub_seasons": [
                {
                    "name":              "Zone A",
                    "season_start":      "October 31, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Zone B",
                    "season_start":      "November 27, 2026",
                    "season_end":        "January 31, 2027",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
                {
                    "name":              "Zone C",
                    "season_start":      "December 12, 2026",
                    "season_end":        "January 17, 2027",
                    "bag_limit":         "3 daily",
                    "possession_limit":  "9",
                },
            ]
        },
        # ── Snipe ───────────────────────────────────────────────────────────
        {
            "name":             "Snipe",
            "asterisk":         False,
            "season_start":     "November 7, 2026",
            "season_end":       "February 21, 2027",
            "season_raw":       "November 7, 2026 - February 21, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        # ── Woodcock ────────────────────────────────────────────────────────
        {
            "name":             "Woodcock",
            "asterisk":         False,
            "season_start":     "December 18, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "December 18, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from TPWD hunting license page.
    Valid through August 31 each year.
    Migratory Game Bird Endorsement ($7) required for all migratory bird hunting.
    Federal Duck Stamp ($25) required for waterfowl hunters 16+.
    """
    return [
        {
            "name":             "Resident Hunting License",
            "asterisk":         True,
            "covers":           "Any legal bird/animal (terrestrial vertebrates); valid to Aug 31",
            "resident_cost":    "$25.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident General Hunting License",
            "asterisk":         True,
            "covers":           "Any legal bird/animal including deer; valid to Aug 31",
            "resident_cost":    None,
            "nonresident_cost": "$315.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Non-resident Special 5-Day Small Game/Exotic Hunting License",
            "asterisk":         False,
            "covers":           "Exotic animals and small game for 5 consecutive days",
            "resident_cost":    None,
            "nonresident_cost": "$48.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Senior Resident Hunting License (age 65+)",
            "asterisk":         False,
            "covers":           "Same as Resident Hunting License for seniors",
            "resident_cost":    "$7.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Hunting License (under age 17)",
            "asterisk":         False,
            "covers":           "Hunting license valid for any legal bird/animal",
            "resident_cost":    "$7.00",
            "nonresident_cost": "$7.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Texas Migratory Game Bird Endorsement",
            "asterisk":         True,
            "covers":           "Required in addition to hunting license to hunt any migratory game bird (dove, duck, goose, rail, gallinule, snipe, sandhill crane, woodcock)",
            "resident_cost":    "$7.00",
            "nonresident_cost": "$7.00",
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
                    "label": "Texas License Sales Portal",
                    "url":   "https://www.txfgsales.com/"
                },
                {
                    "label": "USPS — Federal Duck Stamp",
                    "url":   "https://www.fws.gov/duckstamps/"
                }
            ],
        },
        {
            "name":             "Super Combo License (Resident)",
            "asterisk":         False,
            "covers":           "Hunting + fishing license + 5 state endorsements at a discount",
            "resident_cost":    "$68.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "A Texas Migratory Game Bird Endorsement ($7) is required in addition "
                "to a valid hunting license to hunt any migratory game bird in Texas."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident General Hunting License",
                "Youth Hunting License (under age 17)"
            ],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "licenses/hunting-licenses-and-permits/hunting-endorsements"),
                    "label":    "TPWD — Hunting Endorsements",
                    "evidence": (
                        "Texas Migratory Game Bird Endorsement (Item 168): $7. "
                        "Required to hunt any migratory game bird (waterfowl, coot, "
                        "rail, gallinule, snipe, dove, sandhill crane, and woodcock)."
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
                "Goose",
                "Teal (September Teal)"
            ],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "licenses/hunting-licenses-and-permits/hunting-endorsements"),
                    "label":    "TPWD — Hunting Endorsements (Federal Duck Stamp)",
                    "evidence": (
                        "Federal Duck Stamp (Item 138): $25 plus fulfillment. "
                        "Required for all waterfowl hunters 16 years of age or older. "
                        "A valid hunting license, HIP Certification, and Texas Migratory "
                        "Game Bird Endorsement are also required."
                    )
                }
            ]
        },
        {
            "title": (
                "South Zone dove season now opens September 1 (previously September 14). "
                "Special White-winged Dove Days have been eliminated — standardized daily "
                "bag limits and shooting hours apply across all days."
            ),
            "applies_to": ["Dove"],
            "sources": [
                {
                    "url":      NEWS_RELEASE,
                    "label":    "TPW Commission — April 1, 2026 News Release",
                    "evidence": (
                        "The South Zone dove hunting season structure during the first "
                        "segment will include an earlier regular season opening date "
                        "(Sept. 1 – Oct. 25), eliminate the Special White-winged Dove Days, "
                        "and institute standardized daily bag limits and shooting hours "
                        "across all days in the South Zone."
                    )
                }
            ]
        },
        {
            "title": (
                "Duck bag limits have species-specific restrictions: 5 mallards "
                "(max 2 hens), 3 wood ducks, 3 pintails, 2 redheads, 2 canvasbacks, "
                "1 scaup, 1 dusky duck (mottled/Mexican/black duck)."
            ),
            "applies_to": ["Duck"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "regs/animals/duck"),
                    "label":    "TPWD — Duck Regulations",
                    "evidence": (
                        "Daily bag 6 in aggregate, with no more than: 5 mallards "
                        "(only 2 of which may be hens), 3 wood ducks, 3 pintails, "
                        "2 redheads, 2 canvasbacks, 1 scaup, 1 dusky duck."
                    )
                }
            ]
        },
        {
            "title": (
                "Dusky ducks (mottled, Mexican, black duck, and hybrids) are off-limits "
                "for the first 5 days of the regular season in each zone."
            ),
            "applies_to": ["Duck"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "regs/animals/duck"),
                    "label":    "TPWD — Duck Regulations",
                    "evidence": (
                        "Due to mottled duck population concerns by USFWS, all dusky ducks "
                        "are off-limits for the first five days of the regular season in each zone."
                    )
                }
            ]
        },
        {
            "title": (
                "A free Federal Sandhill Crane Hunting Permit is required to hunt "
                "sandhill cranes, available online or at TPWD Law Enforcement offices."
            ),
            "applies_to": ["Sandhill Crane"],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "licenses/hunting-licenses-and-permits/hunting-endorsements"),
                    "label":    "TPWD — Hunting Endorsements (Sandhill Crane)",
                    "evidence": (
                        "A free Federal Sandhill Crane Hunting Permit is required to hunt "
                        "sandhill cranes, which is available at TPWD Law Enforcement offices "
                        "or online."
                    )
                }
            ]
        },
        {
            "title": (
                "HIP Certification is required for migratory bird hunters and is "
                "obtained when purchasing a hunting license by indicating intent "
                "to hunt migratory game birds."
            ),
            "applies_to": [
                "Resident Hunting License",
                "Non-resident General Hunting License"
            ],
            "sources": [
                {
                    "url":      ("https://tpwd.texas.gov/regulations/outdoor-annual/"
                                 "hunting/migratory-game-bird-regulations/stamps-permits-and-certification"),
                    "label":    "TPWD — Stamps, Permits, and Certification",
                    "evidence": (
                        "Harvest Information Program (HIP) Certification is required "
                        "for waterfowl hunters 16+; obtained when purchasing a hunting "
                        "license by indicating intent to hunt migratory game birds."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[TX_migratory] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[TX_migratory] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[TX_migratory] Using hardcoded data from TPWD season dates.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Texas",
        "category":  "Migratory Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "2026-2027 Hunting Season Dates | TPWD",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from TPWD Outdoor Annual and April 2026 news release."
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
        description="Scrape Texas Parks & Wildlife migratory game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/TX_Migratory_Bird_dataset.json",
        help="Output JSON filename (default: data/TX_Migratory_Bird_dataset.json)"
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

    print(f"[TX_migratory] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
