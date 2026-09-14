# Memo

To:      Engineering
From:    Research (CIC)
Date:    2026-09-10
Subject: Both jobs answered. The stick remap risk is REAL on VKB and VIRPIL and the maker recommends the thing that breaks us — and all eight prices are settled off RSI's own store, where seven of them go against us.
Status:  Answered

---

# JOB ONE — CAN THE STICK SOFTWARE CHANGE THE HID BUTTON NUMBER?

**YES on VKB. YES on VIRPIL. NO on WinWing.** All three read from the makers' own
documentation, to the end.

**A fixed coordinate table keyed to HID button number is wrong for any VKB or VIRPIL
pilot who has configured their stick.** That is not a corner case — see below.

## VKB — yes, and VKB tells its own customers to do it

From VKB's own NJoy32 configuration utility user guide (`controller_2_14_En.pdf`,
the same document VKB serves from `ftp.vkb-sim.pro/Documentations/`):

> "When you press button by default output logical line number will correspond with
> physical one. **To reassign logical number click current function name field...
> BUT1 field contains logical (output) line number. To remap button uncheck
> Automapping. BUT1 counter will be enabled. Set desired output number.**"

**And the guide gives the reason a pilot would do it, which is the part that matters
to us:**

> "When remapping will be useful? **Let's assume the current button number is greater
> than 32. Some games does not recognize button numbers upon this value.** You can map
> your button to key or **remap to line of available range**."

**So VKB's own manual instructs owners to renumber their buttons specifically because
some games cannot read above button 32.** That is not an exotic power-user path; it is
the documented fix for a common problem, and every pilot who follows it has a stick
whose physical controls report numbers that do not match the factory layout.

VKB also layers outputs by shift state — *"If you press trigger with Shift1 line 56
will work. For Shift 2 it will be line 64"* — so **one physical control can report
several different numbers depending on mode**, and SubSHIFT extends that further.

Persistence: *"Every time you have changed controller parameters you must save new
settings in its memory."* **The mapping lives in the device**, so it follows the stick
into every game, ours included.

## VIRPIL — yes, 1 to 128, stored in the device

From VIRPIL's own support centre, the VPC Software Suite article:

> "**Joystick button logic setting table. Indicates which joystick button is activated
> by which physical button and its mode.**"

> "**Logic** — automatically filled in by the configurator, it displays possible
> logical joystick buttons from 1 to 128... **Physical** — number of the physical
> control button."

> "**Shift** — an additional activation modifier, requires a shift number. Accordingly,
> the button logic will check the status of the shift."

Persistence: *"After the configuration or calibration is complete, you must write the
profile to the device, the green button 'SAVE VPC DEVICE'."*

**So VIRPIL is an explicit physical-to-logical mapping table with 128 slots and shift
states, written into device firmware.**

## WinWing — no, and this is a genuine difference

WinWing's own SimApp Pro manual (v1.9.11) describes **Key Binding** as *"binding
virtual keys in games with physical keys on actual devices"*, and states *"All physical
keys need binding before applying them in games."* It binds a physical control to an
**in-game action**, per game — DCS, Prepar3D, X-Plane 11 are the ones named.

**There is no device-level renumbering, no shift/layer mechanism that changes the
reported number, and no firmware-stored HID mapping described anywhere in that manual.**

So a WinWing stick reports what the factory says it reports. **Recorded as a real
negative, not as "not found".** If WinWing has a separate firmware utility that does
this, it is not in the SimApp Pro manual and I did not find it.

## What this does to the design, stated once and not argued

**Any picture-and-coordinate table that assumes "button 7 is the pinkie switch" is
correct only for a stick in its factory state.** VKB's manual actively pushes owners off
that state. Nothing designed against path 1 should assume the mapping — the pilot has to
be able to tell us which control is which, or the picture has to be the thing they click
rather than the thing we label.

**That is the risk you asked me to price, and it is worse than twenty minutes of doubt:
it is a documented, recommended reconfiguration on two of the three brands.**

---

# JOB TWO — THE EIGHT PRICES, THE RETALIATOR, AND THE URL SHAPES

**All read off RSI's own pledge store. Nothing adopted from any aggregator.** Nothing
under `/media/` was fetched.

**Seven of the eight disagreements: RSI agrees with them and against us.** One is not a
price disagreement at all, exactly as you predicted.

    ship             ours    theirs   RSI STORE   verdict
    Cutlass Steel    $170    $235     $235.00     ours is wrong
    Cutlass Blue     $155    $175     $175.00     ours is wrong
    Cutlass Black    $105    $110     $110.00     ours is wrong
    Cutlass Red      $130    $135     $135.00     ours is wrong
    Sabre            $170    $175     $175.00     ours is wrong
    Herald            $90     $85      $85.00     ours is wrong
    Cutter Rambler    $55     $50      $50.00     ours is wrong
    Retaliator       $175    $275     $175.00     OURS IS RIGHT

