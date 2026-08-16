# DECISION — a ship is a HULL, a CONFIGURATION, and a LIST of ways to get it. Three layers, not one row.

    ruled by  Sleven, 2026-08-16, in session with C1.
    status    SETTLED. Build to this shape.
    replaces  the single-field recommendation in
                docs/finding-editions-paints-acquisition.md, which proposed an
                acquisition FIELD with six routes. The six routes survive. The
                "one field on the ship" part does not.

---

## The ruling

**Three layers:**

1. **The hull** — Aegis Tiburon. One record. The thing that has a shape, a
   model, and hardpoints.
2. **The configuration** — stock, or Wikelo's livery plus upgraded components.
   Same hull, different fit.
3. **The acquisition routes** — a LIST, attached to a configuration, not to the
   hull.

**The six routes stand:** shop · pledge · trade · award · subscription ·
factory.

**Acquisition is a list, not a label.** A Tiburon can be pledged for real
money, bought in a shop for aUEC, and handed out by Wikelo with a special
livery. Three routes to one hull, two configurations. A single field cannot
express that and would force a choice that is simply wrong.

## Why now, and why this shape

**Wikelo reward ships are a per-patch pattern.** CIC established it from CIG's
own roadmap on 2026-08-16: 4.10 gives a Drake Clipper with "a unique base
livery and upgraded components as a reward for completing a Wikelo's Emporium
contract", and 4.11 gives an Aegis Tiburon under identical wording. **Not new
hulls. Configurations of existing ones, with a distinct acquisition route.**

CIC's own recommendation, independently reached: model generically — base hull
plus livery plus component loadout plus acquisition source — rather than adding
two bespoke rows.

**This is the second independent argument for the same thing.** The first was
the 89 leftover game files: 53 differ from their base ONLY in fitted
components, and 18 are mechanically identical and differ only cosmetically.
Those were already established as **factory loadouts, not variants**. They are
configurations, and they have been waiting for somewhere to live.

## What this collapses

Four problems become one shape:

- **The 89 leftovers** stop being unexplained ships and become configurations
  of hulls the site already has.
- **The 18 cosmetic editions** stop needing rows of their own.
- **Paints** stop being awkward. They already attach via `required_tags` and
  already carry `event_source` — Concierge, Subscriber, IAE, Luminalia, Best In
  Show. Those are acquisition routes wearing a different name.
- **Every future Wikelo giveaway** is one new configuration, not a new ship and
  a new special case.

**The alternative was explicitly rejected:** a single acquisition label on the
ship means a bespoke row every patch, forever. That is the thing CIC warned
about and it is the thing this ruling exists to prevent.

## What the dealer matrix becomes

Unchanged in behaviour. It is a **view over route = shop**. It answers the one
question it has always answered — which shop sells this for aUEC — and it stops
being asked to describe a ship traded at Wikelo, a livery from a subscription,
or a loadout that arrives already fitted, which it never could.

## Cost, stated plainly

**This is bigger than adding a column.** It touches the ship model that
everything else reads from. It was taken now specifically because Build A will
generate thousands of pages with "where to buy" baked into the template, and
after that it is far more expensive.

## NOT designed here, deliberately

**The schema is not specified in this document and must not be guessed at.**
Sleven's standing rule: build two or three concrete cases before generalising
into a shared shape.

The three concrete cases are already known and are the right ones:

1. Wikelo's Drake Clipper (4.10)
2. Wikelo's Aegis Tiburon (4.11)
3. Any one of the 53 component-only editions already in the data

Build those three, then let the shared shape come out of what they actually
needed.

## What must not happen

- **No bespoke row per giveaway.** That is the failure this prevents.
- **No single acquisition value per ship.** It cannot express reality.
- **No schema designed before the three concrete cases exist.**
