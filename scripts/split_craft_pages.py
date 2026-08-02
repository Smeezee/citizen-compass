"""
Split the combined craft indexes into per-page files.

WHY THIS EXISTS
---------------
The file-count check said crafting fits: ~1,600 pages against a 20,000 cap.
That was true and it was the wrong measurement. It costed FILES, not BYTES.

`blueprint_index.json` is 10.91 MB. If a browser renders blueprint pages from
that bundled index, every visitor downloads 10.91 MB before seeing anything -
and no file-count check would ever have surfaced it.

So: page-per-file is a requirement, not a preference. The combined indexes stay
as BUILD ARTIFACTS for derivation; they must never be what a browser fetches.

WHY SOURCES GET THEIR OWN FILE
------------------------------
Splitting per blueprint alone does NOT fix the tail. Measured over all 1,597
rows, with `sources` inline:

    p50 2,191   p90 12,690   p95 18,334   p99 63,706   max 91,648 bytes

p99 is 63 KB - 29x the median - because a handful of blueprints carry very long
source lists (the worst is 127 sources at 90,637 bytes, 99% of its own row).
A mean of 7 KB with a 90 KB tail is two different problems, and only one of
them is solved by splitting.

With `sources` moved to a sibling file:

    p50 1,868   p90 2,311   p95 2,962   p99 3,040   max 3,284 bytes

The distribution collapses: nothing exceeds 3.3 KB, and files over 20 KB go
from 74 to zero. That is what makes the page cheap to fetch.

And because 873 of 1,597 blueprints (54.7%) have an EMPTY source list, a
sources file is written ONLY where there is something to write - 724 files
instead of 1,597. An empty file per blueprint would be 873 requests that can
only ever return "[]".

OUTPUT
------
    blueprints/<key>.json          page data, no sources        1,597 files
    blueprints/sources/<key>.json  lazy-loaded source list        724 files
    items/<id>.json                one item description         5,344 files
    blueprints/_list.json          minimal listing for the index page

Run: venv/Scripts/python.exe scripts/split_craft_pages.py
"""

import json
import os
import re
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(REPO, "data-layer", "processed")
BP_IN = os.path.join(PROC, "blueprint_index.json")
IT_IN = os.path.join(PROC, "item_descriptions.json")

BP_OUT = os.path.join(PROC, "blueprints")
SRC_OUT = os.path.join(BP_OUT, "sources")
IT_OUT = os.path.join(PROC, "items")

SAFE = re.compile(r"[A-Za-z0-9._-]+")


def read_json(path):
    if not os.path.exists(path):
        sys.exit("BUILD INPUT MISSING: %s\nNothing was written." % path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, obj):
    # separators drop the whitespace the combined file carries, and newline=''
    # keeps the bytes identical on every platform - the same reproducibility
    # trap that made build_deploy.py emit CRLF on Windows and LF elsewhere.
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def fresh(d):
    """Rebuild the output directory from scratch so a removed blueprint cannot
    leave a stale page behind. A file that survives because it was written once
    is exactly the orphan problem this project keeps finding."""
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)


def main():
    blueprints = read_json(BP_IN)
    items = read_json(IT_IN)

    if not isinstance(blueprints, list) or not blueprints:
        sys.exit("blueprint_index.json is not a non-empty list. Nothing was written.")
    if not isinstance(items, dict) or not items:
        sys.exit("item_descriptions.json is not a non-empty object. Nothing was written.")

    keys = [r.get("blueprint_key") for r in blueprints]
    if not all(keys):
        sys.exit("some blueprint rows have no blueprint_key - refusing to guess a filename.")
    if len(set(keys)) != len(keys):
        sys.exit("blueprint_key values are not unique - pages would overwrite each other.")
    unsafe = [k for k in keys if not SAFE.fullmatch(k)]
    if unsafe:
        sys.exit("blueprint_key values unsafe as filenames: %s" % unsafe[:5])
    unsafe_items = [k for k in items if not SAFE.fullmatch(str(k))]
    if unsafe_items:
        sys.exit("item keys unsafe as filenames: %s" % unsafe_items[:5])

    fresh(BP_OUT)
    os.makedirs(SRC_OUT)
    fresh(IT_OUT)

    listing, n_src = [], 0
    for row in blueprints:
        key = row["blueprint_key"]
        sources = row.get("sources") or []
        page = {k: v for k, v in row.items() if k != "sources"}
        page["has_sources"] = bool(sources)
        page["source_count"] = len(sources)
        write_json(os.path.join(BP_OUT, key + ".json"), page)

        if sources:
            write_json(os.path.join(SRC_OUT, key + ".json"), sources)
            n_src += 1

        listing.append({
            "blueprint_key": key,
            "output_name": row.get("output_name"),
            "output_type": row.get("output_type"),
            "output_grade": row.get("output_grade"),
            "source_count": len(sources),
        })

    listing.sort(key=lambda r: (r["output_name"] or "", r["blueprint_key"]))
    write_json(os.path.join(BP_OUT, "_list.json"), listing)

    for k, v in items.items():
        write_json(os.path.join(IT_OUT, str(k) + ".json"), v)

    def total(d):
        return sum(os.path.getsize(os.path.join(r, f))
                   for r, _, fs in os.walk(d) for f in fs)

    n_pages = len(blueprints)
    print("blueprint pages : %5d  (%.2f MB)" % (n_pages, (total(BP_OUT) - total(SRC_OUT)) / 1048576))
    print("sources files   : %5d  (%.2f MB)  %d blueprints have none"
          % (n_src, total(SRC_OUT) / 1048576, n_pages - n_src))
    print("item files      : %5d  (%.2f MB)" % (len(items), total(IT_OUT) / 1048576))
    print("_list.json      :        (%.1f KB)" % (os.path.getsize(os.path.join(BP_OUT, "_list.json")) / 1024))
    print("TOTAL FILES     : %5d" % (n_pages + n_src + len(items) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
