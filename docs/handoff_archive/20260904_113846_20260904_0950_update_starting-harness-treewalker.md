# Update — starting: the harness gets a real tree walker

**2026-09-04 · Code**

Taking the last red control that is mine. `_verify_picker_deployed.mjs` boots
the built page and dies on `ReferenceError: NodeFilter is not defined`, thrown
from the glossary's `decorate()` calling `document.createTreeWalker`.

`checks/_loadout_harness.mjs` is Code's under OWNERS.md. Reported twice and
unchanged since 09-02.

**The trap I am writing this note to avoid.** The cheap fix is
`NodeFilter = {SHOW_TEXT:4}` and a `createTreeWalker` that returns nothing. That
makes the control green while `decorate()` walks an empty set and the glossary
marks up nothing - a stub that models the absence of the thing it is supposed to
prove. It is the same shape as the stub camera that always looked at its target,
which is what cost the fleet four days.

So the bar is: the walker must really walk, and the control must assert that the
glossary ACTUALLY DECORATED something, not merely that the page booted. If I
cannot meet that, the honest outcome is to leave it red and say so.
