# WORK ORDER — the roadmap watcher. Complete and standalone: endpoints, cadence, on-demand check, the two silent-failure traps. This is the ONLY document to build from.

    from       C3 (Cowork), 2026-08-14
    revision   2. CIC closed both open items and found a bug in rev 1 that would
               have shipped. Changes are marked. If you have rev 1, discard it.
    for        C1 -> Code
    supersedes WORKORDER_rework-tripwire-build-spec-2026-08-14.md and BOTH copies
               of AMENDS_tripwire-release-view-only-2026-08-14.md.
    origin     Sleven: "is there any way that we could keep track of this stuff and
               hold this data and see if we can find truth to it?"

---

## 0. What changed in rev 2, and one of them was my error

**My rev 1 said: "does any deliverable whose title contains 'Constellation' exist,
beyond the one known card?"**

**There is not one known card. There are at least three, and the string
"Constellation" appears 23 times in the Release View payload** — Taurus (3.14),
Phoenix (3.3), Merlin/Constellation Docking (3.13), all historical, all `Released`.
**A tripwire built to rev 1 fires on its first run and every run afterwards,
forever.** CIC caught it before anyone wrote a line.

**The cause is worth naming because rev 1 warns against it in §6.** The "exactly one
card" figure came from the **Progress Tracker**. I applied it to **Release View**.
Two boards, two different card sets — which is the precise mistake my own coverage
section exists to prevent. I made it while writing the section.

Also corrected: conditional requests do not work (tested, not assumed), the payload
is 149 KB on the wire not 820 KB, and dead boards return HTTP 200.

## 1. What this is for, in one paragraph

CIC established three independent ways that **CIG has said nothing publicly about a
Constellation rework.** That answer is correct and it expires. This watcher exists so
"nothing yet" gets re-checked automatically instead of by somebody remembering to
ask. **The signal we want is a NEW Constellation card appearing on CIG's roadmap.**

## 2. Endpoints — both approved, staged rollout

    STAGE 1 - build and schedule now
    GET https://robertsspaceindustries.com/api/roadmap/v1/boards/1
    149 KB on the wire (gzip), 820 KB decoded, ~850 ms

    STAGE 2 - build now, schedule when Sleven says
    POST https://robertsspaceindustries.com/graphql
    operation `deliverables` under a `progressTracker` root
    Content-Type: application/json and nothing else
    required vars: startDate, endDate  (String!, non-nullable)
    optional:      search, deliverableSlug, teamSlug, projectSlugs [String],
                   categoryIds [Int], sortBy: SortMethod, offset: Int, limit: Int
    response:      data.progressTracker.deliverables.totalCount + metaData[]
    targeted call is ~125 bytes on the wire, ~93 ms

**Stage 2 is approved, not refused.** Sleven's decision was to roll out in
increments — prove one endpoint, then add the second. **Build both clients now.**
Stage 2 sits behind a config flag he flips when he is ready.

**CIC verified stage 2 needs no session**: same call with credentials omitted and
referrer suppressed returned HTTP 200 and an identical result.

**Board enumeration is closed.** An undocumented index at `/api/roadmap/v1/boards`
returns exactly two: board 1 `Release-View` (live, 4.9.0) and board 2 `Squadron-42`
(**frozen** — its own description says it will not be updated). Boards 3, 4, 6 and 10
do not exist. **There is no third surface and stage 1 misses nothing for
board-numbering reasons.**

## 3. TWO SILENT-FAILURE TRAPS — both produce a false "nothing found"

**These are the most important paragraphs in this document.** Both failure modes look
exactly like a clean negative result on a tripwire whose only job is to not miss
something.

### 3A. Errors arrive as HTTP 200

A nonexistent or failed board returns **status 200** with the failure in the body:

    {"success":0,"code":"ErrInvalidObject","msg":"Specified board does not exist.","data":null}

**A client that checks `resp.StatusCode == http.StatusOK` and proceeds reads a dead
board as a valid response with zero cards** — byte-for-byte the same conclusion as
"no Constellation card found."

**Branch on the `success` field, never on the status code.** Treat `success: 0` as an
error that raises an alert, not as an empty result.

### 3B. "Constellation" already appears 23 times

Every occurrence is historical and `Released`. **Substring-matching the response body
fires immediately and permanently.**

The check must be **either**:

    a diff against a stored baseline of known card IDs, or
    a match scoped to UNRELEASED releases only (4.9 / 4.10 / 4.11 /
      Star Citizen 1.0 as of 2026-08-14)

CIC verified **the unreleased slice is currently clean**, so a baseline captured now
is a valid zero point.

**Store the release name alongside every card.** Then "Constellation card on Release
View, release 3.14, Released" can never be misread as a new one. This is the same
principle as writing the surface name into every result — a record that does not
carry its own context gets misread eventually.

## 4. The baseline — let the watcher capture its own

**Do NOT hand-capture the baseline from a browser and load it in.**

The watcher's own first run must write the baseline, through the **same code path**
that will later do the diffing. A baseline captured by a different client normalises
fields differently — whitespace, entity decoding, key ordering, date parsing — and
**every one of those differences shows up as a false alert on run one.**

This is the same rule already applied to the on-demand check in §5, for the same
reason.

**CIC's independent snapshot is still valuable — as a cross-check, not as the
baseline.** After the watcher writes its own, compare the two. If they disagree, the
watcher's normalisation is wrong and that is worth knowing before it runs unattended.

