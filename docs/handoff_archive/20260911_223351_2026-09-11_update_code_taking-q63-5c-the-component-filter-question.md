# Update — Code is taking Q63.5C: can a visitor filter ships by a component, today, at all?

**2026-09-11 22:31 CDT.** Tray checked, nothing new.
`_verify_correspondence.py` still exit 1, so **T-008 and the Q58 4px are still
built and still undeployable, and my letter asking C1 to rule the red is
unanswered.** No override used.

**So I am taking the research C1 called the one that matters**, because its
answer may remove a promise from the page rather than add work to it.

**The question, in C1's words:** *"is there a join today, at all, that would let
a visitor filter ships by a component? What I need is a yes with the mechanism,
or a no with what is missing. Not an estimate of how hard it would be."*

**And the consequence, which is why it is not a normal feature question:** if the
answer is no, the filter is **held OUT of the interface with a dated line** — it
does not get built and it does not get shown as coming. **Hard rule 11: the page
must not promise a filter that cannot answer.**

**What I already know and will not re-derive:** the front page's own data carries
no component field at all — I read every field of `frontpage_data.json` this
afternoon for P20. **So the question is really whether the ship page's dataset
can answer it, and whether that answer can reach the front page honestly.**

**Where I am looking:**

    testing/_src/loadout_data.gen.js    the ship page's component data, read
                                        from the game files. Does it map ship ->
                                        components in a form a filter could use?
    the ship page's own disclosure      it says the link between component data
                                        and PRICED SHOP ITEMS is unproven. That
                                        may be a different join from the one
                                        ruling 5 needs, and I will not conflate
                                        them.

**The distinction I expect to matter:** *"which ships mount a size-3 shield"* and
*"which ships can I buy a size-3 shield for"* are different questions with
different joins, and ruling 5 may only need the first. **I will answer both
rather than pick the convenient one.**

**Look-and-report. Nothing is authorised to change** — C1 quotes his scope
limit: *"They are not blanket authorization to begin unrelated implementation."*

*Code, 2026-09-11 22:31 CDT.*
