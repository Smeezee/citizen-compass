# RESEARCH — how DPS is calculated across the tools, and the thing we have been quietly claiming

**SOURCE NOT STATED. Relayed by Sleven, 2026-09-12, part three of the competitive search he is
running himself, including its own later correcting pass. NOT the Design desk and NOT Echo.**

**Sections 0 and 8 are C1's. Sections 1 to 7 are the document as received, both passes merged in
the order they arrived, unaltered.**

**Companions:**

    claude/RESEARCH_the-competitive-landscape-and-where-we-win-2026-09-12.md
    claude/RESEARCH_rentals-the-third-acquisition-path-2026-09-12.md

---

## 0. C1'S VERIFICATION PASS

### THIS IS THE BEST OF THE THREE, AND IT LANDS ON US, NOT ON A RIVAL

The first two documents were about what competitors do. **This one found something about our own
page, and it is the kind of finding this project is supposed to produce about itself and did
not.**

### THE FINDING — "MATCHES CIG ON 272 OF 275" IS TRUE AND IT DOES NOT MEAN WHAT IT LOOKS LIKE

**Our loadout bench states that summed pilot DPS matches CIG on 272 of 275 stock ships.** It is
displayed as a trust mark. **Read plainly, a visitor takes it to mean our combat number is
validated against the game's own authority.**

**The report's correcting pass says CIG's own `pilot_dps` and `turret_dps` are themselves isolated
per-gun sums — not a simulation of a ship firing.** Its evidence, which I checked arithmetically:

    Gladius     1944.5  =  545.6 + 545.6 + 853.3        exact
    Hammerhead 19630    =  24 x 817.92                  exact to rounding

**Both hold.** So if the premise is right, **our 272-of-275 agreement is proof that our addition
matches their addition.** It says our arithmetic is faithful. **It says nothing about whether the
number a pilot would actually do is anywhere near it**, because three energy repeaters sharing one
capacitor cannot all fire flat out, and neither figure knows that.

**The claim is not false. The framing is doing work the claim cannot support** — and this project
exists to not do that. **It is the cheapest fix in all three documents: it is a label, not a
model.**

### THE OPEN QUESTION THAT HAS TO BE SETTLED BEFORE ANY OF IT IS RELABELLED

**Is CIG's figure a sum of BURST values or of SUSTAINED values — and which one is in our `sdps`
field?**

The report's own two examples do not obviously agree:

- **CF-447 sustained is given as 414.5**, and the Hammerhead check requires **817.92 per gun**, a
  ratio of **1.97**. So the Hammerhead figure is built from burst, not from that sustained number.
- **Our stored values are said to match CSG's SUSTAINED column** — M7A 929.1, Attrition-5 602.9,
  Bulldog 111.9 — **and our field is named `sdps`, for sustained.**

**Those two things cannot both be true of one CIG field.** Either CIG uses burst for turrets and
sustained for pilot guns, or our `sdps` holds something other than what its name says, or one of
the report's figures is wrong.

**This is the project's own worst defect class wearing a different hat** — the same count taken on
two surfaces — and **it is not settled by reading more of anybody's website. It is settled in one
query against our own data**, which is ordered to Code.

**Nothing gets relabelled until that comes back.** Relabelling on top of an unresolved unit
confusion would just move the error somewhere harder to find.

### RULED — IF WE SHOW POWER PIPS, THEY MOVE THE NUMBER WE PRINT

The report states it as a recommendation. **This desk adopts it as a rule.** Showing a power
control that visibly does nothing to the damage figure beside it is a UI that lies by layout. **A
control that does not affect the number must not sit next to the number.**

### THE EQUAL-TIME STRIP IS THE BEST IDEA IN ANY OF THE THREE DOCUMENTS

**Damage delivered in 5, 10, 15, 30 and 60 seconds**, instead of arguing about whether "burst" or
"sustained" is the honest single number.

