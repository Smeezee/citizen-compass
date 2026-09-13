# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: The gate is rule 27 in CLAUDE.md. Here is where and the exact wording. One thing I did differently from what you asked, and why.

**Nothing in this letter asks you for anything.**

## WHERE

**`CLAUDE.md`, `### 27`, inside the `## HARD RULES` block**, immediately after rule 23 and before
`## Standing rule: keep LATEST_HANDOFF.md current`. **30,248 bytes to 32,552, verified after the
write.**

**Why that position and not with 24, 25 and 26:** those three sit 120 lines further down under
`## Known caveats`, which is the defect the split proposal already reports — **the file's own first
instruction points at HARD RULES, so a desk obeying it literally never reaches them.** A rule whose
entire purpose is to be obeyed goes where desks actually read. **The numbering now reads 1-23, 27
in the rule block and 24-26 stranded, which makes that misplacement impossible to ignore.** That is
a side effect I am content with.

## THE EXACT WORDING

    ### 27. THE OWNER-ASK GATE. Never ask Sleven for a manual step until you have
    checked whether an approved path already exists.

    Ordered by Sleven, 2026-09-12, as a standing order:
    `correspondence/open/architecture/2026-09-12_memo_owner_the-owner-ask-gate.md`.
    Numbered here because rules live in this list and nowhere else.

    A manual step means anything that puts his hands in the machine: a terminal
    command, a commit, a click, a password, a swap, "your word" on a thing a desk
    could already be authorised to do.

    BEFORE the ask, run the gate:

    1. Does Build already have an approved path? A one-time approval, an existing
       Owner order that covers this, a swap script, a guard exception, or a job
       Architecture can simply order without him at the keyboard.
    2. If a path exists, use it. The ask does not happen.
    3. If no path exists, the letter carries a heading `Already checked` listing
       what was checked and what came back. A letter without that heading has not
       run the gate and is not to be sent.
    4. The ask itself is ONE LINE: the decision, or the action. Not a tutorial.

    DELETE THE LESSON. He uses commit, deploy, tray, sweep, watcher and push every
    day. Explaining a term he already uses is not helpfulness, it is padding, and
    it buries the ask. Teach a term only when he says he does not know it.

    AND THE SHAPE THAT IS REFUSED OUTRIGHT: "I should have checked first" cannot
    appear in the same letter that makes the ask. An apology for not running the
    gate is not a substitute for running it. If you notice mid-letter that the gate
    was skipped, stop, run it, and send one letter.

    THE FAILURE THIS COMES FROM. A guard blocked Code from committing, and this
    desk turned "Code is blocked by the control Sleven installed on purpose" into
    "Sleven, open a terminal" without once asking whether the guard had an
    authorised route. A control he built to protect the project became a chore
    handed back to him. That inversion is the thing this rule exists to stop.

    IT BINDS BUILD TOO. When a guard blocks a commit, a swap or a deploy, the
    report names the approved escape hatch first. "Owner must type" is the last
    line of that report, never the first, and it is only correct after the hatch
    has been looked for and found absent.

## BUILD IS TOLD

**Sent as its own letter, not a line in this one.** The matching failure mode is in rule 27's last
paragraph so it binds Build from the rule file rather than from a memo it has to remember.

## THE ONE THING I DID DIFFERENTLY

**You said a short skill or checklist is fine. I am not building one, and I think you already
gave the reason: "tools alone will not fix this; the rule must."**

**A skill only loads when something matches its trigger.** That is the same unreliability as a
habit — it fires when the shape is recognised and is silent when it is not, and **the letters that
break this gate are exactly the ones where the desk did not notice it was asking for a chore.** A
rule in the file every desk reads at boot has no trigger to miss.

**What I am doing instead is stronger than either, and it is your own pattern: a control.** I have
ordered Code to propose a check that reads the owner tray and flags any letter that asks for a
manual step without an `Already checked` heading. **Deterministic, in the sweep, catches me rather
than trusting me.** Proposal first, nothing built.

**If you want the skill as well, say so and it is a small job.** I am not doing it on my own
because I think it would be the appearance of a fix sitting next to a real one.
