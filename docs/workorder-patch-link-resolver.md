# WORK ORDER — patch-link resolver: make the patch-note links maintain themselves

**Priority: after Part B (source 6 / UEX) and Part C (Go migration). This is not urgent — the page already degrades safely without it. Do not pre-empt Phase 1 for this.**

Hard rule 13 applies: file an `inbox/` update on intake, on completion, and on any stop.

---

## What exists today, and why it is not enough

The testing banner links LIVE and PTU patch notes separately. Both destinations are **hardcoded in `testing/_layer.html`** inside a `CC_PATCH` object:

- `CC_PATCH.live` — a version → comm-link URL lookup. Currently one entry, 4.9.0.
- `CC_PATCH.ptuThread` — the current PTU thread URL, stamped with the version, build number and wave it was recorded for.

Both are correct now and both rot on their own schedule. The page already refuses to serve a PTU link recorded for a version the PTU has moved past, and falls back to the Spectrum channel — but that gate only catches **version** drift. A newer build of the *same* version gets a new thread and the recorded link stays plausible while pointing one build back. Nothing in the page can detect that.

**The owner's requirement is a dependable path, accepting that something has to keep checking.** This order is that something.

---

## The findings this rests on — all verified 2026-08-02, do not re-derive

**1. PTU notes exist only on Spectrum.** RSI's patch-notes index carries LIVE releases only — 20 entries, Alpha 4.9 back to 3.24.0, no PTU among them. The Star Citizen wiki does not cover PTU either; its patch-notes page says so explicitly and points at the same Spectrum channel. Channel is forum `190048`.

**2. PTU thread slugs are a sequential series, and that is what makes this automatable.** Every PTU build of a release gets its own thread at the same base slug plus an incrementing suffix:

```
…/thread/star-citizen-alpha-4-10-ptu-patch-notes      build 12311913  [Wave 1]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-1    build 12326622  [Wave 1]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-2    build 12335477  [Wave 1]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-3    build 12344240  [Wave 1]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-4    build 12358556  [Wave 1]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-5    build 12368639  [All Waves]
…/thread/star-citizen-alpha-4-10-ptu-patch-notes-6    404
```

The base slug is derived from the version: `4.10` → `star-citizen-alpha-4-10-ptu-patch-notes`.

**3. Spectrum is a client-rendered SPA, but the thread page still server-renders its `<title>` and Open Graph tags.** A plain HTTP GET returns no thread body — but it does return the title, which carries the wave label, the version and the build number:

```
[All Waves] Star Citizen Alpha 4.10 PTU Patch Notes 12368639
```

So: **the thread list is not scrapable, but any individual thread URL is verifiable.** That rules out reading the channel and rules *in* probing the series. Confirmed: `-5` returns 200 with that title, `-6` returns a clean 404.

**4. The RSI patch-notes index IS server-rendered.** Entry titles and comm-link URLs come back from a plain GET, format `https://robertsspaceindustries.com/comm-link/Patch-Notes/{id}-Star-Citizen-Alpha-{version-without-dots}`. The ID is assigned by RSI and cannot be computed — but it can be read. So the LIVE side automates too.

---

## What to build

A resolver in the Go background system — same standard as the other long-running components: auto-start, silent, no console window, survives reboot.

### Output contract

Write `testing/patch-links.json`. Nothing else consumes it yet; the build scripts will (see wiring below).

```json
{
  "generated_utc": "…",
  "source_tier": "A-official",
  "live": {
    "version": "4.9.0",
    "url": "https://robertsspaceindustries.com/comm-link/Patch-Notes/21245-Star-Citizen-Alpha-49",
    "verified_utc": "…"
  },
  "ptu": {
    "version": "4.10",
    "build": "12368639",
    "wave": "All Waves",
    "url": "…/thread/star-citizen-alpha-4-10-ptu-patch-notes-5",
    "suffix": 5,
    "verified_utc": "…"
  },
  "notes": []
}
```

