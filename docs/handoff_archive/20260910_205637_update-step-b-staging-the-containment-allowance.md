    state        WORKING
    blocked_on
    clears_by

Filed at 20:57 CDT / 01:57 UTC — `date` run at 20:55:00, this typed after it.

# GO RECEIVED. STAGING THE CONTAINMENT ALLOWANCE — THE HALF OF STEP B THAT
# SPENDS NOTHING AND WAKES NOTHING.

## WHAT I AM TREATING "GO" AS, SAID PLAINLY BEFORE I ACT ON IT

**Item 1 of the step B request: narrow the launcher's write allowance and build
the control that keeps it from colliding with a protected folder.** Mine to
build, costs nothing, launches nothing.

**I am NOT treating it as item 2 or item 3.** The probe wake still needs the
master switch, the switch still does not exist, and **creating it is his act and
not mine.** The gate will refuse a wake tonight exactly as it did three times
this afternoon, and I am not going near it.

**This is also the first line of Echo's own recommended order** — *everything
staged first, then the real switch enabled, then one prepared run.* Staging is
step one of that sequence whichever way "go" was meant.

## HIS ONE-LINE QUESTION, ANSWERED IN ONE LINE

**No. None of Echo's three answers changes the step B request** — she backs the
narrow allowance I proposed, she backs Option 1 for the switch, and the lease
idea changes what step H eventually is rather than anything in step B. **Move on
the request as written.**

## FOUR MEMOS READ BEFORE STARTING

    20:10  the export folder location is world-readable - MY ERROR, accepted
    20:13  the answer routing works, and the supersede misses on a date prefix
    20:33  the clock question is withdrawn - do NOT open memo.go, do NOT touch
           the timezone
    20:51  Echo answered the three questions - INPUT, NOT AUTHORISATION

**On the export folder: he is right and §2 of my own audit is the evidence
against §8 of it.** `C:\Users\Public` inherits `Everyone:(RX)` — I recommended a
location that would have been readable by every account on the machine, which is
a weaker boundary than the thing it replaced. **Nothing was run, nothing is
broken, and the ACL is his under rule 6 regardless.**

**On the date-prefix defect: the investigation is withdrawn and I am not doing
it.** The watcher stamps local; the mismatch came from a desk typing a UTC date
into a filename after 19:00 local. His rule — a reply preserves the filename it
received, character for character — fixes it with no code change, **and I am
explicitly not touching the timezone, which would collide with the
`America/Chicago` ruling in the brakes spec.**

**The one thing that is mine out of all four** — a check that no filed memo
carries two dates, catching both the `2026-08-30_2026-08-31_` and the
`2026-09-08_20260908_` shapes — **is behind containment and the brakes and does
not jump the queue.**

## WHAT I AM BUILDING NOW

    the allowance narrows   Edit(inbox/**)  ->  Edit(inbox/_replies/**)
    one constant            the directory name is named once and the allowance
                            is derived from it
    the probe grows a third attempt         a write into a PROTECTED folder,
                            which must be refused
    the control             a checker proves the reply path and the protected
                            names cannot collide - in BOTH directions

**Verified before choosing the shape: the watcher genuinely recurses into
`inbox/` subfolders** — `processPath` walks new directories, adds watches and
picks up content already inside them. A reply written to `inbox/_replies/` is
filed normally. **A reply path the watcher never reads would have been a desk
talking into a wall, so that was worth checking before building on it.**

**And the collision that actually matters is the opposite of the one feared.**
The allowance cannot reach a protected folder by construction — `inbox/_replies/**`
does not match `inbox/Citizen Compass AI Brain/...`. **The real risk is somebody
adding `_replies` to `protected_folders.txt`, at which point every reply is
silently never filed.** The control asserts both directions.

Nothing woken. Nothing committed. The switch is still absent.
