# VERIFIED — the recording path works, and a sound event is visible in the waveform

    date     2026-09-09
    desk     Adjutant
    file     Videos\Captures\Star Citizen  2026-09-09 17-24-49.mp4
    length   26.1 seconds, Windows Game Bar, Vulkan renderer

## MEASURED

    video     1920x1080, h264 — frames checked at 5s and 20s, both show the
              game (a weapons shop interior, HUD present). Not black.
    audio     AAC, stereo, 48 kHz. NOT silent.
              overall mean -42.9 dB, peak -26.4 dB
    renderer  Vulkan. No DirectX 11 restart was needed.

**Per-second levels, and this is the finding:**

    0-8s      peak about -50 dB, rms about -64 dB
    9s        peak -25.3 dB, rms -38.5 dB     <- 25 dB jump in one second
    10-25s    peak -25 to -30 dB, rms about -39 dB

**CORRECTED THE SAME DAY — the 9-second step was not a game event.** Sleven
supplied the cause: it was him raising the in-game volume in the settings menu,
having turned it down to listen to chat. **The step is his hand on a slider.**

The original entry here called it "a sharp edge of exactly the kind the
audio-trigger design rests on." **That was wrong, and it was wrong in the way
this project is most careful about** — a real measurement, correctly taken, with
a cause invented for it. The level change happened; the meaning was supplied by
me. Struck rather than quietly reworded, so the record shows a finding got
manufactured out of a true number.

**Nothing in this document's other measurements is affected.** The capture path,
the resolution, the frames, the presence of audio and the absence of silence were
all read from the file and all stand.

## WHAT THIS DOES AND DOES NOT PROVE

**Proves:** the capture path works end to end on his machine under Vulkan, and
game audio reaches the file rather than arriving silent.

**Also proves, though not in the way first written:** a 25 dB change is plainly
visible by reading the samples with no signal processing at all. **The
sensitivity is real even though this particular cause was a settings slider.**

**Does not prove** the question the design actually rests on: whether distinct
game sound *effects* can be told apart from each other. A level jump is not a
fingerprint — and this one was not even a game sound. **Nothing in this file
demonstrates a single game event.** That still needs the real recording with
named events in it.

**The lesson worth keeping:** a loudness change tells you something changed,
never what. Anything that reads level alone will happily report a volume slider,
a Discord notification or somebody's music as a transaction. **The trigger has to
match the sound, not the size of it.**

## TWO PRACTICAL NOTES FOR THE REAL RUN

**The game was quiet for the first 9 seconds only, and that was a chat-listening
setting, not the game's normal level.** From 9s on it sits at about -27 dB peak.
Usable. Louder still helps the small sounds — a purchase confirmation may sit only
a few dB above the floor where this step sat 25 above it.

**Game Bar records the window that had focus when recording started.** Three
earlier attempts captured the Claude desktop window instead of the game — 960 x
1036, digitally silent, six and a half minutes of one of them. The filename is
the tell: Windows names the file after what it captured. **"Star Citizen …" is
right, anything else is a wasted run.**
