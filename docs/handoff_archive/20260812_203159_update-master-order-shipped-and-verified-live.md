# Update — the master order is committed, pushed and live. Every asset verified byte-for-byte against the build.

Sleven gave the go-ahead in session for both open decisions: commit/push/deploy,
and the fonts.

## Pushed

```
daeefc7..ce984a6  main -> main     verified by re-fetching; local and origin
                                   both at ce984a65eefdf01
```

Seven logical commits, `git add` by path, never `-A`:

```
11b1751  Slots are 1..N now, and the poll loop has one owner
78cd951  The exporter cannot produce that dead file again
9789d2d  The keybind page warns about the conflicts that matter, and scrolls again
eb61435  Two sticks side by side on /stick-test, for real this time
fb90301  A collector launch that exits no longer rewrites the Desktop
525173b  The holo viewer is on the 167-ship fleet, placed from the mesh in front of it
ce984a6  The harnesses are build gates now, and the pages' own scripts get parsed
```

## Deployed

`scripts/deploy_testing.ps1`, never `wrangler pages deploy`. Dry run first —
and the `-WhatIf` is trustworthy here, because this script does **not**
auto-elevate, so it cannot lose its own switch the way `setup_checks_task.ps1`
did on 2026-08-01. I checked that rather than assuming it.

```
13 files uploaded (479 already uploaded)
https://citizencompasstesting.citizencompass-contact.workers.dev
Version ID 6929d5bb-efaa-4eb0-8839-0acd9704cba6
```

## Verified live, and the first attempt was wrong

The script says plainly that exit code 0 is not proof, so:

```
ALL 13 LIVE ASSETS ARE BYTE-FOR-BYTE IDENTICAL TO THE BUILD
  keybinds.html  index.html  stick-test.html  holo.html  sc_export.js
  holo_data.gen.js  kb_actions.gen.js  OFL.txt  all four woff2
  models/Sabre.glb (1,772,312 bytes)
```

**My first comparison said six of them DIFFERED, and it was my check that was
broken.** I compared `Invoke-WebRequest`'s decoded `.Content` re-encoded to
UTF-8, which changes the byte count wherever a file contains a multi-byte
character — the live sizes came out slightly *larger*, and OFL.txt was out by
exactly 12 bytes. The give-away was that the woff2 files matched perfectly: a
real deploy fault does not spare the binaries and hit only the text. Re-ran
against the raw bytes on disk with SHA256 and everything matches.

Worth recording as its own small lesson: **a verification that reads the
artefact through a decoder is not verifying the artefact.**

Behaviour markers confirmed present in the served files, not just in the build:

```
keybinds.html   swapSlot 2 · cc.js.slots.v2 1 · navMayScroll 3 · pafter 2
                kbbunatt 2 · KB_CATEGORIES[b.map] 1
index.html      swapSlot 2 · pollStop 4        (the injected engine reached it)
holo.html       unitScale 3
holo_data.gen.js  "mode": "unit" · 167 ships
```

**The index may serve stale from a cache**, per §8 — I fetched with a fresh
client and got the new bytes, but a browser that has the old page will need a
hard reload. A cached page is not a failed publish.

## Fonts — shipped, on Sleven's word

Four woff2 files plus `OFL.txt` copied from `data-layer/derived/fonts-ofl/` into
`testing/_deploy/fonts/`, **verified byte-identical to the masters before the
build and again after the deploy.** The README no longer says "intentionally
incomplete"; it records the OFL 1.1 requirement that the licence travels with
the fonts, that it was Sleven's instruction and his call, and why the 691-row
action table is deliberately excluded from these faces.

`testing/_deploy/` is gitignored, so the fonts are a deploy asset and not a
commit — the same as `images/` and `models/`.

## One blocked thing, resolved by moving rather than deleting

`git add` failed on a stale `.git/index.lock` — zero bytes, 50 minutes old, no
`git` process running. Per rule 1 it was **moved to `_to_delete/`**, not
deleted:

```
_to_delete/git_index.lock_stale_from_193856_moved_20260812_202803
```

Sleven deletes it. Nothing else was touched to get git working.

## What is live but still unverified

Unchanged from the build report, and worth repeating now that it is public:

- **No browser was ever opened.** The holo white-out fix, the panel layout and
  the tab-switch behaviour are proven by analysis and by harnesses, not by
  looking at them.
- **No hardware.** Two- and three-stick behaviour is synthetic pads. The swap
  itself, js1-on-the-left and side-by-side with a real pair still need the two
  sticks.
- **The collector was not run** — doing so writes to the Desktop, which is both
  outside the repo and the exact side effect under test. It is also **not
  released**; §6 forbids that and nothing was published.

Next: reading `docs/prompt-code-collector-log-first-redesign-2026-08-13.md`,
which Sleven flagged mid-session, noting that C1 has a correction coming on §5.
