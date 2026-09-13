# Memo

To:      Architecture
From:    Owner
Date:    2026-09-11
Subject: Rulings. The committed Git repository is the record, automation is frozen, the Q54 footer, process cuts, and the export drops on change.
Status:  Closed

## MY WORDS, EXACTLY

> "Make the committed Git repository the official record and treat the cloud as a
> copy. Freeze automation because it is safely off and disconnected. Before Q54
> deploys, replace the false footer with honest wording; unfinished features are
> acceptable on the test site, false claims are not. Reduce duplicate reports,
> unnecessary desk reviews and routine owner approvals. For the Perplexity export,
> remove any document as soon as its approved version changes, then return it only
> after reapproval."

Those are rulings. Everything below is how they land on your side. Echo's answers,
which these follow, are on disk at
`claude/ECHO_the-five-answers-and-two-corrections-2026-09-11.md`.

## 1. THE RECORD

**The committed Git repository is the official record. The claude.ai project is a
copy.** Not the local folder: what is committed.

Specify it. Do not build it. What I want answered:

- **The flow, one way:** work finished on disk, then committed, then copied to the
  project. The copy never becomes something anybody edits as the authority. Each copy
  says which commit or content hash it came from.
- **Getting the missing documents back.** Documents that exist only in the project
  have to come into the repository. Say how we find them all and how we prove none
  were missed, because four random ones were missing and nobody knows the real count.
- **The check.** A memo that names a document path should prove that the document
  exists, is tracked by Git, belongs to the authoritative set, and matches the
  recorded revision when one is named. "The file exists" alone is not enough.
- **Hard rule 2 collides with this, so say how.** Right now every commit needs my
  go-ahead for that change. If the record is what is committed, I become the
  bottleneck on every document, which is the routine approval I just told you to cut.
  Propose the narrowest standing commit permission that makes the record work, and
  what stays behind my word. I will rule on it. **Pushing is a separate question and
  is not part of this.**

The project instruction that tells sessions to save to the cloud is mine to change,
not yours.

## 2. THE FREEZE

The wake system stops at containment. No brakes, no doorbell, no activation, and
nothing queued ahead of the front page to extend it. Record the freeze in
`docs/CURRENT-STATE.md` and `NEXT.md`. Build writes one archive entry after Q54 with
the running watcher, the switch state, the finished steps, and what has to be
rechecked before anyone restarts the work.

**How I read it:** the freeze covers the wake system. Defects in the mail service that
is already running are not frozen, and they stay on the queue behind the front page.

## 3. THE Q54 FOOTER

Build has its own letter telling it to hold the upload. You need to know the rule: **the
test site may be unfinished, but it may not say anything false.** That standard applies
to every page, not just this sentence.

## 4. CUT THE PROCESS

Reduce duplicate reports, desk reviews that add no new evidence, and owner approvals
for routine reversible work. **Bring me a short list of specific cuts, each one named,
for a yes or no.** Say for each what it removes and what it risks.

Echo's list of what must not be cut is in her document: database destruction,
spending, publication, deployment, security boundaries, and final independent
verification. I have not ruled on that list. Treat it as the starting point.

## 5. THE EXPORT

**A document drops out the moment its approved version changes, and comes back only
after I approve it again.** That is your recommendation, and it is now the ruling.
Amend `claude/DESIGN_the-curated-export-2026-09-11.md`. Nothing gets built.

## 6. A CORRECTION FOR THE RECORD

Wherever the record says the path allowance is unproven, correct it. It selected the
one write that went through without a prompt, and no-prompt mode denied the writes it
did not match. **Containment, the two together, passed.** What is still untested is the
allowance refusing a write by itself with an approver present, and no wake runs with an
approver.

---

ANSWERS:

**Architecture, 2026-09-11. All six taken. Four are done; two are in your tray for a
yes or no.**

    1  the record        SPECIFIED  claude/SPEC_the-record-is-what-is-committed-2026-09-11.md
    2  the freeze        RECORDED   docs/CURRENT-STATE.md and NEXT.md; Build has the
                                    archive-entry letter
    3  the Q54 footer    RECORDED   the standard, written as a rule over every page
    4  the cuts          IN YOUR TRAY  five named, each for a yes or no
    5  the export        AMENDED    section 5F, drop-on-change
    6  the correction    DONE       and it went further than you asked

---

## 6 FIRST, BECAUSE I CHECKED IT RATHER THAN TRANSCRIBING IT

**You are right and Echo is right, and the evidence is stronger than either of you
put it.** I read `logs/wake_payload_probe_20260910-221939.json` rather than taking
the correction on its face.

    permission_denials names BOTH refused calls as tool_name "Write"
    the write that SUCCEEDED was also a "Write" — to inbox/_replies/_probe.md —
    and it is not in that list

**The only thing separating them is the path.** Without the allowance, the
in-allowance write would have hit the same approval wall as the other two and would
be sitting in the denial list with them. **The allowance did the selecting. The two
together contained. Your sentence is exactly right.**

**Your limit is exactly right too and I have written it in your words:** what is
still untested is the allowance refusing a write by itself with an approver present,
and no wake runs with an approver.

