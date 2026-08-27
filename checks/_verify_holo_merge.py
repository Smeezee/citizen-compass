"""Prove build_holo_data.merge_join tells a duplicate from a real collision.

Q6. The guard used to exit on ANY repeated key. That stalled the generator from
17 August to 27 August over seven duplicates, and the holo page was served from
a ten-day-old build the whole time.

It now skips a duplicate and keeps the PLACED record - Sleven's decision, on the
grounds that the placed record carries the per-hardpoint provenance
(`placed_from`, `aimed_at`, `depth`) that the recovered one has as null.

**The dangerous case must still refuse.** That is what this file is for. A guard
that has been taught to say yes is only safe if it can still be made to say no,
so both directions are exercised here and the file fails if either stops
working.

Run:  python checks/_verify_holo_merge.py
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import build_holo_data as B  # noqa: E402

FIXTURES = os.path.join(HERE, "_fixtures_holo")
RESULTS = []


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        RESULTS.append(False)
        print("  FAIL  %s - %s" % (name, exc))
        return
    RESULTS.append(True)
    print("  pass  %s" % name)


def write_join(payload):
    os.makedirs(FIXTURES, exist_ok=True)
    path = os.path.join(FIXTURES, "hardpoints_join.json")
    with io.open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh)
    B.JOIN = path
    return path


def placed(model, with_provenance=True):
    hp = {"port": "hardpoint_gun_left", "pos_model": [1.0, 0.0, 0.0]}
    if with_provenance:
        hp.update({"placed_from": "own", "aimed_at": "fraction", "depth": 0})
    return {"model": model, "hardpoints": [hp]}


def recovered(model):
    return {"model": model, "resolved_by": "rule",
            "hardpoints": [{"port": "hardpoint_gun_left",
                            "pos_model": [1.1, 0.0, 0.0],
                            "placed_from": None, "aimed_at": None, "depth": None}]}


# ---------------------------------------------------------------- the cases

def t_duplicate_is_skipped_not_fatal():
    """Same model on both sides: skip, keep the placed record, do not exit."""
    write_join({"ROC": recovered("ROC.glb")})
    fleet = {"ROC": placed("ROC.glb")}
    out, meta = B.merge_join(fleet)
    assert "ROC" in meta.get("duplicates_skipped", []), \
        "the duplicate was not recorded as skipped: %r" % meta
    assert meta["merged"] == 0, "a duplicate was merged in: %r" % meta
    hp = out["ROC"]["hardpoints"][0]
    assert hp.get("placed_from") == "own", \
        "THE PLACED RECORD WAS REPLACED - placed_from is %r, so the provenance " \
        "the disclosure work needs is gone" % hp.get("placed_from")
    assert hp["pos_model"] == [1.0, 0.0, 0.0], \
        "the recovered position overwrote the placed one: %r" % hp["pos_model"]


def t_different_model_still_refuses():
    """The dangerous case. Two records, two different hulls, one key."""
    write_join({"Gladius": recovered("Redeemer.glb")})
    fleet = {"Gladius": placed("Gladius.glb")}
    try:
        B.merge_join(fleet)
    except SystemExit as exc:
        assert "DIFFERENT model" in str(exc), \
            "exited, but not for the reason expected: %r" % str(exc)
        return
    raise AssertionError(
        "NO EXIT. A recovered record naming Redeemer.glb was allowed to collide "
        "with a ship whose model is Gladius.glb. This is exactly the case the "
        "guard exists for.")


def t_missing_model_is_treated_as_dangerous():
    """A record with no model cannot be shown to be the same hull, so it must
    NOT be waved through as a duplicate."""
    write_join({"Mystery": {"resolved_by": "rule", "hardpoints": []}})
    fleet = {"Mystery": placed("Mystery.glb")}
    try:
        B.merge_join(fleet)
    except SystemExit:
        return
    raise AssertionError(
        "a recovered record with NO model was treated as a duplicate. Absence of "
        "evidence is not evidence of sameness.")


def t_clean_input_still_merges():
    """The control: a recovered ship with no collision must still be added."""
    write_join({"Brand_New": recovered("Brand_New.glb")})
    fleet = {"Something Else": placed("Something_Else.glb")}
    out, meta = B.merge_join(fleet)
    assert meta["merged"] == 1, "a non-colliding ship was not merged: %r" % meta
    assert "Brand New" in out, "merged under an unexpected key: %r" % sorted(out)


def t_no_join_file_is_not_a_silent_pass():
    B.JOIN = os.path.join(FIXTURES, "does_not_exist.json")
    out, meta = B.merge_join({"A": placed("A.glb")})
    assert meta.get("note"), "a missing join dataset should say so: %r" % meta


def main():
    print("Verifying build_holo_data.merge_join in both directions")
    original = B.JOIN
    try:
        check("a duplicate is skipped and the PLACED record survives",
              t_duplicate_is_skipped_not_fatal)
        check("a DIFFERENT model still refuses, loudly",
              t_different_model_still_refuses)
        check("a recovered record with no model is not waved through",
              t_missing_model_is_treated_as_dangerous)
        check("CONTROL - a non-colliding ship still merges",
              t_clean_input_still_merges)
        check("CONTROL - a missing join dataset is reported, not ignored",
              t_no_join_file_is_not_a_silent_pass)
    finally:
        B.JOIN = original

    failed = RESULTS.count(False)
    print("\n%d checks, %d failed" % (len(RESULTS), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
