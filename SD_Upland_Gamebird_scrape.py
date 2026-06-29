#!/usr/bin/env python3
"""
SD_Upland_Gamebird_scrape.py
Scrapes South Dakota GFP upland game bird hunting regulations.
Source: https://gfp.sd.gov/hunt/

Usage:
    python SD_Upland_Gamebird_scrape.py [--pretty] [--output FILENAME]
"""

import json
import sys
import argparse
import re
from datetime import datetime, timezone

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


# ---------------------------------------------------------------------------
# Source metadata
# ---------------------------------------------------------------------------

SOURCE_URL = "https://gfp.sd.gov/hunt/"
SOURCE_LABEL = "Hunting in South Dakota | South Dakota GFP"


def scrape_source_meta(soup):
    """
    Attempt to extract last-updated date from the page.
    SD GFP pages show only a copyright footer with no explicit update date.
    """
    page_label = SOURCE_LABEL
    if soup:
        title_tag = soup.find("title")
        if title_tag and title_tag.get_text(strip=True):
            page_label = title_tag.get_text(strip=True)

    scraped_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "page_url": SOURCE_URL,
        "page_label": page_label,
        "last_updated": None,
        "update_note": (
            "No explicit last-updated date found. "
            "Page footer reads \u00a9 Copyright 2026 State of South Dakota. "
            "Regulations sourced from 2025 South Dakota Hunting and Trapping Handbook "
            "(valid through Jan. 31, 2026 for 2025 licenses; Jan. 31, 2027 for 2026 licenses)."
        ),
        "scraped_at": scraped_at,
    }


# ---------------------------------------------------------------------------
# Hardcoded dataset (SD GFP pages use JS rendering; HTML parsing is unreliable)
# ---------------------------------------------------------------------------

