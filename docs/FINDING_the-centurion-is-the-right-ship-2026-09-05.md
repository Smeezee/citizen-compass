# FINDING — the Centurion on the site is the right ship. The mark can be cleared.

C1 (Architecture), 2026-09-05

Sleven marked the Centurion *"not the right ship"* in his walk. It has sat on the
open list uninvestigated since. I have now looked, and **the model is correct.**

## What is on the site

Decompressed and rendered from `testing/_deploy/models/Centurion.glb`: a
six-plus-wheeled armoured vehicle carrying a **radar dish** and a **raised
multi-barrel top turret**.

## What CIG says the Centurion is

From CIG's own ship record, `anvl_centurion.json`:

    ClassName    ANVL_Centurion
    Role         Anti-Air
    Description  Built on Anvil's popular Atlas Platform, the Centurion presents
                 a tactical solution for short-range anti-aircraft operations
    ClassName    ANVL_Centurion_Remote_Top_Turret
    Name         hardpoint_wheel_left01..left04, right01..right04

**A radar dish and a top turret on a wheeled Atlas chassis is precisely an
anti-air vehicle.** The model matches the record.

## Why it looked wrong, and this is the useful part

The Centurion and the Ballista are **the same chassis**:

                        width   height   length
    site Centurion       6.75     5.25    16.65
    site Ballista        6.74     5.36    16.72
    CIG Centurion hull   6.28     4.42    16.71   (chassis only, no wheels/turret)

Within 0.11 m of each other on every axis. Both are Anvil Atlas platform
vehicles - CIG files the Centurion under
`Data\Objects\Vehicles\ANVL\Atlas\Centurion\`.

**They differ only above the deck:**

    Centurion   radar dish + multi-barrel turret     anti-air gun
    Ballista    rows of missiles on raised rails     surface-to-air missiles

They are genuinely different models - 510,022 triangles against 325,975,
different bytes - not one file used twice. But at a glance they are the same
vehicle with different gear on the roof. **That is almost certainly what the
mark was**, two near-identical hulls one after the other in a list.

## The CIG chassis corroborates rather than contradicts

The bare chassis out of `Data.p4k` is 6.28 x 4.42 x 16.71 against the site's
6.75 x 5.25 x 16.65 - **length agrees to 6 cm**, and the site's model is wider
and taller by exactly what wheels and a turret add, both of which are separate
files not present in the bare chassis.

Three independent things agree: CIG's written description, CIG's geometry, and
what is on the page.

## Recommendation

**Clear the mark. Replace nothing.** The Centurion comes off the open defect
list and off the replacement list.

**Not established and not claimed:** whether the model carries all eight wheels
CIG's record names. The render angle hides some and I did not count them. That
is a separate and much smaller question than the one that was asked.
