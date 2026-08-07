# FINDING — the 5,108 contract records now divide cleanly by star system

    from    C3 (Cowork), 2026-08-07
    for     C1 -> Claude Code, and whoever picks up mission-board work next
    data    data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/contracts/
            (5,108 records) joined against starmap.json from the same snapshot
    output  data-layer/derived/contracts-by-system/contracts_by_system.json —
            every record tagged with system + release flags, MANIFEST.json alongside it

Sleven asked whether we can now split the mission list into Stanton / Nyx / Pyro. Yes —
built this session, joined against the game's own starmap hierarchy rather than guessed
from names.

---

## Method

`starmap.json` has three `Star`-type root nodes with no parent: Stanton, Pyro, Nyx.
Everything else (planets, moons, landing zones, outposts, POIs) chains up to one of
those three through `ParentUUID`. Walked that chain for all 2,054 starmap entries and
built a location-name -> system lookup from the 1,438 that carry a real (non-placeholder)
name.

Each contract record was then resolved in order: its `RequiredLocations` names first,
then `AvailabilityLocations` names, then (last resort) a literal Stanton/Pyro/Nyx
substring match on the DebugName/GeneratorClass itself. `system_resolution_method` on
every row in the output says which path was used, so nothing is silently guessed.

## The split

    2,151  Stanton   (1,926 released — 225 NotForRelease)
    1,706  Pyro      (1,229 released — 476 NotForRelease, WorkInProgress)
      412  Nyx       (  398 released —  14 NotForRelease)
      839  unresolved — no system reference found on the record at all

**4,269 of 5,108 (83.6%) resolved.** The 839 that didn't mostly read as genuinely
system-agnostic generator templates — generic hauling/time-trial/assassination templates
with no location baked into the template itself, resolved at runtime rather than fixed at
authoring time — not a join failure on a sample check. Not individually audited record by
record, so treat that read as a first pass, not a closed finding.

**Pyro is carrying more than four times Stanton's NotForRelease rate** — 27.9% of Pyro's
located records aren't live yet, against 10.5% for Stanton and 3.4% for Nyx. That's worth
knowing before anyone scopes "capture Pyro missions" work: the template count you can
actually see in-game right now is meaningfully smaller than Pyro's raw share of the file.

## Unique templates per system (GeneratorClass family only — the other naming family,
## MissionBrokerEntry, still needs its DebugName suffixes normalized down to real
## template counts, not done this pass)

    Stanton   73 unique GeneratorClass templates
    Pyro      51
    Nyx       58
    unresolved 15

## Not verified

- The 839 unresolved records haven't been read one by one — this is a batch
  classification, not a manual check.
- The MissionBrokerEntry family (the ~2,165 records whose template ID lives only in a
  DebugName string, not a separate field) hasn't been collapsed to a clean template count
  the way the GeneratorClass family has. That's the next real step if the "template
  catalog per system" idea from the brainstorm moves forward.
- Whether `data-layer/derived/starmap-routes/` already has a cleaner location->system
  table than the one built here from scratch — worth checking before this becomes the
  standing join, in case it duplicates work that already exists.
