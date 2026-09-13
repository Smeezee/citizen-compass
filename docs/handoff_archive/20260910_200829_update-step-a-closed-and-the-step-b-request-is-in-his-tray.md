    state        BLOCKED
    blocked_on   the step B authorisation, and one decision inside it that is his
    clears_by    OWNER

Filed at 20:10 CDT / 01:10 UTC — `date` run at 20:05:11, this typed after it.

# STEP A IS ACCEPTED AND CLOSED. THE STEP B REQUEST IS WRITTEN AND IN HIS TRAY.

## THE FULL MAIL CYCLE JUST RAN ON A REAL LETTER, IN PRODUCTION

**Not a synthetic one. The step A report itself:**

    19:53:48  Status: Open       ->  correspondence/open/owner/
    20:01     Status: Answered   ->  correspondence/open/build/   MY TRAY
              and the owner-tray copy superseded at 20:02:02
    20:06:26  Status: Closed     ->  correspondence/answered/
              and the build-tray copy superseded at 20:06:26

**All three status words, in order, on a live thread, with a rule-1 copy kept at
every move.** Yesterday that letter would have gone into the archive the moment
he answered it and I would never have seen the reply.

**I closed it myself, and that is the point of the third word:** closing is now a
deliberate act by a desk rather than a side effect of somebody replying once.
Only the `Status:` line was changed — the question as asked and his answer
underneath it both survive verbatim.

## WHAT HE TOOK AND WHAT HE ADDED

**Accepted, all of it, and closed.** Three things he put on the record: that
condition 2 was caused rather than simulated; that my own command lied to me
mid-swap and I wrote it down instead of moving past it — **"the fourth
silent-success this week and the only one found while it was happening"**; and
that two of my assertions failed while the system was right both times.

**On Q7 he accepted my refusal of a second reader for `protected_folders.txt`.**
That matters for step B and it creates the one disagreement in it.

## THE STEP B REQUEST — WHAT IS IN IT

`correspondence/open/owner/2026-09-11_memo_owner_step-b-authorisation-request-containment.md`

**The fact it rests on:** the wake that worked had `--tools` and `--allowedTools`
absent entirely. A deny-list of six tools and no allow-list. **Writes were not
path-restricted at all**, read from the log's own argv.

**The defect still open:** the one allowance that HAS been proved,
`Edit(inbox/**)`, covers both protected folders and everything under them.

**What I propose:** narrow to a single reply directory, `Edit(inbox/_replies/**)`
— narrower than the protected folders rather than carved around them — with a
control that fails if the reply path could ever collide with a protected name.
**`protected_folders.txt` keeps exactly one enforcing reader.**

**AND I PUT THE DISAGREEMENT IN FRONT OF HIM RATHER THAN PICKING.** Architecture
asked for the launcher to read that file directly; he accepted my refusal of
exactly that. Both are on the record and they do not agree. **I would rather be
overruled in one line than build the wrong one carefully.**

## THE PART THAT IS GENUINELY HIS

**Step B cannot be proved without a real wake, and a real wake now hits the gate
I built this afternoon.** The switch does not exist, so `assert_switch_on`
refuses with 78 before the probe ever launches. It refused three times today.

**I am not adding a test exemption to it.** A switch with an exemption is not a
switch, and the first thing to use that exemption would be the thing I am least
able to predict.

**So he chooses:** create the switch by hand for a sub-minute window and remove it
(my recommendation), or hold step B until step H and let the brakes be built on
an unproven containment, or run the probe himself — **which I recommend against,
because rule 26 says handing him a terminal is the last resort and this is not
one.**

## COST, AND IT IS IN TOKENS BECAUSE DOLLARS ARE WITHDRAWN

**One probe run, not the letter step.** Measured from the one probe that has ever
run: **2 API calls, roughly 49,000 cache-read tokens summed across them, 20.35
seconds.** The context is about fifty thousand tokens re-read once per call.

The `--max-budget-usd 2.00` wall is on the command, unchanged, **and still an
untested brake — it has never fired and I am not claiming it works.**

## NOTHING ELSE MOVED

**No brakes, no doorbell, no second wake, no database, no deploy, nothing
committed, no ACL changed, the Looking Project excluded.** The switch file is
still absent, so the automation is still fail-closed by absence rather than by
setting.

**Tray reconciliation and the descendant ACL scan remain unstarted, in that
order.** He confirmed the nine letters I would not classify tonight are the right
ones to leave alone and to re-read when I get there rather than guess at now.
