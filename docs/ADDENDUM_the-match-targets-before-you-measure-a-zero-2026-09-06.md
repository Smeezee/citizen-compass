# ADDENDUM 2 — the §8 match test aims at the wrong tables and will report a zero that means nothing. Read this before running it.

    from      C1, 2026-09-06
    for       Code
    amends    §8 of docs/ORDER_the-observations-table-and-the-exact-resolver-2026-09-06.md
              and §8 of docs/ADDENDUM_the-log-miner-is-the-first-writer-...-2026-09-06.md
    method    read the actual key strings out of
              citizen-collector/captures/gamelog-dataset.json and the target
              columns out of app/models.py. Both, before asking for the number.

**Nothing about the tables, the constraints or the resolver changes. This
corrects only what gets compared to what, and it protects you from reporting a
zero as a result.**

---

## 1. What the log's names actually look like

I asked you to match 992 ship names and 542 equipment names against
`shop_items.name`. I had not looked at either. They are not display names.

    ship_classes        AEGS_Avenger_Stalker
                        AEGS_Avenger_CML_Chaff
                        AEGS_Avenger_SCItem_Seat_Pilot

    equipment_seen      987_jacket_01_01_01
                        Drink_bottle_cruz_01_dark_a
                        Carryable_1H_CU_Glowstick_Pink

    locations           Nyx_Levski        GrimHEX      RR_ARC_L1
                        INVALID_LOCATION_ID

    shop_class_names    CEntityComponentShopUIProvider::SendShopBuyRequest

**`shop_items.name` is UEX's display name.** `AEGS_Avenger_Stalker` against
`Avenger Stalker` is not a near miss to be loosened - it is **a different naming
space**, and matching them by similarity is precisely the thing rule 17 forbids.
Run as written, §8 returns approximately zero and the zero says nothing about
either dataset.

**`shop_class_names` are not shops at all.** They are C++ method names the
extractor keys on. **Do not compare them to anything.** That one is my error in
reading the file's structure, and it would have looked like 18 unmatched shops.

## 2. The targets that are real, per name space

**`equipment_seen` -> `components.class_name`.** That column exists, is
`String(150)`, `NOT NULL`, and carries `uq_components_class_name`. It is a class
name matched against a class name, same space, exact equality, and it is the one
comparison in this whole exercise that should actually produce a number worth
having. **Measure this one.**

**Transaction `itemName` -> `shop_items.name`.** The 308 transactions carry
`itemName` alongside `client_price`, and that field is CIG's display name, so
this is the correct display-to-display comparison. **Measure this one too**, and
report it separately from the one above - they are different questions.

**Transaction `itemClassGUID` -> nothing yet.** A GUID is exact by nature and is
the strongest key in the whole dataset. **Report whether any table in this
database holds a CIG item GUID at all.** If none does, say so; that is a finding,
not a task.

**`ship_classes` -> THERE IS NO TARGET COLUMN AND THAT IS THE FINDING.** I
checked: `ships` has `name`, `ship_registry` has `ship_code`, `source_slug`,
`folder_slug`, and **neither has a class-name column.** `components` has one;
ships do not. So 992 real CIG ship class names observed in play have nowhere in
this database to land.

**Do not add the column in this order.** Report it. Whether ships get a
`class_name` is a schema decision that touches the loadout pipeline and the
hardpoint work, and it is not made inside a collector order.

**`locations` -> compare, but expect a low number and do not act on it.**
`locations` has `name`, `code` and `nickname`. `GrimHEX` may match; `Nyx_Levski`
and `RR_ARC_L1` almost certainly will not. **Exclude `INVALID_LOCATION_ID`** -
CIG's own null marker, and counting it as an unmatched location would be
counting a non-thing.

## 3. What §8 should report, replacing what it said

Six numbers and one sentence, all separate, none combined into a rate:

    1. shop_items rows, and distinct shop_items.name
    2. terminals rows, and distinct terminals.name
    3. components.class_name exact matches against equipment_seen (of 542)
    4. shop_items.name exact matches against transaction itemName
    5. locations matches against the log's locations, INVALID_LOCATION_ID excluded
    6. whether any table holds a CIG item GUID

    plus: ships have no class_name column - confirm or correct that.

## 4. The one thing that must not happen

**A low number is not permission to loosen the matcher.** If (3) comes back at
5%, that is a statement about how much of the catalogue is missing, and the fix
is more catalogue or a cross-reference table - the project already has that
pattern in `shop_item_commodity_xref`, which links two id spaces **without
merging them and without guessing**.

Rule 17 does not have a threshold below which it stops applying. If a number
comes back bad enough to make fuzzy matching tempting, that is exactly the moment
it is most important that it stays refused. **Report the number and stop.**

---

*C1, 2026-09-06. I asked for a measurement without checking what was being
measured. The strings were on disk the whole time.*
