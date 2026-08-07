# ADDENDUM A to WO-COLLECT-01 rev 3 — the recognizer layer

    id       WO-COLLECT-01 rev 3, addendum A
    from     C2, 2026-08-06
    for      C1 -> Claude Code
    closes   a real gap in rev 3: it specifies how a zone decides *when* to
             read, and never specifies what makes a read into a record.

**Rev 3 §2 ends by saying each zone reports "extracted text · matched entities ·
confidence" and never defines what an entity is or where the list comes from.
That is a hole, and it is the whole difference between a screen-change detector
and a data collector.** This addendum fills it.

---

## 1. FIRST, A CORRECTION TO THE FRAMING

**The zone watchers are not programmed to look for anything.** That is deliberate
and it is the point of the design. A zone is a change detector — 16 pixels, a
hash, a settle timer. It knows something appeared. It has no idea what.

**Everything that turns a settled rectangle into a record happens in a separate
layer, after the read.** Keeping those apart is what lets the zones survive a
patch: CIG can move every panel in the game and the zones do not care, because
they were never told where anything was.

**So the real question is not "what do the watchers look for."** It is:

    1. what lists do we hand the matcher                §3
    2. what patterns can it find with no list at all    §4
    3. what do we tell a zone to expect                 §5
    4. how does it catch itself being wrong             §6
    5. what must it refuse to look at                   §7

---

## 2. THE THREE RECOGNIZER CLASSES

Every read passes through three, in order. **A read that produces nothing in any
of them is discarded, not stored.**

**Class A — vocabulary.** The string is matched against a closed list we already
hold. This is most of the value and it is why no AI is needed. §3.

**Class B — shape.** No list required; the string is a number, a unit, a
timestamp, a percentage. Recognised by pattern. §4.

**Class C — structure.** Not the text, the layout. Is this region one panel, a
two-column table, or a scrolling list? **Determines whether names and numbers on
the same row belong together** — the single most important thing to get right,
because a name paired with the wrong row's price is worse than no price at all.

Structure is read from the glyph segmentation that §3b already performs: line
positions give rows, and a consistent column gap across ≥3 lines gives columns.
**No extra machinery. It falls out of the atlas pass for free.**

---

## 3. THE VOCABULARY PACK — everything we can hand it today

`names.dat`. All of this is already on disk, collected and gated. **Counts are
from the project record, not re-counted for this addendum.**

| list | count | source | use |
|---|---|---|---|
| item names (priced) | 7,728 | UEX | the main match target |
| item files (all) | 21,849 | scunpacked `items/` | catches anything UEX lacks |
| FPS gear records | 5,420 | `fps-items.json` | gear shops |
| ship names — game | 316 | scunpacked `ships/` | ship kiosks, spawn menus |
| ship names — live | 254 | `ship_resolution.json` | what we actually publish |
| shop / terminal names | 823 terminals, 479 item shops | UEX | shop identity |
| trade locations | 965 | `trade_locations.json` | station and refinery names |
| systems | 96 | source 1 | location |
| planets | 324 | source 1 | location |
| moons | 73 | source 1 | location |
| stations | 60 | source 1 | location |
| cities | 5 | source 1 | location |
| outposts | 117 | source 1 | location |
| positioned entities | 1,774 with x/y/z | `starmap_positions.json` | any place name on screen |
| manufacturers | 152 | sources 1/3/6 | disambiguates similar item names |
| companies | 311 | sources 1/3/6 | shop branding |
| factions | 74 | sources 1/3/6 | mission and reputation UI |
| blueprints | 1,597 | scunpacked | crafting UI |
| contracts | 5,108 | scunpacked | mission board |
| labels | 90,121 | `labels.json` | **the catch-all — see below** |
| keybind actions | 910 | `defaultProfile.xml` | settings screens |

**`labels.json` is the sleeper entry.** 90,121 strings is effectively every piece
of text CIG puts on screen. **Matching against it will not tell us what a thing
is, but it will tell us that a string is real game text and not a misread** —
which is exactly the signal needed to separate "the OCR failed" from "we found
something we have no list for." Keep it as the lowest-priority tier of the match
cascade.

