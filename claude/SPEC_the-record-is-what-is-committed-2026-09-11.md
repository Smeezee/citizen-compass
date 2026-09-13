# SPEC — THE RECORD IS WHAT IS COMMITTED

**Specification only. Nothing built, nothing committed, no permission taken.**

**His ruling, 2026-09-11:**

> *"Make the committed Git repository the official record and treat the cloud as a
> copy."*

**Not the local folder. What is committed.** That distinction is the whole spec: an
uncommitted file on disk is work in progress, and a mirrored file in the project is a
view. **Only the committed object is the record.**

This answers the four things he asked for and nothing else. **Section 4 contains a
problem with his own instruction that has to be settled before any of it runs.**

---

## 1. THE FLOW, AND IT IS ONE WAY

    work finished on disk  ->  committed to Git  ->  mirrored into the project

**Each arrow is a different kind of act and only the first two are reversible by the
desk that did them.**

**Nothing is mirrored that is not committed.** A desk that has written a document and
not committed it has not produced a record; it has produced a draft. Mirroring a draft
is what created the present mess in the opposite direction.

### EVERY MIRRORED COPY CARRIES WHERE IT CAME FROM

The first lines of every mirrored document, above its own title:

    <!-- MIRROR. Source of record: <repo-relative path>
         commit <40-char sha>   blob <40-char sha>
         mirrored <date> by <desk> -->

**Two hashes, because they answer different questions.** The commit says *when this
version of the world was recorded*. The blob says *what this file's bytes were* — and
it does not move when an unrelated file changes, which is what makes it the one a
check compares against. `git hash-object <path>` produces it; `git rev-parse HEAD`
produces the other.

**A mirrored document with no provenance header is not a mirror. It is an orphan**,
and the recovery in section 2 treats it as one.

### THE ONE-WAY RULE CANNOT BE ENFORCED, SO IT IS DETECTED

**There is no way to make the claude.ai project read-only.** Any Cowork session can
call `project_write` on any path, and that is precisely how every document in section
2 came to exist only there. **A rule that depends on every future desk behaving is
not a control** — hard rule 12.

**So the control is a detector, and it is exact:** re-hash a mirrored document's body
and compare it to the `blob` in its own provenance header. **They disagree only if
somebody edited the cloud copy.** No judgement, no similarity, no tolerance — the
bytes match or they do not.

**It runs over the whole mirror, reports every disagreement, and fixes nothing.**
An auditor flags; it never auto-fixes. A cloud edit that a detector silently
overwrote would destroy work somebody meant to do.

### WHAT THE MIRROR IS FOR, SO NOBODY WIDENS IT

**A session with the project and no repository access can still read the state.** That
is the entire purpose. It is not a backup — the repository is the backup — and it is
not a place to work.

### 1A. THE MIRROR IS A NAMED SMALL SET — HIS RULING 24, 2026-09-12

> *"Reduce the external AI-project mirror to only the documents outside sessions
> genuinely need. The local repository remains the complete official record. Avoid
> unnecessary duplicate documents and stale copies."*

**The qualifying test follows from the purpose above and nothing else: a document is
mirrored ONLY if a session that cannot reach the repository would be unable to orient
without it.**

    docs/CURRENT-STATE.md          the state. The one document that answers
                                   "what is true now".
    claude/PROMPT_boot-a-new-*.md  one per desk. A cold session's own instructions.
    NEXT.md                        the queue, so a cold read knows what is in flight
                                   and does not propose work already ordered.

**Nothing else.** Findings, specs, designs, rulings, audits, echoes, results and
correspondence stay in the repository. **A session that cannot reach them also cannot
act on them**, and a copy it can read but not act on is the duplicate his ruling names.

**THE ORDER IS NOT NEGOTIABLE AND IT IS THE WHOLE RISK IN THIS RULING: RECOVER FIRST,
SHRINK SECOND.** Section 2's audit runs to completion and every project-only document is
pulled into the repository **before one document is removed from the mirror.** Shrinking
first would delete the only copy of documents nobody has counted yet — **the 2026-09-10
finding established that such documents exist and that their number is unknown.**

**Removing a document from the mirror is a DELETION and rule 1 governs it.** Nothing is
deleted until its repository copy has been read back and its content hash matched.

---

## 2. GETTING THE MISSING DOCUMENTS BACK, AND PROVING NONE WERE MISSED

