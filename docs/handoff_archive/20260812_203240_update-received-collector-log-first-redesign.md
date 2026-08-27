# Update — received the collector log-first redesign order. §5 is ON HOLD: Sleven says a correction is coming.

Receipt per rule 13, before starting anything.
`docs/prompt-code-collector-log-first-redesign-2026-08-13.md`, from C1.

Sleven, mid-session: *"Read docs/prompt-code-collector-log-first-redesign-2026-08-13.md
when you finish the slot work. C1 has a correction coming on §5."*

The slot work is finished, committed, pushed and live — see the previous update.

## What the order is

A rebalance, not a deletion: the Game.log miner is carrying the project (308
transactions, 992 ship classes, 43 locations, one JSON file) while the
screenshot path burned **818 MB in a 2.5-hour session**, most of it 60-second
interval frames — including photographing the **main menu** at ~3 MB a frame.

Nine buildable items, all measured off Sleven's machine rather than reasoned:

```
§1  location_inventory_name has never matched - look, report, do not paper over
§2  gate interval capture on appears_in_game, then 60s -> 120s
§3  Alt+F3 becomes a burst, built on session_burst.go, settings-driven
§4  build NOTHING - the miner already runs on entry and exit
§5  THE PRIVACY LEAK - location_candidates[] writes raw log lines   <- ON HOLD
§6  export guard with a negative-control test
```

## §5 is not being touched until the correction lands

**This is the item the order calls the most important, and the one gating
putting the collector on anyone else's machine.** 57 of 57 sidecars currently
carry player ID `204354536218` in `location_candidates[]`.

Sleven has said a correction to §5 is coming. Building against a superseded §5
would be the exact defect this project has a rule against — eight files
accumulated for one job yesterday and at least one contradicted another. **So
§5, and §6 with it, wait for the corrected text.** §6's whole job is refusing
what §5 defines as unsafe, so building it against the old definition would bake
in the wrong allow-list.

Recording what I would otherwise have done, so the correction can be compared
against it rather than re-derived: keep the diagnostic and drop the payload —
pattern names tried plus a count, no log text — and never a name-detection
regex, for the reason §5b gives.

## One prerequisite in the order itself

Its preamble says:

> You are currently mid-way through the lifecycle/absence schema work
> (`app/models.py`, `app/absence.py`, the 7917a851cc5d migration). Finish and
> commit that first. This is not urgent enough to interrupt a migration.

That work is real and uncommitted in the tree: `app/models.py` modified,
`app/absence.py`, `alembic/versions/7917a851cc5d_...` and
`checks/_verify_absence_pass.py` untracked. **It was not mine and I have not
touched it**, so I do not yet know how finished it is.

It is also a migration, which is rules 3 and 4 territory — a verified backup
before anything touches the real database, and nothing destructive outside the
guarded harness. I am not going to start that on my own reading of a
one-line instruction in another order's preamble.

## Waiting on Sleven for the sequence

Three candidate next steps, none started:

1. Assess and finish the lifecycle/absence work, as the order's preamble asks.
2. Do the collector items that are **not** blocked — §1, §2, §3, and §4's
   "build nothing" — leaving §5/§6 for the correction.
3. Something else entirely.

Nothing is in flight. The tree is clean apart from the pre-existing uncommitted
work described above.
