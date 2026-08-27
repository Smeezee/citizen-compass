#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_kb_actions.py - the action browser's data, generated rather than pasted.

Same pattern as build_keybind_modes.py, and for the same reason: the browsing
structure is DERIVED from data-layer/processed/keybinds_site.json, which already
has an owner. Pasting a copy into the page would create a second copy of
information that drifts the first time the source changes, and nothing would
report the drift - it would just quietly show the wrong thing. Rule 14.

WHAT COMES OUT

  KB_ACTIONS        691 labelled actions, each with its category, section,
                    per-action description where one exists, and its bindings.
  KB_CATEGORY_ORDER 9 categories, in first-seen order (the game's order, since
                    keybinds_site.json is derived from defaultProfile.xml).
  KB_SECTIONS       35 sections - 34 named groups plus the ungrouped bucket.
  KB_DOF            the axis evidence table.

THE 35th SECTION IS NOT A NAMED GROUP. 34 groups carry names; 9 labelled actions
carry no group at all. They are collected under one explicit "Ungrouped" bucket
rather than dropped, because silently showing 682 of 691 actions is exactly the
kind of quiet subtraction nobody notices.

WHAT IS DELIBERATELY ABSENT: SECTION DESCRIPTIONS

The order asks for "each section with its plain-English description". No such
field exists in keybinds_site.json - it carries a per-ACTION `desc` on 208 of
the 691 rows and nothing at section level. The descriptions the order refers to
live in a prototype that is not in this repo.

