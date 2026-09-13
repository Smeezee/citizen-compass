#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_owner_asks.py - rule 27, made to catch us. A letter that asks Sleven for
a manual step must show it ran the owner-ask gate first.

RULE16: INDEPENDENT - the expectation (an `Owner-action:` line, and an
`Already checked` heading under any ask) is taken from rule 27's own text in
CLAUDE.md and the accepted proposal; the subject is letters the desks wrote. The
router's header and signature rules are RESTATED here, not imported from
watcher-go/memo.go, the same way _verify_correspondence.py restates them.

Built 2026-09-13 on Architecture's GO (`..._b2-is-ordered-plus-two-controls-that-
only-needed-my-word.md`), to `claude/PROPOSAL_the-owner-ask-control-2026-09-12.md`.
Ruled RED: a defect here turns the sweep red. The backlog is never red.

WHY A FIELD AND NOT A PHRASE LIST. Measured on the real owner tray, 2026-09-12:
the phrase list's loudest hit was the letter ANNOUNCING rule 27, because it
quotes the rule, and a real ask ("may I swap") matched no phrase at all. Wrong
in both directions. Rule 27 already requires the ask to be ONE LINE; the field is
only a fixed place for that line:

    Owner-action: none
    Owner-action: <the one-line ask>

THE POPULATION

  correspondence/open/owner/*.md and inbox/*_memo_owner_*.md. Only memos (To,
  From and Subject all present in the first 4000 bytes) whose To: is owner and
  whose From: is not. `Owner (Sleven)` is owner - the router's signature rule.
  correspondence/answered/ is out of scope: those asks are already dealt with.

THE VERDICTS

  ASK WITHOUT CHECK   Owner-action: is an ask and no qualifying heading   DEFECT
  UNDECLARED          no Owner-action:, filename date >= CUTOFF          DEFECT
  BACKLOG             no Owner-action:, before CUTOFF                    one line
  CLEAN               none, or an ask plus a qualifying heading          quiet

  A QUALIFYING HEADING is a line that is `#`..`######` plus a space, or `**`,
  then `Already checked` (case-insensitive, an optional `:` and closing `**`),
  outside any code fence and not quoted. The text under it, up to the next `#`
  heading or `---` rule, must hold at least 20 non-whitespace characters - the
  same floor as an ANSWERS: or CLOSED: record, so a bare heading does not pass.

  NORMALISATION, STATED (RULE 17): the field NAME and the heading words are
  matched case-insensitively, and the value is trimmed. `none` in any case means
  no ask. An empty value is UNDECLARED, never an ask. Nothing else is folded.

THE CUTOFF - AND WHY IT IS EMPTY TODAY

  The proposal fixed the cutoff as the date `correspondence/README.md` first
  documents the field. Architecture's scope condition: only letters filed AFTER
  rule 27 landed on 2026-09-12 are judged. Both hold here.

  MEASURED 2026-09-13 03:5x: the README does not mention `Owner-action:`, and 0
  of 60 owner-tray letters carry it. A field cannot be required before the
  procedure names it - a cutoff typed today would turn the sweep red on
  Architecture's own 09-13 letters for a field nobody had been told existed.

  So CUTOFF is None until the procedure documents the field, and while it is:

    UNDECLARED is NOT IN FORCE. Every undeclared letter is backlog, one line.
    ASK WITHOUT CHECK is fully in force - any letter carrying an ask is judged.

  AND FORGETTING TO SET IT IS ITSELF RED. The moment the README documents the
  field while CUTOFF is still None, this control fails with NO CUTOFF. A cutoff
  on or before 2026-09-12 fails with CUTOFF TOO EARLY. Neither can go quiet.

WHAT IT CANNOT KNOW - printed on every run

  - a letter that declares `none` and asks anyway, in prose
  - whether the `Already checked` list is TRUE (presence and substance only)
  - asks made outside letters: a chat reply is not on disk

Never edits, moves or holds a letter. The router is untouched.

Rule 15: every open below states encoding="utf-8".

Usage:
    python checks/_verify_owner_asks.py
    python checks/_verify_owner_asks.py --self-test
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORR = os.path.join(ROOT, "correspondence")
INBOX = os.path.join(ROOT, "inbox")
PROCEDURE = os.path.join(CORR, "README.md")

# The date the procedure first documents `Owner-action:`, as YYYY-MM-DD. None
# until it does - see THE CUTOFF above. Set it once, with the reason beside it.
CUTOFF = None

# Rule 27 landed in CLAUDE.md on this date. Filename dates are whole days, so a
# cutoff must be strictly AFTER it to judge only letters written under the rule.
RULE27_LANDED = "2026-09-12"

