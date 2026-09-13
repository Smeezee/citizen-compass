# Memo

To:      Owner
From:    Architecture
Subject: The wording for hard rule 2's exception, for your approval — plus one thing in ruling 24 that has an order to it
Status:  Closed

**Ruling 21 creates a standing exception to hard rule 2 and `CLAUDE.md` does not carry
it. Until it does, the rule file and your ruling disagree on paper.** Wording below.
**`CLAUDE.md` is yours; I have not touched it.**

## THE PROPOSED WORDING

To be added under rule 2, after `**Never `git add -A`.** Stage by name, every time.`

    **ONE STANDING EXCEPTION, ruled 2026-09-12: documentation commits by Code.**

    Code may run `git commit` on documentation without asking, when ALL of these
    hold:

      - every staged path is in the documentation set below
      - a pre-commit guard is installed AND has been proven able to refuse,
        by mutation, on a path outside the set
      - staged by name. `git add -A` is still never.
      - one work item per commit, named in the message

    THE DOCUMENTATION SET: tracked `.md` files under `docs/`, `claude/`,
    `design/` and `correspondence/`, plus `NEXT.md`, `LIVE.md`, `RECOVERY.md`.

    NOT INCLUDED, and these need his word every time: `CLAUDE.md`, `OWNERS.md`,
    any code, any data, any deletion, any rename, and EVERY push.

    If the guard is not installed, or cannot be shown to refuse, the exception
    does not apply and rule 2 stands unchanged.

## THREE THINGS ABOUT IT WORTH THIRTY SECONDS

**The guard is the whole exception.** Your ruling says "only after an automatic guard
proves it refuses anything outside the allowed scope", and I have written that as a
precondition rather than an aspiration: **no proven guard, no exception.** A permission
that depends on a desk remembering the scope is not narrow, it is unenforced.

**`CLAUDE.md` and `OWNERS.md` are excluded on purpose.** They are `.md` files and they
are not documentation — they are the rules and the ownership list. **A permission that
lets a desk commit the file containing the permission is not a narrow one.**

**"Specifically named documentation files" — I read that as the scope being specified
rather than left to judgement, so I wrote a precise rule instead of a literal file
list.** A list of eight hundred documents would be unmaintainable and would go stale the
first time somebody added one. **If you meant a literal enumerated list, say so and I
will write that instead.**

## AND ONE THING IN RULING 24 THAT HAS AN ORDER TO IT

**Shrinking the mirror is a deletion, and there are documents that exist ONLY in the
mirror.** The 2026-09-10 finding established that — four chosen at random were not on
disk anywhere, and the real number has never been counted.

**So: recover first, shrink second.** The audit runs to completion and every project-only
document is pulled into the repository before one document leaves the mirror. **Shrinking
first would delete the only copy of documents nobody has counted yet.**

**Written into the record spec that way, with the mirror set named:** the state document,
each desk's boot prompt, and `NEXT.md`. **Nothing else — a session that cannot reach the
repository cannot act on a finding either, and a copy it can read but not act on is the
duplicate you named.**

---

## QUESTIONS

1. Approve the rule 2 exception wording as written, or change it?
2. "Specifically named documentation files" — the precise rule above, or did you mean a
   literal enumerated list of files?


---

ANSWERS:

**Owner, 2026-09-12, in his own words: "I have nothing more to say. If is going to cause a
problem. fix it to where it doesn't cause a problem."**

**The window closed with a yes.** No change to the text. **Code applies it as a single
named change with nothing else in that commit, and only after the guard has been recorded
refusing** — that precondition is in the text itself, so the exception cannot exist before
the evidence does.

**Recorded by Architecture, 2026-09-12.** Build has been told it is cleared, with the
boundary of that instruction restated: **it does not reach a deploy, a push, a deletion,
money, credentials, the public site, or anything about rights, Fan Kit or publication.
Those stay his regardless of how broadly the words read.**
