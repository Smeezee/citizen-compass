"""Rule 12 proof for the unreleased-content filter and checker.

RULE16: UNPROVEN - it imports both the checker and the publication filter and
judges what they return. The content they are given is written here and
is unreleased by construction, so the pair has to catch what this file
planted; what cannot be reached from inside is whether their idea of
'unreleased' is the right one.

Two things are proven here, and the second is the one that matters:

  1. `scripts/publication_filter` withholds exactly the flagged records and
     nothing else - including the trap where the STRING "false" reads as True
     under plain Python truthiness.
  2. `unreleased_content_check` DEFECTS on a published file carrying a flagged
     record, and - the important half - reports LIMITATION rather than PASS
     when there is no corpus to examine. A checker that finds nothing because
     it had nothing to look at, and calls that a pass, is the silent-success
     shape this project keeps finding.

Run:  python checks/_verify_unreleased_content.py
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checks.file_checks import unreleased_content_check  # noqa: E402
from scripts.publication_filter import (  # noqa: E402
    filter_publishable,
    is_publishable,
    unreleased_reasons,
)

PASSED = 0
FAILED = []


def check(condition, message):
    global PASSED
    if condition:
        PASSED += 1
        print("  ok   " + message)
    else:
        FAILED.append(message)
        print("  FAIL " + message)


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def main():
    # ---- 1. the filter itself -------------------------------------------
    print("\n1. the filter withholds exactly the flagged records")
    clean = {"debug_name": "PU_Delivery_Real", "not_for_release": False,
             "work_in_progress": False}
    nfr = {"debug_name": "PU_Delivery_Local_legal_Cave_Pyro_CFP_2",
           "not_for_release": True, "work_in_progress": False}
    wip = {"debug_name": "PU_Test_WIP", "not_for_release": False,
           "work_in_progress": True}

    check(is_publishable(clean), "an unflagged record is publishable")
    check(not is_publishable(nfr), "not_for_release is withheld")
    check(not is_publishable(wip), "work_in_progress is withheld")
    check(unreleased_reasons(nfr) == ["not_for_release"], "the reason is named")
    check(unreleased_reasons(wip) == ["work_in_progress"], "the wip reason is named")

    pub, held = filter_publishable([clean, nfr, wip, clean])
    check(len(pub) == 2 and len(held) == 2,
          "filter_publishable splits the corpus and returns BOTH halves")

    # NEGATIVE CONTROL: the truthiness trap. A bare non-empty string "false"
    # is True in Python. A filter that used plain truthiness would withhold a
    # publishable record here, or - worse, with the flags inverted - publish a
    # withheld one.
    print("\n2. [NEG] the string \"false\" must not read as flagged")
    strfalse = {"debug_name": "X", "not_for_release": "false"}
    check(bool(strfalse["not_for_release"]) is True,
          "[NEG] confirming the trap is real: bool('false') is True in Python")
    check(is_publishable(strfalse),
          "[NEG] the filter does NOT fall for it - 'false' reads as not flagged")
    check(not is_publishable({"debug_name": "Y", "not_for_release": "true"}),
          "the string 'true' DOES read as flagged")
    check(is_publishable({"debug_name": "Z"}),
          "a record missing the flags entirely is publishable")

    tmp = Path(tempfile.mkdtemp(prefix="unreleased-"))
    try:
        # ---- 3. no corpus -> LIMITATION, never PASS ----------------------
        print("\n3. no corpus to examine is reported as NOT PERFORMED")
        empty_repo = tmp / "empty"
        write(empty_repo / "releases" / "ships.json", [{"name": "Arrow"}])
        f = unreleased_content_check(empty_repo)
        check([x.result for x in f] == ["LIMITATION"],
              "a published tree with no contract corpus -> LIMITATION")
        check(not any(x.result == "PASS" for x in f),
              "[NEG] it never reports PASS over an empty corpus")
        check(any("NOT PERFORMED" in x.details for x in f),
              "the finding says NOT PERFORMED in as many words")

        # ---- 4. NEGATIVE CONTROL: a real leak is caught ------------------
        print("\n4. [NEG] a flagged record in a PUBLISHED file is a DEFECT")
        leaky = tmp / "leaky"
        write(leaky / "releases" / "contracts.json", [clean, nfr])
        f = unreleased_content_check(leaky)
        check(any(x.result == "DEFECT" for x in f),
              "[NEG] a published file carrying not_for_release is a DEFECT")
        check(any("PU_Delivery_Local_legal_Cave_Pyro_CFP_2" in x.details
                  for x in f if x.result == "DEFECT"),
              "[NEG] the finding NAMES the offending record")

        # ---- 5. the same records, filtered, are clean --------------------
        print("\n5. running the corpus through the filter clears the defect")
        fixed = tmp / "fixed"
        publishable, _ = filter_publishable([clean, nfr, wip])
        write(fixed / "releases" / "contracts.json", publishable)
        f = unreleased_content_check(fixed)
        check(not any(x.result == "DEFECT" for x in f),
              "the filtered corpus raises no DEFECT")

        # ---- 6. nested shapes are walked, not assumed --------------------
        print("\n6. a nested publication shape is still examined")
        nested = tmp / "nested"
        write(nested / "static" / "by_system.json",
              {"systems": {"Pyro": {"contracts": [nfr]}}})
        f = unreleased_content_check(nested)
        check(any(x.result == "DEFECT" for x in f),
              "[NEG] a flagged record nested three levels deep is still caught")

        # ---- 7. unparseable file is not called clean ---------------------
        print("\n7. an unreadable corpus is not reported as clean")
        broken = tmp / "broken"
        p = broken / "releases" / "contracts.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('{"not_for_release": tru', encoding="utf-8")  # truncated
        f = unreleased_content_check(broken)
        check(any(x.result == "WARNING" for x in f),
              "a file mentioning the flags that will not parse -> WARNING")
        check(not any(x.result == "PASS" for x in f),
              "[NEG] an unparseable file is never reported as a pass")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASSED} passed, {len(FAILED)} failed")
    if FAILED:
        for m in FAILED:
            print("  FAILED: " + m)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
