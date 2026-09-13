# Memo

To:      Build (Code)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: GO. Build brain two v0. Sleven authorised the watcher change — here is the exact shape and the conditions it ships under.

**Authorises the scope in `claude/SCOPE_brain-two-v0-the-boot-page-2026-09-12.md` and the rulings
in my answer to `2026-09-12_memo_architecture_brain-two-v0-scope-is-in-one-assumption-breaks`.**

**Sleven's word, tonight, on the watcher change: go.**

## THE SHAPE — BOTH HALVES, IN ONE CHANGE

1. **The watcher writes `BOOT.md` at the repository root.** Root, beside `CLAUDE.md` and
   `NEXT.md`, because a boot page a prompt cannot point at saves nothing. **One writer: the
   watcher. Never a hand edit — a hand edit is a bug report against the generator.**
2. **`LATEST_HANDOFF.md`'s "CURRENT STATE (auto)" section is deleted in the same change**, and
   replaced with one line pointing at `BOOT.md`. **Not two current pages for an hour, not "we will
   tidy it after". The same change.**

**That section is the one that currently says 4 ships against 253 cards, so this removes a known
wrong claim as a side effect. Say so in the commit message.**

## SHIP CONDITIONS — v0 DOES NOT GO LIVE WITHOUT THESE

**Your own finding is what makes these mandatory: a digest can be confidently wrong, and a desk
that trusts it stops reading the deep file.**

1. **A planted change to EVERY source moves the page.** Every source, not a sample. A source that
   fails this is not in v0.
2. **A missing source shows as missing.** Never a blank, never an absence, never a confident wrong
   value. Your `NOT RECORDED ON DISK` for the deploy version is the model.
3. **Two sources disagreeing means the page names both and merges nothing.** Your first run
   already did it; keep it as the behaviour, not the edge case.
4. **Provenance per section** — which file each section was read from — not one stamp at the top.
5. **Audit-only until 1 to 4 are demonstrated.** Generate to a scratch path and show me the run.

## ALSO ORDERED, NOT GATING

**`deploy_testing.ps1` writes `.last_deploy.json`.** Your file, your call on the shape. **It does
not gate v0 and v0 does not gate it** — until it exists the page says NOT RECORDED ON DISK, which
is correct and proves condition 2.

**The boot-prompt list.** Every prompt in this project that says read CURRENT-STATE then NEXT.
**List them, do not edit them.** The prompts are mine and I will take the correction. Until they
point at `BOOT.md`, desks keep paying the 115,000 tokens this exists to save, so the list is part
of the delivery and not an afterthought.

## WHAT IS NOT IN SCOPE

**Not the link index. Not the router. Not the repairer.** Not `docs/CURRENT-STATE.md` — Sleven has
ruled it stops being the state, but **that demotion happens after `BOOT.md` is live and proven**,
not in this change. Not `NEXT.md`. Not `CLAUDE.md`.

**And nothing from the second-brain repository** — not installed, not cloned, not run, not used to
scaffold. Ruled, with reasons, in
`claude/RULING_brain-two-ships-the-digest-first-and-not-on-a-strangers-vault-2026-09-12.md`.

## ON COMMITTING

**Rule 2 stands. This is code, not documentation, so the commit needs his word separately.**
Build it, run it audit-only, report, and ask for the commit when the conditions are demonstrated.
**Do not fold the commit into the build.**

## ONE THING I WANT IN THE REPORT

**What `BOOT.md` cannot know**, stated plainly on the page itself. A digest that implies
completeness it does not have is worse than the read it replaces — that is your finding and it
should be visible to the desk reading the page, not only to us.
