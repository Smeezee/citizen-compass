# Memo

To:      Architecture
From:    Owner
Date:    2026-09-11
Subject: Three jobs — a new intake tray, the rotations recommendation, and the Perplexity export design
Status:  Closed
**None of these delays Build. Step A is approved and running on its own track.**

---

## 1. A NEW INTAKE TRAY — `correspondence/open/adjutant/`

**RULED. Requests from me enter through that tray. The owner tray becomes
OUTBOUND ONLY** — the system writes answers and decision requests there for me to
read, and nothing of mine enters through it.

**Why: one folder cannot be both directions once mail moves on its own.** Intake is
me to the machine; the owner tray is the machine to me. A folder that is both is a
folder where nobody can tell what is waiting for whom, and that is the exact
confusion this whole system is being built to remove.

**Specify it. Do not build it — that is Build's, after step A.**

**AND THE WARNING THAT COMES WITH IT, WHICH IS YOUR OWN RECORD.** A desk is four
things: the procedure, the tray, the router and the checker. **When the design desk
was added on 2026-09-08 the checker, the README and the tray all learned and the
ROUTER did not**, which would have refused every letter addressed to it. **Name all
four in the spec or this repeats.**

**And say plainly whether `memoTrays` being a typed map in `memo.go` now collides
with the standing ruling that the desk list is derived from the tray folders on
disk.** If it does, that is a finding and it is older than this letter.

---

## 2. THE ROTATIONS RECOMMENDATION — SHORT, PLAIN, AND IT IS A RECOMMENDATION

**Two things I have to decide and I will not decide either one silently.**

    how many FAILED CORRECTION ROUNDS before a job comes to me
    whether my FIRST FILING of a job spends one of the four deliveries

**Give me a recommendation in plain language with the reason, not a menu.** You
already showed me the arithmetic; I do not need it again. **I need your answer and
what it costs.**

**Short.** This is one of a dozen things in front of me tonight.

---

## 3. THE CURATED PERPLEXITY EXPORT — DESIGN ONLY

**Separate architecture work. It does not touch the automation queue and it must not
delay it.**

**Settled and not reopening:** the Perplexity sandbox account gets no access to the
live Citizen Compass tree, ever. Not read, not traverse. **A curated one-way export
folder instead.** `C:\Users\Public` is not to be used — its permissions are inherited
and world-readable; the export needs a dedicated location with explicitly controlled
permissions.

**Design it. Do not build it.** What I want answered:

**What crosses the boundary, and how that set is DERIVED rather than maintained.** A
checklist of what is safe to copy is a typed list, and the next new secret file will
not be on it. **Name the documents by exact filename, or find something better — but
say which, and say why it cannot rot.**

**What happens when a copied document changes.** One-way is easy; one-way and current
is the part people get wrong.

**And the boundary itself** — the folder's permissions, who writes it, who reads it,
and what happens if the account name changes, because `PerplexitySandbox` is a
vendor's internal detail and not a stable identity.

**The background, all on disk:** Build's ACL audit of 2026-09-10, filed 19:24:50 in
`docs/handoff_archive/`, and
`claude/ECHO_what-actually-stops-a-runaway-2026-09-10.md`.

---

## WHAT NONE OF THIS AUTHORISES

No database work, no deployment, no unrestricted execution, no automation activated.
**The Looking Project is excluded entirely.**

---

ANSWERS:

**Architecture, 2026-09-12. CLOSED AS A SUPERSEDED DUPLICATE. All three jobs in this
letter were answered on 2026-09-11 and the answers are in the owner tray under
`2026-09-10_memo_architecture_intake-tray-rotations-recommendation-and-the-export-design.md`
— the same letter, under the date the watcher stamped on the copy that was replied to.**

**READ THAT FILE, NOT THIS ONE.** This copy exists only because the date rule was adopted
mid-exchange and this letter had already arrived under two different dates.

**Where each of the three landed, so nobody re-does one:**

    1  the adjutant tray     claude/SPEC_the-adjutant-tray-2026-09-11.md.
                             All four things named — procedure, tray, router,
                             checker — plus a FIFTH you did not ask for and
                             need: the router is a compiled binary, so a
                             rebuild and swap sits inside the third. Nothing
                             is done until the RUNNING watcher files a memo
                             addressed To: Adjutant.
    1b memoTrays vs the      ASKED AND ANSWERED: YES, it collides, and it is
       derived desk list     older than your letter. memo.go types the list;
                             scripts/wake_desk.py derives it from the trays and
                             cites the 2026-09-10 ruling. The refusal you value
                             SURVIVES the fix — a memo is refused because the
                             TRAY does not exist, which is the same refusal from
                             a better source. It rides with the adjutant tray:
                             same file, same rebuild, same swap.
    2  the rotations         Answered, and YOU RULED IT 2026-09-11. Two failed
                             correction rounds is the trigger; your first filing
                             spends no delivery; the four becomes a runaway
                             backstop whose firing is itself a signal.
    3  the curated export    claude/DESIGN_the-curated-export-2026-09-11.md.
                             The boundary inverted from a content refusal to an
                             allow-list in your control folder, because a refusal
                             is a deny-list and permits everything it was not
                             taught. §5F rules drop-on-change.

## AND I AM REVERSING MY OWN DECISION TO LEAVE THIS SITTING HERE

**The state document records this copy as DELIBERATELY left open**, on the grounds that
filing a second answer under a mismatched date would be worse than a stale copy in the
tray. **That weighed both costs in the archive's terms and they are not the same kind of
cost.**

    a duplicate in answered/   costs nothing. The archive is a RECORD.
    a stale letter in open/    costs a read at every boot, forever. The tray
                               is a WORK QUEUE, and an Open letter in it is a
                               claim that something is owed.

**I re-verified all three of these jobs today before concluding they were done. That is
the price, and it recurs.** So: closed here, with the mismatch declared rather than
avoided. **Two files will sit in `answered/` for one exchange — this one and the
2026-09-10 copy. That is the whole cost and it is paid once.**

**The rule that generalises: a stale copy is only cheap in a folder nobody works.**

*C1, 2026-09-12.*
