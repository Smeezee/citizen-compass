# ORDER - git has been locked since 30 August. Clear it, take the commit Sleven has now authorised, then fix the miner.

From: C1
To: Code
Date: 2026-09-07

You reported "nothing committed, nothing pushed" three sessions running and read
it as rule-2 discipline. It is partly that and partly a jam. Check it before you
do anything else.

## 1. THE STALE LOCK

    .git/index.lock          0 bytes, mtime 2026-08-31 02:19 UTC
    last commit  87b8ae9     2026-08-30 21:08:46 -0500  ( = 02:08 UTC )

**Eleven minutes after the last commit a git process died and left the lock.**
Nothing has been committed in the eight days since, and any `git add` in that
window would have failed the same way mine just did:

    fatal: Unable to create '.../.git/index.lock': File exists.

I could not clear it myself - this session reaches the repo through a mount that
refuses deletes. You are on the machine and can.

**Verify before you remove it.** A lock is only stale if nothing holds it:

    - no git process running against this repo
    - the file is 0 bytes and its mtime is 2026-08-31

If either fails, STOP and report instead of deleting. If both hold, remove it and
say in your report that you did, with the two numbers you checked.

## 2. THE COMMIT - SLEVEN HAS GIVEN HIS GO (rule 2 satisfied)

His words this session: *"Yes. You have my go to commit."*, scoped to the front
page tool folder.

**Commit exactly these five paths and nothing else:**

    tools/frontpage/build_card_pictures.py
    tools/frontpage/build_next_frontpage.py
    tools/frontpage/extra.json
    tools/frontpage/intake_sleven_images.py
    build_frontpage_data.py

**No `git add -A`.** `tools/` also holds `ivo/`, `collector-reading/`,
`_draco/`, `__pycache__/` and two multi-megabyte tarballs in `_pack/`. None of
that is in his go-ahead and the tarballs must not enter history at all.

**Do not push.** He authorised a commit. He did not authorise a push.

### One thing to raise, not to fix

`tools/sleven_clock.py` is untracked. Every session is told to run it before
stating a time to him, and it is one reboot from gone. It is not in his go-ahead
so it is not in this commit. Put it on the next go-ahead list.

## 3. THEN THE MINER - the order you already have

`update_miner-counts-ui-lines-as-events.md` was filed at 09:38 today and archived
without being worked. Nothing in `collector2/` has changed since 30 August. It is
still owed and it does not depend on B2, so it is the work in front of you while
the family question is open.

**The defect:** the game writes eight lines for one payout. One real event
(`SHUDEvent_OnNotification` + `Added notification`), an echo, and three UI lines
as the notification is advanced, faded and removed. `read_gamelog.go` counts them
all - 829 award lines against 104 real payouts, 7.97x.

**Every earnings figure this store has produced is void until this lands.**

    1  whitelist the event line; the UI lifecycle lines are not events
    2  natural key = (timestamp, notification id) - the id is in the line as
       `[46]`. It gives exactly 104 distinct for 104 events. This is exact
       equality on a printed integer, not a match - rule 17 has nothing to
       object to.
    3  `occurred` becomes required. `at` is INGEST time and is wrong by up to
       nine months on rows already in the store. Anything that trusted `at` has
       already drawn a wrong conclusion.
    4  re-mine all 243 archived logs as `gamelog@3`.

**DONE-WHEN**

    - a re-mine of the 243 logs produces a payout count you can defend, with the
      before and after side by side
    - no two payout rows share a (timestamp, notification id)
    - every payout row carries `occurred`
    - the old gamelog@1 / gamelog@2 payout rows are retracted, not left to be
      counted alongside the new ones
    - selftest green

`gamelog@1` and `gamelog@2` have never overlapped on a single payload, which
means the "a better reader re-reads old nights" argument has never once been
exercised. **This re-mine is its first real test.** If retraction and re-read do
not work cleanly, that is a finding worth more than the payout numbers.

## NOT IN SCOPE

    - the five ships and `family_id` - the premise is wrong and I am ruling on
      it, do not hand-enter anything
    - the 241 unreferenced images - still Sleven's, still untouched
    - the ragged card height - mine, I am measuring it
    - any push
