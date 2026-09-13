# Update — Q57 is done at the source. And the PUBLIC site is still saying the invented sentence.

**2026-09-11 13:25 CDT / 18:25 UTC.**

## THE ORIGIN WAS NOT WHERE ANYBODY SAID IT WAS

Q57 warned that the audit named `build_frontpage_data.py` and that C1 had
checked and the string is not there. **The item also says the sentence lives in
`frontpage_data.json` "and behind that in the database". That is wrong too, and
it matters, because it sends the next person to the wrong place.**

**`build_frontpage_data.py` does not read the database at all.** It reads a
`SHIPS = [...]` literal out of **`testing/index.html`** — a 332 KB page file
last written 2026-08-02. The real chain is:

    testing/index.html  (SHIPS literal)
      -> build_frontpage_data.py
        -> frontpage_data.json
          -> build_next_frontpage.py  (+ price_corrections.json clear_note)
            -> next.src.html -> the front page

**The database is not in the front page's chain anywhere.** `seed.py` carries
the same sentence and feeds the database, which feeds the API — a second,
separate carrier.

**I proved the chain live before touching it:** re-running
`build_frontpage_data.py` reproduced `frontpage_data.json` **byte for byte**, so
the generator is current and regeneration was safe. That check is what made the
rest of this safe rather than hopeful.

## WHAT CHANGED

    testing/index.html    the RAPTOR's "notes" -> ""   (1 occurrence, asserted)
    seed.py               the RAPTOR's 'notes' -> ''   (1 occurrence, asserted)
    frontpage_data.json   regenerated. ONE row changed, ONE field: RAPTOR.note.
                          254 rows before and after, every other row and every
                          other top-level key identical - compared entry by
                          entry, not by reading a diff.
    price_corrections.json
                          "clear_note": true REMOVED from the RAPTOR entry.
                          The entry itself is KEPT, with its `was`, its `why`
                          and a line recording that the source was fixed on
                          2026-09-11, so nobody re-adds either the sentence or
                          the patch.

**Then the page was regenerated with no patch in play, and the note came out
empty.** `RAPTOR` is still on the page — role, status and 253 ships unchanged —
which is Sleven's ruling: it stays, as the joke it is.

**`next.src.html` came out BYTE-IDENTICAL to before.** The patch had been
producing exactly what the fixed source now produces, so **the published page
does not change and no deploy is needed.** Q57 is a source repair, not a visible
one.

**DONE-WHEN, both halves:** the note is empty in the source the front page is
built from, and `price_corrections.json` no longer carries a `clear_note` for
it. Six controls that read the changed files pass: roster, assets,
anchored-to-nothing, unreleased content, drift, display names.

## THE PART THAT IS NOT MINE AND IS WORSE

**The invented sentence is on the PUBLIC live site right now.** Fetched, not
inferred:

    https://citizencompass.netlify.app/   HTTP 200, 205,898 bytes
    "Referral-program reward only (50 referrals required)"   1 occurrence

It is baked into `releases/latest.html` and `static/preview.html`, **both C1's**,
and the live site is published by Sleven by hand. **So a page the public can
read asserts, in the site's own voice, that a ship which does not exist is
flight-ready and costs 50 referrals.** That is hard rule 11 on the public site,
and it is the same sentence Q57 exists to remove.

**I have not touched either file.** They are C1's and publication is Sleven's.
**Routing it to C1 rather than raising it as a question** — the fix is the same
one-field edit, and the republish is Sleven's call.

## TWO THINGS FOUND ON THE WAY, NEITHER ACTED ON

**1. `Valkyrie Liberator` is real, and this settles P18.** My Q55 entry said
somebody had to look rather than guess (rule 19). The answer was already on
disk: `price_corrections.json` carries it at **$375.00**, *"RSI store, Valkyrie
Liberator Edition. Same $375.00 as the Valkyrie"*, read on 2026-09-06 **by
Sleven himself**. So the ship exists and the new front page is genuinely one
ship short — it is a drop, not a name the old page should not have had. **P18
can be written as a restore rather than a question.** Routed to C1 with this.

**2. The Javelin and MOTH refusal is deliberate.** `build_frontpage_data.py`
prints *"refused joins (named, not guessed): ['Javelin', 'MOTH']"* on every run.
That is the origin of P19, and it is a refusal by design rather than an
accident — which changes how that entry should be written.

## NOT PERFORMED, AND SAID SO RATHER THAN PASSED

**I could not read the database.** `load_dotenv()` raised and `DATABASE_URL` is
not in the environment, so the connection fell back to localhost with no
password and was refused. **I did not go looking for credentials — rule 23 puts
those closed and I am not reopening them.**

So: the fix to `seed.py` corrects the DB's SOURCE, and **whatever rows the
database holds today are unchanged and unverified by me.** Correcting stored
rows is an importer or migration matter, not a hand edit — hard rule 3 says the
real database only ever sees `alembic upgrade head` and forward-only importer
runs, and I have not sent it anything.

## OWNERSHIP, DECLARED RATHER THAN ASSUMED

    testing/index.html    NO OWNER in OWNERS.md. Edited because it is the real
                          origin and Q57 told me to find it and fix it - but
                          the gap is real and should be filled by C1.
    seed.py               Code owns the SCRIPT. OWNERS.md says that if the
                          SHIPS LITERAL is what is being edited, "that is a
                          data decision and it comes to Architecture first."
                          **It came from Architecture**: the 2026-09-07 memo
                          says in its own words "Delete the '50 referrals'
                          note", and Q57 is C1's queue entry for it.
    frontpage_data.json,
    price_corrections.json
                          C1's directory. Both named by Q57's own DONE-WHEN,
                          which is the delegation.

*Code, 2026-09-11 13:25 CDT.*
