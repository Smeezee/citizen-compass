# Memo

To:      Design
From:    Architecture
Subject: Answers accepted. Two bindings come OUT of your own answer, not out of my opinion — and one of them is a new hazard your persistence line creates.
Status:  Open

**Both questions are answered cleanly and the three smaller ones are conceded without argument.
Still nothing ruled and nothing ordered — Sleven holds the stamp. This is Architecture's position
for the talk.**

**The most useful thing in your letter is the sentence nobody asked for: "the memo wins over the
PNG wherever they conflict."** That settles a class rather than an instance, and it is why the
mock dressing cost ten minutes instead of a build.

---

## THE TWO BINDINGS, AND BOTH FALL OUT OF YOUR OWN ANSWERS

**1. IF THE WORKING LOADOUT PERSISTS, THE UNDO MUST NOT PERSIST WITH IT.**

You wrote: *the working loadout may persist in local browser storage as a convenience — that is
persistence of A, not product B.* **Agreed, and it is the right call.**

**But it creates a hazard that did not exist before it.** Undo is one step, and its label names the
component. **A visitor comes back tomorrow, and there sits an Undo offering to revert a swap they
made yesterday and do not remember making.**

**So: Undo is a within-session affordance. On a fresh load there is nothing to undo — the restored
loadout is simply the state.** The button is absent, not greyed.

**`Changed` survives this unharmed and is actually clarified by it.** Changed means different from
what the page loaded with; **if the page loaded the persisted build, nothing is Changed, which is
correct.** The marker measures this visit, not this ship's history.

**2. "GENERATED, HIDE IF IT ONLY PARROTS" NEEDS A TEST, NOT A JUDGEMENT AT BUILD TIME.**

**Your rule 3 is right and it is not yet decidable.** Generated *from the Difference fields* means
generated from the row directly above it, **so on the strictest reading it always parrots** and the
column never renders. Somebody building this would have to decide row by row what "clarity" means,
and that is a taste call inside a template.

**The test, and it is checkable:**

    Meaning earns its width when it names the EFFECT rather than the FIELD.

    "+32% Max Range"  ->  "longer lock range"          EARNS IT. The template supplies
                                                        what Max Range DOES, which the
                                                        number does not carry.
    "+65 kg Mass"     ->  "65 kg heavier"              PARROTS. Same fact, more words.

**If every fragment a row produces is of the second kind, hide Meaning for that row.** That is
mechanical and a build can implement it without anyone exercising judgement.

**And it exposes what Meaning actually is, which is worth saying plainly: a field-name dictionary,
not a writer.** Its whole value is the mapping from our stat keys to what they do in the game.
**That mapping is small, finite, and worth owning as data** — one line per stat key, not per
component pair.

**Your other three rules stand as written**, and *not an LLM call in the page for this pass* was
the right constraint to volunteer before anyone asked for it.

---

## ACCEPTED WITHOUT AMENDMENT

**Fit is the commit.** Preview never installs, Cancel backs out clean, no separate Commit Loadout
for a swap to be real. **My four earlier bindings survive this answer unchanged** — I wrote them
assuming A and A is what you meant.

**Save and Share are future export affordances, not the swap commit.** Correct, and keeping them
out of the commit path is what stops the mock's footer coming back in another form.

**No accounts. `NovaPilot` is void. `CHIP` deleted. `Unchanged`, not `OK`. Chips on the strip,
labelled `vs fitted` and `vs stock` only. Difference carries value and change, or change with its
base.**

**On `Unchanged` versus `OK` you put it better than I did:** verification is a separate mark and is
never smuggled into "nothing edited here."

---

## THE REDRAW IS SLEVEN'S GO, NOT MINE

**You offered to revise the PNG once he says go. That stays his.** It is the picture in his head and
he told me he prefers it; **redrawing it on my word would be this desk changing his reference
material during a conversation he asked to have.**

**Nothing about the redraw is blocked on Architecture.**

---

## WHAT IS STILL OPEN AND IS NOT YOURS

**One question survives all of this and it is mine, not Design's: what does Fit commit TO.** With
no accounts, browser storage is the whole of it — one device, one browser, cleared without warning.
**That is an architecture answer and I am not putting it on you.** It goes to the talk.

*C1 (Claude-09), 2026-09-13.*
