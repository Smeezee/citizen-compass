# Work order — Station Directory, pulled out for C1

    from      C3 (Cowork), 2026-08-07
    for       C1
    source    claude/station-directory-plan.md (idea, parked, raised 2026-08-01 in the
              Brainstorming and Ideas session — full detail lives there; this is the
              pulled-out, standalone version Sleven asked for so it can move
              independently instead of sitting buried in an ideas doc)
    status    Sleven wants this actively in front of C1 now — not queued behind
              everything else, and specifically considered alongside the collector
              work already in front of Code. See the capture-mechanism section below.

---

## What it is

For every station and landing zone, keep a simple record of what shops are
inside it, what they sell, and exactly how to physically get to them. Not
"Everus Harbour sells food" — but "the food kiosk is on the ground floor, right
outside the hangar elevators." Some places are ten steps from the hangar. Some
require an internal elevator and a walk across the whole station. Right now a
player has no way to know which before they land.

## Why it matters

It makes the tagline literally true. "Know where to buy, before you fly"
currently means knowing the price and the station. It should mean knowing which
elevator to take.

It's also the one part of this project that can't be copied from a data dump.
Everything else on the site comes from files anyone could in principle download
— game data, wiki APIs, price feeds. This is knowledge that only exists in
players' heads and Discord threads, and it evaporates when the conversation
scrolls. Nobody has organized it; scattered fragments exist (a Star Citizen Wiki
page saying "reach the commodities terminal by visiting the Galleria, walking up
the stairs, and entering the Admin booth" is exactly the right shape of
information, just buried and incomplete), but nothing pulls it together.

## What it connects to, already in hand

- The 2,066-entity location hierarchy from `claude/FINDING_missions-and-locations-full-breakdown.md`
  (`data-layer/derived/location-gazetteer/`) — every place, tagged to its system
  and planet/moon.
- UEX pricing data, once wired — shop names and prices at each location.

Station-level walking directions sit between those two. Add them and "where is
it" plus "what does it cost" become one answer instead of two separate lookups.

## Scope, honestly

Only about 20-40 locations actually matter — the major landing zones and
stations people genuinely dock at (Area18, Lorville, New Babbage, Orison, Grim
HEX, the main orbital stations). Each has roughly 5-15 shops, so somewhere
between 200-500 entries total. Walking one location properly and writing down
what's where takes 15-30 minutes, so the whole thing is realistically 10-20
hours of in-game time — spread across normal play over weeks, not a weekend
push. An earlier "a weekend" estimate in an older conversation was too
optimistic; this is the corrected number.

## Capture mechanism — this is the part Sleven specifically wants coordinated with C1, not built blind

The original plan's own proposal for how this data gets logged: a simple form —
where you are, what you found, how you got to it — that drops a file into the
capture pipeline. Alt-tab out of the game, thirty seconds, back in. No new
machinery underneath it.

**Sleven flagged directly:** the collector-as-a-program work already in front of
Code (`claude/workorder-collector-as-a-program.md`, WO-UI-01) is the same shape
of thing — something that runs while he plays and captures information with
minimal friction, already auto-detecting location context from the game log.
Before anyone builds a second, separate capture form for station-directory
notes, C1 should look at whether WO-UI-01's collector window can grow a
lightweight "log a location note" action — a text field plus whatever location
context the collector already has — instead of standing up an independent
mechanism. Not a mandate to merge them; a request not to design the two blind to
each other, since they're solving the same underlying problem (capture
something while playing, get it into the pipeline with minimal friction).

## Open questions, unchanged from the original plan — still Sleven's to answer, not C1's or C3's

1. Player submissions ever, or Sleven-only indefinitely? (Note the standing rule:
   no site feature may require an RSI account login, which bounds this either way.)
2. Text, screenshots, or both? Screenshots raise their own publish-rights
   question, separate from this decision.
3. How much walking detail — "second floor, north side" versus real turn-by-turn
   directions? The second is far more useful and far slower to write.
4. Which locations first? Almost certainly wherever Sleven already spends his
   time, not a systematic sweep.
5. What happens when a station gets reworked by a patch? Flag the whole location
   unverified, or leave old entries standing with a version stamp until someone
   re-checks them?

## Data-staleness note, worth carrying into any build

This data goes stale in a way the rest of the project's data does not. Game
files can be re-downloaded and re-checked automatically; a rebuilt station
can't be — only a person walking through it again notices. Every entry needs a
verified-patch stamp, and the site needs to visibly flag old entries as old
rather than quietly send someone on a wrong trip. This is the strongest case in
the whole project for the verification-stamp pattern already in the database.

## Where this sits

Not blocking anything, not part of Phase 1 or Phase 2. Needs no code to start —
the original plan's own recommendation stands and is worth repeating: the first
move is Sleven walking one station and writing down what's where by hand, to see
how long it actually takes and how useful the result reads, before any tooling
gets built around it. The capture-mechanism coordination with WO-UI-01 above is
the one piece that does need C1's attention now, since it affects how Code
scopes the collector work already in progress.
