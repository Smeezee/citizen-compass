# FINDING — The seven holo collisions are one hull twice, not two hulls

**Written by Code, 2026-08-27. For Sleven and C1.**
**Q6 of `ORDER_the-queue-2026-08-27.md`: report the collision before fixing it.**

`build_holo_data.py` has refused to emit since 17 August. `holo_data.gen.js` is
stamped 08-17, so the holo page has been served from a ten-day-old generation
and nothing noticed, because `build_deploy.py` does not call this generator.

It stops in `merge_join`:

    COLLISION: ATLS would overwrite 'ATLS' - refused
    COLLISION: C8R_Pisces would overwrite 'C8R Pisces Rescue' - refused
    COLLISION: Khartu-Al would overwrite 'Khartu-al' - refused
    COLLISION: M50 would overwrite 'M50 Interceptor' - refused
    COLLISION: MDC would overwrite 'MDC' - refused
    COLLISION: ROC would overwrite 'ROC' - refused
    COLLISION: ROC-DS would overwrite 'ROC-DS' - refused

    7 recovered ship(s) collide with ships already placed. Refusing to emit:
    one of the two is wrong about which hull it is, and picking silently is
    how a Gladius ends up wearing somebody else's hardpoints.

**The refusal is correct. Its stated reason is not what is happening here.**

---

## Neither record is wrong about which hull it is

Every one of the seven pairs points at the **same model file**:

    ATLS -> ATLS.glb        C8R_Pisces -> C8R_Pisces.glb
    Khartu-Al -> Khartu-Al.glb   M50 -> M50.glb
    MDC -> MDC.glb          ROC -> ROC.glb    ROC-DS -> ROC-DS.glb

Same port counts. Same port names. This is not a Gladius about to wear somebody
else's hardpoints — it is **one hull arriving twice**, from the placement pass
and from the recovery join. Four of the collisions are on a name that is
character-for-character identical on both sides; a fifth differs only in the
case of one letter (`Khartu-Al` / `Khartu-al`).

## Four of the seven are byte-identical and need no decision at all

    ATLS   MDC   ROC   ROC-DS

Zero hardpoints on both sides, `hardpoints` byte-identical. There is nothing to
choose between them. These four are pure duplicates.

## Three differ, and only in ways that make the PLACED record the better one

    C8R_Pisces   Khartu-Al   M50

**The positions disagree slightly.** The M50's left wing gun sits at
`-4.919` in the recovered record and `-5.196` in the placed one — 28 cm apart on
a five-metre arm, about 5%. The C8R Pisces' guns differ by 10-20 cm. These are
two placement passes disagreeing about the same port, not two different ships.

**And the placed record carries per-hardpoint provenance the recovered one does
not.** On the Khartu-Al:

    field         recovered   placed
    placed_from   null        "own"
    aimed_at      null        "fraction"
    depth         null        0

**`placed_from` is the field Q7 depends on.** The disclosure bar has to
distinguish a marker derived from a mount name from one that is CIG's own
transform — that is the whole point of `placed_from`, and the recovered records
have it as null. Preferring the recovered record would strip exactly the
provenance the next queue item needs.

The recovered record does carry things the placed one lacks — `aligned`,
`hull_check`, `resolved_by`, `resolved_from`, `why` — but those are top-level
bookkeeping about the recovery, not claims about the hull.

---

## What I recommend, and why it is still not my call

**Keep the placed record; skip the recovered one.** That is what the loop
already does per collision — `continue` — and it costs only the recovery
bookkeeping fields. It preserves `placed_from`, which Q7 needs.

**The narrow fix is to the guard, not to the data:** it should distinguish
*same hull arriving twice* from *two hulls claiming one key*, and exit only on
the second. As written it treats both as the ambiguous case, which is why a
duplicate has held the holo page at a ten-day-old generation.

**Why it is Sleven's call anyway:** the three that differ have two different
answers on record for where a gun is, and I cannot tell from this data which
pass is right. Choosing the placed one because it carries more metadata is a
reason to prefer a RECORD, not evidence about a POSITION. If the recovery pass
is the more accurate one, the right fix is to merge — take the recovered
positions and keep the placed provenance — and that is a different change from
the one-line skip.

**Nothing has been changed.** `build_holo_data.py` still refuses, and the holo
page is still on the 08-17 generation, which is the honest state until somebody
decides.

## One more thing worth separating

This is **not** from the M5 model import. `hardpoints_fleet.json` predates it by
ten hours, and the collision has been there since 17 August.

---

*Code, 2026-08-27.*
