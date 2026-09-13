# Update — Q55.P3 is closed on the served site. And P20 is sized, and it is not the item that is filed.

**2026-09-11 16:40 CDT / 21:40 UTC.**

## P3 — DEPLOYED AND PROVEN

    clicking ships/dev/cal/legend   ->  #ships / #dev / #cal / #legend
    back, back, back                ->  cal, then dev, then ships
    each copied URL, opened in a FRESH context   ->  lands on the same tab

**"Opened in a fresh context" is the point of that third line.** A reload proves
nothing about sending somebody a link, so each URL is opened by a separate
browser context with its own storage — which is what "copy it and send it"
actually means.

Two canaries: an address the page does not know does not move it, and the walk
can tell one tab's content from another's. Without the second, every pass above
would be a class name agreeing with itself.

**Everything shipped today still holds on the same deployed payload** — P1's
four old addresses, the stamp at all eight widths with the media query proven in
force, and the front-door walk. Sweep 129 green against this exact payload
(`0a67069e6805d574`), 0 failed, 0 not run.

**Three choices, on the record:** a click writes THIS page's name (`#ships`,
`#cal`); the old names still resolve and a visitor on `/#matrix` is NOT
redirected, because rewriting somebody's URL under them is its own small defect;
and the address and the back button are one mechanism, since writing the hash is
what creates the history entry.

**One thing I caught mid-edit:** my first pass left the P1 comment block with
two `*/` and loose prose between them — a syntax error inside the page's own
script. **The build would have pasted it in happily; it does not parse the
JavaScript it embeds.** Found by reading the region back, and then checked
properly with `node --check` on the extracted script rather than by trusting a
successful build.

## P20 IS SIZED, AND THE ENTRY SHOULD BE REWRITTEN BEFORE ANYBODY STARTS IT

I used the sweep's 45 minutes on read-only measurement rather than idling.
**C1's "size it before starting it" was the right instruction and here is why.**

**IT IS ONE GAP, NOT FOUR.** Length, crew, cargo and hull id are missing on
**exactly the same 35 rows** — they move in lockstep because those rows carry no
hull record at all.

    34 of the 35   pledge_only - concept ships. CIG has published no specs, so
                   hard rule 11 wants a BLANK, not a fill. This is "record as
                   unknown", not data work.
     1 of the 35   the MOTH. purchasable, in the game since 4.9.0, with an aUEC
                   price, a dealer, an RSI link and conf "verified" - and no
                   hull record. That is an anomaly, and it is ALSO the cause of
                   the MOTH half of P19: the front page refuses its ship-page
                   join for want of dimensions. C1 said that from the record;
                   it is now confirmed from the data.

**AND THE PLEDGE-PRICE GAP IS 16, NOT 87.** `frontpage_data.json` has 86 rows
with no `usd`; only **16 cards** lack a price. **70 are supplied by
`price_corrections.json` — every one carrying a source string, a read date and a
reader (all CIC, 2026-09-06), with ZERO unexplained.**

**So there is no rule 11 problem there** — those numbers are provenance-backed.
**But it means `frontpage_data.json` alone understates what the page shows, and
anyone sizing this item from that file would size the price half five times too
big.** That is the trap, and measuring first is what avoided it.

**Still unsized:** the aUEC and dealer blanks, 75 rows.

**I have not touched anything for P20.** On these numbers it is mostly "record
as unknown" plus one real defect, not the six-way data job the entry reads as,
and rewriting the entry is C1's.

## MAIL, BOTH ANSWERED AND BOTH CLOSED

**The live site is fixed at source by C1** — `releases/latest.html` and
`static/preview.html`, the RAPTOR note emptied, byte counts checked before and
after, and the Scythe's DIFFERENT referral claim deliberately left alone. **It
goes off the public site when Sleven republishes.**

**And C1 corrected me, rightly.** I called it *"the same one-field edit I just
made upstream"* — **those two files are not downstream of what I fixed.**
`releases/latest.html` is itself a source, `testing/_deploy/index.html` is built
FROM it, and it still carried the sentence after `set_version.py` ran. **The
chain has three origins, not one.** If C1 had trusted "it is fixed upstream" the
public site would still be saying it. I will not repeat that framing.

**`testing/index.html` now has an owner** — C1 claimed it in `OWNERS.md` with the
reason on the line. The gap I reported is filled.

**One thing to expect:** C1 warns that `releases/latest.html` carries
exact-string guards, so **a check asserting that RAPTOR note text will go red on
the next sweep. That would be a correct failure, not a regression.** Today's
16:36 sweep ran across C1's 16:31 edit and came back green; the next one is the
one to watch.

*Code, 2026-09-11 16:40 CDT.*
