# Update — Q53 is done. The front-page inventory is on disk.

**`docs/FINDING_the-front-page-inventory-2026-09-11.md`.** Every capability of
the old front page, marked PRESENT / ABSENT / CHANGED on `/next`, read off the
**served** origin in a real browser — not `_src`, not `_deploy`. Q53's
DONE-WHEN is met and **Q54 is unblocked.**

**A correction to my own previous update:** it signed off "01:2x", a placeholder
I left in after correcting the same slip in the update before it. **The probe
round finished at 01:13 CDT / 06:13 UTC.** Rule 18 twice in one night is once
too many; the times in the finding are the machine's.

## FIVE PROBES, EACH WITH A CANARY THAT PASSED

    checks/_diag_q53_front_page_inventory.mjs   census, gate, hash addresses
    checks/_diag_q53_round2.mjs                 fields, sorting, currency, strip
    checks/_diag_q53_round3.mjs                 marks, dealers, per-field gaps
    checks/_diag_q53_names.mjs                  the ship list, exact equality
    checks/_diag_q53_patchmark.mjs              where a patch mark could hide

**Each exits 2 if its canary comes back clean** — a capability known absent must
be reported absent, a name that cannot exist must be reported missing, a pattern
that cannot match must find nothing. All five reported their canary, so none is
a green light with no bulb in it.

## THE FOUR THAT MATTER MORE THAN THE LINKS

1. **The confidence note is gone for 203 of 253 ships.** The old page carries a
   CONFIDENCE / NOTES cell on **254 of 254** rows, 61 distinct texts, 165 of
   them *"Confirmed — starcitizen.tools 4.9.0"*. The new page carries a
   confidence sentence on 50 cards and **a patch number on 4** — and I probed
   rendered text, `title`, `aria-label` and every `data-*` attribute before
   saying so, because a mark can sit where a reader never looks. It does not.
   **The new page's own footer says "Every figure carries the patch it was
   checked against."** Measured against the cards it describes, that is not true
   of 249 of them. Reported, not fixed. Hard rule 20's ground, and not the same
   item as Q61.

2. **Nothing sorts.** Nine of the old page's ten columns have a sort handler.
   The new page has no sort control of any kind.

3. **One ship is on the old page and not the new one: `Valkyrie Liberator`.**
   The old page also carries `Valkyrie` and `Liberator` separately and both are
   on the new page. **Whether that is a drop or a name the old page should not
   have had is refused, not picked** (rule 19) — both are named in the finding
   and it is Q55's first job, and one lookup.

4. **Five side panels are absent** — DISPLAY, HELP, FEEDBACK, KEYBINDS, FIND IT.
   The whole accessibility overlay is the first: 7 presets, 6 fonts, 11 sliders,
   a CSS export box. **And the FEEDBACK panel holds `Send another response`,
   which is the reset-after-submission requirement Q55 already states as
   Sleven's own. It is built today and would be lost.**

## AND THE LINK HALF WAS RIGHT ABOUT THE LINKS, WRONG ABOUT ONE MEANING

**Three of the eight — `#dev`, `#calendar`, `#legend` — are CHANGED, not gone.**
`/next` carries all three as tab views and all three render. But the count could
not see the thing that is newly broken: **nothing on the new page has an
address.** A tab click writes neither `location.hash` nor `location.search`, and
`/next#dev` finds no element of that id. Any link already shared to `/#dev` or
`/#legend` stops resolving after a swap. **There is also a ninth absent link the
count missed:** the Spectrum thread `.../SC/forum/190048`.

**Two ships lose their ship page:** `AEGS_Javelin` and `ARGO_MOTH` link out to
RSI on the new page instead of to `loadout.html`.

## WHAT I DID NOT DECIDE, ON PURPOSE

**Nothing is marked keep or drop.** The finding separates the two items already
decided by Sleven or by rule 8 (the resubmit control, the trademark strip), the
two a swap decides mechanically whoever rules on the rest (an address for each
tab, and that `/next` serves **ungated** where `/` does not), and everything
else as his call. **The trademark strip differs in both directions and I have not
touched a character of it** — rule 8, reported.

## THREE THINGS FOR THE RECORD

- **`checks/_verify_deploy_drift.py` reported NOT PERFORMED**, not passed: its
  rebuild half needs PostgreSQL and `python-dotenv`, and `build_find_data.py`
  refused to build without them. It failed closed and restored `_deploy` and
  `_src` byte for byte. So this inventory describes **what is served** and says
  nothing about whether a rebuild would change it.
- **`checks/_verify_correspondence.py` is RED and exits 1**, on memos in
  `correspondence/open/owner/` that are addressed to Architecture and marked
  Answered while still sitting in an open tray. **Pre-existing, not mine, not
  touched** — flagging it because a red control should not sit unmentioned.
- `_verify_owners.py` and `_verify_rule16_labels.py` both pass with the five new
  files in place. The throwaway scratch script I used to find a selector went to
  `_to_delete/q53_peek_20260911/` rather than being deleted (rule 1).

**Nothing edited on either page, nothing deployed, nothing committed.**

*Code, 2026-09-11.*
