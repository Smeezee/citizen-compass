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

**Architecture, 2026-09-11.**

    claude/SPEC_the-adjutant-tray-2026-09-11.md
    claude/DESIGN_the-curated-export-2026-09-11.md

**Both on disk. Both specified, neither ordered. Build is untouched.**

---

# 2. THE ROTATIONS RECOMMENDATION — ANSWERED FIRST BECAUSE IT IS THE ONE YOU CAN DECIDE TONIGHT

## TWO FAILED CORRECTION ROUNDS.

**Reason: one round is not a pattern.** The first correction genuinely often works —
that is what a correction is for. **Two is the smallest number that tells "the fix
did not work" apart from "the fix keeps not working",** and the second one is the
thing you actually need to see.

**Three means you hear about a problem on its third failure**, by which point two
desks have spent real time going round on it.

**THE COST: you will occasionally be handed a job that a third round would have
solved.** That costs you a glance and a "go again". **The reverse mistake costs a
morning.**

## NO — YOUR FIRST FILING DOES NOT SPEND A DELIVERY.

**Reason: the four exists to catch desks going round in circles with each other. You
handing work in is not a lap.**

**And it makes your own rule consistent.** The design already says a job that goes to
you and comes back does not spend a punch. **The owner edge should not spend one in
either direction** — it is one rule instead of one rule and an exception.

**THE COST: a job gets one more legal hop before the backstop fires.** That is not a
loss; it is exactly what the healthy route needs. Owner → Architecture → Build →
Audit → Architecture was landing on four and freezing a job that had passed every
check. **With your filing exempt it lands on three and closes.**

---

# 1. THE ADJUTANT TRAY

**Specified. All four things named, and there is a fifth.**

    1  PROCEDURE   correspondence/README.md + "Session roles" in CURRENT-STATE
    2  TRAY        correspondence/open/adjutant/ with a .keep
    3  ROUTER      memoTrays in watcher-go/memo.go
    4  CHECKER     checks/_verify_correspondence.py
                   and watcher-go/memo_desks_match_procedure_test.go
    5  BUILD AND SWAP   the router is a COMPILED BINARY

**Five is the one that would bite.** On 2026-09-08 the router simply did not learn.
**Today the router is an exe, so "the router learned" means the source changed AND it
was rebuilt AND the running watcher was swapped.** A desk added to the source and
never swapped in is the same failure with one more step — **and it would look more
finished than the last one, because the code would be right.**

**The pass condition is a memo addressed `To: Adjutant` actually landing in the tray,
filed by the running watcher.** Not a green test.

## YOUR COLLISION QUESTION — YES, AND IT IS OLDER THAN YOUR LETTER

    memo.go            memoTrays is a TYPED MAP
    wake_desk.py       desks() is DERIVED from the trays on disk, and its
                       comment quotes your 2026-09-10 ruling

**The ruling was made, applied to the launcher, and the watcher was never changed.**
Two programs, two desk lists. **The same shape as `protected_folders.txt`: a rule with
one reader.**

**The derived ruling stands and the watcher is the one that is wrong.**

**And the watcher's reason for a typed list survives the change**, which is why this is
cheap: it wanted a typed list so a memo to a nonexistent desk is refused. **Refusal
comes from the tray not existing, not from the name not being in a list.** Same
refusal, better source.

**The risk, stated: a stray or mistyped folder under `open/` becomes a desk.** The
guard is the checker that already asserts the tray set matches the procedure. **Derive
the behaviour, check the set.**

**RIDE IT WITH THE ADJUTANT CHANGE.** Same file, same rebuild, same swap. **Adding
the adjutant to a typed list that is about to be deleted is work that exists only to
be undone.**

## AND ONE THING I WILL NOT PRETEND

**Outbound-only cannot be enforced.** You have a keyboard; nothing stops a file landing
in `open/owner/`. **What can be done is detection**, and it is one assertion: an OPEN
memo in `open/owner/` whose `From:` is Owner is misfiled.

**Only OPEN ones.** Once the answer-routing fix lands, an ANSWERED memo `From: Owner`
belongs in `open/owner/` — that is your answer coming back. **A check that flagged
those would go red on correct behaviour and be switched off within a week.**

