# FINDING — the largest honesty defect on the board is not a defect

**C1 (Claude-09), 2026-09-13, 03:1x CDT. Found by checking before building, on a job Sleven had
already said go to.**

## WHAT THE RECORD SAID

Three documents carry it in the same words — `NEXT.md` under Q62.T-011, the outgoing C1's
handover, and the C1 boot prompt itself, where it is listed under **"looks settled and is not"**:

> **116 rows show one price beside a list of shops.** Sized, entered, nobody working it, and it
> is the largest honesty defect on the board — the exact thing this site exists to fix.

I brought it to Sleven as the answer to *what is next*, split into a free half and a large half.
**He said go.**

## WHAT IS ACTUALLY THERE

Counted out of the deployed `testing/_src/next.src.html` DATA blob, 253 rows:

    purchasable                                   179
      with a per-dealer price map (dp)             63
      without one                                 116
        of those, carrying ONE dealer             116
        of those, carrying MANY dealers             0

**All 116 have exactly one dealer. Not a list. One.**

`shopLine()` renders them as `at <b>New Deal</b> · Lorville`. **One price, one shop, one place.
That is not an implication. It is the complete and honest statement of what we know.**

**The misleading shape — a price beside several shops with no per-shop price — occurs zero
times.**

## AND THE 63 ARE HONEST TOO, WHICH IS THE OTHER HALF OF THE CHECK

**60 of the 63 carry more than one dealer**, so `dl` demonstrably holds a list whenever a list is
known. **The pipeline is not truncating anything.**

On **47 of the 63** the dealers genuinely disagree, median spread **5.3%**, maximum **10.5%**. The
card already handles it: it names the cheapest dealer and prints `+N at <the dearer one>`, or
`same at N shops` when they agree.

**`a` is the cheapest dealer's price on every dp row checked** — not a separate reference figure
floating above two real ones. That was the thing that would have made it genuinely dishonest, and
it is not what is happening.

## HOW THE WRONG NUMBER GOT INTO THREE DOCUMENTS

**The count was right and the sentence attached to it was wrong.**

The inventory counted rows with a price and no per-dealer price map: 116. **True.** The entry then
described those rows as *a price beside a list of shops* — **without ever checking how many shops
each one has.** Nobody re-derived it, and it propagated into the handover and then into the boot
prompt, where it acquired the authority of a standing warning.

**This is the fifth instance of one pattern this week**, and his own words for it are already a
standing rider in `design/ANGLES.md`:

> the front page's data is a narrow projection of a much richer dataset, and we keep reading the
> projection and calling it the project

**This one is the mirror image of the other four.** The others read the projection and reported
something missing that the deeper dataset held. **This one read a count out of the projection and
attached a claim to it that the projection itself disproves in one query.** Same root: a number
was not asked what it contained.

**And it survived three rewrites because each desk inherited the sentence rather than the
measurement.** The boot prompt's own line — *EVERY SWEEP CARRIES ONE ROW WHOSE ANSWER IS KNOWN
FROM OUTSIDE THE SWEEP* — is the control that would have caught it, and no sweep was ever run on
this entry at all.

## WHAT IS LEFT, AND IT IS A REAL JOB WEARING A DIFFERENT NAME

**For 116 purchasable ships we know exactly one shop.**

**Whether that is the truth or the limit of what we ever recorded has never been asked.** Some
ships genuinely sell at one place. Some almost certainly do not.

**That is Research and data completeness. It is not display, not wording, and not honesty** — the
page is already saying exactly what we know. And **it must not be sized off the front page**,
which is the projection.

**Not opened as a job here.** Sizing it is itself a piece of work and it belongs to whoever asks
the upstream dataset, not to whoever reads the card.

## ONE COSMETIC THING, RECORDED AND NOT ORDERED

`shopLine()` uses `<s>` and `<u>` as styling hooks, with `text-decoration:none` restoring them in
CSS. **`<s>` means "no longer accurate" in HTML** and a screen reader may announce the place name
as struck-out content. **Cosmetic and accessibility, not correctness. Not a job.**

## WHAT I DID WITH IT

- **`NEXT.md` Q62.T-011 corrected in place** with the measurement, the counts, and how the wrong
  sentence got there. The old wording is quoted in the correction rather than deleted.
- **The recommendation to Sleven is withdrawn in his tray.** He said go to a job that does not
  exist, and he is told before anything was built.
- **Nothing was built. Build was told not to start it before he answered, and never did.**

*C1 (Claude-09), 2026-09-13.*
