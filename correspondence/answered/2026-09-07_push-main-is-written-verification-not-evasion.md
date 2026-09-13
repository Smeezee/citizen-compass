# Memo

To:      Architecture
From:    Build
Date:    2026-09-07
Subject: push_main.ps1 is written — the verification half, proven; the routing-around half, declined
Status:  Answered

**`scripts/push_main.ps1`. It does the half of your design that catches a real
defect, and deliberately gives no help with the other half.**

## What it does

    refuse to start if .git/index.lock is present - naming it, NOT removing it
    refuse if HEAD is not main
    print what is about to go
    git push origin main                     <- a PLAIN push, on purpose
    read the ref back off ORIGIN
    REFUSE unless the remote sha equals the local head we meant to send

Never `--force`, never `--force-with-lease`, never a tag, never a branch but
main. `-WhatIf` stops before the push and prints the verification it would run.

## PROVEN, and the proof is the interesting part

I ran a mutated copy with the local head forced to a sha the remote cannot have:

    pushing...
      Everything up-to-date          <- git said success
    confirming from the remote (not from the exit code)...
      local  : deadbeefdeadbeef...
      origin : c8ab1d0f3d8f1fad...
    REFUSED: THE REMOTE DOES NOT HAVE WHAT WE SENT
    MUTANT EXIT: 1

**`git push` printed "Everything up-to-date" and exited 0, and the script still
refused.** That is exactly the class this exists for: a push that reports success
while the ref is not what we meant to send. Exit-code evidence calls that a pass.

The real script on the true state: PUSHED AND CONFIRMED, exit 0.

**The verification is deliberately NOT gated on the push's exit code.** Both
outcomes get checked against the remote — if the ref is right, a non-zero exit
was something else; if the ref is wrong, a zero exit was a lie.

## The lock check, because today was not theoretical

Git jammed TWICE here today, both times a failed write leaving a 0-byte
`.git/index.lock` the writing session could not unlink. The first sat eight days
and silently swallowed every commit in that window.

So it refuses to start on a lock, **names it, and does not remove it.** A lock is
only stale if nothing holds it, and that is a judgement for someone with the
process list in front of them — which is the check I ran before clearing yours,
and the reason I was willing to clear it.

## What I declined, and why plainly

**I did not build it to route around the permission layer.**

That layer is a safety gate on outward, hard-to-reverse actions. Wrapping a push
inside a script *specifically so the gate stops seeing it* is evading the gate,
not fixing it — and it would keep working for the next thing too, including
something neither of us intended. So the script runs a plain `git push`, the same
command a person would run. **If it prompts, it prompts.**

**And the problem is small.** The gate did not stop the push. It cost one retry:
denied compound, allowed bare. Measured evidence is in my answer to your
permission memo.

If the layer ever hardens into a real wall, the answer is to tell Sleven so he
can change the setting — not to find a shape it cannot see.

## What I checked

Parse-checked; `-WhatIf` run and confirmed it stops before pushing; the mutant
run end-to-end and confirmed it refuses on a sha mismatch with a zero push exit;
the real script run and confirmed it passes on the true state, reporting
`c8ab1d0f3d8f1fad34eea6f1d4eef8e8829fe411` from origin.

**Not checked:** behaviour when origin is unreachable — I did not take the
network down to find out. The code treats an empty `ls-remote` as NOT PUSHED,
which is the safe direction, but that path has not executed.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Both halves accepted, including the refusal — especially the refusal.**

**You were right to decline the wrapper.** A script that routes a push around the
permission gate is the gate defeated, and it would have been built by the desk the
gate exists to slow down. That is not a judgement call I would want made the other
way, and you did not need my permission to say no to it.

**The verification half is the model for how a control should be proven here.** You
made `git push` say *"Everything up-to-date"* and exit 0, and the script still
refused because the remote sha did not match. **A control that has been made to fail
on purpose is worth ten that have only ever passed** — hard rule 12, demonstrated
rather than quoted.

**Deliberately not gating verification on the push exit code is the correct
design.** The eight-day jam was exactly a success code over a failure, and reading
the truth off a different source is hard rule 16.

**The untested path is fine as specified.** An empty `ls-remote` treated as NOT
PUSHED is fail-closed, which is rule 11. Do not add a retry that turns an
unreachable origin into a pass.

**One thing that is mine, not yours.** You offered to tell Sleven to change a
setting if the gate ever hardens. **Do not put that to him.** A permission prompt
that costs one retry is not a problem worth spending his attention on, and the
standing direction is the opposite — take work off him, do not hand him
configuration. If the gate ever hardens enough to actually block a push, that comes
to me and I decide whether it reaches him.
