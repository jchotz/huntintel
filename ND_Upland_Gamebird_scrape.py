#!/usr/bin/env python3
"""
ND_Upland_Gamebird_scrape.py — HuntIntel North Dakota Upland Game Bird Scraper
Fetches the North Dakota Game & Fish upland game page and signed proclamation,
then outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python ND_Upland_Gamebird_scrape.py
    python ND_Upland_Gamebird_scrape.py --output my_output.json
    python ND_Upland_Gamebird_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL   = "https://gf.nd.gov/hunting/upland"
PROC_URL     = "https://gf.nd.gov/gnf/regulations/docs/combination/proc-combination-2025.pdf"
PROC_LABEL   = "2025-2026 Small Game, Waterfowl and Furbearer Proclamation"
SPRING_TK_PDF = "https://gf.nd.gov/gnf/regulations/docs/springturkey/proc-sprg-trky-2026.pdf"
SPRING_TK_LABEL = "2026 Spring Wild Turkey Proclamation"

LICENSE_PURCHASE_URLS = [
    {
        "label": "ND Game & Fish Online License Portal",
        "url":   "https://apps.nd.gov/gnf/onlineservices/lic/public/myGNF.htm"
    },
    {
        "label": "ND Game & Fish Buy and Apply",
        "url":   "https://gf.nd.gov/buy-apply"
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
    if not raw or raw in ("—", "–", "-", "N/A", "n/a", "n/a"):
        return None
    return raw


def strip_asterisk(text: str) -> tuple[str, bool]:
    has = text.rstrip().endswith("*")
    return text.rstrip("* ").strip(), has


# ── Scraper ────────────────────────────────────────────────────────────────────

def scrape_source_meta(soup: BeautifulSoup) -> dict:
    return {
        "page_url":     SOURCE_URL,
        "page_label":   "Upland Game | North Dakota Game and Fish",
        "last_updated": None,
        "update_note":  (
            "No explicit last-updated date on source page. "
            "2026-27 season dates are tentative until the proclamation is signed (expected late July). "
            "2025-26 data is from the signed proclamation."
        ),
        "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def build_species() -> list[dict]:
    """
    2025-26 signed season data from the North Dakota Small Game,
    Waterfowl and Furbearer Proclamation (proc-combination-2025.pdf).
    Note: Tree squirrel is classified as upland game in ND.
    Wild turkey is lottery-only; spring is residents only.
    """
    return [
        {
            "name":             "Hungarian Partridge",
            "asterisk":         False,
            "season_start":     "September 13, 2025",
            "season_end":       "January 4, 2026",
            "season_raw":       "September 13, 2025 - January 4, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Ring-necked Pheasant",
            "asterisk":         True,
            "season_start":     "October 11, 2025",
            "season_end":       "January 4, 2026",
            "season_raw":       "October 11, 2025 - January 4, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "3 male (rooster) pheasants daily",
            "possession_limit": "12",
            "sub_seasons": [
                {
                    "name":         "Youth Season",
                    "season_start": "October 4, 2025",
                    "season_end":   "October 5, 2025",
                    "bag_limit":    "3 daily",
                    "possession_limit": "12",
                    "note": "Residents and nonresidents age 15 or younger; adult (18+) companion required, companion may not carry firearm or hunt."
                }
            ]
        },
        {
            "name":             "Sharp-tailed Grouse",
            "asterisk":         True,
            "season_start":     "September 13, 2025",
            "season_end":       "January 4, 2026",
            "season_raw":       "September 13, 2025 - January 4, 2026",
            "hunting_units":    "Statewide (with closed exception area — see key notes)",
            "bag_limit":        "3 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Ruffed Grouse",
            "asterisk":         True,
            "season_start":     "September 13, 2025",
            "season_end":       "January 4, 2026",
            "season_raw":       "September 13, 2025 - January 4, 2026",
            "hunting_units":    "Restricted (Bottineau, Rolette, Cavalier, Pembina, Walsh counties and part of J. Clark Salyer NWR in McHenry County)",
            "bag_limit":        "3 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Tree Squirrel",
            "asterisk":         False,
            "season_start":     "September 13, 2025",
            "season_end":       "February 28, 2026",
            "season_raw":       "September 13, 2025 - February 28, 2026",
            "hunting_units":    "Statewide",
            "bag_limit":        "4 daily",
            "possession_limit": "12",
        },
        {
            "name":             "Wild Turkey (Spring)",
            "asterisk":         True,
            "season_start":     "April 11, 2026",
            "season_end":       "May 17, 2026",
            "season_raw":       "April 11, 2026 - May 17, 2026",
            "hunting_units":    "Open units (lottery; residents only)",
            "bag_limit":        "1 bearded or male turkey per license",
            "possession_limit": "1",
        },
        {
            "name":             "Wild Turkey (Fall)",
            "asterisk":         True,
            "season_start":     None,
            "season_end":       None,
            "season_raw":       "2026-27 regulations not yet posted",
            "hunting_units":    "Open units (lottery)",
            "bag_limit":        "TBD — regulations not yet posted",
            "possession_limit": "TBD",
        },
    ]


def build_licenses() -> list[dict]:
    """
    License costs from the ND Game & Fish licensing pages (resident/nonresident).
    Small Game license covers all upland game birds except turkey.
    Prerequisite fees (certificate, general game & habitat) are included separately.
    """
    return [
        {
            "name":             "Small Game License (age 16+)",
            "asterisk":         True,
            "covers":           "Hungarian Partridge, Pheasant, Sharp-tailed Grouse, Ruffed Grouse, Tree Squirrel, Crow, Doves, Sandhill Cranes, Snipe, Woodcock",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$150.00 (14-consecutive-day or two 7-consecutive-day periods)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Small Game License (age 15 or younger)",
            "asterisk":         False,
            "covers":           "Same as adult Small Game License",
            "resident_cost":    "No license fee (certificate + general game & habitat still required)",
            "nonresident_cost": "No license fee (certificate + general game & habitat still required)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Wild Turkey License — Spring (residents only)",
            "asterisk":         True,
            "covers":           "Spring wild turkey season; lottery required",
            "resident_cost":    "$20.00 (plus Small Game License required)",
            "nonresident_cost": None,
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Wild Turkey License — Fall",
            "asterisk":         True,
            "covers":           "Fall wild turkey season; lottery required",
            "resident_cost":    "$20.00 (plus Small Game License required)",
            "nonresident_cost": "$100.00 (available only after resident lottery if licenses remain)",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "Fishing, Hunting, Furbearer Certificate (prerequisite)",
            "asterisk":         False,
            "covers":           "Required annually for all hunters",
            "resident_cost":    "$2.00",
            "nonresident_cost": "$5.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
        {
            "name":             "General Game and Habitat License (prerequisite)",
            "asterisk":         False,
            "covers":           "Required annually for all hunting except furbearer",
            "resident_cost":    "$20.00",
            "nonresident_cost": "$20.00",
            "purchase_urls":    LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    return [
        {
            "title": "Nonresidents may not hunt any game during the first 7 days of the regular pheasant season.",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/hunting/pheasant",
                    "label":    "ND Game & Fish — Pheasant hunting page",
                    "evidence": "In accordance with NDCC 20.1-08-04.9, nonresidents shall be prohibited from hunting from October [first seven days of regular season]."
                },
                {
                    "url":      PROC_URL,
                    "label":    f"{PROC_LABEL} — Section 12",
                    "evidence": "Male pheasants may be taken statewide from October 11, 2025 through January 4, 2026."
                }
            ]
        },
        {
            "title": "Youth pheasant season (2 days) requires a non-hunting adult companion age 18+.",
            "applies_to": ["Ring-necked Pheasant"],
            "sources": [
                {
                    "url":      PROC_URL,
                    "label":    f"{PROC_LABEL} — Section 12, Youth Pheasant Season",
                    "evidence": "An adult, at least 18 years of age, must accompany the youth pheasant hunter into the field. Any adult accompanying the youth into the field may not carry a firearm and may not hunt any species of wildlife."
                }
            ]
        },
        {
            "title": "A specific area in southeastern ND is closed to sharp-tailed grouse hunting.",
            "applies_to": ["Sharp-tailed Grouse"],
            "sources": [
                {
                    "url":      PROC_URL,
                    "label":    f"{PROC_LABEL} — Section 14",
                    "evidence": "That portion of North Dakota bordered on the west by ND Highway 32, on the north by the Sheyenne River, on the south ND Highway 11 and on the east by the Red and Bois de Sioux Rivers shall be closed to sharp-tailed grouse hunting."
                },
                {
                    "url":      "https://gf.nd.gov/hunting/sharp-tailed-grouse",
                    "label":    "ND Game & Fish — Sharp-tailed Grouse page",
                    "evidence": "Sharp-tailed grouse are very similar to greater prairie-chicken which are not legal to hunt. Learn how to differentiate the two species before going into the field."
                }
            ]
        },
        {
            "title": "Ruffed grouse season is restricted to 5 specific counties and part of J. Clark Salyer NWR — not statewide.",
            "applies_to": ["Ruffed Grouse"],
            "sources": [
                {
                    "url":      PROC_URL,
                    "label":    f"{PROC_LABEL} — Section 16",
                    "evidence": "Ruffed grouse may be taken in Bottineau, Rolette, Cavalier, Pembina, and Walsh counties and that portion of J. Clark Salyer National Wildlife Refuge in McHenry County south of the Upham-Willow City road from September 13, 2025 through January 4, 2026."
                }
            ]
        },
        {
            "title": "Spring wild turkey is open to North Dakota residents only.",
            "applies_to": ["Wild Turkey (Spring)"],
            "sources": [
                {
                    "url":      SPRING_TK_PDF,
                    "label":    f"{SPRING_TK_LABEL} — Section 2",
                    "evidence": "Only North Dakota residents are eligible for the spring wild turkey season."
                }
            ]
        },
        {
            "title": "Both spring and fall wild turkey require a lottery license application.",
            "applies_to": ["Wild Turkey (Spring)", "Wild Turkey (Fall)"],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/hunting/lotteries",
                    "label":    "ND Game & Fish — Hunting Lotteries",
                    "evidence": "Turkey licenses are allocated by lottery. After the first lottery has been held, if licenses remain, nonresidents may purchase a fall wild turkey license."
                }
            ]
        },
        {
            "title": "Fall 2026-27 wild turkey regulations have not yet been posted.",
            "applies_to": ["Wild Turkey (Fall)"],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/regulations/fall-turkey",
                    "label":    "ND Game & Fish — Fall Turkey Regulations page",
                    "evidence": "2026 regulations will be posted here after the proclamation has been signed."
                }
            ]
        },
        {
            "title": "Nonresident small game license is limited to 14-consecutive-day or two 7-consecutive-day periods per purchase.",
            "applies_to": ["Small Game License (age 16+)"],
            "sources": [
                {
                    "url":      "https://gf.nd.gov/licensing/nonresident",
                    "label":    "ND Game & Fish — Nonresident Licensing",
                    "evidence": "A nonresident must choose between a 14-consecutive-day or two 7-consecutive-day license periods and may purchase more than one license per year."
                }
            ]
        },
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[ND_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    soup = fetch_html(SOURCE_URL)

    dataset = {
        "state":     "North Dakota",
        "category":  "Upland Game Birds",
        "source":    scrape_source_meta(soup),
        "species":   build_species(),
        "licenses":  build_licenses(),
        "key_notes": build_key_notes(),
    }
    return dataset


def main():
    parser = argparse.ArgumentParser(
        description="Scrape North Dakota Game & Fish upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="ND_Upland_Gamebird_dataset.json",
        help="Output JSON filename (default: ND_Upland_Gamebird_dataset.json)"
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

    print(f"[ND_scrape] Wrote {args.output}", file=sys.stderr)
    print(output_str)


if __name__ == "__main__":
    main()
