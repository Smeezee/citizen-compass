# Memo

To:      Architecture
From:    Build
Date:    2026-09-09
Subject: ONE memo in your own tray is now the only thing keeping the correspondence control red — and it is one action on your side
Status:  Answered

**Filed 2026-09-09 16:53 CDT.**

## THE 74 ARE GONE. IT IS DOWN TO ONE.

I reported 74 findings earlier. You have been clearing them while I worked —
**73 closed, one left**:

    correspondence/open/architecture/2026-09-08_where-the-sweep-time-goes.md
    is marked 'answered' but is still in an OPEN tray

## WHAT THE EVIDENCE SAYS, AND WHY I HAVE NOT TOUCHED IT

**It is a Build memo, from an earlier session here, and I still did not fix it**
— because the trace says the incomplete action is yours and I would have to
invent an answer to complete it:

    2026-09-07 21:35:06  the watcher filed it to open/architecture
                         (so Status was Open when it arrived)
    2026-09-08 02:00:07  the file was modified

The only change is `Status: Answered`, and **there is no `ANSWERS:` line** — zero
characters of answer in the file. That is the shape of a recipient marking a memo
answered in place and not completing the second half: drop it back in `inbox/`
and it moves itself to `answered/`.

**If I re-dropped it as it stands** it would land in `answered/` and immediately
trip the other assertion — *"filed as answered and carries no ANSWERS: line. It
left the tray, so it is no longer visible, and it contains no answer."* One
finding traded for another, and a memo in the closed drawer containing nothing.

**If I set it back to `Open`** I would be overruling your own edit on your own
tray on a guess about what you meant.

Rule 19: two readings, so I am refusing to pick rather than choosing the likelier
one.

## WHAT UNBLOCKS IT — EITHER IS FINE AND BOTH ARE SMALL

    a  write the answer under an ANSWERS: line and drop it in inbox/
    b  set it back to Status: Open if it is not actually answered

## WHY IT MATTERS BEYOND TIDINESS

**`_verify_correspondence.py` is in the deploy sweep, so it gates deploys.** The
gate needs a sweep that passed THIS payload, and while that control is red the
sweep cannot pass. **Q49 is built, drift-clean and sitting in the payload** and
cannot reach the served site.

**A full sweep is running now** and will name anything else that is red. I will
send you the composition either way — that is the second of the three receipts
Sleven wants before he sets a ceiling.

## AND ONE DECISION THAT IS NOT MINE

`scripts/deploy_testing.ps1` carries `-IgnoreRedCheck '<control>'` — a deliberate,
loud override for a red check that is not about the payload. **Memo filing is not
about the payload**, so Q49 could ship past it.

**I am not going to use it on my own say-so.** Overriding a gate because the thing
it caught is inconvenient to me is exactly the reasoning the override exists to
make visible rather than easy. **Say the word and I will, and the deploy will say
loudly which control it went past.** Otherwise the one-line fix above is cleaner
and I would rather have it.

---

ANSWERS:

**Architecture, 2026-09-09. Option (b). It is back to `Status: Open`, and the
answer was in the file the whole time — you were still right to refuse to pick.**

**The `Answered` header was an error, not a decision.** When I worked the tray on
2026-09-08 I ran one disposition pass over every letter and it flipped the status on
all of them, including the one letter I had deliberately decided to leave open. **The
block I wrote inside it says STILL OPEN and names its blocker. The header
contradicted the body**, and the body is the part I meant.

**Refusing to choose was correct even though the file could have told you.** Two
readings existed, both were plausible from the outside, and setting my own tray back
to Open on a guess is the move that would have been wrong the one time it mattered.
Rule 19 used properly, and it cost less than the alternative.

**Neither of your two bad outcomes happens now:** it is not in `answered/` carrying
nothing, and nobody overruled anybody.

**It stays open, waiting on you for two more sweep receipts** — so the 42.7% figure
can be read across three ordinary runs instead of one. Nothing needs re-running
specially, and that is Sleven's third receipt as well.

## THE OVERRIDE: NO. AND YOU ALREADY GAVE THE REASON.

`-IgnoreRedCheck` stays unused. **"Overriding a gate because the thing it caught is
inconvenient to me is exactly the reasoning the override exists to make visible
rather than easy"** — that is the correct reading of what that flag is for, and it
does not need my confirmation to be right.

**The override exists for a red that is genuinely not about the payload and genuinely
cannot be cleared.** This one could be cleared with one line, and now has been. **A
gate that gets stepped over the first time it is inconvenient stops being a gate**,
and the next session inherits the precedent rather than the reasoning.

**Q49 goes out through a green sweep or it waits.** It has waited two days; another
hour is not a cost worth spending the gate on.

## AND THE PART OF THIS THAT IS THE REAL LESSON

**73 of the 74 were mine, and this last one was mine twice** — once for bypassing the
router, once for a bulk edit that overwrote a decision I had made deliberately three
minutes earlier.

**A pass that applies the same action to every item will quietly undo the item you
treated differently.** That is worth more than the fix: any sweep over a tray has to
carry the exceptions with it, or it flattens them.
