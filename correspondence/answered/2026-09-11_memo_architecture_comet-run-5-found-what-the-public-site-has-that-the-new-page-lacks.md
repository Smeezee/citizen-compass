# Memo

To:      Engineering
From:    Owner
Subject: The last outside review is in. Here is what the public site has that the new front page lacks.
Status:  Closed

The full review is on disk: `claude/RESULT_comet-run-5-comparison-2026-09-11.md`. It compared
the new front page (A) with the public site (B) on the same tasks. 22 findings, 19
CONFIRMED. This closes the five-run review; runs 1 to 4 are filed beside it.

## THE POINT TO GET RIGHT

Comet judged a first-time visitor would trust the public site more, because it puts one price
and a "Confirmed — starcitizen.tools 4.9.0" tag in the same row. That trust is partly false:
4.9.0 is a patch the game left in late August, and run 2 found the same site calling the
Idris-P price "confirmed" while its own Legend says it is in conflict.

So carry over where the public site puts trust — beside the price, no clicks — and not what it
claims. That is the per-row confidence note at the top of the Q53 inventory, and it must only
say what is true.

## CHECKED AGAINST THE DEPLOYED FRONT PAGE BEFORE SENDING

On the public site and missing from the new front page:
1. **C-013:** the "General 2026 outlook" and "Known non-purchasable ships" paragraphs
   (Development Progress). Not in `next.html`.
2. **C-015:** a link to the official patch notes. Not in `next.html`.
3. **C-018 / T-002:** no link from the front page to the item and commodity price tool. The
   only route is three levels deep on a ship page.

## FROM THE REVIEW, NOT RE-CHECKED BY ME

- C-014: the public table shows every dealer for every ship at once; the new page shows one
  location line per card.
- C-016: the public list links every ship to its RSI page; the new list does not, except for
  concept ships.
- C-017: 19 searchable categories on the public site against 12 buttons on the new page. Read
  it together with T-003, the Ground button that hides most ground vehicles.
- C-002: 253 ships on the new page against 254 on the public site. One ship is missing and
  nobody has said which or why.

## ALREADY ROUTED

C-001 = T-009 (two prices). C-003 and C-021 re-find T-008 (the patch badge read as price
verification) independently, which raises its priority. C-005 and C-006 = the feedback route,
already ruled.

## WHAT I WANT

Queue entries for the new items, one per item, with C-002 first (a missing ship is a data
question, not a layout one), then 1 to 3 above. These are gaps against the page the new one
replaces, so they belong in the Q53 inventory. Bring me only anything that needs my
keep-or-drop.

---

ANSWERS:

**Architecture, 2026-09-11. Filed, and C-002 is closed rather than queued — I traced it
before filing it, off the public site's own data.**

## C-002 IS CLOSED. NO SHIP IS MISSING.

**You put it first because a missing ship is a data question rather than a layout one.
It is a data question and the data answers it.**

Counted from the SHIPS array in `releases/latest.html`, the published page itself:

    254 entries, 254 unique, zero duplicated names
    and it carries THREE separate rows:  Liberator  |  Valkyrie  |  Valkyrie Liberator

**253 against 254 is the `editions.json` fold, the same cause Build traced for P18 this
afternoon.** `build_next_frontpage.py:74` drops any row named as a `from_row`, and that
file has exactly one entry. **The Valkyrie card renders the Liberator Edition line, and
searching "valkyrie liberator" returns it.**

**Nothing to restore, nothing to queue.**

## AND THE SAME LOOKUP ANSWERED THE QUESTION UNDER IT

**P27 was blocked on "are the other editions separate cards?" It is not blocked any
more.**

    edition-style ships as SEPARATE rows on the public site     6
      600i Executive Edition    Avenger Titan Renegade
      C8X Pisces Expedition     Carrack Expedition
      F8C Lightning Executive   Gladius Pirate
    folded onto a parent on the new page                        1
      Valkyrie Liberator

**The other six survive as cards on the new page by arithmetic rather than assumption:
254 − 253 = 1, and the one is the Liberator.**

**So the fold is applied to exactly one of seven similar ships.** That is the whole of
P27 and it is one question in your tray.

## THE REST ARE FILED AS RELEASE BLOCKERS

Per your other ruling — the public site is replaced whole, so every gap is a blocker.
**C-013, C-015 and C-018 as their own entries. C-014 is P21 with its status changed
rather than a second entry. C-016 and C-017 filed with the entries they must be read
beside** — C-016 with P23 and T-020, C-017 with T-003 and P9, because **three entries
now land on that one control and whoever touches it needs all three.**

**C-018 / T-002 is resolved to KEEP** by your "fix everything" letter, which closes
P55.P16's keep-or-drop.

## YOUR TRUST OBSERVATION IS THE SHARPEST THING IN THE LETTER AND IT CHANGED P5

**You caught the trap in Comet's own judgement before I read it.** The public site is
judged more trustworthy and is the less accurate page — 4.9.0 is a patch the game left in
August, and run 2 found that same site calling a price *confirmed* while its own Legend
says the price is in conflict.

**So P5's DONE-WHEN now carries the distinction in your terms:** carry over WHERE the
public site puts trust — beside the price, no clicks — and never WHAT it claims.
**A confidence note that is present and wrong is worse than absent, and the public site
is the proof.**

## C-003 AND C-021

**Not filed again. They raise T-008's priority instead.** Three reviewers finding the
patch badge independently is the strongest signal in the whole set, and it is already
first in the order.

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.** C-002 accepted as closed; the edition fold is now one question in my tray.
