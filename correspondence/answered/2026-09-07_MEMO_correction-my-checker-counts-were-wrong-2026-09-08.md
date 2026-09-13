# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: correction — the numbers in my visual-checks memo this morning were wrong
Status:  Answered

The memo I sent earlier today, "twenty-one visual checks already exist and not one of
them is registered," carried a false claim. Sleven told me to verify my own
arithmetic and it did not survive. Correcting it before anyone acts on it.

## What I said

"Seventy-four are `_verify_*` modules registered in `CHECKERS` and run on the schedule
by `run_checks.py`."

## What is actually true

There are **73** `_verify_*.py` files, not 74, and **none of them is registered**.
Only one file anywhere in `checks/` imports a `_verify_` module, and that is another
`_verify_` script. They are standalone scripts, run by hand, once.

The registered total is **36**, counted by parsing each module's `CHECKERS` list:

    file_checks      16
    node_checks       2
    db_checks         7   (schema_checks' two are re-exported through it,
                           so they are inside this 7, not additional)
    shop_checks       6
    source_checks     4
    network_checks    1

So my headline — the data layer has seventy-four permanent eyes and the visual layer
has none — was a false comparison. The `_verify_` scripts are in the same throwaway
category as the `_diag_` ones. Visual work is not being singled out.

## What survives, and is stronger for being checked

**Ninety-four single-use scripts against thirty-six permanent ones.** 73 verifications
plus 21 diagnostics, each written to answer one question on one day, against 36 things
that run again tomorrow. That is a much larger pattern than the one I claimed, and it
is not a design-desk observation — it is yours to rule on.

**Not one of the thirty-six looks at a rendered page.** Checked across all seven group
modules: none mentions Playwright, Puppeteer, Chromium or headless anything. The two
in `node_checks` are the export round-trip and mutation harnesses, which need `node`,
not a browser.

So the narrow claim holds. Nothing that runs on a schedule has ever looked at what the
site actually renders, and everything that has looked, looked once.

## What does not change

The ask is the same: a ruling on whether a browser-driven visual check may be a
registered checker, and if yes, register three existing `_diag_` scripts unchanged as
the cheapest possible proof. Build owns that change.

`claude/DESIGN_ten-eyes-2026-09-08.md` has been rewritten with the corrected counts
and states the error rather than quietly fixing it.

I published a number I had glanced at rather than counted. The method that caught it
is the one Sleven set today — look again from another angle — and it caught it on the
second angle, not the first.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed. Publishing the correction yourself is the standard here** and it is worth more than the counts were. A desk that corrects its own numbers before anybody catches them is the only kind whose numbers can be used without re-checking.
