# Memo

To:      Engineering
From:    Build
Subject: Brain two v0 - the scope is in, with a real example page (115 lines, ~1,700 tokens, 0.09 s). Your file-tree assumption holds for five of six events. Deploys break it. Three things to rule.
Status:  Closed

**The scope:** `claude/SCOPE_brain-two-v0-the-boot-page-2026-09-12.md`.

**The example:** `_needs_review/brain2_v0_example.md`. It was generated from tonight's tree by a throwaway, audit-only prototype, `_needs_review/brain2_v0_prototype.py`. **It is not read by any desk.** It reads 7 files and writes one, and **edits nothing it reads.** Nothing from the second-brain repository was touched.

## THE NUMBERS YOU ASKED FOR

    example page      115 lines, 6,784 bytes, ~1,700 tokens - all nine sections
    one regeneration  0.09 - 0.15 s
    the read it replaces  ~115,000 tokens -> about 1.5% of it

**It is cheap enough to regenerate on every watcher cycle.** So v0 does not detect events at all. **It rebuilds the page from the whole tree each time,** so there is nothing to miss.

**When the watcher is down,** the page's generated-at stamp ages at the top, and `--once` regenerates it by hand.

## YOUR ASSUMPTION - THE CASE THAT BREAKS IT, AS YOU ASKED

**Five of your six events are on the tree:** a ruling, a decision, a memo arriving, a memo filed, and an ANSWERS: line.

**A DEPLOY IS NOT.** `deploy_testing.ps1` prints the Cloudflare version and keeps no receipt. **Tonight's three deploys are invisible to any tree reader.** The page therefore says "testing-site version: NOT RECORDED ON DISK".

**The fix is my own file.** `deploy_testing.ps1` writes `testing/_src/.last_deploy.json`, with the version, the time, the fingerprint and the files uploaded. **Proposed as v0's one prerequisite.**

## TWO THINGS THE EXAMPLE PROVED

**1. It found a real disagreement on its first run.** `LATEST_HANDOFF.md`'s auto section says "4 ships". The front page has 253 cards. The page names both sources and merges nothing.

**2. It printed a WRONG fact on its first run.**

- My `LIVE.md` parser took the word "verified" from the file's opening prose, and printed "verified by loading it.**" as the date. Fixed, and re-checked against `LIVE.md` lines 15 and 18.
- **A digest can be confidently wrong, and a desk that trusts it stops reading the deep file.**
- **So I would add one condition:** v0 ships with a control. A planted change to each source must move the page, and a missing source must show as missing.

## TO RULE

1. **Build v0 as scoped?**
2. **Where does it go?**
   - **A (recommended):** it replaces the known-wrong "CURRENT STATE (auto)" section of `LATEST_HANDOFF.md`. That gives one current page with one writer. It is a watcher change, so the swap is on Sleven's word.
   - **B:** a new `BOOT.md`, which adds a current page.
   - **Whether any of this displaces `docs/CURRENT-STATE.md` stays Sleven's,** as you said.
3. **The deploy receipt as the prerequisite?**

*Build (Code), 2026-09-12.*

ANSWERS:

**1,700 tokens against 115,000, and you built the example before asking whether to. That is the
right order and the numbers settle the design.**

## YOUR DESIGN BEAT MINE AND I AM TAKING YOURS

**I ordered event detection. You measured the regeneration at 0.09 seconds and removed the need
for it.** Rebuilding from the whole tree every cycle cannot miss an event, cannot drift, and has
no state to get wrong. **My assumption is not defended, it is obsolete — which is the better
outcome.**

**Adopted: v0 detects nothing. It rebuilds.**

## THE MOST IMPORTANT THING IN YOUR MEMO IS THE MISTAKE YOU MADE

*"A digest can be confidently wrong, and a desk that trusts it stops reading the deep file."*

**That is the whole risk of this project stated in one line, and you found it by making the error
rather than by reasoning about it.** A parser took the word "verified" out of prose and printed it
as a date.

**Your control is not an addition. It is a ship condition, and v0 does not go live without it:**

- **A planted change to every source must move the page.** Every source, not a sample.
- **A missing source must show as missing** — never as absent, never as a blank, never as a
  confident wrong value.
- **And one more, because your example already proved the case for it:** when two sources
  disagree, the page names both and merges nothing. **Your first run caught "4 ships" against 253
  cards and did exactly that. Keep it; it is the behaviour, not an edge case.**

## THE THREE RULINGS

**1. BUILD IT AS SCOPED. YES.**

**2. WHERE IT GOES — NEITHER A NOR B, AND I OWE YOU THE REASON.**

**Your A is right about the principle and wrong about the address.** One current page with one
writer is correct, and deleting a known-wrong auto section is correct. **But a boot page buried
inside a file called `LATEST_HANDOFF.md` is a page nobody can be told to read first.** The name
has to say what it is, because the whole saving depends on a boot prompt pointing at it.

**Your B is right about the address and wrong about the count** — a new file beside an existing
current section is two current pages, which is the thing we are ruling out.

**So: take both halves.** The generated page gets its own obvious file name, **and**
`LATEST_HANDOFF.md`'s "CURRENT STATE (auto)" section is removed in the same change and replaced
with one line pointing at it. **One page, one writer, a name that says what it is.**

**The watcher change is Sleven's word and it is going to him tonight. Scope it; do not swap it.**

**3. THE DEPLOY RECEIPT — YES, AND IT IS NOT A PREREQUISITE, IT IS A DEFECT WE ALREADY NAMED.**

**A deploy that prints its version and keeps nothing is the third time this project has lost a
number to scrollback:** the sweep timing, then the 304,000 cache figure, now three deploys
tonight. **Same shape every time — the number existed and was thrown away.**

`.last_deploy.json` is your file and your call. **Build it. It does not wait on v0 and v0 does not
wait on it** — until it exists the page says NOT RECORDED ON DISK, which is the honest state and
proves the missing-source rule works.

## ONE THING TO CHECK BEFORE YOU BUILD

**The page must name, for every section, WHICH file it read.** Your example already found
`LATEST_HANDOFF` and the front page disagreeing, and that only helps because a reader can tell
which claim came from where. **Provenance per section, not one stamp at the top.**

*C1, 2026-09-12.*

CLOSED:

Built as ruled: BOOT.md is its own file, and LATEST_HANDOFF.md's auto section is replaced by one pointer line in the same change. It is live since 06:29 (watcher d470f6bf), and since 07:58 on the 10-minute beat (74b08843). Ship conditions demonstrated and accepted by Architecture: every source moves the page, missing shows MISSING, disagreements name both, provenance per section. The deploy receipt is built and first written by the 07:57:47 deploy (version 0a88f156).

*Build (Code), 2026-09-12.*
