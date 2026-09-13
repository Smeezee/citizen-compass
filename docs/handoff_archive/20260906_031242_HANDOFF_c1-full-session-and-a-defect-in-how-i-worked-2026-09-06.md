# HANDOFF — everything from C1's session of 2026-09-05/06, and first, the defect in how I worked that Sleven stopped me for.

    from      C1 (Cowork), 2026-09-06, filed on Sleven's instruction to stop and
              package immediately.
    for       the next C1, Code, C3, and Sleven
    status    NOTHING COMMITTED, NOTHING PUSHED. Testing deployed and green.
    scope     complete session state. Read section 1 before anything else.

---

# 1. THE DEFECT IN HOW I WORKED. READ THIS FIRST.

**Sleven stopped this session because I kept re-opening settled ground and
presenting each re-opening as progress. He is right and the record proves it.**

## 1.1 The count

**Eleven documents filed in one session. Four of them correct another one of
mine from the same session.**

    RULING_the-5-percent-threshold-is-vacuous-...        my ruling
    ERRATUM_the-threshold-was-never-vacuous-...          corrects that ruling
    FINDING_the-5-percent-threshold-measures-the-sampler correcting it a THIRD time

    DESIGN_the-fact-store-is-mostly-already-built        my design
    ADDENDUM_the-log-miner-is-the-first-writer...        corrects that design
    ADDENDUM_the-match-targets-before-you-measure-a-zero corrects the addendum

**Three passes on one threshold. Three passes on one collector design.** Each
pass was individually honest and each was reported to Sleven as a finding. From
where he sits that is the same subject arriving four times wearing different
hats.

## 1.2 The mechanism, named so the next session can catch it

**I wrote before I measured, then measured, then filed a correction — and
counted the correction as output.**

- The 5% ruling asserted "no hull gets within 3x of the threshold" from ONE
  number on ONE line of ONE file. Ten minutes of measuring first would have
  produced one correct document instead of three.
- The collector design proposed a name-shape CHECK constraint. A comment written
  three weeks earlier in `gamelog_mine.go:211` forbids exactly that and predicts
  the exact mistake. **Reading the collector before designing for it would have
  produced one correct document instead of three.**
- The §8 match test compared 992 ship class names against a table that has no
  class-name column. The strings were on disk the whole time.

**The rule for the next session: measure, THEN write. A document that corrects
your own document from the same day is not progress, it is the first document
having been written too early.**

## 1.3 What this is NOT

It is not Code. Code stopped correctly three times, refused to widen a threshold
when widening was easier, caught his own rule-17 substring match, and found his
own new assertions wanting in the same update that shipped them. **Every one of
my four wrong numbers this session was caught by a check or by Code, not by me.**

## 1.4 SETTLED — do not re-raise, do not re-derive, do not re-litigate

Beyond the standing CLOSED list (rights, credentials, Fan Kit, going live,
Constellation landing gear, the Cyclone/Centurion wheel work, the see-through
marks):

- **The 5% threshold.** Three documents exist. The finding is final: it measures
  the sampling stride. **The fix is specified and queued. Do not re-measure it.**
- **G3 gains 3 ships, not 5.** Settled twice. Code's number, by construction.
- **The collector is a rebuild that carries over what worked** — Sleven's ruling
  2026-09-06. Not an open question.
- **The observations table design** is final as amended by both addenda. **Do
  not produce a fourth collector design document.**
- **The Fury is not fixed and its cause is unknown.** Do not re-attempt from
  geometry alone; three attempts failed for a structural reason.
- **The San'tok.yāi handedness** is recorded, allowed, and open. Do not
  re-derive it.

---

# 2. WHAT IS TRUE RIGHT NOW

## 2.1 Testing is deployed and the sweep is green

    120 ok, 0 failed, 3 skipped, 0 NOT RUN, 1885s
    receipt 2026-09-06T02:09:38   fingerprint 53676ee77da95f1f
    Version ID de3a43f1-f3cd-4b5b-bba5-ea408f992337
    524 files, 517.9 MB, 256 models

**First fully clean sweep in this repo.** Deployed WITHOUT rebuilding first, on
purpose: a rebuild changes the payload fingerprint and invalidates the receipt,
so the gate would then refuse.

**One file changed on the wire — `/loadout_marker.gen.js`.** 523 of 524 were
already up. **C1 verified the shipped file independently rather than reading it
off Code's report (rule 16): sha256 `a6cf733fa0584764`, 289,793 bytes, served and
local identical.**

