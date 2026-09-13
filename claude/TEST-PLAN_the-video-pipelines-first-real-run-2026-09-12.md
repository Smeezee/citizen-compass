# TEST PLAN — the video pipeline's first real run

    from    C1, architecture, 2026-09-12
    why     Sleven asked whether a recorded YouTube video about Star Citizen
            would work as the real test the build status calls for.
    answer  Yes, and it is a better test than the synthetic clip. Four things
            to know first, and one to be careful with.

---

## IT EXERCISES THE WHOLE THING, WHICH THE SYNTHETIC CLIP DOES NOT

**Real speech tests the transcription. On-screen text tests the reading. Real motion
tests the frame grabbing.** The test MP4 already in `input/` proves the plumbing; it
proves nothing about the three parts that do the actual work.

## FOUR THINGS TO KNOW BEFORE RUNNING IT

**1. Keep it SHORT — three to five minutes, not forty.** The configuration takes
`MAX_FRAMES=12` and samples them evenly across the whole video, with no scene detection —
a deliberate version-1 limit. **On a forty-minute video that is twelve stills more than
three minutes apart, which tells you almost nothing about whether frame grabbing works.**

**2. The first run downloads the speech model and will look stuck.** The README says so.
**It is not hung; it is fetching Whisper.** Only the first job pays it.

**3. Picture description will NOT run, and that is correct.** `.env` has
`ENABLE_VISION=false` because it needs an Ollama vision model installed first
(`gemma3:4b` in the sample). **Expect frames, a transcript and read-off text — no written
description of what is in the picture** until that model is pulled and the flag flipped.

**4. Transcription is set to CPU int8.** Deliberate, to keep installation simple. **It
will be slower than the machine is capable of** and that is not a fault to chase on the
first run.

## THE ONE CAREFUL PART, AND IT IS NOT THE TEST

**A recorded YouTube video is somebody else's work, and so is the transcript the pipeline
produces from it.**

**Locally, for a test, deleted afterwards — that is ordinary and not a rights question.**

**The thing to watch is the REPORT.** A transcript of another creator's video committed
into a public repository is republishing their content. **So: the video and anything
derived from it stay out of the repository, and the job folder gets cleared when the test
is done.** `data/` is not in this project's repository today and should not become so.

## THE TEST THAT COSTS NOTHING AND IS ALSO USEFUL

**A sixty-second screen recording of our own site.** No rights question at all, dense
with on-screen text for the reader to chew on, and **the report it produces is a record
of what the site actually shows** — which this project has never had.

**It does not test transcription**, because there is no speech in it. **So the honest
version is both: our own site for the visual half, a short talking clip for the audio
half.**

## WHY THIS TOOL IS ON THE BOARD AT ALL

**The design desk's standing weakness, recorded for weeks: it cannot see a rendered
page.** Every visual judgement it has made went through a screenshot taken by hand.

**A tool that turns a recording into timestamped frames with the text read off them is an
instrument for exactly that**, and it runs locally with nothing sent to a cloud. **The
Ten Eyes design is about machines looking at screens. This is one of them, arrived at
sideways.**

**Nothing is ordered on it.** Recorded so it is on the board rather than filed as a side
project.

*C1, 2026-09-12.*