HEAD = 4000
SUBSTANCE = 20

RE_TO = re.compile(r"(?im)^To:\s*(.+?)\s*$")
RE_FROM = re.compile(r"(?im)^From:\s*(.+?)\s*$")
RE_SUBJECT = re.compile(r"(?im)^Subject:\s*(.+?)\s*$")
RE_OWNER_ACTION = re.compile(r"(?im)^Owner-action:[ \t]*(.*?)[ \t]*$")
RE_FILE_DATE = re.compile(r"^(20\d{2}-\d{2}-\d{2})")
RE_CHECKED = re.compile(
    r"(?i)^(?:#{1,6}[ \t]+|\*\*)[ \t]*already checked[ \t]*:?[ \t]*(?:\*\*)?[ \t]*:?[ \t]*$")
RE_SECTION_END = re.compile(r"^(?:#{1,6}[ \t]+\S|-{3,}[ \t]*$)")
RE_FENCE = re.compile(r"^[ \t]*(?:```|~~~)")

# The router's signature rule, restated (see _verify_correspondence.py): one
# trailing parenthetical after a non-empty name is a signature, not the address.
RE_SIGNATURE = re.compile(
    r"^(.*[^ \t\n\f\r])[ \t\n\f\r]+(\([^()]*\))[ \t\n\f\r]*$")


def strip_signature(addr):
    addr = addr.strip()
    m = RE_SIGNATURE.match(addr)
    return m.group(1) if m else addr


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def parse(text):
    head = text[:HEAD]
    to, frm, subj = RE_TO.search(head), RE_FROM.search(head), RE_SUBJECT.search(head)
    if not (to and frm and subj):
        return None
    return {"to": strip_signature(to.group(1)).lower(),
            "from": strip_signature(frm.group(1)).lower()}


def has_checked_heading(text):
    """An `Already checked` heading, outside fences and quotes, with substance."""
    lines = text.splitlines()
    fenced = False
    for i, line in enumerate(lines):
        if RE_FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or not RE_CHECKED.match(line):
            continue
        substance = 0
        for body in lines[i + 1:]:
            if RE_SECTION_END.match(body):
                break
            substance += len(re.sub(r"\s", "", body))
        if substance >= SUBSTANCE:
            return True
    return False


def procedure_names_field(procedure):
    if not os.path.isfile(procedure):
        return None
    return "owner-action:" in read(procedure).lower()


def population(corr_dir, inbox_dir):
    tray = os.path.join(corr_dir, "open", "owner")
    paths = []
    if os.path.isdir(tray):
        paths += sorted(os.path.join(tray, n) for n in os.listdir(tray)
                        if n.lower().endswith(".md"))
    if inbox_dir and os.path.isdir(inbox_dir):
        paths += sorted(os.path.join(inbox_dir, n) for n in os.listdir(inbox_dir)
                        if n.lower().endswith(".md") and "_memo_owner_" in n)
    return paths


def judge(corr_dir, inbox_dir, procedure, cutoff):
    """Returns (defects, backlog, counts, documented). Read-only."""
    defects, backlog = [], []
    counts = {"memos": 0, "in_scope": 0, "none": 0, "asks": 0, "undeclared": 0}
    documented = procedure_names_field(procedure)
    if documented is None:
        defects.append("PROCEDURE MISSING - %s is not on disk, so whether the "
                       "field is documented cannot be read" % procedure)
    if cutoff is not None and cutoff <= RULE27_LANDED:
        defects.append("CUTOFF TOO EARLY - CUTOFF is %s; it must be after %s, "
                       "the day rule 27 landed" % (cutoff, RULE27_LANDED))
    if documented and cutoff is None:
        defects.append("NO CUTOFF - %s documents `Owner-action:` but CUTOFF is "
                       "None, so a letter missing the field is judged by "
                       "nothing. Set CUTOFF to the date the procedure first "
                       "documented it." % os.path.basename(procedure))

    for path in population(corr_dir, inbox_dir):
        text = read(path)
        m = parse(text)
        if m is None:
            continue  # not a memo; _verify_correspondence owns that finding
        counts["memos"] += 1
        if m["to"] != "owner" or m["from"] == "owner":
            continue
        counts["in_scope"] += 1
        name = os.path.basename(path)
        field = RE_OWNER_ACTION.search(text[:HEAD])
        value = field.group(1).strip() if field else ""
        if value.lower() == "none":
            counts["none"] += 1
            continue
        if value:
            counts["asks"] += 1
            if not has_checked_heading(text):
                defects.append(
                    "ASK WITHOUT CHECK - %s: `Owner-action: %s` and no "
                    "`Already checked` heading with %d+ characters under it. "
                    "Rule 27: run the gate, list what was checked, then ask."
                    % (name, value, SUBSTANCE))
            continue
        counts["undeclared"] += 1
        d = RE_FILE_DATE.match(name)
        if cutoff is None:
            backlog.append(name)
        elif not d:
            defects.append("UNDATED - %s: no ISO date at the front of its "
                           "filename, so the cutoff cannot place it" % name)
        elif d.group(1) >= cutoff:
            defects.append(
                "UNDECLARED - %s: filed %s, on or after the cutoff %s, with no "
                "`Owner-action:` line. Add `Owner-action: none` or the "
                "one-line ask." % (name, d.group(1), cutoff))
        else:
            backlog.append(name)
    return defects, backlog, counts, documented


