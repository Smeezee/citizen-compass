# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: Your third route is right and my suggestion was wrong — and a standing rule I issued tonight never reached you, which is my error and is visible in your own filenames

Status:  Open

**Nothing here changes what you are doing. Two items, both short, and one of them
is an apology.**

---

## 1. THE `.keep` WOULD HAVE BEEN EATEN AND YOU WERE RIGHT TO REFUSE IT

**I told you a committed `.keep` was one of two acceptable answers. It is not an
acceptable answer, and you proved why from the source.** An unrecognised extension
goes to `_needs_review/` on sight — **the marker file removed by the program it was
placed there to serve.** And `inbox/` is gitignored at line 28, so it could not have
been committed without a negation rule I did not mention either.

**The launcher creating it in the pre-flight is better than both options I offered.**
It survives a fresh clone, it cannot be eaten because a directory is not a file, it is
on the receipt, and `reply_path_is_a_file` closes the failure at the point it would
occur rather than after the money is spent.

**Your six planted states include mine in its worst form. That is the right answer to
a warning — turn it into a control that fails, not a thing somebody remembers.**

## 2. A STANDING RULE WAS ISSUED TONIGHT AND YOU NEVER GOT IT — MY ERROR, AND IT IS THE ONE-READER DEFECT AGAIN

**THE RULE, EFFECTIVE NOW:**

    A NEW ORIGINAL LETTER carries NO manually added date in its filename.
    The watcher stamps it, from this machine's clock, at the moment it files it.

    A REPLY preserves the filename it received, EXACTLY, character for character.

**Why it cannot be "use the right date":** `memo.go` only fills a GAP —

    if !reLeadingDate.MatchString(base) {
        base = time.Now().Format("2006-01-02") + "_" + base
    }

**A filename that arrives already stamped keeps whatever it was stamped with, right or
wrong, permanently.** So the only version that holds is do not stamp it at all.

**HOW I KNOW YOU DID NOT HAVE IT — YOUR OWN TWO LETTERS IN MY TRAY:**

    2026-09-11_memo_owner_containment-is-staged-and-the-only-thing-left-is-your-switch.md
    2026-09-11_memo_owner_both-replies-path-items-handled-and-your-first-answer-would-have-been-eaten.md

**This machine's date is 2026-09-10.** A letter I filed dateless twenty minutes before
yours was named `2026-09-10_...` by the watcher. **Yours carry tomorrow, because a
session clock running UTC is a different day after 19:00 here.** That mismatch already
broke one supersede tonight.

**AND THE PART THAT IS MINE, NOT YOURS:** I issued this as a standing rule and routed
it to Architecture only. **A rule with one reader — in a letter whose subject was a
rule with one reader.** You were working correctly against instructions you had never
been given.

**Do not rename anything already filed.** From the next letter forward, no date.

---

## WHAT I AM NOT ASKING FOR

**Not a fix to the coalesce.** Named and parked with Architecture is right.

**Not a rename pass.** Two filenames carrying the wrong day cost nothing now that the
cause is known and the rule is in place.

**Nothing else changes.** The switch is still absent and still mine. No brakes, no
doorbell, no second wake, nothing committed, no ACL changed, and the Looking Project
is excluded entirely.
