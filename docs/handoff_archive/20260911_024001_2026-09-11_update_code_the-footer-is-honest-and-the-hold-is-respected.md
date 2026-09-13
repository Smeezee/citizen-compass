# Update — the footer is honest, the upload is still held, and the regeneration carried a second change I did not author

**2026-09-11 02:40 CDT / 07:40 UTC. Nothing is uploaded.**

**Owner's 02:29 memo reached me before the upload, because he told me to check
the tray first.** It arrived four minutes after I started the second sweep. That
sweep was stopped rather than left running — the footer change moves the payload
fingerprint, so it would have been 31 minutes vouching for bytes that no longer
exist.

## THE SENTENCE

    was   "Every figure carries the patch it was checked against, and a blank
           means we do not know rather than a guess."
    now   "Verification is incomplete: most ships on this page do not yet show
           the patch they were checked against."

**Measured, not asserted:** 4 of 253 cards carry a patch number anywhere — text,
`title`, `aria-label`, or any `data-*` attribute. 249 of 253 do not, so "most do
not yet show" is true of the page as it stands.

**I did not use his example wording**, since he said it was not his wording and
any true sentence works. **And I did not claim the gap is being fixed** — that
would be a statement about Q55's future, which is not mine to put on a page.

**The trademark and disclaimer lines were not touched.** Rule 8. The strip is
byte-identical and I checked it rather than assuming: *"This is an unofficial
Star Citizen fan site. Ship imagery © Cloud Imperium Games. Star Citizen®,
Roberts Space Industries® and Cloud Imperium® are registered trademarks of
Cloud Imperium Rights LLC."* — unchanged. **Nothing was done about the
confidence notes**, which stay Q55.

## WHERE THE CHANGE WENT, AND WHY NOT WHERE THE SENTENCE WAS

**The sentence lived in three files and two of them are outputs.**
`OWNERS.md` is explicit: *"nobody edits `testing/_src/next.src.html` by hand,
including me. Changes go into the generator and the file is rebuilt."* So the
edit went into `tools/frontpage/build_next_frontpage.py` and the page was
regenerated. Editing the page would have been silently discarded by the next
generator run — which `OWNERS.md` records has already happened once.

**DELEGATION, recorded as required.** Order:
`correspondence/open/build/2026-09-11_memo_build_hold-the-q54-upload-until-the-footer-is-honest.md`,
From: Owner. Files: `tools/frontpage/build_next_frontpage.py` and its outputs —
**both C1's.** The order named the sentence rather than the path; the path
follows from where the sentence is authored, and I changed nothing else in that
generator. Originals are in `_to_delete/q54_footer_before_20260911/`.

## THE SECOND CHANGE, WHICH IS NOT MINE AND MATTERS MORE THAN THE FIRST

**I diffed the regenerated page against the old one to prove only the sentence
moved. Two lines moved, not one.** The other was the embedded data, and the
difference is one field on one ship:

    RAPTOR note, was   "Flight-ready, no dealer. Referral-program reward only
                        (50 referrals required) - not normally purchasable
                        directly. Included for completeness, not as a
                        realistic buy target."
    RAPTOR note, now   ""

Every other field on every other ship is identical — checked by parsing both
blobs and comparing them entry by entry, not by reading the diff.

**That sentence is being served right now.** `grep` on the live testing site's
bytes finds it. **C1 cleared it at the generator via `clear_note`, and the
generated page was never rebuilt, so the correction never reached the page.** It
took a regeneration for somebody else's fix to actually ship.

**So Q57's DONE-WHEN is satisfied in the page** — the RAPTOR's note is empty in
the source the front page is built from. The `price_corrections.json` half of
that item is not mine and is untouched.

**And it is the same defect shape as the one I hit two hours ago** with the
ASSEMBLED list: a fix applied in one place, a stale copy downstream, and nothing
that compares the two. The RAPTOR one is worse, because what the stale copy kept
serving was an invented claim about a ship that does not exist — hard rule 11,
on the live testing site, for however long the page has been stale.

## STATE

    footer            honest, measured, rebuilt from the generator
    RAPTOR note       empty, carried in by the regeneration
    trademark strip   untouched
    gate              still injected into the front door
    _redirects        `/ /next 200`, unchanged
    drift control     16 passed, 0 failed
    correspondence    exit 0 on the real tray
    memo closed       the reply-path answer went back through inbox/ with
                      Status: Closed, same filename, and the router filed it to
                      answered/ and superseded the open copy. open/build/ no
                      longer holds it.
    sweep             running against the new payload (sweep3.log)
    uploaded          NOTHING

**The freeze is noted and nothing touches the wake system.** No step C, no
doorbell, no activation. The archive entry recording where automation stands is
owed **after** Q54 is up, and it is not started, because he said when Q54 is
done and it is not done.

*Code, 2026-09-11 02:40 CDT.*
