# SPEC — THE ADJUTANT TRAY. Executable by Build. NOT YET ORDERED.

    from    C1, architecture
    date    2026-09-11
    ruled   Sleven, 2026-09-11: requests from him enter through
            correspondence/open/adjutant/. THE OWNER TRAY BECOMES OUTBOUND ONLY.
    order   NOT ORDERED. After step A. It does not delay Build.
    ON DISK because a desk that can only see files must be able to read anything
            it executes against.

---

## 1. THE RULE

    correspondence/open/adjutant/    INBOUND.  Him to the machine.
    correspondence/open/owner/       OUTBOUND. The machine to him.

**His reason, and it is the right one: one folder cannot be both directions once
mail moves on its own.** A folder that is both is a folder where nobody can tell what
is waiting for whom.

**The Adjutant is the seventh desk.** It is addressed `To: Adjutant` when he does not
know or does not care which desk should take something; its job is to read, decide,
and write a memo to the desk that should have it. **A letter of his addressed to a
named desk still goes to that desk directly and does not pass through here.**

**This is consistent with what the Adjutant already does** — design sections 10 and
18 have it reading the heartbeat and rendering the roll call at the start of a
conversation. Receiving mail is the same desk, not a new one.

---

## 2. A DESK IS FOUR THINGS — HIS WARNING, AND IT IS THE PROJECT'S OWN RECORD

`watcher-go/memo.go` records both failures, one day apart:

> *"audit: the router learned first, and the CHECKER stayed silent… design: the
> checker, the README and the tray all learned first, and THE ROUTER did not."*

> *"A desk is not a name in a list; it is four things — the procedure, the tray, the
> router and the checker — and updating any three of them leaves something that looks
> finished."*

**All four, named:**

    1  THE PROCEDURE   correspondence/README.md
                       and the "Session roles" section of docs/CURRENT-STATE.md
    2  THE TRAY        correspondence/open/adjutant/ , with a .keep
    3  THE ROUTER      memoTrays in watcher-go/memo.go — see section 3
    4  THE CHECKER     checks/_verify_correspondence.py
                       and watcher-go/memo_desks_match_procedure_test.go

### AND THERE IS A FIFTH STEP HIDING INSIDE THE THIRD

**The router is a compiled binary.** Editing `memo.go` teaches the source; the running
watcher still has the old list.

    5  THE BUILD AND THE SWAP   rebuild, then swap the running watcher

**A desk added to the source and never swapped into the running process is the
2026-09-08 failure with one more step in front of it** — and it would look more
finished than that one did, because the code would be right.

**Nothing is done until a memo addressed `To: Adjutant` has actually been filed to
the tray by the running watcher.** That is the pass condition, not a green test.

---

## 3. THE ROUTER'S TYPED LIST COLLIDES WITH A STANDING RULING — AND IT IS OLDER THAN HIS LETTER

**He asked and the answer is yes.**

    watcher-go/memo.go      memoTrays is a TYPED MAP in the source
    scripts/wake_desk.py    desks() is DERIVED from the tray folders on disk,
                            and its comment cites the 2026-09-10 ruling:
                            "A tray existing on disk IS the desk existing."

**Two programs, two desk lists, one typed and one derived.** The ruling was made and
applied to the launcher; the watcher was never changed. **Same shape as
`protected_folders.txt` — a rule with one reader.**

### THE DERIVED RULING STANDS, AND THE REFUSAL SURVIVES IT

The watcher's typed list has a good stated reason: *"A memo to a desk that does not
exist is REFUSED and sent to _needs_review."* **That reason does not require a typed
list.**

**Refusal comes from the TRAY not existing, not from the name not being in a list.** A
memo `To: marketing` is refused because `correspondence/open/marketing/` is not there.
Same refusal, better source, and creating a desk becomes one deliberate act instead of
four.

**The risk it introduces, stated:** a stray or mistyped directory under `open/` becomes
a desk. **The guard is the checker, which already asserts the tray set matches the
procedure.** Derive the behaviour; check the set.

**RIDE THIS CHANGE WITH THE ADJUTANT TRAY.** It is the same file, the same rebuild and
the same swap, and doing it separately means touching `memo.go` twice. **Adding the
adjutant to a typed list you are about to delete is work that exists only to be
undone.**

---

## 4. OUTBOUND ONLY IS A CONVENTION, NOT AN ENFORCEMENT — SAY SO

**Nothing can stop him putting a file in `open/owner/`.** He has a keyboard. **Do not
build something that pretends otherwise.**

**What CAN be done is detection**, and it is one assertion in the correspondence check:

    an OPEN memo in correspondence/open/owner/ whose From: is Owner
    -> MISFILED. It belongs in adjutant/.

**Only open memos.** Once the answer-routing fix lands, an ANSWERED memo `From: Owner`
routes to `open/owner/` legitimately — that is the answer coming back to him and it is
exactly right. **A check that flagged those would go red on correct behaviour and be
switched off inside a week.**

---

## 5. WHAT DOES NOT CHANGE

**No change to how any other desk is addressed. No new status word. No change to
`inbox/` as the single way in** — the adjutant tray is a destination, not a second
drop point. **One way in, one sorter.**

---

## 6. HOW IT IS PROVEN

    a memo To: Adjutant is filed to correspondence/open/adjutant/
      BY THE RUNNING WATCHER, not by a test that checks a returned string
    a memo to a desk with no tray is still refused to _needs_review/,
      and the refusal message names the desks that DO exist
    creating a tray folder makes that desk addressable with no code change
    removing one makes it refuse again
    an OPEN memo From: Owner in open/owner/ is flagged as misfiled
    an ANSWERED memo From: Owner in open/owner/ is NOT flagged

**The first assertion is the one that matters** and `memo.go` says why at line 202:
`TestAnAnsweredMemoLeavesTheOpenTray` asserted a returned path, never touched the
filesystem, and passed while the same memo existed twice.

*C1, 2026-09-11. Specified, not ordered.*
