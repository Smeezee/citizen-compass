    state        BLOCKED
    blocked_on   the switch, and his ruling on Echo's Option 1
    clears_by    OWNER

Filed at 21:31 CDT / 02:31 UTC — `date` run at 21:28:26, this typed after it.

# BOTH `_replies` ITEMS HANDLED. HIS FIRST SUGGESTION WOULD HAVE BEEN EATEN BY
# THE WATCHER, SO I TOOK A THIRD ROUTE AND SAID WHICH.

**Reports filed:** to him,
`2026-09-11_memo_owner_both-replies-path-items-handled-and-your-first-answer-would-have-been-eaten.md`;
to Architecture, the coalesce regression for placement.

## 1. THE DIRECTORY — NEITHER OF HIS TWO OPTIONS SURVIVES THIS REPOSITORY

**A committed `.keep` inside `inbox/_replies/` would be routed to
`_needs_review/` on sight.** Nothing in `main.go` or `classify.go` skips
dotfiles, and `.keep` is an unrecognised extension. **The marker file would be
moved out by the program it was placed there to serve.** And `inbox/` is
gitignored, so committing under it needs a negation rule first.

**"Prove the desk can create it" is unprovable without spending**, and the
pessimistic reading is the one with his own $0.19 measurement behind it.

**So: the LAUNCHER creates it, in the pre-flight, before anything is launched.**

    reply path   inbox\_replies   (created here, before anything is launched)

On the receipt, so nobody assumes it happened. Works on a fresh clone where no
committed marker could survive. **Cannot be eaten, because a directory is not a
file.**

**And a FILE at that path now refuses with 78 and a `reply_path_is_a_file`
record** rather than letting a wake report success with nothing on disk — his
measured failure mode, closed where it would occur.

## 2. THE COALESCE REGRESSION — NAMED, PARKED, NOT FIXED

`pendingInboxFiles` counts the top level only and says so in its own comment.
`_replies/` is a subdirectory, so **replies count as zero pending and the
coalesce never engages — about seventy seconds of tail each.**

**Named to Architecture for placement.** Not fixed inside step B, and **I did not
propose the fix either**: the obvious one, counting `_replies/` as pending, is
exactly what that comment says would make the watcher believe it is permanently
busy. The exclusion is sound; the reply directory is a case it did not
anticipate. That is a design question, not mine.

## THE CONTROL GREW A SIXTH SECTION, THE PROOF A SIXTH STATE

    _verify_reply_path.py   14 assertions (was 11), self-test exits 1
    _prove_reply_path.py    six planted states, all correct

**The sixth planted state is a FILE where the reply directory belongs** — his
memo's worst case, and it now fails a control instead of costing a run. It runs
against a redirected ROOT so nothing in the real `inbox/` is touched; a planted
file there would be routed away within seconds and the fixture would evaporate
mid-test.

## TWO DEFECTS IN MY OWN CONTROL, BOTH FOUND BY RUNNING IT

**The source-order check compared a call site in `main()` against the DEFINITION
of `containment_probe` further up the file** and reported the order broken when
it was right.

**Before that, it searched for the call followed by a newline** — the pre-flight
calls it inside the line that prints the path, so it found nothing.

**Both were false RED, which is the safe direction**, and both are the same
lesson as the reassuring detail line earlier: **a check is not finished when it
agrees with you.** Notes left in the code at both sites.

## RE-RUN

    _verify_api_key_guard.py  36/0    _prove_launcher_gate.py  4 planted, correct
    _prove_switch.py    32/0, 2 NP    _prove_wake_record.py    holds
    _verify_reply_path.py     14/0    _prove_reply_path.py     6 states, correct
    _verify_rule16_labels.py  GREEN   wake_desk.py --self-test exit 0

## UNCHANGED

**The switch is still absent, the probe has not run and cannot.** No brakes, no
doorbell, no second wake, `memo.go` unopened since the swap, timezone untouched,
nothing committed, no ACL changed.
