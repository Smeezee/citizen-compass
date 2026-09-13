# FINDING — the collector can read a shop screen. Proven tonight, on captures taken in August.

**C1, 2026-09-06.** This is the first brick of the collector and everything above
it was resting on an assumption. It is no longer an assumption.

---

## What was proven

A shop terminal frame from `citizen-collector/captures/`, read by machine, with
every name matched **exactly** against CIG's own display strings from
`labels.json` — 50,707 of them.

**Item names it read off the screen:**

    QuikCool          a cooler
    LightBlossom      a weapon
    LightFire         a weapon
    Marlin
    Canister, Fuse, Attachment

**Places it read:**

    People's Service Station Delta
    Nyx Gateway
    Platinum Bay

**Money it read:** 230,400 · 44,000 · 57,750 · 27,516 · 20,900 · 11,550 · 4,620

**And the wallet balance, on the same frame as the prices** — which is the money
check the whole provability argument depends on, available in one capture rather
than two.

**No fuzzy matching anywhere.** A name is kept only when a run of words equals a
CIG display string after case-folding. Rule 17 holds, and so does Sleven's ruling
of 2026-08-30: *"the reader is made good enough that it does not need the crutch."*

## The settings, and they were measured rather than chosen

Exact CIG-name matches on the same two frames:

    plain, full size          9        masked                    3
    2x upscale               16        2x upscale + masked      13
    psm 4                     2        psm 11                   12

**Upscaling wins because the game's UI font is small and the reader is trained on
document-sized text.** Masking loses a little on a clean shop frame and gains a
lot on a frame with the debug overlay across it — 0 names to 8. Both are kept:
**2x upscale, overlay masked, psm 6.**

**The debug overlay had to be masked and that is a finding, not a convenience.**
`r_DisplayInfo` prints a wall of tiny text down the top right and whole-frame
reading turns it into noise that swamps the shop panel. It is still valuable — it
names the location in plain text — but it is a **separate read at a separate
scale**, never mixed into the item list.

## Three things this does NOT do, stated plainly

**1. It reads names and prices but does not pair them.** The reader can see
`LightFire` and `57,750` on one frame and cannot say they belong together.
Pairing needs the layout — where on the screen each sits — not just the text.
**Until that exists there is no price row, only a bag of names and a bag of
numbers.** That is the next brick, not this one.

**2. A 50,707-word vocabulary produces false hits.** `Opal`, `Patti`, `Angie`,
`Natale` came back as matches and are almost certainly OCR noise landing on a
real string by chance. **A bigger vocabulary is not a better one.** The fix is to
narrow it to what a shop of that kind can actually sell, and to require a match to
sit where an item name sits — both of which need the layout work above.

**3. Volume is matched as a word and its number is not captured.** The screen
says `Volume: 2500 µSCU`; the pattern expected a form the reader does not emit.
Small, and unfixed.

## What it is worth

**The reading half of the collector is no longer a question.** It was open from
2026-08-02 and every design above it — the fact store, the observations table,
the learning — assumed it without evidence.

**And it needed nothing new.** No hardware, no model, no service, no permission.
The captures were taken in August, the vocabulary was sealed in the snapshot on
27 August, and the reader is installed on the machine already. **Three things
that were called blockers this week were all sitting on the same disk.**

## Where it lives

`tools/collector-reading/read_shop.py`. It reads, prints and writes nothing.
Every frame it reports carries the patch, the time and the trigger from the
capture's own sidecar, and a frame with no sidecar is refused rather than read.

*C1, 2026-09-06.*