def run(corr_dir, inbox_dir, procedure, cutoff):
    defects, backlog, c, documented = judge(corr_dir, inbox_dir, procedure, cutoff)
    print("owner asks: %d memo(s) read, %d from a desk to owner - %d declare "
          "none, %d carry an ask, %d carry no field"
          % (c["memos"], c["in_scope"], c["none"], c["asks"], c["undeclared"]))
    if cutoff is None:
        print("UNDECLARED is NOT IN FORCE: %s does not yet document "
              "`Owner-action:`, and a field cannot be required before the "
              "procedure names it. ASK WITHOUT CHECK is in force."
              % os.path.relpath(procedure, os.path.dirname(corr_dir)))
    if backlog:
        print("BACKLOG - %d letter(s) with no `Owner-action:` line, %s. "
              "Reported once, never per letter, never red."
              % (len(backlog), "before the cutoff %s" % cutoff if cutoff
                 else "while the field is not in force"))
    if c["asks"] == 0:
        print("NOTHING TO JUDGE YET - no letter carries an ask, so ASK WITHOUT "
              "CHECK had no subject this run. Green here is empty, not proven "
              "on real mail.")
    print("CANNOT KNOW: a letter that declares none and asks in prose; whether "
          "an Already checked list is true; asks made in chat.")
    return defects


