# Update — the scrub tool is committed and pushed. `bf95d98..ccd3f0c`.

```
bf95d98..ccd3f0c  main -> main
local and origin both at ccd3f0c19e6833e107ee2a9643c8a398ba3fc237
scripts/scrub_sidecars.py at origin: 241 lines
```

Staged by path. `git status` showed one staged entry - `M scripts/scrub_sidecars.py` -
and everything else in the tree was already dirty or untracked before this
session touched anything.

## Why it was worth keeping rather than discarding

The cleaning of 394 sidecars is a **claim about privacy**, and a claim about
privacy should be re-checkable by whoever doubts it. Running the tool now prints

```
sidecars: 449   clean: 449   leaking: 0
Nothing to scrub - every sidecar is already clean.
```

which is evidence reproducible in two seconds, rather than a sentence in a
handoff that has to be taken on trust.

## Both branches exercised before committing, not just the used one

The dirty path had been run for real; the clean path had not been checked since
the data changed under it. Planted a fixture and ran both:

```
clean  ->  "Nothing to scrub - every sidecar is already clean."
dirty  ->  planted.json   location_candidates, raw log line, account handle in Player[]
           REPORT ONLY - nothing was written.
```

## One fix went in first

With nothing dirty it printed *"Re-run with --apply to back up and rewrite these
0 file(s)"* - inviting a pointless destructive run. In a tool whose entire
argument is about not claiming things that are not true, that was a small
instance of the same fault, so it says nothing to scrub instead.

## State

The collector order is now fully committed and pushed:

```
7d12ace  §1 location_inventory_name is a measured zero
b75a94a  §2/§4 main-menu gate, 120s, miner timing recorded
6dde2bd  §3 hotkey burst
1a741d6  §5/§6 export guard, consent v3, leak test
f951ef2  sending includes the screenshots
98e6740  the screenshots decision filed in the repo
bf95d98  the SEND button cannot send less than consent v3 promises
ccd3f0c  the scrub tool
```

**Still not verified anywhere**: acceptance 1 wants a grep of a fresh captures
folder after a REAL session. Everything to date is archive fixtures plus a
rewrite of the existing folder. It needs the game played, and no amount of
further work here substitutes for it.
