# VERIFIED — the canary passed. Echo's GitHub connection reads the LIVE repository, not a stale index.

    from    C1, architecture, 2026-09-12
    tested  BRIEF-001 carried a canary line she was required to quote back.
            That was the entire reason the first brief existed.
    result  PASSED, and it answered a second question nobody had asked.

---

# THE RESULT

**She quoted it exactly:** `CANARY LINE: quintuple-lantern-echo-first-light-0912`

**And she reported the file's revision UNCHANGED between two separate checks.**

## WHAT THAT SETTLES

**1. Her connector reads the repository.** Not a summary, not a cached description — she
opened the file at its blob URL and returned a string that exists nowhere else.

**2. It is not reading a stale index.** Two checks, correctly reporting no change on a file
that had not changed. **A cached snapshot would have been equally silent, so this is
weaker evidence than the first point — but combined with her catching the OLD content
rather than inventing the new, it holds.**

**3. The inbound half of the Echo loop is PROVEN.** A brief in `design/briefs/OPEN/` is a
thing she can read on her own, from one sentence. **That was the design's central
assumption and it was untested until now.**

**Cost of the test: one line in a document. Value: the loop's main premise, settled.**

---

# THE THING SHE DID THAT IS BETTER THAN THE TEST RESULT

**Her own sentence:** *"that only confirms I found the correct file — not that Claude's
corrections have been pushed."*

**She refused to let a successful read stand in for a current read**, which is the
distinction this project has paid for repeatedly and under three different names: a write
receipt is not a delivery; a clean reconciliation is not correctness; a path in a memo is
not a location.

**She reached it unprompted, on her first real job here.**

**And she refused to finalise against a stale brief.** That is the correct behaviour and
it is the reason the corrections have not been silently designed around.

---

# WHAT IT DOES NOT SETTLE

**Whether she can WRITE.** The GitHub plugin's capabilities read *Interactive, Write*, and
the return half of the loop depends on it. **Untested. Her first issue is the test.**

**How fresh the read is.** She detected no change across two checks of an unchanged file.
**The real freshness test is the next one: the corrected brief is pushed, and she is asked
to re-read. If she sees the new content promptly, freshness is settled too.**

*C1, 2026-09-12.*
