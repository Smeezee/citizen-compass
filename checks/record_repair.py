#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record_repair.py - B3, the repairer. It turns a DISPOSITIONED B1/B2 gap into a
proposed batch of repairs whose inputs are already on this machine, and applies
the batch only on one word from Architecture or Owner. Never on a timer, never
from the open web.

RULE16: INDEPENDENT - the repairs come from what desks WROTE under `ANSWERS:` in
answered router letters; the proof that a HISTORY row landed is B1's own
`record_audit.audit()` counting it dispositioned, a different program reading
the ledger in its own format; the authority is a letter, never a flag.

Built to `claude/PROPOSAL_b3-the-repairer-2026-09-13.md`, all four decisions
ruled yes by Architecture 2026-09-13 (`..._b3-four-decisions-ruled-go-after-
sitting.md`); retiring a ledger row is a B3 command, not a hand edit.

ONE LEDGER FORMAT, ONE OWNERS PARSER. LEDGER and LEDGER_ROW are imported from
record_audit.py (B1); parse_owners from _verify_owners.py. No second copy of either.

WHAT IS READ     answered letters under correspondence/ that carry a `Router-key:`
                 above `ANSWERS:`. Under `ANSWERS:`, one line per row, exactly:
                     `<source>` | `<token>` | <class> | <note>      HISTORY
                     MOVED `<source>` | `<token>` -> `<new path>`   repoint
                     DEFECT `<source>` | `<token>`                  nothing to apply
                 A reply for a key not above ANSWERS: in the same letter is NOT
                 SENT; a line that starts like a reply and fits no form is
                 MALFORMED; two DIFFERENT replies for one key, anywhere, are
                 AMBIGUOUS, all named, none applied (rule 19). Byte-identical
                 twin letters are one reply.
WHAT IS APPLIED  HISTORY: a row appended to the ledger (never twice; a key already
                 there with a different class or note is refused - retire it first).
                 MOVED: `<token>` -> `<new path>` in the citing document, REFUSED
                 when the new path is not on disk, the source is a letter or
                 CLAUDE.md or OWNERS.md, the source is claimed in OWNERS.md by a
                 desk other than the letter's To:, or the token is not there.
                 RETIRE (--retire "<source> | <token>"): the row leaves the ledger
                 and a `RETIRED` line stays, so its old reply is never re-added.
THE WORD         --apply ID applies only if the batch computed NOW hashes to ID AND
                 a letter under correspondence/ from Architecture or Owner to Build
                 carries `B3-apply: <ID>` on its own line. Nothing else is read.
                 One OS user runs every desk, so a forged From: cannot be
                 prevented; it is made loud - the authorising letter is printed and
                 named in logs/record_repair.json.

The dry run (the default) writes nothing at all.

Rule 15: every text open states encoding="utf-8".

Usage:
    python checks/record_repair.py                              dry run: the batch and its BATCH-ID
    python checks/record_repair.py --retire "<src> | <token>"   add a retire to the batch (repeatable)
    python checks/record_repair.py --apply ID [--retire ...]    apply, under the word
    python checks/record_repair.py --self-test
