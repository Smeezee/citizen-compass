# Update — Q44 and Q5 a/c/d done. The watcher now says out loud that the site is a full patch behind.

**2026-08-30 10:30 UTC / 2026-08-30 05:30 local · Code (background session)**

    7a684a1  Q44 - exact vocabulary hits only, in BOTH specs
    d66ce4c  Q5 a, c, d - the live version the watcher was throwing away

## THE HEADLINE, FROM A REAL RUN AGAINST RSI

    PATCH GAP: live is 4.10.0 and the site says its numbers were verified
    against 4.9

**RSI states the live version in the board's own description and the watcher
has been downloading it every four hours since it was built.** `board.go`'s
struct did not declare `description`, so Go discarded it at unmarshal and the
watcher reported on cards instead. **An undeclared field is not a missing field
- it is one thrown away silently**, the same shape as the `success` envelope
that same file already learned from.

**Both sides come from somewhere else** - the version from RSI, the verified
patch read out of the page's own data layer, not a constant in the watcher.
A watcher holding its own copy of the number it checks agrees with itself
forever. Rule 16, and it is the whole point of the item.

**Fails loud, proven by test.** An empty, blank or reworded description is
UNREADABLE and says so; `PatchGap` reports NOT KNOWN rather than level. `ø` is
recorded as PTUNone - an answer, not a parse failure.

## a AND d

    watch "Constellation" -> "*"      3 cards matching -> 828, baseline retaken
    boards [1 2] -> [1]               board 2 says, in its own payload,
                                      "will not be updated" - confirmed live by
                                      the field this commit taught it to read

**A substring match would already have let `"*"` through as a literal and
matched nothing**, which reads exactly like a quiet board. That branch is why
it is a real widening rather than a silent one.

**IN THE DEFAULTS, NOT JUST THE SETTINGS FILE.** `roadmap-watcher-settings.json`
is gitignored - widening it fixes this machine and nothing else, and a fresh
checkout would still watch one ship and still poll the dead board.

## b IS A STOP, AND IT IS RULE 6

Installing it as a service is **Windows Task Scheduler**, which hard rule 6 puts
behind an explicit ask every time. **The item's own argument stands** -
`last_good_scheduled_run` is empty, it has never once run on its own schedule,
and a tripwire nobody trips is not a tripwire. **One word from Sleven and it is
done.**

## Q44 - THE FUZZY SPEC WAS IN TWO DOCUMENTS

Q44 named rev3 §3c. The identical paragraph and acceptance line sat in
`HANDOVER-collector-rev5-COMPLETE.md`, **the newer handover, the one somebody
picks up first.** Both now read `EXACT hit or discard - no edit distance`.

Against a 7,728-entry list a 20% edit distance does not resolve a misread, **it
picks the nearest thing**, and the output is indistinguishable from a correct
read. It carved an exception into hard rule 11 and stood for three revisions.

## DEFERRED

    D6  Q5b needs Sleven: register the watcher as a scheduled task (rule 6).
    D7  roadmap-watcher-settings.json is gitignored while config.go's defaults
        are tracked - two sources for one decision. Defaults now carry it, but
        the split is worth closing.
    D8  the watcher's history file grew by 828 rows in one run now the filter is
        board-wide. Fine today; worth a size policy before it is a year old.
