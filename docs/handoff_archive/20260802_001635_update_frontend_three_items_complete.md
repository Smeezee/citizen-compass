# UPDATE — front-end order: all three items done. Stopping as instructed.

Builds A, B and C not started — they are downstream of decisions 2 and 3.

## 1. `find.src.html` added to PAGES, guard re-proven

```python
PAGES = [
    ('keybinds.src.html', 'keybinds.html'),
    ('loadout.src.html',  'loadout.html'),
    ('find.src.html',     'find.html'),
]
```

**Rule 12, three entries:**

| test | result |
|---|---|
| all three outputs moved aside, rebuild | **all three restored, byte-identical** (25,106 / 23,104 / 20,517) |
| `find.src.html` removed (the *new* entry) | **exit 1**, "PAGE SOURCE MISSING: find.src.html" |
| source restored, rebuild | exit 0, all three copied |

Outputs were **moved aside to `_to_delete/`, not deleted** (rule 1) and restored.

**A correction to my own method, worth recording.** My first read of the failure
case reported `BUILD EXIT=0` — because I piped Python through `tail`, so `$?`
captured `tail`, not Python. The guard was fine; my measurement was not. Re-run
without the pipe: **exit 1**. This is precisely the trap rule 12's new paragraph
describes — prove by behaviour, and make sure the thing you measured is the
thing you meant to measure.

**Observation, not a defect:** when the guard fires, `index.html` has already
been written, so `_deploy/` is left with a new index and a stale page from the
prior build. On a fresh deploy directory there would be no stale page and links
would 404 — exactly what the error message says. Not changing it; out of scope.

## 2. Tab layout — RECOMMENDATION ONLY, nothing implemented

Confirmed the order's measurements in the source: `calc(44% + 150px)`,
`+290px`, `+430px`, `+570px`.

On 1920×1080, 44% = **475px**:

| tab | top | on a 1080px viewport |
|---|---:|---|
| DISPLAY | 475px | fine |
| FEEDBACK | 625px | fine |
| KEYBINDS | 765px | tight |
| LOADOUT | 905px | mostly off-screen |
| FIND | **1045px** | **35px of viewport left — effectively invisible** |

**Also confirmed: the page already has a `<nav>`**, carrying *Ship Purchase
Matrix* and *Sale Calendar*. There is somewhere for destinations to go.

### Recommendation

**Split by kind, not by fitting more in.**

- **Right edge keeps DISPLAY and FEEDBACK.** Both act on the page you are
  looking at. Two tabs sit at 475px and 625px — comfortably on screen at 1080p,
  with room for a third at 765px if one is ever genuinely page-level.
- **FIND moves into the existing `<nav>`.** It is a destination, the nav already
  exists, and it already holds exactly this kind of link.
- **KEYBINDS moves into the nav too.** Same reasoning.
- **LOADOUT is already ruled** — it goes on the ship page, opening on the ship
  you are viewing. That is the pattern for destinations and it is the right one.

That is 5 → 2 on the right edge, and nothing becomes unreachable.

### On build ownership

The order is right that hand-patching after every build is not workable, and
right that C2's 8a would make Sleven's LOADOUT removal impossible.

**The build should own an explicit list with an explicit position per tab** —
not re-emit whatever was last in the file. Adding a sixth then requires editing
the list and choosing a position, which is a deliberate act with a visible
layout consequence, rather than a silent append that pushes something
off-screen. Removing one requires deleting a line, and it stays removed.

**Not implemented.** Sleven decides the layout first; emitting a broken layout
reliably is not an improvement.

## 3. The backend decision — for Sleven, with corrected numbers

**Two of the order's figures are not supported by the landed data**, and one of
them changes the arithmetic that the whole ceiling argument rests on.

Measured directly from the sealed snapshots:

| quantity | order says | **measured** | source |
|---|---:|---:|---|
| item files | "21,849" | **7,728** | UEX snapshot, 100 category files |
| labels | "90,121" | **63,375** | source 2 snapshot, matches its manifest |
| item price rows | — | 23,734 | UEX `items_prices_all` |
| terminals / shops | 823 | **823** | UEX `terminals` |
| ships | 316 | 316 game files, 254 live | `ship_resolution.json` |

**21,849 is close to nothing in the data. 23,734 is the item *price row* count** —
so the likely explanation is items being conflated with price rows. Worth
confirming before anyone quotes it again.

### What that does to the ceiling argument

A page-per-item build is:

```
7,728 items + 823 shops + 316 ships = 8,867 pages
```

**That is under the 20,000-file Cloudflare cap, not over it.** The order's "would
exceed it" does not hold against the measured counts. The cap is real; it is
just not the binding constraint at this size.

### The trade-off, stated plainly

**Static JSON**
- Keeps the zero-backend property. A deploy stays a folder of files.
- No uptime dependency, no monitoring gap, no fallback to design.
- A bundled index with client-side rendering avoids per-item files entirely, so
  the cap is not even approached.
- Cost: heavier client, and filtering/search happen in the browser.

**FastAPI**
- More flexible; Railway already runs and currently powers nothing public.
- Cost: the site starts depending on a service being up. There is **no
  monitoring, no uptime history, and no fallback** for when it is not — and the
  live site has never had a runtime dependency.

### Recommendation

**Static JSON.** Three reasons, in order of weight:

1. The measured page count fits comfortably, so the argument that forced FastAPI
   does not survive the corrected numbers.
2. Introducing a runtime dependency is a one-way door for a site whose entire
   deploy story is "a folder of files", and it would be taken before any
   monitoring exists to notice it failing.
3. Nothing on the roadmap yet needs server-side work — no auth, no writes, no
   real-time. FastAPI becomes the right answer the moment one of those appears,
   and that decision is cheaper to take later than to unwind.

**This is a recommendation, not a decision. Waiting.** No FastAPI work started.

## Also confirmed while here

- `data-layer/ship_resolution.json` exists and is structured as the order
  describes (`counts`, `matched`, `no_game_file`, `ambiguous`, `tier_variants`).
  Used, not re-derived.
- The build independently reports `unmatched: 6` naming 85X, Arrastra, Fury,
  Mantis, Merchantman, PTV — the same six the auditor found. Third independent
  corroboration.

## Not committed

This order does not grant commit-and-push authority and hard rule 2 requires it
per change. The `build_deploy.py` edit is in the working tree, proven, and
uncommitted. Say the word.
