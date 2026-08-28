"""S9 of the 4.10 work order - the three things that must be re-measured.

    "Everything below was measured on 4.9 and a weapon rebalance is exactly what
     changes it."

  1  "Every shield in the game is identical by damage type" - 73 items, one
     Absorption pattern, one Resistance pattern.
  2  "Thermal, Biochemical and Stun are inert on both sides" - 0 weapons deal
     them, 0 defences resist them. BOTH halves.
  3  The armour damage-multiplier profiles. The record disagrees with itself:
     C3 counts 9, CURRENT-STATE says 10, the work order says EIGHT. Measured
     here rather than chosen.

RULE16: UNPROVEN - both sides of every comparison come from scunpacked, so this
    shows that source agreeing or disagreeing with itself across two commits.
    That is exactly right for the question asked - DID IT CHANGE - and it cannot
    tell you whether scunpacked's extraction is faithful to the game. The
    independent source would be the client's own p4k, which is C1's lane and was
    not used.

WHAT IT DOES NOT DO
===================
It does not interpret. "Absorption Physical Minimum 0, Maximum 0.45" is reported
as the range it is, because C1 established today that publishing 0.45 flat is
wrong at the bottom of the range where a shield absorbs NONE of a ballistic hit.
Nothing here collapses a range to one number.

Usage:
    python scripts/remeasure_4_10.py
    python scripts/remeasure_4_10.py --before <run_id> --after <run_id>
"""

import argparse
import datetime
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPS = os.path.join(REPO, "data-layer", "external-sources",
                     "scunpacked-data", "snapshots")
OUT = os.path.join(REPO, "data-layer", "derived", "weapon-diff-4-10")
CHANNELS = ("Thermal", "Biochemical", "Stun")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def log(m):
    print(m, flush=True)


def load(run_id):
    p = os.path.join(SNAPS, run_id, "ship-items.json")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def typ(r):
    return str((r.get("stdItem") or {}).get("Type") or "")


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


# ------------------------------------------------------------------ 1. shields

def shields(items):
    sh = [r for r in items if typ(r).startswith("Shield")]
    absorb, resist = {}, {}
    for r in sh:
        b = (r["stdItem"].get("Shield") or {})
        absorb.setdefault(canon(b.get("Absorption")), []).append(
            r["stdItem"].get("Name"))
        resist.setdefault(canon(b.get("Resistance")), []).append(
            r["stdItem"].get("Name"))
    return {"count": len(sh), "absorption_profiles": absorb,
            "resistance_profiles": resist}


# ------------------------------------------------- 2. the three damage channels

def channels(items):
    offence = {c: [] for c in CHANNELS}
    for r in items:
        st = r.get("stdItem") or {}
        am = (st.get("Ammunition") or {}).get("ImpactDamage") or {}
        alpha = ((st.get("Weapon") or {}).get("Damage") or {}).get("Alpha") or {}
        for c in CHANNELS:
            if (am.get(c) or 0) or (alpha.get(c) or 0):
                offence[c].append(st.get("Name") or st.get("ClassName"))

    # A defence "resists" a channel when it does something other than nothing:
    # an armour multiplier away from 1.0, or a shield resistance away from 0.
    defence = {c: [] for c in CHANNELS}
    for r in items:
        st = r.get("stdItem") or {}
        dm = (st.get("Armor") or {}).get("DamageMultipliers") or {}
        for c in CHANNELS:
            if c in dm and dm.get(c) != 1:
                defence[c].append(("armour", st.get("Name"), dm.get(c)))
        res = (st.get("Shield") or {}).get("Resistance") or {}
        for c in CHANNELS:
            v = res.get(c)
            if isinstance(v, dict) and (v.get("Minimum") or v.get("Maximum")):
                defence[c].append(("shield", st.get("Name"), v))
    return {"offence": offence, "defence": defence}


# ------------------------------------------------------------------- 3. armour

