# Update — the bounce folder is watched and every tray reports its depth

**2026-09-09 16:50 CDT.** Two additions to `checks/_verify_correspondence.py`,
one from each of two desks asking for the same thing. Built once.

## (a) UNDELIVERED POST — AND THE PATH WAS WRONG

**The audit desk reported the bounce folder as `correspondence/_needs_review/`.
That folder does not exist.** Architecture said so and told me to find the path
the router actually uses. It is:

    watcher-go/main.go:113
      needsReviewDir = filepath.Join(projectRoot, "_needs_review")

**At the REPO ROOT, not under `correspondence/`.** The control now asserts on the
path the router actually uses. `routeSimple` in `classify.go:336` does
`os.MkdirAll` on it, so the router does create what it names — that half is
clean, the description of it was not.

**The assertion is narrow, as ordered: a `To:` header, not "anything in the
folder".** Measured before writing it — **25 files in `_needs_review/`, zero
carrying a `To:` header.** They are July session-handoff text, status files and a
search script. A control firing on those would cry wolf and be switched off
inside a week.

**It is green on the live folder today**, which is the state Architecture
predicted.

## (b) TRAY DEPTH AND THE OLDEST LETTER — FLAG ONLY, NEVER A GATE

    desk            open  oldest       age
    architecture       8  2026-09-08   1 day
    audit              7  2026-09-08   1 day
    build             18  2026-09-07   2 days
    design             9  2026-09-08   1 day
    owner              1  2026-09-08   1 day
    research           4  2026-09-05   4 days

    OLDEST LETTER IN THE SYSTEM: 2026-09-05, 4 days, research desk

Age comes from the letter's own `Date:` header where it has one and from the
filesystem where it does not, **and the report says which it used** — a date the
control guessed would be worse than no date at all.

## RULE 12 — BOTH ADDITIONS GO RED ON DEMAND

`--self-test` now plants **13** defects and catches **13**, exiting 1 as the
convention requires. Three of them are new:

    bounced-to-nobody.md   a memo to a desk that does not exist, in the bounce
                           folder, exactly as the router leaves it -> RED
    old-handoff.txt        a status file with no address in the same folder
                           -> MUST STAY QUIET, and does
    tray depth             asserted against a tray this file wrote, so the count
                           and the age have a known answer. A report that
                           silently returns nothing is the same defect as a
                           check that cannot fail.

Control runtime: **0.16s**, unchanged in practice.

## THE CONTROL IS CURRENTLY RED, AND IT WAS RED BEFORE I TOUCHED IT

**65 findings, none of them from my two additions** — I checked, the bounce
assertion contributes zero and the depth report contributes zero.

All 65 are about `correspondence/answered/`: memos filed there that carry **no
`ANSWERS:` line**, and several that still say **`Status: Open`**. Every one of
them is dated 2026-09-08 — after the last green sweep of 2026-09-07 22:42, which
is why the receipt does not show it.

**That is other desks' filing and I am not touching it.** An answered drawer
holding open questions is exactly what the control exists to say, and it is
saying it. Flagged here so it is visible rather than discovered in a sweep.

My own two answered memos are clean and neither appears in the 65.

**Nothing committed.**