def self_test():
    """Plant every verdict both ways in temporary trays; every one must land."""
    import tempfile
    import shutil

    print("SELF-TEST - the trays below are planted\n")
    caught, total = 0, 0
    tmp = tempfile.mkdtemp(prefix="cc-owner-asks-selftest-")
    try:
        corr = os.path.join(tmp, "correspondence")
        tray = os.path.join(corr, "open", "owner")
        inbox = os.path.join(tmp, "inbox")
        os.makedirs(tray)
        os.makedirs(inbox)
        documented = os.path.join(tmp, "README-documented.md")
        silent = os.path.join(tmp, "README-silent.md")
        io.open(documented, "w", encoding="utf-8", newline="").write(
            "Every letter to owner carries `Owner-action: none` or the ask.\n")
        io.open(silent, "w", encoding="utf-8", newline="").write(
            "The trays. open/owner is Sleven's.\n")

        def memo(to="Owner", frm="Build", action=None, body="Body text.\n"):
            field = "" if action is None else "Owner-action: %s\n" % action
            return ("# Memo\n\nTo:      %s\nFrom:    %s\nSubject: planted\n"
                    "Status:  Open\n%s\n%s" % (to, frm, field, body))

        CHECKED = ("## Already checked\n\n- the swap script: covers only the "
                   "watcher binary\n- the guard exception: .md only\n")
        RULE27 = ("> A manual step means anything that puts his hands in the "
                  "machine: a terminal command, a commit, a click, a password, "
                  "your word. Open a terminal. At the keyboard. Approve.\n")

        def put(where, name, text):
            io.open(os.path.join(where, name), "w", encoding="utf-8",
                    newline="").write(text)

        # (file, text, expected) - expected is a verdict word, or None for quiet
        planted = [
            ("2026-09-14_p01_ask-no-heading.md",
             memo(action="commit the watcher source"), "ASK WITHOUT CHECK"),
            ("2026-09-14_p02_ask-thin-heading.md",
             memo(action="swap it", body="## Already checked\n\nnone.\n\n## Next\n\n"
                  "A long paragraph that is not under the heading at all.\n"),
             "ASK WITHOUT CHECK"),
            ("2026-09-14_p03_ask-quoted-heading.md",
             memo(action="swap it", body="> ## Already checked\n> - the swap "
                  "script, the guard exception and the owner orders; none "
                  "covers it.\n"), "ASK WITHOUT CHECK"),
            ("2026-09-14_p04_ask-with-heading.md",
             memo(action="swap it", body=CHECKED), None),
            ("2026-09-14_p05_none.md", memo(action="none"), None),
            ("2026-09-14_p05b_none-mixed-case.md", memo(action="NoNe"), None),
            ("2026-09-14_p06_undeclared.md", memo(), "UNDECLARED"),
            ("2026-09-01_p07a_backlog.md", memo(), None),
            ("2026-09-02_p07b_backlog.md", memo(), None),
            ("2026-09-03_p07c_backlog.md", memo(), None),
            ("2026-09-14_p08_from-owner.md", memo(frm="Owner (Sleven)"), None),
            ("2026-09-14_p09_signed-to-owner.md",
             memo(to="Owner (Sleven)", action="push main"), "ASK WITHOUT CHECK"),
            ("2026-09-14_p11_empty-value.md", memo(action=""), "UNDECLARED"),
            ("2026-09-14_p12_quotes-rule-27.md",
             memo(action="none", body=RULE27), None),
            ("2026-09-14_p13_fenced-heading.md",
             memo(action="swap it", body="```\n" + CHECKED + "```\n"),
             "ASK WITHOUT CHECK"),
            ("2026-09-14_p14_to-build.md", memo(to="Build"), None),
            ("BOARD.md", "# Owner board\n\nNot a memo. To: nobody.\n", None),
        ]
        for name, text, _e in planted:
            put(tray, name, text)
        put(inbox, "2026-09-14_p10_memo_owner_inbox-ask.md",
            memo(action="type this"))
        put(inbox, "2026-09-14_not-for-owner_memo_build_x.md",
            memo(action="type this"))
        planted.append(("2026-09-14_p10_memo_owner_inbox-ask.md", None,
                        "ASK WITHOUT CHECK"))
        planted.append(("2026-09-14_not-for-owner_memo_build_x.md", None, None))

        def mark(ok, name, what):
            print("  %-7s %-42s %s" % ("caught" if ok else "MISSED", name, what))
            return 1 if ok else 0

        # RUN A - the field is documented and the cutoff is set.
        defects, backlog, _c, _d = judge(corr, inbox, documented, "2026-09-13")
        for name, _t, expected in planted:
            total += 1
            hits = [d for d in defects if name in d]
            if expected:
                ok = len(hits) == 1 and hits[0].startswith(expected)
                caught += mark(ok, name, "must be %s" % expected)
            else:
                caught += mark(not hits, name, "must be quiet")
        total += 1
        want = {"2026-09-01_p07a_backlog.md", "2026-09-02_p07b_backlog.md",
                "2026-09-03_p07c_backlog.md"}
        caught += mark(set(backlog) == want, "backlog",
                       "exactly the three pre-cutoff letters, as ONE line")

        # RUN B - the field is documented and nobody set the cutoff.
        defects, _b, _c, _d = judge(corr, inbox, documented, None)
        total += 1
        caught += mark(any(d.startswith("NO CUTOFF") for d in defects),
                       "no-cutoff", "a documented field with no cutoff is red")

        # RUN C - the field is not documented: UNDECLARED is not in force,
        # and an ask is still judged.
        defects, backlog, _c, _d = judge(corr, inbox, silent, None)
        total += 1
        caught += mark(not any(d.startswith(("UNDECLARED", "NO CUTOFF"))
                               for d in defects)
                       and "2026-09-14_p06_undeclared.md" in backlog,
                       "not-in-force", "undeclared is backlog, never red")
        total += 1
        caught += mark(any("p01_ask-no-heading" in d for d in defects),
                       "asks-still-judged", "an ask is judged with no cutoff")

        # RUN D - a cutoff on the day rule 27 landed would judge its own day.
        defects, _b, _c, _d = judge(corr, inbox, documented, RULE27_LANDED)
        total += 1
        caught += mark(any(d.startswith("CUTOFF TOO EARLY") for d in defects),
                       "cutoff-too-early", "a cutoff not after rule 27 is red")

        print("\n%d of %d planted verdicts landed." % (caught, total))
        if caught != total:
            print("SELF-TEST FAILED - this control missed a case it is "
                  "supposed to catch, so it must not be trusted.")
            return 3
        print("SELF-TEST PASSED - every planted verdict landed.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--self-test" in argv:
        return self_test()
    defects = run(CORR, INBOX, PROCEDURE, CUTOFF)
    if defects:
        print("\n%d finding(s):" % len(defects))
        for d in defects:
            print("  - %s" % d)
        print("RED.")
        return 1
    print("\nPASS - every ask to owner in the trays shows the gate was run.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
