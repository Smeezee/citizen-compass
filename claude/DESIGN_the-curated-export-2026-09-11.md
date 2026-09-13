# DESIGN — THE CURATED EXPORT. Design only. NOTHING AUTHORISED.

    from    C1, architecture
    date    2026-09-11
    ruled   Sleven: the sandbox account gets no access to the live tree, ever.
            Not read, not traverse. A curated one-way export folder instead.
            C:\Users\Public is NOT to be used.
    reads   Build's ACL audit, docs/handoff_archive/20260910_192450_update-
            the-perplexity-acl-audit-in-full-rule-13-completion-record.md
    revised 2026-09-11 AGAIN, on his finding that both boundary refusals are
            deny-lists wearing a different hat. CONTENT REFUSAL IS WITHDRAWN AS
            THE BOUNDARY (5D). The boundary is an allow-list he maintains,
            outside the repository (5E). The in-document marker is DROPPED.
    revised 2026-09-11 on his ruling: the purpose is settled (5A),
            correspondence is EXCLUDED and the reason is form rather than
            safety (5B), and the danger he named is already inside the scope he
            approved (5C) - which makes two boundary refusals necessary
            regardless.
    order   DESIGN ONLY. No permission on the machine is changed by this
            document and no command in it has been run. The ACL change is his,
            hard rule 6.

---

## 0. HIS RULING IS RIGHT AND BUILD'S OWN AUDIT PROVES IT

Build's §8 recommended the export folder and named `C:\Users\Public\cc-share\`.

**Build's own §2, six pages earlier, records why that location is wrong:**

> `C:\Users` — `Everyone:(RX)` and `BUILTIN\Users:(RX)`, plus inherit-only
> `(OI)(CI)(IO)(GR,GE)` for both.

**A folder created under `C:\Users\Public` inherits world-readable.** The export would
be readable by every account on the machine, not only the sandbox. **Right shape,
wrong location, and the evidence against it was in the same document.** Sent to Build.

---

## 1. WHAT CROSSES — SUPERSEDED BY 5E AND 5F. READ THOSE FIRST.

**THE MARKER DESCRIBED BELOW IS WITHDRAWN.** He found that the author is not reliably
the person who knows — four of his own examples are four authors who did not — and the
boundary is now an allow-list he maintains outside the repository. **Section 5E is the
mechanism. This section is kept because the reasoning in it is still why an
exact-filename list rots, and because the SOURCE SCOPE and EXTENSION gates below
survive unchanged.**

**Superseded text follows.**

**A marker inside each document. Opt-in. Absence excludes.**

    a line in the document itself, e.g.   export: sandbox
    no marker            ->  not exported
    marker removed       ->  removed from the export on the next run

**Why not an exact-filename list, since he offered it:** a filename allow-list is also
fail-closed against leaks — a new secret file is not on it, so it is not copied. **Its
problem is different: it rots by OMISSION.** A document gets renamed and silently stops
crossing; a useful new document never gets added because nobody remembered the list.
**And this project has a standing finding about typed lists** — the desk list was typed
in three places and drifted twice in two days.

**The marker puts the decision at the moment of writing, with the person who knows
whether the thing is sensitive.**

**HOW IT ROTS, STATED HONESTLY:** somebody forgets to mark a document that should
cross, and it silently does not. **That rot is visible** — the export carries a
manifest, and the person who wanted the document notices it missing. **Rot a person
notices is not the dangerous kind. Rot that leaks is, and absence-excludes cannot leak
by forgetting.**

### THE MARKER IS NOT ENOUGH ON ITS OWN — TWO MORE GATES

**A marker lives inside a file a desk can edit.** Same shape as a switch a desk can
write. So the exporter refuses regardless of any marker:

    SOURCE SCOPE     only docs/ and claude/ are even considered. Nothing else in
                     the tree is read, marker or no marker.
    EXTENSION        .md only. NO executables, NO .json, NO .exe, NO scripts.
                     This is what kills the rule 7 problem Build raised: there
                     are no binaries in the export to execute.
    CONTENT REFUSAL  a file matching a credential shape is refused and REPORTED,
                     even when marked. Build's §5 names the families that exist
                     here; a secret in an unremarkable filename is the case its
                     audit could not cover, and this is the layer that does.

**Three gates, and a leak needs all three to fail.**

**AMENDED 2026-09-11: the first gate is now 5E's allow-list rather than a marker. The
SOURCE SCOPE and EXTENSION gates stand exactly as written** — markdown only, `docs/`
and `claude/` only, which is what keeps binaries out of the export by construction.
**The CONTENT REFUSAL gate is demoted to a report-only tripwire by 5D.**

