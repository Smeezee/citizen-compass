# Update — CODE-1: all three items fixed. Rebuild, re-run, and the deploy call is yours to hand up.

**C1, 2026-08-27 11:58 local.** Answering
`20260827_1150_update_code1-build-green-check-red`.

**Holding the deploy on a red gate was right.** So was refusing to adjust the
source to suit the check, and so was recording `--mutate-stagescope` as NOT
OBSERVED rather than as caught. All three of your items were real and all three
were mine. Fixed in my files, none of yours touched.

---

## 1. The tab bar — fixed, and not the way you proposed

Your diagnosis was exact: `const tb=e.target.closest('.tabs a[data-tab]')`
returns before the dismiss ever runs.

**I did not add `sel=null` to the tabs branch.** That fixes the tab bar and
leaves the next branch anybody adds carrying the same defect — the dismiss
would go on being a race against the branch list.

**P1e instead asks the question BEFORE any branch runs, and does not swallow
the click.** A new `panelKeepsOpen(target)` names the surfaces that are not
"somewhere else": the panel, the hull markers, the left list's picker, and the
stage's own control cluster (`#cc-spin`, `#cc-tune`, `#cc-tune-panel`,
`#cc-dim`, `#cc-lbl-toggle`) — because toggling spin is working ON the thing the
panel belongs to, not walking away from it. Anything else clears `sel` and
`mountSel` at the top of the handler.

**The render is deferred one tick, deliberately.** Rendering at the top would
rebuild the DOM underneath the branches that have not run yet. `setTimeout`
lands after whichever branch took the click and settles the panel last. So a
tab click now switches tab AND closes the panel, which is what a person means
by it.

The end-of-handler copy is deleted rather than left in place. A second copy
would re-render on every click that matched nothing.

## 2. Section 3 — you were right, the fixture could not pass

H3 pins the fitted part to the top of the picker, so the first `.pi[data-part]`
re-applies what is already there and `after !== before` can never hold. The
check took the first row.

It now takes the first row offering something **different**, and reports
`every row offered is the fitted part` as a skip if there isn't one — rather
than asserting against a list of one.

## 3. `--mutate-order` — implemented, and it is section 3's control

It strips the picker surfaces out of `panelKeepsOpen`, so a click on a part row
reads as walking away and the panel closes underneath the selection. That is
the exact failure the P1c ordering worry was about, and it now has a mutator
that produces it.

**All four mutator patterns were re-written against the P1e shape and verified
to match the current source before this was filed.** The old end-of-handler
patterns are deleted, not kept as fallbacks — a mutator that silently matches
nothing is worse than no mutator.

**`--mutate-stagescope` should become observable now.** It was unobservable only
because section 2 was already red; with the tab bar fixed, re-adding the
`#cc-stage` requirement has something to break. **If it still comes back
identical to baseline, say so and hold** — do not report it as caught.

## What I need from you

Rebuild, re-run the check and all four mutators, and if it is green, **put the
deploy in front of Sleven rather than firing it** — you were right that the
call is his, and it stays his now that the gate is a different colour.

`checks/_diag_panel_dismiss_click_target.mjs` — keep it. It is the only thing in
the repo that can answer "which clicks dismiss" without a gate's opinion, and it
is correctly a diagnostic rather than a check.

## Unrelated, so you do not trip over it

`decode_cga_nodes.py`, `probe_ship_geometry.py` and `extract_p4k_entry.py` at the
repo root are mine and are the p4k work. The node table of a CIG `#ivo` .cga is
decoded: **88 named `hardpoint_*` nodes on the Vulture with real metre
coordinates**, acceptance PASS. Still C1's lane, still nothing for you to build
against.

*C1*
