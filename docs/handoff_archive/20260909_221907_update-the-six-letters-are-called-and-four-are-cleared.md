# Update — the six letters are called: 4 cleared, 2 stay open, 0 binned

**Filed 2026-09-09 22:25 CDT.** Tray item 2. The tray is 14 letters, down from 14
with six stale ones in it; four of those six are now in `correspondence/answered/`
and gone from `open/build/`.

## THE SIX, ONE WORD EACH

    raptor-is-resolved-from-rsi                  SUPERSEDED   cleared
    the-in-game-data-gap-is-measured             DONE         cleared
    audit-to-build_the-hook-claims-both-hold     SUPERSEDED   cleared
    the-seventy-five ... small-import-authorised DONE         cleared
    ruling-the-five ... not-null-stands          NEVER STARTED  STAYS OPEN
    the-stop-hook-points-at-a-file-deleted       NOT DONE       STAYS OPEN

**Nothing went to the Recycle Bin.** Neither of the two that were never started
is dead — both contain work that still ought to happen, which is the case you
said not to bin.

## THE TWO YOU SAID YOU COULD NOT CALL FROM OUTSIDE

**Did the small import execute? YES.**
`data-layer/derived/ship-wiki-fields/wiki_ship_fields.json`, 7,669 bytes, written
2026-09-07 22:59. usd 76 and url 10 exactly as authorised; **cargo landed 0, not
120, and the 120 was my own bad count** — `if not s.get("cargo")` read a real
capacity of zero as a blank. 14 real disagreements reported and left unresolved.
Nothing a visitor is served changed.

**Did B2 run for the 231? NO. It was never started.** Not a judgement — a search:

    family_id  in alembic/     0 hits
    family_id  in app/         0 hits
    family_id  anywhere in the repo, any language     0 hits
    alembic migrations on disk: 16, none about families

There is no migration, no hand-entered mapping, no CSV-FM or Starlancer BLD row.
**The ruling letter stays open because the work in it is entirely undone.**

## YOU WERE RIGHT ABOUT THE RAPTOR, AND I CHECKED RATHER THAN AGREED

It is superseded **twice**, both on 2026-09-07: first by the STOP memo that
reverses it outright, then by Sleven's own call that the row is KEPT and labelled
as RSI's April Fools gag with a link to their own page. **Nothing from the
original order was ever applied** — the row still reads role `Ground Vehicle`,
`usd` null, `url` null, which is exactly what it would not say if it had been.

**One part of that letter was NOT superseded and I answered it rather than
clearing it unanswered.** Its item 3 asked for the count of `conf="verified"` rows
with no `url` in the front page's source: **13 of 254, and all 13 are
`pledge_only`** — the same perfect separation Architecture found in the 75. For
twelve of them `verified` means "we are sure this ship exists", not "we hold a
URL". **RAPTOR is the one that differs in kind**: its problem is invented text, not
an absent link. Nothing fixed, per that letter's own instruction.

## ONE OF THE SIX IS BLOCKED, AND IT IS MY OWN PERMISSION LAYER

**The Stop hook is still in `.claude/settings.json`.** It still runs
`generate_handoff.py`, which has not existed since 5081be4 on 1 August.

You were right that it is not blocked on *authorisation* — I read
`2026-09-09_20260909_memo_audit-to-build_the-stop-hook-is-authorised-sleven-said-go.md`
before touching anything, and it carries your written go. **I attempted the edit
three times and every attempt was refused by this session's permission layer:**

    cp .claude/settings.json to _to_delete/  (a BACKUP)   REFUSED
    python edit removing only the hooks key               REFUSED
    the Edit tool, the natural tool for the job           REFUSED

The refusals are the harness's, not a hard rule's — the path `.claude/` is fenced
for this session regardless of what the memo says. **I stopped after three rather
than looking for a way around it**, which would have been exactly the "switch the
guard off in a hurry" move the billing guard exists to prevent.

**This is the rule 26 case: no desk on this machine can perform the action.** Not
a workflow, a genuine last resort. The edit is one deletion, and here is exactly
what it is, so it costs one paste and no thinking:

Delete the entire `"hooks"` block from `C:\Users\david\citizen-compass\.claude\settings.json`,
leaving the file as:

    {
      "permissions": {
        "allow": [
          "Edit",
          "Write",
          "Bash(git add:*)",
          "Bash(git commit:*)",
          "Bash(git status)",
          "Bash(git diff:*)",
          "Bash(python:*)",
          "Bash(pytest:*)"
        ]
      }
    }

**The permanent fix rather than this one time:** the refusal message says a Bash
permission rule in settings would allow it — but that rule would live in the same
fenced file, so it is the same block one level up. **The honest answer is that a
session which is expected to maintain `.claude/` has to be started able to write
it.** That is your call about how this session runs, not something I can arrange
from inside it.

**Nothing is lost while it stays.** `pipeline_log.txt` is still frozen at
2026-08-01 23:40 and the Go watcher is current to this minute — the hook has been
firing into nothing for five weeks and the job has been done throughout.

## AND ONE THING THAT WILL NEED ARCHITECTURE, NOT ME

The ruling letter's disposition of RAPTOR was *"held out as the single known
exception"*, and the STOP memo then said B2 *"gets cleaner, not harder"* because
RAPTOR would leave the ships table entirely. **Sleven's ruling then put it back**
— kept deliberately, as a joke card. **So the exception is live again and nobody
has said what `family_id` it takes.** Flagged, not decided, and not going to
Sleven: it is Architecture's ruling to make and it is queued behind the card work
he has already ordered.

Nothing committed.
