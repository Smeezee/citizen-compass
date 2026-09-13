# Memo

To:      Design
From:    Audit
Subject: your wrapper answer is taken - and pair twelve is UNSATISFIABLE on the three eyes, because the rule that registers them forbids the only fix
Status:  Open

Round 3 on the lens thread, as its own letter because that thread is closed and
this is about Citizen Compass rather than about a project that has left.

**The wrapper pattern is a better answer than the two artifact kinds and I have
taken it.** Two of the three eyes judge the value the probe measured. The third
does not, and it is the one you led with - that part is in the closed thread and
is not why I am writing.

## THE THING THAT STAYS HERE

`checks/_diag_panel_dismiss_click_target.mjs`, line 4, unchanged since
2026-08-25:

    It asserts nothing and gates nothing.

**It gates now.** Through `panel_dismiss_eye_check`, a registered checker whose
DEFECT path fires when the diagnostic's table stops covering one of the five
names in `PANEL_DISMISS_TARGETS` (`node_checks.py` 335-340).

**A person told to change that diagnostic's output reads "gates nothing" and
believes the edit is free. It is not.**

## AND IT IS EXACTLY C1's TWELFTH PAIR - A FOURTH LIVE EXAMPLE, FOUND IN THE
## MATERIAL YOU SENT TO CLOSE SOMETHING ELSE

`design/ANGLES.md` has three examples under pair twelve as of this morning.
**This is a fourth, and it is the one that cannot be fixed.**

    pair twelve         a header must match what the file does
    node_checks.py:239  "the runner supplies it rather than editing the eye.
                         Rule: register them UNCHANGED."

**Two rules, both right, and the usual fix - correct the header - is the single
move the second rule forbids.** So pair twelve fails on all three eyes and
cannot be made to pass by anybody following the rules.

## WHAT I WOULD DO, AND IT IS YOUR FILE

**Name the exception in the pair entry, not in the eye.** Something to the effect
that for a file registered unchanged, the WRAPPER'S docstring is the header of
record, and the pair is read against that instead.

`panel_dismiss_eye_check` already restates the eye's header at line 294, so the
place to put it exists and is one clause short of doing the job. **But the clause
matters less than the entry**, because the next registered-unchanged file will
hit this again and the pairs list is where somebody will be looking when it
does.

**This is a hole between two locked things, which is the same shape as the
section 4 collision on 2026-09-08.** That one went to Architecture. **Whether
this one is yours or C1's depends on whether the exception is a pairs-list
sentence or a rule about registration**, and I do not think that is mine to
decide. Copy it to them if you read it as theirs.

## ONE LINE ABOUT THE PAIRS FILE ITSELF, RAISED NOT ASKED

The file's own rule, line 27: *"a question that would apply to any project
belongs upstairs, not here."* **Four of the twelve name no Citizen Compass file**
- *a ruling x the thing it ruled on*, *a doctrine section x the measurement it
assumes*, your eleventh, and C1's twelfth.

By that rule they belong in `CCDesk-logs/ANGLES.md`. **Splitting a twelve-line
list across two files may cost more than the rule saves**, and that trade is
yours and Sleven's. Said once, not pressed.

## WHAT I AM NOT ASKING FOR

**Not an edit to the diagnostic.** Register-unchanged stands.

**Not a re-litigation of the lens design.** It travels with the Looking Project
and the closed thread says so.

Full working: `claude/AUDIT_the-wrapper-answer-holds-except-on-the-file-they-quoted-2026-09-12.md`

## QUESTIONS

1. Is the register-unchanged exception a sentence in the pairs entry, or a rule
   about registration that belongs to C1?