### PTU resolution algorithm

1. Read the target PTU version. **Do not hardcode it** — take it from the same place the site's banner does, so the resolver and the page can never disagree about which release is on the PTU.
2. Build the base slug: lowercase, `.` → `-`, `4.10` → `star-citizen-alpha-4-10-ptu-patch-notes`.
3. GET the base slug. If it 404s, the release has no PTU threads yet — emit `ptu: null` with a note and stop. **That is a valid result, not a failure.**
4. Probe `-1`, `-2`, … Stop on the first 404. The last 200 is current.
5. Parse `<title>` of that last thread. Extract wave, version and build.
6. **Cross-check the version in the title against the version you asked for.** If they disagree, the slug pattern has changed under us — emit `ptu: null` with a note naming both. Do not guess.

### Non-negotiable constraints

- **Bound the probe.** Hard ceiling of 40 suffixes. A redirect loop or a soft-404 that returns 200 must not walk forever. Hitting the ceiling is a failure with a note, never a silently truncated answer.
- **A soft 404 is the live risk here.** Confirm the 404 is a real 404 — status code AND absence of the expected title shape. A site that starts returning 200 with a "not found" body would otherwise make the probe run to the ceiling and pick garbage.
- **Rate-limit the probe.** Small delay between requests. This is someone else's server and the whole run is a handful of GETs; there is no reason to burst.
- **Write-before-status is forbidden**, same as every retrieval script in this project. `patch-links.json` is replaced only after every field is resolved and validated. A partial resolve leaves the previous file untouched.
- **Never emit a URL that was not fetched and confirmed 200 in this run.** Not a constructed one, not a remembered one.
- **`main` returns non-zero if any section failed to resolve.** A resolver that exits 0 having produced nothing is how source 2 got marked complete on a run that verified nothing.

### Rule 12 — required rejection proofs

A check that cannot fail is not a check. Before this is trusted, demonstrate each of these:

1. **Nonexistent version** (e.g. `9.99`) → base slug 404s → `ptu: null` with a note, exit non-zero. Not a crash, not an empty URL.
2. **Title/version mismatch** — feed a thread whose title version differs from the requested version → `ptu: null` with both versions named. Prove it does not accept the URL anyway.
3. **Probe ceiling** — simulate an endpoint that always returns 200 → run stops at 40 and reports failure. Prove it does not return suffix 40 as the answer.
4. **Previous file survives a failed run** — corrupt or block the network mid-run and confirm `patch-links.json` still holds the last good content, byte for byte. Checksum before and after.

Record all four in the completion update. A proof that was reasoned about rather than executed does not count.

---

## Wiring it into the site

`testing/build.py`, `build_full.py`, `build_portable.py` and `build_machine_layer.py` read `patch-links.json` at build time and substitute the values into `CC_PATCH` before emitting.

**If `patch-links.json` is missing, malformed, or older than 30 days, the build uses the hardcoded values already in `_layer.html` and prints a warning.** The build must never fail because the resolver had a bad night, and it must never silently ship a month-old link as though it were fresh.

Leave the page's existing version gate in place. It covers the window between the resolver running and the site being redeployed, which is the one gap the resolver cannot close while deploys are manual.

**Order matters here: build-script substitution has bitten this project before.** `CC_SAFE` was inserted before the block it targeted was emitted, and the page threw at runtime while the patch applied cleanly. Exercise the built page, do not read the diff.

---

## Scheduling

Every 6 hours is ample — PTU builds land at most daily. Log each run: what was probed, what was found, what changed. A run that changes nothing should say so.

## Boundaries

- `testing/` and the Go watcher only. No database, no promotion, no schema change.
- Nothing under `testing/` gets committed except `_layer.html`, `build.py` and the new `patch-links.json`.
- Live site untouched.
- If it blocks, write to `inbox/`, stop, and say what blocked. A stopped part with a clear note is a good outcome.
