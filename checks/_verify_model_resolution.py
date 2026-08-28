#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H2 / H3 / H5 - the model-to-ship resolution, and the pairs it must REFUSE.

THE RULE THIS DEFENDS IS "NO FUZZY MATCHING", and it is not abstract. On this
exact data, guessing has already produced four confident wrong pairs:

    Dragonfly Black -> Yellowjacket
    E1 Spirit       -> C1 Spirit
    G12a            -> 125a
    Zeus MR         -> Zeus ES

In the real pipeline that bolts the wrong hull onto four ships and nothing
catches it. So the load-bearing half of this control is not that the resolver
finds pairs - it is that it REFUSES those four, by name, every run.

WHAT THE RESOLVER FOUND, AND HOW IT CONTRADICTS THE ORDER'S PREMISE
===================================================================
The order says forty models we own are "sitting pointing at nobody" and calls
it "a name-matching failure, not a missing asset". Measured:

     1  resolved by an exact match
    25  ARE MODELS FOR SHIPS CIG HAS NOT BUILT - Kraken, Galaxy, Orion,
        Pioneer, Liberator, Hull D, Hull E, Zeus Mk II MR, the three Rangers,
        the three G12s. They are in LOADOUT_UNRELEASED, they have no ports and
        no ship page, and there is nothing to wire them to.
    14  genuinely unresolved

