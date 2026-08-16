# FINDING — what the three concrete cases actually needed

    built by  Code, 2026-08-16, to
                docs/DECISION_hull-configuration-acquisition-2026-08-16.md
    status    the three cases exist and are derived from data.
              THE SHARED SHAPE IS NOT PROPOSED HERE. That is Sleven's next
              decision, and this document is the input to it.

Everything below is measured from `configurations.json`, which
`build_ship_configurations.py` derives from the 20260801T204744Z game snapshot,
the 20260801T235530Z UEX snapshot, and the site's own published rows in
`releases/latest.html`. Nothing is hand-entered.

---

## The three cases, as built

| case | configuration | what it turned out to be | routes |
|---|---|---|---|
| Drake Clipper | stock | — | shop (5 terminals, 3,619,730 aUEC), pledge ($150) |
| | Wikelo War Special | **6 components swapped**, 0 placeholder noise | trade *(unverified)*, factory |
| Aegis Tiburon | stock | — | shop **not available**, pledge ($775) |
| | Wikelo reward (4.11) | **not in any file** | trade *(unverified)* |
| Aegis Sabre Firebird | stock | — | shop (New Deal Lorville, 5,580,410 aUEC), pledge ($185) |
| | Wikelo War Special | **7 components swapped**, 4 placeholder differences excluded | trade *(unverified)*, factory |

---

## What each case forced into the shape

### 1. A hull needs two identities, not one

The site calls it **Clipper**. The game files call it **Drake Clipper**. The UEX
price rows call it **Clipper**. Joining on either name alone fails on one of the
three sources every time, so a hull record carries both and the join is stated
rather than guessed.

This is not new — `ship_resolution.json` already records that suffix matching is
insufficient ("Starfighter Inferno" vs "Ares Inferno") — but it lands directly
on the hull layer.

### 2. `component_changes` MUST be nullable, and this is the finding that matters

Case 2 exists to make this fail, and it did.

- The Clipper's Wikelo config: `component_changes: [6 entries]`
- A stock config: `component_changes: []`
- The Tiburon's 4.11 config: **`component_changes: null`**

An empty list says *nothing is changed*. That is a claim, and for the 4.11
Tiburon it is a false one — nobody knows what it changes, because CIG has not
shipped the file. Collapsing "no changes" and "not yet known" into the same
empty list would publish an invented fact on the first page it reached.

**A shape that cannot say "not yet known" will be wrong every time a patch is
announced**, which by CIC's reading is every patch.

### 3. `available` and `verified` are two different questions

The Wikelo route is `available: true, verified: false`. Both halves are true at
once and neither can be dropped:

- CIG's roadmap says these ships are a Wikelo reward. That is a statement by the
  publisher, not a row in a file.
- The three Wikelo Emporium terminals in UEX are typed `fuel`, and no vehicle
  price row references any of them. Nothing we hold can confirm or deny it.

So every route carries who said so and what the evidence was. `verified: false`
carries an explicit `why_unverified` naming what would settle it: someone going
there in game.

### 4. An absence needs to say which kind of absence it is

The Tiburon returns `shop: available: false, verified: true` — verified because
the check ran and found nothing, not because the ship is known to be unbuyable.
The record carries the note out loud:

> an absence in this snapshot, not a claim that it can never be bought — a
> terminal added after the pull would look the same from here

Two independent sources agree on it, which is worth having: UEX has no price row
for the Tiburon, and the site's own row says `status: pledge_only`, `dealers: []`.

### 5. A configuration can have a livery it cannot name

CIG's roadmap says the reward carries "a unique base livery". No file marks any
paint as belonging to an edition. The Clipper has 7 named liveries and the
Tiburon 4, all attaching mechanically through `required_tags` — and picking the
likeliest-sounding one would be a guess published as fact.

So the livery field records: *stated by the roadmap · not identified in files ·
here are the candidates*. The question stays open in the data instead of being
closed by the builder.

### 6. Routes attach to the configuration, and the hull has none

This came out of the build rather than being imposed on it. Shop and pledge
attached to **stock**; trade and factory attached to the **Wikelo config**. At
no point did a route want to live on the hull. The ruling's third layer holds.

---

## Two corrections to the earlier finding

**1. "11 of 67 slots refitted" for the Sabre Firebird overstates it.** Four of
those eleven are `<= PLACEHOLDER =>` on both sides — CIG's own placeholder
entries whose class names differ while both remain placeholders. The real figure
is **7 components swapped**. The builder excludes them and counts them
separately rather than dropping them silently, because a page whose whole job is
to answer "what does the War Special actually give me" must not inflate the
answer by four.

(The 67 and my 109 are different denominators: the earlier count was of
component slots, mine is of every port in the loadout tree. Both are stated with
their method rather than reconciled by adjusting one to match.)

**2. The 4.10 Clipper reward is already in a 2026-08-01 snapshot.**
`DRAK_Clipper_Collector_Military` is in the game files we pulled two weeks before
CIC read the 4.10 roadmap entry. The configuration files land ahead of the
patch. That is useful: the 4.11 Tiburon config will probably appear in a snapshot
before it is obtainable, and a `component_changes: null` will become a real list
without anything else about the record changing.

---

## What is NOT here, deliberately

- **No schema.** No table, no migration, no field on `Ship`. The ruling forbids
  designing one before these cases exist, and they now exist.
- **No generalisation over the other 86 game-only files.** Three cases were
  ordered; three were built.
- **Nothing published.** The dealer matrix is untouched, no page reads this yet,
  and nothing was deployed.

## Where it lives

    build_ship_configurations.py                     the builder
    data-layer/derived/ship-configurations/          configurations.json + MANIFEST
    checks/_verify_ship_configurations.py            12 checks, every one driven
                                                     with input that must fail it

The verifier proves the diff can fail in both directions (a real swap is found;
a ship against itself, a reordered file, and placeholder churn all report
nothing), that the shop route answers no when there is no data and yes when
there is, and that a missing site row **stops the build** rather than quietly
reporting "no pledge price" for a ship that costs $150 — which is what the first
version of it did.
