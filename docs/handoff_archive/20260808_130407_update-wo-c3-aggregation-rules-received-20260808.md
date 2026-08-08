# Update — C3 aggregation-rules work order received (2026-08-08)

Received from C1: reverse-engineer the real aggregation rules for
`ShieldsTotal`, `Power`, `Cooling`, `Emission` (EM and IR), `Distortion.Pool`
and DPS, by testing candidate formulae against CIG's own computed aggregates in
`ships.json` across all 316 ships. Then spec (not build) the temporary loadout
page.

**Routing flag.** The order is addressed `for C3 (Cowork research session)`, not
Claude Code. Sleven handed it to this session. Proceeding, with the reasoning
stated so it can be overridden cheaply: the core of this job is a full
computation across 316 ships joined against `ship-items.json`, and a full scan
of that kind is already on record as having **timed out through the Cowork
bridge** (C2's open item 10, "run it locally"). That part is structurally
better placed here. If C3 is already on it, this stops.

**The method, restated so it is not lost:** `ships.json` carries CIG's own
computed aggregates for each ship's stock loadout, and `ship-items.json` carries
the components. That is 316 worked examples with the answers in the back of the
book — every rule gets tested against labelled data rather than guessed at.

**What I owe, per aggregate:** a candidate rule as actual arithmetic, run across
all 316, reported as a **residual** — exact matches, near misses, misses, and
what the misses have in common. "Works on 300 of 316" is the finding. "Verified"
is not. Anything I cannot derive gets marked **unshippable** rather than
approximated.

**The discriminating case for shields:** the Zeus Mk II CL shows N-1 (three
7200 generators, `ShieldsTotal.Hp` 14,400). One example is not a rule. A ship
fitted with two *different* generators separates N-1 from capacity-weighted
fast, and finding one is the first thing to do.

**Constraints:** research and a proposal only, do not build. Stay off
`citizen-collector/` entirely — C1 is the sole writer and is actively in it.
Verify against files on disk, not planning docs. Every check gets a case that
could have failed it.