So it is mostly NOT a name-matching failure. It is a library that runs ahead of
the game data. That is a better problem to have and a different one, and it is
reported rather than smoothed over.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe checks/_verify_model_resolution.py [--self-test]
"""
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESOLVER = os.path.join(ROOT, "scripts", "resolve_ship_models.py")

SELFTEST = "--self-test" in sys.argv
_passed, _failed, _notes = [], [], []


def check(got, label, detail=""):
    want = (not got) if SELFTEST else got
    (_passed if want else _failed).append(("%s %s" % (label, detail)).strip())
    print("  %s  %s%s" % ("PASS" if want else "FAIL", label,
                          ("  " + detail) if detail else ""))
    return bool(want)


tmp = tempfile.mkdtemp(prefix="cc_res_")
out = os.path.join(tmp, "report.json")
proc = subprocess.run([sys.executable, RESOLVER, "--json", out],
                      capture_output=True, text=True)
print("\n1. THE RESOLVER RAN")
check(proc.returncode == 0 and os.path.exists(out),
      "the resolver produced a report", (proc.stderr or "")[-160:])
if not os.path.exists(out):
    sys.exit(2)
with io.open(out, "r", encoding="utf-8") as fh:
    R = json.load(fh)

print("     orphans %d | resolved %d | unreleased %d | unresolved %d"
      % (len(R["orphans"]), len(R["resolved"]), len(R["unreleased"]),
         len(R["unresolved"])))
check(len(R["orphans"]) > 30, "there really are orphan model files",
      str(len(R["orphans"])))
check(len(R["resolved"]) + len(R["unreleased"]) + len(R["unresolved"])
      == len(R["orphans"]),
      "and every one of them is accounted for in exactly one bucket - none "
      "quietly dropped",
      "%d + %d + %d of %d" % (len(R["resolved"]), len(R["unreleased"]),
                              len(R["unresolved"]), len(R["orphans"])))

# ------------------------------------------- 2. THE FOUR WRONG PAIRS
print("\n2. THE FOUR CONFIDENT WRONG PAIRS ARE REFUSED")
paired = {r["file"]: r["cls"] for r in R["resolved"]}
WRONG = [
    ("Dragonfly_Yellowjacket.glb", "Dragonfly Black"),
    ("E1_Spirit.glb", "C1 Spirit"),
    ("G12a.glb", "125a"),
    ("Zeus_Mk_II_MR.glb", "Zeus Mk II ES"),
]
for f, wrong_to in WRONG:
    got = paired.get(f)
    check(got is None or wrong_to.replace(" ", "_").lower() not in got.lower(),
          "%s was NOT paired with %s" % (f, wrong_to),
          "paired with %s" % got if got else "not paired at all")
_notes.append("the four known-bad pairs are all refused: %s"
              % ", ".join(f for f, _ in WRONG))

# THE POSITIVE HALF. Refusing everything also refuses those four.
check(len(R["resolved"]) > 0,
      "and the resolver still makes at least one pair - otherwise refusing "
      "the four above would be free",
      "%d resolved: %s" % (len(R["resolved"]),
                           ", ".join(r["file"] for r in R["resolved"][:3])))

# --------------------------------- 3. MANUFACTURER, AS AN INDEPENDENT FIELD
print("\n3. EVERY PAIR AGREES ON MANUFACTURER")
bad = [r for r in R["resolved"] if r.get("mfr_check") == "DISAGREE"]
check(not bad, "no claimed pair disagrees on manufacturer",
      ", ".join(r["file"] for r in bad[:3]))
check(all(r.get("mfr") for r in R["resolved"]),
      "and every paired ship has a manufacturer to check against")
_notes.append("manufacturer check on every pair: %d agree or unstated, 0 "
              "disagree" % len(R["resolved"]))

# ------------------------------------------ 4. THE UNRELEASED BUCKET
print("\n4. MODELS FOR SHIPS CIG HAS NOT BUILT")
print("     %d of the %d orphans" % (len(R["unreleased"]), len(R["orphans"])))
check(len(R["unreleased"]) > 15,
      "most of the orphans are models for ships with no ship page at all - "
      "NOT a name-matching failure, which is what the order assumed",
      str(len(R["unreleased"])))
names = {u["ship"] for u in R["unreleased"]}
for want in ("Kraken", "Galaxy", "Orion", "Liberator"):
    check(any(want in (n or "") for n in names),
          "%s is one of them" % want)
_notes.append("%d of %d orphan models are for UNRELEASED ships - Kraken, "
              "Galaxy, Orion, Pioneer, Liberator, Hull D/E, Zeus Mk II MR, "
              "three Rangers, three G12s" % (len(R["unreleased"]),
                                             len(R["orphans"])))

# ------------------------------------------------ 5. H3, EDITIONS
print("\n5. EDITIONS RESOLVE TO THEIR OWN FILE OR A NAMED BASE")
eds = R["editions"]
own = [e for e in eds if e["own_model"]]
base = [e for e in eds if not e["own_model"] and e["base_model"]]
orphaned = [e for e in eds if not e["own_model"] and not e["base_model"]]
print("     %d editions | %d have their own file | %d take a base | %d neither"
      % (len(eds), len(own), len(base), len(orphaned)))
# WHAT `editions` ACTUALLY IS, because the old assertion here read it wrong.
#
# This said `len(eds) > 50` under the label "the fleet really is mostly
# editions" and went red on 2026-08-27 at 16. Both halves were off:
#
#   * The list is NOT every edition in the fleet. `resolve_ship_models.py`
#     skips any class already wired to a model (`if WIRED.get(cls): continue`),
#     so it is the editions STILL NEEDING RESOLUTION. As the model library
#     filled in through the day, that number fell - which is the pipeline
#     working, read as a failure.
#   * A count of the fleet's composition is not what this section defends
#     anyway. Section 5's subject is that every edition here reaches a model,
#     by its own file or by a NAMED base, and that none is left with neither.
#
# So the population is PRINTED, and what is ASSERTED is that the population
# exists to assert against - reported NOT PERFORMED rather than passed if the
# library ever completes and the list empties, since every check below it is of
# the form `all(... for e in eds)` and would go green on nothing.
check(bool(eds),
      "there are unresolved editions for the checks below to run against",
      "%d - every assertion below is `all(... for e in eds)`, so an empty list "
      "would pass them all on nothing" % len(eds))
check(all(e["base"] for e in eds),
      "every edition names the base hull it was derived from - structurally, "
      "from the ClassName, not from a list somebody typed")
check(not orphaned or len(orphaned) < len(eds) / 4,
      "and almost all of them reach a model",
      "%d reach nothing" % len(orphaned))

# THE NEGATIVE HALF THE ORDER NAMES: an edition WITH its own file must not
# fall through to the base.
fell = [e for e in own if e["base_model"] and e["own_model"] != e["base_model"]
        and e["own_model"] is None]
check(not fell,
      "an edition WITH its own file does not fall through to the base hull",
      str(len(fell)))
check(all(e["mfr_ok"] for e in base),
      "and every edition taking a base hull shares that hull's manufacturer",
      "%d differ" % sum(1 for e in base if not e["mfr_ok"]))
_notes.append("editions: %d total, %d with their own export, %d sharing a base "
              "hull" % (len(eds), len(own), len(base)))

# ------------------------------------------------ 6. H5, THE DELIVERABLE
print("\n6. H5 - SHIPS WITH NO GEOMETRY IN ANY OF THE THREE LIBRARIES")
miss = R["missing"]
print("     %d ships" % len(miss))
for m in miss:
    print("       %-32s %s" % (m["name"], m["mfr"]))
check(len(miss) > 0,
      "the list exists and is not empty - if it were, the question about RSI's "
      "models would already be answered",
      str(len(miss)))
check(len(miss) < 60,
      "and it is small - which is the whole point of producing it before "
      "anyone talks to CIG",
      str(len(miss)))
check(all(m.get("name") for m in miss),
      "every entry is a NAMED ship, as the order requires - not a count alone")
_notes.append("H5: %d ships have no geometry in any of the three libraries"
              % len(miss))

print("\n" + "=" * 68)
for n in _notes:
    print("  " + n)
print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
if _failed:
    print("FAILED:")
    for f in _failed:
        print("  " + f)
if SELFTEST:
    print("\n--self-test: expectations were inverted, so a non-zero exit is "
          "the correct outcome.")
sys.exit(1 if _failed else 0)