def build_dataset(source_meta):
    scraped_at = source_meta["scraped_at"]

    species = [
        # ---- Ring-necked Pheasant (regular) --------------------------------
        {
            "name": "Ring-necked Pheasant",
            "asterisk": False,
            "season_start": "October 18, 2025",
            "season_end": "January 31, 2026",
            "season_raw": "Oct. 18 – Jan. 31",
            "hunting_units": "Statewide (some game bird refuges open Dec. 1 or Dec. 8)",
            "bag_limit": "3 roosters daily",
            "possession_limit": "15 roosters",
            "sub_seasons": [
                {
                    "name": "Youth Season",
                    "season_start": "September 27, 2025",
                    "season_end": "October 5, 2025",
                    "bag_limit": "3 roosters daily",
                    "possession_limit": "15 roosters",
                    "note": "Ages 12–17; youth under 16 must be accompanied by an unarmed adult; 10 a.m. CT opener.",
                },
                {
                    "name": "Resident-Only Season",
                    "season_start": "October 11, 2025",
                    "season_end": "October 13, 2025",
                    "bag_limit": "3 roosters daily",
                    "possession_limit": "9 roosters",
                    "note": "South Dakota residents only; public lands only; 10 a.m. CT opener.",
                },
            ],
        },
        # ---- Prairie Chicken & Grouse --------------------------------------
        {
            "name": "Prairie Chicken, Sharp-tailed & Ruffed Grouse",
            "asterisk": False,
            "season_start": "September 20, 2025",
            "season_end": "January 31, 2026",
            "season_raw": "Sept. 20 – Jan. 31",
            "hunting_units": "Statewide",
            "bag_limit": "3 (any combination)",
            "possession_limit": "15 (any combination)",
            "sub_seasons": [],
        },
        # ---- Greater Sage Grouse (CLOSED) ----------------------------------
        {
            "name": "Greater Sage Grouse",
            "asterisk": False,
            "season_start": None,
            "season_end": None,
            "season_raw": "SEASON CLOSED",
            "hunting_units": None,
            "bag_limit": None,
            "possession_limit": None,
            "sub_seasons": [],
        },
        # ---- Partridge & Chukar --------------------------------------------
        {
            "name": "Partridge (Gray/Hungarian) & Chukar",
            "asterisk": False,
            "season_start": "September 20, 2025",
            "season_end": "January 31, 2026",
            "season_raw": "Sept. 20 – Jan. 31",
            "hunting_units": "Statewide",
            "bag_limit": "5 (any combination)",
            "possession_limit": "15 (any combination)",
            "sub_seasons": [],
        },
        # ---- Quail ---------------------------------------------------------
        {
            "name": "Quail",
            "asterisk": False,
            "season_start": "October 18, 2025",
            "season_end": "January 31, 2026",
            "season_raw": "Oct. 18 – Jan. 31",
            "hunting_units": "Statewide",
            "bag_limit": "5 (any combination)",
            "possession_limit": "15 (any combination)",
            "sub_seasons": [],
        },
        # ---- Wild Turkey (Big Game) ----------------------------------------
        {
            "name": "Wild Turkey (Big Game — Draw Required)",
            "asterisk": True,
            "season_start": None,
            "season_end": None,
            "season_raw": "Multiple seasons — see sub-seasons",
            "hunting_units": "Prairie and Black Hills units",
            "bag_limit": "1–2 per license type",
            "possession_limit": "Per license",
            "sub_seasons": [
                {
                    "name": "Spring Prairie",
                    "season_start": "April 11, 2026",
                    "season_end": "May 31, 2026",
                    "bag_limit": "1 or 2 males (per license)",
                    "possession_limit": "Per license",
                    "note": "Draw required; application Jan. 14 – Feb. 11, 2026.",
                },
                {
                    "name": "Spring Black Hills",
                    "season_start": "April 25, 2026",
                    "season_end": "May 31, 2026",
                    "bag_limit": "1 male",
                    "possession_limit": "Per license",
                    "note": "Residents + limited NR draw (2,225 NR licenses available); application Jan. 21, 2026.",
                },
                {
                    "name": "Spring Custer State Park",
                    "season_start": "April 25, 2026",
                    "season_end": "May 23, 2026",
                    "bag_limit": "1 male",
                    "possession_limit": "Per license",
                    "note": "Residents only; draw required.",
                },
                {
                    "name": "Fall Prairie",
                    "season_start": "November 1, 2026",
                    "season_end": "January 31, 2027",
                    "bag_limit": "1 or 2 any turkey (per license)",
                    "possession_limit": "Per license",
                    "note": "Draw required; application Aug. 18 – Sep. 2, 2026.",
                },
            ],
        },
    ]

    licenses = [
        {
            "name": "Habitat Stamp",
            "asterisk": False,
            "covers": "Required for all hunters age 18+ before purchasing any hunting license (one per license year). Not required for 1-day, youth, or mentored licenses.",
            "resident_cost": "$10",
            "nonresident_cost": "$25",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
                {
                    "label": "SD GFP Licenses Page",
                    "url": "https://gfp.sd.gov/hunt-fish-license/",
                },
            ],
        },
        {
            "name": "Small Game License*",
            "asterisk": True,
            "covers": "Pheasant, grouse, partridge, quail, cottontail rabbit, tree squirrel, and predator/varmint species. Full season for residents.",
            "resident_cost": "$36",
            "nonresident_cost": "$142 (10-day, two 5-day periods)",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Resident Combination (Small Game + Fishing)*",
            "asterisk": True,
            "covers": "Residents 18+: small game hunting and fishing privileges combined.",
            "resident_cost": "$60",
            "nonresident_cost": "N/A",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Resident Senior Combination (65+)*",
            "asterisk": True,
            "covers": "Same privileges as Combination license; for residents age 65 or older.",
            "resident_cost": "$43",
            "nonresident_cost": "N/A",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Resident 1-Day Small Game",
            "asterisk": False,
            "covers": "Residents 18+; one daily limit per species; no Habitat Stamp required.",
            "resident_cost": "$15",
            "nonresident_cost": "N/A",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Youth Small Game (ages 12–17)",
            "asterisk": False,
            "covers": "Resident and nonresident youth ages 12–17; no Habitat Stamp required.",
            "resident_cost": "$5",
            "nonresident_cost": "$10 (10-day, two 5-day periods)",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Mentored Small Game (under age 16)",
            "asterisk": False,
            "covers": "Youth under 16 hunting with an unarmed adult mentor; no Habitat Stamp required.",
            "resident_cost": "$5",
            "nonresident_cost": "$10 (10-day, two 5-day periods)",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Turkey — Prairie Spring (1 male)*",
            "asterisk": True,
            "covers": "Wild turkey big game license; spring prairie unit; draw required.",
            "resident_cost": "$28",
            "nonresident_cost": "$121",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
                {
                    "label": "Spring Prairie Turkey Application (PDF)",
                    "url": "https://gfp.sd.gov/userdocs/docs/2026springturkey-prairie-app.pdf",
                },
            ],
        },
        {
            "name": "Turkey — Prairie Spring (2 males)*",
            "asterisk": True,
            "covers": "Wild turkey big game license; spring prairie unit, 2 males; draw required.",
            "resident_cost": "$40",
            "nonresident_cost": "$151",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Turkey — Black Hills Spring / Archery*",
            "asterisk": True,
            "covers": "Spring Black Hills and archery turkey; residents + limited NR draw (2,225 NR licenses).",
            "resident_cost": "$28",
            "nonresident_cost": "$121",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
                {
                    "label": "Spring Archery/BH/CSP/Mentored Application (PDF)",
                    "url": "https://gfp.sd.gov/userdocs/docs/2026springturkey-ast_bst_cst_mst-app.pdf",
                },
            ],
        },
        {
            "name": "Turkey — Prairie Fall (1 any turkey)*",
            "asterisk": True,
            "covers": "Fall prairie unit; either sex; draw required.",
            "resident_cost": "$20",
            "nonresident_cost": "$106",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
                {
                    "label": "Fall Turkey Application (PDF)",
                    "url": "https://gfp.sd.gov/userdocs/docs/2025fallturkey.pdf",
                },
            ],
        },
        {
            "name": "Turkey — Prairie Fall (2 any turkey)*",
            "asterisk": True,
            "covers": "Fall prairie unit; either sex, 2 birds; draw required.",
            "resident_cost": "$25",
            "nonresident_cost": "$131",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "Turkey — Mentored",
            "asterisk": False,
            "covers": "Mentored youth turkey license (spring or fall); unarmed adult mentor required.",
            "resident_cost": "$5",
            "nonresident_cost": "$10",
            "purchase_urls": [
                {
                    "label": "Apply — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "NR Shooting Preserve — 1-Day*",
            "asterisk": True,
            "covers": "Nonresident small game hunting on licensed shooting preserves; one day.",
            "resident_cost": "N/A",
            "nonresident_cost": "$50",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "NR Shooting Preserve — 5-Day*",
            "asterisk": True,
            "covers": "Nonresident small game on licensed shooting preserves; five days.",
            "resident_cost": "N/A",
            "nonresident_cost": "$96",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
        {
            "name": "NR Shooting Preserve — Season*",
            "asterisk": True,
            "covers": "Nonresident small game on licensed shooting preserves; full season.",
            "resident_cost": "N/A",
            "nonresident_cost": "$146",
            "purchase_urls": [
                {
                    "label": "Purchase — Go Outdoors South Dakota",
                    "url": "https://license.gooutdoorssouthdakota.com/Licensing/CustomerLookup.aspx",
                },
            ],
        },
    ]

    key_notes = [
        {
            "title": "Rooster-Only Rule — All Pheasant Seasons",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/pheasant/",
                    "label": "SD GFP Pheasant Page",
                    "evidence": "Only male (rooster) pheasants may be harvested; hens are fully protected across all seasons.",
                }
            ],
        },
        {
            "title": "Pheasant Shooting Hours Start at 10 a.m. CT",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook (pp. 26–29)",
                    "evidence": "\"Shooting hours: 10 a.m., Central Time, to sunset.\" Unique restriction — does not follow sunrise rule.",
                }
            ],
        },
        {
            "title": "Grouse, Partridge & Quail: Sunrise to Sunset",
            "applies_to": [
                "Prairie Chicken, Sharp-tailed & Ruffed Grouse",
                "Partridge (Gray/Hungarian) & Chukar",
                "Quail",
            ],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook",
                    "evidence": "Shooting hours: Sunrise to sunset statewide for prairie grouse, ruffed grouse, partridge/chukar, and quail.",
                }
            ],
        },
        {
            "title": "Sage Grouse Season Closed — Population Below Threshold",
            "applies_to": ["Greater Sage Grouse"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/sage-grouse/",
                    "label": "SD GFP Sage Grouse Page",
                    "evidence": "Season closed. Minimum threshold is 300 males on all leks for two consecutive years before a resident-only season will be considered. 2024 count: 94 males on 17 leks.",
                }
            ],
        },
        {
            "title": "Non-Toxic Shot Required on Most Public Lands",
            "applies_to": ["Ring-necked Pheasant", "Prairie Chicken, Sharp-tailed & Ruffed Grouse", "Partridge (Gray/Hungarian) & Chukar", "Quail"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook",
                    "evidence": "Non-toxic shot is required to hunt small game on most public lands (WPAs, National Grasslands, and other designated public lands).",
                }
            ],
        },
        {
            "title": "Nonresident Small Game Limited to Two 5-Day Periods",
            "applies_to": ["Ring-necked Pheasant", "Prairie Chicken, Sharp-tailed & Ruffed Grouse", "Partridge (Gray/Hungarian) & Chukar", "Quail"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/license-types/",
                    "label": "SD GFP License Types & Costs",
                    "evidence": "Nonresident Small Game license is described as '10-days, two 5-day periods' — not a full-season license.",
                }
            ],
        },
        {
            "title": "Youth Under 16 Must Be Accompanied by Unarmed Adult",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/pheasant/",
                    "label": "SD GFP Pheasant Page",
                    "evidence": "All youth hunters under age 16 must be accompanied by an unarmed adult during the youth pheasant season.",
                }
            ],
        },
        {
            "title": "Turkey Is Big Game — Separate Draw License Required",
            "applies_to": ["Wild Turkey (Big Game — Draw Required)"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/turkey/",
                    "label": "SD GFP Turkey Page",
                    "evidence": "Wild turkey is classified as Big Game in South Dakota. Turkey licenses are issued through a draw application system; not covered by small game license.",
                }
            ],
        },
        {
            "title": "NR Black Hills Turkey Now Limited — 2,225 Licenses",
            "applies_to": ["Wild Turkey (Big Game — Draw Required)"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook (Important Changes, p. 3)",
                    "evidence": "2025 change: Nonresident Black Hills spring turkey licenses are no longer unlimited; 2,225 NR licenses available.",
                }
            ],
        },
        {
            "title": "Resident-Only Pheasant Season — Public Lands Only (Oct. 11–13)",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook (pp. 27–28)",
                    "evidence": "The 3-day early resident-only season is restricted to public lands statewide and is not open to nonresidents. Possession limit is reduced to 9 birds.",
                }
            ],
        },
        {
            "title": "Game Bird Refuges Have Later Opening Dates",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url": "https://gfp.sd.gov/UserDocs/nav/HuntingandTrappingHandbook_2025_WEBUPDATE.pdf",
                    "label": "2025 SD Hunting and Trapping Handbook",
                    "evidence": "Renziehausen GPA, Gerken GBR, and White Lake GBR open Dec. 1 – Jan. 31. Sand Lake NWR (Brown County) opens Dec. 8 – Jan. 31.",
                }
            ],
        },
    ]

    dataset = {
        "state": "South Dakota",
        "category": "Upland Game Birds",
        "source_url": SOURCE_URL,
        "source_label": SOURCE_LABEL,
        "source_last_updated": None,
        "source_update_note": source_meta["update_note"],
        "source": source_meta,
        "species": species,
        "licenses": licenses,
        "key_notes": key_notes,
    }

    return dataset


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scrape South Dakota upland game bird regulations into JSON."
    )
    parser.add_argument(
        "--output",
        default="SD_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: SD_Upland_Gamebird_dataset.json)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (indent=2)",
    )
    args = parser.parse_args()

    print("Fetching SD GFP hunt page...", file=sys.stderr)

    soup = None
    if requests and BeautifulSoup:
        try:
            resp = requests.get(SOURCE_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            print("Page fetched successfully.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: could not fetch page ({e}). Using hardcoded data.", file=sys.stderr)
    else:
        print("Warning: requests/beautifulsoup4 not available. Using hardcoded data.", file=sys.stderr)

    print("Extracting source metadata...", file=sys.stderr)
    source_meta = scrape_source_meta(soup)

    print("Building dataset...", file=sys.stderr)
    dataset = build_dataset(source_meta)

    indent = 2 if args.pretty else None
    json_out = json.dumps(dataset, indent=indent, ensure_ascii=False)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(json_out)

    print(f"Done. Output written to: {args.output}", file=sys.stderr)
    print(json_out)


if __name__ == "__main__":
    main()
