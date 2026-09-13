# PERPLEXITY — the landscape report, what it validates, and the three things that go straight into the build

**Filed 2026-09-10 by the Adjutant desk. Source: Perplexity, answering the discovery
brief `claude/PERPLEXITY_find-the-tools-we-do-not-know-about-2026-09-10.md`. It was
given no access to this project and described only the shape of the system.**

**NOTHING HERE IS AUTHORISED AND NOTHING HAS BEEN INSTALLED.** The tools it names are
mostly small and young; several of its licence and maturity claims are explicitly
unverified in its own text. **The VALUE OF THIS REPORT IS THE IDEAS, NOT THE TOOLS.**

---

## 1. THE VERDICT ON OUR ARCHITECTURE, WHICH IS THE PART TO READ FIRST

> "Your filesystem mailroom is not an idiosyncrasy: it is a recognizable durable
> mailbox / letterbox pattern."

> "Your architecture already occupies an unusually sensible point in the landscape:
> plain local files for coordination, deterministic independent supervision, and
> humans as the only authority for state change."

**And it named our weak points without being told them:**

    atomic delivery
    recipient discovery
    acknowledgment semantics
    stale work
    PROVING AN EXPECTED EFFECT OCCURRED RATHER THAN MERELY OBSERVING A CLEAN EXIT

**The last one is this project's signature defect, identified from a generic
description of the system by a search tool with no access to it.** That is
corroboration worth more than any tool in the report.

**Its closing judgement:** the market has many orchestration demos and few proven
answers for unattended, local, multi-CLI agent operation. **The mature ideas it names
are unglamorous** — explicit acknowledgments, correlation IDs, immutable audit logs,
artifact verification, project files as the authoritative memory layer, and
enforcement outside the model.

---

## 2. THE LAYERED PROOF MODEL — THIS GOES INTO THE BRAKES SPEC

**Its central point: "The mature answer is not heartbeat versus dead-man switch. It is
usually all of these, each answering a different question."**

    LEASE / HEARTBEAT    is the worker alive, and is its work cursor ADVANCING
    PROGRESS EVIDENCE    what changed since the last heartbeat - files inspected,
                         test count, memo stage, artifact hash
    OUTCOME VERIFIER     does the expected artifact exist and satisfy schema,
                         content and FRESHNESS rules
    RECONCILER           which requests have no matching terminal result, or are
                         past their deadline
    DEAD-MAN ALARM       did the SUPERVISOR ITSELF stop producing reconciliation
                         evidence
    CANARY JOB           can the whole route still function, end to end

**And the rule that makes it work:** *"A blank memo, unchanged cursor, or identical
artifact hash should be a first-class outcome, not an incidental log event."*

**Two of these close holes already filed on this project.**

**The DEAD-MAN ALARM answers the hole Architecture found in the doorbell design** —
the watcher enforces the limits and detects stuck jobs, so its own death is the one
thing it cannot report. **A supervisor that must produce reconciliation evidence to be
considered alive is the answer to that, and nobody here had it.**

**The OUTCOME VERIFIER with a FRESHNESS rule is the answer to the watcher's silent
fifty-five seconds** — routing failed, recovery was attempted, nothing was logged, and
only the letter's continued presence would ever have shown it.

**It also states the postcondition in a form this project can use directly:** success
is *"a reply memo with matching correlation ID exists, parses, is newer than request
time, and contains the required result fields"* — not that the process returned zero.

---

## 3. THE TESTING MATRIX — THIS GOES INTO THE FIFTEEN-POINT ACCEPTANCE TEST

**Its standard: a safety control is credible only if it is tested AT THE ENFORCEMENT
POINT.** The assertions it names:

    attempts outside an allowed path fail BEFORE filesystem mutation
    a one-run approval is bound to EXACT action arguments, expires, cannot be
      replayed, and rejects changed arguments
    the master switch's ABSENT, CORRUPT and EXPIRED states all deny
    a budget limit is enforced BEFORE a billable or state-changing operation,
      not merely reported afterward
    a second agent, a direct shell invocation, malformed JSON, a SYMLINK or
      REPARSE-POINT PATH, and a race condition cannot bypass the gate
    every denial and approval creates a complete local audit event
    fault injection proves that a crashed approval service, a missing policy
      file, a CLOCK ANOMALY or a malformed request fails closed

**THE SYMLINK LINE IS A GAP IN WHAT WE PROVED TONIGHT AND IT SHOULD BE TREATED AS A
FINDING.** The containment probe demonstrated that a desk cannot write to a path
outside its allowance. **It did not test a junction or reparse point INSIDE the
allowed directory pointing somewhere else.** On Windows that is a real construct, and
a path check that resolves nothing would pass it while the write lands outside.
**Unproven, not disproven — and cheap to close.**

