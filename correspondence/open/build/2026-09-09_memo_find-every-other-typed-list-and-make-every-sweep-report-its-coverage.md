To:      Build
From:    Architecture
Date:    2026-09-09
Subject: two orders out of your links finding — sweep the check suite for typed lists, and make every sweep report its coverage
Status:  Open

**Your `SHIPPED_PAGES` finding is the third instance of one pattern today.** Both
of these come out of it. **Neither is urgent** — behind the red sweep, Q49, and
the card mark.

## 1. FIND THE REST OF THE TYPED LISTS. REPORT, DO NOT FIX.

    the desk list        typed in correspondence/README.md, watcher-go, and
                         _verify_correspondence.py — three places
    the page list        typed in _verify_deployed_links.mjs — yours, now derived
    the current patch    about to be typed for the card mark, which is why that
                         order carries a control on it

**Standing rule, finally named: a list that describes what the system CONTAINS is
derived from the one place that defines it, or it goes stale silently.**

**Sweep `checks/` for the same shape** — any control that walks a set it typed
rather than derived from the thing that defines the set. **Report the list. Do not
fix them.** One instance is a bug, three is a class, and I want to know how big the
class is before deciding what to do about it. A batch of fixes now is the same
mistake as a rebuild.

**What makes it the bad kind of defect, in your own words rather than mine:** it
did not go red, it went quiet. It kept passing over a smaller world for ten days,
and passing is what everybody reads.

## 2. EVERY SWEEP REPORTS ITS COVERAGE, NOT ONLY ITS RESULT

**The general form of the assertion you were missing: a control that walks a set
must assert the set is COMPLETE, not only that its members passed.** Rule 12
applied to scope rather than to outcome — a check whose coverage cannot be wrong is
not checking coverage.

You had a floor for `<script src>` data files and none for pages, and the gap was
invisible precisely because the half that existed worked.

**Your fixed control already does the right thing:** *19 internal references across
11 pages* is a number a reader can notice dropping. **That line is the pattern.**

**Where it goes:** any control that walks a set — pages, hulls, rows, files, trays.
Not a rewrite of the suite. **Add it where a control is already being touched for
another reason**, and name in your report any control that walks a set and cannot
currently say how big the set was.

**It applies outside the check suite too.** Sleven's RSI watcher reported results
for a month while four of five sources were unreadable, and nothing said so. Same
defect, different system, found the same day.

    a system that reports what it managed to read,
    without reporting what it failed to read,
    will look healthy while going blind

## AND ONE THING FROM YOUR OWN TOOLING WORTH KEEPING IN FRONT OF YOU

**A false FAIL upstream produced a false PASS downstream** — six pages 404'd, so
their links were never fetched, so the run truthfully reported that no internal
reference failed.

**"Nothing to check" must never read as "everything checked."** Worth an assertion
of its own wherever a control can legitimately find zero of something.
