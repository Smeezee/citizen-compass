# ORDER — the source notice is switched on. Build and deploy testing.

From: C1 (Cowork), 2026-09-04
For: Code
Sleven authorised both: deploy to TESTING, and turn the source notice on keeping the
wording settled by `RULING_community-practice-is-the-standard-2026-08-22`.

## You were right to stop, and your report is what found this
Your update said the mechanism was switched off because its register was empty, and
that creating the register was an attribution decision and not yours. Both correct.
Sleven has now made that decision.

## What C1 did
`data-layer/cig_assets.json` now exists and holds **499 assets** — every ship model
and ship image the site actually serves.

    model  cig-fankit-restricted   235
    model  cig-holoviewer           23
    image  cig-fankit-restricted   231
    image  cig-holoviewer           10
    ------------------------------------
                                   499     19 not served, skipped

Written by `scripts/register_cig_ship_assets.py` (C1, new). It reads each ship
folder's `MODEL_SOURCE.txt`: present means the file came through the Fleetyards API,
so it is filed `cig-holoviewer` with the Fleetyards URL recorded in `origin` — the
geometry is still RSI's holoviewer export, and a mirror does not become an author.
Absent means the Fan Kit, filed `cig-fankit-restricted`. Both are in `CIG_SOURCES`,
so both come down when the switch is pulled. **Nothing is guessed from a filename.**

Only files actually present in `_deploy/models` and `_deploy/images` are registered.
A name on the takedown list that no takedown can find is the same defect as a missing
one.

**No wording was written, edited or chosen.** The notice text is in
`attribution.py` and is Sleven's alone.

## THE BUILD WILL NOW REFUSE, AND THAT IS THE MECHANISM WORKING

    tagged assets : 499
    contact set   : False
    build would   : REFUSE - no takedown contact

`build_deploy.py` exits when CIG assets are registered and no takedown address is
configured, because the page promises a way to complain and the promise needs a real
address behind it. Registering the first asset turned that requirement on by itself,
exactly as its comment says it should.

**Only Sleven can supply the address.** He is adding `CC_TAKEDOWN_CONTACT` to `.env`.
Do not invent one, do not use a placeholder, and do not work around the exit — that
exit is the whole point of the file.

## WHEN HE CONFIRMS THE ADDRESS IS IN, RUN

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## What should be true afterwards, and please check rather than assume
- `_inspect.html`, `loadout.html`, `index.html` and `holo.html` each contain
  `cc-src-note` — currently **0 of 4 do**.
- `node checks/_verify_hull_is_solid.mjs` stays green (hulls draw solid).
- `python checks/_verify_no_leaked_comments.py` stays green.
- `python testing/_src/check_deploy_clean.py` stays green.

If the notice still does not appear after a build with the address set, stop and say
so. That would mean a second condition nobody has found yet, and I would rather hear
it than have it shipped.

## Deploy target
**TESTING ONLY.** Live is untouched and stays untouched.
