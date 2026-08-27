# PROMPT FOR CODE — collector redesign: the log is the dataset, the screenshot is the exception. Plus the privacy leak that blocks every crew build.

    from    C1, 2026-08-13
    for     Code
    basis   Live watch of a 2.5-hour session on 2026-08-12, plus reading the
              collector's own mine output. Every number below came off Sleven's
              machine tonight, not from reasoning.
    status  GO-AHEAD to build, commit, push. Sleven confirmed each decision in
              §2, §3 and §4 individually.

    SEPARATE from `prompt-code-MASTER-keybinds-and-the-rest-2026-08-12.md`.
    That order still stands and is still unrun. This one does not touch the
    website, the keybinds page, the holo viewer or the fonts. Two different
    subsystems, two orders, no overlap. Run them in whichever sequence suits.

    You are currently mid-way through the lifecycle/absence schema work
    (`app/models.py`, `app/absence.py`, the 7917a851cc5d migration). Finish and
    commit that first. This is not urgent enough to interrupt a migration.

---

## 0. The measurement that drives everything here

Two collection paths run side by side in this program. One of them is carrying
the project. The other is filling the disk.

**The Game.log miner, all-time, from the collector's own output on 2026-08-12:**

```
mine: 244 logs read (0 unreadable), 0 new rows, 308 total (287 buy, 21 sell),
      43 locations, 992 ships, 56 quantum destinations
```

308 transactions. 992 ship classes. 56 quantum destinations. 43 locations. Read
back through `logbackups`, so it covers years of play that predate the tool.
Disk cost: one JSON file.

**The screenshot path, one session, 2026-08-12 22:37Z to 00:39Z:**

```
369 captures
818 MB
104  interval:60s
  6  event:terminal_open
  0  event:transaction
 30  hotkey (manual)
```

Roughly 380 MB/hour, of which the overwhelming majority is unprompted 60-second
interval frames. A sidecar written near the end of that session:

```json
"location": "main menu (Frontend_Main, not in world)",
"trigger":  { "kind": "interval", "seconds": 60 }
```

**It was photographing the main menu, every 60 seconds, at roughly 3 MB a frame.**

### Do not "fix" the transaction trigger. It is not broken.

`event:transaction` sitting at 0 looks like a dead parser and is not one. The
game writes `SShopBuyRequest` / `SShopSellRequest` only when a sale **completes**.
Sleven opened terminals six times and bought nothing, so the live trigger
correctly never fired. The same pattern has matched 308 times in the archive.
`reMineTxn` is `Verified: true` and keyed on payload shape rather than class
name, which is why it survived CIG renaming `CEntityComponentShopUIProvider` to
`CEntityComponentShoppingProvider` between 4.9 and 4.10.

The collector said so itself, in English, and it was right:

> `mine: nothing new this pass. That is normal after a session with no trading`

**Leave the transaction path exactly as it is.** It is the best-working code in
the collector.

### What screenshots are still for — the reason this is a rebalance, not a deletion

The log records **what was bought**: one item, one price. It does not record the
other forty rows on the board, the stock levels, or the prices at a shop the
player walked past without trading at.

**The screen is the only source for prices nobody paid.** That is the actual
product, and it is worth real disk — but only in the seconds when a price board
is on screen. Which is exactly when a human would reach for the hotkey.

So: log = continuous, free, complete for what was done. Screenshot = expensive,
deliberate, aimed at boards. Everything below follows from that split.

## 1. One reader has never matched and deserves a look

```
mine: these readers have never matched anything:
      object_container, spawn_location, location_inventory_name
```

`object_container` and `spawn_location` are both `Verified: false` and their
zero is unremarkable. **`location_inventory_name` is the odd one.** Its sibling
`location_inventory` is `Verified: true` and fired six times tonight, so a name
variant sitting at zero right beside a working pattern is more suspicious than
the other two.

**Check it, report what you find, and do not paper over it.** If the pattern is
genuinely stale, say so and propose the replacement. If it covers something
Sleven simply hasn't done, say that instead and leave it alone. The extractor
table's whole design is that a zero is either information or a warning, and the
only way to tell is to look.

## 2. Interval capture: gate it on being in-world, then raise it to 120s

**Confirmed by Sleven.** Both halves, in this order — the gate matters more than
the number.

The sidecar already carries what this needs:

```json
"game_log": { "appears_in_game": false, ... }
```

**When `appears_in_game` is false, take no interval capture at all.** No main
menu, no loading screen, no shader-optimisation wait. There is nothing on that
screen any dataset wants and it currently costs ~3 MB a minute to prove it.

