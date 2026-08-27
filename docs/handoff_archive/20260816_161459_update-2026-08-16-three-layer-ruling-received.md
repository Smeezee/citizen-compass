# Update - received: a ship is a HULL, a CONFIGURATION, and a LIST of routes

Sleven's ruling of 2026-08-16, SETTLED. It replaces the single-field
recommendation in `docs/finding-editions-paints-acquisition.md` - the six routes
survive (shop, pledge, trade, award, subscription, factory), the "one field on
the ship" does not.

What I am about to do, and in this order:

1. Read what already exists - the finding it replaces, the 89 leftovers, the 18
   cosmetic editions, how paints attach through `required_tags` / `event_source`,
   and the ship model everything reads from.
2. Build the THREE CONCRETE CASES and nothing more:
   - Wikelo's Drake Clipper (4.10)
   - Wikelo's Aegis Tiburon (4.11)
   - one of the 53 component-only editions already in the data
3. Report what those three actually needed, and let the shared shape come out of
   that.

What I will NOT do, because the ruling says so explicitly:

- no schema designed before the three cases exist
- no bespoke row per giveaway
- no single acquisition value per ship

Nothing about the dealer matrix changes in behaviour: it becomes a view over
route = shop, answering the question it has always answered.

Noted and not forgotten: this touches the ship model everything reads from, and
it was taken now specifically because Build A will bake "where to buy" into
thousands of pages. Nothing is committed or deployed from this until the three
cases are real and reported.
