# SPEC — AN ANSWER GOES BACK TO THE SENDER. Executable by Build. NOT YET ORDERED.

    from    C1, architecture
    date    2026-09-10
    why     Sleven, 2026-09-10: *"every answer you have written me today went
            into a folder nobody reads."* Verified against
            `watcher-go/memo.go` — his reading of the code is exact.
    scope   the routing of an ANSWERED memo, and nothing else. No new folder,
            no second copy, no change to how an open memo is routed.
    order   NOT ORDERED. Build is mid-brakes and this does not jump it. His
            instruction: specify it, do not build it.
    ON DISK because a desk that can only see files must be able to read
            anything it executes against.

---

## 1. THE DEFECT, FROM THE SOURCE

`watcher-go/memo.go`, `memoDestination`, lines 165-170:

    answered := m.Status == "answered" || m.Status == "closed" || m.Status == "done"
    if answered {
        return filepath.Join(correspondenceDir, "answered"), ..., true
    }
    tray, known := memoTrays[m.To]

**The answered test runs before `m.To` is read.** Every answer, from every desk,
to every recipient, lands in `correspondence/answered/`.

**A desk cannot reply to a desk. It can only reply to an archive.**

## 2. IT IS NOT ONLY HIM — HIS QUESTION 2, AND HE GUESSED RIGHT

**Every desk. The branch does not know who anybody is when it fires.**

    Build answers Architecture      -> answered/. Architecture never sees it.
    Audit answers Build             -> answered/. Build never sees it.
    Architecture answers Owner      -> answered/. Owner never sees it.

**New letters arrive normally; ANSWERS vanish.** So every tray fills with fresh
questions and never with replies, and the system reads as one-directional to
everybody in it. **That is why it feels dead.**

## 3. THE ANSWER ROUTES ON `From:`, NOT ON `To:` — AND THIS IS THE PART HIS LETTER GETS WRONG

**His proposed shape is "an answered memo addressed `To: Owner` lands in my tray."
There is no such memo.**

A letter he wrote carries `To: Architecture, From: Owner`. **Answering it does not
change the headers** — the ANSWERS block is appended and the status flips. Its `To:`
still says Architecture.

**Routing an answered memo on `To:` would send it back to the desk that just
answered it.**

    THE RULE:  an OPEN memo goes to the tray of its To:
               an ANSWERED memo goes to the tray of its From:

An answer travels back up the line it came down. **That is the whole fix and it is
one lookup.**

## 4. `From:` MUST BE VALIDATED, AND TODAY IT IS NOT

`readMemo`, lines 130-135:

    To:   strings.ToLower(strings.TrimSpace(to[1]))     lowercased
    From: strings.TrimSpace(from[1])                    NOT lowercased,
                                                        NOT looked up

**`To:` is checked against `memoTrays` and refused to `_needs_review/` when
unknown. `From:` is free text.** It has never mattered because nothing routed on
it. It matters now.

**Real values in the live archive today include `From: Research (CIC)`.** That
matches no tray.

    on an ANSWERED memo, From: is lowercased, trimmed and looked up in
    memoTrays, exactly as To: is
    unknown From: on an answered memo  ->  _needs_review/, with the reason
    an OPEN memo's From: is not validated and does not need to be

**Validate it only where it is load-bearing.** Refusing an open letter over an odd
`From:` would break working traffic for nothing.

**AND THE DESKS MUST WRITE BARE DESK NAMES.** `From: Research (CIC)` becomes
`From: Research`; the CIC identity belongs in the signature line, where it already
is. One-time correction, and rule 19 says the alternative is refusing it, not
guessing at it.

**Echo's point stands and is not solved by this:** `From:` is a claim, not
authentication. A desk can type any name. That is the same weakness `To:` already
has, it is not made worse, and the fix for it is the service knowing what it
launched — not a header rule.

## 5. THE SUPERSEDE BUG THIS WOULD INTRODUCE — HIS QUESTION 1, AND THE ANSWER IS YES

**`clearOpenCopy` would delete the answer it just filed. Nondeterministically.**

`classifyMemo` writes the answered file first, then calls `clearOpenCopy(base)`,
which loops **every** tray looking for that basename and moves the first hit to
`_to_delete/`:

    for _, tray := range memoTrays {
        p := filepath.Join(correspondenceDir, "open", tray, base)
        ...
    }

**Today that is safe because the answered file goes to `answered/`, which the loop
never scans.** Under this change the answer lands in `open/<from>/` — **which is one
of the trays the loop scans.**

**And Go randomises map iteration order.** So on some runs it moves the stale copy
from the sender's original tray, and on others it moves the answer that was filed
two lines earlier. **A defect that works most of the time is worse than one that
never does.**

    REQUIRED: clearOpenCopy takes the destination it must NOT touch, and skips it.

**The gate also widens.** Line 266 runs the supersede only when
`dir == correspondence/answered`. It must run whenever the memo is answered,
whatever tray it landed in — otherwise the stale open copy stays in the original
tray and the same letter reads as waiting in one place and answered in another,
which is the exact defect `clearOpenCopy` was written for on 2026-08-30.

## 6. NO SECOND COPY — HIS QUESTION 3

**He is right to be wary and the answer is that there is no copy.**

**Do not file the answer in the tray AND in the archive.** The tray copy is the one
that gets edited — that is what a tray is for — and the archive copy rots beside it.
**This repository has been bitten by two-of-everything three times; `memo.go`'s own
header says so and `OWNERS.md` exists because of it.**

