#!/usr/bin/env python3
"""
C5 - the patch diff. What changed between two sealed snapshots.

    python build_patch_diff.py --from <snapshot> --to <snapshot> [--no-items]

THIS IS THE ARTIFACT NOBODY ELSE PUBLISHES. Every fan site says what the game
contains today. None of them says what changed, with both sides named down to
the build number and the join done on IDs.

RULES IT FOLLOWS, AND EACH ONE IS A THING THAT WOULD OTHERWISE GO WRONG
=======================================================================

JOIN ON IDs, NEVER NAMES. A ship's UUID is its identity; its Name is a label
that CIG rewords between patches. A name join reports a rename as a removal
plus an addition, and reports two ships sharing a display name as one - both
of which manufacture change that did not happen.

NAME BOTH BUILDS BY THEIR COMMIT SUBJECT. Not "4.9" and "4.10". The upstream
repository's head commit subject IS the game build - `4.9.0-LIVE.12232306` -
and it is read out of each snapshot's own manifest. A diff whose sides are
labelled "about 4.9, we think" is not evidence of anything.

DISTINGUISH A GAME CHANGE FROM A SCHEMA CHANGE. A field that appears because
upstream started emitting it is NOT a patch change, and counting it as one
poisons every number in the summary. So a field missing from the OLD snapshot
ENTIRELY - not just from this record - is reported separately as a schema
change, never as "the game changed this".

IT REPORTS. IT NEVER WRITES TO THE CATALOGUE. Auditor rule. Everything lands
under data-layer/derived/patch-diff/ and nothing else is touched.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(REPO, "data-layer", "derived", "patch-diff")
# A TEST SEAM, THE SAME SHAPE THE REST OF THIS REPO ALREADY USES (CC_GEO_DIR,
# CC_FLEET_MATCHED, CC_VIEWER). C5b has to build a snapshot with a KNOWN
# planted change, and that snapshot needs a manifest naming its build - but a
# control must never write into the tracked manifest tree to get one.
MAN_ROOT = os.environ.get("CC_MANIFEST_DIR") or os.path.join(
    REPO, "data-layer", "external-source-manifests")


def die(msg):
    print("STOPPED: " + msg)
    sys.exit(1)


def load_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def build_name(snapshot_dir):
    """The build this snapshot IS, from its own manifest. Never guessed."""
    run_id = os.path.basename(snapshot_dir.rstrip("/\\"))
    man_dir = os.path.join(MAN_ROOT, run_id)
    if os.path.isdir(man_dir):
        for f in sorted(os.listdir(man_dir)):
            if not f.endswith(".json"):
                continue
            try:
                m = load_json(os.path.join(man_dir, f))
            except Exception:
                continue
            g = m.get("git_metadata_captured_before_stripping") or {}
            subj = g.get("git_head_subject")
            if subj:
                return {"run_id": run_id, "build": subj,
                        "commit": g.get("git_head_commit"),
                        "commit_date": g.get("git_commit_date")}
    # FAIL RATHER THAN GUESS. A diff that cannot say which build a side is
    # should not publish a side.
    die("no manifest with a git_head_subject for snapshot %s. A diff whose "
        "sides are not named down to the build number is not evidence of "
        "anything, so nothing was written." % run_id)


def read_ships(snapshot_dir):
    d = os.path.join(snapshot_dir, "ships")
    if not os.path.isdir(d):
        die("no ships/ in %s" % snapshot_dir)
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"):
            continue
        try:
            r = load_json(os.path.join(d, f))
        except Exception as e:
            die("ships/%s did not parse: %s" % (f, e))
        key = r.get("UUID") or r.get("ClassName")
        if not key:
            continue
        out[key] = r
    return out


def read_items(snapshot_dir):
    p = os.path.join(snapshot_dir, "items.json")
    if not os.path.exists(p):
        return {}
    data = load_json(p)
    rows = data if isinstance(data, list) else list(data.values())
    out = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        key = r.get("UUID") or r.get("uuid") or r.get("ClassName")
        if key:
            out[key] = r
    return out


def flatten(obj, pre=""):
    """Field paths to scalar values. Lists are compared whole, by their JSON,
       because a list's ORDER is meaningful in this data and a per-index diff
       would report an insertion as a change to every element after it."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, pre + k + "."))
    elif isinstance(obj, list):
        out[pre.rstrip(".")] = json.dumps(obj, sort_keys=True)[:4000]
    else:
        out[pre.rstrip(".")] = obj
    return out


def field_universe(records):
    """Every field path that appears ANYWHERE in a side. This is what makes
       'our old snapshot lacked the field' answerable at all."""
    u = set()
    for r in records.values():
        u.update(flatten(r).keys())
    return u


