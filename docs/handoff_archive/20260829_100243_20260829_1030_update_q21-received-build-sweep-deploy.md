# Update — Q21 through Q26 received. Taking Q21 (rebuild and deploy) with Q24 folded into its run, as the order says.

**2026-08-29 10:30 local · Code (background session)**

Sleven relayed C1's answers and put Q21 first. Filing before I start, rule 13.

## THE FOUR ANSWERS, AND WHAT I DO WITH EACH

    Q22  the last rule-16 label      C1 did it. VERIFIED MYSELF, not taken on
                                     the line: 105 labelled, 0 unlabelled,
                                     0 malformed. I had already removed the
                                     closed baseline entry at 09:52.
    holo-hardpoints/                 claimed by C1 in OWNERS.md. Closed.
    Q25  the separator DECISION doc  MINE. I own the enforcer, so I am the only
                                     one who can write what it enforces.
    Q26  the off-hull ten            BLOCKED-BY Q21. Not measuring the old
                                     payload.

## WHAT I AM DOING NOW

    1  Q24  the false comment at build_deploy.py:1359 - my file, one line
    2       python testing/_src/build_deploy.py
    3       assert BANU_Defender 50/51 and MISC_Hull_C 2 are gone
    4       run_all_controls.py --include-deployed
    5       deploy_testing.ps1
    6       verify the served site

## ONE LINE IN Q21 IS NOW STALE, AND IT MATTERS FOR THE ORDER

Q21 ends: *"Sweep first, let it finish, then deploy — the sweep rebuilds the
payload."*

**The sweep no longer rebuilds the payload.** I removed that this morning:
`_verify_deploy_drift.py` snapshots, rebuilds, compares and puts everything back
byte for byte, mtimes included. **Q21's own command list is already right** -
build, then sweep, then deploy - so nothing about the plan changes. But the
reason given for the order is gone, and the order now matters MORE rather than
less: **a sweep will no longer quietly fix a payload somebody forgot to build.**

## AND I STOPPED A SWEEP TO DO THIS

The clean re-run I started at 09:58 was measuring the payload Q21 replaces.
Killed rather than left to finish - its drift finding is the one Q21 closes, and
a green-or-red on a superseded payload tells nobody anything. **The verification
of the drift fix does not depend on it**: that stands on the 612-file
before/after manifest, hash and mtime, which is already recorded.

## Q24 IS C1'S RULE 14 VIOLATION AND I AM NOT RE-LITIGATING IT

C1 edited `build_deploy.py:1359`, caught it, reverted it, and wrote the erratum.
`git diff` on that file is empty and it is byte-identical to `4710d30` — **I
checked rather than took the sentence.** Self-caught and self-reported is the
system working. I am making the edit because the file is mine.
