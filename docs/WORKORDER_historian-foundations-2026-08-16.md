# WORK ORDER — one thing is being thrown away every time it changes, and it is the foundation the Historian's best feature would stand on. Fix that this week. Everything else here is a decision, not a build.

    from      C3 (Cowork), 2026-08-16
    for       C1 -> Code (§1 only) and Sleven (§3, §4)
    prompted  Sleven: "ten ways to improve the AI historian idea"
    basis     claude/ai-historian-ten-improvements-2026-08-16.html - the ten
              ideas in full. This order carries only the parts that are
              time-sensitive or expensive to reverse.
    scope     The Historian is a parallel side project, approved to start
              LATER, not now. **Nothing in this order builds any of her.**

---

## 0. Why this exists and what it deliberately leaves out

Ten ideas were produced. **Seven of them can wait indefinitely and lose nothing by
waiting.** They are recorded in the HTML and should stay there.

**Three cannot wait**, for two different reasons:

    §1  something is being DESTROYED on every run, right now
    §2  an architecture choice that becomes a rewrite if made later
    §3  a product boundary that every future feature will ask about

That is the whole order. **It is short on purpose** — a side project that has not
started does not need a build plan, it needs the handful of doors kept open.

## 1. URGENT AND CHEAP — the watcher records that something changed, then destroys what it was

**This is a live data-loss defect, found while checking whether the Historian's
strongest feature had a foundation. It does not, yet, and the reason is fixable
this week.**

The best idea on the list is that she answers **"what changed"** — the one thing no
wiki, tool or spreadsheet in this hobby keeps, because they all overwrite. Citizen
Compass decided not to. That decision is currently only half-implemented.

**In `roadmap-watcher/store.go`:**

    Fingerprints map[string]string   // ONE fingerprint per card

`Diff` compares the new fingerprint against the stored one, reports the change,
and **writes the new value over the old one.** The previous fingerprint is gone.
The only surviving trace is a line in a text log.

**So the watcher can tell you a card changed. It cannot tell you what it changed
from, and it cannot be asked a question about last month at all.**

**`data-layer/derived/model-fingerprints/model_fingerprints.json` has the same
shape** — one current snapshot per model, no history. Mine. Same defect, and I
built it that way three days ago without thinking it through.

**What to change:** keep the current-state map exactly as it is — the diff logic
depends on it and works. **Additionally append every observation to a durable log**,
one line per card per run, never rewritten:

    timestamp, board, card_id, name, release, fingerprint, source

**Append-only. JSONL is fine. A table is better.** The requirement is that nothing
ever overwrites a previous row.

**Why this is urgent when the Historian is not:**

- **The value is entirely in elapsed time.** A history started today is worth
  something in six months. A history started in six months is worth nothing for a
  year. **Every week of delay is a week permanently missing from the archive.**
- **It cannot be backfilled.** Not from CIG, not from anywhere. History nobody
  wrote down is gone.
- **It is nearly free.** One append per card per run, six runs a day, a few hundred
  cards. Kilobytes.

**Do the roadmap watcher and the model fingerprints the same way**, so a later
query can read both as one time series. That is the only design constraint here.

**Rule 12 applies:** the check that matters is one proving a *changed* card produces
two rows with different fingerprints and both survive. A history that has never been
observed retaining anything is the same category of thing it exists to prevent.

## 2. DECIDE BEFORE ANY CODE — the model must never decide a fact

**This is the one that becomes a rewrite.** Recording it now so the decision is made
deliberately rather than by whoever writes the first prototype.

**The obvious build** — hand the question and some data to a language model, read
out what comes back — **cannot be made trustworthy and cannot be made cheap.**

**The alternative:** classify the question, run a deterministic query, hand the model
the result and let it choose wording only.

    question -> classify -> deterministic QUERY -> rows
                                                -> model phrases those rows
                                                -> answer

**The model never produces a number. It only produces sentences about numbers it was
handed.**

