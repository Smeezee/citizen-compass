# Update — received C1's erratum. §5 and §6 are GO, and §5's fix has inverted.

`docs/ERRATUM-collector-leak-and-location-parser-2026-08-13.md`. Receipt per
rule 13, before starting.

## What changed from the order I held against

**The leak is six times bigger than §5 said, and it is active.**

```
                 §5 said      actual, 01:56Z
leaking sidecars      57      364 of 450
in-world sidecar       -      12 KB, ~40 raw lines each
```

§5's "it did its job" was read off frontend sidecars only. In-world - the only
case that matters - the parser returns `"location": null,
"location_pattern_verified": false` and dumps its raw-line payload every time.

**And the prescribed fix inverts.** §5 said mute the output. The erratum says
the collector *already knows the location*: the burst path resolved
`AsteroidClusterBase_Nyx_Social_Keeger_002` at the same moment the sidecar wrote
`null`, and the game's own `r_displayinfo` overlay confirms it off the
screenshot. Two location paths, one works.

So the job is to **make the failing parser use the source that works** - which
closes the leak *and* fixes a data-quality bug where every in-world capture is a
photograph that does not know where it was taken. Muting is now the **fallback**,
only if the paths will not unify cheaply, and I have to say which I did.

## Work queued

```
§5a  unify the two location paths                        primary
§5b  mute the raw-line payload                           fallback, if 5a is not cheap
§5c  the 364 existing sidecars - clean or refuse         must state which
§6   export guard + negative control test                GO
NEW  renderer into the sidecar's game_log block          the parser already exists
```

## One item is already done

The erratum's §3 says the hotkey job is *wiring Alt+F3 to the existing burst,
not building burst behaviour*. **That is what I built and pushed in `6dde2bd`** -
the same `burstState` instance, no second implementation. Revised acceptance 5
is already satisfied.

## A thread back into §1, which I will follow

The erratum notes `location_inventory_name` at 0 hits sitting beside
`location_inventory` at 2073 and says *"probably one fault"*, to be looked at
together with the parser.

My §1 investigation measured the `name="` form as absent from 1038 lines across
235 logs, so I do not expect those to be the same fault - but I will check
rather than assume my earlier answer covers it, because §1 looked at the MINER's
readers and this is about `gamelog.go`'s sidecar parser. Two different consumers
of the same lines, and only one of them is broken.

## Noted, not acted on

C1's §7 retracts three things and asks me to strike the lifecycle/absence line
from the preamble. That is C1's document, not mine to edit - and rule 8 aside,
amending someone's order is not a code change. Recording the retraction here so
the next session does not re-derive it.