**When true, interval capture runs at 120 seconds**, up from 60. Change the
default in `collector-settings.txt` (`interval_seconds = 120`) and make sure an
existing file that still says 60 keeps working and says so in the log, the same
way the old `interval_minutes` conversion already does.

**This is a gate on data that already exists, not new detection.** If you find
yourself writing a new window-state check or a second in-game heuristic, stop —
`appears_in_game` is already computed for every sidecar and it is the answer.

**Event and hotkey captures are NOT gated.** They fire regardless. If
`terminal_open` somehow resolves while the flag reads false, take the picture —
an event is evidence the flag is wrong, not a reason to skip the frame.

## 3. The hotkey becomes a burst

**Confirmed by Sleven**, in his words: *"Make the hot key a burst. That way I can
scroll for a few seconds and try to capture multiple things. If I have to take
multiple screenshots, that's fine."*

One press of Alt+F3 currently yields one frame. It should yield a short burst so
a commodity board can be scrolled through while it records.

`session_burst.go` already has the machinery, including a `terminal_scroll`
concept. **Build on it rather than writing a second burst path** — two burst
implementations in one program is exactly the drift this project has a rule
against.

Specifics:

- **Duration and rate are settings**, not constants. Start at something like 6
  seconds at 1 frame/second and let `collector-settings.txt` override both. The
  right numbers depend on how fast he scrolls and neither of us knows that yet.
- **A second press during a burst extends it, or is ignored** — your call, but
  say which in the log line and never start a second overlapping burst. The
  30 presses tonight included nine inside twelve seconds, so this will happen.
- **Every frame in a burst is one capture with its own sidecar**, and the
  sidecar trigger says burst, which press it belongs to, and its index in the
  burst. A burst that cannot be reassembled later is just noise with a
  timestamp.
- **The existing single-frame behaviour must remain reachable** via a setting.
  If bursts turn out to be wrong for some situation, that should be a config
  change, not a rebuild.

## 4. The miner's timing does not change. Deliberately.

Sleven asked whether the miner could run on entering and exiting the game.
**It already does exactly that**, twice tonight, on start and on game exit:

```
[2026-08-12 17:51:04] mine: ...
[2026-08-12 19:09:36] mine: 244 logs read ...
```

**Build nothing here.** This section exists so nobody reads the conversation
later and adds a timer that was explicitly not wanted. If anything, the current
behaviour is better than a timer: mining on exit means the session's complete
log is read once, rather than a partial file being read repeatedly.

## 5. THE PRIVACY LEAK — one field, and it blocks every crew build

**This is the most important item in this document.** Nothing goes on anyone
else's computer until it is closed.

### Where it is

`gamelog.go`:

```go
LocationCandidates []string `json:"location_candidates,omitempty"`
```

When the location parser cannot confidently identify where the player is, it
writes **the raw log lines** into the sidecar so a human can read them and
improve the pattern. Raw lines carry `playerGEID`, the account handle, shard
IDs — everything.

**57 of 57 sidecars in the current captures folder carry player ID
`204354536218` this way.**

It is the single place in the entire collector that bypasses the allow-listing,
and it was deliberate. The file says so:

> capture once while actually in the PU, then read `location_candidates[]`...
> That is the intended path from UNVERIFIED to VERIFIED.

**It did its job.** Tonight's sidecars report `location_pattern_verified: true`.
The scaffolding is still standing and is now purely a liability.

### The fix

**Keep the diagnostic, drop the payload.** Replace the raw lines with the names
of the patterns that were tried and failed, plus a count. Something like:

```json
"location_why": "no location pattern matched",
"location_patterns_tried": ["gamerules", "requested_inventory", "zone_change"],
"location_candidate_lines": 4
```

That preserves everything the field was actually used for — *which matcher
should I be looking at* — and carries no log text at all.

**Do not attempt a regex that strips names out of the raw lines.** That is the
wrong shape of solution and it will fail quietly. See §5b.

**And handle what is already on disk.** 57 existing sidecars carry the ID right
now. Either rewrite them in place, stripping the field, or make the export path
refuse them (§6) — but do not leave a folder of leaking files sitting there with
a fixed program on top of it. State in your report which you did.

### 5b. On "detect player names and scrub them" — the honest answer

Sleven asked for this directly: *"whenever a player's name comes in, and we can
verify that it's a player's name, we scrub that information."*

**Arbitrary player-handle detection is not achievable and should not be
attempted.** Handles look like ordinary words. Any heuristic either misses real
handles or eats legitimate shop and item names, and both failures are silent.
Building it would produce a scrubber everyone trusts and nobody can verify.

