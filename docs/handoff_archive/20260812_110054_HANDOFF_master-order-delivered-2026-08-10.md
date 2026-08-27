# HANDOFF — the master order is filed, and nothing was lost to the credit cutoff

    from    C1, 2026-08-10
    for     Code, and the next session that reads LATEST_HANDOFF.md
    basis   Sleven: "All the stuff that was supposed to be done on the website
              didn't get pushed before I ran out of weekly credits. Weekly
              credits are back up now. Now move."

---

## 1. The premise was wrong, and that matters more than the fix

Sleven believed work was lost when his weekly credits ran out. **Verified
against the repo, not reasoned about:**

```
git log --oneline origin/main..HEAD          -> EMPTY (zero unpushed commits)
grep -c "listening" testing/_deploy/keybinds.html   -> 12
grep -c "listening" testing/_src/keybinds.src.html  -> 12
```

**Everything committed is on `origin/main`. The rebind flow is live on the
deployed page.** Commit history confirms it: `9dc7acf` (keybind page reads and
writes a real profile), `f8b501c` (you can now change a binding), `2e24515`
(exporter checks), `6a4edbf` (three days of collector work). All pushed.

**What actually happened:** four fix orders were written and filed to `docs/`
and Code never ran them. That's the entire gap. Nothing was lost; four things
were queued and never picked up. Whoever reports back to Sleven should say this
explicitly — he is otherwise going to keep looking for a phantom problem.

## 2. What's now in the queue

`docs/prompt-code-MASTER-clear-the-queue-2026-08-10.md` — filed via `inbox/`,
watcher confirmed at 10:59:26. It is the run order for everything outstanding
and it **carries Sleven's explicit go-ahead to commit, push AND deploy** at the
end, which is unusual and is stated plainly in the document.

It sequences four existing orders (deliberately by reference, not restated — one
writer per artifact, hard rule 14):

- `docs/prompt-code-holo-viewer-fixes-and-fleet-2026-08-10.md`
- `docs/prompt-code-keybind-rebind-joystick-2026-08-10.md`
- `docs/prompt-code-keybinds-search-and-navkeys-2026-08-10.md`

plus two things not previously ordered: landing the fonts, and the collector
shortcut-ordering fix.

**Two source facts re-verified so Code doesn't have to re-establish them:**
joystick rebind genuinely is absent (lines 1786 and 1795 are the only two
`commit(...)` calls, both `'kb1_' + ...`), and `#kbbq` genuinely has no
`stopPropagation` guard (declared 1555, read into `elQ` 1594, no guard anywhere
near it) unlike `#q` which has one.

## 3. Fonts — the licence question is closed, and I made the scope call

Five files staged and verified on disk at `data-layer/derived/fonts-ofl/`;
`testing/_deploy/fonts/` still holds only the placeholder `README.txt`.

C3 read the actual `LICENSE` file inside each font's real distribution package —
Saira Condensed, Rajdhani and Chakra Petch are all genuine SIL OFL 1.1,
redistribution permitted with `OFL.txt` travelling alongside. That closes the
"confirm the licence before shipping" condition.

**Scope call, made by C1 rather than stalling the order, and flagged as C1's:**
SC fonts on chrome only (headings, tab labels, panel titles, buttons — `.cc-ui`),
**not** on the 691-row action table. Reason: `_layer.src.html` already ships a
five-mode accessibility font switcher including Atkinson Hyperlegible, scoped
`*:not(.cc-ui):not(.cc-ui *)`. Marking the whole keybind panel `.cc-ui` would
make the densest small-text screen on the site the one screen that ignores a
low-vision reader's setting, and Saira Condensed is a condensed face, which makes
that strictly worse. This is C3's recommendation in
`docs/RULING_holo-viewer-models-keybind-overlay-and-fonts-2026-08-09.md` §3,
adopted. **Chrome-only first and widening later is a one-line change; shipping
everywhere and discovering the accessibility hole later is a regression somebody
has to notice first.** Sleven can overrule it knowingly.

## 4. Sleven's shortcuts are currently broken and only he can fix them

The investigation run on 2026-08-09 overwrote his real Desktop and Start Menu
`Citizen Collector.lnk` files, pointing them at a scratch folder. The rule-6
guard correctly blocked repointing them from inside a session. He's been told:
repoint both to the real `citizen-collector\collector.exe`, or delete both and
let the next real launch recreate them. **`DesktopSim` is deliberately still in
place so they launch something rather than dangling — do not remove it until he
confirms the shortcuts are fixed.**

## 5. Still Sleven's alone, unanswered, and deliberately not guessed

- **Cutlass Black "Best In Show" airframe** — same as base or not. `MANUAL_MATCHES`
  stays empty. A guess produces 15 wrong markers that look as confident as right
  ones.
- **Publishing a collector release / installing `gh`** — not authorised. The
  update-feed 404 is currently the *safe* state; a feed pointing at a nonexistent
  asset turns a clean "no update found" into a failed download on every install
  every six hours.
- **Cloud-upload R2 bucket + Worker + key** — account-level, offered, unanswered.
- **UEX token, PostgreSQL password, Cloudflare token** — all three still
  unrotated after exposure.
- **CIG description-rights question** — 5,344 item descriptions still cannot ship.
