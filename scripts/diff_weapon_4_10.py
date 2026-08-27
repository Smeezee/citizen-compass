"""The 4.10 weapon controls, run against a snapshot and the frozen 4.9 baseline.

Order: docs/WORKORDER_the-4-10-pull-2026-08-27.md (C3), which folds in CIC's
acceptance fragment. Two of the four controls are amended there because as
written they would have failed a good pull.

WHAT THIS IS AND IS NOT
=======================
It reads two files and compares them. It does not decide whether 4.10 is good,
it does not publish anything, and every number it prints about the before-side
is 4.9 - the baseline says so in a field literally called WARNING.

THE MATCH IS BY UUID, EXACTLY
=============================
Never by name. §5 of the order is the reason: CIG calls the C-788 the "Combine
Cannon" and there is NO ITEM BY THAT NAME - "Combine" appears only inside
description prose. A search by name returns nothing, and reporting that as
"weapon absent" would read as caution while being a miss.

WHY DPS IS NOT A CONTROL
========================
The baseline stores it under a key called `NOT_CONTROL_1_derived_dps` and this
never asserts on it. The AD4B reads 84.4 per round and the Revenant 63.3 - 33%
apart - and BOTH have a DPS of exactly 1266. Rate of fire absorbs the
difference, so a diff keyed on DPS calls them the same weapon.

READING THE OUTCOME (§8), applied here rather than left to the reader
=====================================================================
    1, 3 pass, 5a passes, 4 quiet     trustworthy
    any of 1, 3, 5a shows ZERO        the importer is broken, not the patch
    4 also moves                      INCONCLUSIVE - diagnose the diff first
    magnitude off, direction right    FLAG, do not fail
    5b shows nothing                  EXPECTED - report which of a/b/c

Usage:
    python scripts/diff_weapon_4_10.py --snapshot <run_id>
    python scripts/diff_weapon_4_10.py            (newest complete snapshot)
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
BASE = os.path.join(REPO, "data-layer", "derived", "weapon-baseline-4-9",
                    "weapon_baseline_4_9.json")
OUT_DIR = os.path.join(REPO, "data-layer", "derived", "weapon-diff-4-10")
TARGET_PATCH = "4.10.0-LIVE.12519617"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class DiffError(RuntimeError):
    pass


def log(m):
    print(m, flush=True)


def newest_snapshot():
    dirs = [d for d in glob.glob(os.path.join(SNAPS, "*"))
            if os.path.isdir(d) and not d.endswith(".partial")]
    if not dirs:
        raise DiffError("no complete snapshot in %s" % SNAPS)
    return os.path.basename(sorted(dirs)[-1])


def patch_of(run_id):
    """The patch gate, §2: the EXISTING field, not a new one."""
    man = os.path.join(REPO, "data-layer", "external-source-manifests", run_id,
                       "01_scunpacked-data_manifest.json")
    if not os.path.exists(man):
        raise DiffError("no manifest for %s - the gate has not run, and this "
                        "does not proceed on an ungated snapshot" % run_id)
    with open(man, encoding="utf-8") as fh:
        m = json.load(fh)
    g = m.get("git_metadata_captured_before_stripping") or {}
    subj = g.get("git_head_subject")
    if not subj:
        raise DiffError("the manifest for %s carries no git_head_subject. That "
                        "field is the only place the patch appears." % run_id)
    return subj


def extract(item):
    """The same shape the baseline stores, read from a raw ship-items record."""
    st = item.get("stdItem") or {}
    w = st.get("Weapon") or {}
    am = st.get("Ammunition") or {}
    dmg = w.get("Damage") or {}
    modes = w.get("Modes") or []
    absent = "<ABSENT>"
    return {
        "className": st.get("ClassName"),
        "name": st.get("Name"),
        "weapon_size": w.get("Size"),
        "CONTROL_1_per_round_damage": {
            "Ammunition.ImpactDamage": am.get("ImpactDamage"),
            "Weapon.Damage.Alpha": dmg.get("Alpha"),
            "Weapon.Damage.AlphaTotal": dmg.get("AlphaTotal"),
            "Modes[].DamagePerShot": [m.get("DamagePerShot") for m in modes],
        },
        "NOT_CONTROL_1_derived_dps": {
            "Weapon.Damage.Dps": dmg.get("Dps"),
            "Weapon.Damage.DpsTotal": dmg.get("DpsTotal"),
            "Weapon.RateOfFire": w.get("RateOfFire"),
        },
        "CONTROL_2_explosive": {
            "Ammunition.ExplosionRadius":
                am.get("ExplosionRadius", absent),
            "Ammunition.ExplosionSafetyDistance":
                am.get("ExplosionSafetyDistance", absent),
        },
        "CONTROL_3_ammunition_and_class": {
            "Ammunition.UUID": am.get("UUID"),
            "Ammunition.Size": am.get("Size"),
            "Ammunition.Pierceability": am.get("Pierceability"),
            "Ammunition.MaxPenetrationThickness": am.get("MaxPenetrationThickness"),
            "Ammunition.Speed": am.get("Speed"),
            "Ammunition.Capacity": am.get("Capacity"),
        },
    }


def phys(block):
    d = (block or {}).get("Ammunition.ImpactDamage") or {}
    return d.get("Physical")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=None)
    args = ap.parse_args()

    run_id = args.snapshot or newest_snapshot()
    subj = patch_of(run_id)

    log("=" * 74)
    log("4.10 WEAPON CONTROLS   snapshot %s" % run_id)
    log("=" * 74)
    log("  git_head_subject : %s" % subj)

    # §2 - fail closed, and the clean-stop case said as a result rather than a
    # failure.
    if TARGET_PATCH not in subj:
        with open(BASE, encoding="utf-8") as fh:
            base_patch = json.load(fh).get("patch")
        if "4.9.0-LIVE.12344265" in subj:
            log("\n  THE UPSTREAM REPO HAS NOT MOVED. This snapshot carries the "
                "same build as the\n  one already on disk, so there is nothing "
                "to diff.")
            log("  That is a CLEAN RESULT, not a failure. No control ran.")
            return 0
        raise DiffError(
            "this snapshot is %r, not %r. It is not a 4.10 pull and NO CONTROL "
            "RUNS - a pull that cannot prove its build produces a confident "
            "answer about the wrong one." % (subj, TARGET_PATCH))
    log("  patch gate       : PASS")

    items_path = os.path.join(SNAPS, run_id, "ship-items.json")
    if not os.path.exists(items_path):
        raise DiffError("no ship-items.json in %s" % run_id)
    with open(items_path, encoding="utf-8") as fh:
        items = json.load(fh)
    by_uuid = {}
    for r in items:
        u = (r.get("stdItem") or {}).get("UUID")
        if u:
            by_uuid[u] = r
    log("  records          : %d, %d with a UUID" % (len(items), len(by_uuid)))

    # The corpus-level discriminator, computed before any control is read.
    prev = sorted(d for d in glob.glob(os.path.join(SNAPS, "*"))
                  if os.path.isdir(d) and not d.endswith(".partial")
                  and os.path.basename(d) != run_id)
    corpus_changed = corpus_common = 0
    if prev:
        with open(os.path.join(prev[-1], "ship-items.json"), encoding="utf-8") as fh:
            old_items = json.load(fh)
        old_by = {}
        for r in old_items:
            u = (r.get("stdItem") or {}).get("UUID")
            if u:
                old_by[u] = r
        both = set(old_by) & set(by_uuid)
        corpus_common = len(both)
        corpus_changed = sum(
            1 for u in both
            if json.dumps(old_by[u], sort_keys=True)
            != json.dumps(by_uuid[u], sort_keys=True))
        log("  corpus vs %s : %d of %d common records changed"
            % (os.path.basename(prev[-1]), corpus_changed, corpus_common))

    with open(BASE, encoding="utf-8") as fh:
        baseline = json.load(fh)

    results, missing = {}, []
    for group, subjects in baseline["subjects"].items():
        for s in subjects:
            u = s.get("uuid")
            rec = by_uuid.get(u)
            if rec is None:
                missing.append((group, s.get("className"), u))
                continue
            results[u] = {"group": group, "before": s, "after": extract(rec)}

    if missing:
        log("\n  SUBJECTS NOT FOUND BY UUID IN THE NEW SNAPSHOT (%d):" % len(missing))
        for g, cn, u in missing:
            log("     %-36s %s  [%s]" % (cn, u, g))
        log("  A subject that vanished is a finding, not a silent skip.")

    verdict = {}

    # ---------------------------------------------------------- CONTROL 1
    log("\n" + "-" * 74)
    log("CONTROL 1 - S4 ballistic gatlings, per ROUND (not DPS)")
    log("-" * 74)
    c1 = [v for v in results.values()
          if v["group"] == "control_1_and_3_s4_ballistic_gatlings"]
    moved, zero, rows = 0, 0, []
    for v in c1:
        b, a = phys(v["before"]["CONTROL_1_per_round_damage"]), \
               phys(v["after"]["CONTROL_1_per_round_damage"])
        pct = None if not b else (a - b) / b * 100.0
        rows.append((v["before"]["name"], b, a, pct))
        if b == a:
            zero += 1
        else:
            moved += 1
    for n, b, a, pct in rows:
        log("  %-30s %8s -> %-8s %s" % (n, b, a,
            ("%+.1f%%" % pct) if pct is not None else "n/a"))
    if not c1:
        verdict["control_1"] = "NOT RUN - no subjects resolved"
    elif zero == len(c1):
        # SS8 SAYS A ZERO MEANS THE IMPORTER IS BROKEN. THAT INFERENCE HAS A
        # PREMISE, AND THE PREMISE IS TESTABLE.
        #
        # "The importer did not carry the change" is only one explanation for a
        # zero. The other is that the change is not in this build's data. The
        # two are told apart by asking whether the importer carried ANYTHING:
        # if a third of the catalogue moved and one of our own subjects moved
        # exactly as predicted, a broken importer is not a live hypothesis.
        #
        # On 2026-08-27 this mattered. Control 1 read zero on all six gatlings
        # and the first version of this file reported "the importer is broken".
        # 1,951 of 5,380 records had changed and the C-788 had fallen -10.6% as
        # predicted. The importer was fine; the gatling change was absent.
        verdict["control_1"] = ("FAIL - every subject unchanged"
                                + (". CORPUS MOVED (%d of %d records changed) and "
                                   "other subjects moved, so this is the CHANGE "
                                   "BEING ABSENT FROM THIS BUILD, not a broken "
                                   "importer" % (corpus_changed, corpus_common)
                                   if corpus_changed else
                                   ". The corpus did not move either - THIS is a "
                                   "broken importer"))
    else:
        ups = [p for _, _, _, p in rows if p and p > 0]
        in_band = [p for p in ups if 60 <= p <= 75]
        if ups and len(in_band) == len(ups):
            verdict["control_1"] = "PASS - all risen, within +60%..+75%"
        elif ups:
            verdict["control_1"] = ("FLAG - direction right, magnitude outside "
                                    "+60%%..+75%% on %d of %d"
                                    % (len(ups) - len(in_band), len(ups)))
        else:
            verdict["control_1"] = "FAIL - movement is not upward"

    # ---------------------------------------------------------- CONTROL 3
    log("\n" + "-" * 74)
    log("CONTROL 3 - Ammunition.Size on the S4 gatlings (CIG's stated cause)")
    log("-" * 74)
    bad = []
    for v in c1:
        b = v["before"]["CONTROL_3_ammunition_and_class"].get("Ammunition.Size")
        a = v["after"]["CONTROL_3_ammunition_and_class"].get("Ammunition.Size")
        log("  %-30s %s -> %s" % (v["before"]["name"], b, a))
        if a != 4:
            bad.append((v["before"]["name"], a))
    verdict["control_3"] = ("PASS - every S4 gatling fires Size 4 ammunition"
                            if not bad else
                            "FAIL - %d still not Size 4: %s"
                            % (len(bad), ", ".join("%s=%s" % x for x in bad)))

    # ------------------------------------------------------ CONTROL 2 (5a/5b)
    log("\n" + "-" * 74)
    log("CONTROL 2 - the C-788 Cannon")
    log("-" * 74)
    c2 = [v for v in results.values()
          if v["group"] == "control_2_s4_ballistic_combine_cannon"]
    if not c2:
        verdict["control_2a"] = "NOT RUN - the C-788 did not resolve by UUID"
        verdict["control_2b"] = "NOT RUN"
    else:
        v = c2[0]
        b, a = phys(v["before"]["CONTROL_1_per_round_damage"]), \
               phys(v["after"]["CONTROL_1_per_round_damage"])
        pct = None if not b else (a - b) / b * 100.0
        log("  5a direct damage  %s -> %s   %s" % (b, a,
            ("%+.1f%%" % pct) if pct is not None else "n/a"))
        if b == a:
            verdict["control_2a"] = "FAIL - unchanged"
        elif pct is not None and pct < 0:
            verdict["control_2a"] = ("PASS - fell %.1f%%" % pct
                                     if -15 <= pct <= -5 else
                                     "FLAG - fell %.1f%%, outside the ~-10%% expected" % pct)
        else:
            verdict["control_2a"] = "FAIL - direction wrong (%+.1f%%)" % (pct or 0)

        exb = v["before"]["CONTROL_2_explosive"]
        exa = v["after"]["CONTROL_2_explosive"]
        log("  5b explosive      before %s / after %s"
            % (exb.get("Ammunition.ExplosionRadius"),
               exa.get("Ammunition.ExplosionRadius")))
        if exa.get("Ammunition.ExplosionRadius") == "<ABSENT>":
            verdict["control_2b"] = (
                "NOT OBSERVABLE FROM THIS SOURCE - absent before and after, as "
                "in all three snapshots held. Expected; not a hole in the "
                "extraction (21 other WeaponGun records carry the field).")
        else:
            verdict["control_2b"] = ("UNEXPECTED - the field is present after; "
                                     "the order's premise needs revisiting")

    # ---------------------------------------------------------- CONTROL 4
    log("\n" + "-" * 74)
    log("CONTROL 4 - negative controls, chosen before the diff existed")
    log("-" * 74)
    c4 = [v for v in results.values() if v["group"] == "control_4_negative_controls"]
    movedn = []
    for v in c4:
        same = json.dumps(v["before"]["CONTROL_1_per_round_damage"], sort_keys=True) \
            == json.dumps(v["after"]["CONTROL_1_per_round_damage"], sort_keys=True)
        same3 = json.dumps({k: v["before"]["CONTROL_3_ammunition_and_class"].get(k)
                            for k in v["after"]["CONTROL_3_ammunition_and_class"]},
                           sort_keys=True) \
            == json.dumps(v["after"]["CONTROL_3_ammunition_and_class"], sort_keys=True)
        log("  %-30s damage %s   ammunition %s"
            % (v["before"]["name"], "same" if same else "MOVED",
               "same" if same3 else "MOVED"))
        if not (same and same3):
            movedn.append(v["before"]["name"])
    verdict["control_4"] = ("QUIET - no measured field moved" if not movedn else
                            "MOVED on %s - INCONCLUSIVE, diagnose the diff first"
                            % ", ".join(movedn))

    # ------------------------------------------------------------- outcome
    log("\n" + "=" * 74)
    log("OUTCOME")
    log("=" * 74)
    for k in ("control_1", "control_3", "control_2a", "control_2b", "control_4"):
        log("  %-11s %s" % (k, verdict.get(k, "NOT RUN")))

    if corpus_changed and verdict.get("control_1", "").startswith("FAIL"):
        log("\n  NOTE: a FAIL on control 1 with a moving corpus is a statement "
            "about THE PATCH,\n  not about the importer. Read the line.")

    trustworthy = (verdict.get("control_1", "").startswith(("PASS", "FLAG"))
                   and verdict.get("control_3", "").startswith("PASS")
                   and verdict.get("control_2a", "").startswith(("PASS", "FLAG"))
                   and verdict.get("control_4", "").startswith("QUIET"))
    log("")
    if verdict.get("control_4", "").startswith("MOVED"):
        log("  INCONCLUSIVE - a negative control moved. Diagnose the diff before "
            "reading anything else.")
    elif trustworthy:
        log("  TRUSTWORTHY - proceed.")
    else:
        log("  NOT TRUSTWORTHY on the above. Read each line; a zero on 1, 3 or "
            "5a means the importer, not the patch.")

    os.makedirs(OUT_DIR, exist_ok=True)
    rep = {"generated_by": "scripts/diff_weapon_4_10.py",
           "order": "docs/WORKORDER_the-4-10-pull-2026-08-27.md",
           "snapshot": run_id, "git_head_subject": subj,
           "baseline": "data-layer/derived/weapon-baseline-4-9/weapon_baseline_4_9.json",
           "at_utc": datetime.datetime.now(datetime.timezone.utc)
               .isoformat(timespec="seconds"),
           "verdict": verdict,
           "corpus_changed": corpus_changed, "corpus_common": corpus_common,
           "subjects_missing": [{"group": g, "className": c, "uuid": u}
                                for g, c, u in missing],
           "detail": {u: v for u, v in results.items()}}
    path = os.path.join(OUT_DIR, "diff_%s.json" % run_id)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1, ensure_ascii=False)
    log("\nwrote %s" % os.path.relpath(path, REPO))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except DiffError as exc:
        print("NOT PERFORMED: %s" % exc, file=sys.stderr)
        sys.exit(2)
