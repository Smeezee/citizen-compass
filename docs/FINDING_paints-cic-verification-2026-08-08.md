# FINDING — CIC's paint sweep is good store work, and its one big conclusion is wrong for us. We already hold the "retired" paints it says don't exist anywhere.

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1
    ask       Sleven forwarded CIC's 30-page sweep of the RSI pledge store's paint catalogue.
    method    Standing rule: CIC's output is a claim until someone verifies it locally.
              Counted paints in BOTH data sources we hold, independently, and compared
              against CIC's store figures.

---

## 1. CIC's central claim, and the verdict

**CIC wrote:** *"genuinely retired/event-exclusive paints … simply aren't listed anywhere on
the live store once their sale window ends … For a truly exhaustive historical list of every
paint ever made, a community wiki is the better source."*

**That is true of the store and false of this project.** We already hold them, in two
independent sources that agree with each other:

    UEX snapshot 20260801T235530Z    1,099 livery rows
    game files  20260801T204744Z     1,077 Paints entries
    RSI store   (CIC, today)         ~480+ listings including packs

The two data sources land within 2% of each other. The store shows roughly half.

**Cross-check inside our own UEX data, which settles it:** of the 1,099 liveries, **601
carry a live store URL and 498 do not.** That 498 is exactly the "retired, no longer sold"
class CIC was looking for — and the names are precisely the event exclusives it named as
unavailable:

    Cutlass Skull and Crossbones Livery      Nomad Lovestruck Livery
    Caterpillar Deck the Hull Livery         Cutter IceBreak Livery
    Vulture Deck the Hull Livery             Freelancer IceBreak Livery
    Prospector Deck the Hull Livery          Cutter Deck the Hull Livery

Luminalia ("Deck the Hull"), the IceBreak event, Valentine's ("Lovestruck"), pirate-week
("Skull and Crossbones"). **No community wiki needed. Do not authorise that scrape.**

**CIC's store work is not wasted and should not be discarded** — its 601-ish live count
corroborates our `url_store` field, which nobody had validated against reality before. That
is a genuine cross-source confirmation and worth keeping. The error was only in the
conclusion about what exists elsewhere, which CIC could not have checked from a browser.

## 2. `Paints` is the single largest item type in the game files

Worth stating on its own, because it reframes how big this category is. Counted across all
5,384 `ship-items.json` records:

    1,077  Paints          <-- largest single type in the file
      885  ManneuverThruster
      381  MainThruster
      320  WeaponAttachment
      317  Turret
      202  WeaponGun

Paints outnumber every weapon type combined. A "liveries are a category off by default"
decision is defensible for UI noise, but this is not a fringe dataset.

## 3. The ship link exists and is strong — 993 of 1,077

Each paint carries `RequiredTags`, which is the mechanical link to the hull it fits:

    Hornet Mk II Canopy Camo Livery   -> ['Paint_Hornet_F7_Mk2']
    Reclaimer Dolivine Livery         -> ['Paint_Reclaimer']
    Hull C Dusk Livery                -> ['Hull_C_Paint']
    Hermes Navarra Livery             -> ['Paint_Hermes']

**993 of 1,077 (92%) have it; 84 do not.** So "which ships can wear this paint" is
answerable from data we hold, on a real identifier, not a name match. This confirms the
mechanism `CURRENT-STATE.md` already asserted, and puts a number on it for the first time.

## 4. Where our data is genuinely weaker than the store — stated plainly

Not everything favours us, and pretending otherwise would repeat exactly the mistake this
project keeps logging:

- **No images. At all.** `screenshot` is an empty string on all 7,728 UEX items (already on
  record). The store has the pictures; we have the names. **This is the real gap, and it is
  the same open rights question from this morning** — whether a product-page image is usable
  is Sleven's call, unchanged.
- **Attribution is patchy.** 402 of 1,099 UEX livery rows have no `vehicle_name`, and 571
  have no `game_version`. The game files' `RequiredTags` is the better join; UEX's
  `vehicle_name` should not be trusted as the primary key.
- **No prices for most.** Prior census: Liveries 19 priced out of 1,099.
- **Store-only facts we cannot derive:** current USD price, live discounts, "New" and
  "Limited Time" flags, and pack composition. If those matter, that IS CIC's lane and its
  sweep is the right instrument.

## 5. Rights caution before anyone builds on this

The game-file paint entries carry a **CIG-written `Description` field** (e.g. *"Get in close
for the kill with the Canopy Camo livery…"*). That is the same class of material frozen
under `claude/finding-description-rights-correction.md`. **Names, tags, ship links and
counts are facts and are fine. The description text is not cleared and must not ship**
until Sleven settles it. Flagging, not deciding — rule 8.

## 6. Recommendation

1. **Do not commission a wiki scrape for historical paints.** The gap CIC identified is
   already closed by data on disk. This is the third time on this project that a declared
   gap turned out to be a file nobody opened.
2. **Keep CIC on the store**, for the things only the store has: USD price, discount state,
   pack composition, and the Limited Time / Premium / Standard tags. That is a genuine,
   non-duplicative lane.
3. **Build the paint dataset off `RequiredTags`**, not UEX `vehicle_name`, and carry
   `url_store` presence as the "currently purchasable" flag — it is already proven to
   separate live from retired.
4. The 84 paints with no `RequiredTags` are the residue to classify by hand, same method as
   `ship_resolution.json`. Small enough to be tractable.

## 7. What I did not check

- Did not verify CIC's individual per-ship lists ship by ship; I checked its overall
  conclusion and its live-vs-retired split, which is what the decision turns on.
- Did not open any paint's store page and did not fetch any image.
- Did not touch the repo, the DB, or any site code.
- Have not confirmed whether the 498 no-store-URL rows are *all* genuinely retired versus
  some being unreleased or data gaps — the named examples are unambiguous, the full 498 are
  not individually verified.
