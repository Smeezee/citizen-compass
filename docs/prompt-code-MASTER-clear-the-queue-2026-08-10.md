# PROMPT FOR CODE — clear the whole queue, then push and deploy

    from    C1, 2026-08-10
    for     Code
    basis   Sleven, just now: "I would like you to fix all these problems
              yourselves or give me the prompt to give to code... All the stuff
              that was supposed to be done on the website didn't get pushed
              before I ran out of weekly credits. Weekly credits are back up
              now. Now move."
    status  GO-AHEAD GIVEN for commit, push AND deploy at the end of this
              order. That is Sleven's own instruction above, not an assumption.
              This is the one thing in this document that is not conditional.

---

## 0. First, a correction — nothing was stranded by the credit cutoff

**Verified before writing this, not assumed:**

```
git log --oneline origin/main..HEAD    -> EMPTY. Zero unpushed commits.
grep -c "listening" testing/_deploy/keybinds.html    -> 12
grep -c "listening" testing/_src/keybinds.src.html   -> 12
```

Everything committed is on `origin/main`, and the rebind flow is live on the
deployed page. **Sleven believes work was lost to the credit cutoff. It wasn't.**
Say so plainly in your report back so he stops looking for a phantom problem.

**What actually happened:** four fix orders were written and filed to `docs/`
and never executed. That's the entire gap. This document is the run order.

---

## 1. Run these four existing orders, in this sequence

**Do NOT re-read their contents from this document — they are not restated here
on purpose.** This project has been bitten five times by one artifact having two
writers and the copies drifting (hard rule 14). Each order below is the single
writer of its own instructions. Read each file and execute it as written.

Sequence matters — 1a and 1b touch `holo.src.html`, 1c and 1d both touch
`keybinds.src.html`, so do the keybind pair back-to-back to avoid two rounds of
rebuild-and-verify on one file:

| order | file | what it covers |
|---|---|---|
| 1a | `docs/prompt-code-holo-viewer-fixes-and-fleet-2026-08-10.md` | white-hull blowout, marker cm→m scale, 167-ship fleet dataset |
| 1b | *(same file, §3)* | the fleet-dataset swap — read the `pos_model` warning carefully, it is the exact trap §2 is about |
| 1c | `docs/prompt-code-keybind-rebind-joystick-2026-08-10.md` | HOTAS/gamepad rebind capture (reuse `poll()`/`fireDev()`, do not rebuild) |
| 1d | `docs/prompt-code-keybinds-search-and-navkeys-2026-08-10.md` | dead `#kbbq` search under Capture-ON, End key eaten instead of scrolling |

**Two things I re-verified in the source just now, so you don't have to
re-establish them:**

- Joystick rebind genuinely is not there. `keybinds.src.html` lines 1786 and
  1795 are the only two `commit(...)` calls, both `'kb1_' + ...`. Keyboard and
  mouse only, exactly as 1c describes.
- `#kbbq` genuinely has no guard. It's declared at line 1555, read into `elQ` at
  1594, and there is no `stopPropagation` anywhere near it — unlike `#q`, which
  has one. 1d's root-cause claim is correct.

## 2. Fonts — land them. The licence question is closed.

**Five files are staged and waiting** at `data-layer/derived/fonts-ofl/`
(verified on disk just now): `SairaCondensed-SemiBold.woff2`,
`SairaCondensed-Bold.woff2`, `Rajdhani-SemiBold.woff2`,
`ChakraPetch-SemiBold.woff2`, `OFL.txt`. `testing/_deploy/fonts/` currently holds
only `README.txt`.

**The licence question that blocked this is answered and is not yours to
re-open.** C3 read the actual `LICENSE` file inside each font's real
distribution package — all three families are genuine SIL OFL 1.1,
redistribution permitted with `OFL.txt` travelling alongside. Record:
`docs/handoff_archive/20260809_201131_HANDOFF_fonts-are-on-disk-2026-08-10.md`.
Sleven's decision to ship them is made.

**Do:**

1. Copy all five files into `testing/_deploy/fonts/`. `OFL.txt` ships too — it
   is a licence condition, not documentation. It is not optional and it does not
   get trimmed.
2. **Rewrite `testing/_deploy/fonts/README.txt`.** It currently says this
   directory is "INTENTIONALLY INCOMPLETE," which is now factually false. State
   what is here, which families, that they are OFL 1.1, and that `OFL.txt` must
   ship with them.
3. Confirm the `@font-face` rules and `DEFAULT_ALLOWED_DIRS` already accommodate
   this — C3 says they do, and `fonts/README.txt` was already in the 8 deployed
   assets of `9dc7acf`, which corroborates it. **Check rather than trust; if a
   guard fails, that's a real finding, report it.**

### 2b. Scope — chrome only. This is my call and I'm naming it as mine.

Sleven hasn't answered the chrome-vs-content question, and this order is not
worth stalling on it, so I'm making the call and it is cheaply reversible.

**SC fonts go on chrome only** — headings, tab labels, panel titles, buttons.
Marked `.cc-ui`. **The 691-row action table content is NOT marked `.cc-ui`** and
keeps following whatever font the reader picked in the accessibility switcher.

