# Taking CIG content down

**Run this. It removes every CIG-sourced asset from the built site and rebuilds it.**

```
venv\Scripts\python.exe scripts\takedown.py --yes
```

**Then publish the result — the removal is only on this machine until you do:**

```
powershell -File scripts\deploy_testing.ps1
```

That is the whole procedure. Everything below is explanation.

---

## If you want to see what it will do first

```
venv\Scripts\python.exe scripts\takedown.py --dry-run
```

Prints the exact list of files and changes nothing. Without `--yes` it refuses
to remove anything, so it cannot happen by accident.

## What "CIG-sourced" means

It means the asset's record in `data-layer/cig_assets.json` has a `source` of
`cig-holoviewer` or `cig-fankit-restricted`.

It is **a field on a record, not a folder and not a filename**. Folders get
reorganised and prefixes get dropped by build steps nobody remembers are there;
a `models/cig/` directory survives until the first person who tidies up. A field
survives, and it carries the date, the origin URL and a note as well.

Anything **not** carrying that source is not touched. Our own renders, the
scunpacked-derived data and the OFL fonts all stay.

## What happens to the files

They are **moved**, not deleted — into `_to_delete/takedown_<timestamp>/`.

If a takedown turns out to have been wider than intended, nothing is lost. It
also means you can hand someone the exact list of what came off.

## Why the site still works afterwards

Each removed record is stamped `removed: <date>`. The build reads that stamp and:

- drops those ships out of the model map, so no page can build a URL to them;
- publishes them in `LOADOUT_WITHDRAWN`, so the ship page can tell the
  difference between *"we have no model for this hull yet"* and *"this model was
  taken down"* — and says the second one, because saying the first would be
  untrue;
- tears the 3D viewer down properly rather than leaving a dead canvas or a
  spinner that never resolves.

Every number, component and stat below the viewer comes from the game files, not
from the model, so the rest of the page is unaffected.

**The stamp is the durable half.** Deleting the file alone would last until the
next model sync put it back, and the site would quietly start serving it again
with nobody noticing. If a withdrawn asset does reappear in the build, the build
moves it straight back out and prints a loud notice — it fails safe towards
removal rather than refusing to build, because a build that will not run is the
wrong behaviour in the middle of a takedown.

## If the rebuild fails

The removal has still happened and the register is still stamped — that part is
done, and it is the part that matters. But **do not deploy** until the build is
fixed, because the published site would still reference what was pulled.

## Has this ever actually been run?

Yes — every time the checks run. `checks/_verify_takedown.py` executes
`scripts/takedown.py` as a real subprocess against a fixture containing both
tagged and untagged assets, and asserts that the tagged ones are gone, that
**the untagged ones survive**, and that the site still builds. That second
assertion is the one that catches a script which just deletes everything, and it
has been observed failing on a deliberately broken version.

A takedown script nobody has ever executed is a script that fails the first time
it is needed.
