# BUILD AND DEPLOY. The numbers moved again — more coverage, not less. And you should know the placement now reads the 4.10 snapshot.

**2026-08-27 19:52 local · C1** — read from `date`.

## I keep sending you different numbers. Read the manifest, not me.

Three notes today have quoted three different port counts because I kept
working after sending each one. **Stop trusting the figures in my notes.** The
authority is on disk:

    data-layer/derived/holo-hardpoints-align/MANIFEST_client_overlay.json  -> counts
    data-layer/derived/hardpoint-placement/MANIFEST.json                   -> counts

As of right now the build should print:

    client marker records added for 30 hull(s) the dataset had none for
    client hardpoint overlay: 1082 port(s) moved onto CIG positions

**The rule that does not change: none of those may be zero, and loadout.html
must appear in the disclosure-CSS line.** If a count differs from this note but
is non-zero and the manifests agree with it, build anyway — it means I did more
work, not that something broke.

## THE 4.10 SNAPSHOT IS COMPLETE AND MY SCRIPTS ARE NOW USING IT

Your clone finished. `snapshots/20260827T225641Z` has lost its `.partial` and
carries 318 ship classes.

**`build_hardpoint_placement.py` takes the newest snapshot automatically, so
this run scaled every hull against 4.10 lengths rather than 4.9.** I did not
choose that; the script has always taken the newest and the newest changed
underneath it. Flagging it because it is your front: **the placement
manifest's `dimensions` field now points at the 4.10 snapshot.** Acceptance
still passes 150 of 160, so nothing moved badly, but the provenance changed and
you should not discover that from a diff.

## What got better since your deploy

**The hull rule was finding 120 of 18,891 `.cga` entries and was exactly right
about all of them — and blind to the rest.** It takes the file whose stem equals
a contiguous run of its own folders. CIG does not always name a folder for the
ship inside it:

    AEGS\Sabre\AEGS_Sabre_Raven.cga          folders: AEGS, Sabre
    MISC\Freelancer_v2\MISC_Freelancer.cga   folders: MISC, Freelancer_v2
    ORIG\300_Series\ORIG_300I.cga            folders: ORIG, 300_Series

Every one of those is a hull and none equals any run of its folders.

**Second rule added, and it is an authority rather than a pattern: exact
equality against CIG's own `ClassName` list from ships.json.** It cannot admit a
prop — there is no ship class called `aegs_hab_bunkbed_sq_player`. Still no
fuzzy matching; a stem that merely resembles a class name matches nothing. Two
ambiguous cases (Javelin, Basher — two paths each) are dropped and named, not
picked.

    transforms   116 hulls -> 135
    placement    146 converted -> 160, 137 passed -> 150
    overlay      93 hulls / 955 ports -> 106 hulls / 1,082 ports
    ship page    165 classes fully on CIG coordinates -> 181

**Newly on real coordinates:** the whole Freelancer family (base, DUR, MAX,
MIS), Cutlass Black and Red, Constellation Aquila and both Phoenixes, 300i,
Sabre Raven, Vanguard Hoplite, Fury LX, MPUV 1T.

## The stale guard fired twice today and both times it was right

Once when the airframe experiment left 55 files behind, once when the
Constellations moved from lowercase to capitalised class names. Both times it
stopped rather than letting the overlay read a refused hull. I moved the files
to `_to_delete/hardpoint-placement-stale-2026-08-27/` — **97 files there now,
worth a glance before you delete them.**

The placement directory currently matches its manifest exactly: 160 and 160.

## Verified before sending

    overlay entries matching nothing                     0
    client records colliding with an existing record     0
    client model files the ship page references      30/30
    client model files shadowing an existing record      0
    direct markers from the client records             304
    classes emitting zero markers                        0

Testing only. Nothing to the live site without Sleven's go-ahead.

— C1
