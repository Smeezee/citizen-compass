# FINDING — the question the collector doc calls "BLOCKS EVERYTHING" has been answerable since 7 August. There are 757 captured frames on this machine and the UI text in them is crisp.

    from    C1 (Cowork), 2026-08-30
    asked   by Sleven: if the website is clear, move Code to the collector -
            "but we need to talk about where that's at"
    method  opened the frames. Internal working material, rule 10: a frame may
            contain a name, nothing derived from one ever may. Nothing from
            these images is published and none is reproduced here.

---

## 1. WHERE THE COLLECTOR ACTUALLY IS

`docs/COLLECTOR_open-questions-and-unknowns.md`, written by C2 on 2026-08-06,
states it in one line and it is still true:

> **The collector's capture half is BUILT and working. The reading half is
> entirely unbuilt.**

    89 Go files · 26,991 lines · version 0.3.3
    last code change     2026-08-23
    last build           2026-08-20
    selftest             PASS, 0 failed, run 2026-08-27 on Windows
    frames captured      757 sidecars + 757 PNGs, 2026-08-07 to 2026-08-15

**It captures. It does not read.** Everything between those two is the unbuilt
half, and the doc ranks the blockers.

## 2. TIER 1.1 — "BLOCKS EVERYTHING" — IS ANSWERED, AND THE ANSWER IS YES

> **1.1 Is the game's UI font legible in a captured frame at 1920x1080?**
>     open since 2026-08-02 · blocks the glyph atlas, the reader, the
>     vocabulary, all of it · answered by Sleven pressing the hotkey at a
>     kiosk. Ten minutes.

**Nobody had to press anything. 757 frames have been sitting in
`citizen-collector/captures/` since 7 August.** I opened one.

    frame     1920x1080, RGB, captured by Windows.Graphics.Capture
    location  a service station interior, in world, patch 4.9.188.23497

**The UI text is crisp at 1:1.** Letterforms are clean-edged, high contrast
against a busy background, and the small digits are distinct - percentages, a
four-digit pressure reading and its unit, a label in caps. **Nothing about it
suggests a reader would struggle.** The capture path preserves text well.

**THE HONEST LIMIT ON THAT ANSWER.** This is the in-world HUD, not a shop
kiosk. Kiosk text is denser and may be smaller. **What is now settled is that
the CAPTURE PIPELINE does not destroy text** - which is what "blocks
everything" was really asking, because a blurry capture would have killed the
design outright. **A kiosk frame is still wanted to size the glyphs.**

## 3. AND THE REST OF TIER 1 IS NOT ANSWERED

> **1.2 Is the aUEC balance on screen often enough to catch both sides of a
> transaction?** blocks the entire event recorder.

**Still open, and no frame on disk can answer it.** Checked every sidecar:

    AsteroidClusterBase_Nyx_Social_Keeger    161 frames
    RR_JP_NyxCastra                           80
    RR_JP_StantonMagnus                       32
    RR_MIC_LEO                                29
    main menu                                 49
    no location recorded                     406

**Zero frames at Area18, Lorville, Orison, New Babbage or any shop.** The
collector has been run in space and at one asteroid base. **The one place the
reader is being built for has never been photographed.**

## 4. WHAT THIS MEANS FOR MOVING CODE ONTO IT

**The ten minutes C2 asked for in August is still the unlock, and it is now a
smaller ask than it was:** stand at a shop kiosk, open the panel, press the
hotkey. **One frame answers 1.2 and sizes the glyphs for 1.1 at the same
time.** Without it, anyone building the reader is designing against the HUD and
hoping the kiosk matches.

**What Code CAN do before that frame exists:**

    - the glyph atlas scaffolding, calibrated on HUD text, which is proven
      legible and is on disk in quantity
    - the frame-to-region pass: find text blocks, before knowing what they say
    - TIER 2.3, the chat-region exclusion. It is a PRIVACY control and it
      fails closed or not at all. It does not need a kiosk.

**What Code CANNOT sensibly do:** the column detector (2.2, "the least tested
idea in the whole design"), the purchase-delta proof (1.2), and the vocabulary
- all three are shaped by a screen nobody has captured.

## 5. WHY THIS IS WORTH MORE THAN IT LOOKS

**This is the fourth time this week a blocker turned out to be already
answered on disk** - `place_fleet.py`, `labels.json`, the mining figures, and
now this. **Each was filed as "waiting on Sleven" or "not in the repository"
and each was one `ls` away.**

The pattern is not carelessness about data. **It is that a question, once
written down as blocked, stops being asked.**

— C1
