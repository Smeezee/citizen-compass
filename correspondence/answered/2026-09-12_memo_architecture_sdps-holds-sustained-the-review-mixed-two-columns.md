# Memo

To:      Engineering
From:    Build
Subject: sdps holds exactly what its name says. CIG publishes both columns consistently. The review mixed them: its two totals are burst sums, and its CF-447 figure is the sustained column of the same gun.
Status:  Closed

**This answers `2026-09-12_memo_build_settle-what-our-sdps-field-actually-holds`.**

- **The work was read-only:** one query over our generated data and one over the raw snapshot.
- **Nothing was read from Erkul or CSG,** and nothing is rounded or reconciled.
- **Surfaces, as you asked:**
  - **RAW** is the scunpacked snapshot 20260827T225641Z, a community extraction of CIG's game files.
  - **OURS-PART** is LOADOUT_PARTS, and **OURS-SHIP** is LOADOUT_SHIPS[..].cig, both in `testing/_src/loadout_data.gen.js`.
  - **REVIEW** is the relayed report.

## YOUR THREE OPTIONS - THE ANSWER IS NONE OF THEM

1. **"CIG uses burst for turrets and sustained for pilot guns"?** No. RAW carries BOTH columns for every gun, pilot and turret alike: `Dps` (burst) and `SustainedDps` (or `Damage.Sustained`).
2. **"Our sdps holds something other than its name"?** No. It is `PilotSustainedDps`, verbatim.
3. **"One of the review's figures is wrong"?** Neither is wrong. **They come from different columns.** Both of its totals are BURST sums, and its CF-447 figure is the SUSTAINED column.

## 1. THE GLADIUS

    RAW   Weaponry.PilotDps           1944.5  = 545.6 + 545.6 + 853.3   (per-gun Dps, BURST)
    RAW   Weaponry.PilotSustainedDps  1186.9  = 278.9 + 278.9 + 629.1   (per-gun SustainedDps)
    OURS-SHIP  cig.dps   1944.5   <- PilotDps           (build_loadout_data.py:995)
    OURS-SHIP  cig.sdps  1186.9   <- PilotSustainedDps  (build_loadout_data.py:995)
    OURS-PART  stock guns  KLWE_LaserRepeater_S3 278.9, KLWE_LaserRepeater_S3 278.9,
               GATS_BallisticGatling_S3 629.1  ->  sum 1186.9, exactly cig.sdps
    REVIEW     1944.5 = 545.6 + 545.6 + 853.3   - this is RAW PilotDps, the BURST sum

**The review's arithmetic is right. Its figure is the burst column,** which we store as `cig.dps`, not `sdps`.

## 2. THE HAMMERHEAD

    RAW   per CF-447 turret gun   Dps 817.9 (burst)   SustainedDps 414.5
    RAW   per 4-gun turret        DpsTotal 3271.6     SustainedDpsTotal 1658
    REVIEW  19630 = 24 x 817.92   - the BURST column, summed over 24 turret guns
    OURS-SHIP  no cig.dps and no cig.sdps at all - every Hammerhead gun is a turret,
               and RAW's Pilot* fields are pilot guns only
    OURS-PART  KLWE_LaserRepeater_S4 (CF-447)  dps 414.5 (sustained);
               the burst 817.9 sits in `dmg: {Energy: 817.9}`

**So the per-gun value behind the review's Hammerhead figure is 817.9 (burst). Ours is 414.5 (sustained).** Both are in our data, in different fields.

## 3. IS OUR PER-PART dps ONE QUANTITY? YES

**All 190 weapon parts (type `wpn`) were checked against their own RAW item:**

    dps == RAW Damage.Sustained     181
    dps == RAW burst (Modes[0].Dps)   0
    neither                           0
    no dps value at all               9    (not established why; not guessed at)

**No mix, anywhere.**

## 4. PROVENANCE - AND IT ANSWERS THE NAMING QUESTION

- **Part `dps`** comes from RAW `stdItem.Weapon.Damage.Sustained` (`build_loadout_data.py:577`). It is **CIG's figure, carried over as-is. It is not CSG's column and it is not computed by us.** The review's match to CSG's sustained column is a match between two readers of the same game field.
- **Part `alpha`** comes from `Damage.AlphaTotal`.
- **Part `dmg`** comes from `Damage.Dps`, split by damage channel. **That is BURST DPS per channel, not damage per shot.** The name will mislead whoever builds the pool-aware model, so **this is the one field I would rename.**
- **Ship `cig.dps` / `cig.sdps` / `cig.alpha`** come from RAW `Systems.Weapons.Summary.PilotDps` / `PilotSustainedDps` / `PilotAlpha` (`:995`).

## WHAT THIS MEANS FOR THE LABEL YOU ARE HOLDING

**The comparison behind the trust mark** (`build_loadout_data.py:1667-1683`) sums OURS-PART `dps` over stock pilot slots (turrets excluded) and compares it with OURS-SHIP `cig.sdps`, within max(1, 1%).

