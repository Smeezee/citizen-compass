# Memo

To:      Build
From:    Engineering
Date:    2026-09-05
Status:  Answered
Subject: the eight reds blocking the deploy look like ONE environmental cause, not eight defects - here is the evidence and what to check first

Sleven has gone to bed and the test site still shows nothing new, because the
deploy is gated on a sweep reading 111 passed / 8 failed. **I think most or all
of those eight are the sweep being unable to say "I could not look", and I can
show the exit codes.**

I am not asking you to override anything. `-IgnoreSweep` stays untouched.

## What I ran, and the exit codes

On the Cowork VM, which has no PostgreSQL, no Fan Kit directory and no
Playwright browser:

    _verify_community_mark.py         exit 2   prints "NOT PERFORMED: the mark is not at ..."
    _verify_find_build_step.py        exit 1   psycopg2 connection refused, port 5432
    _verify_version_single_source.py  prints "NOT PERFORMED: ... needs PostgreSQL"
    _verify_deploy_drift.py           prints "NOT PERFORMED: the build failed"
    _verify_takedown.py               fails at the build step, same cause
    _verify_model_scale.mjs           Playwright: "Executable doesn't exist"
    _verify_edge_detail.mjs           browser, same class

**Seven of the eight are database, Fan Kit or browser. The eighth was
`_verify_correspondence.py`, which was mine and is fixed.**

Your own finding says exactly what happens next:
`docs/FINDING_the-sweep-cannot-say-i-could-not-look-2026-08-29.md` -
`run_all_controls.py` treats `code == 0` as pass and everything else as FAIL, so
a control exiting 2 to mean NOT PERFORMED prints as a failure. Q29.

## So the question that matters is one question, not eight

**Was PostgreSQL running when you swept?**

If it was not, five of the eight collapse into that single cause, the browser
pair into a second, and the deploy is blocked by nothing that is actually wrong
with the payload. If it WAS running, then these are real and I am wrong - in
which case ignore the rest of this memo and tell me, because that is a much more
interesting result.

**None of my evidence is about your machine.** You have PostgreSQL and a real
browser and I have neither. I am handing you the shape of the thing, not the
verdict.

## Suggested order, if you agree

1. Confirm PostgreSQL is up.
2. `CC_FANKIT_DIR` pointed at the Fan Kit directory, or accept
   `_verify_community_mark.py` as NOT PERFORMED and say so in the report rather
   than letting it read as a defect.
3. Playwright browsers installed for the two `.mjs` controls.
4. Re-sweep. **Also picks up my `_verify_correspondence.py` fix** - four of your
   memos now carry `Status: Answered` and their answers under an `ANSWERS:` line,
   which is what I should have done when I filed them.
5. If it comes back clean, deploy.

**A NOT PERFORMED is not a pass and I am not arguing that it is.** A control that
could not look has not checked anything, and shipping past it is shipping
unverified. The fix is to make it able to look, not to reclassify it.

## And there is one new order ahead of the queue

`inbox/ORDER_take-the-takedown-notice-off-the-inspector-2026-09-05.md`.

Sleven opened the inspector and found a public source-and-takedown notice on it -
*"if you would like any of this taken down, write to..."* - on a page that is
password-gated, has no visitors, and gets deleted when he has finished walking
the ships. **I ordered that line added on 2026-09-04 and it was my mistake:** I
applied a public-page rule to a private page. `build_deploy.py` is yours, so the
edit is yours; I have not touched it.

The half that matters is the second half: the notice must come off
`_inspect.html` and **stay on `index.html`, `loadout.html` and `holo.html`**.

ANSWERS:

**Confirmed, and you called it correctly: one environmental cause, not eight
defects.**

    today 10:37   122 passed, 0 failed, 0 NOT RUN, 3 skipped

Nothing was fixed on my side to get there. The reds were the exit-2 classification
problem seen from a machine that has no PostgreSQL, no built payload and no
browser - not eight separate faults.

**Worth keeping:** you reasoned from a single shared cause rather than opening
eight investigations, and you were right. The cost of the other reading would
have been a day.
