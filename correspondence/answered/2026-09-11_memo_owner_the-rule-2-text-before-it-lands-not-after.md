# Memo

To:      Owner
From:    Architecture
Subject: The exact words going into CLAUDE.md, before they land rather than after. Nothing needed from you unless you want to stop it.
Status:  Closed

**This is a notice with a window, not a question.** The Adjutant approved the wording under
your delegation and gave you a stop — *"if he wants to see it before it lands, he will say
so."* **A stop you are told about afterwards is not a stop, so here it is first.**

## THE ONE LINE, IN SUMMARY

**Code will be allowed to commit documentation files without asking you each time — and
only after a guard has been watched refusing something outside that scope.** Nothing else
changes. No pushes, no code, no deletions, and `CLAUDE.md` and `OWNERS.md` still need your
word every single time.

## THE EXACT TEXT GOING INTO YOUR RULE FILE

Under rule 2, after *"Never `git add -A`. Stage by name, every time."*

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

## WHY YOU ARE SEEING IT AND NOT JUST HEARING ABOUT IT

**You said you were not a hundred percent sure and delegated the judgement.** The
judgement was made and I am not re-opening it. **But the file this edits is the one that
governs every desk in the project, and you told me anything about the rules comes to
you.**

**Say nothing and it lands.** Code applies it as a single named change with nothing else
in that commit, and only after the guard has been recorded refusing.

**Say stop and it does not.**

---

## QUESTIONS

1. Anything you want changed in that text before it goes into `CLAUDE.md`? Silence means
   it lands.


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
