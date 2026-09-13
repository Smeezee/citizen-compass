# Memo

To:      Owner
From:    Build
Date:    2026-09-11
Subject: Both `_replies` items handled. Your first suggestion would have been eaten by the watcher, so I took a third route and said which.
Status:  Closed

**Read before the probe, as you asked. Neither item delayed anything and no wake
has run.**

---

## 1. THE DIRECTORY EXISTS BEFORE ANYTHING LAUNCHES — AND NEITHER OF YOUR TWO OPTIONS SURVIVES THIS REPOSITORY

**You said: create it with a `.keep`, committed — or prove the desk can create
it — and say which. "Either is fine. Assuming is not."**

**I checked both before choosing and they both fail, for different reasons:**

**The committed `.keep` would be EATEN by the watcher.** Nothing anywhere in
`main.go` or `classify.go` skips dotfiles, and `.keep` is an unrecognised
extension — so `classify.go` routes it to `_needs_review/` on sight. **The marker
file would be moved out by the program it was placed there to serve**, leaving an
empty directory and a junk entry to show for it. And `inbox/` is gitignored at
`.gitignore` line 28, so committing anything under it needs a negation rule
first.

**"Prove the desk can create it" is unprovable without spending**, and the
pessimistic reading is the one with measured evidence behind it — your $0.19 run
of 2026-09-10.

**SO THE THIRD ROUTE, AND IT IS THE ONE I TOOK: the launcher creates it, in the
pre-flight, before anything is launched and before anything is spent.**

    reply path   inbox\_replies   (created here, before anything is launched)

**It is on the receipt so nobody has to assume it happened.** It works on a fresh
clone where no committed marker could survive, and **it cannot be eaten, because
a directory is not a file.**

**And if something occupies that path as a FILE, the launcher refuses with 78 and
a `reply_path_is_a_file` record** rather than letting a wake report success with
nothing on disk. **That is your measured failure mode, closed at the point it
would occur.**

## 2. THE COALESCE REGRESSION IS NAMED AND PARKED, NOT FIXED

**Confirmed from the source exactly as you read it.** `pendingInboxFiles` counts
the top level only, `_replies/` is a subdirectory, so replies count as zero
pending and **the coalesce never engages for them — about seventy seconds of
tail per reply.**

**Named to Architecture for placement**, per your instruction, in
`2026-09-11_memo_architecture_the-reply-path-never-coalesces-and-it-is-a-regression-not-a-break.md`.
**Not fixed inside step B, and I am not proposing the fix either** — the obvious
one, counting `_replies/` as pending, is precisely what that comment says would
make the watcher believe it is permanently busy. **The exclusion is sound and the
reply directory is a case it did not anticipate.** That is a design question.

## 3. YOUR SECTION 3 — I HAD CHECKED THE SAME THING AND WE AGREE

I verified the recursion before choosing the shape, for the same reason you did:
**a reply path the watcher never reads would have been a desk talking into a
wall.** `addWatchRecursive`, the new-directory walk in `handleFsEvent`, and the
startup `WalkDir` all agree. `isProtected` keying on the first segment only is
what keeps `_replies` unprotected.

---

## THE CONTROL GREW A SIXTH SECTION AND THE PROOF GREW A SIXTH STATE

`checks/_verify_reply_path.py` — **14 assertions now**, up from 11:

    the launcher has a function that creates the directory
    and the pre-flight calls it BEFORE anything is launched   (source order)
    and nothing on disk occupies that path as a FILE

`checks/_prove_reply_path.py` — **six planted states, all correct:**

    UNTOUCHED - the real files                            0 findings   OK
    the reply directory added to protected_folders.txt    2 findings   OK
    protected_folders.txt naming nothing                  1 finding    OK
    the launcher's constant deleted                       1 finding    OK
    a wide Edit allowance left in the launcher's code     1 finding    OK
    A FILE where the reply directory belongs              1 finding    OK

**The last one is yours** — it is the state your memo is about, in its worst form,
and it now fails a control instead of costing a run.

## AND TWO DEFECTS IN MY OWN CONTROL, BOTH FOUND BY RUNNING IT

**The source-order check compared a call site in `main()` against the DEFINITION
of `containment_probe` further up the file**, and reported the order broken when
the order was right. **A source-order check that does not say which two things it
is ordering is easy to get backwards and hard to notice.** The note is in the
code.

**Before that, its first version looked for the call followed by a newline** — the
pre-flight calls it inside the line that prints the path, so it found nothing and
failed a correct arrangement.

**Both were false RED, which is the safe direction**, and both are the same
lesson as the reassuring line I fixed an hour ago: a check is not finished when it
agrees with you.

## EVERYTHING RE-RUN

    _verify_api_key_guard.py  36/0     _prove_launcher_gate.py  4 planted, correct
    _prove_switch.py    32/0, 2 NP     _prove_wake_record.py    holds
    _verify_reply_path.py     14/0     _prove_reply_path.py     6 states, correct
    _verify_rule16_labels.py  GREEN    wake_desk.py --self-test exit 0

---

## STILL NOTHING RUN, AND STILL WAITING ON THE SAME ONE THING

    C:\Users\david\.cc-control\automation.switch   still absent

**The probe has not run and cannot.** No brakes, no doorbell, no second wake,
`memo.go` unopened since the swap, timezone untouched, nothing committed, no ACL
changed, the Looking Project excluded.

*Build, 2026-09-11.*

---

ANSWERS:

**Owner, 2026-09-11. Closed.**

Read. Your third route was accepted in
`correspondence/open/build/2026-09-10_memo_build_your-third-route-is-right-and-a-rule-never-reached-you.md`.
Nothing left to answer here.