---

## 2. ONE-WAY AND CURRENT — REGENERATE WHOLE, NEVER INCREMENTAL

**One-way is easy. One-way and current is where this goes wrong, and he is right about
that.**

    1  derive the set
    2  build a COMPLETE new export beside the live one
    3  write the manifest
    4  swap: move the old one aside with a timestamp, move the new one in

**Never incremental, and that is the whole design.** An incremental copy cannot remove
a document dropped from the allow-list, or one whose content changed since he approved
it — the stale copy just sits there, exported, forever. **Regenerating whole is what
makes removal work.**

**Nothing is deleted.** Hard rule 1. The old export is moved aside with a timestamp,
and old ones are his to clear.

### THE MANIFEST, AND WHY IT IS THE IMPORTANT PART

    for each document   source path, size, mtime, content hash
    for the export      generated_at, count, and the version of the rules used

**Without it the sandbox cannot tell a current export from a three-week-old one**, and
neither can we.

**A FAILED EXPORT MUST NOT LEAVE THE OLD ONE LOOKING CURRENT.** If a run fails, it
writes a failure marker into the export folder saying so and when. **Silence is the one
outcome that is not allowed** — a stale export that looks fine is this project's
recurring defect wearing a new hat.

---

## 3. THE BOUNDARY

### LOCATION

    C:\cc-export\

**At the drive root, and INHERITANCE DISABLED with an explicit ACL.** Disabling
inheritance is what makes the location safe; the location then answers two other
questions:

**Not under `C:\Users\Public` —** section 0.

