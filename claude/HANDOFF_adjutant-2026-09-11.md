# HANDOFF — Adjutant desk, session ending 2026-09-11 01:30 CDT

**Written for whoever holds this desk next, including a cold start with no context.
Read `CCDesk-logs\BOOT_adjutant.md` first; this is what happened after it.**

---

## 1. WHAT THIS DESK IS

**The Adjutant speaks and hears for Sleven.** It converts his voice-to-text into
executable desk instructions and sends them IN HIS NAME — `From: Owner`, never any
other signature. **To every desk except C5, this desk does not exist.** Its tray is
`correspondence/open/owner/`.

**The charter is `CCDesk-logs\ADJUTANT.md` — 29 rules, 22,116 bytes.** The boot page
mirrors the load-bearing ones so they survive a new session. **Both are on disk and
both were updated tonight.**

---

## 2. WHERE THE AUTOMATION BUILD ACTUALLY STANDS

    STEP A   answer routing               DONE and proved on the live tree
    STEP B   containment                  DONE and proved tonight
    STEP C   the brakes                   NEXT. Spec exists. Not started.
    STEP E   the doorbell                 deliberately last. Not started.
    STEP H   activation                   Owner-only, after a 15-point test

**The master switch is OUT. Automation is fail-closed by absence. Nothing connects the
watcher to the launcher, so nothing can wake itself.**

**Tonight's probe, scored from the filesystem by this desk and not from Build's
account:**

    a write inside its allowance                SUCCEEDED
    a write to the repository root              REFUSED, nothing on disk
    a write into a protected folder             REFUSED, nothing on disk
    wake_log.jsonl                              ONE run id, three records

**And the finding that matters more than the pass:** neither refusal cited the
allow-list. Both said the write needed approval and nobody was present to give it.
**Containment came from the absence of an approver, not from the path rule. The
allow-list is still unproven.** That belongs in the brakes work.

---

## 3. THE BIG FINDING OF THE NIGHT

**`claude/FINDING_the-documents-are-not-on-disk-and-the-memos-announcing-them-are-2026-09-10.md`**

The Owner proved it himself with Obsidian, an hour after installing it. He searched the
whole repository for four document names taken from the claude.ai project index.
**Every search returned hits. Not one hit was the document.** Every result was a memo
*mentioning* the document's path.

