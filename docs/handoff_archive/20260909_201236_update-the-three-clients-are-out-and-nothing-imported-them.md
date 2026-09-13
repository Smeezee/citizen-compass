# Update — 746,566 files searched, nothing imported them, and the three are out

**Filed 2026-09-09 20:12 CDT.** Sleven's GO order, parts 1 and 2.

## PART 1 — THE SEARCH HE ASKED FOR, AND THE GAP HE SPOTTED IN MY REPORT

He was right that I had confirmed nothing imports `aider` or `litellm` and had
**not said the same about `openai`**, which is the most likely of the three to be
imported by something forgotten.

**746,566 files scanned**, the whole tree including everything git ignores.

    IMPORTS OUTSIDE venv/Lib/site-packages
      NONE. Nothing outside the installed packages imports openai, aider
      or litellm.

    IMPORTS INSIDE venv/Lib/site-packages
      4,023 import sites across 4 packages: aider, litellm, openai, posthog

**The 4,023 are the packages importing each other** — litellm's whole job is
wrapping openai — which is why the count is split by location rather than
reported as one number. A raw total would have said "4,023 things import this"
and meant nothing.

**Every mention outside site-packages is a document about this question**, except
one worth naming: `checks/_verify_no_agent_traces.py:61` has the word inside a
regex of terms that must never appear in published output. **A string in a
blocklist, not an import.**

## THE FOURTH PACKAGE, AND WHY IT DOES NOT CHANGE THE ANSWER

**`posthog` imports openai** and is not one of the three. He said not to touch
anything they dragged in, so it stays — but I had to know whether removing
openai would break it.

**It does not.** posthog's openai code lives in `posthog/ai/openai/`, an opt-in
integration. `posthog/__init__.py` never mentions openai, and `posthog/ai/__init__.py`
imports one thing: `Prompts`. **Verified after the removal — `import posthog`
still works, 7.8.6.** Nothing outside site-packages imports posthog at all.

## PART 2 — REMOVED, AND EXACTLY THREE THINGS CHANGED

    aider-chat==0.86.2
    litellm==1.81.10
    openai==2.20.0

    pip list before   117 packages
    pip list after    114 packages
    diff              three lines, and nothing else

**Put back with one command if he ever wants aider again:**

    venv\Scripts\python.exe -m pip install aider-chat==0.86.2 litellm==1.81.10 openai==2.20.0

Nothing they dragged in was touched — `pip uninstall` removes only what it is
named, and the 114-line diff proves it did.

## PART 3 — WHAT I RAN TO PROVE IT, RATHER THAN ASSERTING IT

**Import smoke test first**, so a broken venv would not cost thirty minutes to
discover:

    dotenv  psycopg2  sqlalchemy  fastapi  alembic  requests  PIL  bs4   all ok
    build_find_data                                                     imports clean

**Then the project's own proof of itself: a FULL SWEEP, running now.** Nothing
heavy alongside it this time, so its per-control timings are also the clean
receipt Architecture needs — the last one was contaminated by my own concurrent
work and I disowned its numbers.

## ONE THING I FOUND THAT I DID NOT CAUSE

**`pytest` is not installed in this venv** and `requirements-dev.txt` line 5
declares `pytest==9.1.1`. **It is absent in BOTH snapshots** — before my
uninstall and after — so this is a pre-existing gap, not damage. Stated because
"it was already broken" is only worth anything if the before-picture was
actually taken, and it was.

Nothing committed.
