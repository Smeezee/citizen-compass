# Correspondence

**This is where the people working on Citizen Compass write to each other.**

If you have just been handed this project and are reading it cold: everything
here is memos. Somebody wrote to somebody, and it is either waiting for a reply
or it has had one.

    open/architecture   waiting on the architect
    open/build          waiting on the builder
    open/research       waiting on research
    open/audit          waiting on the audit desk
    open/design         waiting on design
    open/owner          waiting on the owner — his decisions only
    answered/           replied to, kept for the record

---

## The four desks

Memos are addressed to the **job**, never to a person or a codename, because
people change and jobs do not.

    Architecture   design, code review, the work queue, the decisions.
                   Owns what the thing should be.
    Build          executes on the machine. Builds, tests, sweeps, deploys.
                   Owns what actually runs.
    Research       gathers and verifies sources. Owns whether a claim is true.
    Audit          reads everything, writes nothing but memos. Reviews the
                   other desks' work and checks claims against the repository
                   rather than against prior documents. Owns no path, holds no
                   artifact, and does not carry work it has audited.
    Owner          Sleven. His alone: anything legal, anything public,
                   anything that cannot be undone.

    Design         works out what a thing should look like and how a person
                   uses it, before anyone builds it. Produces designs, options
                   and recommendations; does not execute and does not decide.

**SIX DESKS, AND THE LIST GREW TWICE IN ONE DAY.** Audit was stood up by Sleven that day and
operated for a day with no tray — it could send post and could not receive any.
His ruling, and it is the general rule: **a new desk gets a mailing path when it
is created, not when somebody asks whether it wants one.** A desk that cannot be
written to is half a desk.

**It happened again the same day.** Design was stood up and also had no tray, and
also had to write a memo about it — through somebody else's tray. **Twice is a
pattern, not bad luck.** The desk list is typed in three places (this file, the
router in `watcher-go`, and `checks/_verify_correspondence.py`) and a new desk
requires all three to be edited by somebody who remembers. **The fix is to derive
the list from the trays on disk rather than type it three times**, and it is on
the queue.

## How to send one

Write a plain markdown file and **drop it in `inbox/`**. That is the only way
in. Something is always watching that folder and it will file this for you.

    # Memo

    To:      Architecture
    From:    Build
    Date:    2026-08-30
    Subject: one line that says the thing
    Status:  Open

    Then write the memo. Say what you need and what a good answer looks like.
    Show your evidence. If you measured something, give the number.

**`To:`, `From:` and `Subject:` are all required.** A document with only one of
them is not a memo and will be filed as an ordinary document — that is
deliberate, so a report that happens to contain the word "To:" is not quietly
posted to somebody's desk.

**A memo to a desk that does not exist is refused, not guessed at.** It goes to
`_needs_review/` with the reason on it. A letter delivered to the wrong desk is
worse than one that visibly failed to arrive.

## How to answer one

Reply **inside the same memo**, under a line reading `ANSWERS:`, and change
`Status:` to `Answered`. Then drop it back in `inbox/` and it moves itself to
`answered/`.

**Never edit anything above the `ANSWERS:` line.** The question as it was asked
has to survive, or six months later nobody can tell whether the answer was any
good.

## The one rule that makes this work

**NOBODY STOPS WORKING TO WAIT FOR A REPLY.**

Write the memo, file it, take the next thing. The only exceptions are things
addressed to the Owner: anything irreversible, anything public, anything legal.
Those genuinely wait.

Everything else keeps moving. A question sitting in a tray costs nothing. A
person sitting still costs a day.

## Why it is set up this way

Until 2026-08-30, a question from the builder to the architect could only get
there by the **owner** reading a status report, spotting the question inside it,
and carrying it across by hand. He was doing a postman's job between two people
who could both read the same filing cabinet.

There was also a false start worth knowing about: the architect built a separate
folder to bypass the inbox, having dropped two files in `inbox/` and watched
them get filed away within seconds. The inbox was doing its job — the files were
simply not addressed to anybody. **A second filing system next to the one that
works is how a project ends up with two of everything.**

So: one way in, one thing sorting, one place to look.

## Owner-action

A letter that asks Sleven for a MANUAL STEP - a terminal command, a commit, a click, a
password, a swap, or "your word" on something a desk could already be authorised to do -
carries:

    Owner-action: yes

and a heading `Already checked` listing what was checked for an approved path and what came
back. Rule 27 in CLAUDE.md is the rule; this is where the field is declared.

A letter that asks him for a DECISION carries `Owner-action: no` or omits the field. A
decision is not a chore.

Letters dated before 2026-09-12 predate rule 27 and are not judged against this field.
