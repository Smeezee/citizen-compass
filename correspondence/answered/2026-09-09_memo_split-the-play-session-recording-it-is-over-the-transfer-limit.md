# Memo

To:      Build
From:    Owner
Date:    2026-09-09
Subject: split the play-session recording so it can be read — 1.23 GB, over the transfer limit
Status:  Answered

**The recording asked for on 2026-09-08 exists.** It is the first material this
project has ever had that carries picture and sound locked to the same instant.

    C:\Users\david\Videos\Captures\Star Citizen  2026-09-09 17-31-05.mp4
    1,231,075,654 bytes, recorded 17:31:05 today, roughly 20 minutes

**It cannot be moved off the machine as one file** — the transfer path caps at
400 MB per file. It needs cutting up on the machine, which is your job and
nobody else's right now.

## WHAT TO PRODUCE

**1. The audio on its own, first.** It is small and it is the half this recording
was made for.

    ffmpeg -i "<the file>" -vn -c:a aac -b:a 96k "<out>\session-audio.m4a"

Roughly 15 MB for 20 minutes. **Produce this one first even if the rest waits** —
the whole question the recording was made to answer is whether the game's sound
effects can be told apart, and that can start on the audio alone.

**2. The video cut into pieces under 400 MB, stream-copied, no re-encode.**

    ffmpeg -i "<the file>" -c copy -f segment -segment_time 200 \
           -reset_timestamps 1 "<out>\session-%02d.mp4"

About six pieces at ~200 MB. **Stream copy, not re-encode** — re-encoding would
change the audio samples, and the samples are the evidence.

**3. Put them in a new folder**, `Videos\Captures\_for_analysis\`, not loose beside
the original. **Do not touch or move the original.** It is the only copy of
something that cannot be made again — that recording is of a specific evening in
a specific patch.

## IF FFMPEG IS NOT ON THE MACHINE

Install it and say you did. If that is blocked, say so plainly and say what you
tried; do not hand the command to me.

## WHAT IS ALREADY KNOWN ABOUT THIS FILE

From the 26-second test recorded just before it, same settings, same session:
1920x1080 h264, AAC stereo 48 kHz, real audio present, Vulkan renderer, Game Bar
capture. Detail in
`claude/VERIFIED_the-capture-works-and-sound-events-are-visible-2026-09-09.md` —
including a correction worth reading, because a level jump in that test was
recorded as a game event and it was me moving a volume slider.

**Nothing in the test demonstrates a single game sound.** This file is supposed
to. That is what it is for.

ANSWERS:

**Done 2026-09-09 17:57 CDT. Audio first, as ordered. The original is byte-for-byte
untouched and I proved it rather than asserting it.**

    C:\Users\david\Videos\Captures\_for_analysis\

    session-audio.m4a       12,866,537     12.3 MB    17:26.08
    session-00.mp4         236,068,467    225.1 MB    200.48s
    session-01.mp4         231,567,900    220.8 MB    200.42s
    session-02.mp4         238,075,291    227.0 MB    199.20s
    session-03.mp4         238,651,244    227.6 MB    200.66s
    session-04.mp4         234,294,789    223.4 MB    199.54s
    session-05.mp4          51,737,629     49.3 MB     45.76s

**Largest piece is 227.6 MB against your 400 MB cap** — 43% of headroom to
spare, so no piece is near the line.

## THE AUDIO IS REAL, AND I CHECKED RATHER THAN ASSUMED

The whole reason for the recording is whether game sounds can be told apart, so a
silent track would have been worth knowing about immediately:

    n_samples    100,423,678
    mean_volume        -36.7 dB
    max_volume         -14.3 dB

**22 dB between the mean and the peak.** That is a quiet bed with distinct louder
events on top of it — the shape you would want. It is not silence and it is not
clipped. **I have not listened to it and I am not claiming any particular sound
is in there**; that is the analysis, and this is only the statement that there is
something to analyse.

## THE ORIGINAL

    sha256 before   145C5A62...1DA26DF0
    sha256 after    145C5A62...1DA26DF0      identical
    size            1,231,075,654 bytes      unchanged

**Hashed before I touched anything and again after everything was written.** It
was only ever read. Nothing was moved, renamed or written beside it — the new
files are in `_for_analysis\` as you asked.

## STREAM COPY, PROVEN BY THE STREAMS THEMSELVES

Every piece: `h264 1920x1080` and `aac 48000 Hz stereo` — the same codecs,
resolution and sample rate as the source. **No re-encode, so the samples are the
same samples.**

    segments total   1,046.06s
    original         1,046.08s
    difference          0.02s     container rounding across six files

The one thing that is not a perfect match: the six pieces total 1,230,395,320
bytes against the original's 1,231,075,654 — **680,334 bytes less, 0.06%.** That
is six mp4 containers' worth of headers and index tables differing from one, not
missing picture or sound. The durations above are the check that matters and they
account for every second.

## ONE CORRECTION TO YOUR MEMO

**It is 17 minutes 26 seconds, not roughly 20.** 1,046.08s, 1920x1080 h264 at 54
fps, 9.41 Mbps, AAC stereo 48 kHz — read from the file, not from the capture
settings.

## FFMPEG WAS NOT ON THE MACHINE. I INSTALLED IT AND HERE IS WHAT AND HOW

    winget install --id Gyan.FFmpeg --silent
    ffmpeg 9.0.1-full_build (Gyan), installed under
    %LOCALAPPDATA%\Microsoft\WinGet\Packages\

Hash verified by winget against the publisher's release before extraction.

**There was already an ffmpeg on the machine and it could not have done this** —
playwright ships one at `checks/.playwright-browsers/ffmpeg-1011/`, and it is
built `--disable-everything` with only webm, VP8, mjpeg and png enabled. **No AAC,
no mp4, no segment muxer.** I checked its build flags rather than trying the
command and reading the error, because a stripped ffmpeg failing on a 1.2 GB file
is a slow way to learn something `-version` says in one line.

Nothing else was installed and nothing else changed.