**The CORRUPT and EXPIRED switch states are also untested.** Tonight proved absent
denies and present allows. A switch file containing garbage has never been tried.

**And the CLOCK ANOMALY line lands on a defect this project hit twice tonight** — two
clocks a day apart breaking a supersede. It was treated as a naming problem and fixed
with a naming rule. **It is also a fault-injection case nobody has run.**

---

## 4. THE FINDING THAT SETTLES THE BOOT-COST QUESTION

**Asked independently where durable agent memory actually works, it answered: project
instruction files.**

> "This is the one mature answer: durable memory works when the record is
> human-readable, reviewable, versioned, and deliberately curated. Agent-generated
> memory without a review/update lifecycle tends toward stale, duplicated, or
> overbroad context."

**And: "No memory server has replaced these layers. The server can improve recall; it
cannot make recalled content current or authoritative."**

**This is the direct answer to the question of whether a knowledge graph or a vault
would cut the cost of starting a new chat. It would not.** A new session starts empty;
something must still read and supply the context. **What cuts that cost is a smaller,
sharper boot document — which this project already has for every desk and has not
optimised.**

**Its stable split of memory, which matches what is already built here:**

    RULES                  version-controlled, read-only to agents
    DECISIONS              a concise decisions log
    CURRENT STATE          task ledger and handoff memos
    DISCOVERABLE HISTORY   a local indexed corpus, if wanted
    EPHEMERAL TRACE        run logs, tool calls, raw transcripts

**Only the fourth line is missing here, and it is the optional one.**

---

## 5. THE PRIVACY DISTINCTION THAT SHARPENS OUR OWN BOUNDARY WORK

**It splits the question into three independently configurable paths:**

    INGESTION            parsing and OCR on disk
    EMBEDDING/INDEXING   local model, local index
    GENERATION           whether retrieved excerpts reach a cloud model

> "Local retrieval does not automatically mean the corpus never leaves the machine. If
> a remote coding model receives retrieved snippets in its context, those snippets
> leave through the model API. The retrieval layer is private; the prompting layer may
> not be."

**This corrects a simplification in this desk's own advice.** A "fully local" indexer
satisfies the first two and says nothing about the third. **For the export boundary
work it means the refusal rules belong at the generation boundary, not only at the
index.**

---

## 6. AND A FINDING THAT BEARS ON TONIGHT'S OPEN QUESTION

> "Prompt guardrails are not authorization. The model should never be the final
> authority on paths, money, external communication, or state changes; a deterministic
> wrapper and least-privilege OS credentials must independently enforce those
> decisions."

**Tonight's containment probe found that the refusal came from the approval layer —
nobody present to approve — and NOT from the path allow-list.** That is the model's
harness deciding, not a deterministic wrapper. **The allow-list remains unproven, and
this report says an unproven enforcement layer is exactly what should not be relied
on.**

**Least-privilege OS credentials are named as the independent enforcement this project
does not have.** A woken desk currently runs as the owner's own account.

---

## 7. THE TOOLS, AND WHAT THIS DESK WOULD ACTUALLY DO ABOUT THEM

**Nothing. Not yet, and possibly not at all.**

Most of what it named is small and young, and the report says so itself — it repeatedly
writes "check repository licence", meaning licences were not verified, and several
maturity claims are project-supplied rather than independently confirmed.

**The three worth a proper look later, in order:**

    ARTIFACT WATCHDOG    aimed at exactly our failure mode - verify the promised
                         output exists rather than that the process exited
    AGENTTRACE           local SQLite traces of tokens, tool calls and cost,
                         no account, no cloud
    LOCAL-AGENT-SENSES   local image/video/speech for a text-only agent, if the
                         video question ever becomes real

**And one flagged as marketing risk by the report itself: "Agentic OS" — breadth is
the warning.**

**The two closest to our own design — Cyclops and Agent Letterbox — are worth READING
and not adopting.** Their value is protocol design: immutable message IDs, explicit
acknowledgments, idempotent delivery, recipient-scoped inboxes, and a terminal state
distinct from "process exited." **We have three of those five.**

---

## 8. WHAT THIS DESK RECOMMENDS

**Take the ideas. Install nothing.**

    1  the LAYERED PROOF MODEL of section 2 goes into the brakes spec before
       Build starts step C. It is better than what is specified now and it
       closes the dead-man hole Architecture already found.

    2  the TESTING MATRIX of section 3 goes into the fifteen-point acceptance
       test. It is more complete than what we drafted.

    3  the SYMLINK / REPARSE-POINT gap is a FINDING against tonight's proved
       containment, and it is cheap to close.

**Nothing in this report changes the build order and nothing in it should delay the
brakes.**
