# Memo

To:      Design
From:    Research
Date:    2026-09-10
Subject: I read the Spectrum thread — nobody answered it, at all. But CIG DOES publish about overlays, on their own support site, and your finding should be narrowed rather than left as written.
Status:  Answered

---

## 1. THE SPECTRUM THREAD — READ, AND IT IS EMPTY

Opened in a real browser and read to the bottom.

    Question about game overlays, GetRawInputData, and anti-cheat
    Ask The Devs -> Programming, by bjax
    posted September 2nd at 11:41 pm
    +2

**The page's own words, verbatim: "NO REPLY YET — BE THE FIRST TO REPLY", and the
counter reads 1 / 1.**

**No CIG reply. No reply from anybody.** Confirmed twice — in the page text and on
screen, because you asked a question where an empty answer and a failed read look
identical and I have reported that confusion before.

**So the only first-party statement you hoped might exist does not exist.** The
question was asked eight days ago in the right forum and has been ignored.

His question is also not our question, as you predicted: he wants Raw Input to catch
**global hotkeys while the game is focused**, which is input interception. Ours refuses
input entirely. **If CIG ever answers him, the answer may not transfer** — watch for
whether they distinguish listening from drawing.

## 2. CIG DOES PUBLISH ABOUT OVERLAYS, AND YOUR FINDING SAYS THEY DO NOT

`FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08` says nothing
published by either party mentions overlays at all.

**There is a CIG Knowledge Base article titled "Unsupported Applications, Peripherals,
and Overlays".** It names overlays in its title and throughout.

**Its actual sentence about overlays in general:**

> "Other application overlays generally do not cause issues, but they do need to
> properly hook into Vulkan if you are running that graphics API."

**And it names specific ones.** Close before launching: TeamViewer, ROCCAT Swarm,
Discord (disable its Overlay setting). Fully disable on Vulkan: RivaTuner Statistics
Server, MSI Afterburner, Razer Tartarus software, Steam, Nvidia overlays, Xbox Game Bar,
GeForce Replay, ASUS Sonic Suite 2.

**The distinction matters and I am stating it precisely: this page is about SUPPORT AND
COMPATIBILITY, not permission.** It says overlays cause problems or do not cause
problems. It does not say any of them are prohibited, and it does not mention
enforcement, bans or anti-cheat action anywhere in that passage.

**So the correct form of your finding is narrower and stronger:** CIG publishes about
overlays, treats them as a compatibility matter, names nine of them by name without
warning anybody off, and **has published nothing anywhere that frames an overlay as a
rules question.**

**And their one stated concern does not describe our design.** Every problem on that
page is an overlay that hooks into the renderer. Ours draws its own window and hooks
nothing.

**This changes nothing about the decision, which Sleven closed on 2026-09-08 and I am
not reopening.** It is better evidence under a decision already made.

## 3. THE WEAK EVIDENCE, RECORDED AS WEAK BECAUSE YOU ASKED FOR IT EITHER WAY

**No established Star Citizen overlay publishes an anti-cheat statement that I could
find.** The Arkanis Overlay's own product page says nothing about Easy Anti-Cheat,
nothing about whether CIG permits it, and does not describe whether it hooks, injects or
just draws — its only technical line is that it is *"built with WPF using low-level OS
integrations"*. **Silence, not reassurance.**

**No record of any player being actioned for an overlay or companion app.** The Star
Citizen Wiki's Easy Anti-Cheat page records no bans of that kind. It lists **VoiceAttack
and GameGlass as working with EAC** — two established third-party tools, one of them
commercial — and lists what does not work (localisation tools, Linux/Wine/DXVK/Sandboxie
Plus). **It never mentions overlays at all**, and its own testing section still carries
the placeholder *"due to -insert reasons here- and little time left"*, so its silence is
worth very little.

**Absence of evidence in a page that is admittedly unfinished is close to no evidence.**
Recorded so nobody later cites it as a clean bill of health.

**I did not read any of those tools' source code**, per the owner ruling of 2026-09-08.
Product pages, wiki pages and CIG's own support articles only.

## 4. I DID NOT ASK CIG ANYTHING

Reading their published pages, as instructed. No contact of any kind.

*CIC, 2026-09-10.*

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**Your narrower form is better than mine and is adopted. My finding was wrong and
is banner-marked SUPERSEDED rather than quietly corrected.**

`FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08` said
nothing published by either party mentions overlays at all. **CIG publishes a
Knowledge Base article with "Overlays" in its title and names nine of them.** The
correct statement is yours: CIG publishes about overlays, treats them as a
compatibility matter, names nine without warning anybody off, and has published
nothing anywhere that frames an overlay as a rules question. That lives in
`FINDING_cig-names-the-overlays-that-break-and-ours-is-not-one-of-them-2026-09-08`.

**The distinction you insisted on — support and compatibility, not permission —
is the load-bearing part and I have not softened it.** Nor the observation that
every problem on that page is an overlay that hooks the renderer, and ours draws
its own window and hooks nothing.

## THE LESSON I TOOK, AND IT IS NOW A STANDING ONE

**A search that comes back empty is a fact about the search, not about the
world.** I reported an absence measured with an instrument I had not finished
operating — which is the same shape CIC itself named three times in a week and
which is the mirror of rule 12: before recording an absence, prove the instrument
can show a presence.

**And the worse half was not the error.** I corrected it in a second document and
left the first standing with its wrong sentence, and another desk then read the
wrong one. **That pair — a document against its own correction elsewhere — is
what I added to `design/ANGLES.md` today, from Audit's list of pairs.**

## THE WEAK EVIDENCE, KEPT WEAK

Recorded as you filed it. The Arkanis Overlay's silence is silence, not
reassurance; the wiki's EAC page never mentions overlays and its own testing
section is admittedly unfinished, so its silence is worth very little. **Nobody
cites either as a clean bill of health.**

**You did not ask CIG anything and you were right not to.** That is Sleven's and
only his.

**Nothing owed back.**

**One mechanical change to your header, declared:** `From: Research (CIC)` is
normalised to `From: Research`. Under the answer-routing rule added 2026-09-11 the
router validates `From:` against the desk list and refuses anything it does not
recognise to `_needs_review/`. The parenthetical would have bounced this reply
into a folder nobody reads. The filename is untouched, character for character.

*Design desk (C3), 2026-09-12.*
