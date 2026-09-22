"""Materialise the endpoint list, because the page count is not knowable ahead.

The API is a bare JSON array, 25 per page, with no total in the response, so
the capture is "page until an empty array" -- 169 pages on 2026-09-22 and a
different number next month. The engine takes a fixed endpoint list and has no
paging primitive, and it should not grow one for this: the registry is already
the right place to write down exactly what will be fetched, and wss-gho does
the same thing (its 3,321 endpoints are generated from measured row counts).

So this runs BEFORE `wss validate` in the capture workflow and rewrites the
endpoints block. The diff is the signal: a month where the register grew by two
pages says so in git history.

WHY THIS ALSO OWNS THE SHRINK CHECK. The last page holds between 1 and 25
projects and oscillates every time the register grows, so a per-endpoint
`max_shrink_pct` fires on it by design -- and a quarantined page is never
archived, so that gate would predictably drop real data once a month. The gate
that belongs here is on the WHOLE REGISTER, which is what this asserts. Per
page, `must_contain: sustaincert_id` still rejects an error or empty body.
"""
import json, re, socket, sys, time, urllib.error, urllib.request
from pathlib import Path

_o = socket.getaddrinfo   # this host black-holes IPv6; see wss-gho/examples/map_activity.py
socket.getaddrinfo = lambda h, p, f=0, t=0, pr=0, fl=0: _o(h, p, socket.AF_INET, t, pr, fl)

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry" / "goldstandard.registry.projects.yml"
URL = "https://public-api.goldstandard.org/projects?query=&page={page}"
UA = "wss-probe (+https://github.com/q3dresearch)"
DELAY = 2
MAX_PAGES = 2000          # a runaway guard: 50,000 projects is far beyond plausible
MAX_SHRINK = 0.40         # the register losing >40% of its projects is not a refresh


def page(n, tries=3):
    for attempt in range(tries):
        try:
            b = urllib.request.urlopen(urllib.request.Request(
                URL.format(page=n), headers={"User-Agent": UA}), timeout=60).read()
            return json.loads(b)
        except Exception as exc:
            if attempt == tries - 1:
                raise SystemExit(f"  page {n} failed after {tries} tries: {type(exc).__name__} {exc}")
            time.sleep(DELAY * (attempt + 2))
    return []


def main():
    text = REG.read_text()
    known = len(re.findall(r"^  - url:", text, re.M))
    print(f"  registry currently lists {known} page(s)", flush=True)

    # Walk from the last known page rather than from 1: normally two or three
    # requests, and it costs nothing when the count has not moved.
    n = max(1, known)
    if page(n):
        while n < MAX_PAGES:
            time.sleep(DELAY)
            if not page(n + 1):
                break
            n += 1
    else:
        while n > 1:
            time.sleep(DELAY)
            n -= 1
            if page(n):
                break
    if n >= MAX_PAGES:
        raise SystemExit(f"  refusing to list {MAX_PAGES}+ pages — check the API before trusting this")

    # Count the register, so the shrink check is on the thing that matters.
    time.sleep(DELAY)
    last = page(n)
    total = (n - 1) * 25 + len(last)
    prev = re.search(r"^  (\d[\d,]*) projects over (\d+) pages", text, re.M)
    if prev:
        before = int(prev.group(1).replace(",", ""))
        if total < before * (1 - MAX_SHRINK):
            raise SystemExit(f"  REGISTER SHRANK: {before:,} -> {total:,} projects "
                             f"({(1-total/before)*100:.0f}%). Not rewriting; look before capturing.")
        print(f"  register: {before:,} -> {total:,} projects", flush=True)

    block = "".join(
        f'  - url: "{URL.format(page=i)}"\n'
        f"    delay_seconds: {DELAY}\n    timeout_seconds: 60\n"
        for i in range(1, n + 1))
    new = re.sub(r"(?m)^endpoints:\n(?:  .*\n|\n(?=  ))*", f"endpoints:\n{block}\n", text, count=1)
    if new == text:
        raise SystemExit("  endpoints block not found — registry shape changed")
    # A rewrite that eats a neighbouring block is silent: the file still parses,
    # `wss validate` still passes, and the gates are simply gone. The first
    # version of this function was written `(?ms)`, where `.` matches newlines,
    # and it deleted the whole gates block. Check the keys survived.
    lost = [k for k in re.findall(r"(?m)^([a-z_]+):", text) if not re.search(rf"(?m)^{k}:", new)]
    if lost:
        raise SystemExit(f"  rewrite dropped top-level key(s): {lost} — refusing to write")
    new = re.sub(r"^  \d[\d,]* projects over \d+ pages on \d{4}-\d{2}-\d{2}\.",
                 f"  {total:,} projects over {n} pages on "
                 f"{time.strftime('%Y-%m-%d', time.gmtime())}.", new, count=1, flags=re.M)
    REG.write_text(new)
    print(f"  wrote {n} endpoint(s) for {total:,} projects")
    print("  CHANGED" if known != n else "  unchanged page count")


if __name__ == "__main__":
    main()
