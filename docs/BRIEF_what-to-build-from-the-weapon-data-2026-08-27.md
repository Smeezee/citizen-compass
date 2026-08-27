# BRIEF — six things worth building from what today's weapon work found. One of them is a sentence, and it may be the most valuable thing on the site.

    from      C3 (Cowork), 2026-08-27
    for       C1 + Sleven
    ask       Sleven: "how can we use what we have and make it better with all
              of this info"
    basis     today's three findings - the weapon taxonomy, the 4.9-vs-4.10 data
              gap, and the damage interaction being computable.
    status    ideas, ranked. Nothing built, nothing scheduled.

---

## 0. The one-line version

**Every other Star Citizen tool answers "what are this weapon's numbers." We can
answer "what will this weapon do to that ship, and is it worth building instead
of buying." Nobody else can, because nobody else joined these three datasets.**

## 1. SHIP THIS FIRST, AND IT IS A SENTENCE

**A shield stops all of a laser's damage and only 45% of a ballistic's.**

That is CIG's own number, identical on all 67 shields, and **a new player does not
know it.** It is the single most useful fact in everything measured today and it
costs nothing to publish — no calculator, no join, no new data.

**Put it in plain words where somebody choosing a weapon will read it.** Not as a
stat block. As the sentence above.

**Everything else in this document is a way of showing that same fact in more
detail.** If only one thing ships, ship the sentence.

## 2. Effective damage against a real target — the feature nobody else has

Every tool shows DPS in isolation. **DPS in isolation is not what a player wants
to know.** They want to know whether this gun gets through that ship.

We hold every link:

    the gun's damage, split by channel
    the shield's absorption, per channel
    the armour's multiplier, per channel
    the item's own resistance, per channel

**So a weapon can be shown against a chosen ship rather than against nothing.**
"1,266 DPS" becomes "roughly half of it reaches the hull while shields hold."

**This is the loadout bench's reason to exist.** It already knows the ship and the
fitted weapons. It is one arithmetic step from telling a person something no other
tool tells them.

**BLOCKED ON ONE THING, and it must not be skipped:** shields carry a
`Resistance` block as well as `Absorption` and **nobody has established whether
they stack or which applies when.** Publishing a confident wrong number here is
worse than publishing DPS. **Resolve that first, from the client, not by
assuming.**

## 3. Craft or buy — a decision nobody answers

We hold **1,597 recipes** with ingredients, quantities in SCU and craft times. We
hold **UEX prices** joined on real game UUIDs.

**Nothing on the internet puts those two side by side.** A player deciding whether
to build a gun or buy one has to work it out by hand across two sites.

    this gun:  ~21,500 aUEC at CenterMass, Area 18   (UEX, dated)
    or:        9 minutes, Agricium + Hadanite + Dolivine

**That is a real decision people make**, and it is a straight join of two datasets
we already have.

**Worth knowing before it is scoped:** only about 14% of ship weapons are
craftable at all, so most rows show a price and no recipe. **That is honest and
fine — but the page must not look broken on the 86%.**

## 4. "You cannot craft this" is a feature, not a gap

**Missiles, launchers, turrets and countermeasures have ZERO recipes.** Not one.

Somebody hunting for a missile blueprint is hunting for something that does not
exist. **Saying so plainly saves them the hunt** — and stating a confident absence
is exactly what this project is already good at and most fan sites are not.

**Same for the three dead damage channels.** Thermal, Biochemical and Stun are
zero on every gun, absorbed fully by every shield, and some armour is outright
immune. **Say they are unimplemented. Do not render three empty columns.**

## 5. Date the claim, because 4.10 just proved why

**CIG confirmed the energy-versus-shield bonus was broken and that 4.10 fixed
it.** So every guide, video and forum post written during that window describes
behaviour that was a bug.

**We are the only project positioned to say that**, because we already stamp
`last_verified_patch` on every row and CIC has the patch notes.

**A line like "this changed in 4.10" beside a number is worth more than the number
being slightly more precise.** It is also the "what changed" idea from the
Historian work, shippable now, without the Historian.

**And it is a warning to ourselves:** the 45% figure in §1 is 4.9-era, and 4.10
changed how armour mitigation is applied. **Re-measure before publishing it, do
not just carry it forward.**

## 6. The cheapest fix in this document — one manifest field

Today's confusion happened because **no build string exists anywhere inside a
snapshot's files**, and our manifest records the commit hash and date but not the
commit MESSAGE — which is the only place the patch version lives.

    20260801T204744Z    4764726...   2026-07-16    <- 4.9, invisible
    20260827T030607Z    db00b74...   2026-08-20    <- 4.9, invisible

**Add `git_commit_subject`. One field.** Then every future snapshot says which
patch it is, on its own face, forever.

**Do it before the 4.10 pull**, so the pull records what it is rather than needing
somebody to go and look it up afterwards.

## 7. Sequencing, and why this order

    1  the manifest field           minutes, prevents the whole class of error
    2  pull 4.10 and re-diff        everything below is 4.9 until this happens
    3  the sentence in §1           costs nothing, highest value per word
    4  "cannot be crafted" flags    absence stated, no arithmetic, no risk
    5  craft-or-buy                 a join of two datasets we hold
    6  effective damage             LAST, and only after the stacking question

**Six is last on purpose.** It is the best feature here and the only one that can
be confidently wrong. **Everything above it is either a fact we can state or an
absence we can state, and neither can mislead.**

## 8. What I checked and what I did not

**Checked:** every figure quoted here against the datasets on disk today - the 67
shields, the 91 armour plates, the 1,597 recipes, the craftable percentages by
weapon type, the absent build strings in both snapshots.

**Did NOT check:**
- **Whether Absorption and Resistance stack.** §2 is blocked on it and I did not
  resolve it. **It is the single most important open question in this document.**
- **Whether any of these numbers survive 4.10.** Armour mitigation changed in the
  patch. **Assume the armour half of §2 is stale until re-measured.**
- **Whether a visitor wants any of this.** No question log exists yet. Every
  ranking above is my judgement of what a new player asks, not a measurement of
  what they ask.
