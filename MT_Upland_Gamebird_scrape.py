#!/usr/bin/env python3
"""
MT_Upland_Gamebird_scrape.py — HuntIntel Montana Upland Game Bird Scraper
Fetches the Montana FWP upland game bird page and regulations PDF,
then outputs a structured JSON dataset matching the HuntIntel schema.

Usage:
    python MT_scrape.py
    python MT_scrape.py --output my_output.json
    python MT_scrape.py --pretty          # pretty-print JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ── Constants ──────────────────────────────────────────────────────────────────

SOURCE_URL = "https://fwp.mt.gov/hunt/regulations/upland-game-bird"
PDF_URL    = "https://fwp.mt.gov/binaries/content/assets/fwp/hunt/regulations/2025/2025-upgbrd-final-for-web.pdf"
PDF_LABEL  = "2025 UPLAND GAME BIRD PDF"

LICENSE_PURCHASE_URLS = [
    {
        "label": "Montana FWP Buy and Apply",
        "url":   "https://fwp.mt.gov/buyandapply"
    },
    {
        "label": "FWP Online Licensing",
        "url":   "https://ols.fwp.mt.gov"
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
    """Strip extra whitespace and normalise dashes."""
    return re.sub(r"\s+", " ", text).strip()


def parse_cost(raw: str):
    """
    Return a cost string or None.
    Treats em-dashes / 'N/A' / blank as None.
    Keeps compound values like '$10.00 standard / $5.00 discounted'.
    """
    raw = clean(raw)
    if not raw or raw in ("—", "–", "-", "N/A", "n/a"):
        return None
    return raw


def strip_asterisk(text: str) -> tuple[str, bool]:
    """Return (clean_name, has_asterisk)."""
    has = text.rstrip().endswith("*")
    return text.rstrip("* ").strip(), has


# ── Scraper ────────────────────────────────────────────────────────────────────

def scrape_source_meta(soup: BeautifulSoup) -> dict:
    """Pull page-level metadata."""
    # The FWP page does not publish an explicit last-updated date.
    return {
        "page_url":     SOURCE_URL,
        "page_label":   "Hunt By Species: Upland Game Birds | Montana FWP",
        "last_updated": None,
        "update_note":  (
            "No explicit last-updated date found on source page; "
            "page states regulations are typically posted mid July."
        ),
        "scraped_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }


def scrape_species(soup: BeautifulSoup) -> list[dict]:
    """
    Parse season / bag-limit rows from the FWP page.
    The FWP page renders an HTML table with columns:
      Species | Season | Daily Bag Limit | Possession Limit
    Falls back to a hardcoded dataset if the table is absent or changes.
    """
    species_list = []

    # Try to find the regulations table on the page
    tables = soup.find_all("table")
    target = None
    for tbl in tables:
        headers = [clean(th.get_text()) for th in tbl.find_all("th")]
        if any("season" in h.lower() for h in headers):
            target = tbl
            break

    if target:
        rows = target.find("tbody").find_all("tr") if target.find("tbody") else target.find_all("tr")[1:]
        for row in rows:
            cells = [clean(td.get_text()) for td in row.find_all("td")]
            if len(cells) < 2:
                continue
            raw_name = cells[0] if len(cells) > 0 else ""
            raw_season = cells[1] if len(cells) > 1 else ""
            raw_bag = cells[2] if len(cells) > 2 else ""
            raw_poss = cells[3] if len(cells) > 3 else ""

            name, has_asterisk = strip_asterisk(raw_name)

            # Parse season dates — format varies; try "Month Day, Year - Month Day, Year"
            season_start, season_end = parse_season(raw_season)

            species_list.append({
                "name":            name,
                "asterisk":        has_asterisk,
                "season_start":    season_start,
                "season_end":      season_end,
                "season_raw":      raw_season,
                "bag_limit":       raw_bag or None,
                "possession_limit": raw_poss or None,
            })
    else:
        # Fallback: hardcoded from 2025 regulations
        print(
            "[MT_scrape] WARNING: Could not find a season table on the FWP page. "
            "Using hardcoded 2025 dataset.",
            file=sys.stderr
        )
        species_list = _hardcoded_species()

    return species_list


def parse_season(raw: str) -> tuple[str | None, str | None]:
    """
    Try to split a season string like 'Sept. 1 - Jan. 1' or
    'September 1, 2025 - January 1, 2026' into start / end.
    Returns (start, end) as strings, or (None, None).
    """
    raw = clean(raw)
    # Match patterns like "No closed season"
    if "no closed season" in raw.lower() or not raw or raw == "—":
        return "No closed season", "No closed season"

    # Split on dash variants
    parts = re.split(r"\s*[-–—]\s*", raw, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()

    return raw, None


def _hardcoded_species() -> list[dict]:
    """2025 Montana upland game bird season data from official regulations."""
    return [
        {
            "name": "Mountain Grouse",
            "asterisk": False,
            "season_start": "September 1, 2025",
            "season_end": "January 1, 2026",
            "season_raw": "September 1, 2025 - January 1, 2026",
            "bag_limit": "3 in aggregate daily",
            "possession_limit": "9",
        },
        {
            "name": "Partridge",
            "asterisk": True,
            "season_start": "September 1, 2025",
            "season_end": "January 1, 2026",
            "season_raw": "September 1, 2025 - January 1, 2026",
            "bag_limit": "8 in aggregate daily",
            "possession_limit": "24",
        },
        {
            "name": "Ring-necked Pheasant",
            "asterisk": True,
            "season_start": "October 11, 2025",
            "season_end": "January 1, 2026",
            "season_raw": "October 11, 2025 - January 1, 2026",
            "bag_limit": "3 cock pheasants daily",
            "possession_limit": "9",
        },
        {
            "name": "Sage Grouse",
            "asterisk": True,
            "season_start": "September 1, 2025",
            "season_end": "September 30, 2025",
            "season_raw": "September 1, 2025 - September 30, 2025",
            "bag_limit": "2 daily",
            "possession_limit": "4",
        },
        {
            "name": "Sharp-tailed Grouse",
            "asterisk": True,
            "season_start": "September 1, 2025",
            "season_end": "January 1, 2026",
            "season_raw": "September 1, 2025 - January 1, 2026",
            "bag_limit": "4 daily",
            "possession_limit": "16",
        },
        {
            "name": "California/Gambel's Quail",
            "asterisk": False,
            "season_start": "No closed season",
            "season_end": "No closed season",
            "season_raw": "No closed season",
            "bag_limit": "No limit",
            "possession_limit": "No limit",
        },
    ]


def scrape_licenses(soup: BeautifulSoup) -> list[dict]:
    """
    Parse license cost table from the FWP page.
    Expected columns: License | Resident | Nonresident
    Falls back to hardcoded if absent.
    """
    licenses = []

    tables = soup.find_all("table")
    target = None
    for tbl in tables:
        headers = [clean(th.get_text()).lower() for th in tbl.find_all("th")]
        if "resident" in " ".join(headers):
            target = tbl
            break

    if target:
        rows = target.find("tbody").find_all("tr") if target.find("tbody") else target.find_all("tr")[1:]
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 1:
                continue
            raw_name = clean(cells[0].get_text())
            raw_res  = clean(cells[1].get_text()) if len(cells) > 1 else ""
            raw_nr   = clean(cells[2].get_text()) if len(cells) > 2 else ""

            name, has_asterisk = strip_asterisk(raw_name)
            licenses.append({
                "name":              name,
                "asterisk":          has_asterisk,
                "resident_cost":     parse_cost(raw_res),
                "nonresident_cost":  parse_cost(raw_nr),
                "purchase_urls":     LICENSE_PURCHASE_URLS,
            })
    else:
        print(
            "[MT_scrape] WARNING: Could not find a license table on the FWP page. "
            "Using hardcoded 2025 dataset.",
            file=sys.stderr
        )
        licenses = _hardcoded_licenses()

    return licenses


def _hardcoded_licenses() -> list[dict]:
    """2025 Montana upland game bird license costs."""
    return [
        {
            "name": "Upland Game Bird License",
            "asterisk": False,
            "resident_cost": "$10.00 standard / $5.00 discounted",
            "nonresident_cost": "$127.00 standard / $63.50 discounted",
            "purchase_urls": LICENSE_PURCHASE_URLS,
        },
        {
            "name": "3-day Upland Game Bird License",
            "asterisk": True,
            "resident_cost": None,
            "nonresident_cost": "$60.00",
            "purchase_urls": LICENSE_PURCHASE_URLS,
        },
        {
            "name": "Shooting Preserve License",
            "asterisk": False,
            "resident_cost": None,
            "nonresident_cost": "$20.00",
            "purchase_urls": LICENSE_PURCHASE_URLS,
        },
        {
            "name": "Former Resident License",
            "asterisk": False,
            "resident_cost": None,
            "nonresident_cost": "$63.50",
            "purchase_urls": LICENSE_PURCHASE_URLS,
        },
    ]


def build_key_notes() -> list[dict]:
    """
    Key notes are sourced from the regulations PDF and FWP page.
    These are regulatory nuances that cannot be reliably parsed from
    HTML alone — they are curated and pinned to specific source evidence.
    """
    return [
        {
            "title": "Free supplemental permit required for sage grouse hunting.",
            "applies_to": ["Sage Grouse"],
            "sources": [
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - Highlights/Reminders and permit requirement",
                    "evidence": "Free supplemental permit required for sage grouse hunting."
                },
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - Supplemental Sage Grouse Hunting Permit section",
                    "evidence": (
                        "All upland game bird hunters that choose to hunt sage grouse must "
                        "obtain a free Supplemental Sage Grouse Hunting Permit."
                    )
                }
            ]
        },
        {
            "title": "Sharp-tailed grouse hunting west of the Continental Divide is closed.",
            "applies_to": ["Sharp-tailed Grouse"],
            "sources": [
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - Highlights/Reminders",
                    "evidence": "Sharp-tailed grouse hunting west of the Continental Divide is closed."
                },
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - Hunting Season Information table",
                    "evidence": "Sharp-tailed Grouse ... Closed West of the Continental Divide."
                }
            ]
        },
        {
            "title": "In a portion of Carbon County, the partridge season extends to Jan. 10.",
            "applies_to": ["Partridge"],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Montana FWP upland game bird page",
                    "evidence": (
                        "Partridge: Sept. 1 - Jan. 1 (except for portion of Carbon County, "
                        "where it is Sept. 1 - Jan. 10)."
                    )
                },
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - Hunting Season Information table",
                    "evidence": "Portion of Carbon County ... Sept. 01 - Jan. 10."
                }
            ]
        },
        {
            "title": (
                "The 3-day Upland Game Bird License is not valid for sage grouse at any time "
                "or for ring-necked pheasant during the opening week of the season."
            ),
            "applies_to": [
                "3-day Upland Game Bird License",
                "Sage Grouse",
                "Ring-necked Pheasant"
            ],
            "sources": [
                {
                    "url":      SOURCE_URL,
                    "label":    "Montana FWP upland game bird page",
                    "evidence": (
                        "3-day license for nonresidents. The license is not valid for sage grouse "
                        "at any time or for ring-neck pheasants during the opening week of the season."
                    )
                },
                {
                    "url":      PDF_URL,
                    "label":    f"{PDF_LABEL} - License Chart",
                    "evidence": (
                        "The 3-day Upland Game Bird License is not valid for sage grouse at any time "
                        "or for ring-neck pheasants during the opening week of the season."
                    )
                }
            ]
        }
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def build_dataset() -> dict:
    print(f"[MT_scrape] Fetching {SOURCE_URL} ...", file=sys.stderr)
    soup = fetch_html(SOURCE_URL)

    dataset = {
        "state":    "Montana",
        "category": "Upland Game Birds",
        "source":   scrape_source_meta(soup),
        "species":  scrape_species(soup),
        "licenses": scrape_licenses(soup),
        "key_notes": build_key_notes(),
    }
    return dataset


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Montana FWP upland game bird data into JSON."
    )
    parser.add_argument(
        "--output", "-o",
        default="montana_upland_gamebird_dataset.json",
        help="Output JSON filename (default: montana_upland_gamebird_dataset.json)"
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

    print(f"[MT_scrape] Wrote {args.output}", file=sys.stderr)
    # Also print to stdout so it can be piped
    print(output_str)


if __name__ == "__main__":
    main()
