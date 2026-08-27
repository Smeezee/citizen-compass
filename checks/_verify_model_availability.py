"""Prove the M4 sweep's gates by making each one fail on demand.

Hard rule 12: a check that cannot fail is not a check. Everything in
scripts/sweep_model_availability.py that claims to protect the output is fed
input that MUST trip it, and this file fails if the gate stays quiet.

Proven in both directions - each case has a known-bad input that must raise,
and the clean control that must not.

Run:  python checks/_verify_model_availability.py
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import sweep_model_availability as S  # noqa: E402

RESULTS = []


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        RESULTS.append((False, name, str(exc)))
        print("  FAIL  %s - %s" % (name, exc))
        return False
    RESULTS.append((True, name, ""))
    print("  pass  %s" % name)
    return True


def must_raise(fn, fragment):
    try:
        fn()
    except S.SweepError as exc:
        assert fragment in str(exc), (
            "raised SweepError but not the expected one: %r (wanted %r)" % (str(exc), fragment))
        return
    raise AssertionError("NO ERROR RAISED - the gate did not fire on input that must fail")


def fy(rec_id, sc, name, slug="s", holo=True):
    e = {"id": rec_id, "scIdentifier": sc, "name": name, "slug": slug,
         "productionStatus": "flight-ready", "lastUpdatedAt": None, "rsiSlug": None,
         "media": {}}
    if holo:
        e["media"]["holo"] = {"name": "holo-%s.gltf" % rec_id, "size": 1234,
                              "contentType": "application/octet-stream",
                              "url": "https://example.invalid/%s" % rec_id,
                              "uploadedAt": "2026-01-01T00:00:00+00:00"}
    return e


def ours(name, stem, cls=None, model=False):
    return {"name": name, "stem": stem, "cls": cls or (stem or "").upper(),
            "mfr": "Test", "model": model, "glb": None, "why": None, "id": name}


# --------------------------------------------------------------- the gates

def t_duplicate_sc_identifier():
    """Two Fleetyards records with the same scIdentifier must be fatal."""
    items = [fy("1", "orig_85x", "85X"), fy("2", "orig_85x", "85X Limited")]
    must_raise(lambda: S.build(items, [ours("85X", "orig_85x")], []), "duplicate scIdentifier")


def t_duplicate_name():
    """Two Fleetyards records with the same name must be fatal."""
    items = [fy("1", "orig_85x", "85X"), fy("2", "orig_85x_ltd", "85X")]
    must_raise(lambda: S.build(items, [ours("85X", "orig_85x")], []), "duplicate name")


def t_clean_input_does_not_trip():
    """The control: valid input must join without raising."""
    items = [fy("1", "orig_85x", "85X"), fy("2", "rsi_mantis", "Mantis")]
    joined, conflicts, un_ours, un_fy, cross, ctl = S.build(
        items, [ours("85X", "orig_85x"), ours("Mantis", "rsi_mantis")], [])
    assert len(joined) == 2, "clean input joined %d rows, expected 2" % len(joined)
    assert not conflicts, "clean input produced phantom conflicts: %r" % conflicts
    assert not un_ours and not un_fy, "clean input produced residue"


def t_name_collision_is_held_back():
    """Both rules matching DIFFERENT records must not join - it is the 85X case."""
    items = [fy("1", "orig_85x_limited", "85X Limited"), fy("2", "orig_85x", "85X")]
    row = ours("85X", "orig_85x_limited")
    row["name"] = "85X Limited"
    # our stem points at record 1; a differently-named record 2 also carries our name
    row["name"] = "85X"
    joined, conflicts, un_ours, _, _, _ = S.build(items, [row], [])
    assert len(conflicts) == 1, "expected 1 collision held back, got %d" % len(conflicts)
    assert not joined, "a colliding row was joined anyway: %r" % joined
    assert "NAME COLLISION" in conflicts[0]["note"]


def t_unjoined_goes_to_review_not_silently_dropped():
    items = [fy("1", "rsi_mantis", "Mantis")]
    joined, conflicts, un_ours, un_fy, _, _ = S.build(
        items, [ours("Mantis", "rsi_mantis"), ours("RAPTOR", None)], [])
    assert len(joined) == 1
    assert len(un_ours) == 1 and un_ours[0]["our_name"] == "RAPTOR", (
        "an unjoinable row did not reach the review list: %r" % un_ours)


def t_no_fuzzy_and_no_case_folding():
    """A row that would only match by case folding or similarity must NOT join."""
    items = [fy("1", "RSI_Mantis", "mantis")]
    joined, conflicts, un_ours, _, _, _ = S.build(items, [ours("Mantis", "rsi_mantis")], [])
    assert not joined, "case-folded/fuzzy match joined - the rule is exact only: %r" % joined
    assert len(un_ours) == 1, "expected the row in the review list"


def t_pagination_short_is_fatal(tmp):
    """A cache holding fewer records than the API's own total must be fatal."""
    path = os.path.join(tmp, "fy_1.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"items": [fy("1", "a", "A")],
                   "meta": {"pagination": {"totalCount": 244}}}, fh)
    must_raise(lambda: S.load_cached(tmp), "cache short")