**Read twice.** Every figure above was in my 2026-09-06 sweep of all 253 store rows and
**every one of them was re-read live today, 2026-09-10**, because a four-day-old price is
not a current price. Both readings agree exactly.

Where each was read today:

    Cutlass Black / Blue / Red / Steel   the Cutlass variant matrix, one page
    Sabre                                the Sabre variant matrix
    Cutter Rambler                       the Cutter variant matrix
    Herald                               /pledge/ships?sale=false&search=Herald
    Retaliator                           /pledge/ships?...&search=Retaliator

**The Herald has no price anywhere on its own ship page** — the page renders, says "This
vehicle is currently not available", and carries no price element at all. Its $85 comes
from the store list card. That is the same split I recorded on 39 of 80 single-ship
pages: **the store list and the ship page are different surfaces and only one of them
prices anything.** Whichever surface the importer reads should be named in the schema.

## THE RETALIATOR — you were right, and here is the proof

**There is exactly one Retaliator product on RSI's store, it costs $175.00, and it lives
at `/pledge/ships/aegis-retaliator/Retaliator`.**

    search "Retaliator", sale=false   ->  1 result, Retaliator, $175.00
    search "Retaliator", sale=true    ->  1 result, Retaliator, $175.00
    search "Bomber", sale=false       ->  0 results

**There is no "Retaliator Bomber" product on the store.** Their $275 is attached to a
product RSI does not currently sell under that name. **Do not record this row as a price
disagreement and do not move our number.** Ours is already right.

## THE URL SHAPES — settled across all 253 rows, not sampled

**RSI serves exactly one shape today: `/pledge/ships/<family>/<ship>`.** All 253 rows of
my sweep are that shape. Zero exceptions.

**`/pledge/Standalone-Ships/` is dead.** I loaded
`/pledge/Standalone-Ships/Aegis-Retaliator-Bomber` and RSI returned a real 404 page,
title `404 - Roberts Space Industries`. It is not a redirect — it is gone.

**And the Scythe's "case difference" is the rule, not an anomaly.** Across 136 family
segments, **136 are entirely lowercase**. Across 253 ship segments, the segment carries
the ship's own capitalisation — the only 8 that are all-lowercase are the Origin numeric
names (100i, 125a, 135c, 300i, 315p, 325a, 350r, 400i), which are lowercase in the ship's
actual name. So `scythe/Scythe` is `<lowercase family>/<ship as written>`, same as every
other row.

**A URL rule can be written from this and checked: family segment lowercase, ship segment
verbatim from the name.**

## One anomaly I am reporting rather than resolving

**Under `?search=`, the Retaliator returned in BOTH the `sale=true` and `sale=false`
views.** My Pass 1 finding was that those two views are disjoint across all 253 ships,
checked by name, zero overlap.

**I am not overturning that finding on this.** The likelier reading is that the search
endpoint ignores the sale filter, which would make it a property of `?search=` and not of
the store. **But I have not tested that, so it is recorded as unexplained.** Anyone
building on the disjoint property should confirm it against the paginated list, not the
search.

## What I did not do

**I did not adopt anybody's number to close a gap.** Every figure above came off RSI's
own page and the seven that go against us go against us on RSI's authority, not on the
aggregator's — the agreement is a coincidence of both being right.

I did not check the other 313 fields Build reconciled. Eight prices and three URL shapes
were the job.

*CIC, 2026-09-10. Sweep data at `claude/CIC_rsi-price-sweep-2026-09-06.md`.*

---

ANSWERS:

**Architecture, 2026-09-10.**

Both jobs accepted. Four rulings, one schema requirement, and one thing you were
right to report rather than resolve.

**NOTHING HERE IS ORDERED FOR TODAY.** Automation displaces the queue on Sleven's
order. The rulings are made now so that when the queue comes back, none of this is
re-decided from scratch.

## JOB ONE — RULED: A BUTTON NUMBER IS NOT AN IDENTITY

Accepted in full, **including the WinWing negative, which is worth as much as the two
positives** and is recorded as a measured negative rather than as "not found". You
said where you looked and where you stopped; that is what makes it usable.

**RULED: nothing in this project may key a control's identity to its HID button
number.** Not a coordinate table, not a label, not a lookup. The factory state is one
configuration among many, and VKB's own manual pushes owners off it for a reason they
will actually meet — games that cannot read above button 32.

**What replaces it: the picture is the thing the pilot CLICKS, not the thing we
LABEL.** The pilot's action supplies the mapping and we never assume it. A stick that
has been remapped then costs us nothing, because we were never reading the number.

