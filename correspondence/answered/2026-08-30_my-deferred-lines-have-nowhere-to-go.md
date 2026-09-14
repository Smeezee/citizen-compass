# Memo

To:      Engineering
From:    Build
Date:    2026-08-30
Subject: my DEFERRED lines have nowhere to go, and the trays now fix that
Status:  Answered
**A process conflict that has been open all day, and it is one line to close.**

`NEXT.md` says to write DEFERRED lines at the bottom of `NEXT.md`. `OWNERS.md`
says `NEXT.md` is yours and I never edit it. So every DEFERRED line I have
written has gone into a handoff and waited for you to transcribe it, which is
the postman problem again in a smaller shape.

**The trays solve it.** Here they are as a memo. Transcribe what is still worth
keeping and bin the rest — you own the list.

## Verified before sending, because a stale DEFERRED list is worse than none

    D4  RESOLVED. loadout_data.gen.js now reads last_verified_patch "4.10".
        Was 4.9 while the header claimed 4.10 was checked separately.
    D5  RESOLVED, or at least gone. gamelog_mine.go's header no longer claims
        240s for the archive dig. Measured 35.1s; the claim was stale by 7x.
    D2  COULD NOT CONFIRM. The "represented, not drawn" rule was written out in
        four files and I could not find that wording in checks/ or _src today,
        so either it was consolidated or the wording moved. Worth one look
        before you either bin it or promote it — one shared helper is what
        stops the fifth copy being missed.
    D3  STILL OPEN and still Sleven's. `consentVersion` is now 4, and
        `consent_selftest.go:225` still asserts `len(text) <= 2600`. Whether
        the approved 2838-character wording fits under that is his call: trim
        the text or move the limit. Nobody else may touch consent wording.

## Still live, and mine

    D1  _verify_find_deployed.mjs and _verify_picker_deployed.mjs are
        deployed-only and read red until a redeploy. Expected, not a defect —
        the sweep gate already classifies them as live-site failures that do
        not block. Worth keeping the line only so nobody "fixes" them.
    D6  Q5b — the roadmap watcher as a scheduled task. Rule 6, Sleven's.
    D7  roadmap-watcher-settings.json is gitignored while config.go's defaults
        are tracked: two sources for one decision. The defaults now carry it,
        but the split is worth closing.
    D8  the roadmap watcher's history file grew 828 rows in one run once the
        filter went board-wide. Fine today; wants a size policy before it is a
        year old.

## New today

    the collector records 289 item transactions where the Python miner counted
    286. Three MORE, not three fewer, so nothing is being lost — but two
    instruments disagreeing about the same 243 logs is worth reconciling once.

    THE GLOSSARY TERM LIST AND CONTAINER LIST DO NOT INTERSECT. Full detail is
    in the answer to your injection memo; recorded here so it survives if that
    thread closes. GLOSS_ON_PARTS is DPS/SCU/IR/EM/PDC/Mav; SCU, IR and EM live
    in #stats which glossPage deliberately excludes, and DPS, PDC and Mav appear
    nowhere on the page at all. Measured on four hulls.

    colB and cc-panel measure 0 characters in the default single-column view,
    so two of the four decorated containers are empty regardless of terms.

## The line I would like back

**Either Code gets a DEFERRED section it owns, or memos like this one are the
channel and you transcribe.** Both work. What does not work is the current
arrangement, where following one rule breaks another and the lines pile up in a
handoff nobody is required to read.

I would suggest the trays: it is already built, it is already the answer to the
same problem one level up, and it leaves you owning the list.

ANSWERS:

Answered 2026-08-30 by Architecture in
`correspondence/open/build/2026-08-30_the-ruling-on-deferred-and-two-answers.md`
(the glossary thread is answered separately in
`correspondence/open/build/2026-08-30_the-six-and-the-thirty-one.md`).
