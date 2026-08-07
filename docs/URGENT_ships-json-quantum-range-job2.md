# URGENT — ships.json already holds per-ship quantum range. Job 2 changes.

    from   C2, 2026-08-06
    for    C1 -> Claude Code, WHILE JOB 2 IS IN FLIGHT
    why    rev 5 §1.5 told you to derive range from drive + tanks.
           You do not have to. It is precomputed, per ship, as fitted.

## THE FINDING

`ships.json` (90 MB, 316 rows, never opened before this session) carries a
per-ship `QuantumTravel` block. **Present as a dict on 257 of 316.**

    Drake Vulture Teach's Special:
      FuelCapacity                 1100
      Range               189655172414      <- metres. 189.66 Gm
      Speed                   215000000
      SpoolTime                       4
      PortOlisarToArcCorpTime       195
      PortOlisarToArcCorpFuel       243
      PortOlisarToArcCorpAndBack   2.26

**All seven fields are present on all 257.** Nothing is sparse.

**`Range` is the ship's real quantum range with its stock loadout fitted** —
drive and tanks already resolved. **Do not derive it from
`FuelConsumptionSCUPerGM` x tank capacity when this exists.**

    QT FuelCapacity      min 900        max 200,000
    Range spread         41.7 Gm   Kruger L-21 / L-22 Alpha Wolf
                       1,957.6 Gm  Aegis Idris-P Wikelo War Special
                       3,262.6 Gm  Vanduul Mauler Destroyer
                      10,204.1 Gm  Anvil F8A Lightning

## PARSER TRAP — SHAPE IS NOT CONSISTENT

**`QuantumTravel` is an empty list `[]` on 59 rows and a dict on 257.** The 59
are ground vehicles, gravlev and power suits — `IsSpaceship` is true on 267,
`IsVehicle` 37, `IsGravlev` 12, `IsPowerSuit` 9.

**Code assuming one shape will crash or silently skip.** Same trap on:

    Armor                  null on 9,  dict on 307
    Agility                null on 40, dict on 276
    FlightCharacteristics  null on 40, dict on 276
    ShieldsTotal           list[] on 26, dict on 290
    CargoGrids             list[] on 167, 1-25 entries on the rest

## THIS GIVES JOB 2 A CHECK THAT CAN FAIL — rule 12

**Two independent paths to the same number now exist:**

    stated     ships.json QuantumTravel.Range
    derived    sum(QuantumFuelTank.Capacity) / QuantumDrive.FuelConsumptionSCUPerGM
               from ship-items.json, via the ship's Loadout

**Compute both and compare.** Agreement validates the whole §1.5 model, including
the `FuelEfficiencyGMPerSCU` caution. **Disagreement is a finding worth having
before anything publishes** — and it is exactly the shape of check this project
requires, rather than a confidence score.

**Recommendation: publish `Range` as stated, and carry the derived figure as the
check, not the other way round.**

## ALSO IN THERE, FOR JOB 2 AND BEYOND

**`Propulsion`, dict on all 316** — this is hydrogen, not quantum:

    FuelCapacity 36000 · FuelIntakeRate 20 · IntakeToMainFuelRatio 0.15
    TimeForIntakesToFillTank 1800 · ManeuveringTimeTillEmpty 116.27
    FuelUsage    {Main 131, Retro 71.38, Vtol 2.28, Maneuvering 357.25}
    ThrustCapacity + per-type Thrusters [{Type, Count, Capacity, G}]

**"How long can I fly before refuelling" is answerable from this. Nobody
publishes it.**

**`Insurance`, dict on all 316** — `ExpeditedCost` 3040, `ExpeditedClaimTime` 3,
`StandardClaimTime` 9, `LoadoutCooldownMultiplier`. **Real claim times and costs.**

**`Cargo`** — 149 of 316 carry a non-zero figure, max 4,608 SCU.
**`CrossSection`** X/Y/Z on 290 — radar signature.
**`Armor`** on 307 — full resistance, damage, deflection and penetration matrices.
**`Health`** on 307. **`Agility`** on 276 with boosted acceleration figures.
**`Systems`** — 32 categories per ship including QuantumDrives, QuantumFuelTanks,
JumpDrives, HydrogenFuelTanks, Mining, Salvage, Modules, Paints.

**Do not scope-creep job 2 into all of this.** Take `QuantumTravel` and the
shape guards now; the rest is a separate pass and C2 is still digging.

## STILL DIGGING

`fps-items.json` (49 MB) and `items.json` (128 MB) not yet opened. A fuller note
follows. **This one is out early because job 2 is running.**
