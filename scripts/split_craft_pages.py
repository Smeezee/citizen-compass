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
Not primarily size - WO-3 already decided it. WO-3 leads with the best source,
then a grouped summary, with the full list behind a disclosure. So the field
carrying two-thirds of the payload is the one the page does not render until
someone asks for it. Shipping it inline is paying for markup nobody requested.

The distribution says the same thing. Over all 1,597 rows with `sources`
inline:

    p50 2,191   p90 12,690   p99 63,706   max 91,648 bytes    74 rows > 20 KB

p99 is 29x the median. The tail is entirely sources: the worst row is 127
sources at 90,637 bytes, 99% of its own row, and the next four are ~80 KB at
98%. Splitting per blueprint alone would move that tail from one file into 74
of them rather than removing it.

By field: sources 66.6%, modifiers 14.2%, ingredients 7.0%, everything else
12.2%.

And because 873 of 1,597 blueprints (54.7%) have an EMPTY source list, a
sources file is written ONLY where there is something to write - 724 files
instead of 1,597. An empty file per blueprint would be 873 requests that can
only ever return "[]". The page carries `source_count`, so a client knows
whether to fetch without probing for a 404.

OUTPUT
------
    blueprints/<key>.json          body + summarised source block  1,597 files
    blueprints/<key>.sources.json  full list, fetched on disclosure  724 files
    items/<id>.json                one item description            5,344 files
    blueprints/_list.json          minimal listing for the index page

Run: venv/Scripts/python.exe scripts/split_craft_pages.py
"""

import collections
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


def summarise(r):
    """C2's summarise(), reused verbatim from docs/workorder-craft-01.md rather
    than reimplemented - a second implementation of the same shape is a second
    thing to drift."""
    s = r["sources"]
    if r["source_kind"] != "contract" or not s:
        return None
    floor = lambda x: (((x.get("reputation") or {}).get("MinStanding") or {})
                       .get("MinReputation") or 0)
    best = sorted(s, key=lambda x: (-(x.get("chance") or 0), floor(x)))[0]
    rep = best.get("reputation") or {}
    return {"total": len(s),
            "best": {"title": best.get("title"), "giver": best.get("giver"),
                     "mission_type": best.get("mission_type"),
                     "chance": best.get("chance"), "illegal": best.get("illegal"),
                     "standing": (rep.get("MinStanding") or {}).get("Name"),
                     "faction": rep.get("Faction")},
            "givers": collections.Counter(x.get("giver") for x in s).most_common(),
            "mission_types": collections.Counter(x.get("mission_type") for x in s).most_common(),
            "others": len(s) - 1}


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
    fresh(IT_OUT)

    listing, n_src = [], 0
    for row in blueprints:
        key = row["blueprint_key"]
        sources = row.get("sources") or []

        # The page carries the SUMMARISED source block, not the list. WO-3
        # leads with the best source, then a grouped summary, then the full
        # list behind a disclosure - so the field carrying two-thirds of the
        # payload is the one the page does not render until someone asks.
        # summarise() is C2's, reused verbatim rather than reimplemented.
        page = {k: v for k, v in row.items() if k != "sources"}
        page["source_summary"] = summarise(row)
        page["source_count"] = len(sources)
        write_json(os.path.join(BP_OUT, key + ".json"), page)

        if sources:
            write_json(os.path.join(BP_OUT, key + ".sources.json"), sources)
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

    def sizes_in(d, suffix, exclude=None):
        out = []
        for f in os.listdir(d):
            if not f.endswith(suffix):
                continue
            if exclude and f.endswith(exclude):
                continue
            # _list.json is the index listing, not a page. At ~250 KB it would
            # become the reported max and corrupt the page distribution - the
            # one number this split exists to move.
            if f.startswith("_"):
                continue
            out.append(os.path.getsize(os.path.join(d, f)))
        return sorted(out)

    def q(v, p):
        return v[max(0, min(len(v) - 1, int(round(p / 100 * (len(v) - 1)))))]

    pages = sizes_in(BP_OUT, ".json", exclude=".sources.json")
    pages = [s for s in pages]
    srcs = sizes_in(BP_OUT, ".sources.json")
    itms = sizes_in(IT_OUT, ".json")

    n_pages = len(blueprints)
    print("blueprint pages : %5d  (%.2f MB)" % (n_pages, sum(pages) / 1048576))
    print("sources files   : %5d  (%.2f MB)  %d blueprints have none"
          % (n_src, sum(srcs) / 1048576, n_pages - n_src))
    print("item files      : %5d  (%.2f MB)" % (len(items), sum(itms) / 1048576))
    print()
    print("POST-SPLIT DISTRIBUTION (bytes) - p99 is the number that matters")
    for label, v in (("page (fetched always)", pages),
                     ("sources (on disclosure)", srcs),
                     ("item", itms)):
        if not v:
            continue
        print("   %-24s p50 %7s  p90 %7s  p99 %7s  max %7s   over20KB %d"
              % (label, f"{q(v,50):,}", f"{q(v,90):,}", f"{q(v,99):,}",
                 f"{v[-1]:,}", sum(1 for s in v if s > 20000)))
    print("_list.json      :        (%.1f KB)" % (os.path.getsize(os.path.join(BP_OUT, "_list.json")) / 1024))
    print("TOTAL FILES     : %5d" % (n_pages + n_src + len(items) + 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
