# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: AUTOMATION FIRST — prove one desk can be woken, then build the brakes. Your existing queue waits.
Status:  Answered
**New priority and it displaces your list. Getting the desks talking to each other
without me in the middle comes first. Your current queue is not cancelled — it
waits behind this.**

**The gap is small.** The watcher already files every letter. The boot prompts are
written. It is confirmed against Anthropic's own documentation that a headless
`claude -p` run bills against my subscription, not a separate account. **What is
missing is that a letter landing in a tray rings no bell.**

**Do not reach for Temporal or the Agent SDK.** Not yet, and not without my word.

---

## 1. PROVE ONE DESK CAN BE WOKEN. NOTHING ELSE IN THIS STEP.

**Start a desk headless, have it read ONE letter, write ONE reply, and exit.**
Watched by me, on a letter that does not matter.

**That is the whole experiment.** Not a loop, not a schedule, not two desks. **It
either works on this machine or it visibly does not**, and everything after it is
wasted until that is known.

**Report what it actually cost** — `--output-format json` returns usage and a
per-model breakdown, described by Anthropic as a client-side estimate. **Give me
the token counts, and mark the dollar figure as the estimate it is.**

**And confirm which allowance it drew from.** That is the claim the whole design
rests on and it has been read but never observed.

---

## 2. BUILD THE BRAKES BEFORE THE ENGINE

**These are my decided rules, not proposals. Architecture is designing against
them in parallel; you build what it specifies. If a rule cannot be enforced by a
program, say so rather than trusting a desk to obey it** — today's own research
measured instruction decay: the rule was present, unchanged, read at startup, and
long-running sessions stopped acting on it anyway.

**Round counting.** The watcher stamps a round number on every letter. First filing
is round one; every return to a tray it has already been in raises it. **A desk
cannot change its own count.**

**Round three goes to my tray**, `correspondence/open/owner/`, with the history
attached, and is never filed to a desk.

**A letter whose From and To are the same desk is refused, never filed.**

**One wake per desk at a time.** A desk already running does not get a second copy.

**A daily ceiling on wakes across all desks.** Over it, stop waking anything and
tell me. **A published case ran four hours and fifty million tokens because
nothing had a ceiling.**

**A wake log** — written when a wake starts and when it ends. **A wake that never
logs an end stops all further wakes.**

---

## 3. THE THINGS THAT MAKE THE WAKE POSSIBLE

**A signal the waker can read to know a tray is not empty.** Cheap, no model.

**Prove the API key guard holds on a headless run.** It is live now and it has only
ever been tripped by hand. **An unattended run is the case it exists for and the
case it has never faced.**

**Whole-file writes on anything another desk may touch are out.** Targeted edits
only. A published case had a whole-file write silently discard a change made
between read and write and report success; a targeted edit failed loudly instead.

---

## 4. WHAT A WOKEN DESK MAY NOT DO

**Read, write memos, edit what it owns. Nothing else.**

**No deploy, no commit, no push, no delete, no spending, no credentials.** Rules 2
and 23 are unchanged and none of this loosens them. **Not being told no is not
being told yes.**

---

## 5. THEN, AND ONLY THEN, YOUR EXISTING QUEUE

    the card mark build
    the build stamp at build_deploy.py:842 — explicit local time, fail loudly
    the typed-list sweep — report, do not fix
    the third clean sweep receipt, uncontaminated by concurrent work
    the red API-key case — prove the impossibility or build it
    the six old letters — DONE / SUPERSEDED / NEVER STARTED, one word each
    the authorised small import
    the sweep ordering fault
    _verify_placer_candidates.py — NOT PERFORMED, not a bare exception
    claim inject_engine.py in OWNERS.md

**B2 and family_id stay blocked** until Architecture rules what family the RAPTOR
takes. You were right not to guess it.

**The Stop hook is still blocked on me** — your permission layer refuses that file
even for a backup, which is a tool restriction and not a missing authorisation.
**Ask for it when you next need it and I will answer the prompt.**

---

## ONE THING THAT IS NOT A JOB

The previous session filed **twelve timestamped updates** to `docs/handoff_archive/`
in one day, one per piece of work. **That record is the only reason last night
could be reconstructed at all, and a day page written at the end of a day tells
nobody anything while the day is happening.** Keep filing them.

---

ANSWERS:

**SUPERSEDED**, by `2026-09-10_memo_ruling-four-and-it-freezes-the-other-two-are-superseded.md`.

**What is dead in this letter:** *"Round three goes to my tray... and is never
filed to a desk."* The number is **FOUR**, and the behaviour is **FREEZE**, not
forward. Your ruling names both, and names the second as the part that matters:
*"if the desks carry on working it while it sits with me, nothing stopped."*

**What is still live and where it now lives**, recorded here so answering this
letter does not quietly retire it:

    the priority itself - automation before the queue      still stands
    section 1, prove ONE desk can be woken                 restated in the ruling
    section 3, what makes the wake possible                unbuilt, still ordered
    section 4, what a woken desk may not do                unchanged, and rules
                                                           2 and 23 unchanged with it
    section 5, the queue behind it                         unchanged

**And the card is now built against `claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`,
not against this letter or any other memo** - your instruction, in
`2026-09-10_memo_the-design-document-is-the-authority-not-my-memos.md`.

**Nothing was built against the round-three rule.** `scripts/wake_desk.py` carries
no counter, no ceiling and no lock, deliberately, so there is nothing to unpick.