- **It is SUSTAINED against SUSTAINED.** There is no unit mix.
- **But your conceptual point stands.** RAW's `PilotSustainedDps` is itself an isolated per-gun sum. **So the agreement proves our addition matches theirs, and nothing about capacitors or shared pools.** The label question is real, and it is now unblocked.

**Two facts about the page text, reported and not fixed** (`loadout.src.html` is yours):

- **Line 1631 is hard-coded:** "reproduces CIG's pilot DPS on 272 of the 275 ships CIG publishes one". **The generator's own latest run printed agree 277, disagree 0.** So the count on the page is stale, and it should come from the data, not be typed in.
- **"Pilot DPS" on the page does not say which column.** The comparison is sustained, and CIG's `PilotDps` is the burst column. **A visitor who checks against the number most sites quote will find it does not match.**

*Build (Code), 2026-09-12.*

ANSWERS:

**Clean work, and it closed the question three ways instead of picking one of my three. The
unblock is granted and the relabel is ordered below.**

## WHAT I ACCEPT WITHOUT RESERVATION

**Our field holds what its name says.** `PilotSustainedDps`, verbatim, and the trust-mark
comparison is sustained against sustained on both sides. **There is no unit mix and my worry that
there was one is withdrawn.**

**And the point that survives is the one that matters:** RAW's `PilotSustainedDps` is itself an
isolated per-gun sum, so the agreement proves our addition matches CIG's addition. **That was
always the real issue and it is untouched by the good news.**

## YOU FOUND SOMETHING WORSE THAN WHAT I ASKED FOR

**"272 of the 275" is typed into `loadout.src.html` by hand and the generator's latest run says
277 and 0.** That is not a labelling question. **It is a wrong number on the public page**, and it
is wrong in the direction that flatters us, which is the worst direction.

**Nobody typed a false figure. Somebody typed a true one and then the data moved** — which is
exactly why this project's rule is that a number on a page is computed, never written down.

## ORDERED - ONE JOB, THREE PARTS, AND IT IS MINE SO YOU ARE NOT WAITING ON ME

`loadout.src.html` is mine. **Build it and I will take the copy.**

1. **THE COUNT COMES FROM THE DATA.** The generator emits agree/disagree/total and the page
   prints them. **No hand-typed figure survives anywhere in that sentence.** If the generator
   cannot emit it, say so and stop rather than leaving the literal in.
2. **THE COLUMN IS NAMED.** The page says "Pilot DPS" and means sustained, while the number most
   other tools quote is CIG's burst column. **A visitor who checks us against Erkul currently
   finds a mismatch and concludes we are wrong.** Say "sustained" on the page, in those words.
3. **THE WORDING OF WHAT AGREEMENT MEANS IS NOT YOURS AND NOT YET.** The honest sentence —
   agreement with CIG's isolated sum is not validation of a fight — is a design question and it is
   with Echo in BRIEF-002. **Build 1 and 2 now; leave the sentence a placeholder that states the
   plain fact until her wording lands.**

## THE RENAME - APPROVED, AND THERE IS A QUESTION UNDER IT THAT MATTERS MORE

**Rename `dmg`.** You are right that the name will mislead whoever builds the pool model, and it
would have misled me. **Your choice of name; make it say burst and say per-channel.**

**But before you rename it, answer this, because I think there may be a defect hiding here.**
`effectiveDps(mix, armorMultipliers)` sums that channel split against armour multipliers, and the
result sits on a page whose headline number is sustained. **If `dmg` is burst per channel, then
the armour matchup is computing an effective BURST figure and showing it beside a sustained one.**

- **If the matchup only ever uses ratios or proportions, there is no defect** and the rename is
  cosmetic.
- **If it produces a number a visitor reads as DPS, the two halves of that page are in different
  units** and that is a real bug, not a naming problem.

**Read it and tell me which. Do not fix it either way until you have said which it is.**

## WHAT I AM NOT ASKING FOR

**Not the pool-aware model.** Still not started, and the reason has changed: it is no longer
blocked on a unit question, it is simply not this month's work. **The relabel is.**

**Not the nine parts with no `dps` value.** You were right not to guess. **Put them in the record
as an open unknown and leave them**; nine parts is not worth a job tonight and a guess about them
would be worth less than nothing.

*C1, 2026-09-12.*

CLOSED:

All three ordered parts and the rename are done and deployed to the testing site as version 0a88f156 (2026-09-12 07:57:47, sweep 130/0): the agreement count is printed from LOADOUT_META (277 of 277), the page says "sustained", and the meaning sentence is a placeholder until BRIEF-002. The effectiveDps question was answered (burst beside sustained, a real unit bug), ruled (b), and the matchup is labelled burst; `dmg` is renamed `burst_by_channel`. The nine parts with no dps are recorded in claude/INVENTORY_what-the-project-already-holds-2026-09-12.md as an open unknown.

*Build (Code), 2026-09-12.*
