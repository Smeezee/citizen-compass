# WORK ORDER — a claim register, so "CIG has not said this yet" stops being a dead end and becomes a thing we re-ask automatically. Plus three tripwires that would catch a Constellation rework before CIG announces it.

    from      C3 (Cowork), 2026-08-14
    for       C1 -> Code
    prompted  Sleven: "is there any way that we could keep track of this stuff and
              hold this data and see if we can find truth to it?"
    context   the Constellation rework question was closed three independent ways
              today. That answer is correct AND it expires.

---

## 1. The problem with today's result

We spent a day establishing that **CIG has made no public statement about a
Constellation rework.** Three independent negatives — Progress Tracker, five
Spectrum threads, and two full broadcast transcripts including one where gold
standard is explained at length and the host asks directly what gets it next
year.

That is a good result. It is also **true only as of 2026-08-14**, and Sleven's
read of the odds is sound: CIG runs gold standards and Mk2s on old ships
constantly, RSI's build quality has moved a long way, and the Constellation is
old and popular. A rework is foreseeable.

**So the finding is not "no". The finding is "not yet, checked on this date, by
these methods."** If we file it as "no", the next session reads it as settled and
stops looking. If we file it as a dated negative with a re-check, it keeps
working for us.

**This is the same instinct as `last_verified_patch` on a data row, applied to a
question instead of a fact.** The project already believes this; it just has
nowhere to put a question.

## 2. What to build — `data-layer/derived/claims/`

A register of open claims. One JSON object per claim. The point is not to store
rumours; it is to store **what would change our mind, so the check can be
repeated cheaply and by somebody who was not here today.**

    {
      "id": "constellation-rework-mk5",
      "claim": "The RSI Constellation series is getting a rework / Mk5, with
                current models receiving a gold standard pass.",
      "origin": {
        "source": "leak aggregator @Leak News, via a YouTube video",
        "tier": "testimony",
        "note": "the video is unrecoverable; the only record is a photograph of
                 somebody else's screen. This claim can never be strengthened."
      },
      "status": "unsupported",
      "last_checked": "2026-08-14",
      "checked_by": ["C3", "CIC"],
      "evidence_against": [ ...the three negatives, with URLs... ],
      "would_confirm": [ ...see section 3... ],
      "would_refute": [],
      "recheck_after_days": 60
    }

**`status` vocabulary, kept small on purpose:**

    unsupported   nobody official has said it. NOT the same as false.
    supported     an official source says it. Cite it.
    contradicted  an official source says the opposite.
    resolved      it happened, or it definitively did not.

**`unsupported` is the important one.** It is the state today's Constellation
answer belongs in, and it is the state that most needs re-checking. Recording it
as `false` would be the actual error.

## 3. The tripwires — and one of them is ours alone

**Three cheap external checks**, all of which a script or a browsing session can
run without judgement:

1. **Progress Tracker** — does a deliverable containing "Constellation" exist?
   Today: exactly one, an RSI Constellation Taurus card **last updated 2021-08-11**.
   Any newer card is a signal.
2. **Roadmap Roundup comm-links** — does any name a Constellation? Gold standard
   passes appear there by name; that is how the Hammerhead and Aurora passes were
   visible.
3. **Broadcast transcripts** — does "Constellation" appear in an Inside Star
   Citizen or Star Citizen Live episode alongside "gold standard", "rework",
   "Mark 2" or "Mark 3"? **This is the surface that produced today's strongest
   negative and it is checkable per episode as they air.**

**And the fourth, which nobody else can run: we hold the geometry.**

A rework changes the hull. We have 235 `.glb` models and published dimensions for
every ship. **A Constellation rework would show up in our own data before, or
independently of, any announcement:**

- the `.glb` for a Constellation variant changes — different file hash, different
  vertex count, different bounding box
- the published length / width / height in the ship spec data change

Both are already measurable with what tonight's fleet work built. The placement
pipeline computes a bounding box for every hull and compares it against CIG's
published dimensions — **that comparison is already running.** Recording the
result per ship turns it into a change detector for free.

**That is worth more than watching for an announcement**, because it catches the
thing itself rather than the talking about it. And it generalises: it is a rework
detector for all 235 ships, not just the Constellation.

## 4. Where this plugs into what already exists

**Nothing new architecturally.** Three existing pieces do the work:

- **The auditor layer** gets a `claims_checks` group. It flags only, never
  resolves — a claim moving from `unsupported` to `supported` is a human call,
  and the auditor's job is to say "this needs looking at."
- **The results table** already exists for auditor findings. A due re-check is a
  finding.
- **The RSI watcher** is already polling RSI. A Progress Tracker / Roadmap
  Roundup check is one more thing for it to look at.

**The geometry tripwire needs one new thing:** a stored fingerprint per model —
file hash, vertex count, bounding box — so a change is detectable. That is a
small table and tonight's extraction already produced every value in it for 174
ships.

## 5. Seed the register with what today produced

Four entries, ready now:

    constellation-rework-mk5    unsupported   three independent negatives
    drake-marauder-exists       unsupported   no referent anywhere; Drake's 2026
                                              slot filled by the Pitbull; Drake's
                                              only announced-unreleased ship is
                                              the Kraken Privateer (2019)
    origin-m60-exists           unsupported   no referent; Origin's 2026 slot
                                              filled by the M80; Origin has zero
                                              announced-unreleased ships
    rsi-skylark-exists          unsupported   one wiki hit in total, an RSI Meteor
                                              paint. Sleven reports having heard
                                              the name — recorded as an open
                                              thread, not as evidence
    gatac-hyun-exists           unsupported   Gatac roster is Railen, Syulen,
                                              Tyilui. "Hyun" does not match Xi'an
                                              naming conventions

**Each carries the same note: absence from public sources is weak evidence, and
CIG has moved to announcing ships closer to flyable — so an unannounced 2027+
ship would have no public footprint by design.** That is not a reason to believe
the leak. It is a reason not to record `false`.

## 6. Why this is worth doing beyond one rumour

Sleven's standing goal is preservation — keeping what Star Citizen has had,
including what changed and what went away. **A claim register is the same idea
pointed forward instead of back.** Today's "CIG has not announced this" is
tomorrow's "and here is exactly when they did, and here is what we checked before
they said it."

It also protects against the failure this project keeps logging: **a stale answer
sitting under a confident filename.** A dated negative with a re-check date
cannot quietly become wrong, because the register knows when it was last true.

## 7. What I checked and what I did not

**Checked:** that the three external tripwires correspond to sources that actually
produced today's negatives; that the geometry comparison already exists in
tonight's fleet placement work and needs only its output stored; that the auditor
layer's flag-only rule fits without amendment.

**Did NOT check:**
- **I have not built any of this.** It is a design, and the schema in §2 is a
  sketch to argue with, not a spec to implement verbatim.
- The `recheck_after_days` value of 60 is a guess. It should be argued, and it
  probably differs per claim — a rework question and a "does this ship exist"
  question do not age at the same rate.
- Whether the RSI watcher can read the Progress Tracker. It is client-side
  rendered and defeated WebFetch entirely today; CIC read it with a real browser.
  **If the watcher cannot, that tripwire needs a browsing session and is not
  free.** Somebody should establish which before this is scoped.
