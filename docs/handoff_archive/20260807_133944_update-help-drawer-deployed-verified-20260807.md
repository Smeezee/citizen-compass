# Update — HELP drawer deployed to testing and verified on the deployed page (2026-08-07)

**Testing URL:** https://citizencompasstesting.citizencompass-contact.workers.dev

Deployed with `scripts/deploy_testing.ps1` (Workers static assets, not Pages).
Netlify and live untouched.

## The trap fired, and it was worth checking

The first run of the test suite against the **deployed** URL reported the HELP
tab missing — exactly the failure mode the work order warned about, and exactly
why the instruction was "open the deployed page to confirm, not the source."

It was **not** a missed substitution. Checked rather than assumed:

- deployed `index.html` is 1,584,562 bytes, byte-for-byte the local build's size
- deployed page contains `cc-help-tab` (7 occurrences) and `cc-kb-hinthelp`
- the only `__BUILD_INJECTS__` occurrences left are the renderer's own tripwire
  references, which is correct

The real cause was in my test: a fixed 300ms sleep after the password gate.
That is fine on a `file://` build and a race over the network on a 1.5MB page
whose drawer script sits near the end of it. Replaced with an explicit
`waitForFunction` on the drawer announcing itself. A fixed sleep standing in for
a readiness check is the same species of defect as a gate that cannot fail —
it passes for a reason unrelated to what it claims to prove.

## Verified on the deployed page

**38 passed, 0 failed** against the live testing URL, including every negative
control.

Measured content width, `#cc-kb`, at 1920x1080, on the deployed page:

| state | width |
|---|---|
| drawer closed | **1874px** |
| drawer open | **1454px** |
| delta | **420px** — the drawer width |

The keyboard board genuinely re-lays-out into the narrower region: keys narrow,
the mouse block moves in, the device selector and the mode/device rows all stay
visible and clickable. Nothing sits behind the panel.

Read on screen at 1920x1080 across four node types — question (with HOW TO
CHECK), fix (steps, note, and the continue button naming the retest it leads
to), choice, and the dead end with the VKB hand-off and its KNOWN CATCH callout.

## Committed

Committed to `main`. **Not pushed** — no go-ahead given, per hard rule 2.
