#!/usr/bin/env python3
"""Check which version a live site actually serves.

Usage:
  python3 -I served_version.py https://app.example.com --expect 2.4.1

Fetches the page with caching disabled, finds its JavaScript bundles
(for example Vite's assets/index-<hash>.js), and searches them for the
expected version string. A green deploy in the dashboard is not proof the
domain serves it: an earlier rollback can pin the domain to an old build.

Exit code 0 = version found, 1 = not found, 2 = fetch error.
"""
import argparse
import re
import sys
import urllib.parse
import urllib.request


def get(url):
    req = urllib.request.Request(url, headers={
        "Cache-Control": "no-cache", "Pragma": "no-cache", "User-Agent": "served-version-check"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--expect", required=True, help="version string to look for, e.g. 2.4.1")
    ap.add_argument("--max-bundles", type=int, default=10)
    a = ap.parse_args()

    try:
        html = get(a.url)
    except Exception as exc:  # noqa: BLE001
        print(f"FETCH ERROR {a.url}: {exc}")
        sys.exit(2)

    srcs = re.findall(r'<script[^>]+src="([^"]+\.js)"', html) + \
        re.findall(r'<link[^>]+rel="modulepreload"[^>]+href="([^"]+\.js)"', html)
    srcs = list(dict.fromkeys(srcs))[: a.max_bundles]
    if a.expect in html:
        print(f"FOUND  {a.expect} in the HTML of {a.url}")
        sys.exit(0)
    if not srcs:
        print(f"NOT FOUND  no script bundles in {a.url}; check the page by hand")
        sys.exit(1)
    pat = re.compile(r"(?<![\d.])" + re.escape(a.expect) + r"(?![\d.])")
    for src in srcs:
        full = urllib.parse.urljoin(a.url, src)
        try:
            js = get(full)
        except Exception as exc:  # noqa: BLE001
            print(f"  skip {full}: {exc}")
            continue
        if pat.search(js):
            print(f"FOUND  {a.expect} in {src}")
            sys.exit(0)
        print(f"  checked {src}: no {a.expect}")
    print(f"NOT FOUND  {a.url} does not serve {a.expect}. Check for a pinned or rolled-back deployment.")
    sys.exit(1)


if __name__ == "__main__":
    main()
