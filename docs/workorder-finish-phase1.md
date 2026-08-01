# WORK ORDER — finish Phase 1 (source 6 / UEX), and stop the handoff corruption

Three parts, in this order. Part A takes a minute and stops active damage. Part B finishes Phase 1. Part C is the Go migration that was ordered but never executed.

**Commit-and-push authority is granted for this order's scope only.**

Hard rule 13 applies throughout: file an `inbox/` update on intake, on each part completing, and on any stop.

---

# PART A — stop the stray Python watcher (do this first, it takes a minute)

Two processes are writing `LATEST_HANDOFF.md` and they are actively destroying each other's output. Measured today:

```
pipeline_log.txt        14:56:16  regenerated (104855 chars)
logs/inbox_watcher.log  14:57:10  regenerated (update #60, 67491 chars)
```

Fifty-four seconds apart. **37,364 characters discarded by the later, defective writer.** The gap is widening — it was 30,105 two hours ago.

`setup_watcher_task.ps1` registers only `inbox_watcher.exe`. The Python `inbox_watcher.py` is a leftover process from before the migration that was never stopped. It is not scheduled and will not return after a reboot, but it is running now.

**Stop it. Then verify by behaviour, not by a process list:** drop a test file into `inbox/` and confirm only `logs/inbox_watcher.log` gains a line while `pipeline_log.txt` does not.

Do not delete `generate_handoff.py` yet — that is Part C, and deleting it while the Python watcher runs is not a clean retirement.

**This makes the record stable while the rest of the work happens.** Everything else in this order files updates, and until Part A is done those updates land in whichever version the loser wrote.

---

# PART B — source 6, UEX Corp. This is what finishes Phase 1.

## Current state, verified on disk

- `data-layer/external-sources/uex*` — **does not exist.** Nothing has ever been pulled.
- `06_uex-corp_manifest.json` (run `20260731T031754Z`) reads `snapshot_status: blocked_missing_credentials`. That is still accurate.
- `UEX_API_TOKEN` is **absent from `.env`.** The token was obtained but never written.
- **There is no UEX retrieval script.** `scripts/external_sources/` holds scripts for sources 1, 2 and 3 only. This one has to be written, not just run.

## Why this source matters more than its tier suggests

Sources 1, 2 and 3 give stats, names, coordinates and a location graph. **None of them links an item to a shop to a price.** UEX is the only source that does, and "know where to buy, before you fly" is the site's entire stated purpose. Phase 1 without source 6 is Phase 1 without the load-bearing dataset.

## Credentials

Account exists: handle `slevenkoal`, UID 92424, app `Citizen-Compass`, status ACTIVE.

1. Write the token to `.env` as `UEX_API_TOKEN=`.
2. **Confirm `.env` is gitignored** — it is, `.gitignore:4` — and confirm it is untracked, not merely ignored.
3. **Verify with a single request before pulling anything.** One endpoint, one call, confirm a 200 and the expected envelope. Do not begin a full pull on an unverified credential.

**The token was exposed in a chat screenshot.** It is read-only access to public community data with a request quota, not account control — but regenerate it once the pull completes, and record in the manifest that the pull ran under a since-rotated credential.

## API facts (verified from UEX documentation 2026-08-01)

- Base: `https://api.uexcorp.uk/2.0/{resource}/`
- Auth: Bearer token
- Quota: 120 requests/minute, 172,800/day — not a constraint for a full pull
- Response envelope: `{"status": "ok", "data": ...}`
- An `X-Client-Version` header is supported. **Use it** — it means an outdated script cannot quietly keep pulling against a changed contract.

## Scope — pull these, and record what you did not pull

The goal is the item → terminal → price link plus enough location data to resolve where a terminal actually is.

- `items` — carries a `uuid` field documented as the **Star Citizen UUID**
- `items_prices_all` — item, terminal, location hierarchy, buy/sell price, weekly and monthly aggregates
- `terminals` — commodity, item, vehicle-rental and sales terminals
- `vehicles_purchases_prices_all` — ship prices by location
- `categories`, `companies` — needed to resolve foreign keys in the above
- The location hierarchy needed to make a terminal address meaningful: star systems, planets, moons, cities, outposts, space stations