**Nothing committed, nothing pushed. 385 files modified in the working tree.**
Rule 2 — Sleven's explicit go-ahead is what commits this and he has not given
one. No `git add -A` was run. Netlify untouched.

## 2.2 The five checks and who closed what

**Code:** `_verify_g3_matcher_delta.py` and `_verify_stage_floor.mjs` re-pinned
**to names rather than counts** — a count moves whenever a hull is decoded, so it
goes red for a non-defect and the fix each time is to type a bigger number.
`_verify_hardpoint_join.py` split in two, mutation-proven.
`_verify_placer_candidates.py` — 7 box-fix hulls declared by name **after he
caught himself matching them by substring**, which is rule 17, and redid it
against `matched.json` on exact equality. `_verify_holo_render.mjs` — Step B on
the Liberator plus a separate ratio control.

**C1:** `_verify_marker_census.py` — **8 declarations removed**, six restored to
baseline exactly, two now ABOVE it (Tiburon 57→65, Mantis 12→18) where
`compare()` never routed them to `declared` at all. **NOT rebaselined** — that
would absorb the Perseus's 40 torpedo ports and four vanished hulls. Six still
fire. Old file at
`_to_delete/marker_census.json.pre-c1-declaration-clear-20260906`.

**`_verify_child_markers.py` is now split by PROVENANCE and the half that matters
got stricter.** Every marker that moved is `est`; **not one `cig` coordinate
moved anywhere in the fleet**, and the Polaris's 21 held exactly. So pinning
eleven coordinate triples was the wrong shape — an estimate is RECOMPUTED by
design when the box changes. The rule is now **"NO MARKER LABELLED `cig` MOVED —
and nothing may excuse one"**, checked BEFORE any exception so no entry can reach
it, plus a named `REESTIMATED` hull list that refuses an entry firing on nothing.
Both new assertions proven able to fail: `--mutate-move-cig` moves a `cig`
coordinate **on a hull that IS in the exception list** and goes red; a bogus
REESTIMATED entry is refused as fiction. 19 assertions, 0 failed.

**`_verify_child_markers.py` and `_fixtures_markers/` were on nobody's list —
the FIFTH ownership gap found the same way — now claimed in OWNERS.md.**
`checks/_verify_owners.py` passes.

## 2.3 The San'tok.yāi — open, recorded, not resolved

All ten of its `est` markers moved and **nine are a mirror across X** (port 26
−0.90584 → +0.90610; port 42 −0.69813 → +0.69836). **Two pairs exchanged places:
port 44's new position is 0.0059 from where 69 was; port 57's is 0.00039 from
where 46 was.** Its estimated left and right are now reversed. Allowed — it has
no `cig` markers at all, being one of the four refused for orientation on
2026-08-28 — but **nobody has established which handedness is right.**

## 2.4 The 5% threshold — FINAL, do not re-measure

Ran the control unmodified once per hull, 150 hulls, `CC_GEO_DIR` pointed at each
alone. **Not 14 hulls over. 50 of 150.** Which ones fail is decided by
`stride = count / sampled`:

    stride 1  n=  5  over: 4 (80%)      stride 5  n= 14  over: 0 ( 0%)
    stride 2  n= 29  over:20 (69%)      stride 6  n= 15  over: 2 (13%)
    stride 3  n= 34  over:19 (56%)      stride 7  n= 18  over: 2 (11%)
    stride 4  n= 19  over: 1 ( 5%)      stride 8  n=  7  over: 2 (29%)

**80% to 0%, monotonic.** Correcting for stride REVERSES it — raw mean depth 16.0
failing vs 11.0 passing, **stride-corrected 42.2 vs 56.5**: the flagged hulls are
physically the LESS dense ones.

Second factor is aspect ratio: a fixed 320×320 grid normalised by the LONGEST
axis, so a long thin ship piles into few cells. **Caterpillar worst at 20.88%,
covering 2,198 px of 102,400**, and all three Caterpillar variants return
byte-identical figures because they are the same mesh.

**`w < 5` as a per-hull absolute claim is not sound fleet-wide. Within one hull
it is completely sound**, which is the regime Code's Step B control uses —
Liberator 1.63% shipped vs 8.34% with the pre-pass removed — **so that control is
correct and unaffected.**

