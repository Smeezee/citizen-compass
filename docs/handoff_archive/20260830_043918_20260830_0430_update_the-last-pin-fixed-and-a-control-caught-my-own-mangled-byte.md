# Update — the fifth pin is fixed and the deploy is unblocked. Then a control caught a backspace byte I had just written into two of my own files.

**2026-08-30 09:30 UTC / 2026-08-30 04:30 local · Code (background session)**

## THE FIFTH WAS THE SAME SHAPE AND I WAS WRONG TO CALL IT A STOP

C1 supplied the diff and the promise had not gone missing:

    BEFORE  UEX rates how much it trusts each submission - that is why its records
    AFTER   UEX scores how much it trusts each one. That is why these rows carry
            a quality rating, averaged buy and sell figures and stock levels at
            all. Those are fields you only need when the numbers are estimates.

**Three words moved and the replacement is stronger** - the old one gestured at
"its records", the new one names the fields the reader is looking at and says
why they exist. **I verified it on the built page before touching the control.**

Fixed as two halves, per C1's suggestion:

    says UEX weights its submissions        /UEX (rates|scores) how much it trusts each/i
    and says what that weighting is FOR     /(quality rating|confidence)...(estimate|trusts?)/i

**The second half is the one that earns its place.** A rewrite that keeps the
trust claim and drops the consequence still goes red, and the page saying LESS
is the failure worth catching. 30 assertions, exit 0.

**FOUR CONTROLS THIS SESSION PINNED PROSE INSTEAD OF A CLAIM** - `colour`,
`labelled`, `one shot, not per second`, and this. That is a pattern, not four
coincidences: **a control that asserts exact wording fails the day the wording
improves, and improving wording is something this project does on purpose.**

## THEN A CONTROL CAUGHT ME

    _verify_control_bytes.py
      no source file carries an escape-mangled byte
        checks\_verify_shared_viewer.mjs:265
        checks\_verify_ship_name_route.mjs:266

**`document\b` in my new regex became a literal BACKSPACE, 0x08.** The shell
collapsed `\b` to `\b` on the way into Python, and Python read it as the escape
it is. Both files still parsed and both controls still passed - the regex simply
had a control character where a word boundary belonged, so it would have
silently stopped matching what it was written to match.

**A control I did not write caught a defect I made twenty minutes earlier, in a
file I was editing to fix a different false red.** That is the suite doing
exactly what it exists for.

Repaired by writing the byte explicitly rather than through a shell. All three
green.

**This escaping trap has now cost me six edits today** - `\n` in
`_verify_deploy_drift.py` twice, in `build_deploy.py` twice, in `sweep_gate.py`,
and now `\b` here. **DEFERRED: stop writing regexes through a shell heredoc.**
Every one of these came from the same route.

## STANDING

    five controls fixed, all green
    _verify_control_bytes.py green
    deployed-only: find_deployed, picker_deployed - red until the redeploy

Sweeping now. Gate, redeploy, commit, and on down the queue.