### The one list we do not have

**Commodity names.** `items_prices_all.json` holds 23,734 rows and **not one is a
commodity.** The `~200 commodities` figure carried in rev 1 through rev 3 is
**mine, and unverified — treat it as an estimate, not a count.**

`trade_locations.json` records what a place produces and consumes at the level of
category tags (*"Luxury"*, *"Commodity"*), **not item names.**

**This matters more than it looks, because commodity kiosks are build step 5 —
the first real target — and we would be matching against a list we do not have.**

**Action, cheap, before any of this is built:** UEX publishes a commodities
endpoint separately from prices. **Pull the catalogue even though the prices are
absent.** It is one request and it is the vocabulary the highest-value target
depends on. **If it does not exist, commodity names have to be collected
open-vocabulary and confirmed by hand the first time** — workable, but a
different and slower design, and better to know now.

---

## 4. THE SHAPE SET — what it finds with no list at all

These need no vocabulary and work on the first run, including on screens we have
never anticipated.

    aUEC price          digits, thousands separators, optional aUEC suffix
    quantity            number + SCU / cSCU / uSCU / units
    percentage          number + %
    duration            mm:ss and hh:mm:ss
    distance            number + km / Gm / AU
    patch / build       N.N.N.NNNNN
    UTC timestamp       from r_DisplayInfo and the log
    stock state         "In Stock" / "Out of Stock" / "No Stock" / "N available"
    column headers      "Buy" / "Sell" / "Price" / "Qty" — these give class C
    rate / stat units   dps, m/s, rpm, HP, kW

**Prices and quantities are the two that matter.** Both are digit strings, which
means ten glyphs in the atlas rather than sixty, which means **they are the most
reliable thing on the screen, not the least.**

**A price that fails to parse is dropped. Never rounded, never inferred, never
carried from an adjacent row.**

---

## 5. THE PRIORS — what we tell a zone to expect

Rev 3's zone learning records *where* things appear. **These are the other half:
what we already know, handed in, so a match starts from a short list instead of
7,728.**

**The shop's own inventory, once shop identity resolves.** The strongest prior in
the design by a wide margin. Standing in Casaba Outlet, the candidate set drops
from 7,728 items to that shop's known stock. **A 20-way match is near-certain
where a 7,728-way match is merely probable.** Unmatched strings then become
genuinely interesting — they are new stock, and new stock is the thing we most
want to know.

**The patch's known item set.** A name that resolves to an item which does not
exist in this patch is either a misread or a genuinely new item. **We can tell
which:** if the string matches nothing in the current patch but matches something
in the previous one, it is almost certainly a misread of a familiar name. If it
matches nothing anywhere, hold it for review.

**The player's own loadout, from the log.** Proven — 249 of 298 ClassNames join
across 225 sessions. **The inventory and character panels are therefore
predictable before they are read**, which makes them the ideal calibration
target: we know the answer, so a wrong read is measurable rather than invisible.

**Resolution and UI scale.** Selects the atlas. Read once at startup from the
window, not guessed.

**Location, from the log.** Narrows place names to the current system.

---

## 6. THE SELF-CHECKS — how it catches itself being wrong

**Standing rule 12: a check that cannot fail is not a check.** Each of these can
fail, and each fails in a way that names its own cause.

**Known-shop agreement rate.** At a shop whose stock we already hold, record what
fraction of read rows match that stock. **A drop has two possible meanings — the
shop changed, or reading broke — and they are distinguishable:** if the
unmatched strings match *some* item in the catalogue, the shop changed and that
is a finding worth having. If they match nothing at all, reading broke.

**Price plausibility.** A read price more than 10x or less than 1/10 of the last
known price for that item is **held for review, not published and not
discarded.** A tenfold move is either a misread digit or a genuine repricing, and
both are worth a human look.

**Patch agreement.** The patch string read off screen must equal the patch from
the log. **A mismatch means we are reading a stale frame, or the wrong window
entirely** — the failure most likely to poison data silently, and it costs one
comparison to catch.

