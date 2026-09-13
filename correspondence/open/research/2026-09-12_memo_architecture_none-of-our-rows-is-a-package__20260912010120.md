# Memo

To:      Architecture
From:    Research
Date:    2026-09-12
Subject: NONE of our 253 rows is a package. RSI keeps packages in a different catalogue entirely. What we have instead is ten ships that ship WITH other vehicles — and the deciding field comes back clean, 8 of 8.
Status:  Answered
**All 253 rows read individually off RSI's own pledge store today. Nothing from a wiki,
tracker or aggregator. Nothing under `/media/`. No contact with CIG.**

Data file: `claude/CIC_rsi-packages-and-contained-vehicles-2026-09-12.md`.

---

# THE ANSWER TO THE QUESTION AS YOU ASKED IT: ZERO

**Not one of the 253 is a package product.** The premise that some of our rows are
packages does not survive contact with the store.

**RSI keeps the two in different catalogues at different paths:**

    ships     /pledge/ships/<family>/<ship>              all 253 of ours
    packages  /store/pledge/browse/game-packages         14 products, none of them ours

The package catalogue held **14 products** on a single page — Citizen Starter Pack,
Ultimate Explorer Pack, Industrial Pack, Escort Pack, Convoy Pack, Multicrew Pack, Dominus
Pack, Praetorian Pack, five more. **Checked mechanically against our 253 names: zero
overlap.**

**So there is nothing to fold, nothing to split and nothing to flag as redundant.** Pass 1
pulled from the ships catalogue and the ships catalogue only contains ships.

---

# WHAT IS ACTUALLY THERE, AND IT IS A DIFFERENT SHAPE THAN YOU PLANNED FOR

**Ten rows are single ships whose own listing says other vehicles come with them.**

    Carrack                          C8 Pisces + Ursa
    Carrack Expedition               C8 Pisces + Ursa
    Carrack w/C8X                    C8X Pisces Expedition + Ursa
    Carrack Expedition w/C8X         C8X Pisces Expedition + Ursa
    Constellation Andromeda          P-52 Merlin
    Constellation Aquila             Ursa + P-52 Merlin
    Constellation Phoenix            Lynx + P-72 Archimedes
    Constellation Phoenix Emerald    Lynx + P-72 Archimedes
    600i Explorer                    G12
    890 Jump                         85X

**This is a relationship between two rows, not a product type.** It wants an edge —
`contains(ship_id → vehicle_id, source_quote, last_verified_patch)` — not a `is_package`
boolean and not a separate table.

## THE FIELD YOU SAID DECIDES IT — CLEAN, 8 OF 8

You said the last field decides what we do with it, and to say so loudly if a package
contains something we do not carry.

**There is nothing to say loudly.** Every vehicle named as included is already its own row
in our 253: C8 Pisces, C8X Pisces Expedition, Ursa, P-52 Merlin, Lynx, P-72 Archimedes,
G12, 85X. **Eight named, eight present.** Every containment points at a row we already
have.

## AND IT SETTLES THE THING YOU LEFT HANGING ON 2026-09-12

You asked me to note that the "cosmetic ship, functional package" question hangs on
`Carrack w/C8X` and `Carrack Expedition w/C8X` too. **It does, and the store now answers
the factual half:**

**The base Carrack is itself one of the ten.** It is not a plain ship that the w/C8X rows
bundle things onto — RSI's own bullet says the base Carrack comes with a Pisces and an
Ursa. **The four Carrack rows differ from one another in exactly two ways: which Pisces is
named (C8 or C8X), and whether there is a limited edition livery.** Same hull, same
weaponry, same role, same Ursa.

**The judgement remains yours or his.** But it is no longer "one plain ship and three
bundles" — it is four rows of the same ship differing by livery and by which snub comes
with it.

---

# A SECOND, OPPOSITE THING I FOUND — DO NOT LET THESE MERGE

**Fifty-three rows carry RSI's own sentence: "This vehicle is only available as part of a
PACKAGE."**

**That is the reverse of containment and the two must never share a field.** It does not
say the row contains anything. It says RSI will not sell you that ship on its own right
now — Idris-P, Javelin, Polaris, Hammerhead, Merchantman, Reclaimer, Retaliator, Sabre,
Valkyrie, Hull-C, Hull-E, and 42 others. Full list in the data file.

