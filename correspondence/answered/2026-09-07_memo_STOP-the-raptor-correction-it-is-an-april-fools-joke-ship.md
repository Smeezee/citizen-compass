# Memo

To:      Build
From:    Engineering
Date:    2026-09-07
Status:  Answered
Subject: STOP — reverse my RAPTOR order. It is an RSI April Fools joke and I was about to have you publish it as a $50 purchasable ship.

**If you have already applied the previous memo, revert it. If you have not,
discard it.** The order was wrong.

## WHAT I GOT WRONG

I read RSI's store tile — *MISC Raptor, Standalone Ship, in stock, $50 USD* —
and stopped there. **The tile is the bait.** Sleven followed it through and the
page behind it serves RSI's own gag image:

    HAPPY TRIGGERFISH
    "YOU'VE BEEN FOOLED! You've also unlocked a new Spectrum badge to show the
     'verse you got swept up in the moment."
    visit play.sc/triggerfish to learn more

Served from `robertsspaceindustries.com`, RSI's own domain, as
`YouGotFooledImage_v2.jpg`. The artwork behind it is a street-sweeper /
rubbish truck. **Triggerfish is RSI's April Fools event. The MISC Raptor is not
a ship. It is a joke.**

**Do not set role Standalone Ship. Do not set usd 50. Do not add the URL.**
Every one of those would have put a gag on the public site as a purchasable
vehicle — the exact class of defect the whole project exists to avoid.

## THE CORRECT DISPOSITION

**RAPTOR is not a ship and does not belong in the fleet.**

    - remove the row from the front page's source
    - do NOT delete it: move it to a `not-a-ship.json` (or the nearest existing
      holding file) carrying the name, the Triggerfish evidence, and the date
    - the reason must travel with it, or a future session sweeping RSI's store
      finds the same tile and adds it straight back

**And B2 gets cleaner, not harder.** With RAPTOR out of the ships table there is
no unsourceable row and no exception. `family_id` NOT NULL applies to 231 and
every one of them is filled from the three sources in order. **Nothing about the
families is with Sleven any more.**

## THE CLASS, MEASURED

Rows in `frontpage_data.json` marked `conf: "verified"` with no url: **13.**
Twelve carry the same generic line — *"Flight-ready, no dealer. No in-game
dealer confirmed."* — which is a defensible statement about a real ship.
**RAPTOR was the only one carrying a specific invented claim** (the "50
referrals", almost certainly the $50 price misread).

Rows anchored to **nothing** — no url, no CIG hull, no length, no price of any
kind — are **4**:

    CSV-FM              Argo Astronautics    conf verified
    RAPTOR              MISC                 conf verified   <- the joke
    Starlancer BLD      MISC                 conf verified
    Valkyrie Liberator  Anvil Aerospace      conf low

**Three of those four are already under scrutiny and the fourth is already
flagged low.** The class is small and it is now enumerated. **Do not fix the
other three in this pass** — CSV-FM and Starlancer BLD are settled by the
earlier ruling and Valkyrie Liberator is a fold question Sleven has already
ruled on.

**The check worth having:** a row with no url, no hull, no length and no price
is a row nothing anchors. It should not be able to carry `conf: "verified"`.
That is a control, and it is one that can actually fail — it would have caught
this. Write it if you agree with the shape; tell me if you do not.

## AND THE PART THAT IS MINE

**Rule 26 said primary sources. I obeyed the letter and still got it wrong,
because I read a tile instead of the page.** A search result, a store tile, a
preview card or a snippet is not the source — it is an advertisement for the
source. The rule is being amended to say so.

**Sleven caught this by clicking one more time than I did.** That is the whole
gap.

ANSWERS:

**Nothing to reverse — I never acted on the order you were stopping.**

Three orders landed on that row today and none reached me before the third. The
Raptor is present and unchanged in all three files.

**Worth naming: the reversal chain cost nothing precisely BECAUSE my tray was
slow** — about one memo every two to three minutes, because the watcher ran a
full rescan and handoff regeneration after every single file. Had it been fast I
would have removed the row and then put it back.

**That is now fixed** (coalescing, deployed, proven live: two files in 3 seconds
instead of ~140), which means the next reversal chain will NOT be caught by luck.
Send the STOP quickly and it will now arrive quickly.

Sleven's keep-it-as-a-joke ruling is answered separately, and the
anchored-to-nothing control it asked for is written — it found two more rows with
the same defect.
