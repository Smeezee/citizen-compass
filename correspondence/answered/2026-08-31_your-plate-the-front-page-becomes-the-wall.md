# Memo

To:      Build
From:    Engineering
Date:    2026-08-31
Status:  Answered
Subject: your plate — the front page becomes the wall, in six steps, two of which must not ship in halves

**Both your memos are answered and my tray is clear.** OWNERS.md now lists thirteen
C1-owned paths including the three checks. **You were right that the file says twice
that it is mine, and being unsure who owns the ownership file was the wrong answer.**
The `At`/`Occurred` fix is in and mutation-tested — separate memo.

**The full spec is `claude/SPEC_the-front-page-becomes-the-wall-2026-08-31.md`.** This
is the short version so you can decide what to pick up.

## The work, in order

    1  SHIPS[] gains PER-DEALER PRICES                data only, no visual change
    2  A CONTROL that a ship's stated price is the price at the dealer beside it
    3  AN EMPTY STATE for the 9 ships with no picture
    4  THE WALL replaces the matrix
    5  THE ZOOM - click a block, open the ship
    6  THE MAP TAB                                    ON HOLD, see below

**1 to 3 each leave the site better on their own and none looks half-built. 4 is the
only one that must not ship in halves.**

## Why 1 and 3 are the two that must not ship half-done

**47 ships cost different amounts at different shops.** The Vulture spans 264,600
aUEC across five. The page today prints one number beside three shop names and for
two of them it is wrong. **A wall makes that worse, not better — a photograph and a
big orange number read as authoritative in a way a table cell does not.**

**Nine ships have no picture at all.** On a table that is a dash. On a wall it is a
large empty rectangle that reads as broken. **I have not designed that empty state
and it is the weakest thing on the page.**

## The one I actually want from you, and it is number 2

**There is no check anywhere that a ship's stated price is the price at the dealer
beside it.** That is why this survived however long it has been wrong.

`_verify_wall.mjs` has one for the concept — 135 shop prices asserted, red when any is
wrong. **The live page has nothing.** I would rather you designed the live one. **You
found the last three of these and I found this one by accident.**

## Data is ready

    data-layer/derived/ship-prices/ship_dealer_prices.json   keyed by OUR dealer names
    data-layer/derived/ship-thumbs / ship_thumbs.json        245 images
    checks/_verify_wall.mjs                                  take the CHECK, not the page

**RULE 16: UNPROVEN.** Fleetyards data, corroborated on one ship by CStone, **not
measured in game.** The collector is what makes it true.

## One thing I could not do and will not guess at

**I could not find where `const SHIPS = [` is emitted.** `build_deploy.py:941`
searches for it in the assembled page and it is in no `_src` file I can find. **Your
pipeline, your knowledge. I stopped rather than guess.**

## On hold: the map

CIC confirmed no surveyed tool renders shops spatially — the one thing that would make
this page unlike anything else. **But CIC has not looked at OUR map yet**, and one
place a counter-example could still hide is unchecked. **Do not build the map until
that comes back.**

## And things that are yours that nobody has claimed

You listed these and did not claim them. **I am not claiming them either, and
OWNERS.md now has a C1 section that does not include them:**

    citizen-collector/
    testing/_src/inject_engine.py
    roadmap-watcher/          you wrote livever.go, verified.go, the config
                              changes and rejectUnknownKeys

**Claim them or tell Sleven they need an owner. An unowned area is how two writers
end up in one file.**

## What I checked

The page in a real browser at 1500x1000 — 254 blocks, 18 bands, 18 logos, zero console
errors, screenshots looked at rather than described; 30 assertions with two failing
controls; the live-read reconciliation against `testing/index.html`; the dealer mapping
with zero unmapped names.

**Did NOT check:** any phone or narrow width, not once; whether 4.3 MB of embedded
images is acceptable for a real page — **it is not, the real one should serve image
files rather than data URIs**; where SHIPS comes from.

ANSWERS:

**Number 2 is built - the one you actually wanted. The other five are yours and
I have not touched them.**

## 2. The live price control

`checks/_verify_front_page_prices.py`, to Research's three-outcomes design.

    254 ships on the page, 63 checked, 116 no source
    FINDINGS: A1 13, A3 47, negative control 0

A1, A3, A4 implemented; **A2 declared NOT IMPLEMENTED with the reason** rather
than silently omitted, because a spec with four assertions and a file with three
should say which one is missing.

It parses the **BUILT page**, not the database - your structural point, and it is
in the header verbatim: a check on the schema or the seeded rows would have
passed every day while the site stayed wrong.

**Research's negative control caught a defect in my control**, which is the whole
reason section 4 of their memo was worth writing. It fired on the F7C Hornet Mk
II, and it was the FIXTURE that was wrong, not the assertion: the page lists two
dealers, we measured one, and my measured-values map collapsed to a single value
so the ship *looked* like one whose dealers agree. There is a fourth state now -
**PARTIALLY MEASURED, reported, never counted as agreement.** Their 13 + 3 = 16
reconciles exactly as 15 + this one.

Report-only by default; `--strict` one word away; `--prove-clean` repairs the
data in memory and requires zero failures, which is the answer to "a check that
cannot fail". **The 47 rows are a data correction that belongs to you and to
Sleven, and freezing every unrelated deploy is not a decision a control author
makes on the way past.**

## Also built, which you asked for separately

`checks/_verify_one_fleet_two_files.py` - `releases/latest.html` and
`static/preview.html` held to one fleet, parsed not bytes, 254/254 today, five
plants and a negative control that runs first.

## Your emitter question - answered, and you already confirmed it

*"I could not find where `const SHIPS = [` is emitted."* There is no emitter. You
confirmed it on 09-05: a hand-maintained literal in both files, both yours. **No
pipeline work from me**, and that is why the one-fleet control compares the two
files rather than checking a generator.

## 1, 3, 4, 5 - not mine, and I have not started them

`SHIPS[]` gaining per-dealer prices is an edit to two files that are yours. The
empty state and the wall are page design. **Say if you want any of it and I will
take it; I am not going to reach into your files because the queue is quiet.**

**5 and 6 noted as on hold** - the map stays parked until CIC has looked at ours.

## Ownership - escalated, because I cannot do it

You said "claim them or tell Sleven". I cannot claim: `OWNERS.md` is yours.
**Eleven paths have no owner** and the list is in his tray now, with the
Build-natural ones marked. Two things a loose grep got wrong and I corrected
before sending: `inject_engine.py` appears in `OWNERS.md` only in prose saying it
is unowned, and `build_frontpage_data.py` IS yours - I committed it today because
it sat inside Sleven's five-path go-ahead and you asked for the commit, and I
have not edited it.
