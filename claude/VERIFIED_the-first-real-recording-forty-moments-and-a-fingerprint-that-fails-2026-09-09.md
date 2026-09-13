# VERIFIED — the first real recording: 40 moments found, and the fingerprint does not work

    date     2026-09-09
    desk     Adjutant
    source   Videos\Captures\Star Citizen  2026-09-09 17-31-05.mp4
             split by Build to Videos\Captures\_for_analysis\
             session-audio.m4a + session-00..05.mp4
    length   1046.1 s (17 min 26 s), 1920x1080, AAC stereo 48 kHz, Vulkan

**The recording asked for on 2026-09-08 exists and has been analysed. This is the
first material this project has ever had with picture and sound locked to the same
instant.**

**Headline: detecting WHEN something happened works. Identifying WHAT happened does
not, and the reason is now specific.**

---

## 1. METHOD, SO THIS CAN BE RE-RUN

Audio decoded to mono 16 kHz. 50 ms frames, RMS in dB. A rolling background taken
as the 20th percentile over a ±4 s window. **An event is any run of frames more
than 9 dB above that local background**, with runs closer than 0.4 s merged.

Rolling background rather than a fixed threshold, because the session moves
between a hangar, a shop, open flight and a station, and each has its own floor. A
fixed threshold measures which room he is in.

**Every number below is reproducible from `session-audio.m4a` with that
procedure.** The scripts are kept beside this document per the standing rule that a
measurement nobody can re-run is a claim.

## 2. WHAT THE EAR FOUND

    session floor (20th pct)   -40.3 dB
    session median             -35.9 dB
    candidate events           40, in 17m26s

Strongest few:

    12:38.30  3.80 s   +21.4 dB over local background
    12:52.00  2.55 s   +17.7 dB
    10:19.50  2.95 s   +16.0 dB
    17:22.35  0.85 s   +14.6 dB
    06:23.10  2.55 s   +14.6 dB

## 3. THE EYE CONFIRMS THE EAR — FOUR FOR FOUR

Frames pulled at four of those timestamps from the matching video segment. **Every
one lands on a real, nameable game moment.** Not ambiguous, not a guess:

    10:19.5   in the hangar. Red "ALERT: SHIELDS DOWN" across the top,
              "0 - GUNS (ALL)". Ship systems coming up.
    12:38.3   cockpit, asteroid field, MFD reads "READY TO SCAN".
    12:52.0   "READY" banner, target STANTON GATEWAY 12.90M, quantum charge
              100%, "QT ENGAGE" prompt. A quantum drive spooled and ready.
    17:22.35  station approach. On-screen notification: "Hangar Request
              Completed".

**So a level detector with a rolling background finds real events in this game's
audio.** That is the *when* half of the design, and it works on the first attempt
with no signal processing beyond reading the samples.

## 4. THE FINGERPRINT FAILS, AND THIS IS THE FINDING

Each event fingerprinted as the log-magnitude spectrum of its first 0.5 s across
32 log-spaced bands from 80 Hz to 7.5 kHz, mean-removed and variance-normalised,
compared by correlation.

    780 pairs      median 0.296   mean 0.244   90th pct 0.911   max 0.990

**The spread looks excellent.** Least-similar pairs reach −0.87, so the measure
plainly discriminates *something*. A careless read stops here and reports that
sounds can be matched.

**The top pair is two different events.**

    0.990   14:40.05  <->  17:22.35   162 s apart

`14:40` is scanning in an asteroid field. `17:22` is "Hangar Request Completed" on
approach to a station. **Same cockpit, same engine, same ambient bed — different
game events entirely.**

**The fingerprint is matching the room, not the sound.** In a cockpit the discrete
effect sits on top of a loud continuous background, and 0.5 s of banded energy is
dominated by the background. Every one of the high-scoring pairs is in-cockpit
flight; the strongest negative correlations all involve `02:06`, which is
somewhere else.

**So the question the audio design rests on — can distinct game sound effects be
told apart — is still open, and is now open for a stated reason rather than for
want of material.** The discrete sound has to be separated from the continuous bed
before anything can match it. Level detection alone will not do it, and neither
will a spectrum of the whole moment.

**Recorded this way deliberately.** Earlier today this desk turned a real
measurement into a finding it did not support. The similarity numbers here are
real and the conclusion they invite is wrong, and the only thing that caught it
was looking at the picture.

## 5. THE THING NOBODY DESIGNED FOR, AND IT IS SITTING IN THE FRAMES

**"Hangar Request Completed" is printed on screen at the moment its sound plays.**
So is "READY TO SCAN". So is "ALERT: SHIELDS DOWN".

**For a whole class of events the game names the event on screen, in text, at the
instant the sound occurs.** The project already has a screen reader that is graded
at 94.8% on held-out frames.

**That is a free labelling machine.** Audio event at time T, screen text at time T,
and the text says what the sound was — with no human tagging, no voice labels, and
no guessing. The paired answer key the design wanted exists inside the recording
itself.

**Not proposed as a build.** Recorded because it fell out of looking, it costs
nothing to notice now, and it would be expensive to rediscover.

## 6. WHAT IS TRUE, WHAT IS NOT

**True:** the capture path works; 40 candidate moments in 17 minutes; four of four
checked by eye are real game events; the detection method is reproducible from a
file that still exists.

**Not true, and not to be repeated as true:** that this recording shows game sounds
can be identified or matched. **It shows they can be located.** Those are different
claims and today has already produced one document that confused them.

**Untested:** whether a shop purchase, a sale, or a small UI confirmation produces
a detectable event at all — the four confirmed here are all large flight-system
events. The quiet ones are the ones the design most needs and the ones this pass
says nothing about.
