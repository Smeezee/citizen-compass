# FINDING — the pages are clean and the source behind them is not. 1,114 comment blocks ship to every visitor, and in them one session tells another whose file it is.

    from    C1 (Cowork), 2026-08-29
    asked   by Sleven: nothing public may hint the site was built by anything
            other than a person - the interface above all
    method  all 7 pages rendered in a real browser and read text node by text
            node; then every comment in every served file, separately

---

## 1. THE ANSWER TO WHAT HE ACTUALLY ASKED: THE INTERFACE IS CLEAN

Seven pages rendered, every text node, `title`, `alt`, `aria-label`,
`placeholder` and `<meta>` read. **Nothing a visitor sees on screen names an AI,
a vendor, a model or a tool.** No generator meta tag. Nothing in the words.

I also ran the whole vocabulary list — delve, seamless, robust, leverage,
harness, elevate, unlock, streamline, cutting-edge, tapestry, testament to, dive
into, embark, plethora, myriad, meticulous, *in today's*, *it's worth noting*
and about twenty more. **Not one hit.** The only matches were the game's own
words: `Unlock All Doors`, `Copilot turret`, `Mk I`.

Three near-misses worth naming so nobody re-flags them:

    C1        28 times      the Crusader C1 Spirit
    Copilot   several       a real seat name in CIG's data
    DRACOWork three.js      it contains the letters c-o-w-o-r-k

## 2. AND THEN THERE IS Ctrl+U

    1,114 comment blocks - about 315,000 characters - in the served files
    45 traces in 12 files - EVERY ONE in a comment, NONE in the page

**One session talking to another, on a public URL:**

> *"it is C1's file and not mine to edit"*
> *"loadout can point at this file whenever C1 wants. IT WANTS."*
> *"Agreeing with C1's call here, not overriding it."*
> *"C3's brief proposed shipping ..."*
> *"C1/C2 gave every gun inside a turret its turret's position"*

**And the owner, quoted giving instructions**, in five separate files:

> *"Sleven, on the deployed page: 'is there a way to make them see through a
> little'"*
> *"Sleven's test: 'it needs to be very obvious what the page is'"*
> *"Sleven's decision of 2026-08-09"*

**Plus the machinery around it:** `ORDER_the-disclosure-bar-2026-08-27`,
`FINDING_fixed-hardpoints-derived`, *"rule 14"*, `build_deploy.py`,
`loadout.src.html`, and roughly a hundred work-item codes — `H1g-1`, `N11`,
`P3d`, `Q9`, `W3`.

**A stranger reading that does not conclude "a person built this carefully."
They conclude there is a process with named agents, numbered work orders and a
client being quoted.** Which is exactly what it is.

## 3. WHY THIS IS ONE PROBLEM AND NOT FORTY-FIVE

**Nobody should hand-edit 1,114 comments.** They are the best documentation this
project has and every one of them was written to stop somebody re-making a
mistake. **The mistake is not that they exist. It is that they are published.**

One step in the deploy build strips comments on the way into `_deploy` and
leaves `_src` untouched. **We keep the documentation and the visitor stops
reading it.** Filed as Q31; `build_deploy.py` is Code's.

**Two things the strip must not do.**

**`holo.html` carries three.js's MIT licence header** — `@license Copyright
2010-2021 Three.js Authors`. Removing it breaches the licence the library is
used under. Any block matching `@license` or `@preserve` stays, which is the
convention every minifier already follows.

**`_src` is not touched.** Stripping there would trade the documentation for the
privacy. Both are available.

## 4. THE CONTROL

`checks/_verify_no_agent_traces.py`. **RULE16: INDEPENDENT** — it reads the
bytes in `_deploy` and knows nothing about the sources or the queue they came
from, so a trace the build invents is caught even though no source contains it.

It reads **comments and visible text only, never data values**, because that is
where the false positives live and *a control that flags the ship list gets
switched off inside a week.* `--self-test` plants all seven kinds of trace and
catches all seven, then checks it stays quiet on five look-alikes including the
C1 Spirit, the Copilot turret and the MIT header.

**It exits 1 today. That is correct.**

## 5. THE ONE THING I AM NOT DOING ON MY OWN JUDGEMENT

The visible copy carries mid-sentence em-dashes, and **it is mine: I wrote most
of this copy.**

**I FIRST REPORTED 250, WITH 171 ON THE INDEX. THAT WAS WRONG.** I counted
rendered lines, and the index repeats the same eight strings once per ship, 254
times over. Counted once each:

    111   unique lines site-wide
     33   unique lines that are sentences at all
    ~20   where the dash is a writing habit rather than a separator

**Ninety of them are label separators** — `Cooler left — 23 fit`,
`Transponder — the game does not allow this to be changed` — doing a colon's
job. Rewriting those would make the interface worse. **A count that cannot tell
a label from a sentence is not a measurement, and I published one before I
looked at what I had counted.**

It is also just punctuation, used correctly. Rewriting 250 sentences would
change the voice of the site on my opinion rather than Sleven's, on a site whose
whole character is his. **Filed as Q32 and blocked on him.** Measured, shown,
not acted on.

## 6. THE LESSON

**I audited the thing I was asked about and nearly stopped there.** The
interface was clean in ten minutes. The instruction was *nothing should hint*,
and a hint does not stop at the rendered page — the source is one keystroke
away and it is the same publication.

**And what was in it was not a slip.** It is a year of careful engineering notes
that were never written with a reader in mind, published every time we deploy.

— C1
