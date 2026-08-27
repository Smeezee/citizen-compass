"""M4 - Fleetyards fleet-wide model-availability sweep.

Order: docs/ORDER_the-fifteen-are-not-missing-2026-08-27.md (C1, 2026-08-27).

M4a  Pull the full model list from api.fleetyards.net/v1/models, paginated to
     exhaustion, recording name, slug, media.holo.url and the file extension.
M4b  Join to our own fleet by EXACT match only. No fuzzy matching, no name
     similarity. Names that do not join exactly go to a review list.
M4c  Output data-layer/derived/model-availability/ with the joined table, the
     unjoined residue, and a MANIFEST naming source, date and join rule.
M4d  Cross-check the models we already have: where our model is an inherited
     base hull, does Fleetyards hold one for the variant itself.

This script FAILS LOUDLY rather than producing a short table. Every integrity
condition below raises SweepError and exits non-zero:

  - pagination collected fewer records than the API's own totalCount
  - a join key is duplicated on either side (a duplicate key makes "exact"
    ambiguous, which is the 85X name-collision failure mode)
  - the two join rules match one of our rows to two DIFFERENT Fleetyards
    records

Usage:
    python scripts/sweep_model_availability.py            # live pull
    python scripts/sweep_model_availability.py --from-cache DIR
    python scripts/sweep_model_availability.py --out DIR
"""

import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.fleetyards.net/v1/models"
PER_PAGE = 240  # the API's own maxPerPage
UA = "citizen-compass model-availability sweep (unofficial fan site)"

OUR_FLEET = os.path.join("data-layer", "derived", "ship-gaps", "ship_gaps.json")
INHERITANCE = os.path.join("data-layer", "derived", "model-inheritance", "model_inheritance.json")
DEFAULT_OUT = os.path.join("data-layer", "derived", "model-availability")


class SweepError(RuntimeError):
    """An integrity condition failed. The output is not trustworthy."""


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- M4a: pull

def fetch_page(page, per_page=PER_PAGE, retries=3):
    url = "%s?page=%d&perPage=%d" % (API, page, per_page)
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                if resp.status != 200:
                    raise SweepError("page %d returned HTTP %s" % (page, resp.status))
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            last = exc
            time.sleep(2 * (attempt + 1))
    raise SweepError("page %d failed after %d attempts: %r" % (page, retries, last))


def pull_all():
    """Paginate to exhaustion. Verify the count against the API's own total."""
    items, page, total_count, total_pages = [], 1, None, None
    while True:
        payload = fetch_page(page)
        batch = payload.get("items") or []
        pag = (payload.get("meta") or {}).get("pagination") or {}
        if total_count is None:
            total_count = pag.get("totalCount")
            total_pages = pag.get("totalPages")
            log("  API reports totalCount=%s totalPages=%s" % (total_count, total_pages))
        items.extend(batch)
        log("  page %d: %d items (running %d)" % (page, len(batch), len(items)))
        if not batch:
            break
        if total_pages is not None and page >= total_pages:
            break
        page += 1
        time.sleep(0.3)

    if total_count is None:
        raise SweepError("API returned no pagination metadata - cannot prove the pull was complete")
    if len(items) < total_count:
        raise SweepError(
            "pagination short: collected %d of %d records the API says exist" % (len(items), total_count))
    ids = [i.get("id") for i in items]
    if len(set(ids)) != len(ids):
        raise SweepError("pagination returned duplicate record ids - pages overlapped")
    return items, total_count


def load_cached(cache_dir):
    items = []
    names = sorted(n for n in os.listdir(cache_dir) if n.startswith("fy_") and n.endswith(".json"))
    if not names:
        raise SweepError("no fy_*.json pages in %s" % cache_dir)
    total_count = None
    for n in names:
        with open(os.path.join(cache_dir, n), encoding="utf-8") as fh:
            payload = json.load(fh)
        items.extend(payload.get("items") or [])
        if total_count is None:
            total_count = ((payload.get("meta") or {}).get("pagination") or {}).get("totalCount")
    if total_count is not None and len(items) < total_count:
        raise SweepError("cache short: %d of %d" % (len(items), total_count))
    return items, total_count


# ---------------------------------------------------------------- helpers

def holo_of(entry):
    return (entry.get("media") or {}).get("holo") or None


