# Update — the owner's recording is cut and verified; and I have to disown my own sweep's timings

**Filed 2026-09-09 17:58 CDT.**

## THE OWNER'S JOB — DONE, AUDIO FIRST AS ORDERED

    C:\Users\david\Videos\Captures\_for_analysis\

    session-audio.m4a     12.3 MB   17:26.08
    session-00.mp4       225.1 MB   200.48s
    session-01.mp4       220.8 MB   200.42s
    session-02.mp4       227.0 MB   199.20s
    session-03.mp4       227.6 MB   200.66s
    session-04.mp4       223.4 MB   199.54s
    session-05.mp4        49.3 MB    45.76s

Largest piece **227.6 MB against a 400 MB cap** — 43% headroom, nothing near the
line.

**The original is byte-for-byte untouched and I proved it**: SHA-256 taken before
anything was written and again after everything was, identical both times, size
unchanged. It was only ever read.

**Stream copy confirmed from the streams, not from the flag I passed.** Every
piece is `h264 1920x1080` + `aac 48000 Hz stereo`, the same as the source. Six
segments total 1,046.06s against the original's 1,046.08s — 0.02s of container
rounding, every second accounted for.

**The audio is real and I checked rather than assumed**, because a silent track
was the one outcome worth knowing about immediately: 100,423,678 samples, mean
-36.7 dB, peak -14.3 dB. **22 dB of range** — a quiet bed with distinct louder
events on it. Not silence, not clipped. I have not listened to it and claim
nothing about what is in it.

**One correction to the memo: it is 17m26s, not roughly 20.**

**ffmpeg was not on the machine.** Installed `Gyan.FFmpeg 9.0.1` via winget,
hash-verified by winget against the publisher's release. The ffmpeg that WAS here
— playwright's, at `checks/.playwright-browsers/ffmpeg-1011/` — is built
`--disable-everything` with only webm, VP8, mjpeg and png. **No AAC, no mp4, no
segment muxer.** I read its build flags rather than discovering that by failing on
a 1.2 GB file.

## AND THE PART I HAVE TO OWN

**I said earlier that the first full sweep had died. It had not — it is still
running**, 67 minutes in against a 29-minute norm. Its stdout was buffered, so an
empty log looked like a dead process and I reported it that way. **It was a live
process the whole time and I should have checked the process table before saying
so.** I did check it — and read a small memory figure as the wrong thing.

**Worse: I ran heavy work alongside it.** A 256-hull render (8m49s), an ffmpeg
pass over a 1.23 GB file, several browser controls, a local web server and the
links control, all while a timing-sensitive gate was measuring itself.

**So this receipt's per-control timings are contaminated and must not be counted
as the second of Sleven's three.** He wants three sweeps of composition before he
sets a ceiling, and a run that competed with a video encoder tells him about my
afternoon rather than about the suite. **I will say so to Architecture rather than
hand over a number that looks like evidence.**

Its PASS/FAIL result is still worth having — that is what gates the deploy, and
contention does not change whether a control passes.

**A second sweep I started was correctly refused**, which is the guard working:

    ANOTHER SWEEP IS ALREADY RUNNING - refusing to start a second one.
    checks/.last_sweep.json is a single receipt and it is what authorises
    a deploy. Two sweeps finishing minutes apart would each overwrite it.

Rule 14, enforced by construction rather than by my remembering. It listed the
live pids, which is also how I found out my sweep was alive.

## WHAT IS CLEAR NOW

**`_verify_correspondence.py` is PASS.** Architecture answered the memo in their
own tray, so the last blocker on the sweep is gone.

Nothing committed.
