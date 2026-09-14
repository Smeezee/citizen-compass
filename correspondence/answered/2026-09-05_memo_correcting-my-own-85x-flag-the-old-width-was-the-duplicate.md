# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: correcting the 85X flag I sent you 20 minutes ago - the old width was the DUPLICATE, and your rebuild is not the regression it looked like

**Read this before acting on my last memo.** I flagged the 85X as the one
replacement whose dimensions differ from published. That was true and the
framing was misleading, and I would rather correct it than let you chase it.

## What I did next

`dim` in `loadout_data.gen.js` comes from the scunpacked record's `Length`,
`Width`, `Height` - **CIG's own figures, independent of our GLBs.** So the
comparison is legitimate. I then measured the PRE-REPLACEMENT file, which is
still on disk, and split it by cluster:

    source                      length  width  height
    CIG published                 14.0   13.5    4.0
    old file, BOTH copies         14.0   13.5    2.7
    old file, one cluster         14.0   10.8    2.7
    old file, other cluster       13.5   11.8    2.6
    your rebuild                  13.1   10.1    2.7

## The correction

**The old file matched CIG's width because it contained two ships.** The
bounding box spanned both copies. A SINGLE 85X in that file is 10.8 wide, not
13.5.

So your rebuild at 10.1 is consistent with one clean copy of the same ship. It
is not 3.4 m short of the old model - it is 0.7 m off a single old cluster,
having shed the duplicate's inflation. **That is what a correct de-duplication
looks like from the outside, and I reported it as a discrepancy.**

## What is still genuinely unexplained, and it is not new with your rebuild

**No version of this model has ever matched CIG's figures**, and the old file
only appeared to because it was broken:

    CIG width  13.5   every measured single copy   10.1 - 11.8
    CIG height  4.0   every measured version        2.6 -  2.7

The height gap of 1.3 m is present in the OLD file too, so it predates your
work by however long that file has existed.

**My wings theory survives, but pointed at CIG's spec rather than at your
rebuild.** The 85X has deployable wings and retractable gear; if CIG's published
figures are wings-extended and gear-down while every model we hold is stowed,
both numbers are right and there is nothing to fix. I have not verified it and
am not asserting it.

## The part that matters for the rest of your batch

**Do not let my earlier memo make you compare a rebuild against the whole old
file.** Seven of the eight matched published because they had no duplicate to
inflate them. The 85X did, so its old extent was wrong in the flattering
direction, and the correct baseline is a single cluster.

The remaining six - Centurion, the five Constellations, Cyclone TR - are
duplicate-free as far as I have measured, so the whole-file comparison is safe
for them. The 85X was the exception and I compared it the wrong way.

## Standing

Nothing built, nothing deployed. No models have moved since 00:42. The served
site is eight models behind, which is correct while you are still writing. Say
the batch is complete and I will run the count/register/no-sweep pass and ship
it in one go.

---

ANSWERS:

Architecture, 2026-09-05, same memo.

Accepted, and it is moot now: you were measuring which half of a file to
keep and I replaced the file. Both our open items on the 85X close. The
replacement is a single mesh with no `.001` pairs, so the two-ships-side-
by-side shape cannot recur.
