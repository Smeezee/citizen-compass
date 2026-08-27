# Update — /loadout is on the real 316-ship dataset and deployed. 20:40, ahead of the 22:00 target.

```
bf95d98..(uncommitted)   deployed to the testing worker
Version ID b3311e5b-58eb-4bb4-a3fa-bb4058684c5a
ALL 5 LIVE ASSETS BYTE-FOR-BYTE IDENTICAL TO _deploy
```

## §7's numbers

**File size: 431 KB** (`loadout_data.gen.js`). Well under the ~2 MB line, so
per-ship splitting is NOT the next job.

It was 659 KB before two corrections dropped it to 421: turret MOUNTS were
being emitted as weapons (471 statless entries offering themselves as
alternatives to real guns), and CIG's own PLACEHOLDER rows were being shipped
as components.

**Ships, by category rather than as one number:**

```
316  in the snapshot
310  have a loadout
  6  have none, and say why  - 5 ATLS variants and a Power Suit. Exosuits, not
     ships. CIG models them as vehicles; they have no weapons, shields or
     drives because they are something a person wears.
 33  on the site with no game file - every one already flagged pledge_only.
     Listed on the page, disabled, saying "not released yet - CIG has not built
     this ship, so it has no components to show".
470  components emitted, from 5,384 items
```

**The match rate against CIG's own aggregates: 275 agree, 0 disagree.**

That is every ship CIG publishes a `PilotSustainedDps` for, and it reproduces
the 275/275 in `FINDING_ship-aggregation-rules-proven-2026-08-08` from an
independent implementation.

**It did not start there.** My first pass reported 214 agree / 61 disagree,
with the RSI Perseus at 16,596 DPS against CIG's 1,494 and the Polaris at
11,984 against 1,116. That was not a disagreement with CIG - it was a naive sum
adding every manned turret's guns to a figure that means "what the PILOT can
fire". Applying the proven `IsPilotSlaveable` outermost-lock rule took it to
275/0. The page applies the same exclusion, so a customised build stays
consistent with the stock figure.

## What surprised me in the data

**All 81 coolers had no cooling figure.** The resource network carries three
kinds of delta, not two: a cooler CONVERTS power to coolant - consuming at
`Rate`, producing at `GeneratedRate` - and I was only reading Consumption and
Generation. Every ship on the site would have rendered as overheating.

**There is no top speed anywhere in this snapshot.** `StanceSpeed` is null,
`Physics` is null. The mock computed speed as `base - (ehp-hull)/900`, which is
invented arithmetic on an invented base figure. Per §5 the stat is **gone**
rather than estimated, and the page says why.

**`Health` is real hull HP** (29,760 on a Cutlass Black) and present on 307/316.
I had first mapped `hull` to `Mass`, which would have made "Effective HP =
hull + shields" a confident number meaning nothing.

## Prices: deliberately absent, and the page says so

The mock invented `pr`, `shop` and `loc` for every component and drove a whole
"what build B costs and where to get it" section from them. **Those are market
data. They are not in the game files**, and the only price source in the repo
(uexcorp) has no proven join to these items - it is not among the joins the
research finding validated.

So the section now lists what build B **changes**, and states plainly: *"No
prices, and that is deliberate... Showing a made-up number would be worse than
showing none."* The "Cheapest" sort went with it; Best and Quietest remain.

This is the first page where a visitor reads a number and acts on it.

## Provenance, on the page

Header chip: `snapshot 20260801T204744Z · patch 4.9`. A source note states the
snapshot, the counts, that stock totals are CIG's own and customised ones are
ours, that our sum reproduces CIG on all 275, and what is absent and why.

## Verification

```
_verify_loadout_data.js   11/11, and --prove rejects known-bad (registered as a build gate)
build_deploy.py           7 gates + inline JS parse, clean
check_deploy_clean.py     clean
headless render           310 of 310 ships, no throw, no NaN/undefined
```

**The render harness was wrong first and I nearly believed it.** It set
`ctx.shipId`, which does nothing - `shipId` is a `let` in the page's scope, not
a vm context property - so it rendered the DEFAULT ship 310 times and reported
"310 ships rendered". The Cutlass numbers not matching the data is what exposed
it. It now exports a setter from inside the page scope and asserts the change
took.

Rendered output for a real ship, which is the thing nobody had seen before:

```
Drake Cutlass Black
  Sustained DPS   1,305    CIG's own figure
  Effective HP    36,960   hull 29,760 + shields 7,200
  Quantum range   165.1 Gm
  Weapons: 2x CF-337 Panther Repeater (Klaus & Werner),
           2x Mantis GT-220 Gatling (Gallenson Tactical Systems)
```

## NOT committed

Rule 2 - no go-ahead in this session for these files. Deployed but unpushed,
which is the state the order's own §8/§9 implies is fine to report from.