def t_full_cache_is_accepted(tmp):
    """The control for the pagination gate."""
    path = os.path.join(tmp, "fy_1.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"items": [fy("1", "a", "A"), fy("2", "b", "B")],
                   "meta": {"pagination": {"totalCount": 2}}}, fh)
    items, total = S.load_cached(tmp)
    assert len(items) == 2 and total == 2, "clean cache was rejected"


def t_empty_cache_is_fatal(tmp):
    must_raise(lambda: S.load_cached(tmp), "no fy_*.json")


def t_holo_absence_is_reported_not_invented():
    items = [fy("1", "rsi_mantis", "Mantis", holo=False)]
    joined, _, _, _, _, _ = S.build(items, [ours("Mantis", "rsi_mantis")], [])
    assert joined[0]["holo"] is None, "a missing holo was filled in with something"


def t_cross_check_finds_variant_model():
    items = [fy("1", "aegs_eclipse_bis2950", "Eclipse Best In Show 2950")]
    inh = [{"class_name": "AEGS_Eclipse_BIS2950", "display_name": "Aegis Eclipse",
            "inherits_from": "AEGS_Eclipse", "model_file": "Eclipse.glb",
            "suffix_means": "Best In Show edition"}]
    _, _, _, _, cross, ctl = S.build(items, [], inh)
    assert len(cross) == 1 and cross[0]["holo"], "M4d cross-check missed a variant model"


def t_cross_check_control_reports_a_broken_join():
    """M4d's control must show 0 base hulls joining when the source has none -
    that is what distinguishes 'no variants exist' from 'the join is broken'."""
    inh = [{"class_name": "AEGS_Eclipse_BIS2950", "inherits_from": "AEGS_Eclipse",
            "model_file": "Eclipse.glb"}]
    _, _, _, _, cross, ctl = S.build([fy("9", "unrelated", "Unrelated")], [], inh)
    assert ctl["base_hulls_that_join"] == 0 and ctl["distinct_base_hulls"] == 1, (
        "the control did not notice that no base hull joined: %r" % ctl)
    _, _, _, _, cross2, ctl2 = S.build([fy("9", "aegs_eclipse", "Eclipse")], [], inh)
    assert ctl2["base_hulls_that_join"] == 1 and not cross2, (
        "control should show a working join with no variant hit: %r" % ctl2)


def main():
    # Hard rule 6: fixtures stay inside the repo. Never %TEMP%, never anywhere
    # else on the machine.
    scratch = os.path.join(HERE, "_fixtures_m4")
    tmp_short = os.path.join(scratch, "short")
    tmp_full = os.path.join(scratch, "full")
    tmp_empty = os.path.join(scratch, "empty")
    for d in (tmp_short, tmp_full, tmp_empty):
        os.makedirs(d, exist_ok=True)
        for n in os.listdir(d):
            if n.startswith("fy_"):
                os.replace(os.path.join(d, n), os.path.join(d, "_old_" + n))

    print("Verifying scripts/sweep_model_availability.py gates against known-bad input")
    check("duplicate scIdentifier is fatal", t_duplicate_sc_identifier)
    check("duplicate name is fatal", t_duplicate_name)
    check("name collision is held back, not joined", t_name_collision_is_held_back)
    check("unjoined rows reach the review list", t_unjoined_goes_to_review_not_silently_dropped)
    check("no fuzzy and no case folding", t_no_fuzzy_and_no_case_folding)
    check("missing holo is reported as absent", t_holo_absence_is_reported_not_invented)
    check("M4d cross-check finds a variant model", t_cross_check_finds_variant_model)
    check("M4d control separates absent variants from a broken join",
          t_cross_check_control_reports_a_broken_join)
    check("short pagination is fatal", lambda: t_pagination_short_is_fatal(tmp_short))
    check("empty cache is fatal", lambda: t_empty_cache_is_fatal(tmp_empty))
    check("CONTROL - full cache is accepted", lambda: t_full_cache_is_accepted(tmp_full))
    check("CONTROL - clean input does not trip any gate", t_clean_input_does_not_trip)

    failed = [r for r in RESULTS if not r[0]]
    print("")
    print("%d checks, %d failed" % (len(RESULTS), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