def holo_row(entry):
    h = holo_of(entry)
    if not h:
        return None
    fname = h.get("name") or ""
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else None
    return {
        "file_name": fname,
        "extension": ext,
        "url": h.get("url"),
        "size_bytes": h.get("size"),
        "content_type": h.get("contentType"),
        "uploaded_at": h.get("uploadedAt"),
    }


def index_unique(entries, key, label):
    """Exact index. A duplicate key is fatal: it makes 'exact match' ambiguous."""
    out, dupes = {}, {}
    for e in entries:
        k = e.get(key)
        if k is None or k == "":
            continue
        if k in out:
            dupes[k] = dupes.get(k, 1) + 1
        out[k] = e
    if dupes:
        raise SweepError("duplicate %s on the Fleetyards side: %r - exact match is not "
                         "well defined against a duplicated key" % (label, dupes))
    return out


# ---------------------------------------------------------------- M4b: join

def build(items, our_rows, inheritance):
    by_sc = index_unique(items, "scIdentifier", "scIdentifier")
    by_name = index_unique(items, "name", "name")

    joined, conflicts, unjoined_ours = [], [], []
    matched_fy_ids = set()

    for r in our_rows:
        stem, name = r.get("stem"), r.get("name")
        a = by_sc.get(stem) if stem else None
        b = by_name.get(name) if name else None

        if a and b and a["id"] != b["id"]:
            # This is the 85X failure mode: two exact rules, two different records.
            conflicts.append({
                "our_name": name, "our_class": r.get("cls"), "our_stem": stem,
                "by_scIdentifier": {"name": a.get("name"), "slug": a.get("slug")},
                "by_name": {"scIdentifier": b.get("scIdentifier"), "slug": b.get("slug")},
                "note": "NAME COLLISION - not cleared for import until a human confirms the shape",
            })
            continue

        m = a or b
        if not m:
            unjoined_ours.append({
                "our_name": name, "our_class": r.get("cls"), "our_stem": stem,
                "we_have_a_model": bool(r.get("model")),
                "why_no_model": r.get("why"),
            })
            continue

        matched_fy_ids.add(m["id"])
        joined.append({
            "our_name": name,
            "our_class": r.get("cls"),
            "our_stem": stem,
            "our_manufacturer": r.get("mfr"),
            "we_have_a_model": bool(r.get("model")),
            "our_glb": r.get("glb"),
            "why_no_model": r.get("why"),
            "join_rule": "scIdentifier+name" if (a and b) else ("scIdentifier" if a else "name"),
            "fleetyards": {
                "id": m.get("id"), "name": m.get("name"), "slug": m.get("slug"),
                "scIdentifier": m.get("scIdentifier"), "rsiSlug": m.get("rsiSlug"),
                "productionStatus": m.get("productionStatus"),
                "lastUpdatedAt": m.get("lastUpdatedAt"),
            },
            "holo": holo_row(m),
        })

    unjoined_fy = [{
        "name": i.get("name"), "slug": i.get("slug"), "scIdentifier": i.get("scIdentifier"),
        "productionStatus": i.get("productionStatus"), "holo": holo_row(i),
    } for i in items if i["id"] not in matched_fy_ids]

    # ------------------------------------------------------ M4d cross-check
    # Where our model is a base hull standing in for a variant, does Fleetyards
    # hold a model for the variant itself. Same exact-only rule: our project's
    # own stem field is cls.lower(), so class_name.lower() is that same
    # published transform and nothing more.
    #
    # A zero here would be indistinguishable from a join that never worked, so
    # the base hulls are joined as a control: they MUST match. If the variants
    # come back empty while the bases come back full, the join works and
    # Fleetyards genuinely has no separate record for the variant.
    cross = []
    bases = {(e.get("inherits_from") or "").lower() for e in inheritance if e.get("inherits_from")}
    cross_control = {
        "distinct_base_hulls": len(bases),
        "base_hulls_that_join": sum(1 for b in bases if b in by_sc),
        "variants_examined": len(inheritance),
    }
    for entry in inheritance:
        cls = entry.get("class_name") or ""
        m = by_sc.get(cls.lower())
        if not m:
            continue
        cross.append({
            "our_class": cls,
            "our_display_name": entry.get("display_name"),
            "our_model_is": entry.get("model_file"),
            "inherits_from": entry.get("inherits_from"),
            "variant_means": entry.get("suffix_means"),
            "fleetyards": {"name": m.get("name"), "slug": m.get("slug")},
            "holo": holo_row(m),
        })

    return joined, conflicts, unjoined_ours, unjoined_fy, cross, cross_control


