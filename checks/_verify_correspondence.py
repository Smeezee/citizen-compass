#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_correspondence.py - the memo trays hold to the procedure.

RULE16: INDEPENDENT - the rules asserted here come from
`correspondence/README.md`, which is the procedure a HUMAN follows, and they are
spelled out in this file rather than imported from `watcher-go/memo.go`. Nothing
of the router's is taken on trust: if `memo.go` and the README ever disagree
about what a memo is, this control sides with the README and says so. The four
desks are named HERE, with a drift assertion against the README's own list, so
this cannot quietly stop matching the procedure it exists to enforce.

Q47. Until 2026-08-30 a question from the builder to the architect reached its
destination only if the owner read a status report, spotted the question inside
it, and carried it across by hand. The trays end that. This control is what
stops them becoming a folder nobody trusts.

WHAT IT REFUSES, AND WHY EACH ONE MATTERS

  a memo with no To/From/Subject      The README requires all three, precisely
                                      so an ordinary document containing the
                                      word "To:" is not posted to a desk. A file
                                      in a tray that is not a memo means the
                                      router filed something it should not have.

  a memo addressed to no real desk    "A letter delivered to the wrong desk is
                                      worse than one that visibly failed to
                                      arrive." An unknown addressee belongs in
                                      _needs_review, never in a tray.

  a memo in the WRONG desk's tray     open/build/ holding a memo addressed to
                                      Architecture is a letter nobody will read:
                                      the builder skips it as not theirs and the
                                      architect never looks in that drawer.

  an answered memo with no answer     Status: Answered with nothing under an
                                      ANSWERS: line is the filing equivalent of
                                      a green check that never looked. It leaves
                                      the tray, so it stops being visible, and
                                      it contains nothing.

  a closed memo with no record        Status: Closed or Done needs EITHER an
                                      ANSWERS: or a CLOSED: line, 20+ characters
                                      under it. A finished thread is not always
                                      an answered question, so the control does
                                      not demand an answer - but it does demand
                                      a record. (Architecture's order,
                                      2026-09-12: this docstring said Answered
                                      and the code applied the rule to Answered,
                                      Closed and Done alike. The divergence was
                                      the defect.)

  an ANSWERED memo still in open/     unless it is in the tray of the desk that
  (the tray of a DIFFERENT desk)      SENT it, which is the router delivering an
                                      answer - reported as waiting, never failed
                                      (Owner's order, 2026-09-11). Closed and
                                      Done in an open tray still fail anywhere.
  an ANSWERED memo still in open/     and an OPEN memo in answered/. Either way
                                      the tray no longer means what it says.

  UNDELIVERED POST left in the        A memo to a desk that does not exist is
  bounce folder                       REFUSED and filed to _needs_review/ with
                                      the reason on it. That half works. The
                                      recovery half did not exist: nothing
                                      watched the folder, nothing reported it,
                                      and no boot sequence read it - so a
                                      bounced memo stayed bounced until a person
                                      happened to open the folder. The sender
                                      believes it was delivered and the
                                      recipient never knew it existed.

                                      THE PATH. The audit desk reported it as
                                      `correspondence/_needs_review/`. That
                                      folder does not exist. The router's real
                                      one is `_needs_review/` AT THE REPO ROOT -
                                      watcher-go/main.go:113 - and this control
                                      asserts on the path the router actually
                                      uses, not the one it was described as.

                                      NARROW ON PURPOSE: a `To:` header, not
                                      "anything in the folder". That folder
                                      legitimately holds old handoff text,
                                      status files and rescale reports, and a
                                      control that fired on those would cry wolf
                                      and be switched off inside a week.
                                      Measured 2026-09-09: 25 files in there, 0
                                      carrying a To: header. Undelivered post is
                                      the thing with a NAME ON IT that nobody is
                                      coming for.

WHAT IT DOES *NOT* REFUSE, ON PURPOSE

  AN OPEN MEMO IS REPORTED, NEVER FAILED. Q47 says so and the README says why:
  "NOBODY STOPS WORKING TO WAIT FOR A REPLY... A question sitting in a tray
  costs nothing." A control that went red on an unanswered letter would turn
  every question into a thing that blocks a deploy, and the immediate result
  would be that people stop writing memos. That is the opposite of the point.

  So open memos are printed, with their age, and the exit stays 0.

  TRAY DEPTH AND THE OLDEST LETTER ARE REPORTED, NEVER FAILED, for the same
  reason and one more. This desk was carrying 41 unanswered letters, the oldest
  from 30 August, and nothing in the system ever asked about them. Sleven's
  words: "a tray nobody is ever asked about fills up - that is not a failure of
  yours, it is a gap in the machine." The same gap exists on every desk with a
  mailbox, which is why the count goes in the check rather than in one desk's
  habits. A number nobody is shown is a number nobody acts on.

Rule 15: every read below is opened with encoding="utf-8".

Usage:
    python checks/_verify_correspondence.py
    python checks/_verify_correspondence.py --self-test
"""
import io
import os
import re
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CORR = os.path.join(ROOT, "correspondence")

# THE BOUNCE FOLDER, AT THE PATH THE ROUTER ACTUALLY USES.
# watcher-go/main.go:113 -- needsReviewDir = filepath.Join(projectRoot,
# "_needs_review") -- so it is at the REPO ROOT, not under correspondence/.
# It is named here rather than imported, like everything else in this file:
# if the router ever moves it, this control goes looking in the old place and
# says the folder is missing, which is the finding.
NEEDS_REVIEW = os.path.join(ROOT, "_needs_review")

# THE FOUR DESKS, NAMED HERE RATHER THAN IMPORTED. See the RULE16 note. The
# drift assertion below holds this list to correspondence/README.md, so a fifth
# desk added to the procedure fails this control instead of being silently
# unenforced.
#
# `audit` added 2026-09-08. THE DRIFT ASSERTION BELOW IS WHAT TOLD ME. I added
# the desk to the watcher's routing map, deployed it, sent a memo to prove the
# tray received post - and this control went red on the next sweep saying
# "README.md names a tray 'audit' that this control does not know about, so
# nothing is checking it".
#
# That is the assertion doing precisely the job it was written for. Three
# places had to learn about the new desk - the procedure, the router and the
# checker - and the only one that would have stayed silent is the checker.
DESKS = ("engineering", "build", "research", "audit", "design", "owner")

# A memo is a memo only with all three. Straight out of the README:
# "`To:`, `From:` and `Subject:` are all required."
RE_TO = re.compile(r"(?im)^To:\s*(.+?)\s*$")
RE_FROM = re.compile(r"(?im)^From:\s*(.+?)\s*$")
RE_SUBJECT = re.compile(r"(?im)^Subject:\s*(.+?)\s*$")
RE_STATUS = re.compile(r"(?im)^Status:\s*(.+?)\s*$")
RE_DATE = re.compile(r"(?im)^Date:\s*(20\d{2}-\d{2}-\d{2})\s*$")
RE_ANSWERS = re.compile(r"(?im)^\s*(?:\*\*)?ANSWERS:")
# The record a FINISHED thread may carry instead of an answer. Same shape
# as ANSWERS: on purpose, so one is not easier to fake than the other.
RE_CLOSED = re.compile(r"(?im)^\s*(?:\*\*)?CLOSED:")

# THE ROUTER'S SIGNATURE RULE, RESTATED RATHER THAN IMPORTED (RULE16).
# Architecture's order, 2026-09-12, built into the watcher at 03:17: one
# trailing parenthetical after a non-empty name is a SIGNATURE, not part of the
# address - `To: Owner (Sleven)` is addressed to owner. Same pattern as
# watcher-go/memo.go reSignature, with Go's ASCII \s and \S spelled out so the
# two cannot differ on a Unicode space. An address that is ONLY a parenthetical
# is left whole and fails as an unknown desk; nothing is stripped to nothing.
#
# FOUND 2026-09-12 06:24: the router learned this rule and this control did
# not, so three correctly-filed letters to `Owner (Sleven)` went red here as
# "not a desk". Router and checker disagreeing is the finding; this closes it.
RE_SIGNATURE = re.compile(
    r"^(.*[^ \t\n\f\r])[ \t\n\f\r]+(\([^()]*\))[ \t\n\f\r]*$")


def strip_signature(addr):
    """The address without a trailing signature, exactly as the router reads it."""
    addr = addr.strip()
    m = RE_SIGNATURE.match(addr)
    return m.group(1) if m else addr


ANSWERED_WORDS = ("answered", "closed", "done")
# The two end states that need a RECORD rather than an ANSWER.
CLOSED_WORDS = ("closed", "done")

# The header is at the top of a letter or it is not a header. Same 4000-byte
# reasoning the router uses, restated rather than imported: a memo quoted inside
# a long document must not be read as that document's address.
HEAD = 4000


def read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def memo_files(d):
    """Every .md in a tray. `.keep` and anything else is not a memo."""
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, n) for n in os.listdir(d)
                  if n.lower().endswith(".md"))


def parse(text):
    head = text[:HEAD]
    to = RE_TO.search(head)
    frm = RE_FROM.search(head)
    subj = RE_SUBJECT.search(head)
    if not (to and frm and subj):
        return None
    st = RE_STATUS.search(head)
    dt = RE_DATE.search(head)
    return {
        "to": strip_signature(to.group(1)).lower(),
        "from": strip_signature(frm.group(1)),
        "subject": subj.group(1).strip(),
        "status": (st.group(1).strip().lower() if st else "open"),
        # The letter's own Date: header when it has one. None means the age has
        # to come from the filesystem, and the report says which it used - a
        # date this control guessed would be worse than no date.
        "date": (dt.group(1) if dt else None),
    }


def answer_body(text):
    """What is written UNDER the ANSWERS: line, if anything."""
    m = RE_ANSWERS.search(text)
    if not m:
        return None
    return text[m.end():].strip()


def closed_body(text):
    """What is written UNDER the CLOSED: line, if anything."""
    m = RE_CLOSED.search(text)
    if not m:
        return None
    return text[m.end():].strip()


def audit(corr_dir, report):
    """Returns (failures, open_memos). Never raises on a missing tray."""
    fails = []
    opens = []

    # ---- the trays exist ---------------------------------------------------
    if not os.path.isdir(corr_dir):
        fails.append("correspondence/ does not exist - the trays are the whole "
                     "mechanism and there is nowhere to file")
        return fails, opens
    for desk in DESKS:
        d = os.path.join(corr_dir, "open", desk)
        if not os.path.isdir(d):
            fails.append("open/%s/ is missing - a memo to that desk has "
                         "nowhere to land" % desk)
    if not os.path.isdir(os.path.join(corr_dir, "answered")):
        fails.append("answered/ is missing - an answered memo has nowhere to go")

    # ---- open trays --------------------------------------------------------
    for desk in DESKS:
        for p in memo_files(os.path.join(corr_dir, "open", desk)):
            rel = os.path.relpath(p, ROOT)
            m = parse(read(p))
            if m is None:
                fails.append("%s is in a tray but is NOT A MEMO - no To/From/"
                             "Subject in its first %d bytes. The router filed "
                             "something that is not a letter." % (rel, HEAD))
                continue
            # A RETURNED ANSWER IS NOT A DEFECT. Ordered by Owner
            # 2026-09-11, and taken from the router rather than from a new
            # rule of this control's own. watcher-go/memo.go files by status:
            #
            #     Status: Open      ->  open/<To:>     the question going out
            #     Status: Answered  ->  open/<From:>   the answer coming back
            #     Status: Closed    ->  answered/      the thread is finished
            #
            # So an Answered memo in the tray of the desk that SENT it is the
            # router working, and it stays there until the sender has read it
            # and closed it. Before this, every answer the router delivered
            # failed twice - once for To: not matching the tray, once for
            # being answered in an open tray - and stayed red until closed.
            # A control that goes red on a letter waiting to be read trains
            # everyone to ignore red, which is what this control's own header
            # says about unanswered letters.
            returned = (m["status"] == "answered"
                        and m["from"].strip().lower() == desk)
            if m["to"] not in DESKS:
                fails.append("%s is addressed to %r, which is not a desk. An "
                             "unknown addressee belongs in _needs_review, not "
                             "in a tray." % (rel, m["to"]))
            elif m["to"] != desk and not returned:
                fails.append("%s sits in open/%s/ but is addressed to %r. "
                             "Nobody will read it: %s skips it as not theirs "
                             "and %s never looks in that drawer."
                             % (rel, desk, m["to"], desk, m["to"]))
            if m["status"] in ANSWERED_WORDS and not returned:
                fails.append("%s is marked %r but is still in an OPEN tray. "
                             "The tray no longer means what it says."
                             % (rel, m["status"]))
            else:
                # Returned answers land here too, and are REPORTED as waiting
                # rather than failed. Note what is NOT relaxed: `returned` is
                # only ever true for the exact word "answered", so Closed and
                # Done in an open tray still fail, in the sender's tray as
                # much as anywhere else - those belong in answered/.
                opens.append((rel, desk, m, p))

    # ---- answered ----------------------------------------------------------
    for p in memo_files(os.path.join(corr_dir, "answered")):
        rel = os.path.relpath(p, ROOT)
        text = read(p)
        m = parse(text)
        if m is None:
            fails.append("%s is in answered/ but is NOT A MEMO - no To/From/"
                         "Subject." % rel)
            continue
        if m["to"] not in DESKS:
            fails.append("%s is addressed to %r, which is not a desk."
                         % (rel, m["to"]))
        if m["status"] not in ANSWERED_WORDS:
            fails.append("%s is in answered/ but its Status is %r. An open "
                         "memo filed as answered is a question nobody will "
                         "ever see again." % (rel, m["status"]))
        body = answer_body(text)
        if m["status"] in CLOSED_WORDS:
            # A FINISHED thread: an answer OR a closing record will do, and
            # one of them must be there. Not a bare exemption.
            cbody = closed_body(text)
            have = [b for b in (body, cbody) if b is not None]
            if not have:
                fails.append("%s is filed as %r and carries neither an "
                             "ANSWERS: nor a CLOSED: line. A finished thread "
                             "with no record is as invisible as an unanswered "
                             "one." % (rel, m["status"]))
            elif max(len(b) for b in have) < 20:
                fails.append("%s has a closing marker with under 20 "
                             "characters under it. That is a tick, not a "
                             "record." % rel)
        else:
            # ANSWERED: an answer, specifically. A CLOSED: line does NOT
            # substitute - an answered question owes its answer.
            if body is None:
                fails.append("%s is filed as answered and carries no ANSWERS: "
                             "line. It left the tray, so it is no longer "
                             "visible, and it contains no answer." % rel)
            elif len(body) < 20:
                fails.append("%s has an ANSWERS: line with %d character(s) "
                             "under it. That is a tick, not an answer."
                             % (rel, len(body)))

    # ---- THE SAME MEMO IN TWO PLACES AT ONCE -------------------------------
    #
    # FOUND ON THE LIVE TRAYS, 2026-08-30, minutes after the router went in.
    # Answering a memo filed the answer to answered/ and LEFT THE ORIGINAL in
    # the open tray, so one question read as both answered and waiting:
    #
    #     open/owner/...watcher-binary-swap.md   4595 bytes  Status: Open
    #     answered/...watcher-binary-swap.md     5984 bytes  Status: Answered
    #
    # Every OTHER assertion in this control passed on that state, because each
    # tray is individually well-formed. It is only wrong when you look at both.
    # The watcher now sweeps the open copy; this is the check that says so if it
    # ever stops.
    open_names = {}
    for desk in DESKS:
        for p in memo_files(os.path.join(corr_dir, "open", desk)):
            open_names[os.path.basename(p)] = desk
    for p in memo_files(os.path.join(corr_dir, "answered")):
        b = os.path.basename(p)
        if b in open_names:
            fails.append("%s is in answered/ AND still in open/%s/. The same "
                         "question reads as answered and waiting at once, and "
                         "each tray looks fine on its own."
                         % (b, open_names[b]))

    return fails, opens


def drift_check(corr_dir):
    """The README still names exactly the desks this control enforces."""
    p = os.path.join(corr_dir, "README.md")
    if not os.path.isfile(p):
        return ["correspondence/README.md is missing - it IS the procedure, "
                "and without it this control is enforcing rules from nowhere"]
    text = read(p).lower()
    out = []
    for desk in DESKS:
        if ("open/%s" % desk) not in text:
            out.append("README.md no longer names the %r tray, but this "
                       "control still enforces it. One of the two has moved."
                       % desk)
    for m in re.findall(r"open/([a-z]+)", text):
        if m not in DESKS:
            out.append("README.md names a tray %r that this control does not "
                       "know about, so nothing is checking it." % m)
    return out


def bounced_post_check(needs_review_dir):
    """UNDELIVERED POST. Any file in the bounce folder carrying a To: header is
    a letter with a name on it that nobody is coming for.

    The refusal path works and has been proven twice over. This is the RECOVERY
    path, which did not exist: a bounced memo stayed bounced until a person
    happened to open the folder, and it was invisible in both directions - the
    sender believed it was delivered and the addressee never knew it existed.

    The window where that bites is precisely when a new desk is being stood up,
    which is when the traffic ABOUT that desk is heaviest. It has already
    happened twice in one day.

    Proving it can fail takes ten seconds and needs no fixture: drop a memo
    addressed to a desk that does not exist and this goes red. The self-test
    below does exactly that.
    """
    out = []
    if not os.path.isdir(needs_review_dir):
        # A folder the router creates on its first bounce. Absent means nothing
        # has ever bounced, which is the good state, not a finding.
        return out
    for dirpath, _dirnames, files in os.walk(needs_review_dir):
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            try:
                head = io.open(path, encoding="utf-8", errors="replace").read(HEAD)
            except OSError as e:
                out.append("%s could not be read (%s), so whether it is "
                           "undelivered post is unknown. Not reported as clear."
                           % (os.path.relpath(path, ROOT), type(e).__name__))
                continue
            to = RE_TO.search(head)
            if not to:
                continue
            full = bool(RE_FROM.search(head) and RE_SUBJECT.search(head))
            out.append(
                "%s is sitting in the bounce folder addressed to %r%s. It was "
                "REFUSED and filed here with the reason on it, and nothing has "
                "come back for it. The sender believes it was delivered and the "
                "addressee never knew it existed. Re-address it to a desk that "
                "exists and drop it in inbox/, or move it aside - rule 1 - once "
                "its content has been delivered another way."
                % (os.path.relpath(path, ROOT), to.group(1).strip(),
                   "" if full else " (a To: header, but not a complete memo)"))
    return out


def tray_depth(opens, now=None):
    """How many letters each tray is carrying, and how old the oldest is.

    FLAG ONLY, NEVER A GATE, and that is the ruling rather than a preference. An
    open memo does not block anything - "a question sitting in a tray costs
    nothing" - so this returns a report and never a failure.

    Rule 18: the clock is read from the machine, never estimated. Rule 11: where
    a letter carries no Date: header the age comes from the filesystem, and the
    report says WHICH it used rather than presenting a guess as a fact.
    """
    if now is None:
        now = datetime.date.today()
    by_desk = {}
    for rel, desk, m, path in opens:
        when = None
        source = None
        if m["date"]:
            try:
                when = datetime.date(*[int(x) for x in m["date"].split("-")])
                source = "Date:"
            except ValueError:
                when = None
        if when is None:
            when = datetime.date.fromtimestamp(os.path.getmtime(path))
            source = "mtime"
        by_desk.setdefault(desk, []).append((when, source, m["subject"], rel))
    rows = []
    for desk in sorted(by_desk):
        letters = sorted(by_desk[desk])
        oldest, source, subject, rel = letters[0]
        rows.append({"desk": desk, "count": len(letters), "oldest": oldest,
                     "age_days": (now - oldest).days, "source": source,
                     "subject": subject, "rel": rel})
    return rows


def run(corr_dir, needs_review_dir=None, label="correspondence"):
    print("%s: %s" % (label, corr_dir))
    fails = drift_check(corr_dir)
    more, opens = audit(corr_dir, True)
    fails += more
    fails += bounced_post_check(NEEDS_REVIEW if needs_review_dir is None
                                else needs_review_dir)

    if opens:
        print("\n%d memo(s) waiting for a reply - REPORTED, not failed:" % len(opens))
        for rel, desk, m, _path in opens:
            print("   %-10s %s" % (desk, m["subject"]))
            print("              %s  (from %s)" % (rel, m["from"]))
        print("   Nobody stops working to wait for a reply. These do not gate "
              "anything.")

        rows = tray_depth(opens)
        print("\nTRAY DEPTH - flag only, never a gate:")
        print("   %-14s %5s  %-12s %s" % ("desk", "open", "oldest", "age"))
        for r in rows:
            print("   %-14s %5d  %-12s %d day(s)   [%s]"
                  % (r["desk"], r["count"], r["oldest"].isoformat(),
                     r["age_days"], r["source"]))
        deepest = max(rows, key=lambda r: r["age_days"])
        print("   OLDEST LETTER IN THE SYSTEM: %s, %d day(s) old, on the %s "
              "desk - %s" % (deepest["oldest"].isoformat(), deepest["age_days"],
                             deepest["desk"], deepest["subject"]))
        print("   A tray nobody is ever asked about fills up. This is the "
              "asking.")
    else:
        print("\nno memo is waiting for a reply")

    return fails


def self_test():
    """Plant one of each defect and confirm every one is caught."""
    import tempfile
    import shutil

    print("SELF-TEST - every tray below is deliberately wrong\n")
    tmp = tempfile.mkdtemp(prefix="cc-corr-selftest-")
    try:
        for desk in DESKS:
            os.makedirs(os.path.join(tmp, "open", desk))
        os.makedirs(os.path.join(tmp, "answered"))
        # the README the drift check reads
        io.open(os.path.join(tmp, "README.md"), "w", encoding="utf-8",
                newline="").write(
            "open/engineering\nopen/build\nopen/research\nopen/owner\n")

        def put(rel, body):
            io.open(os.path.join(tmp, rel), "w", encoding="utf-8",
                    newline="").write(body)

        MEMO = ("# Memo\n\nTo:      %s\nFrom:    Build\n"
                "Date:    2026-08-30\nSubject: %s\nStatus:  %s\n\n%s")
        # From: is settable, because Owner's 2026-09-11 rule turns on whether
        # the SENDER owns the tray. With only the template above, every plant
        # was From: Build and the new rule could not be exercised in either
        # direction.
        MEMO_FROM = ("# Memo\n\nTo:      %s\nFrom:    %s\n"
                     "Date:    2026-08-30\nSubject: %s\nStatus:  %s\n\n%s")

        planted = [
            ("open/build/not-a-memo.md",
             "# Just a report\n\nIt mentions To: somebody, casually.\n",
             "is in a tray but is NOT A MEMO"),
            ("open/build/wrong-desk.md",
             MEMO % ("Engineering", "filed in the wrong drawer", "Open", "body"),
             "is addressed to"),
            ("open/build/unknown-desk.md",
             MEMO % ("Legal", "there is no legal desk", "Open", "body"),
             "which is not a desk"),
            # ANSWERED IN THE TRAY OF THE DESK IT WAS SENT TO, not sent
            # FROM. Still a failure - this is an answer parked in the
            # recipient's drawer, which the router never does.
            #
            # IT USED TO READ From: Build IN open/build/, and Owner's
            # 2026-09-11 rule makes that a legitimate returned answer - so
            # this plant would have quietly stopped failing and the
            # self-test would have reported a catch it no longer made.
            ("open/build/already-answered.md",
             MEMO_FROM % ("Build", "Engineering", "answered in the wrong "
                          "tray", "Answered", "body"),
             "still in an OPEN tray"),
            # CLOSED in an open tray, in the SENDER's own tray, which is the
            # one place the new rule could have been over-applied. Closed
            # belongs in answered/ and still fails here.
            ("open/build/closed-but-open.md",
             MEMO_FROM % ("Engineering", "Build", "closed but still in an "
                          "open tray", "Closed", "body"),
             "still in an OPEN tray"),
            ("answered/no-answer.md",
             MEMO % ("Build", "filed answered with no answer", "Answered", "body"),
             "carries no ANSWERS: line"),
            ("answered/tick-not-answer.md",
             MEMO % ("Build", "a tick", "Answered", "ANSWERS:\n\nyes\n"),
             "That is a tick, not an answer"),
            # Architecture's order, 2026-09-12 - the two ways it must go RED.
            ("answered/closed-no-marker.md",
             MEMO % ("Build", "closed with nothing in it", "Closed", "body"),
             "carries neither an ANSWERS: nor a CLOSED: line"),
            ("answered/answered-only-closed.md",
             MEMO % ("Build", "answered but only a closing note", "Answered",
                     "CLOSED:\n\n" + "c" * 40),
             "carries no ANSWERS: line"),
            ("answered/still-open.md",
             MEMO % ("Build", "open memo in the answered drawer", "Open",
                     "ANSWERS:\n\n" + "x" * 40),
             "its Status is"),
            # The live defect: the same basename in both drawers. Each copy is
            # individually well-formed, which is exactly why nothing else here
            # notices it.
            ("open/research/2026-08-30_in-two-places.md",
             MEMO % ("Research", "answered and waiting at the same time",
                     "Open", "the original question"),
             "AND still in open/research/"),
            ("answered/2026-08-30_in-two-places.md",
             MEMO % ("Research", "answered and waiting at the same time",
                     "Answered", "ANSWERS:\n\n" + "y" * 40),
             "AND still in open/research/"),
            # THE SIGNATURE RULE'S FAILING SIDE. The router leaves both of these
            # whole, so both must still be "not a desk" here: an address that
            # is ONLY a parenthetical, and one whose parenthetical never closes.
            ("open/owner/only-a-signature.md",
             MEMO % ("(Sleven)", "an address that is only a signature",
                     "Open", "body"),
             "only-a-signature.md is addressed to '(sleven)', which is not a desk"),
            ("open/owner/unclosed-signature.md",
             MEMO % ("Owner (Sleven", "a signature that never closes",
                     "Open", "body"),
             "unclosed-signature.md is addressed to 'owner (sleven', which is "
             "not a desk"),
        ]
        for rel, body, _ in planted:
            put(rel, body)

        # THE SIGNATURE RULE'S PASSING SIDE - the live case of 2026-09-12. The
        # router files `To: Owner (Sleven)` in owner/, so here it must raise
        # NOTHING. Asserted below.
        put("open/owner/signed-to-owner.md",
            MEMO % ("Owner (Sleven)", "addressed with a signature", "Open",
                    "body"))

        # UNDELIVERED POST. A memo addressed to a desk that does not exist,
        # sitting in the bounce folder exactly as the router leaves it. Ten
        # seconds, repeatable any day - rule 12 satisfied by construction, and
        # the reason this assertion needed no elaborate fixture.
        # Owner's rule, the passing side: To: Architecture, From: Build,
        # Answered, sitting in open/build/. The router put it there because
        # Build sent it; Build has not closed it yet.
        put("open/build/returned-answer.md",
            MEMO_FROM % ("Engineering", "Build", "an answer on its way home",
                         "Answered", "ANSWERS:\n\n" + "z" * 40))

        # Architecture's order, the passing side: a Closed memo with a real
        # CLOSED: record must raise NOTHING.
        put("answered/closed-with-record.md",
            MEMO % ("Build", "closed properly", "Closed",
                    "CLOSED:\n\n" + "d" * 40))

        bounce = os.path.join(tmp, "_needs_review")
        os.makedirs(bounce)
        io.open(os.path.join(bounce, "bounced-to-nobody.md"), "w",
                encoding="utf-8", newline="").write(
            MEMO % ("Legal", "there is no legal desk", "Open", "body"))
        # And the thing it must NOT fire on: the folder legitimately holds old
        # handoff text and status files. A control that cried wolf on those
        # would be switched off inside a week.
        io.open(os.path.join(bounce, "old-handoff.txt"), "w",
                encoding="utf-8", newline="").write(
            "# SESSION HANDOFF\n\nA status file. No address on it.\n")

        fails = run(tmp, needs_review_dir=bounce, label="self-test trays")
        blob = "\n".join(fails)

        print("\n%d finding(s) raised. Each planted defect must appear:\n" % len(fails))
        caught = 0
        for rel, _, needle in planted:
            hit = needle in blob
            print("  %-7s %-34s %s" % ("caught" if hit else "MISSED",
                                       os.path.basename(rel), needle))
            if hit:
                caught += 1

        # A DRIFT DEFECT TOO - the README gains a desk nothing checks.
        io.open(os.path.join(tmp, "README.md"), "a", encoding="utf-8",
                newline="").write("open/legal\n")
        drift = drift_check(tmp)
        hit = any("does not know about" in d for d in drift)
        print("  %-7s %-34s %s" % ("caught" if hit else "MISSED",
                                   "README.md", "a fifth desk nobody checks"))
        if hit:
            caught += 1

        # THE BOUNCE FOLDER, BOTH DIRECTIONS.
        hit = any("bounce folder" in f and "bounced-to-nobody.md" in f
                  for f in fails)
        print("  %-7s %-34s %s" % ("caught" if hit else "MISSED",
                                   "bounced-to-nobody.md",
                                   "undelivered post nobody is coming for"))
        if hit:
            caught += 1
        quiet = not any("old-handoff.txt" in f for f in fails)
        print("  %-7s %-34s %s" % ("caught" if quiet else "MISSED",
                                   "old-handoff.txt",
                                   "a status file with no address is NOT post"))
        if quiet:
            caught += 1

        closed_quiet = not any("closed-with-record.md" in f for f in fails)
        print("  %-7s %-34s %s" % ("caught" if closed_quiet else "MISSED",
                                   "closed-with-record.md",
                                   "a Closed memo with a CLOSED: record is fine"))
        if closed_quiet:
            caught += 1

        # THE RETURNED ANSWER, IN BOTH DIRECTIONS - Owner's 2026-09-11 rule.
        # An answer in its sender's tray, addressed elsewhere, must raise
        # NOTHING and must still be REPORTED as waiting. Either half alone
        # would be satisfied by a control that had simply stopped looking at
        # the tray, which is why both are asserted.
        returned_quiet = not any("returned-answer.md" in f for f in fails)
        print("  %-7s %-34s %s" % ("caught" if returned_quiet else "MISSED",
                                   "returned-answer.md",
                                   "an answer in its sender's tray is NOT a defect"))
        if returned_quiet:
            caught += 1
        _rf, _ropens = audit(tmp, True)
        reported = any("returned-answer.md" in rel for rel, _d, _m, _p in _ropens)
        print("  %-7s %-34s %s" % ("caught" if reported else "MISSED",
                                   "returned-answer.md",
                                   "and it is REPORTED as waiting to be read"))
        if reported:
            caught += 1

        # TRAY DEPTH IS A REPORT, AND A REPORT THAT SILENTLY RETURNS NOTHING IS
        # THE SAME DEFECT AS A CHECK THAT CANNOT FAIL. It is asserted here on a
        # tray whose contents this file wrote, so the numbers have a known
        # answer.
        _f, planted_opens = audit(tmp, True)
        rows = tray_depth(planted_opens,
                          now=datetime.date(2026, 9, 30))
        research = [r for r in rows if r["desk"] == "research"]
        ok_depth = (bool(research)
                    and research[0]["count"] == 1
                    and research[0]["oldest"] == datetime.date(2026, 8, 30)
                    and research[0]["age_days"] == 31)
        print("  %-7s %-34s %s" % ("caught" if ok_depth else "MISSED",
                                   "tray depth",
                                   "counts the tray and ages the oldest letter"))
        if ok_depth:
            caught += 1

        # THE SIGNATURE RULE, PASSING SIDE: the router files this in owner/,
        # so it must raise nothing. Its failing side is in `planted` above.
        signed_quiet = not any("signed-to-owner.md" in f for f in fails)
        print("  %-7s %-34s %s" % ("caught" if signed_quiet else "MISSED",
                                   "signed-to-owner.md",
                                   "To: Owner (Sleven) is addressed to owner"))
        if signed_quiet:
            caught += 1

        # +6: the README drift case, the bounce folder's two directions,
        # tray depth, and Owner's returned-answer rule in both directions.
        # +7: README drift, the bounce folder both ways, tray depth, the
        # returned answer both ways, and the closed-with-record green case.
        # +8: all of those, and the signed-address green case (2026-09-12).
        total = len(planted) + 8
        print("\n%d of %d planted defects caught." % (caught, total))
        if caught != total:
            print("SELF-TEST FAILED - this control missed a defect it is "
                  "supposed to catch, so it must not be trusted.")
            return 3
        print("SELF-TEST PASSED - every planted defect was caught.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv):
    if "--self-test" in argv:
        return self_test()
    fails = run(CORR)
    if fails:
        print("\n%d finding(s):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        print("RED.")
        return 1
    print("\nPASS - every memo is a memo, every one is at the desk it is "
          "addressed to, and every answered one carries its answer.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
