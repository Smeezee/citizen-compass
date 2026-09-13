# Update — P28 stopped at the trace, deliberately, and routed to C1

**2026-09-11 17:55 CDT / 22:55 UTC. Nothing edited, nothing deployed.**

**I stopped before the edit under the delegation rule's own clause** — *"If the
order names the file but the change turns out to be wrong, or needs a different
fix than the one written: STOP AND SAY SO."* Memo filed to Architecture.

## WHAT THE TRACE FOUND

**The refusal is one lookup against the wrong dataset, not two candidate paths.**

`build_frontpage_data.py` takes each row's resolution stem and looks for it among
the **315 hull keys inside `five-main-pages.html`**. `AEGS_Javelin` and
`ARGO_MOTH` are absent from those 315; `AEGS_Hammerhead` is present. That is the
entire mechanism.

**So the reasons in the record — "two candidate paths of equal evidence" for the
Javelin, "no published dimensions" for the MOTH — do not describe this join.**
They may describe a different refusal elsewhere in the pipeline. **I have not
looked for it and I am not going to assume they are the same thing.**

**And `build_next_frontpage.py:298` is where it bites:**

    const href = s.hull ? 'loadout.html?from=next#'+s.hull : (s.url||'');

**`hull` is the hull-FIGURES key.** So "does this ship have a ship page?" is
answered by "is it in the figures file?" — two different questions that disagree
for exactly two ships. **The figures refusal is correct; using it to decide the
link is the error.**

## THE ANSWER IS ALREADY IN THE FILE THE JOIN READS

`data-layer/ship_resolution.json` carries
`{"site":"Javelin","file":"aegs_javelin.json","game_name":"Aegis Javelin"}` and
the same for the MOTH — **and the stem is the ClassName in another case.** The
ship page's own dataset has both ids and both pages render.

**The front page is not missing the answer. It throws it away when the figures
lookup fails and then sends the visitor to RSI.**

**One trap I flagged rather than stepped into:** `ship_resolution.json` also
carries `has_model`, and the MOTH's is **false** while its page renders with 75
markers. **So `has_model` is not the gate either** — swapping one wrong oracle
for another would have looked like a fix and been the same defect.

## WHY NOT JUST DO THE DONE-WHEN

**Branch 1, "show that we could not identify its page," would be honest about
our state and wrong about the world.** Both pages exist and are good. It builds
a visible-gap state for exactly two ships that have working pages, **and it
becomes dead code the moment C1 rules on the source question.** Work that has to
be undone is not progress.

**Branch 2, a dated decision that outward is intended, is not mine to write** —
it decides which dataset is authoritative for a link on a published page, in
another desk's generator.

## THE THING WORTH RAISING ON ITS OWN

**`five-main-pages.html` is C3's** — an explicit exception carved out of C1's
`main-page-concepts/` ownership in `OWNERS.md`. **So the front page's answer to
"does this ship have a page on our site" currently comes out of a concept file
owned by a third desk.** Nobody chose that; it is where the key happened to be.

**I have asked C1 to name the authoritative source and said I will implement it
in one change.** Until then P28 is not mine to move.

## WHERE THAT LEAVES THE QUEUE FOR ME

    P1, P2, P3, P24, P26   done and deployed, all proven on the served site
    P18                    closed, not a defect
    P27                    unblocked by today's lookup - C1's to rule
    P20                    sized and routed; the entry still carries the
                           pre-sizing numbers and C1 is rewriting it
    P28                    stopped at the trace, routed, waiting on C1
    P4                     blocked by P14, which is Sleven's
    Group B, 16 entries    Sleven's keep-or-drop, none of it mine

**So Group A is exhausted for me until C1 answers on P20, P27 and P28, or
Sleven rules on Group B.** I am not going to start something adjacent to look
busy — rule 25 is explicit about that, and today's queue advanced on measurement
rather than on volume.

*Code, 2026-09-11 17:55 CDT.*
