# FINDING — special editions, paints, and the thing the site's model cannot express

C1, 2026-08-02. All figures measured from snapshot `20260801T204744Z` and UEX snapshot `20260801T235530Z`. Interpretation is marked where it appears.

---

## 1. The special editions are neither new ships nor paint

73 edition/base pairs were compared field by field — hull, mass, dimensions, cargo, crew, slot count, and every fitted component.

```
53   differ ONLY in which components are fitted
18   mechanically identical to the base ship
 2   also differ in cargo capacity
```

**Same hull. Same slot count. Same dimensions. 7 to 11 components swapped.**

```
Sabre Firebird Wikelo War Special      11 of  67 slots refitted
Apollo Triage Wikelo Sneak Special     11 of 120
Asgard Wikelo War Special              10 of 106
Ares Inferno Wikelo War Special         9 of  66
Ares Ion Wikelo Sneak Special           9 of  66
Zeus Mk II ES Wikelo Work Special       9 of 109
```

So a "War Special" is the ship with military-grade parts already fitted. A "Sneak Special" is the same hull with stealth parts. **They are factory loadouts, not variants.**

**The 18 that are mechanically identical** are the cosmetic ones: every Best In Show edition, the three ATLS gradient colours, the CitizenCon 2948 Mustang, the Caterpillar Pirate, the F8C Platinum, and four Teach's Specials (Fortune, MOLE, Reclaimer, Vulture).

**"Teach's Special" is not one thing** — some are refits, some are paint. Do not treat the label as a category.

---

## 2. Wikelo is a real place, and it does not sell ships for aUEC

Three terminals exist in UEX:

```
709   Wikelo Emporium Dasi Station     type: fuel
710   Wikelo Emporium Kinga Station    type: fuel
711   Wikelo Emporium Selo Station     type: fuel
```

**Zero ship prices at any of them.** Not a missing-data gap — the terminals are typed `fuel`, and no vehicle price row references them.

Contrast Teach's, which is already a column on the matrix:

```
145   Teach's - Levski                 type: item
789   Teach's Rentals - Levski         type: vehicle_rent
790   Teach's Item Shop - Levski       type: item
791   Teach's Ship Shop - Levski       type: vehicle_buy   ← 38 ships priced here
```

**So: Wikelo is a location the site does not know about, offering ships the site does not list, at no aUEC price.** How they are actually obtained is not in any file we hold. Do not publish a claim about it until someone verifies it in game.

---

## 3. Paints attach to ships mechanically — no name matching needed

1,077 paint records in `ship-items.json`, each carrying a `required_tags` field that names its ship directly:

```
Hornet Mk II Canopy Camo Livery    →  Paint_Hornet_F7_Mk2
Hull C Dusk Livery                 →  Hull_C_Paint
Reclaimer Dolivine Livery          →  Paint_Reclaimer
```

**This is the same quality of join as the UUID key** — structural, not a heuristic. Paints can be attached to ship pages without a single name comparison.

And each carries **how you get it**, in `event_source`:

```
589  none recorded          49  IAE                32  Invictus Launch Week
 66  Concierge              42  Event Reward       28  Best In Show
 50  Subscriber             34  Luminalia
```

---

## 4. The finding that matters most — the site's model cannot express any of this

The ship matrix has dealer columns: Area18, Orison, Lorville, Levski, Ruin Station. That model answers exactly one question — **which shop sells this for aUEC.**

It cannot express:

- a ship obtained at Wikelo Emporium for something other than currency
- a livery that comes from being a Subscriber, or from attending IAE, or from Luminalia
- a factory loadout that arrives fitted rather than bought
- a Best In Show edition awarded rather than sold

**That is 40 Wikelo ships, 7 Teach's specials, 9 Best In Show editions, 11 PYAM Execs and 488 paints with a recorded source — none of which the site can currently describe.**

The site's stated purpose is *"know where to buy, before you fly."* The honest generalisation of that is **"know how to get it"** — and *bought at a shop* is one route among several rather than the only one.

**This is worth settling before Build A generates twenty thousand pages**, because "where to buy" is baked into every template if nobody widens it first.

---

## 5. Recommended treatment — three things, three places

**Factory loadout variants (53).** Not matrix rows — same ship, same hull, same price. A **stock loadout selector** on the ship page: Standard / War Special / Sneak Special / Work Special, which swaps the fitted components and opens the loadout bench with that build loaded.

**This makes the special editions the loadout bench's first real content**, and it answers the most natural question anyone would ask of an A/B comparison: *what does the War Special actually give me over stock?* The bench currently has one ship and invented parts; this gives it 53 real, meaningful comparisons on day one.

**Cosmetic editions (18) and paints (1,077).** The same thing, treated the same way: a **liveries strip** on the ship page, grouped by `event_source` so the answer to "can I still get this" is visible. A Best In Show edition and a Luminalia livery are the same kind of object.

**Acquisition route.** A field on the thing itself, not a column on a table. Bought with aUEC at a named shop · pledged with real money · traded at Wikelo Emporium · awarded at an event · Subscriber or Concierge reward · fitted at the factory.

**The dealer columns stay** — they are the right answer for the 219 ships they describe. They just stop being the only answer.

---

## 6. What is verified and what is not

**Verified from data:** the 73 pair comparisons and every count in sections 1–3. The Wikelo terminal records and their type. The absence of vehicle prices at them. The paint `required_tags` and `event_source` distributions.

**Not verified:** how Wikelo ships are actually acquired in game. The data says the terminals exist and no aUEC price references them. Everything beyond that is inference and must be confirmed by someone who has been there before it goes on a page.