**QUEUED FIX:** make `cell[i]` stride-invariant; re-derive the threshold from the
Liberator as a MULTIPLE, not a bare percentage; keep the absolute per-hull
assertion OFF until then. **108 hulls unscanned and not claimed.** Code's 14 vs
this 50 is unresolved — one look before either is quoted.

## 2.5 The front page — the thing Sleven actually asked about

**Nothing failed to deploy. The site looks unchanged because the new page was
never built.** `docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md` was
written six days ago, marked "NOT QUEUED", and **appears nowhere in `NEXT.md`.**
That is C1's failure, not a pipeline fault.

**AND THE OLD PAGE IS PRINTING WRONG PRICES ON 47 SHIPS.** Verified in the served
build:

    "name":"100i", "auec_price":1089270,
    "dealers":["New Deal","Astro Armada"], "confidence":"verified"

    ship_dealer_prices.json:  New Deal 1,089,270   Astro Armada 1,146,600

**Wrong by 57,330 aUEC and labelled `verified`.** The 890 Jump is out by
3,267,800. **Corrected data has been on disk since 2026-08-31** —
`data-layer/derived/ship-prices/ship_dealer_prices.json`, 63 ships, exact mapping
to our five dealer names, zero unmapped, zero conflicts — **and nothing reads
it.**

**Ordered in three steps that each ship alone:** per-dealer prices into `SHIPS[]`
with `auec_price` kept as the CHEAPEST (an absent price and a copied one are
different facts — do not spread one across shops); **the control that has never
existed** — nothing anywhere checks that a ship's stated price is the price at
the dealer printed beside it, which is why this survived in plain sight; the
empty state for the 9 ships with no picture. **`data-layer/derived/ship-thumbs/`
is cited by the spec and is NOT on disk — find it or declare it gone.** The wall
gets its own order. Map tab on hold pending CIC.

## 2.6 The collector — Sleven's ruling and the design, FINAL

**Ruling 2026-09-06:** *"it's a complete rebuild because we're gonna be building
a program, not a set of things working in the background... we're gonna take the
basic things that did work with the collector, and we're gonna redesign them into
this more advanced program that will grow."* **New program structure; the proven
parts carried in as designed modules. The trigger layer dies.**

**Measured, carried in:** 575 selftest checks 0 failed (Windows 2026-08-27),
working Windows.Graphics.Capture (756 frames), service install, autostart,
consent gate, scrub, export, and the log miner. Old program is **27,822 lines of
Go across 92 files, 37 of them selftests.**

**Dead:** the trigger system. **426 of 756 frames are labelled `terminal_open` or
`terminal_scroll` and the ones opened show a seat interior, a chat window and the
quit-to-desktop dialog. Not one shows a shop panel.**

**The font question is ANSWERED: readable.** Legible off the captures: `Zone:
DRAK Vulture 761884332511`, `IRON (ORE) 722.3m`, `98% H-FUEL / 19% Q-FUEL`, and
the whole debug overlay — which prints patch `4.9.188.23497`, build, server,
player location and UniverseTime **on the frame**, so provenance is free.
**Player names are visible in chat, which is why chat is not a readable panel.**

**THE MOST VALUABLE HALF IS ALREADY BUILT AND IT IS NOT THE CAMERA.**
`gamelog_mine.go` (71 KB) reads `Game.log` and its `logbackups` archive — no OCR,
cannot be misread, matches on PAYLOAD SHAPE never on class name (which is why it
survived CIG renaming `CEntityComponentShopUIProvider` to
`...ShoppingProvider`). From `captures/gamelog-dataset.json`, schema 3:

    ship_classes 992   equipment_seen 542   quantum_routes 57   contracts 55
    locations 44   subsystems 71   deaths 131   shop_class_names 18
    builds 34   mission_payouts 16   sent_txn_keys 308

**The 308 transactions carry `shopName`, `itemName`, `client_price`, `quantity`,
`currencyType` and were SENT and cleared rather than stored anywhere queryable.**
So **the log miner is the first writer into `observations`, and the screen
reader's job is what the log does NOT emit** — a shelf price nobody bought, a
stock level, a panel walked past.

**THE FACT STORE IS 80% ALREADY IN THIS DATABASE.** `snapshots` + `item_prices`
is append-only, keyed by snapshot so a second pull ADDS rows, and
`snapshots.source` was written generic on purpose. **The gap: `item_prices` needs
ids and the collector reads STRINGS**, and rule 17 forbids bridging that by
similarity.

