# Memo

To:      Research
From:    Engineering
Subject: New category, nobody has counted it — which of our 253 rows are PACKAGES rather than ships. Three are named; the rest are unknown.
Status:  Answered
**Sleven ruled today that a PACKAGE is a third category, separate from an edition.**

    an EDITION   the same ship, changed — paint, trim, or a different loadout
    a PACKAGE    several ships sold together, none of them changed, and we
                 already carry every one of them as its own row

**The Carrack Expedition is a Carrack, a Pisces and an Ursa.** It was sitting in the
editions audit being tested cosmetic-or-functional, and that test was never the right
instrument for it. **Your own note is what exposed it** — you flagged that it did not fit
the test cleanly and said to read it before applying it. Correct call.

## THE JOB

**Which of our rows are packages?** Same material, same method as your roles sweep —
RSI's own store, nothing from a wiki, tracker or aggregator, nothing under `/media/`.

**Named already, do not re-derive:** `Carrack Expedition`, `Carrack w/C8X`,
`Carrack Expedition w/C8X`.

**For each row you find:**

    the row as WE name it
    RSI's own product name
    the ships it contains, by name, as RSI lists them
    the package's own store URL
    whether every contained ship also exists on the store as its own product

**The last field is the one that decides what we do with it.** A package whose contents we
already carry separately is redundant on our page. **A package containing something we do
NOT carry is not redundant at all, and is the interesting case** — say so loudly if you
find one.

## WHAT NOT TO DO

**Do not decide anything.** Do not say which should be dropped, do not fold anything, do
not recommend. **The card treatment is an open design question in his tray.**

**Do not record a package price.** Not needed and we do not track them.

**Do not infer a package from the name.** "Expedition", "w/", "Pack", "Bundle", "Combo"
are hints, not evidence — the store listing is the evidence. **A row that looks like a
package and is a single ship on the store is a ship, and finding one is worth reporting.**

## ONE THING FROM YOUR LAST SWEEP THAT APPLIES HERE

**Paginate alphabetically, not by weight.** Your own finding: `sortField=weight` returned
duplicate pages and silently dropped 38 of 253 ships, and the page count looked right.
**It is now a standing rider — a paginated sweep is not finished until it is reconciled
against a known list.** Reconcile against the 253-row Pass 1 list as you did before.

*C1, 2026-09-12.*

ANSWERS:

**None of the 253 is a package. The premise does not survive the store.**

Every row in Pass 1 is a vehicle product in RSI's **ships** catalogue. RSI keeps packages in
a **different catalogue at a different path**:

    ships     /pledge/ships/<family>/<ship>          all 253 of ours
    packages  /store/pledge/browse/game-packages     14 products, zero overlap with ours

Those 14 — Citizen Starter Pack, Ultimate Explorer Pack, Industrial Pack, Escort Pack,
Convoy Pack, Multicrew Pack, Dominus Pack, Praetorian Pack and six more — were checked
mechanically against our 253 names. **No row is in both.**

**So the five fields you asked for have no rows to fill.** There is no package store URL to
record for any of ours, because none of ours is a package.

## WHAT IS THERE INSTEAD — TEN SHIPS THAT SHIP WITH OTHER VEHICLES

    Carrack                        C8 Pisces + Ursa
    Carrack Expedition             C8 Pisces + Ursa
    Carrack w/C8X                  C8X Pisces Expedition + Ursa
    Carrack Expedition w/C8X       C8X Pisces Expedition + Ursa
    Constellation Andromeda        P-52 Merlin
    Constellation Aquila           Ursa + P-52 Merlin
    Constellation Phoenix          Lynx + P-72 Archimedes
    Constellation Phoenix Emerald  Lynx + P-72 Archimedes
    600i Explorer                  G12
    890 Jump                       85X

Verbatim quotes for all ten in
`claude/CIC_rsi-packages-and-contained-vehicles-2026-09-12.md`.

**THE DECIDING FIELD IS CLEAN, 8 OF 8.** Every vehicle named as included is already its own
row: C8 Pisces, C8X Pisces Expedition, Ursa, P-52 Merlin, Lynx, P-72 Archimedes, G12, 85X.
**Nothing contained is missing from our catalogue. There is no interesting case to shout
about.**

## THE THING THAT BREAKS YOUR MODEL, AND IT IS THE BASE SHIP

Your definition reads *"the Carrack Expedition is a Carrack, a Pisces and an Ursa."*

**The base Carrack is also a Carrack, a Pisces and an Ursa.** RSI's own bullet on the plain
Carrack page: *"Comes with two additional vehicles: Anvil's own Pisces snub and an RSI Ursa
Rover."*

**So the four Carrack rows are not one ship plus three bundles.** They differ from each
other in exactly two ways: which Pisces is named (C8 or C8X), and whether there is a
limited edition livery. Same hull, same weaponry, same official role, same Ursa.

**Containment is not a product type here. It is an edge between two rows we already carry** —
which makes it `contains(ship → vehicle, quote, last_verified_patch)`, not an `is_package`
flag and not a third table. **Stated as a consequence of the measurement; the card treatment
is still his.**

## A SECOND, OPPOSITE SIGNAL — KEEP IT AWAY FROM THE FIRST

**53 rows carry RSI's own sentence "This vehicle is only available as part of a PACKAGE."**
That says the reverse: not that the row contains anything, but that RSI will not sell that
ship on its own right now. Idris-P, Javelin, Polaris, Hammerhead, Merchantman, Reclaimer,
Retaliator, Sabre, Valkyrie, Hull-C, Hull-E and 42 others. Full list in the data file.
**Three rows are both** — Carrack, Carrack Expedition, 890 Jump.

**This is availability and availability moves.** It wants `last_verified_patch`, not a
property on the ship.

## YOUR "WORTH REPORTING" CASE, AND THE TRAP UNDER IT

**Four ships describe carrying capacity in language that reads exactly like containment and
is not:** Idris-M *"capable of accommodating two medium fighters and a small ground
vehicle"*, Galaxy *"small ships and ground vehicles can be housed in the rear onboard
hangar"*, Tyilui *"four pads … for snub ship transportation"*, Liberator *"extreme-range
deployment for light and medium fighters"*.

**None of them comes with anything.** They are excluded by reading, deliberately, and named
in the data file so nobody re-derives them and gets the opposite answer. **Any automated
extraction over these descriptions will pull all four in.**

## THE RIDER YOU CITED DID NOT CATCH MY OWN ERROR, AND COULD NOT HAVE

I reconciled — 253 read, 253 matched, 0 missing, 0 extra. **And six answers were still
wrong.** My phrase test required a sentence-ending full stop; RSI's bullet lists have none;
the bullets are where containment is declared. Andromeda, Aquila, 600i Explorer, 890 Jump
and both w/C8X rows all came back "no containment language" and all six have it.

**Reconciliation proves every row was read. It says nothing about whether the right question
was asked of each row.** The addition: one row whose answer is known from outside the sweep,
checked against what the sweep said about it. One page of cost.
`claude/FINDING_reconciliation-proves-coverage-not-correctness-2026-09-12.md`.

First pass discarded entirely rather than patched; all 253 re-read.

## NOT DONE

Did not sweep what is inside those 14 packages — separate job, separate reconciliation,
nobody asked. Did not look at withdrawn packages. **Decided nothing, recorded no package
price, inferred no package from a name.**

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

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

Duplicate of the same letter, created when two desks held this seat at once and the watcher renamed rather than overwrote. Closed as a duplicate; the answer is in the original.

*C1 (Claude-09), 2026-09-12.*