"""
import datetime
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from record_audit import LEDGER, LEDGER_ROW  # noqa: E402  ONE LEDGER FORMAT
from _verify_owners import parse_owners      # noqa: E402  ONE OWNERS PARSER

OUT_REL = "logs/record_repair.json"
HEAD = 4000
NEVER_EDIT = ("CLAUDE.md", "OWNERS.md")
OWNER_DESK = {"C1": "architecture", "CODE": "build", "SLEVEN": "owner"}
WORD_FROM = ("architecture", "owner")

RE_ANSWERS = re.compile(r"(?im)^\s*(?:\*\*)?ANSWERS:")
RE_KEY = re.compile(r"(?m)^Router-key:\s*(.+?)\s*$")
RE_TO = re.compile(r"(?im)^To:\s*(.+?)\s*$")
RE_FROM = re.compile(r"(?im)^From:\s*(.+?)\s*$")
RE_STATUS = re.compile(r"(?im)^Status:\s*(.+?)\s*$")
RE_SIGNATURE = re.compile(r"^(.*[^ \t\n\f\r])[ \t\n\f\r]+(\([^()]*\))[ \t\n\f\r]*$")
RE_MOVED = re.compile(r"^\s*MOVED\s+`([^`]+)`\s*\|\s*`([^`]+)`\s*->\s*`([^`]+)`\s*$")
RE_DEFECT = re.compile(r"^\s*DEFECT\s+`([^`]+)`\s*\|\s*`([^`]+)`\s*$")
RE_LOOKS = re.compile(r"^\s*(?:MOVED\b|DEFECT\b|`[^`]*`\s*\|)")
RE_WORD = re.compile(r"(?m)^\s*B3-apply:\s*([0-9a-f]{16})\s*$")
RE_RETIRED = re.compile(r"^RETIRED\s+`([^`]+)`\s*\|\s*`([^`]+)`")

LEDGER_HEADER = """# RECORD-AUDIT-DISPOSITIONS - the B1 disposition ledger

    writer    checks/record_repair.py (B3), and nothing else. Rows are added from
              answered router letters and retired with --retire, both applied
              only on a B3-apply word from Architecture or Owner (Architecture,
              2026-09-13). A hand edit here is a second writer (rule 14).
    reader    checks/record_audit.py (B1), by its LEDGER_ROW pattern
    rows      source | token | class | note - one per line, below

