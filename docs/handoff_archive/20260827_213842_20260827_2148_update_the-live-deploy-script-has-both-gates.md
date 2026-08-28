# Update — `deploy_live.ps1` has both gates, and the control that proves them went in with them. 56 -> 83 assertions.

**2026-08-27 21:48 local · Code (background session)** — Sleven: *"add the gates
to deploy_live.ps1"*. The finding from 20:34 is closed.

## What went in

**1. The build receipt gate**, checked first, before the payload identity checks
and long before the browser checks, so a refusal is immediate rather than four
minutes in:

    missing     no build to judge. Allowed, and SAID so rather than assumed.
    ok          the build reached its last statement.
    anything    refused, naming the status and the exit code.
    unreadable  refused. An unreadable receipt is not a passing one.

Override: `-IgnoreFailedBuild`, which prints a banner saying it is publishing to
the PUBLIC SITE from a build that did not succeed.

**2. The browser-check gate**, the same four checks on the same bytes - both
scripts publish `testing\_deploy`, so a check that passed before Sleven reviewed
the testing site is a check against the very payload going public. A missing
check FILE is refused as NOT CHECKED. Override: `-IgnoreRedCheck '<name>'`,
which names one check rather than waving the gate through.

**Both escape hatches came across, and so did the reason they are not `-Force`.**
A gate with no documented way past it gets bypassed by editing the script, and
then the bypass is invisible.

**And the `-File` normalisation came with them.** Under `powershell -File`,
`-IgnoreRedCheck 'a.mjs','b.mjs'` arrives as the single string `"a.mjs,b.mjs"`
and a `-contains` test is false for both names. That defect was found in the
testing script by RUNNING the three paths; it is not repeated here.

## The control went in at the same time, which was the whole point

Section 9 (**the live gates**) and section 10 (**the receipt, on BOTH scripts**).
**56 -> 83 assertions, 0 failed**, `--self-test` still exits 1.

    9.  deploy_live.ps1 REFUSES a missing browser check FILE / names it /
        never said it would publish
        REFUSES a RED check / names it / quotes the LIVE override / never
        said it would publish
        -IgnoreRedCheck publishes past it / says OVERRIDE and PUBLIC SITE /
        reaches the dry run
        but a DIFFERENT check name does not wave the red one through

    10. BOTH scripts REFUSE a failed build / name the exit code / never reach
        the dry run / -IgnoreFailedBuild gets past it, loudly / then reaches it
        BOTH scripts REFUSE an UNREADABLE receipt

**Section 10 covers the testing script too.** Q2's DONE-WHEN was satisfied there
this evening but only ever proven by me typing it at a prompt. It is now
asserted on every run, on both sides.

## Proven by behaviour, including against the gate's own absence

Every assertion drives the REAL script with `-WhatIf` against throwaway trees -
a genuinely absent check file, a check that genuinely exits 1, a planted failed
receipt, a receipt that is not JSON.

And the load-bearing one, because "it refused" is not the same as "the gate is
what refused". I copied the live script with the browser-check block cut out and
ran the same RED-check fixture through both:

    WITHOUT the gate: exit=0   reached the dry run=True
    WITH    the gate: exit=1   reached the dry run=False

**Without it, a red check publishes to the public site and reports success.**
That is the defect the finding described, measured rather than argued - and it
means section 9 would catch the gate being removed again. The probe copy went to
`_to_delete/probes-2026-08-27/`, never deleted.

## One more thing, in the file's own header

The header claimed this script was a mirror of the testing one, *"and every one
of those differences is a refusal"*. That sentence was untrue for a day. It now
lists both gates - **and says the gap existed**, rather than tidying it away:

> THE LAST TWO IN THAT LIST ARRIVED LATE ... for a day the rehearsal ran four
> browser checks and read the build receipt while the performance did neither.

## What I did NOT do

**`deploy_live.ps1` has still never been run for real, and I did not run it.**
Everything above is `-WhatIf` against temp directories with an obviously fake
token. The live worker was never contacted. Only Sleven publishes the public
site.

Nothing committed, nothing pushed, live site untouched.
