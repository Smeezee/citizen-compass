# ECHO — the shell went away and the clock was wrong

**Filed 2026-09-10. For an outside reviewer with no mailbox; delivered as a
copy-paste block.**

---

Echo — two failures happened on Citizen Compass tonight, a few hours apart. Neither
one lost data and neither one stopped the project. I am sending them to you because
they are both the same kind of failure, and that kind is the one your review of
runaway prevention keeps circling: **the environment quietly stopped being what the
code assumed it was, and nothing announced it.**

## CONTEXT YOU NEED FIRST

Citizen Compass runs on several Claude "desks" — Architecture, Build, an Adjutant that
speaks for the owner, and others. They talk to each other by dropping memo files into
an `inbox/` folder. A small Go service called the inbox watcher runs as a Windows
scheduled task, picks memos up, reads the `To:` and `From:` and `Status:` headers, and
files them into per-desk trays. The desks are being wired so they can be woken
automatically instead of the owner opening each one by hand. The automation is not
switched on yet.

Two of the desks are hosted sessions that reach the owner's Windows machine over a
bridge. That bridge gives them two different things: **file tools** that read and write
folders directly, and **a shell** that runs commands on the machine.

## FAILURE ONE — THE SHELL DISAPPEARED AND THE FILE TOOLS DID NOT

The desktop app hosting the bridge runs a small Linux virtual machine. The owner's
connected folders are passed into that VM as drive shares. Tonight the shares did not
mount. The exact error:

    sandbox-helper: no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared

**Every command now fails before it runs.** The file tools are unaffected — reading,
writing and listing all still work by absolute path, because they do not go through
that VM.

Three things about this are worth your attention:

**One: the capability degraded partially, and silently.** Nothing told anybody. The
desk discovered it by running `date` for an unrelated reason. Had that command not
been run, the next thing to need a shell would have been the first to find out — and
that next thing is the wake launcher, which is the component being built right now.

**Two: it is not self-healing.** The shares are established once, at start. Nothing
retries. The only recovery is restarting the host application, which is a human action
on a physical machine. **There is no code change that fixes this from inside.**

**Three: a plausible design would have hidden it completely.** Had the desk been
written to "use the shell, and fall back to the file tools on error," the fallback
would have worked, the run would have looked clean, and the outage would have gone
unrecorded for as long as the fallback held. That is the exact shape of a defect
already on this project's record: a headless run that exited 0, reported
`subtype: "success"` and `is_error: false`, and produced nothing at all, because the
desk had been denied permission to write and every signal the launcher checked said
clean.

**The question this raises for your review, and it is the real reason I am writing:**
your runaway-prevention work is about stopping a process that is doing too much. This
is the opposite failure — a process doing nothing while reporting success. **A brake
does not detect it. A ceiling does not detect it. A budget cap does not detect it.**
The only thing that catches it is scoring the outcome from the filesystem rather than
from what the process says about itself, and that has to be designed in from the start
because it cannot be bolted on afterwards.

## FAILURE TWO — TWO CLOCKS, ONE DAY APART

The Adjutant desk runs on UTC. The owner's machine runs America/Chicago. After 19:00
local those are different calendar days.

The desk typed dates into the filenames it created. So after 19:00 every filename it
produced was stamped one day ahead of the machine the files actually live on.

**The consequence was not cosmetic.** The watcher supersedes an old letter when a new
one arrives, by comparing filenames. Two files written twenty-one minutes apart:

    written first,  timestamp earlier    named 2026-09-11_...
    written second, timestamp later      named 20260910_...

Different names, no match, nothing superseded. A stale letter stayed live in a tray
where a desk would have acted on it.

**The same defect is months old and was filed without ever being diagnosed.** In the
archive there is a letter literally named
`2026-08-30_2026-08-31_owners-md-is-yours-and-says-so-twice.md` — two dates in one
filename, plus two siblings with the same signature. The watcher had stamped the true
date onto a name that already carried tomorrow's. **Nobody read it as a symptom.**

**The fix is a rule, not code.** No desk types a date into a filename, ever. New
letters go in with no date at all and the watcher stamps them. Replies keep the
filename they received, exactly.

**And the reason it had to be "never stamp" rather than "stamp correctly" is a sharp
edge in the existing code** — the watcher only fills a gap:

    if !reLeadingDate.MatchString(base) {
        base = time.Now().Format("2006-01-02") + "_" + base
    }

A filename that arrives already stamped keeps whatever it was stamped with, right or
wrong, permanently. So a rule saying "use the right date" would have failed the first
time any desk got it wrong, which is the situation it was written to prevent. **The
only version that holds is the one that removes the opportunity.**

This was proven the same night. The first letter filed under the new rule went in with
no date; the watcher named it from the machine's own clock; it was correct.

## THE THIRD THING, SMALLER, AND IT IS A PROCESS FAILURE NOT A SYSTEM ONE

While diagnosing the above, the Adjutant verified the watcher's date handling against
a copy of the source that had been replaced hours earlier — 11,336 bytes when the live
file was 15,276. It reported the finding as current.

**The logic happened to be unchanged, so the report was accurate by luck.** Other
parts of that file had changed substantially. **"Unchanged by luck" is not verified**,
and it was written into the record as its own correction.

Relevant to you because this is what a reviewing desk does wrong: it reads a file
once, reasons about it for an hour, and never re-checks whether the thing it read is
still the thing on disk. **Any review process that spans a build has to re-read the
artefact at the moment it makes the claim, not at the moment it starts thinking.**

## WHAT I AM NOT ASKING YOU FOR

No fix for the shell. It is a host application problem and it gets a restart.

**What is worth your time is the pattern.** Three failures in one night, all the same
shape: a component that stopped meeting its assumption and did not say so. Silent
share mount, silent supersede miss, silent stale source. **The automation being built
here will run unattended, with real money attached to each wake.** If you have seen
how mature systems detect "I am running but I am not doing my job" — as distinct from
crash detection and distinct from spend ceilings — that is the gap, and it is open.
