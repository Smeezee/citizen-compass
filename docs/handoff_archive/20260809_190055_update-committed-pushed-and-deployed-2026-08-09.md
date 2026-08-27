# Update — committed, pushed, deployed, and verified live. Sleven can test now.

Sleven's go-ahead executed in full. Concrete results below, not "it worked".

## Commit `9dc7acf` — 22 files, scoped

**"The keybind page can now read a real profile and write it back"**
22 files changed, 3,995 insertions, 182 deletions.

Staged by explicit path, never `git add -A`. Verified before committing:
**0 files from `node_modules/`, 0 from `citizen-collector/`, and nothing outside
`testing/_src/` + the three root generators + `.gitignore`.** The ~50 CRLF-churn
files elsewhere in the tree are untouched.

The commit message states what is still incomplete — fonts, 2-of-4 model
coverage, the empty section descriptions, and that nothing generated has been
loaded by Star Citizen — so the commit does not overclaim on its own.

### The two files C1 could not classify: LEFT OUT

`testing/_src/_modelfolders.txt` and `testing/_src/_scunpacked_names.json` are
both dated **2026-08-02 01:43** — a week before any of these four orders — and
`grep` finds **nothing** in the repo referencing either. Stale scratch, not
artifacts of this work, so they stay untracked.

`place_hardpoints.py` also **left out**, deliberately: it predates these orders,
2B only consumes its output, and putting it in this commit would attach it to a
change it had no part in. Better as its own commit by whoever can describe the
derivation properly.

## Push — landed on `origin/main`

```
ba25d9c..9dc7acf  main -> main
```

Verified by re-fetching afterwards rather than trusting exit 0: `origin/main` now
resolves to `9dc7acf` and the branch reports in sync with no ahead/behind.

**Three commits went up, not one.** Two were already sitting unpushed locally
from 2026-08-07/08 — `77623fa` (importer preservation) and `8f27c8f` (the two
checkers that reported success by never looking). They are legitimate committed
work from earlier sessions and a push of `main` necessarily carries them.
Flagging it because it was not in the order's expectation of "the first push
since ba25d9c".

## Deploy — `citizencompasstesting`, 8 files changed

Ran `scripts/deploy_testing.ps1`, not a raw `wrangler` call. Guard passed,
payload 486 files / 348.7 MB, 8 new-or-modified assets uploaded:

```
index.html  keybinds.html  holo.html  sc_export.js
kb_actions.gen.js  kb_modes.gen.js  holo_data.gen.js  fonts/README.txt
```

Version ID `294e69ab-265f-40e8-8201-3a31749f5027`.

## Live verification — byte sizes against local `_deploy/`

The script says plainly that exit 0 is not proof, so:

| asset | local | live | code |
|---|---|---|---|
| `sc_export.js` | 16,417 | 16,417 | 200 |
| `kb_actions.gen.js` | 114,028 | 114,028 | 200 |
| `holo_data.gen.js` | 4,317 | 4,317 | 200 |
| `kb_modes.gen.js` | 49,439 | 49,439 | 200 |
| `models/Sabre.glb` | 1,772,312 | 1,772,312 | 200 |
| `/` | 1,590,139 | 1,590,139 | 200 |
| `/keybinds` | 73,988 | 73,988 | 200 |
| `/holo` | 1,183,082 | 1,183,082 | 200 |

**Every one exact.** The live keybind page carries `sc_export.js`,
`kb_actions.gen.js`, `id="pimport"`, `id="kbb"`, `UNATTESTED` and the Saira
Condensed declarations.

**A false alarm I nearly reported as real:** my first pass used two separate
`curl` calls per file and produced "200 with 0 bytes" and "404 with a matching
size". Both were artifacts of the two-request method, not the deploy. Re-run as
one request per file, everything is clean. Worth recording — a verification that
lies in the alarming direction still wastes the next person's time.

## Two things to know before testing

**1. The URLs drop `.html`.** `/keybinds.html` 307-redirects to `/keybinds`, and
`/holo.html` to `/holo`. That is Workers' clean-URL normalisation, not the
password gate and not a fault. **Use the extensionless URLs:**

```
https://citizencompasstesting.citizencompass-contact.workers.dev/keybinds
https://citizencompasstesting.citizencompass-contact.workers.dev/holo
```

**2. Only `index.html` is behind the password gate.** `/keybinds`, `/holo`,
`/loadout` and `/find` serve with no gate — confirmed, `cc-gate` appears in
`index.html` alone. That is pre-existing for the first three (PAGES copies them
verbatim, the gate is only injected into the index build), and **`/holo` now
follows the same ungated pattern**. Nothing here changed the gate; the new page
just inherits how copied pages have always behaved. Raising it because a new
publicly-reachable page is worth knowing about rather than discovering.

## Scope held

No fonts fetched. `MANUAL_MATCHES` still empty — no Cutlass/Aquila guess. No
section descriptions invented. `citizen-collector/` untouched: its
browser-socket selftest work is still uncommitted in the working tree, which is
correct, since this go-ahead did not cover it.