**It ends a class of argument rather than taking a side in it.** Burst flatters guns that dump
fast; sustained flatters guns that never stop; the fight lasts however long it lasts. **An equal
time budget is the only comparison that is fair to both**, it is derivable from figures we already
hold, and no rival publishes it.

**It is also, quietly, the honest fix for the summing problem** — because once the axis is time,
the moment where a shared capacitor runs dry becomes a visible bend in the line rather than a
footnote.

### NOT VERIFIED BY THIS DESK

**Every game-file claim here.** The sustained formula and its cycle model; `shield.absorption.
physical` running 0 to 0.45; deflection scaling with remaining armour HP; distortion draining
rather than damaging hull; ship guns declaring no overheat in 4.10. **All plausible, all
consistent with what CSG is said to publish, none re-derived by this desk.**

**Every claim about Erkul's internals** — `dpsBurst`, `dpsSustain`, `alphaMax`, the `energyDetail`
block, `regenerationCostPerBullet`, weapon-pool segments. Read off a rival's live UI and its
JavaScript by someone else. **Useful as a map of what the problem contains. Not evidence, and not
to be cited on our own page.**

**The arithmetic I did check is the arithmetic above, and only that.**

### WHAT IS OURS AND WHAT IS THE DESIGN DESK'S

**Mine and Code's, not Echo's:** whether we build a pool-aware sustained model, the pool model
itself, whether pips gate the printed figure, and the burst-versus-sustained unit question.
**That is engineering and it is not up for design ranking.**

**Echo's:** every word and state on the page — the provenance labels, the three-stat strip, how
the equal-time strip reads, what the default hero number is, and how a gated figure shows that it
is gated. **Going into BRIEF-002 on that basis.**

---

## 1. THE CORE VOCABULARY — the document as received

- **Alpha** — damage from one trigger pull, all pellets counted.
- **Burst DPS** — damage per second while the gun is actually firing at full rate.
- **Sustained DPS** — long-run average after downtime: capacitor refill, reload, heat.
- **TTK** — time to kill a chosen target through shields, armour and hull. Not a raw DPS number.

**Game-file basics** (wiki / CSG / scunpacked-style): Alpha is about `damage.alpha_total`;
burst-style DPS is about alpha x rate of fire, with the wiki mapping `damage.burst` to "DPS";
energy ship guns are limited by a capacitor or weapon energy pool rather than magazine and reload,
and per CSG the ship weapons declare no overheat and no magazine in the files. FPS weapons differ.

**Confirmed formulas from the later pass (wiki API, 4.10):**

    Burst      = alpha x rpm / 60

    fire_time  = max_ammo / (rpm / 60)
    regen_time = max_ammo / regen_per_sec
    cycle      = fire_time + cooldown + regen_time
    sustained  = (max_ammo x alpha) / cycle

Given as verified against M7A at 929.1 and CF-447 at 414.5. **Regen happens after the dump, not
during fire.**

## 2. ERKUL v5 — the community default

Shows alpha, burst DPS and sustained DPS, split by pilot / manned turret / remote / PDS, plus
power, cooling, penetration and deflection, hull and door HP, LIVE and PTU, and shopping.

Per-weapon it carries `dpsBurst`, `dpsSustain` and `alphaMax`. For energy guns an `energyDetail`
block holds the pool, continuous fire time, regen recharge time, max regen per second, cost per
shot, and a `dpsSustainMax` against efficiency when the shared pool or power pips throttle you.
Weapon pool segments and power states scale energy DPS when several energy guns share a pool.
Gimbal mode, beam sustain and charge weapons are handled; ballistics use ammo counts, energy uses
the pool model.

**Assumptions and limits:** 100% hits — no accuracy, convergence or server registration; sustained
is a long-cycle average that players have complained only matches after unrealistically long fire;
burst is not always a fair cross-gun comparison when dump durations differ; turret and PDS numbers
can look heroic against what crew or AI actually sustain.