**The scale is not known and must not be estimated.** The finding of 2026-09-10 put
the project at ~850 documents and `claude/` on disk at 26, then withdrew the
subtraction as unfounded — the project's paths are its own labels, and some project
documents correspond to files living elsewhere on disk under different names.
**Four chosen at random were genuinely absent. That is all that is established.**

### MATCH ON CONTENT, NOT ON PATH

**Path matching is what makes this look bigger or smaller than it is**, in both
directions: a document mirrored under a tidied-up name reads as missing, and a
disk file that was renamed reads as an orphan.

    for every project document   normalise, hash the body
    for every tracked .md        normalise, hash the body
    match on the hash

**Normalisation is narrow and stated, or it becomes fuzzy matching** — hard rule 17.
Strip the provenance header if present; strip a trailing newline; nothing else. **No
case folding, no whitespace collapsing, no heading extraction.** A document that
differs by one character is a different document and must be reported as one, not
quietly matched.

### THE BUCKETS, AND THE ARITHMETIC IS THE PROOF

    IN BOTH          content hash matches a tracked file        -> nothing to do
    PROJECT-ONLY     no content match anywhere in the repo      -> RECOVER
    DISK-ONLY        tracked, never mirrored                    -> mirror, or
                                                                   deliberately not
    EDITED-IN-CLOUD  has a provenance header whose blob sha
                     does not match its own body                -> he decides

**Every project document lands in exactly one bucket, and the four buckets sum to the
project's own count.** *That* is the proof that none were missed — not "we looked",
not "the search returned nothing". **A document that cannot be bucketed is a fifth
outcome and it stops the audit**, because an unbucketable document is exactly the case
this whole exercise exists to stop being invisible.

**AMENDED 2026-09-12 BY RULING 24. THE ARITHMETIC ABOVE IS THE RECOVERY AUDIT'S AND IT
STANDS EXACTLY AS WRITTEN — it is a one-time reconciliation of what exists where, and
shrinking the mirror does not change what has to be recovered.**

**What changes is the STEADY STATE afterwards, and it needs its own check because the
buckets stop meaning what they meant.** Under a full mirror, DISK-ONLY was a gap to
close. **Under a named small mirror, DISK-ONLY is the normal and correct condition of
almost every document**, so the old check would report the entire repository as a defect.

    the recovery audit, once     four buckets, summing to the project count.
                                 Proves nothing was missed. Unchanged.

    the steady-state check       every document in the mirror SET is present and
                                 matches its source hash; and NOTHING outside the
                                 set is in the mirror. Two assertions, both able
                                 to fail, and neither counts the repository.

**The second check is what stops the mirror creeping back.** Without it, the next
session writes one more document to the project because that is where it was reading,
and in four months the set is eight hundred again.

**The count is reported before any recovery runs**, so the size of the job is a
measured number rather than a discovery partway through.

### WHAT RECOVERY ACTUALLY IS

**Read the project copy, write it to its repo path, commit it.** Nothing is lost and
nothing is at risk — every one of these documents still exists in the project, so a
botched recovery is repeatable.

**The repo path is derived, never invented:** the project's own path, minus any
leading label that is not a real directory. Where that produces a path that already
exists with different content, **the recovery stops on that document and reports it**
rather than choosing (hard rule 19).

### THE SECOND HALF MATTERS MORE AND IT IS NOT OURS

**The project instruction still says to write durable documents to the project.**
Until it says disk-first, the next several hundred documents do the same thing.

**That instruction lives in the claude.ai project settings and no desk can reach it.
He has said it is his to change.** Recovering without changing it is the version of
this job that gets done twice.

---

## 3. THE CHECK — FOUR ASSERTIONS, AND IT MUST BE ABLE TO FAIL ON EACH

**His words: "the file exists" alone is not enough.** A memo that names a document
path asserts four things and the check tests all four separately, reporting WHICH
failed:

    1  EXISTS        the path resolves to a file on disk
    2  TRACKED       git knows it: `git ls-files --error-unmatch <path>`
    3  AUTHORITATIVE it is in the document set defined below
    4  CURRENT       when the memo names a revision, the file's blob sha matches it

**Assertion 4 only fires when a revision was named.** A memo that names no revision is
not wrong; it is less specific, and the check says so rather than passing silently.

### THE AUTHORITATIVE SET NEEDS A DEFINITION, AND HERE IS WHY