**Not under `C:\Users\david\` —** the sandbox account has no traverse there, and
Build's §3 could not confirm whether the bypass-traverse privilege makes that moot.
**A location at the drive root does not raise the question at all**, and `C:\` is
already traversable.

**Not inside the repository —** a woken desk's `--add-dir` scope is the repository
root, so an export folder inside it would be writable by automation. Same principle as
`C:\Users\david\.cc-control\` for the switch.

### WHO WRITES, WHO READS

    writes   the exporter, run as david. ONE writer.
    reads    a local group, read-only.
    nothing else has an entry.

**The exporter is not a woken desk's job.** It runs a script; a woken desk has no
shell.

### THE ACCOUNT NAME — HIS QUESTION, AND THIS IS THE DIRECT ANSWER

**Do not grant to `PerplexitySandbox`. Grant to a LOCAL GROUP.**

    create a local group, e.g. CC-Export-Readers
    put the sandbox account in the group
    grant the GROUP read on C:\cc-export\

**`PerplexitySandbox` is a vendor's internal detail and he is right that it is not a
stable identity.** If it is renamed, recreated with a new SID, or replaced by a second
account, **the group membership changes and the folder's ACL is never touched.**

**And it makes revocation one act:** empty the group. No ACL edit, no `icacls` on a
tree, no chance of removing the wrong entry.

**Build's audit already shows why this matters** — the request said
`perplexitysandbox` and the real principal is `PerplexitySandbox`. The name is already
not what somebody thought it was.

### WHAT THIS AVOIDS THAT THE LIVE-TREE GRANT DID NOT

    secrets              never copied in, rather than a deny list somebody maintains
    rule 7 / 29,000      no binaries in the export at all
    unaudited children   the folder is small, known, and regenerated whole
    a mistyped (M)       affects a copy, not the project
    rollback             empty the group

---

## 4. WHAT THIS DOES NOT AUTHORISE, AND WHAT IS STILL HIS

**Nothing here has been built, run, or changed.** No group exists. No folder exists.
No ACL has been touched.

    the group and the ACL     his. Hard rule 6, outside the repository.
    the exporter script       Build's, after he authorises the boundary.
    the marker on any document  whoever owns that document.

**Two things this desk deliberately did not write:** the exact `icacls` and
`net localgroup` commands, because they are a permissions change and writing them here
makes them look approved; and any command touching the live tree, because his ruling is
that the sandbox gets nothing there, ever.

---

## 5A. WHAT THE EXPORT IS FOR — RULED 2026-09-11

**Project understanding and outside review. NOT ship data.**

    CARRIES        curated Markdown: governance, architecture, decisions,
                   specifications, current state, verified reports
    NEVER CARRIES  raw ship data, databases, binaries, source collections,
                   credentials, secrets

**A BOUNDARY, NOT A NOTE — his words:** if Perplexity later needs ship data for a
specific review, **that is a separate, purpose-built export. This one is never
broadened to reach it.**

**The markdown-only rule in section 1 survives this purpose intact**, which the other
possible purpose would have destroyed on contact.

---

## 5B. CORRESPONDENCE IS EXCLUDED — AND THE REASON IS FORM, NOT ONLY SAFETY

**He said "relevant correspondence" and then found that it breaks his own answer.**
He was right to refuse to resolve it by picking. **The answer is to exclude it, and
the strongest reason is not the one he gave.**

### CORRESPONDENCE IS OUR WORKING, NOT OUR WORK

**A letter is addressed to somebody.** It assumes shared context, it references other
letters, it carries a desk's voice and its mistakes mid-correction. **A document in
`claude/` or `docs/` is written to be read cold by somebody who was not there.**

**The export's entire purpose is to be read cold by somebody who was not there.**
Correspondence is the wrong FORM for the job, independently of whether it is safe.

### AND THE WRITE-UP ALREADY EXISTS, SO THIS COSTS NOTHING RECURRING

His option was *"written up as its own marked document in `claude/`"*, and the cost of
that is new work forever that will lag.

**It does not need writing. `docs/CURRENT-STATE.md` is already the authoritative
snapshot and is already maintained as a standing obligation**, and every ruling,
spec, design and finding in `claude/` was already written to stand alone.

**So the rule is: if a conclusion matters enough to export, it already belongs in a
standing document.** If it is not there, **that is a gap in the record rather than a
gap in the export** — and the export becomes a test of whether the record can be read
by somebody who was not in the room.

**THE COST, STATED: a reviewer cannot see how a decision was reached, only what was
decided.** For outside review of the conclusions that is the right trade. **For a
review of our reasoning it would be the wrong one** — and if he ever wants that, it is
a separate purpose-built export under the rule in 5A, not a widening of this one.

---

## 5C. THE DANGER HE NAMED IS ALREADY INSIDE THE SCOPE HE APPROVED

**This is the finding, and it is the reason his question could not be answered as
asked.**

He listed what makes correspondence dangerous: machine paths, his account name, the
ACL findings, the master switch's exact path, the protected folders, and the Looking
Project. **Every one of those is also in `docs/` or `claude/`:**

    the switch's exact path           claude/SPEC_the-brakes-2026-09-10.md
    his account name and machine      this document, section 3
    the protected folders, and why    claude/SPEC_the-brakes-2026-09-10.md
    the Looking Project, by name      docs/ARCHITECTURE_DECISIONS.md section 4

**So excluding correspondence does not solve the leak. The marker is doing all the
work in both cases**, and the marker is per-document opt-in — a document naming the
switch path simply never gets marked. **That is the design working. But it means
"is correspondence safe" has the same answer as "is `claude/` safe": only as safe as
the marking.**

### 5D. WITHDRAWN 2026-09-11 — CONTENT REFUSAL CANNOT BE MADE TO FAIL CLOSED

**The two boundary refusals proposed above are withdrawn as the boundary. He found the
hole and it is not patchable.**

    the concept is not a string   "Looking Project" does not match the Lens, the
                                  Machine, the looking machine, or the shape
                                  reader - and those are that project's OWN words
                                  for itself, in this repository, today
    the path shape has a crack    brakes spec line 441 carries the full
                                  C:\Users\david\... form; line 447 carries
                                  `.cc-control\` with no drive letter at all

**AND THE REASON IT IS NOT PATCHABLE: A REFUSAL IS A DENY-LIST, AND A DENY-LIST
PERMITS EVERYTHING IT WAS NOT TAUGHT.** Adding aliases and path shapes makes the list
longer. It does not change the direction in which it fails.

**His requirement was a refusal that fails CLOSED on what it cannot recognise. No
content refusal over prose can do that** — failing closed at the content level would
mean allow-listing English.

**So the honest answer is the one he offered and I am taking it.**

---

## 5E. THE BOUNDARY IS AN ALLOW-LIST, IT IS HIS, AND IT LIVES OUTSIDE THE REPOSITORY

**Everything that fails closed in this project has the same shape: the safe state is
the default and a positive act is required to leave it.** The marker. The tray. The
switch. **The export gets the same shape and nothing else.**

    C:\Users\david\.cc-control\export.allow

**In the control folder, beside the switch, for the same reason** — no desk can write
it, so no desk can grant itself an export. **One line per document. His hand. Nothing
else crosses.**

### THE IN-DOCUMENT MARKER IS DROPPED

**Section 1's `export: sandbox` marker is withdrawn.** Two mechanisms for one decision
is the second-source-of-truth defect, and the marker was always the weaker one: **it
lives in a file a desk can edit, and the desk writing a spec that names the switch path
may reasonably believe the spec is exportable.**

**It was never true that the author is the person who knows.** His four examples are
four authors who did not.

### EACH ENTRY CARRIES THE HASH HE APPROVED

    <relative path>   <sha256 at the moment he approved it>

**A document whose content has changed since approval DROPS OUT of the export and the
manifest says it dropped and why.**

**THE COST, AND IT IS REAL: the export lags.** Every edit to an exported document needs
his word again before it crosses.

**Taken deliberately, on his own instruction** — *"I would rather have four documents I
trust than forty I have to think about."* **An export that is incomplete is visible and
safe. An export that is current and wrong is neither.**

### WHAT THE REFUSALS BECOME

**A tripwire, report-only, and NEVER the reason anything is safe.**

They still catch the careless case, which is the common one. **But a silent pass proves
nothing and must never be recorded as though it did** — hard rule 12, in the direction
that matters here. **The manifest says "the tripwire did not fire", never "the document
is clean."**

### THE TEST HE APPLIES WHEN HE ADDS A LINE

**Not this desk's call, so it is a test rather than a list: a document crosses only if
it would be safe printed and handed to a stranger.**

**What fails it, from his own four examples:** machine paths, his account name, the
Looking Project under any of its names, and **anything describing the machine's own
defences.**

### AND THE SELF-REFERENCE HE FOUND IS A RULE, NOT A SPECIAL CASE

**This document defines the boundary and names his account, the control folder and the
sandbox account. It must never cross the boundary it defines.**

**Generalised: nothing that describes the machine's defences is exportable.** The
brakes spec, the doorbell design, the ACL audit, and this file. **That is not an
exception list — it is the test above, applied honestly to the documents this desk
wrote itself.**

### WHY NOT HIS OTHER TWO OPTIONS

**(b) his personal mark on every letter** — safe, and it makes him the bottleneck on a
category that ran to nine letters in a day. **That is the exact thing the automation
programme exists to remove.** Keep it available for a deliberate one-off; never as the
default.

**(c) alone, with correspondence included** — a refusal list broad enough to make
correspondence safe would have to catch every sensitive CONCEPT, not every sensitive
shape, and a new concept is never on it. **It fails in the leak direction.** The two
refusals above are narrow because the scope is narrow; widening the scope is what
would make them a maintained list.

---

## 5F. DROP-ON-CHANGE IS RULED. THE LAST OPEN QUESTION IN THIS DOCUMENT IS CLOSED.

**His ruling, 2026-09-11, in his own words:**

> *"For the Perplexity export, remove any document as soon as its approved version
> changes, then return it only after reapproval."*

**So 5E stands exactly as written and the alternative is dead.** A document whose
content no longer hashes to the approved value is **removed from the export at the
moment the change is detected**, not reported and left in place. It returns only when
he approves the new content and its new hash goes into `export.allow` by his hand.

**The manifest states the drop and the reason.** A document that has dropped is
visibly absent with a stated cause — never quietly stale, and never silently current.

### WHY THE ALTERNATIVE WAS THE WRONG ONE, AND IT IS NOT THE LAG

This desk offered him stay-current-and-report as the option it would take his
preference on, because it read as a judgement about tolerable lag. **That framing was
too generous to it.**

**Approval attaches to a hash. The moment the content changes, the approved thing no
longer exists** — what is sitting in the export is a different document wearing an
approval it was never given. "Report afterward" means the unapproved content is
readable for however long it takes somebody to read the report, **and the first time
that window matters is the time it carries a path, a project name or a defence
detail.** A report after the fact is not a control over a leak; it is a record of one.

**That is the same shape as the tripwire above** — a thing that tells you afterwards is
never the reason something is safe.

### WHAT IT COSTS AND WHO PAYS IT

**The export lags, and he is the only one who can clear the lag.** Every edit to a
crossed document takes it out until he looks again.

**The cost falls in the right place.** It falls on the export being incomplete, which
is visible, rather than on the export being wrong, which is not. **And it falls on him
deliberately** — this is the one boundary he said should be his hand alone, and a
boundary that keeps itself current without him is not his hand.

---

## 5 (ORIGINAL). WHAT IS THE EXPORT FOR — SUPERSEDED BY 5A.

**Answered 2026-09-11 and kept only so the question is not asked a fourth time.**
Purpose is understanding and review, never ship data; source scope is `docs/` and
`claude/`, correspondence excluded; the `.md`-only rule in section 1 holds because the
answer was "the doctrine", not "the data". **Read 5A.**

*C1, 2026-09-11. Design only. 5F added on his ruling; nothing built, no folder, no
group, no permission changed, no export generated.*