### THE THREE STATUSES ALREADY IN THE CODE DO THE WHOLE JOB

The answered test already recognises three words and treats them identically.
**Separate them:**

    Status: Open        ->  open/<To:>        a question travelling out
    Status: Answered    ->  open/<From:>      the answer travelling back
    Status: Closed      ->  answered/         the thread is finished
    Status: Done        ->  answered/         same as Closed

**One copy exists at every moment.** It moves; it is never duplicated.

**And `answered/` starts meaning what its name says** — threads that are finished,
rather than threads somebody replied to once. **Closing becomes a real act by a real
desk instead of a side effect of filing**, which is also what makes the tray
trustworthy: a letter in a tray is genuinely outstanding.

### THE ONE EDGE CASE

**`From:` equal to `To:` on an answered memo** — a desk writing to itself — has
nobody to send it back to. File it to `answered/` and say so in the note.

## 7. WHAT THIS DOES NOT CHANGE

**No new folder. No new status word. No change to open-memo routing. No change to
`_needs_review/`. No change to the desk list.**

**And it does not touch the nine letters already in `answered/`.** They are where
they are and moving them would be a second guess about what each one meant. **Any
that still need an answer, he re-opens by hand** — his call, not a migration.

## 8. HOW IT IS PROVEN

**The existing test `TestAnAnsweredMemoLeavesTheOpenTray` is the cautionary tale for
this whole change** and `memo.go` says so at line 202: it asserted the RETURNED PATH
and never touched the filesystem, so it passed while the same memo existed twice.

**Every assertion below touches the filesystem.**

    an answered memo lands in the FROM desk's tray, not answered/
    the stale open copy leaves the TO desk's tray
    THE ANSWER IS STILL THERE AFTERWARDS — run it repeatedly, because the
      failure it guards is a randomised map order and a single green run
      proves nothing
    Status: Closed lands in answered/ and the tray copy is gone
    an answered memo with an unknown From: goes to _needs_review/ with the
      reason, and NOTHING is moved out of any tray
    From: equal to To: lands in answered/
    an OPEN memo with an odd From: still routes normally on To:

*C1, 2026-09-10. Specified, not ordered.*

---

## 9. A RENAMED ANSWER IS A PROTOCOL ERROR — HIS REQUIREMENT, 2026-09-11. NOT AUTHORISED.

    order   REQUIREMENT ONLY. Behind containment and the brakes. It does not
            jump them, and this section does not authorise a code change.

**Sections 1-8 are BUILT and live. This section is not.**

### WHAT HAPPENS TODAY

`clearOpenCopy` matches on the basename. **A reply that comes back under a different
name matches nothing, and the supersede quietly does nothing.** It is not an error to
the system — it is a file that happened not to match.

**Silent.** Same shape as the fifty-five seconds Build found where routing failed and
the watcher logged nothing: the failure is real, recovery is not attempted, nobody is
told.

### IT HAS ALREADY HAPPENED, ON A LIVE LETTER

    open/architecture/   2026-09-11_memo_architecture_intake-tray-...md   the question
    open/owner/          2026-09-10_memo_architecture_intake-tray-...md   the answer

**Same letter, two trays, two dates, no supersede.** The answer routing worked
perfectly; only the supersede missed.

### THE CAUSE, AND HIS RULE THAT REMOVES IT

**A desk typed the date.** One desk runs on UTC, the machine runs `America/Chicago`,
and after 19:00 local those are different days.

**HIS STANDING RULE, 2026-09-11, EFFECTIVE IMMEDIATELY AND NOT WAITING ON THIS
SECTION:**

    A NEW ORIGINAL LETTER carries NO manually added date. The watcher stamps it.
    A REPLY preserves the filename it received, EXACTLY, character for character.

**The rule alone fixes the supersede, with no code change and no clock change** —
both copies carry the same date, right or wrong, and the basenames match. **That
matters because the obvious alternative was changing the watcher's timezone, which
collides with the `America/Chicago` ruling in the brakes spec.**

**And the code cannot do it for us.** From `memo.go`:

    if !reLeadingDate.MatchString(base) {
        base = time.Now().Format("2006-01-02") + "_" + base
    }

**The watcher fills a GAP. It never corrects a wrong date.** A name that arrives
stamped keeps that stamp forever, which is why the rule is *do not stamp it* rather
than *stamp it correctly*.

### THE REQUIREMENT

**When a memo is answered and the supersede finds no open copy anywhere, that is
reported, not ignored.** It is either a renamed reply or an answer to a letter that
was never open — and both are worth a line.

**Not a refusal.** The answer is already correctly filed and it must stay filed;
refusing it would lose the reply to protect a housekeeping step. **Report and carry
on.**

### AND THE CHECK, WHICH DOES NOT WAIT FOR THE CODE

**A rule a desk has to remember is a rule with one reader.** `_verify_correspondence.py`
asserts that no filed memo carries two dates. **Both shapes are real and both are on
disk today:**

    2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md
    2026-09-08_20260908_memo_audit-to-design_ten-pairs-for-angles-md.md

**`reLeadingDate` only recognises the dashed form**, so a desk typing `20260911_` gets
a second date stapled on and the regex never sees it. **A check that looked only for
the dashed-dashed shape would miss half of it.**

**Proved against real archive data rather than a planted case.**

*C1, 2026-09-11. Section 9 added: requirement only.*
