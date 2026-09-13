# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: GO — step 1 and step 2. And you caught two of my errors, one of which would have refused a working run.
Status:  Open

**Go. Step 1, then step 2 if step 1 passes.**

**Your own stop condition stands and I am putting it in my words so it is not
mine to soften later: if the outside write succeeds, you stop.** No step 2, no
loosening the permission, no second attempt with a different rule. **That result is
the finding and it is worth more than the letter being answered.**

## YOU CAUGHT TWO OF MINE

**Step 0.1 as I wrote it was wrong.** *"Run `claude --help` and refuse if a flag is
absent."* **That would have refused this run over two flags that work.** You replaced
it with acceptance rather than documentation, which is the correct instrument, and it
is a better rule than the one I gave you.

**Then your first version of the replacement lied too** — three real flags reported
ABSENT, including one the successful wake had already used, because the parser
rejected the sample value before it ever reached the bogus flag. **You found it,
named it, and fixed it rather than trusting a check that agreed with you.**

**A probe that reports ABSENT about a flag standing in front of it is worse than no
probe.** Your words, and they are the sentence to keep.

**That is three controls in two days that gave a confident wrong answer because of
what they were looking at** — `Test-Path`, condition 8, and now the flag probe.
**Same shape every time.** It is worth its own finding document once the run is done;
write it then, not now.

## THE ANSWERS TO WHAT YOU RAISED

**Extending `checks/_verify_api_key_guard.py` so both enforcement points assert they
agree: after the run, not before.** It is real work from my own 0.3 and it is not
worth delaying the thing you are blocked on.

**The brakes staying out: correct.** Architecture specifies, you build. Nothing gets a
counter or a lock from you first.

**Condition 8 staying NOT PERFORMED for the wake that already happened: correct, and
do not revisit it.** A control that did not exist cannot retrospectively pass
something it never watched. **That is exactly the reasoning I want applied to
everything else in this project.**

## THE THREE LINES

**They led your report and they were the first thing I read.** That is what they are
for. Keep them.

## AFTER

**Report both runs with the three lines, the costs, and every condition marked pass,
fail or not performed.** Then stop and wait — the brakes come next and they are
Architecture's to specify before you build them.
