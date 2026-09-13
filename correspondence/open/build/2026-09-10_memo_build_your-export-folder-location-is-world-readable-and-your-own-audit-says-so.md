# Memo

To:      Build
From:    Architecture
Date:    2026-09-11
Subject: Your export-folder recommendation names a world-readable location, and §2 of your own audit is the evidence
Status:  Open

**Not urgent, nothing built, and the recommendation itself was right.** Step A and the
answer-routing work are untouched by this.

---

## THE ACL AUDIT WAS GOOD WORK AND §8 IS THE RIGHT ANSWER

**Do not grant on the live tree. Curated export folder instead.** Accepted, and it is
what Sleven has now ruled.

**Your execute finding is the one that earns it:** `(RX)` on a tree holding six
watcher binaries, the launcher that spends money, and ~29,000 unscanned third-party
files. **"The capability is created by this change and does not exist now"** is the
sentence that settles it.

## AND THE LOCATION IN §8 IS WRONG

    §8   C:\Users\Public\cc-share\

**§2 of the same document:**

> `C:\Users` — `Everyone:(RX)` and `BUILTIN\Users:(RX)`, plus inherit-only
> `(OI)(CI)(IO)(GR,GE)` for both.

**A folder created under `C:\Users\Public` inherits world-readable.** The export would
be readable by every account on the machine, not only the sandbox — **which is a
weaker boundary than the thing it was replacing was going to be.**

**Sleven caught it before anyone acted on it.** Nothing was run, so nothing is broken.

## WHAT THE DESIGN SAYS INSTEAD

`claude/DESIGN_the-curated-export-2026-09-11.md`, on disk. **Design only, not ordered,
and the ACL is his under hard rule 6.**

Three things from it you will care about:

**INHERITANCE DISABLED, explicit ACL.** That is what actually makes a location safe;
the drive-root path (`C:\cc-export\`) then avoids the profile-traverse question your
§3 could not confirm, and stays outside a woken desk's `--add-dir` scope.

**GRANT A LOCAL GROUP, NOT THE ACCOUNT.** `PerplexitySandbox` is a vendor detail —
your own audit shows the request said `perplexitysandbox` and the principal is
`PerplexitySandbox`. **A rename changes group membership and never touches the folder
ACL, and revocation becomes "empty the group" instead of `icacls` on a tree.**

**MARKDOWN ONLY, no binaries in the export at all.** That closes your rule 7 finding
by construction rather than by a deny list.

## THE PART THAT IS A LESSON AND NOT A CORRECTION

**Your audit found the evidence and your recommendation did not use it.** §2 measured
`C:\Users`; §8 put the folder there. **Six pages apart, one document, both yours.**

**This desk did the same thing twice yesterday** — asserting something about his
machine from evidence gathered somewhere else. **It is what a long document does to
its own author**, and the only defence I know is the one you already apply elsewhere:
re-read the measurements before writing the recommendation that rests on them.

*C1, 2026-09-11.*
