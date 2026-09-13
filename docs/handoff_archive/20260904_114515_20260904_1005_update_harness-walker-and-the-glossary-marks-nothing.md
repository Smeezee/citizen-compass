# Update — the harness gets a walker; and the glossary explains nothing to anybody

**2026-09-04 · Code**

## The red control is green, and it did real work to get there

`_verify_picker_deployed.mjs`: **30 assertions passed**, including the B9 census
read from the served bytes - 6,019 markers, 4,174 clickable, 1,845 fixed, **0
silent, 0 hulls entirely silent (was 61)**. It had been dying before its first
assertion since the glossary was injected into the build.

`checks/_loadout_harness.mjs` (Code's) now provides `NodeFilter` with the real
DOM constant values and a `createTreeWalker`.

**The walker visits nothing, and the comment says so in those words.** This
harness has no text nodes - an element here is an `innerHTML` string plus a
shallow regex parse of child tags. A SHOW_TEXT walk over that visits nothing,
and that is a true statement about this DOM rather than a convenient one.
Writing a real one means giving the harness a genuine node tree with mutation
flowing back into innerHTML, rewriting a DOM thirty controls are written
against.

## I wrote a false justification into that comment and then tested it

My first version said this was safe because the glossary is proven elsewhere, by
`_verify_glossary_reaches.mjs`, "which counts the terms actually marked."

**I then ran that control instead of trusting my own sentence, and it is not
coverage.** It counts, and then declines to fail, in its own words:

    0 is not a failure here. Which terms and which containers is
    Architecture's decision, not this control's opinion.

The correction is in the file, kept rather than tidied away.

## The finding that matters more than the fix

That control's clean run, against the served site, today:

    loadout.html   impl=true  terms=31  MARKED=0
    index.html     impl=true  terms=31  MARKED=0

**The glossary is present on both pages, carries all 31 terms, and marks zero of
them. It explains nothing to anybody.**

That is the exact state `_verify_glossary_reaches.mjs`'s own header says it was
written after: *"Q35. Sleven asked for hover-and-tap explanations of shorthand.
The mechanism was written, sourced, and careful. It had never explained a single
word to anybody, on any page, and the site reported success the whole time."*

The mechanism now REACHES loadout.html - that half was fixed on 08-30 and the
control proves it. What it does on arrival is nothing.

**And it is green.** G1, G2 and G3 all pass; MARKED=0 is printed under a heading
that says REPORTED, NOT FAILED. Nothing in 118 controls would go red if the
glossary never marked another word.

I am not calling that a defect in the control - its scope argument is
defensible, and which terms get marked in which containers genuinely is
Architecture's decision, not a checker's. **But the combination is the thing
this project names:** a shipped feature doing nothing, a number that says so,
and a suite that is green.

**For C1 / Architecture, not for me to decide:** which terms should be marked,
in which containers, on which pages. Once that exists as an answer, MARKED=0
becomes assertable and this stops being a report.

Two consequences of the walker stub, stated so they are not discovered later:

- an inert walker costs nothing TODAY, because decorate() has nothing to do in a
  real browser either;
- **the day the glossary marks terms for real, the stub becomes a hole** -
  controls booting built pages here would keep passing while decoration silently
  did not happen under test. That is written into the comment, addressed to
  whoever does that work.

## State

Full sweep running against the harness change - thirty controls depend on that
file and none of them may be taken on trust. Nothing deployed since the leak
fix; the harness is not part of the payload.
