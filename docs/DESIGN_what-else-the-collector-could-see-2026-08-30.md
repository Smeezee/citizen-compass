# DESIGN — what else the collector could capture. The surprise is that almost none of it is object recognition: the game already writes most of it down, and labels most of the rest on screen.

    from    C1 (Cowork), 2026-08-30
    raised  by Sleven: "I wanna plan for the future... mining materials,
            weapons on the ground, faction armor, recognizing different
            factions, security ships and security forces"
    status  design, nothing queued. Ships-in-space is Sleven's decided feature
            and is Tier 3 below.

---

## 1. THE ORDERING PRINCIPLE, BEFORE THE LIST

**Four tiers, cheapest first. A thing belongs in the lowest tier that can get
it, and most ideas land far lower than they first appear.**

    TIER 1  THE LOG ALREADY SAYS IT              free, no pixels, exact
    TIER 2  THE GAME LABELS IT ON SCREEN         read text - the atlas
    TIER 3  WE HOLD A 3D MODEL OF IT             synthetic training data
    TIER 4  WE HOLD NEITHER                      genuinely hard, usually skip

**The rule: log before text, text before pixels.** Every proposal gets asked
"does the log already say this?" first. That question has closed four supposed
blockers this week on its own.

## 2. WHAT TIER 1 ALREADY HOLDS, TODAY, WITH NO WORK

From one session of `gamelog-dataset.json`:

    ship_classes         992      equipment_seen       542
    locations             44      quantum_routes        57
    contracts_seen        55      deaths               131
    shop_class_names      18      mission_payouts      16
    builds                34      mineable_rocks         6
    subsystems            71      vehicles_destroyed    18

**Nobody has ever put that in front of a player.** Before building any
recogniser, this is a dataset sitting unused.

## 3. SLEVEN'S FOUR, SORTED — AND THREE OF THEM ARE TEXT

### Mining materials — TIER 2, and it is the biggest one
**Not object recognition.** The mining scanner draws the rock's composition as a
**percentage list on a UI panel**. That is the atlas's job, identical in kind to
a shop row.

**And it is the data C3's mining designs have no source for.** The concepts rank
rocks by what they become; nothing on disk says what a specific rock actually
assayed at. **A player scanning rocks for a week produces a real distribution
that no other tool in this hobby holds.**

**Refinery yields and times sit on the same panel family** and are equally
missing from every dataset we have.

### Weapons on the ground — TIER 2, and TIER 3 is impossible
    fps-items.json      5,420 entries
      WeaponPersonal      458      Char_Armor_Helmet    673
      Char_Armor_Torso    473      Char_Armor_Legs      462

**We hold every FPS weapon and armour piece by NAME and STAT. We hold zero
models of any of them.** The Fan Kit is ships.

**So visual recognition of a gun on the floor is off the table** — there is
nothing to train against. **But the inspect panel names it**, and that name
joins to 5,420 records we already have. **Reading the label is the whole
feature, and it is cheap.**

### Faction armour — TIER 2, same reason
Armour carries a name and the name carries the faction. **Read the name, look it
up.** No model exists to recognise the suit by sight.

### Factions, security forces, NPC groups — TIER 1 + TIER 2
**The log already records ship classes and what killed you** — 992 classes, 131
deaths, 18 vehicles destroyed. Much of "which security force operates here" is
answerable from that without a camera.

**And the HUD labels a target when you target it.** Affiliation, name, and
hostility are drawn as text. **A hostile you have targeted is a text problem.
Only the ones you have NOT targeted need Tier 3.**

## 4. WHAT SLEVEN DID NOT LIST AND I WOULD PUT ABOVE MOST OF IT

**Shop stock levels — the one thing the log genuinely cannot see.** The log
records what YOU bought. It cannot record what was on the shelf and left there.
**Stock, and the price of things you did not buy, is the entire argument for a
screen reader existing at all.**

**Where a ship is actually sold.** The site's tagline is *"Know where to buy,
before you fly"* and its dealer data is unverified. **A player walking a ship
dealer's floor produces exactly that, and it is the site's founding promise.**

**Station and outpost amenities** — refuel, repair, rearm, medical, which shops,
which terminals. **No dataset we hold answers "what can I actually do here",
and every player wants it.**

**Elevator and transit destinations.** Pure text on a panel, and it is the
navigation data every new player is lost without.

**Mission board contents by location** — the log records payouts already;
the board shows what is offered before you accept.

## 5. WHAT MAKES THIS EXTENSIBLE RATHER THAN TEN PROJECTS

**One pipeline, many recognisers.**

    capture  ->  context  ->  regions  ->  reader | matcher  ->  vocabulary  ->  row
               (what am I     (where is    (atlas)  (Tier 3)     (exact hit
                looking at)    the text)                          or discard)

**Only the last two boxes differ per subject.** A new thing to capture is a
DEFINITION - which screen, which regions, which vocabulary to hit against - not
new plumbing.

**AND THE PROJECT'S OWN RULE APPLIES: build 2-3 concrete recognisers before
generalising the pipeline.** Shop kiosk, mining scanner, ship dealer. Three real
ones, then look for what they share. **Do not build the plugin framework first.**

## 6. TIER 3, HONESTLY — THE ONE FEATURE THAT NEEDS PIXELS

**Ships in space is the only item on this page that genuinely requires object
recognition, and it is the one Sleven has decided to build.**

**We hold 258 ship models.** That is the advantage almost nobody attempting this
has: labelled training data can be GENERATED, thousands of angles per hull, by
the same rig that photographed all 295 ships for the marker work.

**The real risk is not the models. It is the gap between a rendered hull and a
game frame** - engine lighting, effects, atmosphere, distance, occlusion.
**That gap is what would sink it, and it is measurable early:** can it tell a
Vulture from a Gladius in one real screenshot? Two hulls, opposite shapes. Days,
not months, to find out.

**And note what Tier 2 takes off its plate.** A targeted ship is labelled by the
HUD. **Tier 3 only has to handle the ships nobody has targeted** - which is a
much smaller, and much more honest, claim.

— C1
