---
name: ANSWER_the-rsi-models-are-the-ones-we-have-2026-08-27
description: Direct answer to Sleven's repeated question about pulling 3D models from the RSI website - what they actually are, why they change nothing, and what does. Read before any session re-opens the model question.
sources: cowork
---

# ANSWER — The RSI models are the models we already have

**Sleven, 2026-08-27:**

> *"We've already determined that everybody else is pulling from the RSI
> website... every single other tool that does this shows, hey, this is our
> size work, and puts a little disclaimer... yet they don't take it down. So
> we've already determined that we can pull all this stuff from the website
> because everybody else is doing that. Yet you keep saying you understand
> that, but then you're telling me, oh, I legally can't do that. No. You
> legally can."*

## First: he is right, and I was wrong, and it is written down in this project

`RULING_community-practice-is-the-standard-2026-08-22.md` settled this five
days ago. `AMENDS_extracted-textures-scope-2026-08-22.md` states it flatly:

> **"No session may cite the CORRECTION document as a reason not to use
> RSI-served content. That reading is retired."**

`RULING_rights-questions-are-settled-2026-08-14.md` says rights are not to be
re-raised *"as a question, a caveat, or a flag."*

I raised it as a caveat anyway, more than once, in a project where it was
already closed in his favour. That is not a judgement call I got wrong — it is
a standing ruling I did not follow. It is struck. Nothing below is a rights
argument, because there is no rights argument left to make.

---

## Second: we already went and got them

**2026-08-22. CIC captured the RSI holoviewer's own loader, live.** Not
guessed at, not reasoned about — the actual files the actual viewer requests
when you open a ship page. Here is what came back.

    OpenCTM v5, MG2, ONE FILE PER SHIP
    exterior hull only
    single mesh BY FORMAT DEFINITION - no hierarchy, no named parts
    zero per-ship textures - the holo look is four shared files, fleet-wide
    no interiors, no cutaways, no diagrams, no paints

Measured against what this project already holds, same two ships:

| | ours `.glb` | RSI `.ctm` |
|---|---|---|
| Avenger | 765,808 B | 1,131,989 B — 131,210 verts, normals present |
| Constellation Andromeda | 2,602,528 B | 4,155,890 B — 544,945 verts, **normals absent** |

Different compression, so bytes are not a polygon count and no claim is made
that they are. What IS claimable: **same structure, same limitation, same
missing pieces**, and on one manufacturer RSI's normals are absent where ours
are present.

**And the Fan Kit's own fourteen `.ctm` files are the same asset family RSI
serves from the site.** Not a re-export. The same lineage.

## Third: so is everybody else's

Every tool he is thinking of, checked the same day:

| Site | What it actually serves |
|---|---|
| **Fleetyards** | `media.holo` → a glTF blob. **Same lineage as our 234.** |
| **myfleet.gg** | *"241+ ships from the RSI Holoviewer"* |
| **Romanito Ship Scale Viewer** | *"models taken from RSI's Holo Viewer"* |
| **Starship42** | RSI Holoviewer files |
| **Erkul** | no 3D at all — flat promotional art |
| **SPViewer / hangar.link / SC Wiki** | no 3D at all |

He is completely correct that the community pulls from RSI. What that means
is not *"there is something over there we are missing."* It means **we and
they are all drawing from one well, and this project is already drinking from
it.** Doing the fetch again would hand us a second copy of the file we open on
every ship page today.

Our own conclusion at the time, and it did not turn on rights:

> **"On engineering grounds and not on rights grounds: the models are the
> worst thing on offer here. They are marginally larger copies of what is
> already on disk, and they solve none of the open problems."**

---

## Fourth: what he is actually seeing, and it is not the model's fault

Two complaints have been riding together and they have two different causes.

### The see-through look is a settings bug, not a model problem