They are therefore NOT emitted, rather than invented. Rule 11: an honest gap is
always acceptable, a fabricated value never is. Thirty-five plausible-sounding
sentences written by me would be indistinguishable from real ones and impossible
to audit later. When the prototype's text is available, add it here - the page
already renders a description when one is present.
"""

import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data-layer", "processed", "keybinds_site.json")
OUT = os.path.join(HERE, "testing", "_src", "kb_actions.gen.js")

UNGROUPED = "Ungrouped"
# 105 of the 691 labelled actions carry no category. They get an explicit
# bucket for the same reason the ungrouped ones do - so the browser shows all
# 691 rather than 586 and nobody has to notice the difference. It is named
# rather than left as the string "None", which reads like a real category.
UNCATEGORISED = "Uncategorised"

# The axis evidence table, corrected per
# FINDING_exporter-round-trip-passes-2026-08-09.md section 8.
#
# UNATTESTED IS NOT REJECTED. "Never seen in any file we have read" and "the
# game will not accept it" are different claims, and only the first one is
# supported. Saying the stronger thing would be a fabrication.
#
# That distinction paid off on 2026-08-12: rotx and roty were UNATTESTED, and
# rather than being wrong they were simply unobserved. The game accepted both
# and wrote them back out. Had they been recorded as invalid, the page would
# have talked somebody out of a binding that works.
DOF = [
    {"axis": "x", "status": "PROVEN",
     "note": "appears in real player profiles"},
    {"axis": "y", "status": "PROVEN",
     "note": "appears in real player profiles"},
    {"axis": "z", "status": "PROVEN",
     "note": "appears in real player profiles"},
    {"axis": "rotz", "status": "PROVEN",
     "note": "appears in real player profiles"},
    {"axis": "slider1", "status": "PROVEN",
     "note": "in the game's own shipped defaults only"},
    # PROMOTED 2026-08-12 BY THE GAME ITSELF. Both were UNATTESTED - absent from
    # CIG's defaultProfile.xml and from both real player profiles - and the page
    # warned anyone binding them. Then Sleven loaded a from-defaults profile
    # containing js1_rotx and js1_roty into Star Citizen, and the game wrote both
    # back out in its own export. That is the strongest evidence available: not
    # "we found it in a file somewhere", but the game asserting the name is
    # valid. Absence was weak evidence and this is what replaced it.
    {"axis": "rotx", "status": "PROVEN",
     "note": "round-tripped through Star Citizen itself, 2026-08-12"},
    {"axis": "roty", "status": "PROVEN",
     "note": "round-tripped through Star Citizen itself, 2026-08-12"},
    # The last unproven name. Still absence, still weak evidence, still NOT a
    # claim that the game refuses it.
    {"axis": "slider2", "status": "UNATTESTED",
     "note": "the only axis name still unproven - never seen, which is not the same as rejected"},
]


def main():
    with open(SRC, "r", encoding="utf-8") as fh:
        recs = json.load(fh)

    labelled = [r for r in recs if r.get("label")]

    cat_order, sec_order = [], []
    for r in labelled:
        c = r.get("category") or UNCATEGORISED
        if c not in cat_order:
            cat_order.append(c)
        s = r.get("group") or UNGROUPED
        if s not in sec_order:
            sec_order.append(s)

    actions = []
    for r in labelled:
        a = {
            "a": r.get("action"),
            "l": r.get("label"),
            "c": r.get("category") or UNCATEGORISED,
            "s": r.get("group") or UNGROUPED,
            "m": r.get("map"),
        }
        # Only carry fields that are actually populated. A key present with a
        # null value reads, in the page, exactly like a value we know to be
        # empty - and we do not know that.
        for src, dst in (("desc", "d"), ("keyboard", "k"), ("mouse", "mo"),
                         ("joystick", "j"), ("gamepad", "g"), ("activation", "act")):
            v = r.get(src)
            if v is not None and str(v).strip() != "":
                a[dst] = v
        actions.append(a)

    if UNCATEGORISED in cat_order:
        cat_order = [c for c in cat_order if c != UNCATEGORISED] + [UNCATEGORISED]
    if UNGROUPED in sec_order:
        sec_order = [c for c in sec_order if c != UNGROUPED] + [UNGROUPED]

    per_cat = collections.Counter(a["c"] for a in actions)
    per_sec = collections.Counter(a["s"] for a in actions)

    out = [
        "/* GENERATED by build_kb_actions.py from",
        "   data-layer/processed/keybinds_site.json - do not hand edit.",
        "   Regenerate instead. This file has one writer and it is the script.",
        "",
        "   SECTION DESCRIPTIONS ARE ABSENT ON PURPOSE. keybinds_site.json has no",
        "   section-level description field, and inventing 35 of them would be",
        "   indistinguishable from real ones later. The page renders a section",
        "   description when one exists; today none do. */",
        "",
        "const KB_ACTIONS=%s;" % json.dumps(actions, separators=(",", ":")),
        "const KB_CATEGORY_ORDER=%s;" % json.dumps(cat_order, separators=(",", ":")),
        "const KB_SECTION_ORDER=%s;" % json.dumps(sec_order, separators=(",", ":")),
        "/* Section descriptions, when they exist. Empty until the prototype's",
        "   text is available - see the module docstring. */",
        "const KB_SECTION_DESC={};",
        "/* Counts, stated by the generator rather than inferred by the page.",
        "   categories/sections are the NAMED ones; the Uncategorised and",
        "   Ungrouped buckets are listed separately because they are not",
        "   categories the game defines - they are where the leftovers go. */",
        "const KB_COUNTS=%s;" % json.dumps({
            "actions": len(actions),
            "categories": len([c for c in cat_order if c != UNCATEGORISED]),
            "sections": len(sec_order),
            "uncategorised": per_cat[UNCATEGORISED],
            "ungrouped": per_sec[UNGROUPED],
        }, separators=(",", ":")),
        "/* Axis evidence. UNATTESTED means never seen, NOT rejected. */",
        "const KB_DOF=%s;" % json.dumps(DOF, separators=(",", ":")),
        "",
    ]

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    print("wrote %s" % os.path.relpath(OUT, HERE))
    named_c = len([c for c in cat_order if c != UNCATEGORISED])
    named_s = len([c for c in sec_order if c != UNGROUPED])
    print("  %d labelled actions" % len(actions))
    print("  %d named categories + 1 %s bucket (%d actions)"
          % (named_c, UNCATEGORISED, per_cat[UNCATEGORISED]))
    print("  %d named sections + 1 %s bucket (%d actions)"
          % (named_s, UNGROUPED, per_sec[UNGROUPED]))
    print("  %d of %d actions carry a per-action description"
          % (sum(1 for a in actions if "d" in a), len(actions)))
    print("  section descriptions emitted: 0 - none exist in the source data")
    print()
    print("  %-52s %s" % ("category", "actions"))
    for c in cat_order:
        print("  %-52s %4d" % (c, per_cat[c]))
    print()
    print("  sections with the fewest actions (sanity check, not a failure):")
    for s, n in sorted(per_sec.items(), key=lambda kv: kv[1])[:3]:
        print("    %-50s %4d" % (s, n))


if __name__ == "__main__":
    main()
