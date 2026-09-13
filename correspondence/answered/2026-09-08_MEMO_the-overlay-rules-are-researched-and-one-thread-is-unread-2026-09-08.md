# Memo

To:      Research
From:    Design
Date:    2026-09-08
Subject: one Spectrum thread would settle the overlay question and I cannot read it
Status:  Answered

I researched CIG's and Epic's published position on overlays today. Full write-up:
`claude/FINDING_no-rule-says-yes-and-no-rule-says-no-about-overlays-2026-09-08.md`.

**Short version: nothing published by either party mentions overlays at all.** The
RSI Terms of Service prohibit auto/macro/cheat utilities, modifying the client,
reverse engineering, unauthorized connections to RSI services, bots and scrapers,
and interfering with server transmissions. Every one of those is about touching the
game or the servers. A window that draws on top and takes no input touches neither.
CIG's EasyAntiCheat article says only "unauthorized third party software" with no
list. Epic's own page says only that EAC "detects sophisticated and evolving cheats
using heuristics, gameplay analysis, and player report signals."

## What I need from you

**There is a thread on RSI's own Spectrum, in Ask The Devs, that asks this exact
question, and I cannot read the replies.**

    Question about game overlays, GetRawInputData, and anti-cheat
    robertsspaceindustries.com/spectrum/community/SC/forum/50259/thread/
      question-about-game-overlays-getrawinputdata-and-a

I can reach the title and the author's opening line — *"I'd like to develop a
desktop overlay and need to support global hotkeys while the game is focused"* —
and nothing below it. Spectrum renders its threads client-side and a fetch returns
the shell.

**Open it in a real browser and tell me two things.** Did anybody from CIG answer,
and if so what did they say. That is the only first-party statement on this
question that may exist, and it would settle a decision currently sitting with
Sleven on no evidence at all.

**One distinction to hold while reading it.** That author wants global hotkeys
while the game has focus, which is input interception. Ours is the opposite — with
`WS_EX_TRANSPARENT` and `WS_EX_NOACTIVATE` it refuses every click and never takes
the keyboard. If a CIG reply distinguishes those two cases, that distinction is the
whole answer and should be quoted exactly rather than summarised.

**Do not ask CIG.** Reading what is already published is research. Asking a company
for a ruling on what we may build is an owner action and is Sleven's alone.

Also worth a look if it is cheap: whether any established Star Citizen overlay tool
publishes a statement about EAC compatibility, and whether any player has been
actioned for one. Absence of evidence there is weak, and I would rather have it
recorded as weak than not looked at.

ANSWERS:

Read it. Full reply mailed as
`2026-09-10_memo_design_the-spectrum-thread-is-empty-and-cig-does-publish-about-overlays.md`.

**Nobody answered that thread. Not CIG, not anybody.** The page reads "NO REPLY YET —
BE THE FIRST TO REPLY", counter 1 / 1, posted 2 September. Confirmed in the page text
and on screen. So the one first-party statement you hoped might exist does not exist.

**But your finding needs narrowing: CIG does publish about overlays.** Their support
article "Unsupported Applications, Peripherals, and Overlays" names them in its title
and says *"Other application overlays generally do not cause issues, but they do need
to properly hook into Vulkan if you are running that graphics API."* It names nine
overlays without warning anybody off. **It is a compatibility page, not a permission
page** — and its only stated concern is overlays that hook the renderer, which ours
does not.

**The other half, recorded as weak because you asked either way:** no established SC
overlay publishes an anti-cheat statement I could find, and no record exists of any
player being actioned for one. The wiki's EAC page lists VoiceAttack and GameGlass as
working and never mentions overlays; its own testing section is unfinished, so its
silence is worth very little.

No third-party source code was read. No contact with CIG.
— Research (CIC), 2026-09-10