## 5. Cadence and the on-demand check

**Every 4 hours** as a starting value. Sleven's words: *"not every hour, but, you
know, every few hours."* Put the interval in config so he can move it without a
rebuild. **Hourly is out.**

**Cost is no longer an argument about cadence.** Stage 1 at four-hourly is ~900 KB a
day on the wire, not the ~4.9 MB rev 1 implied. That is a rounding error.

**A manual "check now" command is a requirement.** Sleven: *"if I say, hey. Go check
this. A simple command set up."*

**It must run the same code path as the timer.** Not a separate script, not a debug
mode, not a different query. If a hand-run and a scheduled run can disagree, the
hand-run is useless for checking on the scheduled one — which is most of what it is
for. **Output goes to the same store**, marked as manually triggered.

## 6. Transport — one line that costs 5.5x if someone "improves" it

**Leave `Accept-Encoding` unset and do not build a Transport with
`DisableCompression: true`.** Go's `net/http` negotiates gzip transparently and
decompresses for you. Setting either silently turns a 149 KB pull into an 820 KB one.

**Put a comment in the code saying so**, because it looks like an omission and
somebody will helpfully add it later.

**Conditional requests do not work — tested, not assumed.** `boards/1` returns no
`ETag`, no `Last-Modified`, and sets `Cache-Control: no-store`. CIC sent both
`If-Modified-Since` and `If-None-Match` and got a full 200 either way. **There is no
304 path. Do not build one.** Rev 1's "try it first" instruction is answered.

## 7. What to key on

**Primary: a new card appears.** Diff against the stored baseline by card ID. A
Constellation gold standard or Mk5 arrives as a **new card**, not as an edit to an
existing one.

**Secondary: a payload hash per card** — normalise, hash, store, flag any card whose
hash moves. Catches edits without trusting a date.

**Do NOT key on `updateDate`.** The API returns `Wed, 21 Aug 2024` for the same card
the UI renders as "Updated Aug. 11th, 2021" — three years apart. **Store both dates
as data. Trigger on neither.**

**Same mechanism as `data-layer/derived/model-fingerprints/`** — snapshot, store,
diff. **Do not generalise them into a shared pipeline yet**; the standing rule is 2-3
concrete integrations first, and this is two and three. Keep the *stored record* the
same shape in both so generalising later is a refactor, not a rewrite.

## 8. Parser traps

**Dates are RFC-1123, not ISO 8601** — `"Mon, 11 Jan 2021 00:00:00 +0000"`. Go's
`time.RFC1123Z` handles it; an ISO layout will not.

**Descriptions are HTML-entity-encoded** — `RSI&#039;s`. **Title matching is safe.
Description matching is not**, and a search for an apostrophe-bearing phrase silently
returns nothing. Unescape first if needed.

## 9. Coverage while stage 1 runs alone

The two boards diverge. Gold-standard cards on each:

    on both surfaces          Retaliator
    Release View only         Aurora, Hammerhead
    Progress Tracker only     Gladius, Sabre Raven, Cutlass, Greycat PTV, 600i

**While stage 1 runs alone the watcher must report "no new Constellation card on
Release View" — never "no Constellation activity."** Write the surface name into
every stored result and every alert.

**One design note for when stage 2 lands.** The targeted GraphQL query is cheap
because the `search` filter runs server-side — but **it only answers the question you
asked.** Stage 1 downloads the whole board, so it can diff *everything* and catch a
card nobody thought to watch for. **Prefer pulling the full deliverable set on stage
2 as well**, for the same reason. The Constellation is today's question; the watcher
should outlive it.

## 10. Blocked / not blocked

**Not blocked.** Sleven approved both endpoints and set the cadence. Board
enumeration and the conditional-request question are both closed. **Build it.**

## 11. Why this document replaces three others — a live watcher defect

**C1 would have read the wrong file.** The inbox watcher **never overwrites**: a
corrected document keeps the plain filename on the WRONG version and the correction
lands under a timestamped one nobody opens. Rev 1 of the AMENDS misstated a decision
of Sleven's and carried his name. Both AMENDS files now contain only a redirect here.

**Also:** `WORKORDER_rework-tripwire-build-spec-2026-08-14.md` was routed into
`docs/handoff_archive/` rather than `docs/`.

**Neither defect is fixed and this will happen to the next corrected document.** Not
C3's lane. Someone needs to own it.

## 12. What I checked and what I did not

**Checked:** that rev 1's "one known card" figure came from the Progress Tracker and
was wrongly applied to Release View — the error is mine and it is the reason §3B
exists.

**Did NOT check:**
- **I have not independently verified any endpoint behaviour.** The board index, the
  200-on-error envelope, the missing cache validators, the wire sizes and the 23
  Constellation occurrences all come from CIC. My tools cannot POST and I did not go
  around them. **CIC's results have been right and mine have needed correcting twice
  today** — weight them accordingly, but a first run still confirms or refutes all of
  it in one shot.
- **Whether board 2 (Squadron 42) could ever un-freeze.** Its description says it will
  not be updated. If SQ42 ships and the board revives, that is a new surface and this
  order does not cover it.
- **What the UI's "Updated Aug. 11th, 2021" actually reads.** It is not `updateDate`.
  It may be a field the API returns under another name, which would be the better one
  to store.
