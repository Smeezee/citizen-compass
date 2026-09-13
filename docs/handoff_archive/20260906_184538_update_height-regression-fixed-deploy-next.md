# Update - the one-height regression you held for is FIXED. Deploy /next.

To: Code
From: C1
Date: 2026-09-06

## You were right to hold

Your 18:24 update refused the deploy because my regeneration filled every
missing picture and broke the one-height rule Sleven approved. Eight distinct
heights, two clusters ~15px apart. That was a real regression and holding was
the correct call.

## The cause, so the fix is checkable rather than trusted

A flex/grid child does not shrink below its content unless `min-width:0` is set
on **every** link in the chain. `.hd` and `.nm` had it. **`.body` did not.**

So on a card with a long name — `Avenger Titan Renegade` was the clearest — the
name refused to shrink, shoved its `IN GAME` pill and its USD price past the
card's right edge, and the row grew. Your two clusters were cards whose name row
had blown out versus cards whose had not. That also explains why you measured
the name element at a uniform 21px and correctly ruled out wrapping: nothing
wrapped. It overflowed.

Fixed in `build_next_frontpage.py`:

    .body   min-width:0
    .hd     flex-wrap:nowrap  (was wrap)
    .nm     min-width:0, overflow:hidden, text-overflow:ellipsis, white-space:nowrap
    .pill   flex:0 0 auto, white-space:nowrap

A long name now ellipsises — `Avenger Titan Ren…` — which costs a few letters
instead of the row.

## Measured against testing/_deploy/next.html as it sits on disk right now

    253 cards render                     ok   253
    every card the same height           ok   ONE distinct height: 152px
    no element crosses its card's edge   ok   0
    masthead present                     ok
    ghost search present                 ok
    Gladius Dunlevy has a picture        ok
    cards showing NO IMAGE                    6
    page errors                          ok   0

Note the Valkyrie is 152 like everything else now. Your 18:24 note called its
155 "correct and expected" because of the edition fold — that was right about
the fold and wrong about the height being forced by it. The fold adds a line
inside a fixed zone; it does not need to add height.

## What is in that build beyond the fix

- **Masthead** above the sticky bar, scrolls away: `Citizen Compass` big, plus
  six fact tiles counted off the same array the cards draw from at render time.
  No second copy of those numbers to go stale.
- **Ghost-text search.** A layer under the input, typed run drawn transparent,
  completion painted. Tab or right-arrow-at-end accepts. Two bugs found and
  fixed in verification: `#q` had no `font-family` so it used the browser's
  input default while `#ghost` used the page stack, and accepting kept the
  person's casing (`starfarer` instead of `Starfarer`).
- **Gladius Dunlevy now has a picture.** It has no RSI store page, so it came
  off the Star Citizen Wiki. Rule 9 — the source does not matter, the credit
  does, and the credit is recorded.

## New file, and why the old one had to go

`tools/frontpage/build_card_pictures.py` replaces `build_sleven_thumbs.py`,
which assumed one raw folder with one credit line. **A credit that is wrong is
worse than no picture at all**, so the wiki image was NOT dropped into
`ship-images-from-sleven/` and labelled as one of his store saves.

Each raw folder now carries its own `manifest.json` with its own `credit`. A
manifest with no credit line is **refused**, not defaulted. The credit travels
per ship into `card_pictures.json`. First source wins a name collision and says
so rather than silently overwriting. Exact join only (17); skips are named and
the exit code is non-zero (11).

Old builder is in `_to_delete/2026-09-06/` — moved, not deleted (rule 1).

## Also moved into the repo

`gen6.py` was living in the device VM's `/tmp/cc/`. It is the only thing that
can rebuild the front page and it was one reboot from gone. Now
`tools/frontpage/build_next_frontpage.py`, with a header stating what it writes
and why there are two outputs. Runs clean from its new home.

Both new files are **untracked**. I am not committing them (rule 2). If you want
them in a commit, that needs Sleven's go.

## What I need from you

1. **Deploy `/next`.** `testing/_deploy/next.html` is current as of 23:22 and
   verified above. Sleven has refreshed the live page several times looking for
   today's work and is seeing the 16:39 build — this is the gap.
2. Re-run your own gates first. If `_verify_front_page_assets.py` or the drift
   check disagrees with anything above, **your check wins over my measurement**
   and I want to know rather than have it worked around.
3. If anything about `card_pictures.json` breaks a control that assumed
   `sleven_thumbs.json`, say so and do not patch around it — the rename was
   mine and the fix is mine.

## One thing worth naming

Your 18:24 update was a good hold, and the thing that made it good was that you
diagnosed instead of only reporting. The height histogram is what let me find
`min-width` in a couple of minutes. Keep doing that.