**Three rows are both**: Carrack, Carrack Expedition and 890 Jump contain vehicles *and*
cannot be bought alone.

**This is availability and availability moves.** It belongs with `last_verified_patch` and
the front end's unverified flag, not as a property of the ship. **I am recording it, not
recommending a schema for it.**

---

# ONE THING THAT WILL BITE AN IMPORTER, AND I HAVE NOT TIDIED IT

**Capacity language reads exactly like containment and is not containment.** The Idris-M is
"capable of accommodating two medium fighters and a small ground vehicle". The Galaxy:
"small ships and ground vehicles can be housed in the rear onboard hangar". The Tyilui has
"four pads … for snub ship transportation". The Liberator "offers extreme-range deployment
for light and medium fighters".

**None of those ships comes with anything.** They describe what fits.

**Any automated extraction over these descriptions will pull all four in as packages.**
They are excluded here by reading, deliberately, and they are listed in the data file so
nobody re-derives them later and reaches the opposite answer.

Same for loadout language — "Includes a Size 1 shield", "comes with a pair of
Behring-quality lasers", "includes an optional missile pod". Components, not vehicles.

---

# A METHOD FAILURE OF MINE THAT THE OTHER DESKS SHOULD HAVE

**My first pass over all 253 was wrong on six rows and reconciled perfectly.** The phrase
test required a sentence-ending full stop; RSI's bullet lists have none; the bullets are
where containment is declared. Andromeda, Aquila, 600i Explorer, 890 Jump and both w/C8X
rows all came back as "no containment language" and all six have it.

**The rider we adopted — reconcile against a known list — did not catch it and could not
have.** Reconciliation proves every row was read. It says nothing about whether the right
question was asked of each row.

**The addition: a sweep needs one row whose answer is known from outside the sweep,
checked against what the sweep said about it.** One known positive, one known negative, one
page of cost. Written up as
`claude/FINDING_reconciliation-proves-coverage-not-correctness-2026-09-12.md`.

I discarded the whole first pass rather than patch it and re-read all 253.

---

# WHAT I DID NOT DO

**I did not sweep the package catalogue's contents.** What is inside those 14 products is a
separate job with its own reconciliation, and nobody has asked for it.

**I did not look at packages RSI has withdrawn.** The 14 are what is offered today. Whatever
historic package a `Carrack w/C8X` once came from is not on that page and I am not
inferring it.

**I decided nothing, recorded no package price, and inferred no package from a name.**

*CIC, 2026-09-12.*

---

ANSWERS: Settled by primary source on 2026-09-12. Sleven opened RSI's Carrack Expedition
page himself and read the variant matrix. The Carrack Expedition matches the base Carrack
on every published field — manufacturer, focus, description word for word, production
state, 126 m / 74 m / 30 m, Large, 3,275,858 kg, 456 SCU, 140 m/s, 1,050 m/s, crew 6,
1x Surveyor (S2), 2x Internal Tank, 1x Kama (S3), 1x Internal Tank, 1x Exodus (S3). The
only differing field is the ship value. RSI's own words for the difference: a limited
edition livery. It is an EDITION and it folds, so Sleven's conclusion that the separate
card is unnecessary stands — on new grounds, not the ones he gave.

Research's sweep was correct and its headline was too narrow. None of our 253 rows is a
package because RSI keeps packages in a separate catalogue at a separate path, which was
never swept. WE CARRY NO PACKAGES. "Packages containing this ship" has no data behind it
and is not built; sweeping that catalogue is a separate job with its own reconciliation
and has not been ordered.

What the read produced instead is a THIRD RELATIONSHIP neither side had named: ten of our
ships COME WITH other vehicles, and all eight contained vehicles are already rows we
carry. Neither edition nor package — a link between two rows that both exist, and the
cheapest high-value item on the board. Separately, 53 rows carry RSI's own sentence "only
available as part of a PACKAGE", which is availability, moves, and is not a property of
the ship.

Method rule adopted, found by Sleven: a marketing render is never evidence of a variant
difference — RSI reuses art across SKUs. A ship's relationship to other ships is read from
the bullet list, never the description, the name or the picture.

Full ruling: claude/RULING_the-carrack-answered-from-rsi-itself-2026-09-12.md
