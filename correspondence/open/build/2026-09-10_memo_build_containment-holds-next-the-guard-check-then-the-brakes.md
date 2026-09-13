# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: Containment holds. Next: the guard check, then the brakes when Architecture's spec is settled.
Status:  Open

**`Edit(inbox/**)` contains an unattended desk on Windows, proven by a refusal.**
That was the one open safety question in the whole automation and it is now measured.
**Nothing else today mattered as much as that.**

## THE TWO FAILED CONDITIONS

**Leave them failed. You were right not to relabel them.** A control that objects to
a real write is working; the write was yours and the control could not know that.
**Failing honestly on a file that genuinely appeared is the behaviour I want, and a
pass I had to argue for is worth nothing.**

**Do not build the watcher-subtraction.** Your own call and it is the right one —
third clever control in two days. **The operational rule is enough: nothing goes into
`inbox/` in the minutes around a wake.** Write that down where the next session finds
it.

## THE COST

**Half a dollar a wake, and the rules are what cost it. Keep the rules.**

I said hand the desk its rules or stop claiming it has them, and I meant it at that
price. **Do not trim `CLAUDE.md` and do not propose a shorter extract** — a desk that
carries most of the rules is a desk nobody can reason about.

**One thing I do want measured, not now:** the letter run read 304,000 cached tokens
against a 33,601-byte prompt file. **Those two numbers do not obviously belong to each
other.** When the brakes are done, find out what the rest of that is. It may be the
cheapest saving available and it costs nothing to look.

## NEXT, IN ORDER

**1. Extend `checks/_verify_api_key_guard.py`** so both enforcement points — the
PowerShell guard and the launcher's own refusal — are asserted to agree. **You named
it, I said after the run, the run is done.**

**2. Then stop and wait for the brakes spec to settle.** `claude/SPEC_the-brakes-2026-09-10.md`
is on disk but **one value in it is still with me** — the per-wake spend cap.
Architecture says the lock, the two ceilings and the log do not wait on that. **Build
those. Leave the cap's value as a lookup with nothing in it and refuse to wake without
one.**

**3. Do not wake anything again until the brakes exist and have been tripped on
purpose.** Your own standard, applied to them: a brake that has never fired is a brake
nobody has tested.

## THE SCRIPT YOU OVERWROTE

**Closed. Do not raise it again.** You said so before I asked, the argv that carried
the proof is preserved, and the replacement is better than what it replaced.
