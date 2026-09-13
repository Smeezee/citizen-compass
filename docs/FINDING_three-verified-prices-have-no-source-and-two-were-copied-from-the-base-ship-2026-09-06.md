# FINDING — three prices marked "verified" have no source anywhere, and two of them are the base ship's price copied across

**C1, 2026-09-06.** Sleven asked what the Gladius Dunlevy is, whether there is a
second Heartseeker, and why one is $200 and the other $30. Answering those three
questions turned up a fourth thing nobody asked about.

---

## 1. The Gladius Dunlevy is real, and it is CIG's

`scunpacked` snapshot `20260827T225641Z`, `ships/aegs_gladius_dunlevy.json`:

    ClassName    AEGS_Gladius_Dunlevy
    Name         Aegis Gladius Dunlevy
    Career       Combat        Role  Light Fighter
    Size 2       Crew 1        Cargo 0

CIG's own description: *"Honor the famed Captain who shaped the course of the UEE
Navy's elite fighter squadron with the Dunlevy variant for the Aegis Gladius. This
special ship pays to tribute to Captain Alexandra Dunlevy and Squadron 42 with red
highlights against a grey base paint and military-grade components."*

**So it is a special edition of the Gladius: a paint and a component loadout, tied
to Squadron 42.** `FINDING_model-resolution-2026-08-23.json` files it under
`editions`, base `AEGS_Gladius`, own model `null`, inheriting `Gladius_Valiant.glb`.

**It is not in the pledge store** — CIC swept both views on 2026-09-06 and it is in
neither. That is consistent with a Squadron 42 promotional edition and it means
**there is no page for Sleven to save a picture from.** The gap stays open, correctly.

## 2. There are two Heartseekers, and both are real

    ANVL_Hornet_F7CM_Heartseeker       "Anvil F7C-M Hornet Heartseeker Mk I"
    ANVL_Hornet_F7CM_Mk2_Heartseeker   "Anvil F7C-M Hornet Heartseeker Mk II"

Sleven found one and not the other because **only the Mk I is in the store.** CIC
read it live at $200 as `F7C-M Super Hornet Heartseeker Mk I`.

**Note that CIG uses two different names for the same ship.** The game data says
*Hornet Heartseeker Mk I*; the store says *Super Hornet Heartseeker Mk I*. Neither
is wrong and neither is ours to normalise — it goes in the alias table by hand.

CIG's description of the Mk II: *"When the F7C-M Super Hornet got upgraded to the
Mk II, there was no doubt in the Anvil Aerospace's mind that they would be giving
the very special Heartseeker edition the same treatment."* Limited edition, and it
is not on sale.

## 3. Why $200 against $30 — and this is an inference, labelled as one

**$30 is not ship money for a Hornet.** Every Hornet on the store is $125 to $240.

CIG's item files carry **`items/paint_hornet_f7cm_mk2_heartseeker.json`** — the
Heartseeker Mk II exists as a *paint* as well as a ship, alongside twenty other
Hornet paints.

**The likeliest reading is that our $30 is the paint's price, not the ship's.**
That fits the amount, and it fits that the ship itself is not sold. **It is an
inference. Nobody has seen a $30 price tag on a Heartseeker Mk II paint, and it is
not being written into the price column as fact.**

## 4. The thing nobody asked about

**Ten rows carry a price with no `pledge_url` and are stamped `confidence:
"verified"`.** Checked every one against CIC's live sweep:

    agrees with the store, just missing its URL          5
    differs, and was corrected today                     1   P-72 Archimedes Emerald 35 -> 40
    the store lists it and shows NO price                1   F7A Hornet Mk II $175
    NO SOURCE EXISTS ANYWHERE                            3

The three with no source:

    600i Executive Edition            $475
    Gladius Dunlevy                    $90
    F7C-M Hornet Heartseeker Mk II     $30

**Two of the three are the base ship's price, copied.**

    Gladius Dunlevy          $90    the Gladius is $90 on the store
    600i Executive Edition  $475    the 600i Explorer is $475 on the store

That is not a coincidence at two significant figures across two unrelated
manufacturers. **A special edition was given its base ship's price and stamped
verified**, and the third is the Heartseeker Mk II at paint money.

**A wrong number is recoverable. A wrong number wearing a "verified" badge is
not**, because every later check trusts it and skips it. `confidence: "verified"`
with a null URL and no source is the exact condition rule 12 forbids — a claim
shaped so nothing can disprove it.

## 5. What this changes

**It is the strongest argument yet for the three-state `price_status`** already
specified for Code: `read`, `stated_absent`, `not_read`. Under it, none of these
three could have been called verified — there was nothing to read.

**Recommended, not done:** the three lose their price and become `not_read`, and
the F7A Hornet Mk II's $175 becomes `stated_absent` — the store lists that ship
and shows no price, confirmed from two surfaces. **Sleven's call, because deleting
a number a visitor can see today is a visible change to the site.**

## What was checked, and what was not

**Checked:** the ship and item files in snapshot `20260827T225641Z`; the model
resolution finding's `editions` block; all 254 rows in `releases/latest.html` for
the price/URL/confidence combination; each of the ten against CIC's 253-row live
sweep by exact name.

**NOT checked:** where the three unsourceable numbers were originally typed, and
by whom. The copied-from-base reading is an inference from the two matches, not a
provenance trace. **Nobody has confirmed a $30 price on the Heartseeker paint.**

*C1, 2026-09-06.*
