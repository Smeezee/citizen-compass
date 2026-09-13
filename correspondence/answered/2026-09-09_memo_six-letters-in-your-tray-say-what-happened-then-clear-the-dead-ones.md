# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: six letters have been sitting in your tray since the 7th and 8th — say what happened to each, then clear the dead ones
Status:  Answered
**Nothing here is a new job. It is closing post that never got closed.**

Six letters are still in `correspondence/open/build/`, all marked `Status: Open`,
none with an `ANSWERS:` block. **Some of them I can see were overtaken by a later
memo. Some I cannot tell.** You are the only desk that knows which.

    2026-09-07  raptor-is-resolved-from-rsi-and-the-front-page-has-an-unaudited-source
    2026-09-07  ruling-the-five-are-three-different-cases-and-not-null-stands
    2026-09-07  the-in-game-data-gap-is-measured-and-most-of-it-is-an-api-pull-not-a-browse
    2026-09-08  audit-to-build_the-hook-claims-both-hold-and-one-thing-claude-md-promises-is-not-there
    2026-09-08  the-seventy-five-finding-is-accepted-cic-is-not-going-and-the-small-import-is-authorised
    2026-09-08  the-stop-hook-points-at-a-file-deleted-five-weeks-ago

## FOR EACH ONE, ONE OF THREE WORDS

**DONE** — the work in it actually landed. Say what proves that: a commit, a file,
a run, an output. **Not "it should have been done."**

**SUPERSEDED** — a later memo replaced it. **Name the memo.** The RAPTOR one looks
like this to me: its central claim was retracted when the ship turned out to be a
deliberate joke entry. The stop-hook pair looks like it too, overtaken by
`2026-09-09_..._the-stop-hook-is-authorised-sleven-said-go`. **Check me rather
than agree with me.**

**NEVER STARTED** — nobody did it and nobody is going to. Say so plainly. That is
information, not a confession.

**The two I genuinely cannot call from outside** are whether B2 ran for the 231,
and whether the small import authorised on the 8th ever executed. **Those two
need a real answer, not a judgement.**

## THEN CLEAR THEM

**DONE and SUPERSEDED:** reply in the memo under `ANSWERS:`, set
`Status: Answered`, drop it back in `inbox/`. The watcher files it. That is the
whole mechanism and it does not need a shell mount.

**NEVER STARTED, and only those:** my instruction, in my words — **move them to
the Windows Recycle Bin. I will empty it myself.** Not deleted outright, not left
in place. If anything blocks sending to the Recycle Bin, put them in
`correspondence/_to_delete/` and say so.

**If a NEVER STARTED letter contains work that still ought to happen, do not bin
it.** Say what it was and leave it open. Binning a live job to tidy a folder is
the one way this goes wrong.

## WHY IT MATTERS RATHER THAN BEING HOUSEKEEPING

**An open tray is supposed to mean somebody is waiting.** Six letters that mean
nothing teach every desk to stop reading the tray, and then a real one sits there
too. This has already happened twice this week: a memo resolved the same day and
never moved, and `_verify_owners.py` carried as unrun while your green sat in
Architecture's tray.

**Answer this one last, after the work you already have.** Nothing here is urgent.
It just has to stop being invisible.

---

ANSWERS:

**Called. Four cleared, two stay open, none binned.**

    raptor-is-resolved-from-rsi                  SUPERSEDED     cleared
    the-in-game-data-gap-is-measured             DONE           cleared
    audit-to-build_the-hook-claims-both-hold     SUPERSEDED     cleared
    the-seventy-five ... small-import-authorised DONE           cleared
    ruling-the-five ... not-null-stands          NEVER STARTED  STAYS OPEN
    the-stop-hook-points-at-a-file-deleted       NOT DONE       STAYS OPEN

Each of the four carries its own `ANSWERS:` block with what proves it. **Nothing
went to the Recycle Bin**: both of the two that were never started contain work
that still ought to happen, which is the case you told me not to bin.

## THE TWO YOU COULD NOT CALL FROM OUTSIDE

**The small import EXECUTED.** `data-layer/derived/ship-wiki-fields/wiki_ship_fields.json`,
7,669 bytes, written 2026-09-07 22:59. usd 76 and url 10 exactly as authorised.
Cargo landed **0**, not the 120 that was forecast, because that count read a real
capacity of zero as a blank - my error, recorded at the time rather than tidied.

**B2 DID NOT RUN.** Not a judgement, a search: `family_id` appears **nowhere in
this repository** - not in `alembic/`, not in `app/`, not in any language. Sixteen
migrations on disk, none about families. No hand-entered mapping, no CSV-FM row,
no Starlancer BLD row. The ruling letter stays open because all of it is undone.

## YOU WERE RIGHT ON THE RAPTOR, AND I CHECKED RATHER THAN AGREED

Superseded twice on 2026-09-07 - by the STOP memo that reverses it outright, then
by Sleven's own call that the row is KEPT and labelled as the gag it is.
**Nothing from the original order was ever applied**, and the row's own fields
prove it: role still `Ground Vehicle`, `usd` null, `url` null.

**One part of it was not superseded, so it was answered rather than cleared
unanswered** - the count of `conf="verified"` rows with no URL: **13 of 254, all
of them `pledge_only`.**

## THE ONE I COULD NOT CLOSE, AND WHY IT IS NOT AN AUTHORISATION PROBLEM

**The Stop hook is still in `.claude/settings.json`.** I read the authorisation
memo first, as you said to - it does carry your written go, and I did not carry
that letter forward as waiting on you.

**Three attempts, all refused by this session's own permission layer:** a backup
copy of the file, a scripted edit removing only the `hooks` key, and the Edit
tool. Not a hard rule - the harness fences `.claude/` for this session whatever
the memo says. **I stopped after three rather than hunting for a way around it.**

That makes it the rule 26 last resort: no desk on this machine can perform it.
The exact edit, and the reason a permission rule cannot fix it from inside, are in
the update filed alongside this answer. **Nothing is lost while it sits** - the
hook has pointed at a deleted file for five weeks and the Go watcher has done the
job throughout.

## ON WHY IT MATTERED

You said an open tray is supposed to mean somebody is waiting. **Two of these six
were answered on disk before I ever opened them** - the small import had a
completion memo sitting in `answered/` since the 8th, and the RAPTOR order had
been reversed twice within hours. Reading the tray would have told me; not
reading it is what rule 24 was written for.
