# WORK ORDER — build spec for the rework tripwires, now that the endpoints are known. Watch BOTH roadmap surfaces, key on card presence and a payload hash, and do NOT key on updateDate.

    from      C3 (Cowork), 2026-08-14
    for       C1 -> Code
    follows   WORKORDER_claim-register-and-rework-tripwires-2026-08-14.md, which
              designed the tripwires but could not specify them: nobody knew
              whether the Progress Tracker was reachable without a browser.
    input     CIC's endpoint discovery, 2026-08-14. It is.
    blocked   §5 - one decision is Sleven's and the build stops there until he
              makes it.

---

## 1. What changed

The earlier work order said: *"Whether the RSI watcher can read the Progress
Tracker... if the watcher cannot, that tripwire needs a browsing session and is not
free. Somebody should establish which before this is scoped."*

**Established. It can, and it is free.** CIC pulled the query signature out of the
roadmap JS bundle rather than guessing it, called the endpoint directly, and
compared the result against what the UI renders — they match. Then ran it again
with credentials omitted and the referrer suppressed: HTTP 200, identical result.
**No cookie, no CSRF token, no auth header, no referer check.**

That removes the headless-browser problem entirely. A Go program can do this.

## 2. Watch BOTH surfaces. This is not belt-and-braces.

    Progress Tracker   POST https://robertsspaceindustries.com/graphql
                       operation `deliverables` under a `progressTracker` root
                       requires startDate and endDate (String!, non-nullable)
                       Content-Type: application/json and nothing else

    Release View       GET  https://robertsspaceindustries.com/api/roadmap/v1/boards/1
                       ~820 KB JSON, no body, no headers

**They are different datasets and neither contains the other.** CIC checked the
gold-standard cards on each:

    Progress Tracker   Gladius, Retaliator, Sabre Raven, Cutlass, Greycat PTV, 600i
    Release View       Retaliator, Aurora, Hammerhead

Retaliator is on both. **Aurora and Hammerhead appear only on Release View;
Gladius, Sabre Raven, Cutlass, PTV and 600i appear only on the Progress Tracker.**

**So watching one surface gives false negatives.** The tripwire's entire job is to
notice a Constellation card appearing. A Constellation gold-standard pass that
landed on Release View only would be invisible to a Progress Tracker watcher, and
the watcher would report "nothing found" — which is worse than not having it,
because somebody would believe it.

The second surface costs one plain GET. **Do both.**

## 3. Key on card PRESENCE and a payload hash. Do NOT key on `updateDate`.

CIC found the trap and it would have bitten whoever built this:

    API returns   updateDate: "Wed, 21 Aug 2024 20:25:52 +0000"
    UI renders    "Updated Aug. 11th, 2021"

**Same card. Two different dates, three years apart.** A tripwire keyed on
`updateDate` reports a number no human can find on the page, and any alert it raises
would be unreproducible by the person checking it.

**The primary signal is presence.** A Constellation gold standard or Mk5 would
appear as a **new card**, not as an edit to the 2021 Taurus one. So:

    does any deliverable whose title contains "Constellation" exist,
    beyond the one known card?

**The secondary signal is a payload hash** — normalise each card's fields, hash them,
store per card, and flag any card whose hash moves. That catches an edit to an
existing card without trusting either date field. **Store both dates as data; use
neither as the trigger.**

**This is the same mechanism as `data-layer/derived/model-fingerprints/`** — snapshot
a payload, store the fingerprint, diff on the next run. Two different sources, one
shape.

**Do NOT generalise them into a shared pipeline yet.** The project's standing rule is
2-3 concrete integrations before abstracting, and this is concrete number two and
three. Build them plainly, and make the *stored record* the same shape in both so
that generalising later is a refactor rather than a rewrite.

## 4. Parser notes — two things that will break a naive implementation

**Dates are RFC-1123, not ISO 8601.** `"Mon, 11 Jan 2021 00:00:00 +0000"`. Go's
`time.RFC1123Z` handles it; `time.Parse` with an ISO layout will not.

**Descriptions are HTML-entity-encoded** — `RSI&#039;s`. **Matching on a title is
safe. Matching on description text is not**, and a search for an apostrophe-bearing
phrase will silently return nothing. If description matching is needed, unescape
first.

## 5. BLOCKED — one decision, and it is Sleven's alone

**Whether Citizen Compass may call an undocumented RSI endpoint on a schedule is a
rule 8 question.** Finding it committed us to nothing; polling it is a different
act. It sits next to the project's open RSI permissions item.

**Nothing in this order may be scheduled until Sleven clears it.** Writing and
testing the client against a handful of manual calls is fine. **A timer is not.**

Two things that should inform the decision rather than be assumed:

- **The Release View GET is the milder ask** — a plain public JSON endpoint, no
  POST body, no reverse-engineered query. If only one is cleared, that is the one to
  ask for.
- **Poll rate is the whole risk.** This data changes weekly at most. A daily check is
  generous; an hourly one is indefensible and is the shape of thing that gets an IP
  blocked and a relationship damaged.

## 6. What I checked and what I did not

**Checked:** that the two gold-standard card lists CIC reported genuinely do not
overlap except on the Retaliator, which is what makes §2 load-bearing rather than
cautious.

**Did NOT check — and this matters:**

- **I have not independently verified the endpoint, the no-session result, or the
  date discrepancy.** All three come from CIC's report. My tools cannot POST, and I
  am not going around them to check. **The no-session claim is the load-bearing one**
  — the entire design in §2 collapses back to "needs a browsing session" if it is
  wrong. Whoever builds this will find out on the first run; that is acceptable, but
  it should be known going in rather than discovered as a surprise.
- **Whether `boards/1` is the only board.** The path is numbered. If there are other
  boards, this watches one of them.
- **What the UI's "Updated Aug. 11th, 2021" is actually reading.** It is not
  `updateDate`. It may be a field the API also returns under another name, in which
  case that field is the better one to store — worth five minutes before building.
