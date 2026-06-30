#!/usr/bin/env python3
"""
huntintel-watch.py — Lightweight change detector for HuntIntel source pages.

Sends only HTTP HEAD requests (headers, no body) to each source page.
If the server says the page changed since our last check, it reports it.

Usage:
    python huntintel-watch.py                     # check all sources, report changes
    python huntintel-watch.py --quiet             # only print if something changed
    python huntintel-watch.py --init              # initialize state file, don't check
    python huntintel-watch.py --auto              # check AND auto-rescrape + deploy changes

State is stored in data/.watch-state.json (~1KB).

Auto-rescrape will run the relevant scraper, regenerate the dataset, and FTP
deploy the updated files. Credentials are read from data/.watch-cred.json:
    {"user": "huntinte@...", "pass": "..."}
Or pass --user and --pass flags.
"""

import json, os, sys, time, subprocess
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(REPO, "data", ".watch-state.json")

def fetch_headers(url, timeout=10):
    """Send HEAD request and return response headers dict."""
    import urllib.request
    req = urllib.request.Request(url, method="HEAD")
    req.add_header("User-Agent", "HuntIntel-Watch/1.0 (+https://huntintel.io)")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        info = resp.info()
        return {
            "status": resp.status,
            "last_modified": info.get("Last-Modified"),
            "etag": info.get("ETag"),
            "content_length": info.get("Content-Length"),
        }
    except Exception as e:
        return {"status": 0, "last_modified": None, "etag": None,
                "content_length": None, "error": str(e)}


def get_source_urls():
    """Read all source URLs from dataset files."""
    manifest_path = os.path.join(REPO, "data", "states.json")
    if not os.path.isfile(manifest_path):
        print("ERROR: data/states.json not found in", REPO)
        sys.exit(1)
    with open(manifest_path) as f:
        mf = json.load(f)

    urls = {}
    for state in mf["states"]:
        for cat in state["categories"]:
            ds_path = os.path.join(REPO, cat["dataFile"])
            if not os.path.isfile(ds_path):
                continue
            with open(ds_path) as f:
                ds = json.load(f)
            page_url = ds.get("source", {}).get("page_url")
            page_label = ds.get("source", {}).get("page_label", "")
            if page_url:
                key = "{}:{}".format(state["id"], cat["id"])
                urls[key] = {
                    "state": state["name"],
                    "category": cat["label"],
                    "url": page_url,
                    "label": page_label,
                }
    return urls


def load_state():
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


# ── Category ID → scraper filename convention ──
CATEGORY_MAP = {
    "upland-gamebirds": "Upland_Gamebird",
    "migratory-birds":  "Migratory_Bird",
}


def get_ftp_creds():
    """Read FTP credentials from data/.watch-cred.json or command-line args."""
    cred_file = os.path.join(REPO, "data", ".watch-cred.json")
    user = None; password = None
    if "--user" in sys.argv:
        idx = sys.argv.index("--user")
        if idx + 1 < len(sys.argv): user = sys.argv[idx + 1]
    if "--pass" in sys.argv:
        idx = sys.argv.index("--pass")
        if idx + 1 < len(sys.argv): password = sys.argv[idx + 1]
    if (not user or not password) and os.path.isfile(cred_file):
        with open(cred_file) as f:
            c = json.load(f)
            if not user: user = c.get("user")
            if not password: password = c.get("pass")
    return user, password


def ftp_upload(local_path, remote_url, user, password, timeout=15):
    """Upload a single file via FTP using curl."""
    result = subprocess.run([
        "curl", "-s", "--connect-timeout", "5", "--max-time", str(timeout),
        "--user", "{}:{}".format(user, password),
        "-T", local_path, remote_url
    ], capture_output=True, text=True, timeout=timeout + 5)
    return result.returncode == 0


