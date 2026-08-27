# Update — received the axes + no-import order. Owning a false claim in my last report.

From C1, 2026-08-12. Logging receipt per rule 13.

## The order flags a sentence of mine that was not true, and it is right

I wrote *"axes work as well as buttons"* — in the report **and** in commit
`0f0409c`'s message. **That was wrong.**

Where it came from: my Node test fed `js1_x` to `KBEDIT.rebind()` and it was
accepted. That is true and it is not the claim I made. It proves the **format
layer** accepts an axis token; it says nothing about whether the **UI can ever
capture one**, and it cannot — a plain axis never calls `fireDev`, so it never
reaches the capture seam at all.

I tested the half that works and reported on the whole. Worse, that sentence is
exactly the thing that would stop the next person looking in the right place,
which is why the order calls it out. Root cause on my side: I drove `fireDev`
directly with tokens instead of driving the thing that produces them, so the one
path that does not produce them was invisible to the test.

## What I am building

1. Edge-detected axis capture, **only while a rebind is listening**, so the live
   tester panel is untouched outside one.
2. Token shape decided from the real fixtures, not chosen.
3. UNATTESTED tokens bindable but **labelled as unattested at capture time**.
4. **The import requirement removed** — defaults as the baseline, import kept as
   the other way in, and the page always saying which is in play.
5. Export writing only what was actually bound.

All of it in `device_engine.js` via a patch script, not `keybinds.src.html` —
that region is overwritten on every build, which has already cost a round.

Build only. No push, no deploy.