Three things that ARE achievable, in priority order:

1. **Allow-list, never detect.** `mineTxnKeep` + `mineForbidden` in
   `gamelog_mine.go` is already correct and has never leaked across 308 rows. It
   is the model. Extend the same discipline to anything new that reaches disk.
2. **Scrub by DECLARED identity.** The log states the local player's handle and
   GEID in its own header lines. Read those once per session, then remove those
   exact strings everywhere downstream. This is not guessing what a name looks
   like — it is deleting a string the log itself identified as the player's
   name, which is verifiable and testable. `collector-scrub-salt.bin` already
   exists for the salted-hash variant if a stable per-player token is wanted
   without the name being recoverable.
3. **Do not mine the subsystems that carry other people's handles.** Actor and
   kill lines are where third parties appear. The miner's own gap report already
   lists Actor as unmined. **Keep it that way on purpose, and write the reason
   into the code** — otherwise somebody adds it in a year as an obvious
   improvement and reopens this.

**Write §5b's reasoning into a comment where the scrubbing lives.** The next
person to read this will have the same good instinct Sleven had, and the
argument against it needs to be sitting where they will find it.

## 6. Export guard — a hard check, not a happy accident

Sidecars have not escaped so far because the export path happens to send PNGs
and not their JSON. **There is no guard that says so.** A future change to
`export.go` could ship the lot and nothing would object.

**Build the explicit refusal:** nothing reaches an export bundle unless it has
passed a named allow-list check. A sidecar that has not been through the
scrubber does not go, and the reason is stated per file, the way the existing
quarantine already states `"no sidecar, so nothing states what was photographed"`.

**Cover it with a negative-control test** — hand the exporter a sidecar
containing `playerGEID` and assert that it is refused and that the refusal names
the field. A privacy guard with no failing-case test is a comment.

## 7. What NOT to do

- **Do not touch the transaction trigger or `reMineTxn`.** §0.
- **Do not add a miner timer.** §4.
- **Do not write a name-detection heuristic.** §5b.
- **Do not gate event or hotkey captures on `appears_in_game`.** §2.
- **Do not build a second burst implementation.** §3.
- **Do not publish a collector release or install `gh`.** Still not authorised.
- **Do not change the upload endpoint, `UPLOAD_KEY` handling, or
  `collector-receiver.worker.js`.** That order already exists
  (`prompt-code-collector-cloud-upload-2026-08-10.md`) and is blocked on Sleven
  doing the Cloudflare side, not on you.
- **Do not `git add -A`.** The tree currently shows ~220 modified files that are
  almost entirely line-ending noise from the Windows mount. Stage deliberately.

## 8. Acceptance

1. Sitting in the main menu for ten minutes produces **zero** interval captures,
   and the log says why once rather than every 120 seconds.
2. In-world, interval captures arrive ~120s apart. An existing settings file
   saying 60 still loads, and the log states the conversion.
3. A `terminal_open` event captures even if `appears_in_game` reads false.
4. One Alt+F3 press produces a burst of frames; each has a sidecar naming the
   trigger as a burst, the press it belongs to, and its index.
5. Two presses two seconds apart produce one coherent record, never two
   overlapping bursts.
6. Burst length and rate are settable; single-frame mode still reachable.
7. **No sidecar written after this change contains `playerGEID`, an account
   handle, a shard ID, or any raw log line.** Verified by grepping a fresh
   captures folder after a real session, not by reading the code.
8. The 57 existing sidecars are either cleaned or refused by export, and the
   report says which.
9. Handing the exporter a sidecar containing `playerGEID` is refused, and the
   refusal names the field.
10. `location_inventory_name` is either fixed, or reported as genuinely
    unexercised with the reasoning shown.
11. A full session run start to finish: miner still runs on entry and exit,
    transaction extraction unchanged, `gamelog-dataset.json` still grows.
12. Self-tests pass, including a new negative control for §6.

## 9. Report back

- Disk for a comparable session, before and after. The 818 MB / 380 MB-per-hour
  figures above are the baseline; a number is the only way to know this worked.
- What `location_inventory_name` turned out to be.
- Which route you took for the 57 existing sidecars, and why.
- The burst defaults you chose and the reasoning.
- Anything in §5 you think is insufficient. This is the item that gates putting
  the collector on another person's machine, and an optimistic report on it is
  worse than no report.

## Commands

```
go build ./...
```

```
go run . -selftest
```

```
git status --porcelain
```
