# ORDER — the two Carrack C8X package entries are gone. Rebuild and deploy testing.

From: C1 (Cowork), 2026-09-04
For: Code

Sleven, walking the inspector: the Carrack with a C8X and the Carrack Expedition with
a C8X are RSI **store bundles**, not ships. There is nothing to show about them that
the Carrack and the Carrack Expedition do not already show. The Carrack and the
Expedition genuinely differ from each other and both stay.

The measurement agreed before he asked: `Carrack_Expedition`,
`Carrack_Expedition_w_C8X` and `Carrack_w_C8X` are **byte-identical**, all three
876,628 bytes. (`Carrack` itself is a different file — so `Carrack_w_C8X` was showing
the Expedition's hull under the plain Carrack's name, which was wrong as well as
redundant.)

## Done
Neither was referenced anywhere on the site — `CC_MODELS` 0, `SHIPS` 0. They existed
only as files, in the inspector's list, and in the takedown register.

    moved, not deleted -> _to_delete/carrack_c8x_20260904T232421Z/
      testing/_deploy/models/Carrack_w_C8X.glb
      testing/_deploy/models/Carrack_Expedition_w_C8X.glb
      sc-ships/Carrack w_C8X/
      sc-ships/Carrack Expedition w_C8X/

    data-layer/cig_assets.json        258 -> 256
    inspector ship list               258 -> 256
    testing/_deploy/models            256 .glb

`C8X_Pisces_Expedition.glb` is a REAL ship — the snub itself — and is untouched.

Verified after: deploy guard clean, `_verify_hull_is_solid.mjs` exit 0.

## RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

Sleven's marks live in his browser. Removing two ships shifts the numbering, so his
counter will read out of 256 — the marks themselves are keyed by filename and survive.

## REPORTED, NOT ACTED ON — 12 more the site cannot reach
Same shape as the two just removed. Built, served, and no site row links to them:

    identical to another file
      Anvil_Ballista_Dunestalker / Anvil_Ballista_Snowblind   (identical to each other)
      Argo_Mole_Carbon_Edition / Argo_Mole_Talus_Edition      (identical to each other)
      Caterpillar_Best_In_Show_Edition_2949 / Caterpillar_Pirate_Edition
      Cutlass_Black_Best_In_Show_Edition_2949  == Cutlass_Black
      Nox_Kue                                  == Nox

    unique geometry - these are NOT duplicates and want a different answer
      Dragonfly_Yellowjacket
      Hammerhead_Best_In_Show_Edition_2949
      Nautilus_Solstice_Edition
      Reclaimer_Best_In_Show_Edition_2949

The first group is the same "store bundle or paint variant, no new information" case
Sleven just ruled on. The second group is four models with real geometry that no
visitor can see — closer to the 30-ship routing problem than to this one.

**Not touched. Sleven named two ships and I removed two ships.**