def diff_side(old, new, label):
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    old_fields = field_universe(old)
    new_fields = field_universe(new)

    changed, schema_only = [], []
    for k in sorted(set(old) & set(new)):
        fo, fn = flatten(old[k]), flatten(new[k])
        diffs, schema = [], []
        for path in sorted(set(fo) | set(fn)):
            a, b = fo.get(path, "\0missing"), fn.get(path, "\0missing")
            if a == b:
                continue
            entry = {"field": path,
                     "from": None if a == "\0missing" else a,
                     "to": None if b == "\0missing" else b}
            # THE DISTINCTION THE ORDER INSISTS ON. If this field does not
            # exist anywhere on the old side, its presence now is upstream
            # emitting something new - a schema change, not a patch change.
            if path not in old_fields and path in new_fields:
                entry["why"] = "field absent from the ENTIRE old snapshot - "
                entry["why"] += "upstream started emitting it"
                schema.append(entry)
            elif path in old_fields and path not in new_fields:
                entry["why"] = "field absent from the ENTIRE new snapshot - "
                entry["why"] += "upstream stopped emitting it"
                schema.append(entry)
            else:
                diffs.append(entry)
        ident = {"id": k,
                 "name": (new[k].get("Name") or new[k].get("ClassName")),
                 "class_name": new[k].get("ClassName")}
        if diffs:
            changed.append(dict(ident, changes=diffs))
        if schema:
            schema_only.append(dict(ident, schema_changes=schema))

    def ident_list(keys, src):
        return [{"id": k,
                 "name": (src[k].get("Name") or src[k].get("ClassName")),
                 "class_name": src[k].get("ClassName")} for k in keys]

    print("  %-6s %5d in / %5d out | +%d -%d ~%d (schema-only %d)"
          % (label, len(old), len(new), len(added), len(removed),
             len(changed), len(schema_only)))
    return {"added": ident_list(added, new), "removed": ident_list(removed, old),
            "changed": changed, "schema": schema_only}


def write(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser(description="Diff two sealed snapshots.")
    ap.add_argument("--from", dest="a", required=True)
    ap.add_argument("--to", dest="b", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-items", action="store_true",
                    help="ships only - items.json is 128 MB a side")
    args = ap.parse_args()

    for p in (args.a, args.b):
        if not os.path.isdir(p):
            die("no such snapshot: %s" % p)

    A, B = build_name(args.a), build_name(args.b)
    print("from : %s  (%s)" % (A["build"], A["run_id"]))
    print("to   : %s  (%s)" % (B["build"], B["run_id"]))
    if A["build"] == B["build"]:
        print("NOTE : both sides name the SAME build. A non-empty diff here "
              "would be the tool, not the game.")

    ships = diff_side(read_ships(args.a), read_ships(args.b), "ships")
    if args.no_items:
        items = {"added": [], "removed": [], "changed": [], "schema": []}
        items_note = "NOT COMPARED - --no-items was passed"
    else:
        items = diff_side(read_items(args.a), read_items(args.b), "items")
        items_note = "compared"

    out = args.out or os.path.join(
        OUT_ROOT, "%s__to__%s" % (A["build"], B["build"]))
    os.makedirs(out, exist_ok=True)

    for kind, d in (("ships", ships), ("items", items)):
        for part in ("added", "removed", "changed"):
            write(os.path.join(out, "%s_%s.json" % (kind, part)), d[part])
        write(os.path.join(out, "%s_schema_changes.json" % kind), d["schema"])

    man = {
        "generated_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "build_patch_diff.py",
        "from": A, "to": B,
        "join": "on UUID, never on name",
        "items": items_note,
        "counts": {k: {p: len(v[p]) for p in ("added", "removed", "changed", "schema")}
                   for k, v in (("ships", ships), ("items", items))},
        "reports_only": "This tool never writes to the catalogue.",
    }
    write(os.path.join(out, "MANIFEST.json"), man)

    lines = [
        "# Patch diff - %s to %s" % (A["build"], B["build"]),
        "",
        "    from   %s   commit %s   %s" % (A["build"], (A["commit"] or "?")[:12],
                                            A["commit_date"] or "?"),
        "    to     %s   commit %s   %s" % (B["build"], (B["commit"] or "?")[:12],
                                            B["commit_date"] or "?"),
        "",
        "Joined on UUID, never on name. Items: %s." % items_note,
        "",
        "| | added | removed | changed | schema-only |",
        "|---|---|---|---|---|",
    ]
    for kind, d in (("ships", ships), ("items", items)):
        lines.append("| %s | %d | %d | %d | %d |"
                     % (kind, len(d["added"]), len(d["removed"]),
                        len(d["changed"]), len(d["schema"])))
    lines += ["",
              "**Schema-only** means a field appeared or disappeared across the",
              "WHOLE snapshot - upstream changed what it emits. That is not the",
              "game changing, and it is counted separately so it cannot be read",
              "as one.", ""]
    for kind, d in (("ships", ships), ("items", items)):
        if d["added"]:
            lines.append("## %s added" % kind)
            for r in d["added"][:60]:
                lines.append("- %s (`%s`)" % (r["name"], r["class_name"]))
            lines.append("")
        if d["removed"]:
            lines.append("## %s removed" % kind)
            for r in d["removed"][:60]:
                lines.append("- %s (`%s`)" % (r["name"], r["class_name"]))
            lines.append("")
    with io.open(os.path.join(out, "summary.md"), "w",
                 encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print("written: %s" % os.path.relpath(out, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
