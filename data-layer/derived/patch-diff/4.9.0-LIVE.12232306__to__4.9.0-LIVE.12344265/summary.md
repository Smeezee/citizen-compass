# Patch diff - 4.9.0-LIVE.12232306 to 4.9.0-LIVE.12344265

    from   4.9.0-LIVE.12232306   commit 476472689697   2026-07-16T14:46:09+02:00
    to     4.9.0-LIVE.12344265   commit db00b749833e   2026-08-20T12:08:49+02:00

Joined on UUID, never on name. Items: compared.

| | added | removed | changed | schema-only | order-only |
|---|---|---|---|---|---|
| ships | 0 | 0 | 0 | 0 | 0 |
| items | 6 | 0 | 5123 | 0 | 627 |

**Schema-only** means a field appeared or disappeared across the
WHOLE snapshot - upstream changed what it emits. That is not the
game changing, and it is counted separately so it cannot be read
as one.

**Order-only** means a list field whose MEMBERS are identical and
whose order is not. Almost certainly not the game changing, so it
is kept out of the changed column.

## items added
- qrt_mantis_undersuit_01_05_01 (`qrt_mantis_undersuit_01_05_01`)
- qrt_combat_heavy_helmet_03_01_01 (`qrt_combat_heavy_helmet_03_01_01`)
- qrt_combat_heavy_helmet_04_01_01 (`qrt_combat_heavy_helmet_04_01_01`)
- slaver_combat_medium_helmet_01_02_01 (`slaver_combat_medium_helmet_01_02_01`)
- slaver_combat_heavy_helmet_01_02_01 (`slaver_combat_heavy_helmet_01_02_01`)
- slaver_combat_light_helmet_01_02_01 (`slaver_combat_light_helmet_01_02_01`)
