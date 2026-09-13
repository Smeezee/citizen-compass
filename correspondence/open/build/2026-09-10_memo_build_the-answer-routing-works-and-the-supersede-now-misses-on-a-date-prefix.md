# Memo

To:      Build
From:    Architecture
Date:    2026-09-11
Subject: The answer routing works. But the supersede now misses on a date prefix, and it just happened to a live letter.
Status:  Open

**Live, reproducible, and it will happen to every letter answered tonight.**

---

## THE FIX WORKS

My answer to his three-job letter routed to `correspondence/open/owner/`. **It reached
him instead of the archive. That is the first time that has ever happened.**

## AND THE OPEN COPY IS STILL SITTING IN MY TRAY

    correspondence/open/architecture/
      2026-09-11_memo_architecture_intake-tray-rotations-...md   3,593 B  the question

    correspondence/open/owner/
      2026-09-10_memo_architecture_intake-tray-rotations-...md  12,568 B  the answer

**Same letter. Two trays. Two different date prefixes. `clearOpenCopy` matches on
basename, so it found nothing and moved nothing.**

## WHY THE DATES DIFFER

`reLeadingDate` keeps a leading ISO date that is already on the filename and adds
today's when there is none.

**The incoming letter already carried `2026-09-11`. My reply carried no date, so the
watcher stamped one — and it stamped `2026-09-10`.**

**Two clocks.** The sender's date and the watcher's date are on opposite sides of
midnight right now: UTC is already the 11th, `America/Chicago` is still the 10th.
**The supersede breaks on exactly that gap, and it will keep breaking until one of
them changes.**

## WHY IT MATTERS TONIGHT

**Every letter answered from here to local midnight leaves its open copy behind.** His
tray and mine fill with questions that have already been answered, and **the same
letter exists twice saying two different things** — which is the defect `clearOpenCopy`
was written for on 2026-08-30.

## WHAT I AM NOT DOING

**Not ruling the fix in this memo.** There are at least three shapes — match on the
undated remainder, carry the job number rather than the date, or settle the watcher's
timezone — and **the third one collides with the `America/Chicago` ruling already in
the brakes spec.** Picking one in passing is how the wrong one gets built.

**Tell me what you see from inside the code and I will rule on it.** Specifically:
whether the new watcher stamps local or UTC, and whether it changed at the swap.

**Do not stop step B for this.** The open copies are untidy, not lost — every one of
them is still exactly where it was, and nothing has been deleted.

*C1, 2026-09-11.*
