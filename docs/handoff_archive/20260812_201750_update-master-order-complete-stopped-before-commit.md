# Update — the master order is built and verified end to end. STOPPED before committing: rule 2, and I need a go-ahead in this session.

Everything below is in the working tree. **Nothing committed, nothing pushed,
nothing deployed.**

## Why I stopped rather than pushing

The order's header says *"GO-AHEAD to build, commit, push AND deploy"*, quoting
Sleven: *"Let's fix the things that are broken. Push a new build."*

**Rule 2 is explicit that this is not enough:** *"Actually running `git commit`
or `git push` requires Sleven saying so, in that message, for that change. 'He
said yes to something similar earlier' is not a go-ahead."*

The go-ahead in that document is C1 relaying a decision made before any of this
existed. This session has had no message from Sleven at all. That is precisely
the case rule 2 describes, so the work is staged in the tree and waiting.

Precedent agrees: `daeefc7` went out this afternoon only after a direct
*"yes"* — 16:30's update records it that way.

## Every acceptance item in §7

```
 0  one stick -> js1, swap disabled with a reason, export has one <joystick>,
    one <options>, only js1_ tokens                        PASS (synthetic)
 1  two sticks -> js1/js2, swap exchanges, ten clicks = two states, no js3
                                                           PASS (synthetic)
 2  a stored slot of 3+ is repaired on load                PASS
 3  export: only js1_/js2_, <options> 1 and 2, <devices> matching exactly,
    GUIDs following their sticks across a swap             PASS
 4  one input on two actions live together warns           PASS
 5  an unattested axis says so at capture time             PASS
 6  KBM->JOY ten times, one loop, counter climbing         PASS (frame queue)
 7  #kbbq searches with Capture ON                         ALREADY BUILT
    End scrolls in the tester, a rebind still takes it     PASS
 8  holo: markers land on the hull, fleet spot-checked across all three
    model-scale conventions                                PASS (167 ships)
    Sabre renders without white blowout                    NOT VERIFIED - no browser
 9  fonts present in _deploy, OFL.txt shipped, README truthful
                                                           BLOCKED - rule 8
10  a collector launch that exits does not touch the Desktop
                                                           BUILT, not run - see below
11  roundtrip.js, mutate.js, build_deploy.py, check_deploy_clean.py
                                                           ALL CLEAN
```

## Gates

```
roundtrip.js                     ALL CHECKS PASSED   (+8 new checks)
mutate.js                        22/23  (M18, the documented survivor)
_verify_slots.js                 21/21  mutant fails 14
_verify_conflict.js               7/7   mutant fails 2
_verify_poll.js                  13/13  mutant fails 4
_verify_navkeys.js               10/10  old behaviour fails 4
_verify_holo_placement.py         8/8   self-proof rejects known-bad
build_deploy.py                  6 gates + inline JS parse, all before any write
check_deploy_clean.py            safe to deploy
go vet ./...                     clean
```

Five of those harnesses are new and all six run **inside the build**, before it
writes anything, failing closed when `node` is absent or a gate file is missing.

## Three things that were reported as done and were not

Worth recording, because in each case the greppable evidence pointed the wrong
way:

1. **`#kbbq` search guard** — the order listed it as NOT built with 0 hits. It
   was already built, with its reasoning written beside it. No work needed.
2. **Nav keys** — listed as "partial, 2 hits". Those two hits were the *cause*:
   because `CODE['End']` resolves, the handler reached its `preventDefault`.
   Nothing had been built.
3. **Side-by-side on `/stick-test`** — the CSS had been correct for days and
   could never fire, because `.wrap` caps the page at 780px and two 420px
   columns need 854. Nothing in the CSS looks wrong, which is why it survived.

## What is NOT verified, stated plainly

- **No browser, anywhere in this session.** Everything is Node and Python
  against the shipped modules. The holo white-out fix, the panel layout and the
  live tab-switch behaviour are unverified visually.
- **No hardware.** Two- and three-stick behaviour is synthetic pads only. Per
  §5b: the swap itself, js1-on-the-left ordering and side-by-side with a real
  pair still need the two sticks.
- **The collector was not run.** Doing so writes a shortcut to the Desktop —
  outside the repo (rule 6) and the exact side effect under test. `go vet` and
  `go build` clean; the ordering verified by reading.

## Two decisions waiting on Sleven

1. **Fonts.** Rule 8 — copying the files into `_deploy` is redistribution and the
   README is a licensing document. Five files, ready to go, one word needed.
2. **Commit / push / deploy.** Per rule 2.

**One thing to know before commit:** `build_holo_data.py`, `holo.src.html`,
`holo_data.gen.js` and `kb_actions.gen.js` were **already modified in the tree
before this session started** — the earlier holo fixes and the rotx/roty
correction. A commit sweeps those in alongside mine. They are good work and
green under the same gates, but it should be a decision rather than a surprise.

Suggested split, if the answer is yes — logical commits, per §8, and `git add`
by path, never `-A`:

```
1  slots are 1..N            device_engine.js, keybinds/_layer hosts, _verify_slots.js
2  export cannot produce that file again
                             sc_export.js, keybinds.src.html, roundtrip.js, mutate.js,
                             _verify_conflict.js
3  the poll loop has one owner
                             device_engine.js, both hosts, _verify_poll.js
4  nav keys, layout, button default
                             keybinds.src.html, stick-test.src.html, _verify_navkeys.js
5  collector: a launch that exits leaves the Desktop alone
                             citizen-collector/{main,ui}.go
6  holo viewer on the 167-ship fleet
                             build_holo_data.py, holo.src.html, holo_data.gen.js,
                             _verify_holo_placement.py
7  the harnesses become build gates
                             build_deploy.py
```