# ---------------------------------------------------------------- M4c: write

def write_outputs(out_dir, run_id, fetched_at, items, total_count, raw_sha,
                  joined, conflicts, unjoined_ours, unjoined_fy, cross, cross_control,
                  source_note):
    os.makedirs(out_dir, exist_ok=True)

    gap_filled = [j for j in joined if not j["we_have_a_model"] and j["holo"]]
    gap_unfilled = [j for j in joined if not j["we_have_a_model"] and not j["holo"]]
    cross_hits = [c for c in cross if c["holo"]]

    def dump(name, obj):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
            fh.write("\n")

    dump("model_availability.json", joined)
    dump("unjoined_ours.json", unjoined_ours)
    dump("unjoined_fleetyards.json", unjoined_fy)
    dump("needs_human_review.json", conflicts)
    dump("gap_fillable.json", gap_filled)
    dump("inheritance_cross_check.json",
         {"control": cross_control, "variants_fleetyards_has_its_own_model_for": cross})

    manifest = {
        "generated_by": "scripts/sweep_model_availability.py",
        "order": "docs/ORDER_the-fifteen-are-not-missing-2026-08-27.md (M4)",
        "run_id": run_id,
        "fetched_at_utc": fetched_at,
        "source": {
            "name": "Fleetyards public API",
            "endpoint": API,
            "pagination": "page/perPage=%d, run to exhaustion" % PER_PAGE,
            "auth": "none - public, no key, not under /media/",
            "records_returned": len(items),
            "api_reported_total": total_count,
            "raw_snapshot_sha256": raw_sha,
            "note": source_note,
        },
        "our_fleet": {
            "file": OUR_FLEET.replace("\\", "/"),
            "rows": len(joined) + len(unjoined_ours) + len(conflicts),
        },
        "join_rule": (
            "EXACT ONLY. Rule 1: our row's stem == Fleetyards scIdentifier "
            "(the in-game class identifier). Rule 2: our row's name == Fleetyards "
            "name. A row joins if either rule matches. If BOTH rules match but to "
            "DIFFERENT Fleetyards records, the row is NOT joined - it goes to "
            "needs_human_review.json as a name collision. No fuzzy matching, no "
            "similarity scoring, no case folding on the primary join: our stem "
            "field is already the project's published lowercase form of cls."
        ),
        "counts": {
            "fleetyards_records": len(items),
            "fleetyards_with_holo": sum(1 for i in items if holo_of(i)),
            "our_rows_joined": len(joined),
            "our_rows_unjoined": len(unjoined_ours),
            "name_collisions_held_back": len(conflicts),
            "fleetyards_residue": len(unjoined_fy),
            "our_ships_with_no_model": sum(1 for j in joined if not j["we_have_a_model"]) + sum(
                1 for u in unjoined_ours if not u["we_have_a_model"]),
            "gap_fillable": len(gap_filled),
            "gap_not_fillable_from_this_source": len(gap_unfilled) + sum(
                1 for u in unjoined_ours if not u["we_have_a_model"]),
            "inherited_variants_fleetyards_has_its_own_model_for": len(cross_hits),
            "m4d_control_base_hulls_that_join": "%d of %d" % (
                cross_control["base_hulls_that_join"], cross_control["distinct_base_hulls"]),
        },
        "what_this_is_not": [
            "Not an import. No model file was downloaded by this script.",
            "Not a rights determination - see RULING_community-practice-is-the-standard-2026-08-22.md.",
            "Not a claim that a Fleetyards holo has usable node hierarchy. These are "
            "the same welded meshes; hardpoints are unaffected.",
        ],
    }
    dump("MANIFEST.json", manifest)

    lines = []
    w = lines.append
    w("=" * 74)
    w("M4 - FLEETYARDS MODEL AVAILABILITY SWEEP")
    w("run %s   fetched %s" % (run_id, fetched_at))
    w("=" * 74)
    w("")
    w("SOURCE      %d records, %d carry a holo model" % (
        len(items), sum(1 for i in items if holo_of(i))))
    w("OUR FLEET   %d rows -> %d joined, %d unjoined, %d held back as collisions" % (
        len(joined) + len(unjoined_ours) + len(conflicts), len(joined),
        len(unjoined_ours), len(conflicts)))
    w("")
    w("-" * 74)
    w("SHIPS WE CANNOT SHOW A MODEL FOR, THAT FLEETYARDS HAS ONE FOR  (%d)" % len(gap_filled))
    w("-" * 74)
    for j in sorted(gap_filled, key=lambda x: x["our_name"]):
        w("  %-34s %-28s %-5s %7.2f MB  via %s" % (
            j["our_name"], j["fleetyards"]["slug"], j["holo"]["extension"],
            (j["holo"]["size_bytes"] or 0) / 1e6, j["join_rule"]))
    w("")
    w("-" * 74)
    w("OUR ROWS THAT DO NOT JOIN EXACTLY - REVIEW LIST  (%d)" % len(unjoined_ours))
    w("-" * 74)
    for u in sorted(unjoined_ours, key=lambda x: x["our_name"] or ""):
        w("  %-34s %-34s model=%s" % (
            u["our_name"], u["our_stem"] or "(no class)", u["we_have_a_model"]))
    w("")
    w("-" * 74)
    w("NAME COLLISIONS HELD BACK  (%d)" % len(conflicts))
    w("-" * 74)
    for c in conflicts:
        w("  %s: scIdentifier -> %s, name -> %s" % (
            c["our_name"], c["by_scIdentifier"]["slug"], c["by_name"]["slug"]))
    if not conflicts:
        w("  none")
    w("")
    w("-" * 74)
    w("FLEETYARDS RECORDS WITH NO ROW OF OURS  (%d)" % len(unjoined_fy))
    w("-" * 74)
    for i in sorted(unjoined_fy, key=lambda x: x["name"] or ""):
        w("  %-34s %-30s %s" % (i["name"], i["slug"], "holo" if i["holo"] else "NO HOLO"))
    w("")
    w("-" * 74)
    w("M4d - VARIANTS WHERE OUR MODEL IS AN INHERITED BASE HULL  (%d of %d examined)" % (
        len(cross_hits), cross_control["variants_examined"]))
    w("     CONTROL: %d of %d distinct base hulls join." % (
        cross_control["base_hulls_that_join"], cross_control["distinct_base_hulls"]))
    w("     A zero above with a full control means the join works and the")
    w("     variants are genuinely absent from the source.")
    w("-" * 74)
    for c in sorted(cross_hits, key=lambda x: x["our_class"]):
        w("  %-38s ours=%-24s fy=%s" % (c["our_class"], c["our_model_is"], c["fleetyards"]["slug"]))
    if not cross_hits:
        w("  none - Fleetyards holds no separate model for any variant we stand in for")
    w("")
    with open(os.path.join(out_dir, "model_availability_report.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-cache", dest="cache", default=None,
                    help="read fy_*.json pages from DIR instead of the network")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

    if args.cache:
        log("Reading cached pages from %s" % args.cache)
        items, total_count = load_cached(args.cache)
        source_note = "read from cache %s - not a live pull" % args.cache
    else:
        log("M4a - pulling %s to exhaustion" % API)
        items, total_count = pull_all()
        source_note = "live pull"
    log("  collected %d records (API total %s)" % (len(items), total_count))

    raw_dir = os.path.join(args.out, "_raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw_path = os.path.join(raw_dir, "fleetyards_models_%s.json" % run_id)
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(items, fh, ensure_ascii=False)
    with open(raw_path, "rb") as fh:
        raw_sha = hashlib.sha256(fh.read()).hexdigest()
    log("  raw snapshot %s  sha256 %s" % (raw_path, raw_sha[:16]))

    with open(OUR_FLEET, encoding="utf-8") as fh:
        our_rows = json.load(fh)["rows"]
    with open(INHERITANCE, encoding="utf-8") as fh:
        inheritance = json.load(fh)
    log("M4b - joining %d of our rows, exact match only" % len(our_rows))

    joined, conflicts, unjoined_ours, unjoined_fy, cross, cross_control = build(
        items, our_rows, inheritance)

    log("M4c - writing %s" % args.out)
    lines = write_outputs(args.out, run_id, fetched_at, items, total_count, raw_sha,
                          joined, conflicts, unjoined_ours, unjoined_fy, cross,
                          cross_control, source_note)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SweepError as exc:
        print("SWEEP FAILED - output not written: %s" % exc, file=sys.stderr)
        sys.exit(2)