The viewer saves the appearance panel to `localStorage` permanently — his
instruction, and the right one. **It has no version stamp.** So a saved blob
overrides the defaults unconditionally and forever, and every appearance fix
we have landed has been overwritten on his machine at boot.

The proof is in his own screenshots: **they are cyan.** The default is amber
and has been since it was pinned. Cyan can only come from a saved value.
Which means his saved `style`, `lineInt` and `glow` are winning too — and the
retune that took see-through from *20.6–67.1% of the hull* down to **0.00% on
all ten measured ships** never once reached his screen.

He has been reporting a fixed defect, accurately, on a build that fixed it.
That is on us, not on him. `ORDER_the-panel-will-not-close-2026-08-27.md`
item P3 fixes it.

### The hardpoints cannot line up from the data we have, and that IS real

This one is not a bug and it will not be fixed by better models. From our own
`place_hardpoints.py`, first paragraph:

> **"We do not have real coordinates. All 53,651 `position` fields in the game
> data are null."**

The markers are derived from the mount's NAME — *"Weapon left wing"*,
*"Missilerack top left rear"* — turned into a region of the hull, then snapped
to a real vertex inside that region. It puts the left wing gun on the left
wing. It cannot put it on the barrel.

**And the RSI models cannot help.** OpenCTM has no node hierarchy — that is
not a property of these particular files, it is the format definition. There
is no place in an OpenCTM file for a hardpoint to be named. It was checked
directly and the finding is recorded as a hard no.

I have told him more than once that "we have the measurements." **What we have
is verified HULL dimensions in centimetres. We have never had mount
coordinates.** Those are two different things and I let them sound like one.

---

## Fifth: what would actually fix the hardpoints — his call, not mine

There is exactly one place known to carry per-hardpoint local transforms:
**the ship XML inside `Data.p4k` on his own machine.** Every mount is defined
there with a position relative to its parent, which is the thing that is null
everywhere else.

Code has already opened that archive twice — the 4.10 keybind extraction and
the DataForge decompression — with no third-party tool, so the capability is
proven rather than hoped for.

**Note the distinction, and it is his own, not mine:** he drew the line at
subscriber flair and said the public ship pages are a different matter. The
p4k is a third category again — it is the shipped client, governed by
`CORRECTION_extracted-textures-are-not-granted.md` as scoped on 2026-08-22.
**Rule 8 puts that call with him alone.** It is not raised here as a caveat
and it is not a request for a rights discussion. It is one sentence of fact so
that when he rules, he is ruling on the actual thing.

**What is needed from him is one line: his live install path, and go or
no-go.** If it is go, this is a real fix and not another promise.

---

## Sixth: the fifteen — CHECKED, and twelve of them have a model

**Sleven asked why this had not been checked. It had not. It has now.**

Of the fifteen ships with no model anywhere on our site, **twelve have a holo
model available** on the Fleetyards public API — no key, not under `/media/`,
and the same lineage as the RSI holoviewer by our own 2026-08-23 finding.

Found: **Mantis, Tiburon, MOTH, Pitbull, Tyilui, Basher, PTV, UTV, Starlite,
M80, Hermes**, and **85X** at a colliding slug that needs a human before it
counts.

Not found: **Command Module, Power Suit, Vanduul Mauler.**

Mantis and Hermes — the two he opened at random — are both on the found list.

Acquisition is ordered in `ORDER_the-fifteen-are-not-missing-2026-08-27.md`,
along with a full-fleet sweep, because fifteen was the known gap and not
necessarily the whole gap.

**The fleet-wide sweep could not be completed from a Cowork session:** the fetch
tool summarises pages through a small model and truncated every paginated
response to 2-3 of 12 entries. That is a tool limit and is recorded as one. Code
hits the API directly with no such ceiling.

---

## What this document is for

Any session that re-opens "why can't we just pull the models from RSI" reads
this first. The answer is not that we may not. **The answer is that we did,
and they are ours already.**

*C1, 2026-08-27.*
