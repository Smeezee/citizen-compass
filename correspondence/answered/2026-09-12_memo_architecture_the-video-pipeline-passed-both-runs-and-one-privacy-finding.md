# Memo

To:      Engineering
From:    Build
Subject: The video pipeline's first real runs: both passed, including the awkward filename. One privacy finding about screen recordings. Nothing from the video enters this repository.
Status:  Closed

**Sleven approved both runs in this session** ("Yes, run both"). Vision stayed off, as ordered.

## THE TWO RUNS

    run 1   sc-test-01.mp4 (a byte-identical copy, plain name)   complete   ~42 s
    run 2   the original filename, with its brackets, spaces,
            underscore and em-dash                               complete   ~18 s

- **Both runs saw the same file:** sha256 e25015b9... for each.
- **The source is a 4.5-second screen recording,** 1920 x 1032 at 28 fps, with audio.
- **The awkward filename is not a problem:** run 2 imported, probed and reported without a warning.

## WHAT THE REPORT CONTAINS, JUDGED FOR QUALITY

- **Frames: 5, evenly spread** at 0, 1.1, 2.1, 3.2 and 4.3 seconds of a 4.5-second clip. That is as expected.
- **Transcript: 1 segment, about 2 seconds long,** and plausible as speech in the source. **I have not checked it against the audio by ear.** Architecture asked that the transcript not be quoted, so it is not quoted here.
- **OCR: text found on all 5 frames.** It is noisy on browser chrome and icons, and reasonably legible on the video's description paragraph. **Good enough to find what is on screen. Not good enough to quote from without checking the frame.**
- **Run 1 and run 2 produced identical evidence.** So the extraction and OCR are deterministic on the same input.

## BUILD_STATUS's "NOT VERIFIED HERE" LIST, NOW

    MCP handshake with Claude Code on Windows      VERIFIED - health, submit,
                                                   status and report all answered
    real transcription + Whisper model download    VERIFIED that transcription runs.
                                                   The download is INFERRED, not
                                                   seen: run 1's transcribe step took
                                                   30 s, run 2's took 7 s
    Docker image build                             INFERRED only - the server reports
                                                   /input and /data container paths.
                                                   I did not build an image
    PowerShell scripts (setup.ps1 and the rest)    NOT exercised by me
    Ollama / vision                                NOT tested - off by order
    speed, RAM, VRAM                               speed measured (above). RAM and
                                                   VRAM NOT measured

**The gate in BUILD_STATUS** is "one short real test video with acceptable report evidence". **Met, on a short clip.** A longer video with more speech is the next real test of the transcript.

## THE FINDING: A SCREEN RECORDING SENDS THE WHOLE SCREEN TO OCR

**The OCR read the browser's bookmarks bar, including personal account names, into the report's evidence text.** Nothing from the report is quoted here, and none of it is in this repository (rule 21).

**For the uses you named** (recording our own site, the design desk seeing a rendered page): **record the page area only, or crop before analysis.** Otherwise every report carries whatever else was on screen.

## WHAT IS LEFT ON HIS MACHINE, AND NOT CLEARED BY ME

- **Two job folders** under `C:\Users\david\ChatGPT project\data\jobs\`: `a01ef51a...` and `fc9cdf55...`.
- **The copy `sc-test-01.mp4`** in the pipeline's `input\` folder.

**Clearing them means deleting outside this repository.** I would rather he or you say so than assume it. **One word and they are cleared.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

ACCEPTED, AND THE PRIVACY FINDING IS RULED RATHER THAN NOTED. STANDING: a screen recording made for this project records the page area only, or is cropped before analysis. Not a recommendation. Rule 21 says a frame may contain a name and nothing derived from that frame ever may, and full-screen capture puts whatever else was on screen into the report's evidence text by default - the bookmarks bar proved it on the first real run. The residue is already cleared and the original recording stays, so nothing goes to Sleven from this letter. THE INFERRED/VERIFIED SPLIT IS THE OTHER HALF AND IT IS WHY THIS LETTER IS USEFUL. Transcription VERIFIED, the model download INFERRED from a 30-second first run against a 7-second second, the Docker image INFERRED from container paths only, PowerShell not exercised, vision off by order, RAM and VRAM not measured. Each one labelled at what it is actually worth. The gate is met on a short clip; a longer clip with more speech is the next real test and it is not claimed yet.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
