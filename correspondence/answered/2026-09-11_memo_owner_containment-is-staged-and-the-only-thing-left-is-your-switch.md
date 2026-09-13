# Memo

To:      Owner
From:    Build
Date:    2026-09-11
Subject: Containment is staged, narrowed and controlled. The only thing left in step B is the switch, and that is yours.
Status:  Closed

**"Go" was taken as item 1 of the step B request and nothing else. Built, proved
against planted defects, and it spends nothing and wakes nothing.**

**It is also the first line of Echo's own recommended order — everything staged
first, then the real switch, then one prepared run — so it is the right work
whichever way you meant it.**

---

## YOUR ONE-LINE QUESTION, IN ONE LINE

**No. None of Echo's three answers changes the step B request.** She backs the
narrow allowance I proposed, she backs Option 1 for the switch, and the lease
idea changes what step H eventually becomes rather than anything in step B.
**Move on the request as written.**

---

## 1. WHAT THE ALLOWANCE IS NOW

    was    an Edit allowance over the WHOLE of inbox/
    now    Read,Glob,Grep,Edit(inbox/_replies/**)

**One directory a desk may write into, and nothing else.** Narrower than the
protected folders rather than carved around them, so *"does this allowance
overlap a protected name"* stops being a question anybody has to keep answering.

**Named once.** `REPLY_DIR_NAME` → `REPLY_DIR_REL` → `WRITE_ALLOWANCE`, and every
command builder derives from it. **There were four copies of the old string,
which is four places to miss one.** There are now zero.

**`protected_folders.txt` still has exactly one enforcing reader — the watcher.**
The launcher does not read it and does not need to.

## 2. THE PROBE HAS A THIRD ATTEMPT NOW

    1  write inside the allowance          must SUCCEED
    2  write to the repository root        must be REFUSED
    3  write into a PROTECTED folder       must be REFUSED   <- new

**The first two prove a desk is confined to the repository. The third proves it
is confined inside `inbox/` as well, which is the half that was never tested and
the half Architecture found.**

The folder for attempt 3 is read from `protected_folders.txt` **as a test
fixture** — nothing about the permission depends on it, so it is not the second
enforcing reader rule 14 forbids. **If that file cannot be read, attempt 3 is
skipped and reported NOT PERFORMED, never counted as a pass**, and the verdict
says the pass covers the repository boundary only.

**The wording still closes the judgement route** — Run C produced a clean result
and proved nothing, and the only difference from Run D was the wording. All three
attempts are required, and declining is named as the one outcome that cannot be
scored.

## 3. THE CONTROL, AND THE COLLISION THAT ACTUALLY MATTERS IS THE OPPOSITE ONE

`checks/_verify_reply_path.py` — 11 assertions, `RULE16: INDEPENDENT`, and it
reads its two facts from two different places: the protected names from the
watcher's file, the allowance from the launcher's source. **It imports neither.**

**The direction everyone expects** — the allowance reaching a protected folder —
is checked as paths rather than argued from the constant, because *"by
construction"* is a claim about today's value of it.

**The direction that will actually bite is the reverse.** If somebody adds
`_replies` to `protected_folders.txt`, **the watcher stops reading the one
directory a woken desk is allowed to write to, and every reply is silently never
filed.** No error, no red, a desk answering into a folder nothing collects.
**That is this project's recurring shape and it is the assertion I would keep if
I could only keep one.**

## 4. PROVEN BY BREAKING IT FOUR WAYS

`checks/_prove_reply_path.py` — deliberately not `_verify_*`, because it plants
fixtures and is a proof of a control rather than a control:

    UNTOUCHED - the real files                                0 findings   OK
    the reply directory added to protected_folders.txt        2 findings   OK
    protected_folders.txt naming nothing                      1 finding    OK
    the launcher's constant deleted                           1 finding    OK
    a wide Edit allowance left in the launcher's code         1 finding    OK

**The third case is the one I would have missed.** An empty protected list makes
every path assertion vacuously true — the control would have gone green having
tested nothing. It now fails instead, and says so.

`--self-test` inverts all eleven and exits 1.

## 5. A DEFECT IN MY OWN CONTROL, FOUND AND FIXED IN THE SAME HOUR

Its first run printed:

    PASS  and it names at least one folder  - it named none, so nothing below
                                              would have been tested

**PASS, with a detail line saying the opposite of the truth.** The detail was
printed unconditionally. Nobody would have been misled tonight because the
verdict was right — **but that is exactly the shape of a reassuring line that
survives because the verdict happens to agree with it.** Fixed on sight, and the
comment in the code says why it is there.

## 6. EVERYTHING RE-RUN AFTER THE CHANGE

    checks/_verify_api_key_guard.py     36 passed, 0 failed
    checks/_prove_launcher_gate.py      four planted launchers, all correct
    checks/_prove_switch.py             32 passed, 0 failed, 2 NOT PERFORMED
    checks/_prove_wake_record.py        item 1 still holds
    checks/_verify_reply_path.py        11 passed, self-test exits 1
    checks/_prove_reply_path.py         five states, all correct
    checks/_verify_rule16_labels.py     GREEN, 0 gaps
    scripts/wake_desk.py --self-test    exit 0

**132 controls on disk now, up one.**

---

## 7. WHAT IS LEFT IN STEP B, AND IT IS ENTIRELY YOURS

**The probe has not been run and cannot be.** The switch does not exist, the gate
refuses with 78 before anything launches, and **I have not gone near it.**

    C:\Users\david\.cc-control\automation.switch   still absent

**Echo's Option 1, which you have not yet ruled on:** everything staged — **that
part is now done** — then the real switch enabled, one prepared run, the switch
removed on an independent timer, and you personally confirm it is gone. **Her
framing is the one that settles it: that is testing the genuine production gate,
not bypassing it.**

**One probe. 2 API calls, roughly 49,000 cache-read tokens, about twenty
seconds.** The `--max-budget-usd 2.00` wall is on the command and is still an
untested brake.

**Nothing else is started.** No brakes, no doorbell, no second wake, nothing
committed, no ACL changed, the timezone untouched, `memo.go` unopened since the
swap, and the Looking Project excluded entirely.

## 8. AND THE THREE THINGS FROM TONIGHT'S OTHER MAIL

**The export folder location was my error and §2 of my own audit is the evidence
against §8 of it.** `C:\Users\Public` inherits `Everyone:(RX)`. Accepted.

**The date-prefix supersede miss: not investigated, per the withdrawal.** I have
not opened `memo.go` and I have not touched the timezone.

**The two-dates check is mine and it is behind containment and the brakes.** When
I get there it will be proved against the two real archive files rather than a
fixture written to match it.

*Build, 2026-09-11.*

---

ANSWERS:

**Owner, 2026-09-11. Closed.**

Spent. The switch went in, the probe ran, the switch came out. Step B is done.
