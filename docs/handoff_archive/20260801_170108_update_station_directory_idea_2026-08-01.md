# UPDATE — Station directory idea raised and parked

Filed from the Cowork brainstorming session (Claude-02), 2026-08-01. Nothing
built, nothing started, no code written. This is an idea recorded so it is not
lost, not a work order.

Full write-up lives in the claude.ai project as `claude/station-directory-plan.md`.
This is the machine-side copy so sessions here can see it exists.

## The idea

For every station and landing zone, record what shops are inside it, what they
sell, and how to physically get to them. Not "Everus Harbour sells food" but
"the food kiosk is on the ground floor, right outside the hangar elevators."
Some shops are ten steps from the hangar; some need an internal elevator and a
walk across the station. A player currently has no way to know which before
landing.

## Why it is worth doing

- It makes the tagline literally true. "Know where to buy, before you fly"
  should mean knowing which elevator to take, not just the price.
- It is the only dataset in this project that cannot be copied. Everything else
  comes from files anyone can download. This is knowledge players hold in their
  heads and trade in Discord, and it disappears when the chat scrolls.
- It is the query an in-flight assistant would actually be asked, and no
  Star Citizen tool answers it today.

## What already exists

Fragments, in prose, scattered. The Star Citizen Wiki's Everus Harbor page says
the commodities terminal is reached "by visiting the Galleria, walking up the
stairs, and entering the Admin booth" — exactly the right kind of information,
one sentence, buried, no floors, no elevators, nothing about the other shops.
Similar scraps exist in YouTube station tours and guide sites.

Nobody has it organised. Work starts from scattered material, not from zero.

## What it connects to on our side

- The location list already pulled from game data: 1,774 places, each knowing
  which place contains it.
- UEX once pulled: shop names and prices per location.

Directions sit between those two. Add them and "where is it" and "what does it
cost" become one answer instead of two lookups.

## Size, estimated honestly

Roughly 20-40 locations actually matter — the major landing zones and stations
people genuinely dock at. Five to fifteen shops each, so 200-500 entries total.
Walking one location and recording it properly is 15-30 minutes, so 10-20 hours
in-game overall.

Spread over normal play across several weeks this is manageable. As a single
push it is a slog. Treat it as the former.

An earlier figure of "a weekend" was given in conversation and is corrected here.

## Capture method proposed

Use the existing inbox pipeline rather than building anything new. A minimal
form — where you are, what you found, how you reached it — that drops a file
into `inbox/`. Alt-tab, thirty seconds, back into the game. Logging a shop must
be faster than deciding whether to bother.

## Staleness — the part that matters

This data goes stale differently from everything else here. Game files can be
re-downloaded and re-verified automatically. A reworked station cannot — only a
person walking through it notices.

Every entry must carry the game version it was checked in, and the front end
must surface it. An old note has to flag itself rather than quietly send someone
on a twenty-minute trip for nothing.

This is the strongest use case in the project for the verification columns that
landed 2026-08-01. Elsewhere they are good practice. Here they are the
difference between useful and actively harmful.

## Risk, stated plainly

Every other dataset here scales with compute — a script runs, data arrives. This
one scales with Sleven's time. If he stops playing it stops growing and rots.

That should be accepted deliberately rather than discovered later. The
counterweight: the same property is what makes it defensible.

## Open, not decided

1. Player submissions ever? Removes the bottleneck, brings accounts, moderation
   and spam. Much larger build, not assumed. Standing rule stands: no site
   feature may require an RSI account login.
2. Text, screenshots, or both? Screenshots are far clearer and raise their own
   publishing questions.
3. How fine does the detail go? "Second floor, north side" versus "out of the
   elevator, turn left, past the clothing shop."
4. Which locations first? Probably wherever Sleven already spends time, not a
   systematic sweep.
5. What happens when a station is reworked — flag the whole location unverified,
   or leave entries with an old version stamp until re-checked?

## Where it sits

Not part of Phase 1 (collection, now one pull from done). Not a blocker for
Phase 2 (validation). A content project that can run alongside everything else,
because starting needs no code — only somewhere to put the notes.

Sensible first move is not building anything: walk one station, write it down by
hand, and see how long it really takes and how useful it reads.

## Boundaries

Nothing else written. No commits, no pushes. Snapshots, database and live site
untouched.