"""


def _read(path):
    with io.open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return fh.read()


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def _addr(raw):
    raw = raw.strip()
    m = RE_SIGNATURE.match(raw)
    return (m.group(1) if m else raw).strip().lower()


def key(src, tok):
    return "%s | %s" % (src, tok)


def letters(root):
    """-> every .md under correspondence/ as {path, to, from, status, keys, body}."""
    out = []
    for dp, _dn, fn in os.walk(os.path.join(root, "correspondence")):
        for f in sorted(fn):
            if not f.lower().endswith(".md"):
                continue
            p = os.path.join(dp, f)
            try:
                text = _read(p)
            except OSError:
                continue
            m = RE_ANSWERS.search(text)
            head, body = (text[:m.start()], text[m.end():]) if m else (text, "")
            h = head[:HEAD]
            to, frm, st = RE_TO.search(h), RE_FROM.search(h), RE_STATUS.search(h)
            out.append({"path": os.path.relpath(p, root).replace("\\", "/"), "text": text,
                        "to": _addr(to.group(1)) if to else "", "from": _addr(frm.group(1)) if frm else "",
                        "status": st.group(1).strip().lower() if st else "",
                        "keys": set(RE_KEY.findall(head)), "body": body.splitlines(),
                        "answered": bool(m)})
    return out


def read_ledger(root):
    """-> (rows {key: (class, note)}, retired {key}, text or None)."""
    p = os.path.join(root, *LEDGER.split("/"))
    if not os.path.isfile(p):
        return {}, set(), None
    text = _read(p)
    rows, retired = {}, set()
    for line in text.splitlines():
        m = LEDGER_ROW.match(line)
        if m:
            rows[key(m.group(1), m.group(2))] = (m.group(3), m.group(4))
            continue
        r = RE_RETIRED.match(line)
        if r:
            retired.add(key(r.group(1), r.group(2)))
    return rows, retired, text


def owner_of(root, src):
    p = os.path.join(root, "OWNERS.md")
    if not os.path.isfile(p):
        return None
    for path, owner in parse_owners(_read(p)):
        path = path.replace("\\", "/")
        if src == path or (path.endswith("/") and src.startswith(path)):
            return owner
    return None


def plan(root, retire=()):
    """-> {"repairs": [...], "problems": [...], "id": ..., counts}. Read-only."""
    replies, problems = {}, []
    for L in letters(root):
        if L["status"] != "answered" or not L["keys"] or not L["answered"]:
            continue
        for ln in L["body"]:
            if not RE_LOOKS.match(ln):
                continue
            m, mv, df = LEDGER_ROW.match(ln), RE_MOVED.match(ln), RE_DEFECT.match(ln)
            if m:
                k, rep = key(m.group(1), m.group(2)), ("HISTORY", m.group(3), m.group(4).strip())
            elif mv:
                k, rep = key(mv.group(1), mv.group(2)), ("MOVED", mv.group(3).strip())
            elif df:
                k, rep = key(df.group(1), df.group(2)), ("DEFECT",)
            else:
                problems.append(("MALFORMED", L["path"], ln.strip()[:160]))
                continue
            if k not in L["keys"]:
                problems.append(("NOT SENT", L["path"], k))
                continue
            replies.setdefault(k, {}).setdefault(rep, []).append(L)

    rows, retired, _t = read_ledger(root)
    repairs, defects, already = [], 0, 0
    for k in sorted(replies):
        reps = replies[k]
        if len(reps) > 1:
            problems.append(("AMBIGUOUS", k, "; ".join(sorted(
                "%s in %s" % (r[0], L["path"]) for r, Ls in reps.items() for L in Ls))))
            continue
        (rep, Ls), = reps.items()
        src, tok = k.split(" | ", 1)
        if rep[0] == "DEFECT":
            defects += 1
        elif rep[0] == "HISTORY":
            if k in retired:
                problems.append(("RETIRED", k, "retired from the ledger; its old reply is not re-added"))
            elif os.path.exists(os.path.join(root, *tok.rstrip("/").split("/"))):
                problems.append(("RESOLVED", k, "the cited path exists now, so B1 no longer reports it; "
                                                "a row would only be STALE - not added"))
            elif k in rows:
                if rows[k] == (rep[1], rep[2]):
                    already += 1
                else:
                    problems.append(("IN LEDGER, DIFFERS", k, "retire it first"))
            else:
                repairs.append(("HISTORY", k, "`%s` | `%s` | %s | %s" % (src, tok, rep[1], rep[2])))
        else:
            new = rep[1]
            why = None
            to = Ls[0]["to"]
            own = owner_of(root, src)
            srcp = os.path.join(root, *src.split("/"))
            if src.startswith("correspondence/"):
                why = "the source is a letter - text above ANSWERS: is never edited"
            elif src in NEVER_EDIT:
                why = "%s is never edited by a program" % src
            elif not os.path.isfile(srcp):
                why = "the source is not on disk"
            elif not os.path.exists(os.path.join(root, *new.rstrip("/").split("/"))):
                why = "the new path %s is not on disk" % new
            elif own and OWNER_DESK.get(own) != to:
                why = "OWNERS.md gives the source to %s; the letter was answered by %s" % (own, to or "nobody")
            else:
                n = _read(srcp).count("`%s`" % tok)
                if n == 0:
                    why = "`%s` is not in the source" % tok
            if why:
                problems.append(("MOVED REFUSED", k, why))
            else:
                repairs.append(("MOVED", k, "%s -> %s (%d)" % (tok, new, n)))
    for k in retire:
        k = k.strip()
        if k in rows:
            repairs.append(("RETIRE", k, ""))
        else:
            problems.append(("RETIRE REFUSED", k, "not in the ledger"))
    repairs.sort()
    bid = hashlib.sha256("\n".join("%s\t%s\t%s" % r for r in repairs).encode("utf-8")).hexdigest()[:16]
    return {"repairs": repairs, "problems": problems, "id": bid, "defects": defects, "already": already}


def find_word(root, bid):
    for L in letters(root):
        if L["to"] == "build" and L["from"] in WORD_FROM and bid in RE_WORD.findall(L["text"]):
            return L["path"]
    return None


def apply(root, p, now):
    """Write the batch. MOVED first, then the ledger, each through a temp file."""
    rows, retired, text = read_ledger(root)
    for kind, k, detail in p["repairs"]:
        if kind != "MOVED":
            continue
        src, tok = k.split(" | ", 1)
        new = detail.split(" -> ", 1)[1].rsplit(" (", 1)[0]
        sp = os.path.join(root, *src.split("/"))
        body = _read(sp)
        _write(sp, body.replace("`%s`" % tok, "`%s`" % new))
    hist = [d for kind, _k, d in p["repairs"] if kind == "HISTORY"]
    gone = {k for kind, k, _d in p["repairs"] if kind == "RETIRE"}
    if hist or gone:
        text = text if text is not None else LEDGER_HEADER
        keep = []
        for line in text.splitlines(True):
            m = LEDGER_ROW.match(line)
            if m and key(m.group(1), m.group(2)) in gone:
                continue
            keep.append(line)
        text = "".join(keep)
        if text and not text.endswith("\n"):
            text += "\n"
        stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        text += "".join("RETIRED `%s` | `%s`  %s\n" % (tuple(k.split(" | ", 1)) + (stamp,)) for k in sorted(gone))
        text += "".join(h + "\n" for h in hist)
        _write(os.path.join(root, *LEDGER.split("/")), text)


def receipt(root, rec):
    _write(os.path.join(root, *OUT_REL.split("/")), json.dumps(rec, indent=1) + "\n")


def run(root, now, apply_id=None, retire=()):
    p = plan(root, retire)
    for kind, k, detail in p["repairs"]:
        print("  %-8s %s%s" % (kind, k, ("   " + detail) if detail else ""))
    for kind, a, b in p["problems"]:
        print("  %-8s %s  -  %s" % (kind, a, b))
    print("B3: %d repair(s) - HISTORY %d, MOVED %d, RETIRE %d; %d problem(s); %d DEFECT repl(ies), "
          "nothing to apply; %d already in the ledger. BATCH-ID %s"
          % (len(p["repairs"]), sum(r[0] == "HISTORY" for r in p["repairs"]),
             sum(r[0] == "MOVED" for r in p["repairs"]), sum(r[0] == "RETIRE" for r in p["repairs"]),
             len(p["problems"]), p["defects"], p["already"], p["id"]))
    if apply_id is None:
        print("DRY RUN - nothing was written. To apply, Architecture or Owner writes to Build: "
              "`B3-apply: %s`" % p["id"])
        return 0
    rec = {"at": now.isoformat(timespec="seconds"), "asked": apply_id, "batch_id": p["id"]}
    if not p["repairs"]:
        rec.update(state="nothing-to-apply")
    elif apply_id != p["id"]:
        rec.update(state="refused", reason="the batch now hashes to %s, not %s - run the dry run again"
                   % (p["id"], apply_id))
    else:
        word = find_word(root, p["id"])
        if not word:
            rec.update(state="refused", reason="no letter from Architecture or Owner to Build carries "
                       "`B3-apply: %s`" % p["id"])
        else:
            apply(root, p, now)
            rec.update(state="applied", word=word, repairs=[list(r) for r in p["repairs"]])
    receipt(root, rec)
    print("B3 APPLY: %s%s" % (rec["state"], (" - authorised by %s" % rec["word"]) if "word" in rec
                              else (" - " + rec["reason"]) if "reason" in rec else ""))
    return 1 if rec["state"] == "refused" else 0


# ------------------------------------------------------------------ self-test
def self_test():
    import shutil
    import tempfile

    results = []

    def check(ok, what):
        results.append(bool(ok))
        print("  %-7s %s" % ("caught" if ok else "MISSED", what))

    root = tempfile.mkdtemp(prefix="cc-repair-selftest-")
    try:
        def put(rel, body):
            p = os.path.join(root, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(body)

        def get(rel):
            return _read(os.path.join(root, *rel.split("/")))

        def tree():
            h = hashlib.sha256()
            for dp, dn, fn in os.walk(root):            # NOT sorted(os.walk()): that walks
                dn[:] = sorted(d for d in dn if d != "logs")   # everything before dn can prune
                for f in sorted(fn):
                    with open(os.path.join(dp, f), "rb") as fh:
                        h.update(os.path.join(dp, f).encode("utf-8") + fh.read())
            return h.hexdigest()

        def letter(rel, to, frm, status, keys, answers=None):
            t = ("# Memo\n\nTo:      %s\nFrom:    %s\nSubject: s\nStatus:  %s\n\n" % (to, frm, status)
                 + "".join("Router-key: %s\n" % k for k in keys))
            if answers is not None:
                t += "\n---\n\nANSWERS:\n\n" + "\n".join(answers) + "\n"
            put(rel, t)

        def silent(fn, *a, **kw):
            import contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                return fn(*a, **kw)

        A, C1DOC = "claude/NOTE_a-2026-09-13.md", "claude/NOTE_c1-2026-09-13.md"
        NOW = datetime.datetime(2026, 9, 13, 14, 0, 0)
        for d in ("correspondence/open/build", "correspondence/answered", "logs"):
            os.makedirs(os.path.join(root, *d.split("/")), exist_ok=True)
        put("OWNERS.md", "# OWNERS\n\n## C1 - Cowork\n\n    %s\n\n## CODE - Claude Code\n\n    %s\n" % (C1DOC, A))
        put("CLAUDE.md", "`docs/c.md`\n")
        put("docs/new.md", "x\n")
        a_text = ("# A\n\nSee `docs/gone.md`, `docs/old.md`, again `docs/old.md`, `docs/m2.md`, "
                  "`docs/x.md`, `docs/dup.md`, `docs/tw.md` and `docs/late.md`.\n")
        put(A, a_text)
        put(C1DOC, "`docs/old2.md`\n")
        R = "correspondence/answered/2026-09-13_memo_build_router-"
        letter(R + "1.md", "Build", "Build (router)", "Answered",
               [key(A, "docs/gone.md"), key(A, "docs/old.md"), key(A, "docs/m2.md"), key(A, "docs/x.md"),
                key("CLAUDE.md", "docs/c.md"), key("correspondence/answered/q.md", "docs/q.md"),
                key(A, "docs/new.md")],
               ["    `%s` | `docs/gone.md` | absence | cited to say it is gone" % A,
                "    `%s` | `docs/new.md` | future | built since the reply" % A,
                "    MOVED `%s` | `docs/old.md` -> `docs/new.md`" % A,
                "    MOVED `%s` | `docs/m2.md` -> `docs/nothere.md`" % A,
                "    `%s` | `docs/x.md` | bogus | not a class" % A,
                "    `%s` | `docs/notsent.md` | example | never sent" % A,
                "    MOVED `CLAUDE.md` | `docs/c.md` -> `docs/new.md`",
                "    MOVED `correspondence/answered/q.md` | `docs/q.md` -> `docs/new.md`"])
        letter(R + "2.md", "Build", "Build (router)", "Answered", [key(C1DOC, "docs/old2.md")],
               ["MOVED `%s` | `docs/old2.md` -> `docs/new.md`" % C1DOC])
        letter(R + "3.md", "Build", "Build (router)", "Answered", [key(A, "docs/dup.md")],
               ["`%s` | `docs/dup.md` | history | one" % A])
        letter(R + "4.md", "Design", "Build (router)", "Answered", [key(A, "docs/dup.md")],
               ["`%s` | `docs/dup.md` | example | two" % A])
        letter("correspondence/open/build/2026-09-13_memo_build_router-5.md", "Build", "Build (router)",
               "Open", [key(A, "docs/open.md")], ["`%s` | `docs/open.md` | example | not answered" % A])
        letter(R + "7.md", "Build", "Build (router)", "Answered", [key(A, "docs/tw.md")],
               ["`%s` | `docs/tw.md` | future | twin" % A])
        shutil.copy2(os.path.join(root, *(R + "7.md").split("/")),
                     os.path.join(root, *(R + "7__20260913120000.md").split("/")))

        before = tree()
        p = silent(plan, root)
        rep = {(r[0], r[1]) for r in p["repairs"]}
        probs = {(x[0], x[1] if x[0] not in ("MALFORMED", "NOT SENT") else x[2]) for x in p["problems"]}
        pk = lambda kind: [x for x in p["problems"] if x[0] == kind]   # noqa: E731
        rc = silent(run, root, NOW)
        check(rc == 0 and tree() == before and not os.path.exists(os.path.join(root, "logs", "record_repair.json")),
              "1  the dry run writes nothing: tree unchanged, no receipt")
        check(("HISTORY", key(A, "docs/gone.md")) in rep and ("MOVED", key(A, "docs/old.md")) in rep,
              "2  a HISTORY reply and a MOVED reply become repairs")
        check(any(x[2] == key(A, "docs/notsent.md") for x in pk("NOT SENT"))
              and all(r[1] != key(A, "docs/notsent.md") for r in p["repairs"]),
              "3  a reply for a key not above ANSWERS: is NOT SENT, never applied")
        check(any("bogus" in x[2] for x in pk("MALFORMED")), "4  a line fitting no form is MALFORMED, named")
        mr = {x[1]: x[2] for x in pk("MOVED REFUSED")}
        check("not on disk" in mr.get(key(A, "docs/m2.md"), ""), "5  MOVED to a path not on disk is refused")
        check("letter" in mr.get(key("correspondence/answered/q.md", "docs/q.md"), ""),
              "6  MOVED inside a letter is refused")
        check("never edited" in mr.get(key("CLAUDE.md", "docs/c.md"), ""), "7  MOVED in CLAUDE.md is refused")
        check("OWNERS.md gives" in mr.get(key(C1DOC, "docs/old2.md"), ""),
              "8  MOVED in a document OWNERS.md gives another desk is refused")
        check(any(x[1] == key(A, "docs/dup.md") for x in pk("AMBIGUOUS"))
              and all(r[1] != key(A, "docs/dup.md") for r in p["repairs"]),
              "9  two different replies for one key are AMBIGUOUS, and neither is applied")
        check(all(r[1] != key(A, "docs/open.md") for r in p["repairs"]),
              "10 a reply in a letter that is not Answered is not read")
        check(("HISTORY", key(A, "docs/tw.md")) in rep and not any(x[1] == key(A, "docs/tw.md") for x in p["problems"]),
              "11 byte-identical twin letters are one reply, not an ambiguity")
        check(any(x[1] == key(A, "docs/new.md") for x in pk("RESOLVED"))
              and all(r[1] != key(A, "docs/new.md") for r in p["repairs"]),
              "26 a HISTORY reply for a path that exists now is RESOLVED, never a stale row")

        W = "correspondence/open/build/2026-09-13_memo_build_b3-apply-"
        rc = silent(run, root, NOW, apply_id=p["id"])
        check(rc == 1 and tree() == before, "12 --apply with no word refuses, and writes nothing")
        put(W + "d.md", "# Memo\n\nTo: Build\nFrom: Design (Grok)\nSubject: s\nStatus: Open\n\nB3-apply: %s\n" % p["id"])
        check(silent(run, root, NOW, apply_id=p["id"]) == 1 and not os.path.exists(os.path.join(root, *LEDGER.split("/"))),
              "13 a word from Design is refused; only Architecture or Owner")
        put(W + "x.md", "# Memo\n\nTo: Build\nFrom: Architecture (Grok covering C1)\nSubject: s\nStatus: Open\n\nB3-apply: %s\n" % ("0" * 16))
        check(silent(run, root, NOW, apply_id="0" * 16) == 1 and get(A) == a_text,
              "14 a word for a different batch is refused")
        put(W + "a.md", "# Memo\n\nTo: Build\nFrom: Architecture (Grok covering C1)\nSubject: s\nStatus: Open\n\nB3-apply: %s\n" % p["id"])
        check(silent(run, root, NOW, apply_id="f" * 16) == 1 and get(A) == a_text
              and not os.path.exists(os.path.join(root, *LEDGER.split("/"))),
              "27 a valid word on disk does not let --apply run under a DIFFERENT id")
        letter(R + "8.md", "Build", "Build (router)", "Answered", [key(A, "docs/late.md")],
               ["`%s` | `docs/late.md` | example | arrived after the dry run" % A])
        check(silent(run, root, NOW, apply_id=p["id"]) == 1 and get(A) == a_text,
              "15 the right word after the batch moved is refused")
        p2 = silent(plan, root)
        put(W + "b.md", "# Memo\n\nTo: Build\nFrom: Architecture\nSubject: s\nStatus: Open\n\nB3-apply: %s\n" % p2["id"])
        rc = silent(run, root, NOW, apply_id=p2["id"])
        rows, _r, ltext = read_ledger(root)
        check(rc == 0 and set(rows) == {key(A, "docs/gone.md"), key(A, "docs/tw.md"), key(A, "docs/late.md")},
              "16 the word applies exactly the HISTORY rows")
        check(get(A) == a_text.replace("`docs/old.md`", "`docs/new.md`") and get(A).count("`docs/new.md`") == 2,
              "17 MOVED repoints every counted occurrence and changes nothing else")
        check(sum(1 for ln in ltext.splitlines() if LEDGER_ROW.match(ln)) == 3,
              "18 the ledger header is never read as a row")
        sys.path.insert(0, HERE)
        import record_audit as ra
        res = silent(ra.audit, root, False)
        disp = {(r[0], r[1]) for r in res["dispositioned"]}
        fnd = {(r[0], r[1]) for r in res["findings"]}
        check((A, "docs/gone.md") in disp and (A, "docs/old.md") not in fnd,
              "19 B1's own audit counts the row dispositioned and the moved citation resolved")
        with io.open(os.path.join(root, "logs", "record_repair.json"), encoding="utf-8") as fh:
            rj = json.load(fh)
        check(rj.get("state") == "applied" and rj.get("word", "").endswith("b3-apply-b.md"),
              "20 the receipt names the authorising letter")
        snap = tree()
        check(silent(run, root, NOW, apply_id=p2["id"]) == 0 and tree() == snap,
              "21 a second apply appends nothing")

        p3 = silent(plan, root, ["%s | docs/nope.md" % A])
        check(any(x[0] == "RETIRE REFUSED" for x in p3["problems"]) and not p3["repairs"],
              "22 retiring a key not in the ledger is refused")
        p4 = silent(plan, root, [key(A, "docs/gone.md")])
        check(silent(run, root, NOW, apply_id=p4["id"], retire=[key(A, "docs/gone.md")]) == 1
              and key(A, "docs/gone.md") in read_ledger(root)[0], "23 a retire without its word is refused")
        put(W + "o.md", "# Memo\n\nTo: Build\nFrom: Owner (Sleven)\nSubject: s\nStatus: Open\n\nB3-apply: %s\n" % p4["id"])
        rc = silent(run, root, NOW, apply_id=p4["id"], retire=[key(A, "docs/gone.md")])
        rows, retired, _t = read_ledger(root)
        res = silent(ra.audit, root, False)
        check(rc == 0 and key(A, "docs/gone.md") not in rows and key(A, "docs/gone.md") in retired
              and (A, "docs/gone.md") in {(r[0], r[1]) for r in res["findings"]},
              "24 Owner's word retires the row, and B1 reports the gap again")
        p5 = silent(plan, root)
        check(all(r[1] != key(A, "docs/gone.md") for r in p5["repairs"])
              and any(x[0] == "RETIRED" for x in p5["problems"]),
              "25 a retired row's old reply is never re-added")
    except Exception as exc:                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        check(False, "the self-test itself ran (%s: %s)" % (type(exc).__name__, exc))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    caught, total = sum(results), len(results)
    print("\n%d of %d planted cases landed." % (caught, total))
    if caught != total or total < 27:
        print("SELF-TEST FAILED - the repairer must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a control's "
          "self-test to be rejected. This is the GOOD outcome.")
    return 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    retire = [argv[i + 1] for i, a in enumerate(argv) if a == "--retire" and i + 1 < len(argv)]
    aid = argv[argv.index("--apply") + 1] if "--apply" in argv and argv.index("--apply") + 1 < len(argv) else None
    return run(ROOT, datetime.datetime.now().replace(microsecond=0), apply_id=aid, retire=retire)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