**Pull only documented endpoints in scope. Do not crawl for siblings.** Record the scope boundary in the manifest the same way source 2's manifest does.

**The join worth knowing about:** UEX `items.uuid` is the Star Citizen UUID, and the already-collected `fps-items.json` carries the same UUIDs in `reference` and `stdItem.UUID`. So the 5,420 gear records already on disk join to UEX pricing on UUID with no name matching. Do not build a name-matching path — that is where this kind of integration usually rots. Note the join key in the manifest.

## Tier C — this must be in the manifest, not just understood

UEX states its own data is community-reported and crowdsourced, with tolerances of **±20% on commodities and ±100% on items.**

Under the canonical-source decision this is **Tier C**: authoritative for aUEC prices and in-game dealer locations because nothing else has them, and **never auto-promoted without review.** Record this explicitly in the manifest so no downstream consumer can mistake it for game-file truth. A manifest that is silent on tier is a manifest that will be misread.

## Retrieval script requirements

Write `scripts/external_sources/uex_corp.py` to the standard the other retrieval scripts now meet. Non-negotiable, because every one of these was a real defect somewhere else in this project:

- **Write-before-status is forbidden.** A response earns its final filename only after status 200, a JSON content type, and a successful parse. Rejected responses are never written.
- `Timeout` and `ConnectionError` are retryable against a ceiling, with backoff.
- `Retry-After` parsed in **both** RFC 7231 forms — integer seconds and HTTP-date — clamped to a sane range, with a fallback for garbage. Calling `int()` on that header raised `ValueError` and killed a run in this project, at the exact moment the server was asking us to back off.
- Per-response `byte_size`, `sha256`, `attempts`, `attempt_log` and measured `elapsed_seconds` recorded.
- **`main()` returns 1 if any endpoint did not land.** A `main()` that returned `None` is precisely how source 2 was marked "complete" on a run that verified nothing.

**Rule 12 applies to the script itself.** Before trusting it, feed it something that must fail and confirm it fails — a rejected status, an unparseable body, a rate-limit response. A retrieval script whose failure path has never executed is untested no matter how many times it has succeeded.

## Gates

Run all five in order, same sequence as the source 1 and source 2 re-lands: files present → JSON parses → file-type inspection → Defender scan with `-DisableRemediation` → content-indicator scan. Malware scan precedes the rename out of `.partial`. Re-hash after the scan and confirm the bytes that were scanned are the bytes that were finalized.

Write a manifest that **earns** its status rather than asserting it.

## When Part B is genuinely done

Source 6 closed means five sources collected and two correctly ruled out (source 4 self-blocked on provenance, source 5 not directly downloadable). **That is Phase 1 complete, and it is the first time that will be true.** Say so in the manifest and in the inbox update — and do not say it before the gates pass.

---

# PART C — the Go migration (ordered earlier, never executed)

Both work orders are already on disk and unchanged:

- `docs/workorder-go-migration.md`
- `docs/workorder-go-migration-addendum.md`

Verified still outstanding as of now:

- `watcher-go/handoff_regen.go:108` — `strings.Split(string(raw), "\n### ")`, unchanged
- `watcher-go/handoff.go:49` and `:65` — both still `firstRunesUpper(text, 500)`
- `generate_handoff.py` — still present

Execute both documents as written. Part A has already handled the stray-process step the addendum calls for, so pick up from Defect 1.

Do not skip step 4's stop condition: if Go and Python output still disagree after both fixes, **there is a third difference — stop and report.** Do not assume Go is correct because it was fixed twice.

---

## Boundaries

- Nothing outside these three parts.
- Live site untouched. `static/preview.html`, `releases/latest.html`, anything deployed.
- Nothing under `testing/` gets committed except `_layer.html` and `build.py`. `testing/_deploy/` is 344 MB and is gitignored.
- No promotion of UEX data into the database. This is Stage 1 — collect and seal. Stage 2 does not exist yet.
- If any part blocks, write to `inbox/`, stop that part, and move to the next. A stopped part with a clear note is a good outcome.
