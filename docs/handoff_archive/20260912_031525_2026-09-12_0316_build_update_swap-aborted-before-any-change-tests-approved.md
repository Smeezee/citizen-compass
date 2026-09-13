# Build update - the watcher swap aborted before any change; Sleven's answers on the two tests

**Code (Build), 2026-09-12. The clock read 03:08:44 CDT at the swap attempt and 03:14:54 at the clone.**

## THE SWAP - ABORTED AT THE FIRST CHECK, NOTHING CHANGED

**The cause is my defect.** I named the hash helper `H`. In PowerShell, `h` is a built-in alias for `Get-History`, so the first hash check called `Get-History -Id <path>` and threw. **That happened before the task was disabled, stopped or touched, and before any file was moved.**

**Verified afterwards:**
- the task is still Running
- the watcher is still PID 19112, the same process since 09-10 19:47
- the root binary is still sha256 f9d983b2...
- no rollback file was written

**A second problem, and it is the real one.** The cleanup's `Enable-ScheduledTask` returned **"Access is denied"**. This session is not elevated. The previous swap's report records the same wall. I am reading how it was handled before trying again. **I will not work around elevation.**

## THE TWO TESTS - SLEVEN'S ANSWERS, VERBATIM

    video pipeline, both runs (simple name, then the original)   "Yes, run both"
    second-brain skills                                          "Read only"

- **The skills test goes no further than reading.** I have cloned it to the session scratchpad, outside both project folders, and I am reading its two SKILL.md files. **Nothing is installed or run** (rule 7 holds).
- **The video test:** a copy named `sc-test-01.mp4` is made in the pipeline's input folder. Nothing from it enters this repository.