**Why, so nobody re-litigates it from scratch:** `_layer.src.html` already ships
a five-mode accessibility font switcher including Atkinson Hyperlegible, a
low-vision face. Every rule is scoped `*:not(.cc-ui):not(.cc-ui *)` — so marking
the whole keybind panel `.cc-ui` would make the single densest, smallest-text
screen on the site the one screen that ignores a low-vision reader's setting.
Saira Condensed makes that strictly worse, because condensed faces are harder to
read at low vision, not easier. This is C3's recommendation in
`docs/RULING_holo-viewer-models-keybind-overlay-and-fonts-2026-08-09.md` §3 and
I'm adopting it.

**If Sleven later wants SC type across the content too, that's his call to make
knowingly.** The point of doing it this way round is that going chrome-only
first and widening later is a one-line change, whereas shipping it everywhere
and then discovering the accessibility hole is a regression somebody has to
notice first.

## 3. Collector — fix the shortcut ordering

**Confirmed by Code's own investigation**
(`docs/handoff_archive/20260809_203154_update-feed-404-folders-investigated-and-a-mistake-i-made.md`):
the "two folders on the Desktop" Sleven complained about are two `.lnk`
shortcuts, and they get rewritten on **every** launch — including a launch that
creates them and then immediately exits because another collector is already
running. Which is exactly what happens when somebody clicks the icon while the
collector is running behind the game.

**The cause is ordering in `main.go`'s double-click branch** — reported as
roughly:

```
894  AskConsent(...)
906  OfferShortcuts(...)      <-- shortcuts written here
921  runUI(...)               <-- single-instance check lives in here
```

**Fix: move `OfferShortcuts` to AFTER the single-instance check**, so a launch
that is going to exit never touches the Desktop or Start Menu. Code proposed
exactly this and correctly held for a go-ahead. **Go-ahead given.**

**Verify those line numbers against the real file rather than trusting them** —
they're from a report, and this project's own standing rule is that a status
brief is not evidence.

**Do NOT try to repoint Sleven's actual shortcuts.** They're currently aimed at
a dead scratch folder from the investigation run, the rule-6 guard correctly
blocked fixing them from here, and Sleven has been told to repoint or delete
them himself. Leave that alone. **You may remove the `DesktopSim` scratch folder
only after he confirms the shortcuts are repointed** — not before, or the
shortcuts dangle.

## 4. What NOT to do

- **Do not `git add -A`.** 50 tracked files show as modified with 191,317
  insertions and 191,317 deletions — pure CRLF/LF churn, verified byte-identical
  after stripping CR. Stage by explicit path, every time, and confirm the file
  list before committing.
- **Do not commit these**, all currently untracked or noise:
  `testing/_src/_modelfolders.txt`, `testing/_src/_scunpacked_names.json` (both
  predate this work by a week, nothing references either), and the modified
  `testing/_src/fixtures/real_export*.xml` unless you can say why they changed.
- **Do not touch `MANUAL_MATCHES`.** The Cutlass Black "Best In Show" airframe
  question is unanswered game knowledge and is Sleven's alone. Leave it empty. A
  guess here silently produces 15 wrong hardpoint markers that look exactly as
  confident as correct ones.
- **Do not publish a collector release or install `gh`.** Sleven hasn't answered
  that yet. The 404 is currently the *safe* state — a feed pointing at a
  nonexistent asset would turn a clean "no update found" into a failed download
  on every install every six hours.
- Do not mark the action-table content `.cc-ui` — see §2b.

## 5. Then commit, push and deploy

**This is the part that has Sleven's explicit go-ahead**, so don't stop and ask
again for it.

1. Commit in **logical commits, not one lump** — the holo fixes, the keybind
   fixes, the fonts, and the collector ordering fix are four unrelated things
   and should read as four things in the log a year from now.
2. Push to `origin/main`. **Verify by re-fetching, not by trusting exit 0** —
   same discipline as `9dc7acf`.
3. `python testing/_src/build_deploy.py`, then `check_deploy_clean.py`, both
   must pass clean before deploying.
4. Deploy to `citizencompasstesting` via the deploy script — **not
   `wrangler pages deploy`**, which publishes to a different URL while reporting
   success. This project has hit that silent failure five times.
5. **Verify live assets byte-for-byte against local `_deploy/`**, same as the
   `9dc7acf` deploy did. Exit 0 is not verification.

## 6. Report back

- Explicit confirmation that nothing was lost to the credit cutoff (§0) — Sleven
  needs to hear that from you as well as from me.
- Per-order results for the four in §1, in their own words' acceptance terms.
- The `pos_model` vs `unit` choice you made for the fleet dataset, and why.
- Which ships you spot-checked across the three model-scale conventions.
- Confirmation `OFL.txt` is in the deployed asset list.
- What the collector's launch actually writes now, run fresh, observed not
  theorised.
- The live-asset byte verification result.

## Commands

```
node testing/_src/roundtrip.js
```

```
node testing/_src/mutate.js
```

```
python testing/_src/build_deploy.py
```

```
python testing/_src/check_deploy_clean.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```
