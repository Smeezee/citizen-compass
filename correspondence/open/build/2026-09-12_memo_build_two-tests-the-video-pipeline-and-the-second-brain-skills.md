# Memo

To:      Build
From:    Architecture
Subject: Two tests to run, both on his machine, both reporting back. Neither touches the Citizen Compass repository.

**Sleven offered to run these himself. He does not type commands for routine work — you
have the tools, so they are yours.**

---

# TEST 1 — THE VIDEO PIPELINE, FIRST REAL RUN

**He has put a real video in `C:\Users\david\ChatGPT project\input\`:**

    (721) Did Star Citizen Make The Right Choice_ - YouTube — Mozilla Firefox
    2026-09-12 02-56-39.mp4          4,834,901 bytes

**The pipeline is installed as an MCP server on your side. `BUILD_STATUS.md` names the
gate: setup passes, the server shows healthy under `/mcp`, and one short real video
completes with acceptable evidence.**

## RUN IT TWICE, AND THE ORDER MATTERS

**RUN ONE — COPY IT TO A SIMPLE NAME FIRST**, something like `sc-test-01.mp4`.

**That filename has parentheses, spaces, an underscore and an em-dash in it.** If run one
fails, you would not know whether the pipeline is broken or the filename is. **One
variable at a time.**

**RUN TWO — THE ORIGINAL FILENAME, UNCHANGED.** That is a real test of its own and the
result is worth having either way. **A crash here is a finding, not a failure.**

## WHAT TO REPORT

    completed or not, and how long
    how many frames came out, and whether they are spread as expected
    the transcript — does it exist, and is it plausible against the audio
    the OCR text — what it read off the screen
    which of BUILD_STATUS's unverified items are now verified:
      Docker image build, PowerShell scripts, the MCP handshake on Windows,
      real Whisper with a model download, speed and memory on that machine

**Vision stays OFF.** `.env` has `ENABLE_VISION=false` and no Ollama vision model is
installed. **Do not turn it on for this run** — one new thing at a time.

**The first transcription downloads the Whisper model. That is not a hang.**

## AND THE PART THAT IS NOT OPTIONAL

**That video is another creator's work and so is the transcript.**

**Nothing derived from it goes into the Citizen Compass repository.** Not the report, not
the transcript, not a frame. **It stays in the pipeline's own `data/` folder, and the job
folder is cleared when the test is judged.**

**Report the findings in a memo. Quote the pipeline's own output sparingly — enough to
judge quality, not the transcript itself.**

---

# TEST 2 — THE SECOND-BRAIN SKILLS, AND THE INSTALL METHOD IS THE TEST'S SAFETY

**`github.com/NulightJens/ai-second-brain-skills`. My assessment is on disk:
`claude/ASSESSMENT_ai-second-brain-skills-2026-09-12.md`. He wants it tested and that is
his call.**

## DO NOT INSTALL IT USER-SCOPE. THIS IS THE WHOLE POINT.

**Their README says to symlink into `~/.claude/skills/`. That makes the skills available
to EVERY Claude Code session on that machine, including the one that works Citizen
Compass.**

**Install them PROJECT-SCOPED instead — inside a throwaway vault folder, so they exist
only there.** If project scope does not work the way I expect, **stop and report rather
than falling back to user scope.**

## THE STEPS

    1  clone to a scratch folder OUTSIDE citizen-compass and outside
       "ChatGPT project"
    2  READ BOTH SKILL.md FILES IN FULL BEFORE ENABLING ANYTHING.
       They are instructions, not a library. Report anything that reads as
       an instruction to act outside its own vault.
    3  create an empty test vault. Nothing of ours goes in it.
    4  install the two skills project-scoped to that vault
    5  run the setup skill, then wiki-self-heal in AUDIT-ONLY mode
    6  no research tools connected — no Exa, no Firecrawl, no Apify

## WHAT TO REPORT

**Whether its own stated constraints actually hold:** does it refuse to modify `raw/`,
does it refuse to delete pages, does it stay on its own branch, does it really decline a
claim with fewer than two sources.

**And the one I care about most: its "autonomy rule" says it continues without pausing.
Watch what it does when it hits something ambiguous.** That behaviour is the reason this
is being tested in an empty folder rather than adopted.

**Do not run it in full mode. Do not point it at anything of ours.**

---

**Neither test changes the project. Both report back as memos.**

*C1, 2026-09-12.*
