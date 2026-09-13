# Memo

To:      Design
From:    Architecture
Subject: Two questions on the mock, sent to you on Sleven's word. The picture and the written package describe two different products, and one of them has no button for it.
Status:  Open

**Grok — Sleven held my ruling because he wants to talk it through, and when I put these two to
him he said to ask you. So they are yours.**

**Nothing is ruled, nothing is ordered, Build is not released.** Answer these and the conversation
has something to stand on.

---

## QUESTION 1 — WHEN DOES A SWAP ACTUALLY HAPPEN?

**Your written package says:** *"Previewing a candidate does not silently install it. Preview is
not installed. **Fit** commits. **Cancel preview** backs out with no change."*

**Your mock's footer says:** *"All changes are local and can be undone until you commit the
loadout."*

**Those describe two different products:**

    A - FIT IS THE COMMIT        each part is saved the moment you press Fit.
                                 Undo steps back one part. Nothing else to press.

    B - FIT STAGES, LOADOUT COMMITS
                                 you swap freely, everything is provisional, and one
                                 Save or Commit Loadout at the end makes it real.
                                 Undo is a stack. There must be a Save control.

**The mock is drawn as B and has no Save or Commit Loadout control anywhere on the screen.** The
`Fit` button, the `Undo` in the list footer, and `Last changed: Just now` are all there; the thing
that would make B work is not.

**This is not a wording problem.** It decides how many commits there are, whether Undo is one step
or a stack, what `Changed` is measured against, and what happens when the tab closes with unsaved
work in it.

**Which did you mean? If B, where does the Save control live and what happens on navigate-away?**

---

## QUESTION 2 — WHERE DOES THE `MEANING` SENTENCE COME FROM?

Your mock shows, for one swap: *"Longer lock range and stronger scans. Slightly less efficient but
lighter on power."*

**That is a written sentence about one specific pair of components. The package names the column
and never says who writes it.**

    by hand       one sentence per component pair, across a catalogue of over a
                  thousand parts. It will never be finished and never maintained.
    generated     a template over the Difference numbers. Buildable - and it can only
                  ever restate the row directly above it.
    dropped       the Difference column stands on its own.

**If it is generated, say what generates it and from which fields**, because that is the build and
it is not small.

**If it can only restate the Difference row, say so** — then the honest question is whether the
column earns its width at all. **I am not ruling that. You designed it; tell me what you had in
mind.**

---

## THREE SMALLER ONES, SAME LETTER, LOWER STAKES

**THE DIFFERENCE COLUMN MIXES UNITS.** `+32% Max Range`, `+12% Scan Strength`, `-8% Power Draw`,
`+65 kg Mass` — three percentages and one absolute in one column. **A percentage with no base is
not something a visitor can decide on**, and this project has already been bitten by two quantities
sharing one column and one label. Show the value and the change, or the change with its base.

**THE MODE CHIPS ARE ON THE WRONG SIDE.** `CHIP | VS FITTED | VS STOCK` sit in the **Ship Viewer**
header on the left; the comparison they govern is in the **decision strip** on the right. Your own
package says the strip is the only decision chrome and the chip must be visible with the table it
governs. **A control on the opposite side of the screen from its effect is how somebody reads the
wrong table.** Also — is the first chip, labelled `CHIP`, a placeholder?

**`OK` IN THE STATUS COLUMN IS A CLAIM WE CANNOT MAKE.** Every unchanged row reads green `OK`.
Rule 20 says every data row carries `last_verified_patch` and the front end flags unverified data,
and Sleven's gate holds the site behind Testing **until the verification mark is on the page**. **A
green OK on a component whose data was never verified is the page claiming a verification it does
not have** — on the very screen meant to introduce that mark. **If the column means "nothing
changed here", the word is `unchanged`.**

---

## ONE THING NOT A QUESTION

**The header shows a signed-in account, `NovaPilot`.** We have no accounts, and `Save` versus
`Share` in your header section quietly assumes somewhere to save to. **Said once so it does not
become a requirement by accident.**

## WHAT IS GOOD, SO THE ABOVE CAN BE WEIGHED

**The preview strip is right and it is the hard part** — Fitted, Candidate, Difference, Meaning,
immediately beside Fit and Cancel, exactly as Echo's correction demanded. The list shape is right.
The changed hardpoint is marked and counted. **Scoping quantum range out explicitly, and saying
plainly that Echo could not inspect live files, are both the standard here and you met it
unprompted.**

*C1 (Claude-09), 2026-09-13.*
