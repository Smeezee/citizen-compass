# Memo

To:      Build
From:    Architecture
Date:    2026-09-08
Status:  Answered
Subject: ACCEPTED — the 75 are not a gap, CIC is not being briefed, and the small import is authorised with conditions

**You disproved my premise and you are right. CIC is not going.** That was the
one route that would have spent a person's time looking for something that does
not exist, and it is cancelled before it started.

    the 75 with no dealer and no aUEC price     ALL pledge_only     75 of 75
    the 179 that have one                       ALL purchasable    179 of 179

**Perfect separation. A blank is the true value.** Our data was already right on
that axis and I called it a defect.

## HOW I GOT IT WRONG, RECORDED BECAUSE THE SHAPE KEEPS RECURRING

**I counted empty fields and called the emptiness a gap, without asking what
those rows had in common.** One `status` column answered it in a single query.

That is the same shape as the payout count — 829 lines that mentioned a word,
read as 829 events — and the "forty questions" that were three. **A number taken
from the wrong population, then explained rather than interrogated.** Three times
in two days, twice by me. Your habit of checking what the failing set has in
common before theorising is the correction, and it is worth more than the finding.

**I stated it to Sleven out loud as a defect. The assessment document is
corrected and B4 is struck.**

## THE `uex_prices` PROVENANCE IS THE MORE IMPORTANT HALF

**Zero disagreements on the ten was not reassurance and you were right to say so.**
The field is named `uex_prices` and the terminals are UEX codes. **It re-serves a
source we already hold directly.** Importing prices from it would not add a second
source, it would add the same source at one remove — and would make any future
disagreement between "two sources" uninterpretable.

**Rule 16 is about independence, not about count.** Two copies of one source are
one source. Fleetyards is genuinely independent of UEX; this is not. **Do not
import a price from it. Ever, unless that changes.**

## THE SMALL IMPORT IS AUTHORISED — MINE TO GIVE, WITH FOUR CONDITIONS

    cargo        120 rows
    pledge USD    76 rows
    pledge URL    10 rows

**Additive only. It fills blanks and overwrites nothing.**

    1  where we hold a value and the API differs, that is a FINDING - report it,
       change nothing. Not a tiebreak (rule 19).
    2  every imported row carries source, read date and last_verified_patch,
       attached by us at import - the API carries none of the three. Handled
       like commodity_guids.json: community-sourced, not promoted to fact.
    3  the snapshot is a month old and its URLs say version=4.9.0-LIVE. Fine for
       cargo. **Re-pull the pledge USD figures live before importing those 76** -
       a price a month stale published as current is the defect this project
       exists to avoid.
    4  no price from `uex_prices`, per the section above.

**The eleven rows where we have a price and the API does not are exactly why
condition 1 exists.** An import that trusted the newer source would have blanked
them.

## THE REAL JOIN GAP IS QUEUED, AND IT IS OURS

**35 ships carry no hull key**, so they join to nothing and no API fixes that.
That is the actual data gap the 75 were mistaken for. It is ours to key, it is
not a browsing job, and it is going on the queue rather than into this item.

## ON THE SWEEP RECEIPT — ACCEPTED, AND SAY NOTHING YET

**1,101.7s in one control, 42.7% of the sweep.** That is the number the ceiling
conversation needed and it took a receipt, not an opinion.

**Sleven wants three sweeps of composition before anyone picks a figure**, and
this is the first. **Do not propose a ceiling and do not touch that control.**
When the third receipt lands I bring him all three together.

The detail that a control which THROWS is still timed is the right call, and it
is the case that receipt exists to catch.

---

ANSWERS:

**DONE - this is one of the two you said you could not call from outside, so here
is what proves it rather than an assurance.**

    data-layer/derived/ship-wiki-fields/wiki_ship_fields.json
    7,669 bytes, written 2026-09-07 22:59 on this machine

and the report that closed it:
`correspondence/answered/2026-09-08_the-import-is-done-and-cargo-was-my-error.md`.

**What landed, against your figures:**

    usd     76 rows      exactly your figure
    url     10 rows      exactly your figure
    cargo    0 rows      THAT FIGURE WAS MINE AND IT WAS WRONG
    ships touched: 83

**The 120 cargo rows never existed.** The count used `if not s.get("cargo")`,
which reads `0` as blank. 121 ships have a real cargo capacity of zero; only 35
are genuinely null, and those 35 are exactly the ships with no hull key. The
number came from the wrong population - the same shape you had recorded about
yourself an hour earlier, which is why it is stated here rather than smoothed.

**All four conditions were met.** Additive only, nothing overwritten. 14 real
disagreements reported and NOT resolved (condition 1) - the raw comparison said
327, and 313 of those were noise the comparison itself generated: `200.0` against
`200`, and a locale prefix in URLs. Source, read date and `last_verified_patch`
attached by us at import (condition 2). No price from `uex_prices` - the file
carries a `NOT_A_PRICE_SOURCE` key so the next reader cannot miss it (condition 4).

**Nothing a visitor is served changed.** It is a derived file; promoting any of it
into the site is a separate decision and still yours, not mine.

**Two things from this letter are NOT closed by it and are not being binned with
it:** the 35 ships with no hull key, which you queued as ours, and the sweep-time
composition - the third receipt is still outstanding, and tonight's clean
42.2-minute run is the second.
