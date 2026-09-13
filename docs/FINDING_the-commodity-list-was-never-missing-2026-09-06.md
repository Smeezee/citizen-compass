# FINDING — the collector's "one genuine blocker" is not a blocker. CIG ships the commodity list and it is on Sleven's disk.

**C1, 2026-09-06.**

## What was on record as blocking

C3's consolidated collector spec names three open questions and calls one of them
the only real blocker:

> There is no commodity name list. All 23,734 price rows held are gear and
> components. Commodity kiosks are the first real target and we would be matching
> against a list we do not hold. The source calls this the one genuine blocker and
> says pull the UEX commodity catalogue ahead of everything else.

## It is in the snapshot we already have

`data-layer/external-sources/scunpacked-data/snapshots/20260827T225641Z/labels.json`
— CIG's own strings file, 90,363 entries, sealed in this repo since 27 August.

    keys under items_commodities_        552
      of those, descriptions (_desc)     221
      the rest                           331
    distinct commodity NAMES             277

Agricium, Aphorite, Bexalite, Laranite, Quantainium, Titanium, Medical Supplies,
Construction Materials, Consumer Goods, Waste, Scrap — with the ore, raw and
refined variants CIG distinguishes (*Agricium* against *Agricium (Ore)*), which a
kiosk read has to tell apart and a third-party list often flattens.

**And the 42 category labels come with it** — Metal, Mineral, Gas, Food, Drink,
Vice, Alloy, Scrap, Waste, Quantum Fuel, Hydrogen Fuel, Medical Supply, Military
Supply, Agricultural Supply, Processed Goods, Consumer Goods, Natural Materials,
Recycled Material Composite. So a read resolves to a name **and** its type.

## Why nobody found it

The obvious place to look is `items/`, and the 33 `cargo_comm_*.json` item files
there all carry `<= PLACEHOLDER =>` as their name. **Looked at from the item
files, the list genuinely is not there.** The names live in the labels file
instead, keyed separately from the items that use them.

## What this changes

**Do not pull the UEX catalogue.** CIG's own file is better on every axis that
matters here — it is first-party, it is already sealed in a dated snapshot with
the rest, it carries the category, it re-derives on every future snapshot, and it
needs nobody's permission.

**Two of the three "blockers" now look answerable from material already on this
machine** — this one from the snapshot, and the font and aUEC-balance questions
from Sleven's own screenshots, which he says show both. The third-party dependency
that was about to be taken on was not needed.

## What was NOT done

**No list has been extracted and no file has been written.** The 277 is a count
from a read, not a built artifact. Roughly a dozen of the 331 non-description
keys are noise — a stray description that lost its suffix, a size-qualified entry
like *Atlasium (8 SCU)*. **A real extraction needs a filter pass and a human
looking at the output**, and it belongs in the collector's build, not in a
finding.

Nothing about how a kiosk is read, or what the reader does with a name once it
has one, is touched here.

*C1, 2026-09-06.*
