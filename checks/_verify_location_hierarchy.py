"""
Rule 12 proof for A1, the location hierarchy resolver.

WHAT COULD SILENTLY GO WRONG HERE
---------------------------------
`resolve_path()` is the kind of function that passes every test anyone thinks
to write and still ships "ARC-L1 Wide Forest Station, None, Stanton" to a live
page, because the case that breaks it - a level that is absent in the middle
of the chain - never occurs in the example anyone tests with. Area 18 has a
city, a planet and a system, all present, all named. It is the Lagrange
station with no moon that breaks things.

So the control here is not "does the happy path work". It is:

  * every gap shape MUST resolve to a clean string      (no "None", no "0")
  * the resolver MUST NOT hang on corrupt parent data   (cycle guard fires)
  * a genuinely empty chain MUST return "", not "None"
  * and the happy path must still work, or the skipping logic has just
    deleted everything and "no None appeared" would be trivially true

That last one matters: a resolver that returns "" for absolutely everything
passes every no-None assertion. A check that cannot fail is not a check, so
the positive cases are part of the control, not decoration.

Run: venv/Scripts/python.exe checks/_verify_location_hierarchy.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.locations import (  # noqa: E402
    KIND_BY_UEX_FIELD,
    MAX_DEPTH,
    RESOLVABLE_KINDS,
    most_specific_reference,
    resolve_path,
    resolve_path_from_chain,
    unresolvable_references,
)
from app.models import LOCATION_KINDS  # noqa: E402


class FakeLocation:
    """Stand-in for a Location row. Deliberately NOT the ORM model: this
    control must run without a database, so that it can be run before the
    migration it is proving has been applied anywhere."""

    def __init__(self, name, parent=None, row_id=None):
        self.name = name
        self.parent = parent
        self.id = row_id


def chain(*names):
    """Build a parent chain from most specific to least. A name of None means
    a level that exists as a row but has no printable name."""
    node = None
    for i, name in enumerate(reversed(names)):
        node = FakeLocation(name, parent=node, row_id=i + 1)
    return node


def main():
    passed = 0
    failed = []

    def check(label, condition, detail=""):
        nonlocal passed
        if condition:
            passed += 1
            print(f"  ok   {label}")
        else:
            failed.append(f"{label} {detail}".strip())
            print(f"  FAIL {label} {detail}")

    # -----------------------------------------------------------------
    print("--- the two kind lists cannot drift apart ---")
    # app.locations and app.models each name the levels. If they disagree, a
    # kind can be selected by the resolver and then rejected by the database
    # check constraint, at import time, on row 700 of 823.
    resolver_kinds = tuple(k for _, k in KIND_BY_UEX_FIELD)
    check("resolver kind order matches models.LOCATION_KINDS",
          resolver_kinds == LOCATION_KINDS,
          f"{resolver_kinds!r} vs {LOCATION_KINDS!r}")
    check("every resolvable kind is a declared kind",
          RESOLVABLE_KINDS <= set(LOCATION_KINDS),
          f"stray: {RESOLVABLE_KINDS - set(LOCATION_KINDS)}")

    # -----------------------------------------------------------------
    print("\n--- KNOWN-BAD: gaps must never render as 'None' or '0' ---")
    # Each of these is a real shape from terminals.json.
    gap_cases = [
        ("station with no moon (ARC-L1)",
         chain("ARC-L1 Wide Forest Station", None, "ArcCorp", "Stanton")),
        ("missing system at the top", chain("Area 18", "ArcCorp", None)),
        ("missing everything but the leaf", chain("Lorville", None, None, None)),
        ("empty-string name mid-chain",
         chain("Baijini Point", "", "Crusader", "Stanton")),
        ("whitespace-only name mid-chain",
         chain("New Babbage", "   ", "microTech", "Stanton")),
        ("literal 'None' string from JSON",
         chain("Port Olisar", "None", "Crusader", "Stanton")),
        ("literal 'null' string from JSON",
         chain("Everus Harbor", "null", "Hurston", "Stanton")),
        ("numeric zero leaked in as a name",
         chain("Grim HEX", 0, "Yela", "Stanton")),
    ]
    for label, node in gap_cases:
        out = resolve_path(node)
        bad = [t for t in ("None", "null", ", 0") if t in out]
        check(f"{label} -> {out!r}",
              bool(out) and not bad and not out.startswith(", ")
              and not out.endswith(", "),
              f"contaminated with {bad}")

    # -----------------------------------------------------------------
    print("\n--- KNOWN-BAD: nothing printable must give '', never 'None' ---")
    empty_chain = chain(None, None, None)
    check("all-empty chain returns empty string",
          resolve_path(empty_chain) == "",
          f"got {resolve_path(empty_chain)!r}")
    check("a None location returns empty string",
          resolve_path(None) == "", f"got {resolve_path(None)!r}")
    check("empty chain list returns empty string",
          resolve_path_from_chain([]) == "")

    # -----------------------------------------------------------------
    print("\n--- KNOWN-BAD: a cyclic parent chain must terminate ---")
    # A self-parented row. Without the cycle guard this hangs the importer
    # forever, which on an 823-row import looks exactly like a slow network.
    loop = FakeLocation("Loop", row_id=99)
    loop.parent = loop
    out = resolve_path(loop)
    check(f"self-parented row terminates -> {out!r}", out == "Loop")

    a = FakeLocation("A", row_id=1)
    b = FakeLocation("B", parent=a, row_id=2)
    a.parent = b  # two-node cycle
    out = resolve_path(b)
    check(f"two-node cycle terminates -> {out!r}", out == "B, A")

    # A chain longer than MAX_DEPTH with distinct rows: must stop, not hang.
    deep = chain(*[f"L{i}" for i in range(MAX_DEPTH + 10)])
    out = resolve_path(deep)
    check("over-deep chain is truncated, not hung",
          out.count(", ") + 1 <= MAX_DEPTH,
          f"got {out.count(', ') + 1} parts")

    # -----------------------------------------------------------------
    print("\n--- POSITIVE: the resolver must still produce real strings ---")
    # Without these, every assertion above is satisfied by returning "".
    positives = [
        (chain("ARC-L1 Wide Forest Station", "ArcCorp", "Stanton"),
         "ARC-L1 Wide Forest Station, ArcCorp, Stanton"),
        (chain("Area 18", "ArcCorp", "Stanton"), "Area 18, ArcCorp, Stanton"),
        (chain("Stanton"), "Stanton"),
        # the gap case must keep BOTH surviving levels, not just the leaf
        (chain("ARC-L1 Wide Forest Station", None, "Stanton"),
         "ARC-L1 Wide Forest Station, Stanton"),
    ]
    for node, expected in positives:
        out = resolve_path(node)
        check(f"{expected!r}", out == expected, f"got {out!r}")

    # -----------------------------------------------------------------
    print("\n--- most_specific_reference: real terminal shapes ---")
    # Taken verbatim from terminals.json.
    ref_cases = [
        ("Lagrange station (station, no moon)",
         {"id_star_system": 68, "id_planet": 4, "id_orbit": 326, "id_moon": 0,
          "id_space_station": 1, "id_outpost": 0, "id_poi": 0, "id_city": 0},
         ("space_station", 1)),
        ("city terminal",
         {"id_star_system": 68, "id_planet": 4, "id_orbit": 4, "id_moon": 0,
          "id_space_station": 0, "id_outpost": 0, "id_poi": 0, "id_city": 1},
         ("city", 1)),
        ("moon outpost",
         {"id_star_system": 68, "id_planet": 4, "id_orbit": 4, "id_moon": 74,
          "id_space_station": 0, "id_outpost": 1, "id_poi": 0, "id_city": 0},
         ("outpost", 1)),
        ("bare system",
         {"id_star_system": 68, "id_planet": 0, "id_orbit": 0, "id_moon": 0,
          "id_space_station": 0, "id_outpost": 0, "id_poi": 0, "id_city": 0},
         ("star_system", 68)),
        # THE ONE THAT MATTERS: a terminal whose only non-zero specific id is
        # an orbit or a poi, neither of which this snapshot can name. It must
        # fall back to a level it CAN name rather than pointing at nothing.
        ("orbit is skipped, falls back to planet",
         {"id_star_system": 68, "id_planet": 4, "id_orbit": 326, "id_moon": 0,
          "id_space_station": 0, "id_outpost": 0, "id_poi": 0, "id_city": 0},
         ("planet", 4)),
        ("poi is skipped, falls back to system",
         {"id_star_system": 68, "id_planet": 0, "id_orbit": 0, "id_moon": 0,
          "id_space_station": 0, "id_outpost": 0, "id_poi": 55, "id_city": 0},
         ("star_system", 68)),
        ("no resolvable level at all returns None, not a guess",
         {"id_star_system": 0, "id_planet": 0, "id_orbit": 0, "id_moon": 0,
          "id_space_station": 0, "id_outpost": 0, "id_poi": 55, "id_city": 0},
         None),
        ("corrupt non-numeric id does not crash",
         {"id_star_system": 68, "id_planet": "banana", "id_orbit": 0,
          "id_moon": 0, "id_space_station": 0, "id_outpost": 0,
          "id_poi": 0, "id_city": 0},
         ("star_system", 68)),
        ("missing keys entirely does not crash", {}, None),
    ]
    for label, record, expected in ref_cases:
        got = most_specific_reference(record)
        check(f"{label} -> {got}", got == expected, f"expected {expected}")

    # -----------------------------------------------------------------
    print("\n--- unresolvable ids are KEPT as ids, never dropped ---")
    # Rule 11: we hold an orbit id we cannot name. The honest form is the
    # number, labelled. Dropping it would lose a fact; naming it would invent
    # one.
    kept = unresolvable_references(
        {"id_star_system": 68, "id_planet": 4, "id_orbit": 326, "id_moon": 0,
         "id_space_station": 1, "id_outpost": 0, "id_poi": 55, "id_city": 0}
    )
    check(f"orbit and poi ids preserved -> {kept}",
          kept == {"id_orbit": 326, "id_poi": 55})
    check("zero ids are not preserved as facts",
          unresolvable_references({"id_orbit": 0, "id_poi": 0}) == {})

    print("\n" + "=" * 62)
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print(f"  - {x}")
        return 1
    print(f"All {passed} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
