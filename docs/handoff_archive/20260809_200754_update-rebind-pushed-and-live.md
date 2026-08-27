# Update — rebind flow pushed and live, plus a deliverable I had left uncommitted

Sleven: "push it". Committed, pushed, deployed, verified.

## Two commits

**`f8b501c` — "You can now change a binding, not just look at it"**
`testing/_src/keybinds.src.html` only. 454 insertions, 22 deletions.

**`2e24515` — "Land the exporter checks that were reported done but never staged"**
`checks/node_checks.py`, `checks/_verify_node_checks.py`, `run_checks.py`.

### The second commit is a miss of mine, and it is worth naming

`checks/node_checks.py` and its verifier were **built for order 1, named in that
order's own acceptance list (§7.5), reported by me as done — and never
committed.** C1's staging list did not include them. That order explicitly said
to *"cross-check against your own knowledge of what you built and correct if
anything's missing"*, and I followed the list without doing that.

So for the last few hours the repo has claimed a checker it did not contain.
`run_checks.py`'s cp1252 fix was in the same gap — the fix for the crash that
killed the entire `file` group on a ship name with a macron.

Both are in now. Verified working before committing: the two checkers report
through `run_checks.py --group file`, and `_verify_node_checks.py` still passes
all twelve of its cases.

## Push

```
9dc7acf..2e24515  main -> main
```

Confirmed by re-fetching: `origin/main` resolves to `2e24515`, branch in sync.

## Deploy and live verification

One changed asset uploaded, `keybinds.html`. Version `d08fbb2b-150c-46e3-80d7-3c4c2c912949`.

`/keybinds` serves **93,409 bytes, byte-identical to the local build**, HTTP 200,
and the served page carries `window.KBEDIT`, `SC_KEY_FROM_CODE`, `kbOverlay`, the
expand-all control, the change counter, the intro block, and the listening
prompt.

## Regression, run before any of the above

`roundtrip.js` ALL CHECKS PASSED · `mutate.js` 19/20 with M18 · rebind suite
ALL REBIND CHECKS PASSED · build and deploy guard clean.

## Left out, deliberately

`place_hardpoints.py` (predates this work), `_c1_verify_wo.py` (unknown, not
mine), and the two 2026-08-02 scratch files. `citizen-collector/` untouched —
its browser-socket selftest is still uncommitted, which remains correct.
