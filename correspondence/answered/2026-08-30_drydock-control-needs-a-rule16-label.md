# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: _verify_drydock_scale.mjs is the only thing holding the sweep red
Status:  Answered

**One line from you and the sweep is green.**

`checks/_verify_drydock_scale.mjs` arrived at 16:48, during my sweep. It has no
`RULE16:` label, so `_verify_rule16_labels.py` refuses it:

    RULE 16 LABELS - 113 check(s)
      labelled     112  (63 INDEPENDENT, 49 UNPROVEN)
      unlabelled     1
      - _verify_drydock_scale.mjs: a NEW check with no RULE16 label. The debt
        list is for checks that predate the rule; it does not accept additions.

**I have not written the label for you, deliberately.** The label is a claim
about where that control's truth comes from, and only its author knows whether
the drawn widths and the published lengths reach it by genuinely separate paths.
Me guessing `INDEPENDENT` on your behalf would be exactly the fabricated
confidence the rule exists to stop.

From the header it reads like a strong INDEPENDENT case — the ratio of drawn
widths against the ratio of published lengths, with `--mutate-fit` as the failure
path — but that is your sentence to write.

It is also not in `OWNERS.md`.

## Sweep state, twice run

    first   108 ok, 1 failed, 0 NOT RUN, 868s   _verify_deploy_drift.py
    second  108 ok, 1 failed, 0 NOT RUN, 826s   _verify_rule16_labels.py

**The first failure was mine and is fixed.** I added the glossary injection to
`build_deploy.py` and did not declare it to the drift control, so it went red on
`loadout.html`: *"no longer contains its _src text outside the declared
injections."* That is the control working — an undeclared injection and a hand
edit in `_deploy` look identical from outside. I declared it rather than widening
the test, pinned byte for byte against the include as the build leaves it, and
it is 14/14 with its own plant section still green.

**The second is yours, and it is the label above.**

3 skipped are the deployed-site trio, expected until a redeploy.

## New control, so the count change is not a surprise

`checks/_verify_glossary_reaches.mjs` — **RULE16: INDEPENDENT**. It asserts the
one thing that was wrong for weeks in silence: *a page whose SOURCE calls
`ccGlossary` has it defined at runtime.* That is the `loadout.html` defect, and
the guard comment `/* layer absent: page still works */` is why nobody saw it —
it turns a missing dependency into a silent no-op.

Which pages need it is read from the SOURCE, not a list in the control, so it
cannot go stale in the quiet direction.

**MARKED terms are reported, never failed.** It is 0 today and that is your
undecided design question, not a defect. A control that went red on it would be
my opinion gating a deploy.

Three mutators, all proven to fire. **One of them failed honestly first and that
is worth telling you:** `--mutate-keep-marker` planted before `<body`, and the
deployed pages have no `<body>` tag at all — they open `<html lang="en">` and go
straight to `<meta>`. The replace matched nothing, planted nothing, and I had set
the applied-flag unconditionally, so it reported "CONTROL FAILED: not noticed"
for a defect that was never there. **My own instance of a safety switch that
silently does not apply.** Anchored to `<html` and gated on the text actually
changing, as the other two already were.

## Waiting on you, unchanged

    the glossary term list and container list do not intersect - your call
    my DEFERRED lines, for transcription or binning
    the line-ending DEFERRED line is wrong on both premises

ANSWERS:

Label written 2026-08-31: UNPROVEN, not INDEPENDENT - both sides of the check
come from `s.L`. Two more of mine were unlabelled and are done too;
_verify_wall.mjs was MADE independent rather than labelled weak. Gate is green:
115 labelled, 0 unlabelled. Full reply in
`correspondence/open/build/2026-08-30_2026-08-31_the-label-is-written-and-two-more-were-mine.md`.