**Dead zone report.** A zone that has produced no match in ten sessions is either
covering nothing or sized wrong. **Report it. Do not silently keep polling** —
that is the shape of the handoff-watcher defect this project has already hit
three times.

**Atlas confidence drift.** If the mean per-glyph score falls session over
session, CIG changed the font or the UI scale moved. **Surface it as a finding
before the data degrades**, rather than after.

---

## 7. THE ANTI-DICTIONARY — what it must refuse to look at

**Hard exclusion, not filtering.** A filter can fail open; an excluded zone is
never read, so there is nothing to leak.

**Zones overlapping the chat region are never sampled.** Not read and discarded —
**never read.** Set at first run, part of consent.

**A zone whose text matches the chat shape** — timestamp, name, colon — **has its
entire output dropped, and the zone is muted for the rest of the session.** Not
just the offending line.

**Any string that matches a player-handle shape and no vocabulary entry is
discarded**, never held for review, never written to a crop.

**Never recognised, at all, by design:** other players' names, party and org
lists, friend lists, shard ids, session ids, anything under `[Social]`,
`[Login]`, `[Network]`.

**This is the section to hand a friend when they ask what it does.** It is the
answer to that question.

---

## 8. WHAT TO POINT IT AT — ranked by what we are missing

| # | target | what we hold now | why here |
|---|---|---|---|
| 1 | **commodity prices** | **zero rows** | largest hole; blocks the whole crafting surface |
| 2 | **stock levels / availability** | nothing | nobody has this, and it is the question players actually ask at a kiosk |
| 3 | **shop identity per visit** | 479 shops, no in-game confirmation | halves the metadata problem for every other target |
| 4 | **price freshness** | 23,734 rows, median 66 days old | the site's whole confidence position rests on this number improving |
| 5 | **refinery rates and yields** | nothing | not in any file; only observable |
| 6 | **rental prices** | nothing | small, easy, entirely absent |
| 7 | **fuel prices** — hydrogen and quantum | nothing | changes by station, nobody tracks it well |
| 8 | **mission reward values** | 5,108 contract definitions, no live payouts | definitions are static, payouts are not |
| 9 | **item stats shown on the kiosk** | game files | a cross-check on source 1, not new data |
| 10 | **item images** | **zero, of 7,728** | see §9 |

**Rows 1 through 4 are the build. Rows 5 through 10 come free** — the same zones,
the same atlas, the same vocabulary, pointed at a different screen.

---

## 9. THE IMAGE QUESTION — flagged, not answered

**Rev 3 already saves a ~200x40 crop per row, for provenance.** A crop of an item
row on a kiosk is, incidentally, **the first image of that item this project has
ever held. Coverage today is zero of 7,728.**

**Worth noting and not acting on:** the description-rights problem
(`claude/finding-description-rights-correction.md`) turns on RSI ToS §XIII.D
granting *images, graphics and artwork* — **and not text.** Screenshots fall in
the granted class rather than the excluded one.

**That is an observation about which clause applies, not a clearance.** I called
the description question wrong once by not checking before asserting, and I am
not repeating it. **Rule 8 puts this with Sleven. Capture the crops for
provenance regardless — they are needed for review either way. Publish nothing
until it is ruled on.**

---

## 10. NOT VERIFIED

- **The commodity name list.** §3. The `~200` figure is mine and unverified, and
  the list itself may not exist in anything we hold. **Check before step 5.**
- **Whether shop stock is stable enough for the §5 prior to help.** If stock
  rotates heavily, the prior is weaker than claimed.
- **Whether column detection survives a scrolling list**, where rows enter and
  leave mid-frame. Class C is the least tested idea here.
- **Whether the chat region is at a fixed position** across UI scales. If it is
  not, §7's hard exclusion needs to be drawn by the player at first run.
- **Whether `labels.json` matching is fast enough at 90,121 entries** to sit in
  the read path. If not it moves to the review step, where time is free.
