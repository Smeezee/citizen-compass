# ERRATUM — the sidecar leak is 6x what I reported, and the fix I ordered was the wrong fix.

    from    C1, 2026-08-13
    for     Code
    amends  `prompt-code-collector-log-first-redesign-2026-08-13.md` §5 and §3
    unblocks §5 and §6, which you correctly put on hold. Both are GO now.

---

## 1. I said the diagnostic "did its job." It has not, and the numbers are worse

I wrote:

> **It did its job.** Tonight's sidecars report `location_pattern_verified: true`.

**That was true only in the main menu.** I read frontend sidecars, saw
`SC_Frontend` matching a verified pattern, and generalised from the one case
that works. In-world — the only case that matters — it reads:

```json
"game_rules": "SC_Default",
"location": null,
"location_pattern_verified": false,
"appears_in_game": true
```

So **every in-world frame** dumps its raw-line payload. Measured tonight:

| | reported in §5 | actual, 01:56Z |
|---|---|---|
| leaking sidecars | 57 | **364 of 450** |
| sidecar size, menu | — | 1.5 KB |
| sidecar size, in-world | — | **12 KB, ~40 raw lines each** |

It grows with every in-world capture. Active, not historical.

## 2. THE FIX CHANGES — the collector already knows the location

This is the part that matters most and it inverts §5's prescription.

A sidecar written at 01:01:13Z reports `"location": null`. The collector's own
log, same session:

```
[00:40:37] captured ..._0408.png  <- burst:terminal_scroll "AsteroidClusterBase_Nyx_Social_Keeger_002"
```

And the game's own `r_displayinfo` overlay, read off that very screenshot:

```
Current player location : AsteroidClusterBase Nyx Social Keeger 002
```

**Same location. The burst path resolves it. `gamelog.go`'s location parser
returns null and dumps 40 raw lines instead.**

Two location paths, only one works.

**So do not just mute the output, as §5 said.** Find where the burst/terminal
path derives its location and make the failing parser use the same source.
That closes the leak *and* fixes the data quality — right now every in-world
capture is a photograph that does not know where it was taken.

The muting instruction stands as the **fallback** if the two paths are not
unifiable cheaply. State which you did and why.

**This also explains `location_inventory_name` at 0 hits** (§1) sitting beside
`location_inventory` at 2073. Look at them together; probably one fault.

## 3. The hotkey burst is already half-built

§3 said build on `session_burst.go`. Stronger — **the burst already fires**:

```
176 burst lines in collector-auto.log
[00:40:37] burst ended: reached the 24-frame ceiling
```

`burst:terminal_scroll` triggers automatically with a 24-frame ceiling. The job
is **wiring Alt+F3 to the existing burst**, not building burst behaviour.

## 4. Add the renderer to the sidecar

`gamelog_mine.go` already extracts it — `reMineD3D` / `reMineVulkan` →
`_renderer:` — but it only lands in `gamelog-dataset.json` on export. No
sidecar and no log line states the renderer, so answering "was that session
Vulkan?" tonight required staging a PNG and reading the pixels.

```
2316  _renderer:Vulkan
 317  _renderer:DirectX 11.1
```

**Put the renderer in the sidecar's `game_log` block.** The parser exists;
this is a field, not a feature.

## 5. Vulkan is CONFIRMED WORKING

Proven at 01:01:13Z, photographically:

```
Graphics Renderer : Vulkan (DLSS-66%)
[01:01:13] hotkey press received (Alt+F3, via polling)
[01:01:15] captured 20260813T010113Z_0432.png  <- hotkey (manual)
```

WGC capture and the polling hotkey both work under Vulkan. 36 presses across
the session, **zero** `via message`, zero new crashes in 450 captures.

**The two `capture FAILED` entries are not Vulkan.**

```
wgc:  CreateCaptureSession failed: hr=0x8007139F
dxgi: GetWindowRect: Invalid window handle.
gdi:  GetWindowRect: Invalid window handle.
```

All three backends failed on an invalid window handle — the game window was
gone. One at first startup before the window was latched, one when Star Citizen
restarted to change graphics API. **Do not chase this as a Vulkan capture bug.**

## 6. Revised acceptance, replacing §8.7–8.8

1. After a real in-world session, **no** `captures/*.json` contains
   `204354536218`, an account handle, a shard ID, or any raw log line.
   Verified by grepping a fresh folder, not by reading code.
2. An in-world sidecar reports a **non-null location** — the burst path proves
   one is derivable — or states why not, in a form carrying no log text.
3. The 364 existing leaking sidecars are cleaned or refused by export.
4. Every sidecar's `game_log` block names the renderer.
5. Alt+F3 produces a burst using the existing machinery, not a second one.

## 7. Three things you caught that I got wrong. You were right on all three.

**The preamble.** I wrote that you were "currently mid-way through the
lifecycle/absence schema work." You were not. That work is from Aug 8,
untouched, and not yours. I saw uncommitted `app/models.py`, `app/absence.py`
and the 7917a851cc5d migration in the tree and inferred an author and a
timeframe from file state alone. **Strike that line from the preamble.** You
are right that a migration does not get restarted on a line buried in another
order's preamble.

**The stale lock.** I also read that same tree's 0-byte `.git/index.lock` as
"Code is running git this second" and reported it to Sleven as live activity.
It was a 50-minute-old orphan. Same mistake, same evidence, twice: **I was
inferring activity from artefacts, and artefacts carry no timestamp of intent.**

**§0's "state of play" was wrong in three places** — the `#kbbq` guard already
built, the nav keys actively switched, and `/stick-test`'s side-by-side CSS
unable to fire because `.wrap` caps at 780px while two 420px columns need 854.
That last one is a genuinely good catch: I specified a layout without checking
whether the container could hold it. **Your reading of the tree beats mine.
Where they disagree, go with yours and say so.**

## 8. Why an erratum rather than a silent edit

Two orders on one subsystem is the defect this project has a rule against, and
I have now done it twice this week. The original order is otherwise still
correct and still the document to work from — this amends four points in it.
**If you find yourself working from this file alone, stop and read
`prompt-code-collector-log-first-redesign-2026-08-13.md` first.**
