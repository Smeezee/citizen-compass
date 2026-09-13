# FINDING — the seat overlap was real, bounded to the handover, and I then attributed four hours of other desks' work to it

**CORRECTED 2026-09-12 01:30 CDT by the desk that wrote it, after Sleven said plainly that
the old chat was archived. He is right. The original conclusion — that the retired C1 was
still running — was wrong, and the way I got there is the more useful half of this
document.**

---

## WHAT ACTUALLY HAPPENED, AND IT IS SMALL

Sleven booted the merged C1 and archived the retiring C1 chat **while this desk was doing its
first read.** For a few minutes at the start, both were live.

    01:01:20  retiring desk  ECHO_DESIGN_DESK_PACK.md rewritten, the boot prompt
                             rewritten 19,455 -> 19,787, answers filed to the two
                             package letters
    01:06:31  new desk       eight letters committed to inbox/, including answers
                             to the same two package letters
    01:06:38  retiring desk  RULING_the-carrack-answered-from-rsi-itself-2026-09-12.md

**That is the whole overlap.** It cost one duplicated answer in the owner's tray, which was
withdrawn, and three duplicated answers in the architecture tray, which the watcher preserved
under `__<timestamp>` suffixes rather than overwriting. **Both desks reached the same
conclusion on the Carrack from different evidence.**

**Nothing after 01:06:38 was the retired desk.**

## MY ERROR, WHICH IS WHY THIS DOCUMENT STILL EXISTS

**I saw files change in shared folders at 01:13, 01:14 and 01:22 and attributed them to the
desk I was already suspicious of. I did not open one of them to see who wrote it.**

**One read settles it.** `docs/AUDIT_which-of-this-desks-documents-are-actually-on-disk-2026-09-12.md`
says on its second line: *from Design (C3), asked by Sleven*. The other `docs/` files touched
in that window — the C3 charter, the keybind and stick-panel documents — are that same desk
pulling its own project-only documents down to disk. **That is ordered recovery work by a
live desk doing its job, and I reported it as a rogue session.**

**The shape:** a mtime tells you a file changed. **It does not tell you who changed it**, and
this project has six desks and a watcher all writing to the same folders. **A writer is
identified by opening the file and reading the signature, not by inferring from timing.**

**It is the same error the outgoing desk warned about in its own handover** — *do not
conclude another writer exists* — and it is one step worse, because I had already been
warned and had a cheap check available. **I told Sleven twice in chat that a desk was still
running. The second time was four hours of other desks' output read as one desk's.**

## WHAT SURVIVES, BECAUSE IT IS NOT ABOUT TONIGHT

**The mail system is safe against a seat overlap and the repository is not.** The watcher
renames rather than overwrites, so two letters with one name produce two files. **A document
write does not do that.** `project_write` replaces a whole document with no version history,
and a bridge commit replaces a file outright. Had both desks written `docs/CURRENT-STATE.md`
or `NEXT.md` in those five minutes, one version would simply be gone, and the size check both
desks run would have passed on the survivor.

**There is still no seat claim anywhere in the repository.** A booting desk cannot tell
whether its seat is already held, and the only available signal — a desk's last timestamped
output — is exactly the signal that cannot distinguish one working desk from two. **Tonight
that did not matter because Sleven closed the old chat himself, within minutes. It is a
handover procedure carried by a person rather than by the machine.**

**The cheap fix, unchanged and still not ordered:** a desk writes one line when it boots —
designation, session identifier, boot time — and a booting desk reads it. It fails safe: a
stale claim from a crashed session costs one line of manual clearing.

## THE RELATED SHAPE ALREADY ON FILE

`claude/FINDING_two-claude-folders-on-two-machines-and-the-receipt-does-not-say-which-2026-09-12.md`
is the same family, and this correction extends it: **a write receipt does not say which
machine, and a file's timestamp does not say which desk.** In both cases the missing field is
identity, and in both cases the fix is to read the artifact rather than reason about the
metadata.

*C1, 2026-09-12. Corrected by its own author.*