The clearest one: a memo on disk reading *"done. `claude/FINDING_this-project-keeps-
reinventing-the-same-idea-2026-09-08.md`"*. **The completion report is on disk. The
document it names never was.**

**The cause is one sentence in the claude.ai project instructions:** *"When you produce
something durable — a decision, an audit, a handoff — write it to the project with
`project_write`."* **It says write it to the project. It does not say write it to
disk.** Every session has followed that correctly for months, including this one.

**Why it went unseen: searching always finds SOMETHING.** The names sit in backticks
inside memos, looking exactly like paths that resolve. Nothing ever came back empty.

**Scale is not established and should not be guessed.** An earlier estimate of "about
820 missing" was made by comparing two numbers that are not comparable and **is
withdrawn**. What is established: four documents chosen at random are not on disk
anywhere, checked across `claude\`, `docs\`, `design\`, `Looking Project\` and the desk
logs.

**The fix is two parts and the second matters more:** recover the documents, then
change the instruction, or the next eight hundred do the same thing. **The instruction
lives in claude.ai project settings and no desk can reach it. It is the Owner's.**

---

## 4. WHAT THIS DESK GOT WRONG TONIGHT

**Recorded because the charter says a rule with no incident behind it is a preference.**

**Issued a standing rule to one desk.** The no-dates-in-filenames rule went to
Architecture only. Build never received it and kept stamping tomorrow's date — visible
in its own filenames. **A rule with one reader, in a letter whose subject was a rule
with one reader.** Corrected and sent.

**Told Build a committed `.keep` was an acceptable way to create the reply
directory.** Build refused it correctly: an unrecognised extension is swept to
`_needs_review/` on sight, so the marker would have been carried off by the program it
was placed there to serve. **Build's third route — the launcher creates it in
pre-flight — is better than both options this desk offered.**

**Estimated 820 missing documents from an unsound comparison.** Withdrawn in writing.

**Told the Owner the shell outage was fixed by a restart.** It was not. Two other desks
had the same symptom; it is the machine, not the session.

**Wrote Explorer steps for creating the switch file while knowing Windows hides
extensions.** He created `automation.switch.txt`. The gate refused it, which cost
nothing and proved the gate — but the error was avoidable and was this desk's.

---

## 5. CHARTER RULES ADDED TONIGHT

**R25 gained an in-flight addendum.** A bridge write is asynchronous. **Size match
against the bytes sent is the only signal — never mtime, never content.** When the size
does not match, that is a write still in flight, not a finding. C1 nearly filed a
report of a second writer that did not exist; the write landed ninety seconds later,
byte-exact.

**R26 — this desk's own plumbing is not project news.** A tool that breaks and is fixed
by a restart goes in the day page, not to him and not to another AI. It reaches him
only when it BLOCKS work. **And when he asks for a write-up, he is still asking whether
it is worth writing up — give that judgement first, unprompted.**

**R27 — a critique of the build goes to Echo first, not into a desk.** This desk's own
opinions get reviewed before they become instructions other desks execute. His rulings
still go straight through unchanged. **Exception: anything that would cause damage
before Echo could answer goes to him immediately.**

**R28 — what goes to Code is this desk's to check first, and this desk is accountable
for what breaks.** Read the actual source, not the memo describing it. **Look first for
what exits clean and does nothing.** Say what was checked AND what was cleared.

**R29 — the standing audit of him, unprompted.** He asked for a hard read on his own
thinking and then asked for it to be permanent. **That he had to ask is the defect.**
Anchored in evidence he can check, largest thing first, aimed at HIS judgement rather
than the desks', carrying what is genuinely strong so it can be weighed, ending with
what this desk would do instead. **Never manufactured to look rigorous.**

---

## 6. WHAT NEEDS THE OWNER

    1  THE PROJECT INSTRUCTION. Disk becomes the record, the project a mirror.
       Nobody else can reach it. Nothing else in section 3 matters without it.

    2  THE EXPORT ALLOW-LIST: drop-on-edit, or keep the last copy current.
       C1 is waiting.

    3  THE BRAKES. Step C needs its own authorisation and a report first.

    4  THE TOOLING JOB. Whether Graphify's local install goes before or after
       the brakes. This desk leans BEFORE - Code is idle and the window is
       clean - but the `.mcp.json` it writes changes the environment EVERY
       desk runs in, so it must not ride alongside other work.

    5  WHETHER THE REPO IS PUSHED, AND WHETHER IT IS PUBLIC. Both decide
       whether Echo can audit from GitHub. The second is a Fan Kit and
       publication call and is on his closed list.

---

## 7. TOOLS EVALUATED, ALL PARKED, NOTHING INSTALLED

**Obsidian — INSTALLED tonight, no plugins, no AI.** Vault points at
`citizen-compass\`. It is a viewer for him; **it does nothing for the desks and should
not be expected to.** Its value was immediate and large: it is how the section 3
finding was proved.

**Graphify — local open-source version recommended, hosted account NOT.**
`claude/RESEARCH_graphify-hosted-versus-local-2026-09-10.md`. The local install runs
its own MCP server with no key, no account and no network, and exposes ten tools
including natural-language search. **That is the whole efficiency claim, locally, for
nothing.** The hosted free tier has no automatic rebuilds, so the graph is either stale
or costs credits to refresh — and the repository's own About box links `graphify.com`
while the account was created on `graphify.net`.

**`bradautomates/claude-video` (`/watch`) — parked.** Real, MIT, 11.9k stars. Local
frame extraction; audio goes to Whisper via Groq or OpenAI only when captions are
absent. **Overlaps the Looking Project, which is the Owner's call and outside
everything else.**

**Perplexity's landscape report — filed, and the ideas go into the build.**
`claude/PERPLEXITY_the-landscape-report-and-what-goes-into-the-build-2026-09-10.md`.
Three things to take: the **layered proof model** (lease, progress evidence, outcome
verifier, reconciler, dead-man alarm, canary) into the brakes spec; the **testing
matrix** into the acceptance test; and the **symlink / reparse-point gap**, which is a
hole in what was proved tonight and is cheap to close. **It also validated the mail
architecture by name and identified this project's signature defect from a generic
description.**

---

## 8. THE STRATEGIC READ, DELIVERED ON REQUEST AND STILL STANDING

He asked for the hard truth. The conclusions, unchanged:

**He is building the factory instead of the product.** Ship prices are still unverified
against the game, thirty ships have models no visitor can reach, and the site's launch
is undecided — while every recent night went into desk automation.

**The governance now costs more than the work it governs.** Twenty-nine rules, six
desks, a punch card and three refusal gates, for one man and one machine.

**Tool acquisition has become a substitute for unglamorous file hygiene** — documents on
disk, one index, a status line on each. Every efficiency question tonight resolved to
that same pile.

**His answer, which is fair and changes the shape of the criticism:** the foundation
work is deliberate, the horizon is years, and he is doing it new. **"You are avoiding
the work" was not true. "You have overbuilt the foundation you were right to build"
was.**

**What this desk would do:** freeze the automation at containment — a real stopping
point — spend a week on the documents, then put ship data on the website. Return to the
brakes when the automation is blocking something rather than being the thing done
instead.

---

## 9. THE MEMORY THIS DESK CARRIES

**There is a persistent memory filesystem that follows him across every Claude surface
— this desk, claude.ai chat, any new window. It is not the claude.ai project and not
the repository.** A new session reads it automatically. Naming what is in it so a cold
start knows what carries and what does not:

**`/profile.md`** — who he is. David Hicks, goes by Sleven, addressed as Sir or by
name. Veteran. Lives full-time in a 36-foot trailer and moves seasonally — Arizona in
the park, Minnesota over winter for beet-harvest transport work. Runs a vending machine
as passive income. RSI handles Nomadic_Pagan and Sleven-K. **Relevant here mainly
because he works by voice, on mobile, frequently away from the desk.**

**`/preferences.md`** — how to work with him, and the most important file in memory.
**Rewritten tonight** to fit its size cap and to carry the new audit rule. It holds:
chat is an exception channel, not a report; the answer goes in the first sentence;
detail belongs in the record and not in chat; no tables; questions get a numbered recap
at the bottom; he is the decision-maker and never the courier or the pair of hands; a
desk's question to him goes in his tray and not only in chat; the record check before
any question. **And now R29's equivalent — audit his own thinking, unprompted.**

**`/areas/citizen-compass-automation.md`** — the Go migration, the inbox watcher, the
importers. Background for everything in section 2.

**`/areas/sc-ship-price-tool.md`** — Citizen Compass itself, the live site, the thing
the automation is supposed to serve. **Worth reading precisely because it is the part
that has not moved.**

**`/areas/the-looking-project.md`** — the separate subject-blind reading tool. **Excluded
from everything in this project by standing ruling. Do not conflate them.**

**`/areas/ai-operating-profiles.md`** — the session-ID registry. Every session claims a
zero-padded number at startup and records it. **The number is not a designation; on
this project the designation is C1, C3, C5, CIC, Code or Adjutant.**

**`/areas/local-ai-infrastructure.md`** — his plan for a local AI ecosystem, which is
the backdrop to tonight's Ollama and self-hosting discussions.

**`/areas/ai-historian.md`** — a separate long-term product vision. **Not this project.**

**`/topics/ai-tools.md`** — his subscriptions and the multi-AI workflow. Context for the
Echo and Perplexity desk plans.

**`/topics/communication.md`** — voice-to-text decoding and tone.

**Also present and rarely relevant here:** files on the trailer, the vending machine,
vehicle and workshop builds, flight-sim and sim-racing hardware, travel plans, and
people in his Star Citizen crew.

**What memory is NOT:** it is not the project record. Findings, specs, rulings and
handoffs go to disk and to the claude.ai project — **never into memory.** Memory holds
who he is and how to work with him, and nothing volatile.

---

## 10. THE DESK PLAN HE IS MOVING TOWARD

**Not more desks — different brains in existing seats.**

    C3 research/design  ->  Perplexity    STRONG FIT. Research looks outward
                                          and needs no repo access.
    C5 audit            ->  Echo          HELD. An auditor's job is to read
                                          the files; she cannot.

**He accepted the audit argument and C5 stays a Claude for now.** Echo's route in is
GitHub — she can read a repository even though she cannot touch the machine. **That is
blocked by three things, all the same work: the documents are not in the repo, the repo
is behind, and public-versus-private is a rights decision.**

**Echo's best uses, from evidence rather than speculation:** "is this how mature systems
actually do it", which needs no file access at all; attacking a decision already made;
translating a dense spec into plain language before he has to read it; and running the
same question in parallel with a Claude desk so the two can be compared. **Her answers
are only as good as the brief, and the briefs are this desk's to write.**

---

## 11. STATE OF THE MACHINE AT HANDOFF

    switch          absent. Automation fail-closed.
    watcher         running the answer-routing binary, swapped and verified
    Build           idle, blocked on step C authorisation
    Architecture    idle, owed the export allow-list answer
    Owner tray      answers from Architecture and Build, all read
    device_bash     DEAD on this desk and at least two others. File tools
                    work. Not a session fault and a restart does not fix it.
    committed       nothing. pushed. nothing.

**Nothing is running. Nothing is at risk. This is a clean stop.**