**A folder list is not good enough, and `claude/` proves it today.** That folder
currently holds, alongside thirty-eight real documents:

    Untitled.md        0 bytes        2026-09-10.md     0 bytes
    Untitled.canvas    2 bytes        Untitled.base    39 bytes
    Untitled 1.canvas  Untitled 2.canvas   Untitled/   .obsidian/

**An empty `Untitled.md` inside `claude/` passes "exists" and would pass "tracked".**
Scratch left by a tool an hour old is indistinguishable from a document if the set is
defined by where a file sits.

**So the set is defined positively:**

    a tracked file, extension .md, non-empty, whose first non-blank line is an
    ATX heading, under one of:  docs/  claude/  design/  correspondence/
    plus the named root files:  CLAUDE.md  NEXT.md  LIVE.md  OWNERS.md  RECOVERY.md

**Excluded and stated so nobody has to guess:** `_work/`, `logs/`, `_to_delete/`,
anything untracked, and anything that is not `.md`.

**The Obsidian scratch in `claude/` is not a defect to fix in this spec** — it is
evidence that the definition has to be positive, and it is named here so the check is
written against a real case rather than a clean one.

### AND THE CHECK MUST BE PROVEN ABLE TO FAIL

Four mutations, one per assertion, each shown to go red: a path that does not exist;
a real file that is untracked; a real tracked file outside the set; a real tracked
in-set file with a deliberately wrong revision. **A check that has only ever been seen
green is not a check** — hard rule 12.

---

## 4. HARD RULE 2, AND THE COLLISION IS WORSE THAN HE DESCRIBED

**His instruction:** propose the narrowest standing commit permission that makes the
record work, and say what stays behind his word. **Pushing is separate and is not part
of this.**

**Before the proposal, the part he has not been told:** the narrowest permission does
not by itself make this work, because **the desk that writes the documents cannot run
git at all today.**

    hard rule 2        no commit without his go-ahead, never `git add -A`
    standing rule      Architecture runs no index-touching git command on the mount
    the reason         `.git/index.lock` from a dead process jammed every commit for
                       EIGHT DAYS; three sessions read the jam as rule-2 discipline
    today              device_bash is down on every Cowork desk — a Windows update
                       released 2026-09-08 stops the workspace mounting the folders

**So C1 can write a document and cannot commit it, whatever permission he grants.**
Granting the permission without settling who runs the command produces a record that
nobody can add to. **That is the thing to decide, and it is a question, not a
recommendation this desk should make alone** — it is in his tray.

### THE NARROWEST PERMISSION, PROPOSED

**A standing permission to commit DOCUMENTS ONLY**, defined as the authoritative set in
section 3, with every one of these attached:

    explicit file list on every commit; `git add -A` never, under any circumstance
    one work item per commit, named in the message
    no non-document path in the same commit, ever
    no push, no force, no rebase, no merge, no tag, no branch operation,
      no history rewriting of any kind
    no delete and no rename of an existing document — rule 1, and a rename is a
      delete to git

**What it does NOT cover, and these stay behind his word exactly as now:** code, data,
build artifacts, anything under `testing/` `data-layer/` `checks/` `tools/`
`watcher-go/`, **`CLAUDE.md` and `OWNERS.md` — those are rules and ownership, not
documents, and they are text only by coincidence** — and every push.

### AND IT IS A CHECK, NOT A PROMISE

**"Documents only" enforced by intention is the same defect as the one-way rule in
section 1.** A pre-commit hook refuses a commit containing any path outside the
authoritative set, and it is proven by mutation before the permission is used once:
stage a `.py` file alongside a document, attempt the commit, watch it refuse.

**If the hook cannot be made to refuse, the permission should not be granted**, because
then the narrowness is a description of good behaviour rather than a boundary.

### WHAT HE GETS BACK FOR GRANTING IT

**The routine approval disappears and the irreversible one does not.** A document
commit is reversible, local, and touches nothing a visitor can see. **The
irreversible act in this area is the push, and he has already separated it.**

---

## 5. WHAT THIS SPEC DOES NOT DO

**Nothing is built.** No recovery has run, no count has been taken, no hook exists, no
commit has been made and no permission has been assumed.

**And the ordering is his.** This sits behind the front page like everything else; the
freeze does not cover it because it is not wake work, but nothing here is urgent enough
to go ahead of Q54.

**Three things are his alone and are in his tray:** the project instruction, the
standing commit permission, and who runs the git command while Architecture cannot.

*C1, 2026-09-11. Specification only.*