**Why it matters more here than in most products:** the existing design notes already
name the real risk — *"she raises the cost of being wrong"*, because a spoken answer
gets believed where a table row gets shrugged at. **A model that can generate a
figure can generate a wrong one.** A model that can only rephrase four rows cannot.

It also solves the cost problem the notes flag: identical questions within one patch
return identical query results, so answers cache, keyed on question plus patch and
invalidated when the patch changes.

**Nothing to build. This is a decision to record so it is not made by accident.**

## 3. SLEVEN'S — two boundaries every later feature will ask about

**Neither is a compliance question.** The rights topic is settled
(`RULING_rights-questions-are-settled-2026-08-14.md`) and this order does not
reopen it. These are product-shape questions, and the ruling explicitly names a
move to monetisation as a new fact that may be raised as one.

**3a. Where the paid line sits.** The standing decision is that Star Citizen
information stays free forever and only on-demand AI access is monetised. **A more
precise line is available**: free covers every fact about the game, in text, on the
website. Paid covers things that are about *you* or about *now* — your own log read
and remembered, the in-flight voice companion, stock alerts, your fleet.

Three independent arguments point the same way: CIG's information stays entirely
unpaywalled; the per-visitor and live work is where the cost actually is; and it is
the version that survives being explained to the community.

**3b. Whether the in-flight companion is a real second product.** The original idea
was querying while flying instead of alt-tabbing. **The move to the website quietly
dropped it**, and the design notes now describe a page-anchored character with a holo
pad who points at a ship table.

Both are right, but they are two products sharing one data layer, and they disagree
about latency, visuals and whether she points at all:

    website        pointing matters, 8s answers acceptable, character art central
    in-flight      audio only, under 3s, screen dark, NO character art needed

**Pointing is what drives the commission budget.** If the in-flight version is real
and goes first, **the art is not on the critical path at all** — and that changes
what gets built and what gets paid for, before any money is spent.

## 4. FREE, AND SLEVEN IS THE ONLY ONE WHO CAN DO IT

**Write one hundred questions with known answers.** An evening's work, no code, no
dependency on anything being built.

    How many size 3 weapon mounts does a Vulture have?
    Which manufacturer makes the Syulen?
    Which ships have no price data at all?     <- correct answer: "I don't know"
    Is XenoThreat running right now?           <- correct answer: REFUSE

**Include questions she must refuse.** The failure mode that kills her is not a wrong
number, it is a confident improvisation. **An exam that only rewards answers teaches
her to answer.** This project already applies exactly that rule to code — every check
needs a case that could have failed it — and it is why the exporter and the
fingerprints are trusted.

Written once, it is a regression test for years, and it can be written today.

## 5. Recorded, NOT for now

The other ideas are in the HTML and should stay there until the side project actually
starts: browser-side game-log reading, speaking the age of every answer, logging
unanswered questions, turning gaps into collector recruitment, and wiring her to the
live 3D viewer. **All good, none urgent, none lost by waiting.**

## 6. What I checked and what I did not

**Checked:** `roadmap-watcher/store.go` directly — the `Fingerprints` map, `Diff`'s
mutation, and `SaveState`. The data loss in §1 is read from the source, not inferred.
`LoadState` already fails closed on a corrupt store specifically so history is not
silently discarded, **which is the right instinct applied to the wrong half of the
problem** — it protects the baseline it has, while the per-run history was never kept.

Every figure quoted in the HTML was checked against the project's own files today.

**Did NOT check:**
- **Whether an append-only log should be JSONL or a database table.** That is Code's
  call and depends on what the query layer becomes. The only hard requirement is that
  nothing overwrites.
- **Whether a small model can carry her voice well enough to be worth hearing.** Open,
  unanswered, and it decides whether the whole thing is worth doing.
- **Any cost figure.** Nothing here is costed and §3 should not be decided on my
  arithmetic.
- **I have not built or changed anything**, including the fingerprint file of mine
  that §1 says is wrong.