## 3. CITIZEN STARTER GUIDE — weapon table and loadout builder

Per-weapon and explicit: alpha is one trigger pull with all pellets; DPS is alpha x RoF; sustained
is after the capacitor empties and refills, and is left blank when a weapon declares no capacitor.
Range is modelled as spread on a cone against a fixed target size plus projectile despawn at
velocity x lifetime — not a measured falloff curve. Crafted "best" stats appear where blueprints
exist.

**Its own hard warning: do not add every gun's DPS into a ship total — the power supply is shared,
and turrets especially overstate.**

The builder adds TTK against target shields, armour and hull; the burst-to-sustained transition
when the capacitor or heat window ends; deflection, armour damage reduction and penetrating DPS;
power triage from real pip budgets in the files; door HP and shots-to-breach; and LIVE against PTU
datasets.

## 4. CITIZEN COMPASS — read from our own code

Shows sustained DPS for the pilot, alpha as a pilot volley, turret DPS separately, and missile
payload as alpha rather than DPS. **Stock builds prefer CIG's precomputed `sdps`; edited builds are
summed from parts.**

- Each part carries precomputed `alpha` and `dps`, and our values match CSG's sustained column —
  Attrition-5 602.9, M7A 929.1, Bulldog 111.9.
- `calc()` adds pilot-gun dps and alpha; turret ports go to `tdps` instead.
- The damage-type mix is summed for the armour matchup, and
  `effectiveDps(mix, armorMultipliers)` is the sum over damage types of type x armour multiplier.
- **Power and cooling budgets are shown as draw against capacity and are not folded into the DPS
  number.**
- The UI claims summed pilot DPS matches CIG on 272 of 275 stock ships.

**Assessment as received:** we are doing honest file-faithful aggregation plus CIG stock figures,
not an Erkul-style shared-pool simulation. A different product choice — and the main combat-math
gap against Erkul and CSG.

## 5. THE OTHERS

**Hardpoint.io** — historically solid on heat and signature fitting; stale against 4.10, so not a
current method reference. **Generic web DPS calculators** — toy formulas with crit chance and vague
sustained modifiers; not file-accurate, ignore for parity. **SPViewer** — performance and endurance
oriented; live data health was shaky when checked.

## 6. SIDE BY SIDE

**Erkul v5** has alpha, burst, a pool-and-regen sustained model, the shared weapon energy pool,
power pips affecting DPS, a four-way pilot/turret split, limited range handling, armour pen and
deflection, analysis-tool TTK, and LIVE/PTU.

**CSG builder** has alpha, burst per gun and inside TTK, a capacitor-cycle sustained, the shared
pool via triage and TTK, pips affecting DPS, careful turret treatment, file-based stock figures,
strong range and spread, pen and deflection, TTK as a core feature, and LIVE/PTU.

**Citizen Compass** has alpha for the pilot, **no burst column**, precomputed part sustain summed,
**no shared pool in DPS**, a power bar only, a pilot/turret split, CIG `sdps` when stock, **no
range**, a matchup table with ranges, **no TTK**, and a single build snapshot.

**Who actually resimulates the ship:** CIG and the wiki give an isolated sum for stock and nothing
for edited; CSG reprints CIG for stock and still sums for edited, with the pips UI not scaling
DPS; Citizen Compass uses CIG `sdps` for stock and still sums for edited; **Erkul resimulates,
with the shared weapon pool and pips. It is the only one that does.**

## 7. WHAT IS MISSING, AND WHAT BETTER LOOKS LIKE

**Gaps almost everyone shares:** hit chance, convergence and server registration — all assume
shots land; real pilot aim time, tracking, lead and atmosphere; AI turret accuracy and engagement
logic, so summing turret DPS overstates; mixed ballistic bleed-through, still fuzzy — **and CC
correctly shows a range rather than a fake single percentage**; Maelstrom and future armour; ammo
logistics for ballistics in long fights, not just magazine size.

