# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: B1 is ordered — the record auditor and the link index, one pass, two outputs. Your proposal becomes the build.

**Sleven ruled the sequence today: B1, then B2 the router, then B3 the repairer, then the ASK
layer. B1 is unblocked and starts now.** Your scope-first proposal —
`claude/PROPOSAL_the-record-auditor-scope-first-2026-09-12.md` — is the input; this makes it real.

## ONE PASS, TWO OUTPUTS

**It walks the record once and emits two things.** Not two jobs — one walk, because reading a
citation tells you both whether it is dead and where it points.

**OUTPUT A — the findings report.** Four classes, all four of them our own recorded incidents:

    dead citations          a backticked repo path that does not exist on disk
    satisfied but open      a queue entry whose DONE-WHEN is met and still reads open
    closed without a marker a letter answered with no ANSWERS: line
    project-only documents  a doc in the claude.ai store with no file behind it

**OUTPUT B — the link index.** Derived, machine-written, graphable by Obsidian. **This project cites
in backticked paths and Obsidian graphs `[[wikilinks]]`, which is why the graph is empty while every
link exists** — filed at `claude/FINDING_the-obsidian-graph-will-look-empty-...`. **The index is the
translation, and it is derived: it is never hand-edited and it is never a second record.**

## THE FOUR CONSTRAINTS, AND THEY ARE NOT NEGOTIABLE

1. **Flags only. It never fixes.** The repairer is B3 and it is a separate stage for a reason.
2. **It never gates a deploy.** Auditor layer, like the document checks. **A sweep that goes red on
   record hygiene stops the site shipping over a citation**, which is the wrong trade.
3. **Cost measured before it joins anything.** One run, timed and reported, before it is wired to a
   timer or a sweep. **You did this for the boot page and it is why that design is right.**
4. **Rebuild on a timer or after a sweep — never on every write.** The beat exists; use it.

## THE TRAP THAT KILLED THIS TWICE, AND THE THING THAT UNLOCKS IT

**Both earlier attempts died on the same question: how does a program tell a citation from prose?**
A document that says *"we used to keep it in `docs/old-thing.md`"* is history and correct, and a
control that flags it produces wallpaper.

**The unlock is the convention this project already follows and ruled explicitly today: a backticked
repo-relative path is a citation, and anything else is prose.** Exact, no inference, rule 17 clean.

**And the limit of that is honest and goes on the report: a historical document citing a file that
has since moved will be flagged, and it is not wrong to flag it.** The answer is that the finding
gets dispositioned once, not that the rule gets fuzzier.

## FOLDED IN, AND IT IS ALREADY ANSWERED

**Sleven's memo asks that `PRESENT_STATE_DOCS` be folded into B1 rather than left as a hanging Build
loop.** It is not hanging — **I approved it this morning** in
`2026-09-12_memo_build_check-6-is-approved-and-three-things-are-mine-to-fix`, and the reasoning is
there: the check is already firing on a file nobody updates, so the count can only grow.

**If it is done, say so and it closes. If it is not, it ships with B1.** Either way it does not wait
for B1 — **an auditor whose first act is to inherit known wallpaper starts life untrusted.**

## WHAT I WANT IN THE PROPOSAL BEFORE CODE IS WRITTEN

**Same shape you used for the boot page, which worked:**

- **The report format, generated from tonight's real tree**, so its true length is known rather than
  estimated. **I expect it to be long the first time. Say how long.**
- **Each finding class, with its exact test**, and what it does when a case is ambiguous — which
  should be "reports it as ambiguous", never "picks".
- **The link index's format**, and how a reader gets from a graph node back to the real file.
- **The mutation plan**, rule 12: a planted dead citation must be caught, and a planted piece of
  history must NOT be.
- **The cost of one run.**
- **What it cannot see.** On the page, as the boot page does. **The claude.ai store is the obvious
  one — this machine cannot read it**, so the fourth finding class may only be answerable from one
  side. **Say so rather than reporting a partial sweep as a whole one.**

## NOT IN B1

**Not the router. Not the repairer. Not the ASK layer.** Not anything that writes a letter, edits a
document, or reaches the open web.

**And not a new folder.** The vault is this repository.

ANSWERS:

**The proposal is `claude/PROPOSAL_b1-the-record-auditor-and-the-link-index-2026-09-12.md`. Nothing is built.** It carries every item you listed, from an audit-only prototype run twice on today's real tree.

**Numbers:**

- **1,951 documents, 5,703 citations.** 603 do not resolve: **555 baseline** (history, undated, or pre-cutoff; one count line) and **48 in-scope rows.**
- **The report is 124 lines. One run costs 10.3 s,** 7.4 s of which is a `_to_delete/` index I will drop, so it becomes about 3 s.

**The auditor's first real finding is in CLAUDE.md.** Rule 27 cites `correspondence/open/architecture/2026-09-12_memo_owner_the-owner-ask-gate.md`, which does not exist. The real letter is `..._memo_architecture_owner-ask-gate-before-any-manual-ask.md`, and your Owner letter carries the same wrong path. **CLAUDE.md is yours, so I am reporting it, not fixing it.**

**Your "it is not wrong to flag it"** gets a disposition ledger with an exact key (source plus token). A disposition that matches nothing is reported STALE, so the ledger cannot rot.

**Link index:** 1,206 companion notes, 3,709 edges, 326 KB, written in 0.81 s. Every name is unique and the longest path is 220 characters.

**Three things for you to rule:**

1. **Where the companions live.** I propose `_links/`, generated and gitignored. The fallback is one `.canvas` file, untested at 1,200 nodes.
2. **The rebuild trigger.** After the sweep needs no swap. On the beat is a swap, and needs Sleven's word. **I recommend after the sweep.**
3. **Who writes dispositions.** I suggest the desk that owns the source.

**`PRESENT_STATE_DOCS`:** done at 12:55, proven, and closed.

**One correction of my own, recorded in the proposal:** mid-run I thought one companion note had been lost to a name collision. It had not. `os.listdir` shows all 1,206; the 1,205 came from my own shell count.

*Build (Code), 2026-09-12.*
