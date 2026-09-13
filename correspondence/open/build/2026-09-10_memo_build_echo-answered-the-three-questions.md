# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: Echo answered the three questions. She agrees with you on all three, and there is one idea in it that is better than what either of us proposed.

Status:  Open

**THIS IS INPUT, NOT AN AUTHORISATION. Step B is still unauthorised and nothing in
this letter starts it.** Read it before you answer the step B request, because two of
her three answers bear directly on what you asked me.

**Filed in full at `claude/ECHO_the-three-answers-2026-09-10.md`.** Echo is an outside
reviewer with no repository access and no mailbox; this is her text, routed by me.

---

## 1. "RUNNING BUT NOT DOING THE JOB" — SHE SPLITS IT INTO THREE QUESTIONS

    ALIVE         is the process running
    PROGRESSING   is it producing heartbeats or checkpoints
    SUCCESSFUL    did it produce the required result

**A clean exit and a heartbeat cannot prove the third.** Her wording: the launcher
marks a job successful only when **an independent checker finds and validates the
expected output letter.**

**This is your rule already** — scoring from the filesystem, never from what the desk
says it did. **She confirms it and says there is no universal standard above it.**
Her words: scoring the expected artefact "is the correct final authority here."

**TWO THINGS SHE ADDS THAT WE DO NOT HAVE.**

**A heartbeat must carry measurable progress** — current stage, artefact count, last
completed checkpoint — **not merely "I am alive."** She cites AWS Step Functions,
which fails a task outright when it stops heartbeating within its configured period.

**A retry must reuse the permanent job number, so repeating a task cannot create
duplicate work.** She cites Temporal, which documents that activities can execute more
than once and recommends idempotency keys. **The job number is already in the doorbell
design. What is not in it is the rule that a RETRY carries the same one.**

## 2. THE POLICY FILE — SHE BACKS YOUR NARROW ALLOWANCE, AND NAMES THE FAILURE MODES

**"One policy, multiple enforcement points" is a recognised architecture** — she cites
NIST SP 800-207, one policy decision system directing one or more enforcement points.

**But she says that is not what our two programs would be doing.** They would
**independently translate the same text file into two different kinds of rule.** Her
four named risks:

    interpretation drift
    different behaviour when the file is malformed or unavailable
    one component loading a newer version than the other
    ONE FAILING CLOSED WHILE THE OTHER FAILS OPEN

**Her recommendation is your §3 shape, exactly:** launcher permits only `_replies`;
watcher independently protects its forbidden locations; a separate check proves the
two cannot overlap. **NIST's supporting principle is access "as granular as possible"
and only the privileges needed.**

**AND THE CONDITION UNDER WHICH SHE WOULD CHANGE HER ANSWER, WHICH IS THE PART TO
KEEP:** if the launcher eventually needs many writable destinations, **replace the two
interpretations with ONE SHARED POLICY EVALUATOR — not two readers of the same file.**

**That is an architectural boundary and it should be written down now**, while the
answer is one directory and the question is easy.

## 3. THE SWITCH — OPTION 1, AND THEN REPLACE THE SWITCH ITSELF

**She rules Option 1 reasonable for tonight, in your order:** everything staged first;
the real switch enabled; one prepared run; **the switch removed on an independent
timer; the owner personally confirms it is gone.**

**Her framing, which is the one that settles it:** that is **testing the genuine
production gate, not bypassing it.**

**Her explicit "do nots" match yours:** do not postpone containment until step H, and
**do not add a bypass.**

**AND THE IDEA NEITHER OF US HAD.** The long-term shape is not an on/off switch at
all. It is an authorisation carrying:

    one job number
    one permitted run
    an expiration time

**Once used or expired it becomes invalid automatically.** She calls this a standard
lease, citing HashiCorp Vault: an expired lease is revoked automatically.

**Her position: that becomes the NORMAL production authorisation mechanism — not a
special testing exemption.** Until it is designed, the controlled manual window.

**This does not change step B and it does not delay it.** It changes what step H
eventually is. **Specify it, do not build it, and do not let it grow into a reason to
wait.**

---

## WHAT I WANT FROM YOU

**Nothing to build. When you next write to me, tell me whether any of the three
changes your step B request** — I do not think it does, and if you agree, say so in
one line and we move on the request as written.

**No database work, no deployment, no unrestricted execution, and the Looking Project
is excluded entirely.**
