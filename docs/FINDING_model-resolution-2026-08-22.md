# FINDING — model resolution. Your four figures all matched. **But the premise did not: 32 of the 40 orphans are not a naming problem at all — they are models for ships that do not exist in the 316.** Twelve flying ships have no geometry anywhere.

    from      C3 (Cowork), 2026-08-22
    for       C1 + Sleven
    task      C1: "Resolve every ship to a model, by hand, with no fuzzy matching"
    tables    data-layer/derived/model-resolution/  (3 tables + MANIFEST)
    lane      pure data resolution. testing/_src/ and holo-hardpoints/ untouched.
              Nothing converted, moved, renamed or deleted. Nothing fetched from RSI.

---

## 1. The four figures — regenerated from source, and they matched

    ships in the data          316    matched
    .glb files on disk         235    matched
    ships wired to a model     201    matched
    ships rendering nothing    115    matched
    orphan model files          40    matched

Read from `testing/_deploy/models/`, `LOADOUT_MODEL` in `loadout_model.gen.js`, and
`LOADOUT_SHIPS` in `loadout_data.gen.js`. **One figure worth adding: the 201 wired
ships point at only 195 distinct files**, because six files are shared by two ships
each.

## 2. WHAT I COULD NOT RESOLVE — leading with it, as instructed

**32 of the 40 orphan files are UNRESOLVED, and the reason is not naming.**

**There is no ship record for them in the 316.** Not under a different name, not
under a longer name, not under a ClassName. The ships are simply absent from
`LOADOUT_SHIPS`.

I checked each one twice — exact normalised name and ClassName first, then a
token-containment sweep purely to *surface candidates for me to judge*, never to
match automatically. **31 of the 32 surfaced no candidate at all.**

They fall into three groups:

**Concept ships CIG has never built** — 19 files. Kraken, Kraken Privateer, Galaxy,
Orion, Pioneer, Endeavor, Crucible, Legionnaire, Nautilus, Nautilus Solstice
Edition, Odyssey, Vulcan, Liberator, Expanse, Genesis, Hull D, Hull E, G12, G12a,
G12r, Ranger CV, Ranger RC, Ranger TR. **We hold models for ships that do not exist
in the game data.** Nothing is broken; there is nobody to wire them to.

**Edition variants CIG's data does not carry as separate records** — 8 files.
Argo Mole Carbon Edition, Argo Mole Talus Edition, Carrack w/ C8X, Carrack
Expedition w/ C8X, Caterpillar Best In Show 2949, Mustang Alpha Vindicator,
Valkyrie Liberator Edition. **The base ship exists and is already wired. The edition
is not a separate ship in the data**, so the file has no owner.

**Two flyable ships genuinely missing from the dataset** — E1 Spirit and
Zeus Mk II MR. **The Zeus is the clean diagnostic: its CL and ES siblings are both
present, so the pipeline works for that hull and the MR record is simply absent
upstream.**

**This is the finding that outranks the rest of the task.** The framing was that
this is the Ares Inferno failure again — a matcher too strict. **It mostly is not.
It is that our model library and our ship dataset were assembled from different
sources and hold different ships.** No amount of matching work closes that; only
adding ship records or accepting that some files have no home does.

## 3. The eight that DID resolve, and four needed a person

**Four resolved automatically**, on exact normalised name or ClassName:
Anvil Ballista Dunestalker, Anvil Ballista Snowblind, Dragonfly Yellowjacket, Nox Kue.

**Four needed a hand, and each is a distinct failure mode worth recording:**

**`Caterpillar_Pirate_Edition.glb` → `DRAK_Caterpillar_Pirate`.** The file carries
the word "Edition"; the ship record does not. One word.

**`Hammerhead_Best_In_Show_Edition_2949.glb` → `AEGS_Hammerhead_Showdown`**, and
**`Reclaimer_Best_In_Show_Edition_2949.glb` → `AEGS_Reclaimer_Showdown`.** The
ClassName says *Showdown*; the display name says *2949 Best In Show Edition*; the
file says *Best In Show Edition 2949*. **Three names for one thing, and the word
order differs from the display name too.**

**`F7C-M_Super_Hornet_Heartseeker_Mk_I.glb` → `ANVL_Hornet_F7CM_Heartseeker`.**
The file says *Super Hornet*. CIG's data says *Hornet*. **The ship was renamed and
our filename kept the old one.** This is the closest thing in the set to the Ares
Inferno shape, and it is one file, not forty.

**Every pair above agrees on manufacturer, checked independently of the name.** No
pair was accepted on name alone.

