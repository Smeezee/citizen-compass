# ECHO — dig into page-specific help

**Filed 2026-09-12 by the Adjutant desk, at Sleven's order. Copy-paste block for Echo.**
Supersedes the same question going to CIC; Sleven moved it to Echo.

---

Echo — Sleven wants you to do the digging on one question: page-specific help on a fan-made reference website. We have done a first pass and hit four walls. Your labels as usual: ESTABLISHED, RECOMMENDATION, FORECAST.

## WHAT IS BEING BUILT, AND WHY THIS QUESTION EXISTS

Citizen Compass is a free, fan-made Star Citizen reference site. It is plain files — no accounts, no login, no server-side application. Traffic is low. The rebuilt version is behind a password while it is being finished.

Sleven ruled that the old single help panel is replaced by help that follows the page:
- On the front page — a searchable list of about 250 ship cards with prices and shops — help explains the front page.
- On a ship page — that ship's own screens, including a weapons and DPS view — help explains that page.
- On the keybinds page, help walks a player through getting their sticks and controls connected.

One help control, same place on every page, different content per page.

## WHAT WE ALREADY ESTABLISHED, SO YOU DO NOT REDO IT

Read directly from the sources, 2026-09-12:
- Nielsen Norman Group splits help into proactive and reactive, and proactive into "push" (shown at you) and "pull" (there when you reach for it). Their guidance: "Favor pull over push revelations." (Kendrick, 2020-12-13.)
- NN/g reports that opening tutorials "interrupt users, don't necessarily improve task performance, and are quickly forgotten", and that help at the moment of need is "the most important guideline". (Laubheimer, 2023-02-12.)
- NN/g: user-initiated overlays are "far less jarring and annoying to users than system-initiated pop-ups"; help should be "available without interfering". (Sherwin, 2015-03-15 — old.)
- The UK Home Office design system recommends "small overlays containing help content for complex interactions", easy to close, with a link to fuller help; and warns contextual help "shouldn't be relied upon to solve design problems". That page says the pattern needs improving and asks for evidence.

From that we have already decided: the control is pressed by the visitor and never opens itself; short in the overlay with a link out for long answers; and one hard rule of our own — **no help text may be written that explains around a known defect.** If help would say "this button only shows some of the ships", that is a bug on our list and it gets fixed, not described.

## THE FOUR WALLS WE HIT — THIS IS WHAT WE NEED FROM YOU

**1. The closest comparisons, and we could not read them.** Erkul (erkul.games), SPViewer (spviewer.eu) and Fleetyards (fleetyards.net) are the tools our visitors already use. All three are JavaScript applications and our fetch tool returns only page metadata, no interface.
What we want: how each one explains itself to a new visitor. Is there any in-page help, tooltips, a first-run tour, a glossary, or nothing at all? Where does it sit, and is it first-party or written by somebody else?
What we found in passing, and want confirmed or broken: Fleetyards keeps documentation on a separate site (docs.fleetyards.net) rather than in the product; a third party publishes its own FleetYards guide; and searching how to use Erkul returns third-party videos and a forum post rather than a first-party help page. **Our working reading is that this whole category leaves explaining to other people.** A design has been built on that reading, so say plainly if it is wrong.

**2. Reference and catalogue sites, not software products.** Every source we found is about software people use daily or government forms people must complete. Ours is a catalogue someone browses for two minutes, maybe once. Is there anything published on help in that situation — wikis, price comparison sites, parts catalogues, transit or reference sites?

**3. Hardware setup help.** The keybinds page has to help a player get a joystick, throttle or controller working with the game. That is closer to a manual than to a tooltip. Is there research or established practice on setup and configuration guidance inside a web page — step state, "did that work?" checks, pictures versus text, or when to hand off to a video?

**4. Anything measured, from a source that is not selling help widgets.** We looked for how often people press a help control and found only vendor figures measuring their own product. We have written that off deliberately rather than quote a number we do not trust. If a non-vendor measurement exists — academic, government, or a company publishing its own data without selling the feature — we want it. If it does not exist, say so plainly and we will stop looking.

## HOW TO ANSWER

- Label each claim ESTABLISHED, RECOMMENDATION or FORECAST, and name the source with its date.
- Say when a source sells help or onboarding software, because that is an interested party.
- Say plainly where nothing exists rather than filling the gap.
- No code, no mockups. We are deciding the shape, not writing it.
- If something you find contradicts a decision above, say so first and directly.
