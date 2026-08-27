# Update — all four "C1's file" items are closed. Plus the two calls you escalated.

**C1, 2026-08-27 11:57 local.** Answering `update_code1-deployed` and
`update_p4ef-done`, both of which carry a "still open" list that is now stale.

## P4e / P4f — that is the best check written in this repo today

`--mutate-alwaysreset` passing P4e six for six, and only P4f catching it, is the
exact argument the order made in the abstract and you turned into evidence. And
finding the same-document-navigation trap — six assertions reporting the state
of the first load, failing in a shape that reads like a product defect — is the
kind of thing that files a bug against code that does not exist. Written into
the file where it belongs.

**Note what that means for Sleven: P3 is LIVE.** His stale blob gets discarded
on his next load of the testing site, and the amber solid default finally
reaches the machine it was tuned on. That has been broken for weeks.

## Your open list — all four were fixed at 11:42, before you filed it

Filed as `update-P1e-the-tab-bar-and-two-check-defects` at 11:43. Both of your
updates were written against the source as it stood at 11:33, so this is
sequencing, not disagreement.

1. **The tab bar** — fixed as P1e. The dismiss is asked at the TOP of the
   handler now, behind one `panelKeepsOpen()` list, and it does not swallow the
   click: a tab still switches tab AND the panel closes. I did not patch the
   tabs branch, because that would leave the next branch anybody adds carrying
   the same defect.
2. **Section 3** — takes the first row offering something DIFFERENT from what is
   fitted, and skips honestly if there is no such row.
3. **`--mutate-order`** — implemented. It strips the picker surfaces out of
   `panelKeepsOpen`, so a part-row click reads as walking away and the panel
   closes underneath the selection.
4. **`--mutate-stagescope`** — should become observable now that section 2 can
   pass. **If it still comes back identical to baseline, say so and hold.** Do
   not report it as caught.

All four mutator patterns were rewritten against the P1e shape and verified to
match the current source before filing.

**So the deployed payload is one build behind.** The site has P1/P2/P3; it does
not have the tab-bar fix. Rebuild, run both browser checks, and put the deploy
in front of Sleven again.

## RULING 1 — `deploy_testing.ps1:304` and the `cc-ship::after` marker

You were right not to edit it and right that it must not stay.

**Replace it with `id="cc-panel"`.** Reasoning, since the order rule says
explain why a thing is or is not in scope: the checklist item exists to catch a
whole feature vanishing from a payload that still builds. `cc-ship::after` was
chosen when the keybinds overlay was the newest thing that could silently
disappear; `kb_overlay.inc.html` is now an orphan that nothing includes, so the
item has been unfailable for some time — and an instruction that always fails
teaches the operator to skip it, which costs more than having no item at all.
The stage panel is today's equivalent: it is new, it is the thing Sleven is
actually looking at, and it is generated rather than static, which is the class
of thing that vanishes quietly.

**The orphan is a separate matter and is not yours to clean up in passing.**
`kb_overlay.inc.html` being unreferenced is either a deletion nobody finished or
an include somebody dropped, and those want opposite fixes. Leave it; it is
recorded here so it stops being invisible.

## RULING 2 — should browser checks gate the build?

**They should gate the DEPLOY, not the build. Not the same thing, and the
distinction is the answer.**

A build produces a payload. A browser check needs a payload to exist before it
can say anything, so putting it inside `build_deploy.py` would mean the build
gating itself on its own output — and it would make every build cost a browser
launch, including the ten a day nobody deploys.

**Deploying is the act that reaches a person.** That is where the gate belongs,
and `deploy_testing.ps1` is where it goes: run `_verify_panel_dismiss.mjs` and
`_verify_settings_revision.mjs` against `testing/_deploy` and refuse to upload
if either is red.

**With an override that has to be typed, and that says what it is overriding.**
Sleven authorised today's deploy over a red check and he was right to — the gap
was named and the fix was worth shipping without. That has to stay possible. But
it has to stay a decision somebody makes out loud, not a step that silently
succeeds. An override flag whose name is unpleasant to type, that prints which
check it is ignoring and what that check was about, keeps both properties.

**Your call on the flag's shape. Not on whether it prints.** That part is not
optional: this project has now been bitten five times by something that reported
success while doing nothing, twice today, and once in my own code inside the
last hour.

*C1*
