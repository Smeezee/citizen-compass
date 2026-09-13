# Memo

To:      Owner
From:    Architecture
Subject: The false Raptor sentence is fixed in both files and only a republish stands between it and the public site — that part is your hand
Status:  Closed

**One action needed from you, and it is the only thing in this letter that is yours.**

## THE PUBLIC SITE SAYS SOMETHING THAT IS NOT TRUE, RIGHT NOW

    https://citizencompass.netlify.app/
    "Flight-ready, no dealer. Referral-program reward only (50 referrals required)
     - not normally purchasable directly."

**About the RAPTOR — which has no game file, no model, and is a deliberate April Fools
joke entry.** The page asserts in the site's own voice that it is flight-ready and names
a price for it. **Hard rule 11, on the one surface strangers can read without a
password.**

## FIXED IN BOTH FILES. VERIFIED BY CONTENT, NOT BY INTENT.

    releases/latest.html    204,481 -> 204,309 bytes
    static/preview.html     285,319 -> 285,147 bytes

The RAPTOR row's note is now empty — the same one-field edit Build made upstream this
afternoon. **I checked that the Scythe's separate referral sentence survived untouched;
it was one careless pattern away from going with it.**

**These two are NOT downstream of what Build fixed.** `seed.py` and `testing/index.html`
were corrected at 14:53 and the sentence was still in both of these at 18:00.
`releases/latest.html` is itself a source — the deployed index is built from it.
**Fixing the origin did not reach the public site and could not have.**

## WHAT IS YOURS

**Republish the live site from Netlify Drop.** Until you do, the sentence is still
public. Nothing else about the site changes — the edit is one empty field.

**I am not asking whether to do it.** It is a false claim on a public page under your own
standard from this morning. **I am telling you the fix is finished and waiting on the
one step no desk can take.**

## WHAT IS NOT YOURS AND IS ALREADY HANDLED

`testing/index.html` had no owner in `OWNERS.md` — Build found it while fixing Q57.
**Claimed by C1, with the reason on the line: it holds the ship-facts literal the front
page is built from, so it is an origin and not a leftover page.** Nothing needed from
you.

---

## QUESTIONS

1. Republish the live site from Netlify Drop when you are next at the machine — is there
   anything you want checked on it first, or should it go as it is?

---

CLOSED:

**Owner, 2026-09-11. Answered and closed. No republish.** The live site is replaced whole once the test site is finished, so it is not being repaired in the meantime. The fixed files stay fixed and ride along if a republish ever happens for another reason. The sentence stays public until the swap; that is my decision and I know the duration is not days.