---

# 3. THE EXPORT

## FIRST — YOU CAUGHT A DEFECT IN BUILD'S RECOMMENDATION AND ITS OWN AUDIT PROVES IT

Build's §8 recommended the export folder and named `C:\Users\Public\cc-share\`.
**Build's own §2, six pages earlier, records that `C:\Users` carries
`Everyone:(RX)` and `BUILTIN\Users:(RX)` with inheritable read.**

**A folder under Public inherits world-readable.** Right shape, wrong location, and
the evidence against it was in the same document. **Sent to Build.**

## WHAT CROSSES — A MARKER IN THE DOCUMENT, NOT A LIST

**Opt-in. Absence excludes. Un-marking removes it on the next run.**

**Your filename option is not unsafe and I want to be accurate about that** — an
allow-list of filenames is also fail-closed, because a new secret file is not on it.
**The two rot differently.** A filename list rots by omission: something gets renamed
and silently stops crossing, or a useful new document never gets added. **A marker
puts the decision at the moment of writing, with the person who knows.**

**Why it cannot rot in the direction that matters: absence excludes, so forgetting can
never leak.** It CAN rot by somebody forgetting to mark something useful — **and that
rot is visible, because the export carries a manifest and the person who wanted the
document notices it missing. Rot a person notices is not the dangerous kind.**

**And a marker alone is not enough, because a marker lives in a file a desk can
edit.** Two more gates, and a leak needs all three to fail:

    SOURCE SCOPE   only docs/ and claude/ are considered at all
    EXTENSION      .md only. No executables — which is what kills the rule 7
                   problem Build raised: there is nothing in the export to run
    CONTENT        a credential shape is refused and reported even when marked.
                   That is the case Build's audit explicitly could not cover —
                   a secret in an unremarkable filename.

## ONE-WAY AND CURRENT — REGENERATE WHOLE, NEVER INCREMENTAL

**This is the whole answer to the part you said people get wrong.**

Build a complete new export beside the live one, write the manifest, then swap — old
one moved aside with a timestamp, never deleted.

**Incremental cannot remove a document whose marker was taken away.** The stale copy
just sits there, exported, forever. **Regenerating whole is what makes un-marking
work.**

**The manifest carries source path, size, mtime, hash, and generated-at**, or nobody
can tell a current export from a three-week-old one. **And a failed run writes a
failure marker** — silence is the one outcome not allowed, because a stale export that
looks fine is this project's recurring defect in a new hat.

## THE BOUNDARY

    C:\cc-export\        drive root, INHERITANCE DISABLED, explicit ACL

**Disabling inheritance is what makes it safe; the location then answers two more
questions.** Not under Public — section 0. Not under `C:\Users\david\` — the sandbox
has no traverse there and Build's §3 could not confirm whether the bypass privilege
makes that moot; **a drive-root folder does not raise the question at all.** Not
inside the repository — a woken desk's `--add-dir` scope would reach it.

## THE ACCOUNT NAME — GRANT TO A GROUP, NOT THE ACCOUNT

**This is the direct answer and it is the strongest part of the design.**

Create a local group, put the sandbox account in it, grant the GROUP read.

**If the vendor renames the account, recreates it with a new SID, or adds a second
one, the group membership changes and the folder's ACL is never touched.**

**And revocation becomes one act: empty the group.** No `icacls` on a tree, no chance
of stripping the wrong entry.

**Build's audit already shows the name is not what people think** — the request said
`perplexitysandbox`, the real principal is `PerplexitySandbox`.

## WHAT I DELIBERATELY DID NOT WRITE

**The exact `icacls` and `net localgroup` commands.** They are a permissions change,
they are yours under hard rule 6, and writing them into a design document makes them
look approved. **Nothing here has been built, run or changed. No group exists. No
folder exists.**

## AND ONE THING TO SETTLE BEFORE ANY OF IT

**What the export is FOR.** Nothing above needs answering until that is decided,
because it decides whether `docs/` and `claude/` are the right source scope at all.

**A design that works for "let it read the doctrine" is a different design from one
that works for "let it read the ship data"** — the second breaks the markdown-only
rule immediately. **Not guessed at.**

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.**
