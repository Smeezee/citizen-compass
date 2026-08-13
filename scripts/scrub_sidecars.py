#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scrub_sidecars.py - strip leaked identifiers out of capture sidecars already on disk.

WHAT THIS IS FOR
================

`gamelog.go` used to write `location_candidates[]` - the raw Game.log lines it
could not parse into a location - straight into every sidecar. In the main menu
the parser worked and the field stayed empty; in-world it never worked, so every
in-world capture shipped ~40 raw lines carrying playerGEID, the account handle
and shard ids. That is the one field in the whole tool that ever bypassed
allow-listing.

The writer is fixed and the export path now refuses these files (see
`sidecarPrivacyRefusal` in export.go), so nothing new leaks and nothing old can
leave the machine. This closes the third gap: the files sitting on disk.

RULE 5 - REPORT-ONLY BY DEFAULT
===============================

This touches hundreds of files, so it prints exactly what it would change and
STOPS. It writes nothing without --apply, and --apply takes a verified backup
first (rule 4). Run the dry run, read the list, then decide.

    python scripts/scrub_sidecars.py                 # report only, writes nothing
    python scripts/scrub_sidecars.py --apply         # backup, verify, then rewrite

WHAT IT REMOVES, AND WHAT IT DELIBERATELY DOES NOT
==================================================

Removes the `location_candidates` key wherever it appears, and nothing else. It
does NOT attempt to find and redact identifiers inside other free-text fields -
that is the name-detection heuristic the order explicitly rules out, and it
would produce a scrubber everyone trusts and nobody can verify.

If a file still fails the check after scrubbing, it is REPORTED, not forced. A
file this script cannot make clean is one a human should look at, and the export
guard is still refusing it in the meantime.

Rule 15: encodings stated.
"""
import argparse
import datetime
import io
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
CAPTURES = os.path.join(ROOT, "citizen-collector", "captures")

# The same shapes export.go refuses, so "clean" means the same thing in both
# places. A file this says is clean must be one the guard would admit.
RAW_LINE = re.compile(r"<\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
HANDLE = re.compile(r"\b(Handle|Player|nickname)\[")


def walk(doc, keys, values):
    """Collect every key and every string value, matching export.go's walk."""
    if isinstance(doc, dict):
        for k, v in doc.items():
            keys.append(k)
            walk(v, keys, values)
    elif isinstance(doc, list):
        for v in doc:
            walk(v, keys, values)
    elif isinstance(doc, str):
        values.append(doc)


def offences(doc):
    """Every reason export.go would refuse this document. Empty means clean.

    KEYS AND VALUES ARE CHECKED DIFFERENTLY, matching scanKey and
    scanForIdentifiers. location_candidates is a field name; a VALUE mentioning
    it is the stale location_reason prose - "see location_candidates[] for the
    raw lines" - which describes the field rather than carrying it. Treating
    that as a leak made every affected file unfixable: strip the array and the
    description still tripped the rule.
    """
    keys, values = [], []
    walk(doc, keys, values)
    out = []
    if any("location_candidates" in k for k in keys):
        out.append("location_candidates")
    joined = "\n".join(values)
    if "playerGEID" in joined:
        out.append("playerGEID")
    if RAW_LINE.search(joined):
        out.append("raw log line")
    m = HANDLE.search(joined)
    if m:
        out.append("account handle in " + m.group(1) + "[]")
    return out


def strip(doc):
    """Remove location_candidates anywhere in the structure. Returns True if
    anything was removed."""
    changed = False
    if isinstance(doc, dict):
        if "location_candidates" in doc:
            del doc["location_candidates"]
            changed = True
        for v in doc.values():
            if strip(v):
                changed = True
    elif isinstance(doc, list):
        for v in doc:
            if strip(v):
                changed = True
    return changed


def say(line):
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="actually rewrite (takes a verified backup first)")
    ap.add_argument("--dir", default=CAPTURES)
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        sys.exit("no captures directory at %s" % args.dir)

    files = sorted(f for f in os.listdir(args.dir)
                   if f.endswith(".json") and f != "gamelog-dataset.json")
    if not files:
        sys.exit("no sidecars found in %s" % args.dir)

    dirty, clean, unreadable = [], 0, []
    for name in files:
        p = os.path.join(args.dir, name)
        try:
            doc = json.loads(io.open(p, encoding="utf-8").read())
        except Exception as e:
            unreadable.append((name, str(e)))
            continue
        off = offences(doc)
        if off:
            dirty.append((name, off))
        else:
            clean += 1

    say("sidecars:   %d" % len(files))
    say("clean:      %d" % clean)
    say("leaking:    %d" % len(dirty))
    if unreadable:
        say("unreadable: %d" % len(unreadable))

    tally = {}
    for _, off in dirty:
        for o in off:
            tally[o] = tally.get(o, 0) + 1
    if tally:
        say("\nwhat was found:")
        for k in sorted(tally, key=lambda k: -tally[k]):
            say("  %-28s %d file(s)" % (k, tally[k]))

    if dirty:
        say("\nfirst 15 affected files:")
        for name, off in dirty[:15]:
            say("  %-46s %s" % (name, ", ".join(off)))
        if len(dirty) > 15:
            say("  ... and %d more" % (len(dirty) - 15))

    if not args.apply:
        say("\nREPORT ONLY - nothing was written.")
        say("Re-run with --apply to back up and rewrite these %d file(s)."
            % len(dirty))
        return 0

    if not dirty:
        say("\nnothing to do.")
        return 0

    # RULE 4: a verified backup before an irreversible bulk rewrite.
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(ROOT, "_to_delete", "sidecars_before_scrub_" + stamp)
    os.makedirs(backup, exist_ok=True)
    for name, _ in dirty:
        shutil.copy2(os.path.join(args.dir, name), os.path.join(backup, name))

    # A backup that ran is not a backup that worked.
    missing = [n for n, _ in dirty
               if not os.path.exists(os.path.join(backup, n))
               or os.path.getsize(os.path.join(backup, n))
               != os.path.getsize(os.path.join(args.dir, n))]
    if missing:
        sys.exit("BACKUP INCOMPLETE - %d file(s) did not copy correctly. "
                 "Nothing was rewritten." % len(missing))
    say("\nbacked up %d file(s) to %s (verified)"
        % (len(dirty), os.path.relpath(backup, ROOT)))

    rewritten, still_dirty, failed = 0, [], []
    for name, _ in dirty:
        p = os.path.join(args.dir, name)
        try:
            doc = json.loads(io.open(p, encoding="utf-8").read())
        except Exception as e:
            failed.append((name, "not valid JSON: %s" % e))
            continue
        strip(doc)
        left = offences(doc)
        text = json.dumps(doc, indent=2, ensure_ascii=False)
        if left:
            # NOT FORCED. Anything still failing is a human's problem, and the
            # export guard is refusing it in the meantime.
            still_dirty.append((name, left))
            continue
        io.open(p, "w", encoding="utf-8", newline="\n").write(text + "\n")
        rewritten += 1

    say("rewritten:  %d" % rewritten)
    if still_dirty:
        say("STILL LEAKING after scrubbing - left untouched, and the export "
            "guard still refuses them:")
        for name, left in still_dirty[:20]:
            say("  %-46s %s" % (name, ", ".join(left)))
    if failed:
        say("could not be read as JSON, left untouched:")
        for name, why in failed[:20]:
            say("  %-46s %s" % (name, why))
    return 1 if (still_dirty or failed) else 0


if __name__ == "__main__":
    sys.exit(main())