def rescrape(changed_key, info, user, password):
    """
    Rescrape a changed source: run scraper, verify, FTP deploy.
    changed_key: 'KS:migratory-birds' or 'MT:upland-gamebirds'
    """
    state_code, cat_id = changed_key.split(":")
    cat_pascal = CATEGORY_MAP.get(cat_id)
    if not cat_pascal:
        print("    Unknown category '{}' — skipping".format(cat_id))
        return False

    scraper = os.path.join(REPO, "{}_{}_scrape.py".format(state_code, cat_pascal))
    dataset = "data/{}_{}_dataset.json".format(state_code, cat_pascal)

    if not os.path.isfile(scraper):
        print("    Scraper not found: {}".format(scraper))
        return False

    # Step 1: Run the scraper
    print("    Running: python3 {} ...".format(os.path.basename(scraper)))
    result = subprocess.run(
        [sys.executable, scraper],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print("    FAILED (exit {}): {}".format(result.returncode, result.stderr[:200]))
        return False

    # Step 2: Verify dataset
    ds_path = os.path.join(REPO, dataset)
    if not os.path.isfile(ds_path):
        print("    Dataset not generated: {}".format(dataset))
        return False
    with open(ds_path) as f:
        try:
            d = json.load(f)
        except json.JSONDecodeError:
            print("    Dataset is invalid JSON")
            return False
    print("    Updated dataset: {} species, {} licenses ({} KB)".format(
        len(d.get("species", [])), len(d.get("licenses", [])),
        os.path.getsize(ds_path) // 1024))

    # Step 3: FTP deploy
    if user and password:
        host = "17761923290d68e3234c7d8081.temporary.link"
        # Upload dataset
        ok = ftp_upload(ds_path, "ftp://{}/{}".format(host, dataset), user, password)
        if ok:
            print("    Deployed: {}".format(dataset))
        else:
            print("    FTP FAILED for {}".format(dataset))
        # Upload states.json too (scraper may update scraped_at timestamp)
        states_json = os.path.join(REPO, "data", "states.json")
        ok2 = ftp_upload(states_json, "ftp://{}/data/states.json".format(host), user, password)
        if ok2:
            print("    Deployed: data/states.json")
    else:
        print("    No FTP credentials — skipping deploy")

    return True


def main():
    quiet = "--quiet" in sys.argv
    do_init = "--init" in sys.argv

    sources = get_source_urls()
    state = load_state()

    if do_init:
        now = datetime.now(timezone.utc).isoformat()
        for key, info in sources.items():
            state[key] = {
                "last_modified": None,
                "etag": None,
                "content_length": None,
                "last_checked": now,
                "url": info["url"],
            }
        save_state(state)
        print("State initialized for {} sources. Next run will detect changes.".format(len(sources)))
        return

    # ── Check each source ──
    changed = []
    errors = []
    unchanged = 0
    skipped = 0

    if not quiet:
        print("HuntIntel Watch — checking {} source pages\n".format(len(sources)))
        print("{:<6} {:<30} {:>10} {:>10}".format("State", "Source", "Status", "Size"))
        print("-" * 60)

    for key in sorted(sources.keys()):
        info = sources[key]
        url = info["url"]
        prev = state.get(key, {})

        headers = fetch_headers(url)
        status = headers.get("status", 0)
        cl = headers.get("content_length", "?")

        # Detect change
        has_changed = False
        reason = ""

        if status == 0:
            # Connection error
            reason = headers.get("error", "timeout/error")
            errors.append("{} - {}: {}".format(key, info["state"], reason))
            if not quiet:
                print("{:<6} {:<30} {:>10} {:>10}".format(key.split(":")[0], info["state"][:28], "ERROR", str(cl or "?")))
            skipped += 1
            continue

        if status == 304:
            # Not Modified (server supports If-Modified-Since — not used here but good sign)
            pass

        # Compare stored values
        lm = headers.get("last_modified")
        etag = headers.get("etag")

        if lm and prev.get("last_modified") and lm != prev["last_modified"]:
            # Check if it's a real change vs. server noise
            try:
                # Parse both timestamps and compare
                from email.utils import parsedate_to_datetime
                old_t = parsedate_to_datetime(prev["last_modified"])
                new_t = parsedate_to_datetime(lm)
                diff_seconds = abs((new_t - old_t).total_seconds())
                if diff_seconds > 3600:  # >1 hour = real change
                    has_changed = True
                    reason = "Last-Modified changed: {} → {} ({}s gap)".format(
                        prev["last_modified"], lm, int(diff_seconds))
            except Exception:
                has_changed = True
                reason = "Last-Modified changed: {} → {}".format(prev["last_modified"], lm)
        elif etag and prev.get("etag") and etag != prev["etag"]:
            has_changed = True
            reason = "ETag changed"
        elif cl and prev.get("content_length") and cl != prev["content_length"]:
            has_changed = True
            reason = "Content-Length changed: {} → {}".format(prev["content_length"], cl)
        elif not prev.get("last_modified") and not prev.get("etag") and not prev.get("content_length"):
            # First check — no baseline yet
            has_changed = False
            if not quiet:
                unchanged += 1
                print("{:<6} {:<30} {:>10} {:>10}".format(key.split(":")[0], info["state"][:28], "BASELINE", str(cl or "?")))
            state[key] = {
                "last_modified": lm,
                "etag": etag,
                "content_length": cl,
                "last_checked": datetime.now(timezone.utc).isoformat(),
                "url": url,
            }
            continue

        # Update stored state
        state[key] = {
            "last_modified": lm,
            "etag": etag,
            "content_length": cl,
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "url": url,
        }

        if has_changed:
            changed.append((key, info["state"], info["category"], url, reason))
            if not quiet:
                print("{:<6} {:<30} {:>10} {:>10}  *** CHANGED ***".format(key.split(":")[0], info["state"][:28], "CHANGED", str(cl or "?")))
        else:
            unchanged += 1
            if not quiet:
                print("{:<6} {:<30} {:>10} {:>10}".format(key.split(":")[0], info["state"][:28], "ok", str(cl or "?")))

    save_state(state)

    # ── Report ──
    print()
    total = len(sources)
    print("Checked: {}  Unchanged: {}  Changed: {}  Errors: {}".format(total, unchanged, len(changed), len(errors)))

    if changed:
        print("\n⚠️  CHANGES DETECTED — these sources need rescraping:")
        for key, st, cat, url, reason in changed:
            print("  {:<4} {:<25}  {}".format(st, cat, reason))
            print("       {}".format(url))

    # ── Auto-rescrape ──
    if "--auto" in sys.argv and changed:
        print("\n🔧 Auto-rescrape enabled. Running scrapers...\n")
        user, password = get_ftp_creds()
        success = 0
        for key, st, cat, url, reason in changed:
            print("  {:<4} {:<25}  -> rescraping...".format(st, cat))
            ok = rescrape(key, {"state": st, "category": cat}, user, password)
            if ok:
                success += 1
            print()
        print("Rescraped {}/{} changed sources successfully.".format(success, len(changed)))

    if errors and not quiet:
        print("\nConnection errors (will retry next run):")
        for e in errors:
            print("  {}".format(e))

    if not changed and not quiet:
        print("\n✅ Everything up to date.")

    # Exit code: 0 = no changes, 1 = changes detected
    sys.exit(1 if changed else 0)


if __name__ == "__main__":
    main()
