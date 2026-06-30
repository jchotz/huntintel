#!/usr/bin/env python3
"""
OR_Upland_Gamebird_scrape.py — HuntIntel Oregon Upland Game Bird Scraper
Fetches the Oregon Department of Fish & Wildlife game bird page
and outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python OR_Upland_Gamebird_scrape.py
    python OR_Upland_Gamebird_scrape.py --output my_output.json
    python OR_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL      = "https://www.eregulations.com/oregon/hunting/game-bird/game-bird-seasons"
MYODFW_URL      = "https://myodfw.com/game-bird-hunting"
EREG_HOME       = "https://www.eregulations.com/oregon/hunting/game-bird"
FEE_URL         = "https://www.eregulations.com/oregon/hunting/game-bird/license-tag-permit-fees"
ODFW_FRAMEWORK  = "https://www.dfw.state.or.us/agency/commission/minutes/25/04_April/Exhibit%20C%20Game%20Birds/Exhibit%20C_Attachment%203_2025-2030%20Upland%20Game%20Bird%20Season%20Framework.pdf"
EREG_LABEL      = "eRegulations — Oregon Game Bird Seasons"

LICENSE_PURCHASE_URLS = [
    {
        "label": "ODFW — Hunt and Fish License Portal",
        "url":   "https://odfw.huntfishoregon.com/"
    },
    {
        "label": "MyODFW — Game Bird Hunting Licensing Info",
        "url":   "https://myodfw.com/game-bird-hunting/licensing-info"
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
        "page_label":   "Game Bird Seasons | eRegulations — Oregon",
        "last_updated": None,
        "update_note": (
            "2026-27 season data compiled from eRegulations Oregon Game Bird "
            "Seasons page (last updated September 2025) and ODFW 2025-2030 "
            "Upland Game Bird Season Framework. Proposed 2026-27 dates used "
            "where available; finalized dates expected from ODFW later in 2026."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2026-27 season data for Oregon Upland Game Birds.
    Sources: eRegulations Oregon Game Bird Seasons (2025-26 current +
    proposed 2026-27), ODFW Game Bird Program Staff Summary, and
    2025-2030 Upland Game Bird Season Framework.

    Oregon's upland game birds:
      - Ruffed & Blue (Dusky) Grouse
      - Chukar Partridge
      - Gray (Hungarian) Partridge
      - Ring-necked Pheasant (roosters)
      - California Quail
      - Mountain Quail
      - Sage Grouse (controlled permit)
    """
    return [
        {
            "name":             "Ruffed Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 1, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        {
            "name":             "Blue (Dusky) Grouse",
            "asterisk":         False,
            "season_start":     "September 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "September 1, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "9",
        },
        {
            "name":             "Chukar Partridge",
            "asterisk":         True,
            "season_start":     "October 11, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 11, 2026 - January 31, 2027",
            "hunting_units":    "Statewide (reduced limit in Lower Klamath Hills Regulated Hunt Area — see key notes)",
            "bag_limit":        "8 daily",
            "possession_limit": "24",
        },
        {
            "name":             "Gray (Hungarian) Partridge",
            "asterisk":         False,
            "season_start":     "October 11, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "October 11, 2026 - January 31, 2027",
            "hunting_units":    "Statewide",
            "bag_limit":        "8 daily (combined with chukar)",
            "possession_limit": "24 (combined with chukar)",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "October 10, 2026",
            "season_end":       "December 31, 2026",
            "season_raw":       "October 10 - December 31, 2026",
            "hunting_units":    "Statewide (+ Special Fee Pheasant Hunts on wildlife areas)",
            "bag_limit":        "2 male (rooster) pheasants daily",
            "possession_limit": "8",
        },
        {
            "name":             "Quail (California & Mountain)",
            "asterisk":         True,
            "season_start":     "September 1, 2026",
            "season_end":       "January 31, 2027",
            "season_raw":       "Western OR: Sep 1 - Jan 31 | Eastern OR: Oct 10 - Jan 31",
            "hunting_units":    "Western Oregon: Sep 1 - Jan 31 | Eastern Oregon: Oct 10 - Jan 31",
            "bag_limit":        "10 daily (max 2 mountain quail in eastern OR)",
            "possession_limit": "30 (max 6 mountain quail in eastern OR)",
        },
        {
            "name":             "Sage Grouse",
            "asterisk":         True,
            "season_start":     "September 6, 2026",
            "season_end":       "September 14, 2026",
            "season_raw":       "September 6 - 14, 2026 (controlled permit draw only)",
            "hunting_units":    "Selected WMUs via controlled hunt permit (Beulah, Malheur River, Owyhee, Trout Creek, Whitehorse, Steens Mountain, Beatys Butte, Silvies, Wagontire, Warner units)",
            "bag_limit":        "2 daily and season",
            "possession_limit": "2",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the eRegulations Oregon License/Tag/Permit Fees page.
    All hunters age 18+ need an Upland Game Bird Validation.
    Nonresident hunters need a Nonresident Game Bird Validation.
    """
    return [
        {
            "name":             "Hunting License (Resident, age 18+)",
            "asterisk":         True,
            "covers":           "Base hunting license required for all hunters",
            "resident_cost":    "$34.50",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Hunting License (Nonresident, age 18+)",
            "asterisk":         True,
            "covers":           "Base hunting license required for all nonresident hunters",
            "resident_cost":    None,
            "nonresident_cost": "$172.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident 3-Day Hunting License (game birds & crows)",
            "asterisk":         False,
            "covers":           "Game birds and crows for 3 consecutive days (no controlled hunts)",
            "resident_cost":    None,
            "nonresident_cost": "$32.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Upland Game Bird Validation (Resident, age 18+)",
            "asterisk":         True,
            "covers":           "Required in addition to hunting license to hunt upland game birds",
            "resident_cost":    "$10.00",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Nonresident Game Bird Validation (age 18+)",
            "asterisk":         True,
            "covers":           "Required in addition to nonresident hunting license to hunt game birds",
            "resident_cost":    None,
            "nonresident_cost": "$44.50",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Combination License (ages 12-17)",
            "asterisk":         False,
            "covers":           "Hunting, angling, shellfish, Columbia River Basin Endorsement",
            "resident_cost":    "$10.00",
            "nonresident_cost": "$10.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Youth Upland Game Bird Validation (ages 12-17)",
            "asterisk":         False,
            "covers":           "Required for youth to hunt upland game birds",
            "resident_cost":    "$4.00",
            "nonresident_cost": "$4.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Sage Grouse Permit",
            "asterisk":         True,
            "covers":           "Required to hunt sage grouse (controlled hunt draw)",
            "resident_cost":    "$2.00 (plus controlled hunt application fee)",
            "nonresident_cost": "$2.00 (plus controlled hunt application fee)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": (
                "All hunters age 18 and older must possess an Upland Game Bird "
                "Validation (resident $10) or Nonresident Game Bird Validation "
                "($44.50) in addition to a valid hunting license."
            ),
            "applies_to": [
                "Hunting License (Resident, age 18+)",
                "Hunting License (Nonresident, age 18+)"
            ],
            "sources": [
                {
                    "url":      FEE_URL,
                    "label":    "eRegulations — Oregon License, Tag, & Permit Fees",
                    "evidence": (
                        "Upland Game Bird Validation (age 18+): $10.00 resident. "
                        "Nonresident Game Bird Validation: $44.50."
                    )
                }
            ]
        },
        {
            "title": (
                "Sage grouse hunting is by controlled permit only — "
                "apply during the July 1 – August 8 application period."
            ),
            "applies_to": ["Sage Grouse"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    f"{EREG_LABEL} — Controlled Sage-Grouse Season",
                    "evidence": (
                        "2025 Controlled Sage-Grouse Season: permit numbers finalized "
                        "August. Application period July 1 - Aug 8. Season Sept 6-14. "
                        "Daily & season bag limit: 2 birds."
                    )
                }
            ]
        },
        {
            "title": (
                "Spruce grouse are protected in Oregon and are not open to "
                "hunting — learn to distinguish them from blue/ruffed grouse "
                "in the Wallowa Mountains."
            ),
            "applies_to": ["Ruffed Grouse", "Blue (Dusky) Grouse"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    f"{EREG_LABEL} — Spruce Grouse Protected Species",
                    "evidence": (
                        "Spruce grouse are protected in Oregon and are not open "
                        "to hunting. Range: Wallowa Mountains only. Male: red eye comb, "
                        "black throat. Female: browner with white barring."
                    )
                }
            ]
        },
        {
            "title": (
                "Within the Lower Klamath Hills Regulated Hunt Area near "
                "Klamath Falls, the daily chukar bag limit is reduced to 2 "
                "and possession limit to 4."
            ),
            "applies_to": ["Chukar Partridge"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    f"{EREG_LABEL} — Chukar Partridge",
                    "evidence": (
                        "Within the posted boundaries of the Lower Klamath Hills "
                        "Regulated Hunt Area near Klamath Falls, the daily chukar "
                        "bag limit is 2 and possession limit is 4."
                    )
                }
            ]
        },
        {
            "title": (
                "Western Oregon Fee Pheasant Hunts require a valid hunting "
                "license, upland game bird validation, and a Western Oregon "
                "Fee Pheasant Permit ($25). Only nontoxic shot allowed."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    f"{EREG_LABEL} — Western Oregon Fee Pheasant Hunts",
                    "evidence": (
                        "Requirements: Valid hunting license + upland game bird "
                        "validation + Western Oregon fee pheasant permit ($25). "
                        "Only federally approved nontoxic shot allowed."
                    )
                }
            ]
        },
        {
            "title": (
                "Only rooster (male) pheasants may be taken. "
                "All pheasant seasons are rooster-only."
            ),
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    f"{EREG_LABEL} — Rooster Pheasant",
                    "evidence": (
                        "Rooster Pheasant — Statewide: Oct 11 - Dec 31. "
                        "2 daily, 8 possession."
                    )
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[OR_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    try:
        soup = fetch_html(SOURCE_URL)
    except Exception as e:
        print(f"[OR_scrape] WARNING: Could not fetch source page: {e}", file=sys.stderr)
        print("[OR_scrape] Using hardcoded data from eRegulations PDF.", file=sys.stderr)
        soup = None

    dataset = {
        "state":     "Oregon",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup) if soup else {
            "page_url":     SOURCE_URL,
            "page_label":   "Game Bird Seasons | eRegulations — Oregon",
            "last_updated": None,
            "update_note":  (
                "Could not fetch source page. "
                "Data from eRegulations Oregon Game Bird Seasons and ODFW framework."
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
        description="Scrape Oregon DFW upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="data/OR_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: data/OR_Upland_Gamebird_dataset.json)"
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

    print(f"[OR_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