## 4. THE ANSWER TO THE QUESTION — ships flying today with no geometry anywhere

**Twelve.** By name:

    Anvil Arrow
    Drake Pitbull
    Gatac Tyilui
    Grey's Basher
    Greycat PTV
    Greycat UTV
    MISC Starlite
    Origin 85X Limited
    Origin M80
    RSI Aurora Mk II
    RSI Hermes
    RSI Mantis

**Three more have no geometry but are not flying player ships** and should not count
toward a decision: Aegis Tiburon and Argo MOTH are concepts, and the Vanduul Mauler
Destroyer is not player-flyable.

**Two more are not ships at all** and were removed from the count: `PowerSuit` and
`DRAK_Command_Module`.

**Twelve is the honest input to the CIG question.** Six of the twelve — Pitbull,
Tyilui, Basher, Starlite, M80, Hermes — are 2026 releases, which is the expected
shape: a fan model library lags new ships. **Whether twelve ships justifies
approaching CIG about the holoviewer models is Sleven's call and nobody else's.**

**I flag one thing about that decision rather than argue it:** CIC's capture
established the holoviewer models are OpenCTM, exterior hull only, no node
hierarchy. **They would render these twelve and would still supply no hardpoints.**

## 5. Table 2 — the 115 ships rendering nothing

    SHARED_HULL    90   an edition of a hull we already hold
    OWN_FILE        7   an orphan file, or a Fan Kit .ctm, belongs to it
    NO_GEOMETRY    15   nothing anywhere (12 flying, 3 not)
    UNSURE          1   see below
    NOT_A_SHIP      2   PowerSuit, Drake Command Module

**Ninety of the 115 are Wikelo War Specials, Teach's Specials, PYAM Execs, Best In
Show editions and paint variants of hulls already on disk.** Under the 2026-08-14
shared-hull ruling those are correct to share, and that is the bulk of the problem
solved by a rule that already exists rather than by new assets.

**Eight of those 90 needed a hand** because the ClassName suffix did not follow the
usual pattern: the F7C-M Heartseeker Mk II, the F7 Hornet Mk II Wikelo, the C1
Spirit Wikelo, the Dragonfly Star Kitten, the Golem low-fuel temporary record, the
Aurora Mk I SE, the base Mirai Fury, and the 600i Executive Edition.

**The one UNSURE row, and I am not guessing either way:**

**`ANVL_Lightning_F8` — the Anvil F8A Lightning.** We hold `F8C_Lightning.glb`. The
F8A is the military variant of the F8C and **I believe the external shape is the
same, but I have not verified it and I will not assert it.** If it is the same,
this is a SHARED_HULL and the count of flying ships with no geometry drops to
eleven. **Sleven can settle this in seconds and nobody else here can.**

## 6. Table 3 — the Fan Kit fourteen. Exactly two fill a gap.

**Your prediction was right and it is now measured.**

    Drake Cutlass Black        no .glb on disk        FILLS A GAP
    RSI Constellation Aquila   no .glb on disk        FILLS A GAP

**The other twelve we already hold as `.glb` and all twelve are already wired to a
ship.** MPUV Cargo, Sabre, F7C-M Super Hornet, Khartu-al, Defender, Mustang Alpha,
Mercury Star Runner, Blade, P-52 Merlin, Freelancer MAX, 600i Explorer, Cyclone.

**So the entire conversion value of the Fan Kit is two files** — and both are ships
the prototype can show and the live page cannot, which is exactly why the prototype
looked like it had models the site was missing. **It did. Two of them.**

Nothing converted. That is H4 and it is Code's.

## 7. What I checked and what I did not

**Checked:** all four figures regenerated from the named sources before starting;
every orphan tested by exact name, then ClassName, then a candidate sweep whose
output I judged by hand rather than accepted; every claimed pair checked against the
manufacturer field independently; all fourteen Fan Kit `.ctm` names matched against
the file list and against `LOADOUT_MODEL`.

**Did NOT check:**
- **Whether any SHARED_HULL row is visually correct.** Ninety rows assert an edition
  shares its base hull. That follows the standing ruling, and **not one was compared
  in game.** If a Wikelo special turns out to have a visibly different silhouette,
  that row is wrong and this document will not have caught it.
- **The F8A/F8C question.** Section 5. Deliberately left open.
- **Which of the twelve are flight-ready TODAY.** I sorted them by what I know of
  the game, not from a live source, and six are recent releases. **Sleven should
  confirm the list before it informs a decision about CIG.**
- **Whether the 19 concept-ship models are worth keeping on disk.** They are wired
  to nobody and will stay that way until CIG builds the ships. Not my call.
