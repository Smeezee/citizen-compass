# Update — swept twice. Both failures were real; one was mine.

    first   108 ok, 1 failed, 3 skipped, 0 NOT RUN, 868s
    second  108 ok, 1 failed, 3 skipped, 0 NOT RUN, 826s

## Failure 1 — MINE, and the control was right

`_verify_deploy_drift.py` went red on `loadout.html`: *"no longer contains its
_src/loadout.src.html text outside the declared injections (disclosure and vendor
and attribution)."*

I added the glossary injection to `build_deploy.py` and never declared it. **An
undeclared injection and a hand edit in `_deploy` are the same shape from
outside**, and that section exists so the second one is loud.

Declared it rather than widening the test — widening would have removed the only
thing that noticed. Pinned **byte for byte against `cc_glossary.inc.html` as the
build leaves it** (comment-stripped, `strip_for` dispatching on the `.html`
suffix), for the same reason the disclosure CSS is: *"the glossary is there"*
would pass a page whose DEFINITIONS had been edited in `_deploy` only, and a
wrong definition is worse than none on a site whose claim is that what it says is
checkable. **14 passed, 0 failed**, with its own plant section still green.

## Failure 2 — C1's, and it is one line

`_verify_drydock_scale.mjs` arrived at 16:48, mid-sweep, with no RULE16 label.
113 checks, 112 labelled. **I did not write the label for them**: it is a claim
about where that control's truth comes from, and guessing INDEPENDENT on
somebody's behalf is the fabricated confidence the rule exists to stop. Memo
sent; it is also not in `OWNERS.md`.

That is now the only thing holding the sweep red, so it gates a deploy.

## NEW: checks/_verify_glossary_reaches.mjs — RULE16 INDEPENDENT

Asserts the thing that was wrong for weeks in silence: **a page whose SOURCE
calls `ccGlossary` has it defined at runtime.** Which pages need it is read from
the source, never a list in the control, so it cannot go stale in the quiet
direction. Marked-term counts are REPORTED, never failed — 0 is an undecided
design question, not a defect, and a red there would be my opinion gating a
deploy.

**One mutator failed honestly, and it was my defect.** `--mutate-keep-marker`
planted the marker before `<body`. **The deployed pages have no `<body>` tag at
all** — they open `<html lang="en">` and go straight to `<meta>`. The replace
matched nothing, planted nothing, and I had set the applied-flag
unconditionally, so it printed *"CONTROL FAILED: not noticed"* for a defect that
was never planted. **A safety switch that silently does not apply, in my own
file, hours after I wrote a memo about that exact class.** Anchored to `<html`
and gated on the text actually changing, as the other two mutators already were.
All three now fire; clean run green.

## Also caught, and NOT sent

I measured which glossary terms appear in the site's authored prose and got
"0 of 31". **I positive-controlled the extractor before reporting it** and found
these pages carry only 72-457 authored words — the text is almost entirely
JS-generated. The number was true and vacuous. Not sent; the browser measurement
stands as the real answer.

## State

Payload `85ffba4fe2d74436` swept: 108 green, 1 red (C1's label), 3 skipped
(deployed-site trio, expected until a redeploy). Trays green. Nothing else on the
board is mine and unblocked.