**File fields rivals underuse:** `shield.absorption.physical` at 0 to 0.45 for ballistic bleed —
the old 50/30/20 folklore is wrong; armour deflection scaling with remaining armour HP; distortion
as drain and disable rather than hull DPS; ship guns declaring no overheat in 4.10.

**Gaps specific to Citizen Compass:** the shared capacitor and weapon pool, the biggest real gap
against Erkul, because summing three energy repeaters can invent DPS the pool cannot feed; no burst
column, when pilots also want the first five to ten seconds; no TTK, which is how people misread
cannons against repeaters; no range slider, when CSG's spread and despawn model changes rankings a
lot; power triage not tied to DPS, so the figure does not drop when overdrawn; turrets labelled as
needing crew but not modelled, which is good honesty that could go further by making pilot-only
DPS the default hero number.

**Recommended priorities as received:**

**P0 — fix the lie that summing creates.** Keep CIG stock `sdps` as the gold label when stock. For
edited energy fits, replace the naive sum with a pool-aware sustained using continuous fire time,
regen time, cost per shot and pool size, and **show "summed (unthrottled)" against "pool-limited"
side by side when they diverge.** If power draw exceeds generation or pool caps, **mark the DPS as
gated rather than silently printing the fantasy number.**

**P1 — teach the fight, not just the gun.** Burst next to sustained and alpha as a three-stat
strip; simple TTK presets for light, medium and heavy targets from file shield and hull values,
with the burst-to-sustain transition; and pilot-only pool-limited sustained plus alpha as the
default hero metric, with turret DPS behind a toggle.

**P2 — go beyond, in CC's voice.** Provenance labels on every combat figure — CIG, pool model,
summed, matchup range; rent-and-buy context, since the DPS is moot if you cannot afford or rent the
hull; a range band borrowing CSG's cone-and-despawn idea for an "effective at 300 / 1000 / 2000 m"
chip; no faked ballistic shield split, keep the ranges; and optionally an "open this fit in Erkul"
handoff once the acquisition and truth layer is solid.

**From the later pass, upgraded and reordered:** label stock DPS as a CIG isolated-gun sum and show
the addends; shared-pool sustained on edited fits; **an equal-time strip at 5, 10, 15, 30 and 60
seconds**, which fixes the Attrition-versus-M7A ranking argument; pilot / manned / remote / PDC as
four numbers; TTK using 4.10 absorption and deflection rather than 3.x myths; **if you show power
pips they must move the DPS you print**; a range toggle on the loadout; and **a published one-page
"how we compute DPS", which Erkul will not do.**

**Not worth time:** crit-chance fantasy calculators; pixel-perfect aim simulation; chasing Hardpoint
or SPViewer as peers until they prove 4.10-live.

**Still stands:** do not add missiles into DPS, do not treat Hardpoint as current, and do not claim
"official" without the isolated-gun caveat.

**It offers an implementation spec next — exact fields, formulas and UI copy for the stats panel.**

---

## 8. C1'S DISPOSITION

**ORDERED TO CODE, and it blocks the rest:** settle whether CIG's `pilot_dps` and `turret_dps` are
sums of burst or of sustained, and what our `sdps` field actually holds. One query, our own data,
read-only.

**ORDERED TO ECHO in BRIEF-002:** every word and state on the stats panel, including how a gated
figure shows that it is gated and what the default hero number is.

**RULED HERE:** a power control that does not move the printed figure does not sit beside it.

**NOT ORDERED:** the pool-aware sustained model. It is the real gap and it is real engineering, and
**it is not started until the unit question comes back**, because a pool model built on a field
whose contents are in doubt is a second wrong number with more machinery behind it.

**NOT ORDERED: the implementation spec the report offers.** See the memo to Sleven — three
documents in one evening have produced more design surface than this project can build, and the
next thing it needs is a decision about what not to do.

*C1, 2026-09-12.*
