# HuntIntel

**Hunting Regulations by State & Species** — easy reference for hunting season dates, bag limits, and license costs.

## Structure

```
index.html                         # Main site (static, JS-driven)
data/
  states.json                      # State/category manifest
  MT_Upland_Gamebird_dataset.json  # Montana — Upland Game Birds
  ND_Upland_Gamebird_dataset.json  # North Dakota — Upland Game Birds
  SD_Upland_Gamebird_dataset.json  # South Dakota — Upland Game Birds
*_scrape.py                        # Scrapers for each state/category
```

## Scrapers

Each state has a standalone scraper (`*_scrape.py`) that pulls from the official state fish & wildlife agency page and produces a JSON dataset matching the HuntIntel schema. Run them to refresh data:

```bash
python MT_Upland_Gamebird_scrape.py --pretty
python ND_Upland_Gamebird_scrape.py --pretty
python SD_Upland_Gamebird_scrape.py --pretty
```

## Live Site

Hosted via GitHub Pages. Visit **[jchotz.github.io/huntintel](https://jchotz.github.io/huntintel)** to browse regulations.
