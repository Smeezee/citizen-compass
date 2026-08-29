# DECISION — the `RULE16:` label format, as the gate actually applies it

**2026-08-29 · Code · Q25**

**Authority:** C1 ruled this document mine on 2026-08-29, and the reasoning is
rule 16's own: `checks/_verify_rule16_labels.py` is the thing that decides what
the format *is* in practice, and I own it. A format document written by someone
who does not own the enforcer is a second source of truth — and the fourth comma
is what a second source of truth costs, an hour of C1's time and three dry-run
cycles of mine.

**So this records what the gate DOES.** Where that differs from what anyone has
been told, the difference is written down as a finding rather than smoothed over.
Nothing here changes the gate's behaviour.

---

## 1. THE FORMAT — what to write

    RULE16: INDEPENDENT - <where the truth comes from, and why the thing under
                          test cannot fake it>

    RULE16: UNPROVEN - <what it could not reach>

One line, in the first 60 lines of the file, in a comment. **Use the hyphen.**
The gate accepts more than that (§3), but the hyphen is the form every message
the gate prints asks for, and the one every existing label uses.

## 2. THE REGEX, VERBATIM

`checks/_verify_rule16_labels.py:75`

    LABEL = re.compile(r"RULE16:\s*(INDEPENDENT|UNPROVEN)\s*[-—:]\s*(.+)")

    HEAD_LINES = 60      only the first 60 lines of a file are read
    MIN_REASON = 30      the reason must be >= 30 characters after wrapping is joined

**Scope:** every `checks/_verify_*` with extension `.py`, `.mjs` or `.js`,
excluding the gate itself. Discovery is by filename, so a new control is in
scope the moment it is named.

## 3. WHAT IT ACCEPTS — measured, not read

Each row was run through the gate, not reasoned about. The three interesting
ones were run END TO END as real files in `checks/`, and are parked in
`_to_delete/probes-20260829/`.

    hyphen          RULE16: UNPROVEN - reason        ACCEPTED
    em dash         RULE16: UNPROVEN — reason        ACCEPTED
    colon           RULE16: UNPROVEN: reason         ACCEPTED
    no spaces       RULE16:UNPROVEN-reason           ACCEPTED
    extra spaces    RULE16:   UNPROVEN   -   reason  ACCEPTED
    inside a JSDoc   * RULE16: UNPROVEN - reason     ACCEPTED
    mid-sentence    ...see also RULE16: UNPROVEN - r ACCEPTED

    comma           RULE16: UNPROVEN, reason         MALFORMED
    semicolon       RULE16: UNPROVEN; reason         MALFORMED
    EN dash         RULE16: UNPROVEN – reason        MALFORMED
    other verdict   RULE16: PARTIAL - reason         MALFORMED
    short reason    RULE16: UNPROVEN - too short     REJECTED (9 < 30 chars)
    lowercase       rule16: unproven - reason        NOT SEEN AT ALL  (§5)

**THE SEPARATOR IS THREE CHARACTERS, NOT ONE.** Hyphen, em dash and colon all
pass. Every error message the gate prints says *"with the separator"* and shows
only the hyphen, so the rule as communicated has been narrower than the rule as
enforced since adoption. **That is not a defect — it is a documentation gap, and
this document is the fix.**

## 4. THE EN DASH IS THE REAL TRAP, AND IT IS WORSE THAN THE COMMA

    ACCEPTED   RULE16: UNPROVEN — reason      em dash   U+2014
    MALFORMED  RULE16: UNPROVEN – reason      en dash   U+2013

**These are one pixel apart in most editors and the gate treats them
oppositely.** The comma cost two people an hour across 2026-08-27 and 28, and a
comma is at least visible. The en dash is not, and the gate's own error message
prints the offending line back — where it looks correct.

The comma was fixed the right way: the gate now separates PRESENT-BUT-MALFORMED
from ABSENT, so a reader is no longer sent looking for a label in a file that
has one. **The en dash lands in that same improved path and reads correctly to
the eye.** Anyone who hits it should suspect the character before the code.

## 5. THE ONE ACTUAL HOLE, FOUND WHILE WRITING THIS

**A lowercase label is not seen as a label at all.**

    checks/_verify_zz_probe_lowercase.py
      -> "a NEW check with no RULE16 label"

The regex is case-sensitive, and so is the fallback that detects a malformed
label — it looks for the literal string `RULE16`. So `rule16: unproven - ...`
produces neither a match nor a MALFORMED report: it is classified as
**unlabelled**.

**That matters because `rule16_baseline.txt` excuses unlabelled files.** The
baseline is checked only against the reason `"no RULE16: line"`
(`_verify_rule16_labels.py:167`), which is exactly what a lowercase label
produces. A file on the baseline carrying a lowercase label would be **silently
excused while appearing to have declared itself** — a check that reports nothing
wrong because it never recognised the thing it was looking at.

It fails today only because the debt list is closed and a NEW unlabelled check is
refused outright. **That is a second guard catching it, not the label logic
working.**

**Not fixed in this item.** Q25 is to record what the gate does, and changing it
would make this document stale on the day it was written. The fix is one word —
make the loose detector case-insensitive so a lowercase label reports MALFORMED
rather than absent — and it is mine to make when it is asked for.

## 6. THE RULES THAT ARE NOT ABOUT THE SEPARATOR

**Exactly one label per file.** Two matches in the first 60 lines is an error:
*"a check has one status"*. Because the gate uses `search` rather than `match`,
**prose that quotes the format counts as a label** — a file explaining
`RULE16: UNPROVEN - ...` in a comment has two, and fails. This document is safe
only because it is not in `checks/`.

**The reason may wrap, and the gate follows it.** Continuation lines are joined
while they are non-empty, start with whitespace or a leading `*`, and do not open
`"""` or `/*`. Leading `*` is stripped, whitespace collapsed. The first version
read only the matched line and printed half-sentences; the reason IS the
deliverable, so truncating it defeated the rule.

**A reason under 30 characters is refused**, with the verdict parsed and
discarded: *"a label that says nothing is worse than no label, because it looks
done"*.

**`rule16_baseline.txt` can only shrink.** It excuses files that predate
adoption. It never excuses a MALFORMED label, and it never accepts an addition —
a new check without a label fails outright. **The list is empty as of
2026-08-29** and the file records why.

## 7. WHERE THE GATE ITSELF IS UNPROVEN

Its own label says it: *"this gate reads the DECLARATION, never the truth of it."*
It confirms a file claims INDEPENDENT; it cannot confirm the claim is true. A
control that labels itself INDEPENDENT while reading its subject's own output
passes here. **That gap is structural and no format document closes it** — only a
reader checking the reason against what the control actually does.

## 8. STATUS AT THE TIME OF WRITING

    RULE 16 LABELS - 105 check(s)
      labelled            105  (56 INDEPENDENT, 49 UNPROVEN)
      unlabelled          0
      malformed label     0
      baseline gaps       0
