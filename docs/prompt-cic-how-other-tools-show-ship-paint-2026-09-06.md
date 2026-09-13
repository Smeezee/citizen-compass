# BRIEF FOR CIC — how does everyone else show a ship's paint? Look, record, do not judge.

    from      C1, 2026-09-06
    for       CIC (Claude in Chrome)
    origin    Sleven, deciding how our own ships should look, asked to see how
              the other tools handle it before he picks.
    status    gathering only. No recommendation is wanted from you.

---

## 1. Why this is being asked, in one paragraph, so you know what matters

Our 3D models have **no texture of any kind.** 0 of 258 files contain an image,
and that is true of RSI's own holoviewer files too. CIG's real paint exists in one
place outside CIG — the game client on Sleven's machine. So every hull on our site
currently renders as **grey clay**, and two ways of faking a painted look have been
built and are waiting on his pick.

**Before he picks, he wants to know what everyone else does.** Not to copy it — to
see what the bar actually is, and whether anyone has solved a problem we think is
unsolvable.

## 2. What to look at

**Erkul, Fleetyards, the Star Citizen Wiki, hangar.link, and RSI's own store and
holoviewer.** Add any other ship tool you find that shows a ship visually. Include
the wiki because it is community-maintained and may do something the commercial
tools do not.

**For each one, per ship, record what you can SEE:**

    is the ship shown as a photograph, a 3D model you can turn, or neither
    if it is a 3D model - is it painted, untextured grey, or a holo/wireframe look
    if it is painted - does it look like CIG's real paint, or an approximation
    are different paint schemes shown at all (Pirate, Best In Show, Emerald)
    if paint variants ARE shown - as photos, as swatches, or on the model
    where does the image come from - is it RSI's own art, or theirs

**And the question underneath all of it:** does anybody display a ship model with
CIG's actual materials on it? If somebody does, **that is the finding**, and what
matters then is what they say about where they got it.

## 3. Rules

**Do not fetch anything under `/media/` on robertsspaceindustries.com.** Rule 22.
You are looking at pages and describing what is on them.

**Describe, do not judge.** Not "theirs looks better" — say what is on the screen.
Sleven is choosing; your job is to give him the same view he would get by opening
ten tabs himself.

**Do not download, convert, or reason about anybody's model files.** Rights are
closed (rule 23). If a site publishes how it obtained its models, quote it and move
on.

**Say what you could not see.** A tool behind a login, a viewer that will not load,
a ship you could not find — record it as unseen rather than absent.

## 4. What to hand back

Plain prose per tool, and one short list at the end: **who, if anyone, shows a
painted model, and how.**

Write it into the claude.ai project as
`claude/CIC_how-other-tools-show-ship-paint-2026-09-06.md`.

## 5. Stop condition

If you find yourself three levels deep in how a renderer works, stop. **The
question is what a visitor sees**, not how it is achieved.

## 6. What C1 checked before writing this, and what C1 did not

**Checked:** our own 258 model files carry no image, measured; only 2 of 256 carry
CIG's real material split; CIG's colours do join by exact material name where the
names survive.

**Did NOT check:** any other tool. That is entirely this brief. Nothing is known
here about what Erkul or Fleetyards render, and no assumption should be read into
the order the tools are listed.