### WHY THE RECORD SAID OTHERWISE, BECAUSE THE SHAPE MATTERS MORE THAN THE ERROR

**Two different runs were collapsed into one claim.** The 16:43 audit wake genuinely
carried no `--tools` and no `--allowedTools` — that is where "no write-path
restriction of any kind" came from, and it is true of that run. **The containment
probe eight hours later is a different command with the allowance present.** I
generalised the first over the second without re-reading the log.

**And there is a fact underneath it that nobody had named, which the containment
design depends on:** the allowance was `Edit(inbox/_replies/**)` and it governed a
`Write` call. **An allow-list written in terms of `Edit(...)` is broader than it
reads**, so any containment argument that leans on the tool name rather than the path
is unsound. Measured, in the record, and in Build's letter.

## 1. THE RECORD — SPECIFIED, NOT BUILT

`claude/SPEC_the-record-is-what-is-committed-2026-09-11.md`. Your four questions in
order: the one-way flow with a commit and blob sha on every mirrored copy; recovery by
CONTENT hash rather than path, with the completeness proof being arithmetic — every
project document lands in exactly one of four buckets and they sum to the project's
own count; the four-assertion check, each provable by mutation; and the narrowest
standing commit permission.

**Two things in it you should know without opening it.**

**The one-way rule cannot be enforced.** There is no way to make the project
read-only — any session can `project_write` anything, which is how this happened. So
it is a detector instead: re-hash a mirrored document and compare it to the blob sha
in its own header. Exact, no judgement, and it flags rather than fixes.

**"The authoritative set" needs a positive definition and `claude/` proves why
today.** That folder currently holds `Untitled.md` at 0 bytes, `2026-09-10.md` at 0
bytes, two empty `.canvas` files and an `.obsidian` directory. **An empty
`Untitled.md` passes "exists" and would pass "tracked".** The set is defined by what a
document IS, not by which folder it sits in.

**And §4 carries a problem with your own instruction, which is question 3 in the cuts
letter.** The narrowest permission does not make this work on its own: Architecture is
barred from index-touching git on the mount after the eight-day `.git/index.lock` jam,
and `device_bash` is down on every Cowork desk since the 2026-09-08 Windows update.
**I can write a document and I physically cannot commit it, whatever you grant.**
This very spec went to disk and to the project without a commit, for that exact
reason — the first document the new rule applies to could not follow it.

## 2. THE FREEZE — RECORDED IN BOTH FILES

`docs/CURRENT-STATE.md` and `NEXT.md`, with the frozen state read from
`logs/wake_log.jsonl` rather than from a memo. **Your reading is the one I wrote: the
freeze covers the wake system, and defects in the running mail service are repairs
rather than extensions and stay on the queue behind the front page.**

**Build has the archive-entry letter with the recheck list, and item 1 on it is a
correction to my own spec.** `MAX_BUDGET_USD = 2.00` was set on my claim of "about ten
times the worst honest run". **The 26-second containment probe alone estimates 0.527 —
the wall is under four times one probe.** The margin claim was wrong. The figure may
still be right. It is not adjusted now; it goes on the restart list.

## 3. THE Q54 FOOTER — WRITTEN AS A RULE, NOT A FIX

**"The test site may be unfinished, but it may not say anything false,"** over every
page, in the state document. The reason it is a rule and not a footer edit is the one
Echo gave: a reviewer who reads a false verification claim assumes the missing
information exists somewhere they cannot see, which corrupts the review rather than
just the page.

## 4. THE CUTS — FIVE, IN YOUR TRAY

The desk log, status-only letters to your tray, second review of a reversible change
that already has a proven control, routine commit approval for documents, and design
review of a spec that is about to be built. **Each with what it removes and what it
risks, and I have not pretended any of them is free** — cutting the desk log in
particular removes the one artifact whose purpose is noticing a pattern across jobs,
and three of this week's findings came out of it.

**I did not treat Echo's keep-list as ruled, since you said you have not ruled it.**

**And the letter says something you did not ask me to say, in section 6.** Your two
rulings today pull against each other: making the record what is committed ADDS a step
to every document, on the same desks, on the same day you told me to cut process.
**The five cuts do not pay for it.** I am not arguing against the record ruling — the
drift is real and four random documents were genuinely absent — but the honest
accounting is that today is a net increase in overhead, and you should expect the
queue to move slower rather than faster until the commit-and-mirror step is one
scripted act instead of three deliberate ones.

## 5. THE EXPORT — SECTION 5F

Drop-on-change written in as the ruling, with your words quoted. **Section 5 of that
document, "the one thing to decide before any of it", is now marked superseded** — it
was answered this morning and was still sitting there asking.

**One thing I want on the record about my own framing:** I offered you stay-current as
a preference call about tolerable lag. **That was too generous to it.** Approval
attaches to a hash, so the moment content changes the approved thing no longer exists
— what sits in the export is a different document wearing an approval it was never
given. A report afterwards is not a control over a leak; it is a record of one. **You
ruled it correctly and I framed the choice wrongly.**

---

**Nothing built. Nothing committed — I cannot. No permission assumed, no folder, no
group, no ACL, nothing deployed, and the wake system is frozen where you left it.**

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.** The two open questions live in the cuts letter.
