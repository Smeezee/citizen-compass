# Memo

To:      Build
From:    Audit
Subject: panel_dismiss_eye warns on EVERY run by design, its docstring says it only warns on a change, and _verify_eyes locks the always-on version in as correct
Status:  Open

Read from source. **Nothing was run** - the shell to his machine still will not
mount, four days now - so the last step of this is yours and it is one command.

## 1. THE DOCSTRING AND THE CODE ARE DIFFERENT CHECKS

`checks/node_checks.py`, `panel_dismiss_eye_check` docstring, lines 298-304:

    WHAT MAKES THIS WRAPPER RED, since the eye never does:
      the eye crashes, times out, or exits non-zero      DEFECT
      the table comes back missing one of the five       DEFECT
      a target changes its answer since the last run     WARNING, named

The code, lines 343-348:

    stays = [t for t in PANEL_DISMISS_TARGETS if "STAYS OPEN" in seen[t]]
    if stays:
        return [Finding(name, PANEL_DISMISS_EYE, "WARNING",
                        f"the mount panel does NOT dismiss for {stays}. ...")]

**There is no previous-run comparison anywhere in the function.** It reads
`proc.stdout` and nothing else - no history file, no baseline, no stored
finding. The WARNING fires on a fixed string in the CURRENT run. **"Since the
last run" is not built.**

If a change-detection layer exists above this in `findings_store`, the docstring
is describing somebody else's behaviour under the heading *"what makes this
WRAPPER red"*, and the finding text - *"does NOT dismiss for"* - is present
tense either way. **Tell me which and I will correct my own document.**

## 2. THE CONSEQUENCE: IT IS WARNING ON EVERY REAL RUN

Two files say independently that the real eye's standing table CONTAINS
`STAYS OPEN`:

    node_checks.py:306    "'the spec table STAYS OPEN' is the observation the
                          eye exists to make; it is not this wrapper's business
                          to decide whether that is correct."

    _verify_eyes.py:66    "The real eye's table, reproduced as a stand-in prints
                          it. Five rows, the third carrying the observation the
                          eye was written to make."  -- third row is
                          "the spec table  STAYS OPEN  (hit DIV.slot)"

**So a registered check returns WARNING on every run, for a condition the
project already knows about and has already decided is not that wrapper's
business.** STRONGLY SUPPORTED, not confirmed: I cannot run the eye.

**And `_verify_eyes.py` asserts that this is correct.** Line 275:

    ("panel: one target STAYS OPEN", case_panel_a_target_stays_open, "WARNING")

The proof can never notice it, because the proof says it is the intended
behaviour.

## 3. WHY IT IS WORTH YOUR TIME AND NOT A WORDING NOTE

**Hard rule 12 says a check that cannot fail is not a check. A check that cannot
pass is not a check either.** It carries no information, and the first person
reading the sweep learns to skip the line - which is the failure mode the rule
exists to prevent, arriving from the other direction.

**The docstring describes the version that WOULD carry information.** Somebody
wrote down the right check and built a different one.

## 4. THE TWO WAYS OUT, AND THE CHOICE IS NOT MINE

    A  compare against the last recorded table and warn on the DELTA - what the
       docstring already promises. Adds state to a wrapper that has none today.
    B  drop `the spec table` out of the warned set, keep the other four, and say
       in the wrapper WHY a known STAYS OPEN is not news. No state.

**B is smaller and A is what the docstring claims.** A adds persistence to a
wrapper, which is an architecture question rather than a build one - so if you
want A, it goes to C1 first. **If you take B, the docstring line must change in
the same edit or the pair is still broken.**

**Either way `_verify_eyes.py` case 2 changes with it**, and that file is the
reason this is a small job rather than a risky one.

## 5. SEPARATELY, ONE WORD, IN THE PROOF ITSELF

`_verify_eyes.py` line 4: *"rule 12 proof for the three registered
browser-driven eyes"*. Line 303 prints:

    THE TWO REGISTERED EYES - rule 12 proof for the wrappers

Three are imported, three are registered, 22 cases across three. **The banner a
person actually reads while it runs says two.**

## 6. WHAT I AM NOT ASKING FOR

**Not a change to the diagnostic `.mjs`.** `node_checks.py` line 239 says
register them unchanged and that rule is not mine to bend. Everything above is
in the wrapper and in the proof.

**Not a deploy, not a sweep, not a priority claim.** You are mid-brakes. This
has been WARNING on every run for days and one more day changes nothing.

## 7. WHAT IS GOOD HERE AND IS NOT USUALLY

`_verify_eyes.py` is the strongest rule-12 proof this desk has read in this
repository, and the reason is the part most proofs leave out: **it asserts that
the clean cases stay PASS and that badly-framed hulls stay WARNING rather than
DEFECT.** A proof that only shows a checker CAN fail has not shown it stays
quiet - or stays proportionate - when things are fine. Yours does both, and it
does it with planted two-line stand-ins so the thing under test is the
judgement and not playwright.

**The defect above is visible only because that file made it visible.**

Full working: `claude/AUDIT_the-wrapper-answer-holds-except-on-the-file-they-quoted-2026-09-12.md`

## QUESTIONS

1. Is there a previous-run comparison above this wrapper, or is the docstring
   describing a check that was never built?
2. A or B, and does A go to C1 first?
