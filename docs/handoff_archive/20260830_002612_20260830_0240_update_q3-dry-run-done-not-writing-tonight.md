# Update — Q3's dry run is done and the list is ready. I am not writing tonight, and three things need answering first.

**2026-08-30 07:40 UTC / 2026-08-30 02:40 local · Code (background session)**

## THE DRY RUN, WHICH IS RULE 5's REQUIREMENT AND IS NOW SATISFIED

    source: model_scaled.glb per ship        <- Q3's whole point
    7 ships, 14 files, every one MOVED ASIDE to _to_delete/, nothing deleted
    Nothing written. Re-run with --write to proceed.

`scripts/fix_model_scale.py` already did the right things: dry run by default,
`--source scaled`, and move-aside rather than delete. Nothing new had to be
built to do this safely.

## A FLAG THAT TOLD THE TRUTH AND A MESSAGE THAT DID NOT

The dry run printed **`would import each sc-ships/<folder>/model.glb`** no
matter what `--source` was set to, while the header two lines above said
`model_scaled.glb`.

**The flag itself is applied correctly** - `src_name = "model.glb" if
args.source == "raw" else "model_scaled.glb"` - so this was a lying message and
not a lost switch. **It is still a defect, and a pointed one: Q3 exists BECAUSE
these ships were once scaled from the wrong file.** A dry run that names the
wrong source is how somebody approves exactly that a second time.

It now prints the real source and the per-ship path with an exists/MISSING
verdict, so the claim can be checked instead of trusted.

## FOUR THINGS FOUND BEFORE ANY MUTATION

**1. Nine model files, not twelve.** Fourteen findings, nine distinct `.glb`s -
variants share models. **Twelve reconciles with nothing on disk.**

**2. Four of the nine do not map to a folder by their deployed name.** The build
derives `Starlancer_TAC.glb` from a folder called `Starlancer TAC`, and
`San_tok.y_i.glb` from `San'tok.yāi`. **A naive from-list keyed on the deployed
name would have found four MISSING folders and either failed or skipped them
silently.** All nine were resolved by reversing the build's own name rule, and
every folder and `model_scaled.glb` was asserted present before the list was
written.

**3. Drake Mule and Greycat STV share one stated triple** - `[8.8, 6.0, 3.5]` -
between two different vehicles. **Both are EXCLUDED from the list.** At least
one of those published figures is wrong, and scaling a hull to bad data makes
the hull wrong while making the auditor go quiet about it.

**4. The DONE-WHEN cannot fail.** *"`_verify_model_scale.py` still exits 0"* -
it exits 0 right now with 24 findings, because it is a findings-only auditor
that flags and never fails. **The finish line I will hold to instead: the seven
files measure inside the band and their rows leave the auditor's SCALE section.**

## AND RULE 15's OWN EXAMPLE BIT A THROWAWAY DIAGNOSTIC

    UnicodeEncodeError: 'charmap' codec can't encode 'ā'

Printing `San'tok.yāi` to a cp1252 stdout. **Rule 15 names that exact ship as
the reason the rule exists**, and says a one-off diagnostic has hit it before.
It has now hit it again. Fixed with `sys.stdout.reconfigure`, the way the
repo's other scripts do it.

## WHAT I AM NOT DOING TONIGHT

**Not running `--write`.** It is an irreversible binary mutation of seven ship
models and **rule 4 wants a verified backup first** - `Backup-CitizenCompass.ps1`
run and its output CONFIRMED, not merely started. That is worth doing awake.

The list is saved and the command is one line when it is time:

    venv/Scripts/python.exe scripts/fix_model_scale.py --source scaled
        --from-list <the list> --write

Uncommitted: `scripts/fix_model_scale.py` (the dry-run message).
**`scripts/fix_model_scale.py` has no declared owner in `OWNERS.md`** - a gap,
and C1's to close.
