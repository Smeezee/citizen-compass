# BRIEF — the loadout bench is an experience, not a display

**2026-08-26 · Sleven's direction, researched and written up by C1**
**NOT AN ORDER. Nothing here is built until Sleven signs off on a design.**

---

## Sleven's brief, in his words

> "It can't just be a display of components and names and stuff. It needs to be
> user friendly ... the interaction of actually going through the steps of
> swapping the parts and understanding what they do needs to be a smooth, fluid
> process."

> "I want to take a little bit of ideas from every other tool and then redesign
> them in my own way and make them more user friendly ... I want anybody who
> stumbles upon our website, never heard of it before, to actually enjoy the
> experience of figuring out what the best setup for their ship is on our page.
> I want it to be smooth. I want it to be efficient, and **I'm okay with it
> taking longer.**"

**Six static mockups were rejected before this brief existed, and they deserved
to be.** Every one of them re-arranged a list. The product is not the list. The
product is the loop: pick a part, understand what it does, see what it changes,
keep or undo.

---

## What the swap actually is today — measured by driving it

Clicked a missile rack on the Aegis Avenger Stalker in the built page. Seven
distinct frictions, none of them about how the list is sorted:

1. **The picker opens ON TOP of the 3D model** — a 328 x 340 box over the exact
   thing being modified. You cannot see the ship while changing it.
2. **16 parts fit that port. Two are visible.** The rest is a scroll inside a
   window smaller than a phone screen.
3. **It compares on the wrong attributes.** A missile rack shows
   `Mass 20 · IR 0 · EM 0` — not how many missiles it holds or what size. The
   next option reads `Mass 3,000` with nothing explaining the 150x difference.
4. **The sorts are secondary**: Least size, Coolest, Quietest, Lightest. Nothing
   about capacity, damage, or what the part is for.
5. **No side-by-side.** "Currently fitted" is at the top and the alternatives
   below, so judging option three means memorising the fitted one's numbers and
   scrolling back. **The user is doing arithmetic in their head.**
6. **The consequence is hidden.** Swapping changes the right rail - which the
   picker is covering. The single reason to swap a part is what it does to the
   ship, and that is the one thing the flow conceals.
7. **The heading names the port, not the part.** "Bomb rack · size 3" above a
   fitted Missile Rack.

---

## What the competition actually does — and the bar is higher than assumed

**Erkul.games v5, rebuilt from scratch, is the tool to measure against.** Its
own release notes describe: *"a card-based dashboard with a dedicated card for
every component family, swap dialogs with sortable stats and deltas, full-spec
detail drawers, and runtime theming"*, plus power management, quantum
calculations, saved builds in a Hangar, public publishing, a creator
leaderboard, and Discord sign-in.

**Two corrections to positions C1 has taken in this project, both recorded
because they were stated confidently and were wrong:**

- **Deltas in the swap dialog are not our idea. Erkul ships them.** The
  "hover an option and watch the numbers move" proposal is the state of the
  art, not a differentiator. Doing it is table stakes; doing it *better* is the
  job.
- **The patch-to-patch diff is NOT an artifact nobody publishes.** Erkul v5
  ships *"patch-to-patch data changes with human-readable labels, before to
  after values and buff/nerf coloring, searchable and filterable."* C1 pitched
  C5/C6 as the one thing nobody else offers. **That was wrong.** C5/C6 remain
  worth building - a diff we can prove is a diff we can trust, and it feeds the
  `last_verified_patch` promise - but the framing must change and nobody should
  repeat the "nobody else does this" claim.

**And the space is crowded.** Beyond Erkul: Hardpoint.io, HubCitizen,
Citizen Starter Guide, SCANZ, StarCitizenHelp all ship a loadout builder of
some kind. **"Another loadout builder" is not a product.**

---

## Where the actual gap is

**Every one of those tools is built for somebody who already knows the game.**
Erkul is, by its own name and history, a DPS calculator. It assumes you know
what a size 3 gimbal implies, what deflection is, why you would care about
distortion pool. It is excellent, and it is for experts.

**Sleven's brief is explicitly the opposite: somebody who has never heard of
the site, arriving for the first time, working out what is good.** Nobody is
serving that person well.

**Three things this project already holds that the others do not:**

1. **The 3D hull with real hardpoint positions.** Erkul has no model. We can
   show WHERE a part goes while you swap it. Nobody else can.
2. **Provenance on every number** - CIG's own figure marked apart from ours,
   and `last_verified_patch` on every row. Nobody else distinguishes the two.
3. **Plain English that already works.** The right-hand rail says "what the
   pilot can fire", "heat · lower is stealthier", "hull plus everything fitted ·
   lower turns better". **Sleven has repeatedly said he prefers that column -
   and the reason is that it explains itself.** The left panel has never
   explained anything; it names things.

**That is the design thesis: the tool that explains.** Not the tool with the
most numbers.

---

## Principles the design must satisfy

Drawn from the brief, not invented:

- **You can see the ship while you change it.** The model is the thing that
  makes this page different; covering it with the picker throws away the one
  advantage we have.
- **Compare on what the part is FOR.** A missile rack on missiles carried and
  size. A shield on HP and regen. A cooler on cooling rate. Mass is a footnote
  on all of them, not the headline on all of them.
- **The consequence is visible before the commit**, not after.
- **Undo is one action**, and reverting to stock is always available.
- **Every number carries a plain sentence** saying what it means, the way the
  right rail already does.
- **No login. Ever.** Erkul now needs Discord to save a build. Being the one
  that asks nothing of a stranger is a real position, and it costs nothing.
- **"Efficient" beats "fast to build."** Sleven has explicitly accepted a longer
  build for a better result. Do not trade the second for the first.

---

## What happens next

**Nothing is built yet.** The next artifact is a design of the SWAP LOOP -
not another arrangement of a list - put to Sleven for judgement. It should
show the sequence: what you click, what opens, where it opens, what you compare
on, what moves, how you get back out.

**None of this blocks the standing queue.** Code has six approved items and not
one of them touches this panel.