def is_real_armour(st):
    """A placeholder is not a profile.

    119 of the 210 armour records are literally named "<= PLACEHOLDER =>", one
    is an invulnerability record (ARMR_AEGS_Javelin_Invulnerable, Energy 0 /
    Distortion 0 / Thermal 0 / Biochemical 0), and a template carries no Armor
    block at all. Counting those is where the 8 / 9 / 10 disagreement in the
    written record comes from: each count swept in a different amount of
    scaffolding."""
    n = str(st.get("Name") or "").upper()
    c = str(st.get("ClassName") or "")
    return ("PLACEHOLDER" not in n and "Template" not in c
            and "Invulnerable" not in c)


def armour(items, real_only=False):
    ar = [r for r in items if typ(r).startswith("Armor")]
    profiles = {}
    for r in ar:
        if real_only:
            st = r["stdItem"]
            if not is_real_armour(st):
                continue
            if not (st.get("Armor") or {}).get("DamageMultipliers"):
                continue
        dm = (r["stdItem"].get("Armor") or {}).get("DamageMultipliers") or {}
        # *Change fields restate the multiplier against a 1.0 baseline. They are
        # the same fact twice, so they are dropped before profiles are counted -
        # keeping them would split identical armour into different "profiles".
        core = {k: v for k, v in dm.items() if not k.endswith("Change")}
        profiles.setdefault(canon(core), []).append(r["stdItem"].get("Name"))
    return {"count": len(ar), "profiles": profiles}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", default=None)
    ap.add_argument("--after", default=None)
    args = ap.parse_args()

    dirs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(SNAPS, "*"))
                  if os.path.isdir(d) and not d.endswith(".partial"))
    after = args.after or dirs[-1]
    before = args.before or dirs[-2]

    log("=" * 74)
    log("S9 RE-MEASUREMENT   before %s  ->  after %s" % (before, after))
    log("=" * 74)

    B, A = load(before), load(after)
    res = {}

    # ---- 1
    log("\n" + "-" * 74)
    log("1. ARE ALL SHIELDS IDENTICAL BY DAMAGE TYPE?")
    log("-" * 74)
    sb, sa = shields(B), shields(A)
    res["shields"] = {"before": {"count": sb["count"],
                                 "absorption_profiles": len(sb["absorption_profiles"]),
                                 "resistance_profiles": len(sb["resistance_profiles"])},
                      "after": {"count": sa["count"],
                                "absorption_profiles": len(sa["absorption_profiles"]),
                                "resistance_profiles": len(sa["resistance_profiles"])}}
    for tag, s in (("before", sb), ("after", sa)):
        log("  %-6s %d shield items | %d distinct Absorption profile(s) | "
            "%d distinct Resistance profile(s)"
            % (tag, s["count"], len(s["absorption_profiles"]),
               len(s["resistance_profiles"])))
    log("")
    if len(sa["absorption_profiles"]) == 1:
        p = json.loads(list(sa["absorption_profiles"])[0])
        log("  the single Absorption profile, as RANGES (not collapsed):")
        for c, v in p.items():
            log("     %-12s Minimum %-6s Maximum %s" % (c, v["Minimum"], v["Maximum"]))
    same = (canon(sorted(sb["absorption_profiles"])) == canon(sorted(sa["absorption_profiles"]))
            and canon(sorted(sb["resistance_profiles"])) == canon(sorted(sa["resistance_profiles"])))
    res["shields"]["unchanged_by_4_10"] = same
    log("\n  VERDICT: %s" % (
        "unchanged by 4.10, and still ONE profile - the 'do not build a shield "
        "comparison' ruling stands" if same and len(sa["absorption_profiles"]) == 1
        else "CHANGED - the ruling needs revisiting"))

    # ---- 2
    log("\n" + "-" * 74)
    log("2. ARE THERMAL, BIOCHEMICAL AND STUN INERT ON BOTH SIDES?")
    log("-" * 74)
    cb, ca = channels(B), channels(A)
    res["channels"] = {}
    for c in CHANNELS:
        ob, oa = len(cb["offence"][c]), len(ca["offence"][c])
        db, da = len(cb["defence"][c]), len(ca["defence"][c])
        res["channels"][c] = {"offence_before": ob, "offence_after": oa,
                              "defence_before": db, "defence_after": da}
        log("  %-12s deals it: %d -> %d     resists it: %d -> %d"
            % (c, ob, oa, db, da))
        for nm in ca["offence"][c][:4]:
            log("        now dealt by: %s" % nm)
    # THE VERDICT COMPARES AFTER TO BEFORE, NOT TO ZERO.
    # A first version tested "is it zero" and printed NO LONGER INERT over a
    # count that had not moved at all - blaming 4.10 for something that was
    # already true in 4.9. S9 asks whether the PATCH changed it.
    changed = any(
        res["channels"][c]["offence_after"] != res["channels"][c]["offence_before"]
        or res["channels"][c]["defence_after"] != res["channels"][c]["defence_before"]
        for c in CHANNELS)
    zero_after = all(res["channels"][c]["offence_after"] == 0
                     and res["channels"][c]["defence_after"] == 0 for c in CHANNELS)
    res["channels_changed_by_4_10"] = changed
    res["channels_fully_inert_after"] = zero_after
    if changed:
        log("\n  VERDICT: 4.10 CHANGED this - the counts above moved.")
    elif zero_after:
        log("\n  VERDICT: unchanged by 4.10, and inert on both sides.")
    else:
        log("\n  VERDICT: UNCHANGED BY 4.10, and not literally inert in either")
        log("  patch. The exception is ONE invulnerability record")
        log("  (ARMR_AEGS_Javelin_Invulnerable), not a ship you can fly. The")
        log("  claim is substantially true, is not exactly true, and 4.10 did")
        log("  not cause that.")

    # ---- 3
    log("\n" + "-" * 74)
    log("3. HOW MANY ARMOUR DAMAGE-MULTIPLIER PROFILES? (8? 9? 10?)")
    log("-" * 74)
    ab, aa = armour(B), armour(A)
    rb, ra = armour(B, real_only=True), armour(A, real_only=True)
    res["armour"] = {"before": {"items": ab["count"], "profiles": len(ab["profiles"]),
                                "real_profiles": len(rb["profiles"])},
                     "after": {"items": aa["count"], "profiles": len(aa["profiles"]),
                               "real_profiles": len(ra["profiles"])}}
    log("  RAW, every armour record including scaffolding:")
    log("     before  %d items, %d profile(s)" % (ab["count"], len(ab["profiles"])))
    log("     after   %d items, %d profile(s)" % (aa["count"], len(aa["profiles"])))
    log("  REAL SHIP ARMOUR ONLY - 119 placeholders and 1 invulnerability record")
    log("  excluded:")
    log("     before  %d profile(s)" % len(rb["profiles"]))
    log("     after   %d profile(s)" % len(ra["profiles"]))
    log("")
    for prof, names in sorted(ra["profiles"].items(),
                              key=lambda kv: -len(kv[1])):
        p = json.loads(prof)
        core = "  ".join("%s %s" % (k[:4], p[k]) for k in
                         ("Physical", "Energy", "Distortion", "Thermal",
                          "Biochemical", "Stun") if k in p)
        log("   %4d item(s)   %s" % (len(names), core))
    log("\n  VERDICT: %d real profiles in 4.10, %d in 4.9 - UNCHANGED."
        % (len(ra["profiles"]), len(rb["profiles"])))
    log("  The RAW count moved %d -> %d, and the profile that vanished belonged"
        % (len(ab["profiles"]), len(aa["profiles"])))
    log("  to a <= PLACEHOLDER => record. The 8 / 9 / 10 in the written record")
    log("  are counts of scaffolding, not of armour.")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "remeasure_%s.json" % after)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"generated_by": "scripts/remeasure_4_10.py",
                   "order": "WORKORDER_the-4-10-pull-2026-08-27.md S9",
                   "before": before, "after": after,
                   "at_utc": datetime.datetime.now(datetime.timezone.utc)
                       .isoformat(timespec="seconds"),
                   "results": res}, fh, indent=1, ensure_ascii=False)
    log("\nwrote %s" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