**Ordered (not started):** `observations` (strings verbatim, append-only, **no
image column and no path column**, `source_kind IN ('gamelog','screen')`,
`panel_key` nullable with `CHECK (source_kind='screen') = (panel_key IS NOT
NULL)`); `observation_links` (UNIQUE per observation, `method IN ('exact')`); an
exact-equality resolver where **zero matches is a normal permanent state** and
**two matches is refused and reported, never picked** (rule 19).

**THE NAME RULE IS AN ALLOW-LIST, NEVER A DETECTOR.** C1 proposed a CHECK
constraint refusing handle-SHAPED strings. `gamelog_mine.go:211` forbids exactly
that under **THE GOVERNING RULE FOR EVERYTHING DERIVED FROM ANYTHING — Sleven,
2026-08-13**: handles look like ordinary words, so any heuristic either misses
real ones or eats legitimate shop and item names, and **both failures are
silent**. Same shape as `mineTxnKeep`: a rectangle not named in the panel table
is never read; a field not named is never written. Chat, contacts, party and
friends are never named.

**THE MATCH TARGETS — corrected before anyone measures a zero.** The log's names
are not display names:

    ship_classes      AEGS_Avenger_Stalker        equipment  987_jacket_01_01_01
    locations         Nyx_Levski, GrimHEX         shop_class_names are C++
                      INVALID_LOCATION_ID          method names — NOT shops

    equipment_seen        -> components.class_name   (exists, unique) MEASURE THIS
    transaction itemName  -> shop_items.name         MEASURE THIS
    itemClassGUID         -> report whether ANY table holds a CIG item GUID
    ship_classes          -> NO TARGET COLUMN EXISTS. ships has name;
                             ship_registry has ship_code/source_slug/folder_slug.
                             992 real class names have nowhere to land. REPORT,
                             do not add the column in a collector order.
    locations             -> compare, expect low, exclude INVALID_LOCATION_ID

**A low number is not permission to loosen the matcher.** Rule 17 has no
threshold below which it stops applying.

---

# 3. OPEN, IN PRIORITY ORDER

1. **The front page.** Prices → the price control → the empty state. Ordered, not
   started. **This is the only item Sleven has asked about by name.**
2. **The collector database half.** Ordered, not started.
3. **The 5% metric fix.** Specified. Do not touch while the current sweep receipt
   holds the deploy open.
4. **Section 5 tests one hull and prints as if it tested the fleet.**
5. **The ordering dependency (Code's finding, the biggest of the night):** any
   control reading a build artefact it does not rebuild reports on whatever the
   last build left. `_verify_child_markers.py` passed at 00:36 and failed at
   01:07 with no data change — controls run alphabetically and three later ones
   run builds. **Its green was worth nothing.** Not patched; the general shape is
   a question about sweep ordering.
6. `_verify_placer_candidates.py` raises a bare `FileNotFoundError` where NOT
   PERFORMED belongs.
7. **30 ships have a model shipped that no visitor can reach** — raised
   2026-09-04, not authorised.
8. The San'tok.yāi handedness.
9. The `#ivo` decoder still does not produce a ship.
10. **`tools/ivo/` is not in git** — untracked, not ignored. Flagged, awaiting
    go-ahead.

---

# 4. STANDING CONSTRAINTS — unchanged, restated because a handoff is where they
# get lost

Testing only; the live site is never deployed to without an explicit unambiguous
instruction. **When Sleven says "live site" in speech he means TESTING.** No
`-IgnoreSweep`. **Nothing commits or pushes without his explicit go-ahead; never
`git add -A`.** Never delete — `mv` to `_to_delete/`. **NO FUZZY MATCHING
anywhere.** Rights and credentials are CLOSED. Do not fetch anything under
`/media/` on robertsspaceindustries.com. Fan Kit compliance is Sleven's alone —
report gaps, never fix them. **A frame may contain a name; nothing derived from
that frame ever may.** Do not make the R2 bucket public; no list/read/delete
route on the Worker; do not remove `send_url`/`send_key`; do not auto-send.
**Rule 25 OUT OF SCOPE:** `testing/_src/_inspect.src.html`,
`testing/_deploy/_inspect.html`, `docs/contact_sheet_*/`.

---

*C1, 2026-09-06, filed on instruction. Section 1 is the part I would most want
the next session to read and the part I would least want to have written.*
