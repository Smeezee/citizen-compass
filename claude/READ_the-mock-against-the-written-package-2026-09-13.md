# READ — the mock against the written package, before we talk

**C1 (Claude-09), 2026-09-13. Read from `design/mocks/loadout-decision-strip-mock.png` directly,
against `correspondence/open/design/2026-09-13_memo_design_loadout-decision-strip-pass-builds-on-echo.md`.
Nothing here is a ruling. Sleven has held the ruling and this is what I would bring to the table.**

**The mock is good and most of it agrees with the memo.** The preview strip is
Fitted / Candidate / Difference / Meaning immediately beside Fit and Cancel, exactly as written. The
component list is the right shape. The changed hardpoint is marked and the count is shown. **What
follows is where the picture and the words say different things, biggest first.**

---

## 1. THE MOCK AND THE MEMO DISAGREE ABOUT WHAT COMMITS A CHANGE. THIS IS THE REAL QUESTION.

**The memo says:** *Previewing a candidate does not silently install it. Preview is not installed.
**Fit** commits. **Cancel preview** backs out with no change.*

**The mock's footer says:** *All changes are local and can be undone until you commit the loadout.*

**Those are two different products.**

    memo    Fit is the commit. One hardpoint at a time. Undo is one step back.
    mock    Fit stages a change. The LOADOUT commit is the commit. Everything before
            it is provisional and reversible.

**Under the mock's model there must be a Save or Commit Loadout control, and there is not one on
the screen.** Under the memo's model the footer sentence is false.

**This is not a wording problem.** It decides whether there is one commit or two, whether Undo is
one step or a stack, what "Changed" is measured against, and what happens if the tab closes. **Every
one of the four bindings I wrote hangs off this, and I answered them assuming the memo. If the mock
is the intent, at least two of my four are wrong.**

**It is the first thing to settle and everything else is cheap after it.**

---

## 2. THE "MEANING" COLUMN IS THE WHOLE BUILD COST, AND NOBODY HAS COSTED IT

The mock shows: *"Longer lock range and stronger scans. Slightly less efficient but lighter on
power."*

**That is a written sentence about one specific swap.** The memo names the column and never says
where the sentence comes from.

    written by hand      one sentence per component pair. There are over a thousand
                         components. It will never be finished and never be maintained.
    generated            a template over the numbers: "+32% Max Range" becomes
                         "longer lock range". Buildable, and it can only say what the
                         numbers already say.
    omitted              the Difference column stands alone.

**Generated is the only one that survives contact with the catalogue**, and a generated sentence is
a restatement of the row above it, not new information. **So the honest question is whether Meaning
earns its width at all, or whether the Difference column with real units does the same job.**

**I am not ruling it. It is the largest unpriced thing in the package and it should not reach Build
undecided.**

---

## 3. THE DIFFERENCE COLUMN IS PERCENTAGES WITH NO BASE, AND ONE ABSOLUTE MIXED IN

The mock shows `+32% Max Range`, `+12% Scan Strength`, `-8% Power Draw`, `+65 kg Mass`.

**Three percentages and one absolute, in one column.** And a percentage with no base is not
actionable: **+32% of a range the reader cannot see is not a number they can decide on.**

**This is the same defect as burst beside sustained**, one surface over — quantities in different
units sharing a column and a label. **Show the value and the change**, or show the change with its
base beside it. Not a bare percentage.

---

## 4. THE MODE CHIPS ARE ON THE VIEWER, NOT ON THE THING THEY CONTROL

`CHIP | VS FITTED | VS STOCK` sit in the **Ship Viewer** header, on the left. **The comparison they
govern is in the decision strip, on the right.**

The memo is explicit that the decision strip is the only decision chrome and that the mode chip must
always be visible with the table it governs. **A control on the opposite side of the screen from its
effect is how somebody reads the wrong table** — which is the exact error the mode chip exists to
prevent.

**Also: the first chip is labelled `CHIP`.** Almost certainly a placeholder, worth confirming rather
than assuming.

---

## 5. "OK" IN THE STATUS COLUMN IS A WORD THAT HAS NOT BEEN EARNED

Every unchanged row reads `OK` in green.

**`OK` says the row is fine. We do not know that.** Rule 20 says every data row carries
`last_verified_patch` and the front end flags unverified data, and Sleven's own gate keeps the site
behind Testing **until the verification mark is visible on the page**.

**A green OK on a component whose data has never been verified is the page claiming a verification
it does not have** — on the same screen that is supposed to introduce the verification mark.

**If the column means "nothing changed here", the word is `unchanged`, not `OK`.** They are
different claims and only one of them is true.

---

## 6. TWO SMALLER THINGS, RECORDED AND NOT ARGUED

**The Undo in the mock is one Undo for the build, in the list footer beside "1 changed".** The memo
says one-step undo **on that hardpoint**. Another consequence of question 1.

**The header shows a signed-in account, `NovaPilot`.** We have no accounts. A mock showing a
signed-in user sets an expectation the site cannot meet, and Save-versus-Share in the memo's header
section quietly assumes somewhere to save to. **Worth saying out loud before it becomes a
requirement by accident.**

*C1 (Claude-09), 2026-09-13. Nothing ruled, nothing ordered.*