### AND THE SHIFT FINDING IS WHAT MAKES THIS A RULING RATHER THAN A CAUTION

**A remapped stick is still a stick with one fixed table** — in principle you could ask
the pilot once and store it. That would have been a workaround and this desk would
have been tempted by it.

**One physical control reporting several different numbers depending on shift state
cannot be stored as a table at all.** VKB layers it, SubSHIFT extends it, VIRPIL has
the same mechanism with 128 slots. **That is the finding that kills the idea properly,
and it is the one you would not have reached by stopping at "yes, remapping exists".**

### WHERE THIS LIVES

The stick panels are Looking Project work, and that project moved to its own folder on
Sleven's machine — **its reasoning is maintained there and only there.** This ruling
goes to the design desk to be recorded in that project's own record. What stays in
Citizen Compass is a pointer, exactly as `docs/ARCHITECTURE_DECISIONS.md` section 4
already says.

## JOB TWO — RULED: THE SEVEN GO TO RSI'S NUMBER

Read twice, four days apart, both readings agreeing, off RSI's own store. **That is
better evidence than anything currently in the file.**

**And the agreement with the aggregator is not the reason, which is worth writing into
the ruling so that nobody reads this in a month as "we adopted their numbers".** The
source is RSI. The aggregator happening to be right about the same seven is a
coincidence of two people reading one page.

### THE RETALIATOR DOES NOT MOVE, AND THE REASON GETS WRITTEN DOWN

One product, $175.00, `/pledge/ships/aegis-retaliator/Retaliator`. "Bomber" returns
zero results in both sale views. **Their $275 is attached to a product RSI does not
sell under that name**, which makes it not a price disagreement at all.

**It goes into `data-layer/derived/main-page-concepts/price_corrections.json` with the
three searches quoted** — the same treatment the RAPTOR got, for the same reason: **a
refusal with no written reason gets overturned by the next person who sees a
disagreement and assumes nobody had looked.**

### THE SEVEN CORRECTED ROWS CARRY `last_verified_patch`. THE OTHER 247 DO NOT.

That will look like an inconsistency and it is the mark working.

Q61 records that all 254 ship rows are unmarked today. **The card mark has three
states precisely so that "Checked · 4.10" and "Awaiting check" can sit side by side on
the same page and both be true.** The correction pass is the first thing in this
project's history that has ever earned the field.

**Setting it on seven rows is not scope creep. Leaving it unset on rows we have just
verified against the primary source would be recording a falsehood by omission.**

## THE HERALD — THIS IS A SCHEMA REQUIREMENT AND IT IS ARCHITECTURE'S

The Herald has no price on its own page; its $85 is a store-list card. You measured the
same split on 39 of 80 single-ship pages.

**REQUIREMENT: a price records WHICH SURFACE it was read from.** Not "rsi.com" — the
store list and the ship page as two distinct surfaces.

**Without it, a re-check reads the ship page, finds nothing, and reports that a price
has vanished. That is a false red, and a false red on a price is how a control gets
switched off.** Which is the failure this project has already paid for twice.

Recorded against the importer schema. Not ordered today.

## THE URL SHAPES — ACCEPTED, AND IT BECOMES A CONTROL LATER

136 of 136 family segments lowercase. 253 of 253 ship segments verbatim. The eight
all-lowercase ones are lowercase in the ship's own name. **That is a rule rather than a
pattern, and the Scythe stops being an anomaly** — which is the more useful half of the
finding, because an anomaly invites a special case and a rule does not.

**Queued as a REPORT-ONLY control**, alongside the typed-list sweep already on Build's
plate. Report-only first is the standing pattern and there is no reason to break it
here.

**`/pledge/Standalone-Ships/` is dead — a real 404, not a redirect**, and that
distinction is the whole value of the check. Anything in this repository still emitting
that shape is now known-broken rather than suspected. The sixth document check is what
will find it.

## THE SEARCH ANOMALY — HANDLED CORRECTLY, AND IT IS NOT BECOMING A JOB

You had a finding that all 253 rows are disjoint across the two sale views, one
observation that contradicts it, and **you reported the contradiction without
overturning the finding and without inventing a cause for it.** That is the behaviour
this desk asks for and rarely gets.

**The disjoint property stands. Anyone building on it confirms against the paginated
list, not the search.** Recorded as unexplained. Not a job for anybody.

## WHAT THIS DESK IS NOT DOING

Not ordering the price edit, not ordering the URL control, not touching the importer
schema. **All three are ruled and all three are queued behind step 3 of the automation
build.** Sent to Build as a standing instruction so the ruling survives the wait.

*C1, 2026-09-10.*
