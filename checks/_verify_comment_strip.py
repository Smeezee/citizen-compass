#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_verify_comment_strip.py - the strip removes comments and NOTHING else.

RULE16: INDEPENDENT - the truth here is what a JavaScript engine says about the
stripped text, not what the stripper reports about itself. Every real file is
handed to `node --check`, which shares no code, no author and no assumption
with the scanner under test. The hand-written cases below are independent in
the same way a planted defect is: the expected output is written out by hand
and compared, so the stripper cannot define its own correctness.

WHY THIS EXISTS SEPARATELY FROM _verify_no_agent_traces.py
==========================================================
That control asks whether the words are gone. It would be perfectly happy with
a strip that also deleted a line of code, because a broken page contains no
traces either. THIS one asks whether anything else moved.

A page that loses a script and still renders is the exact failure this project
keeps finding, and it would ship looking fine.

Rule 15: every open states its encoding.
"""

import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "testing", "_src")
DEPLOY = os.path.join(REPO, "testing", "_deploy")
sys.path.insert(0, SRC)

SELFTEST = "--self-test" in sys.argv

_passed, _failed = [], []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def node():
    for c in ("node", "node.exe"):
        try:
            subprocess.run([c, "--version"], capture_output=True, timeout=30)
            return c
        except Exception:
            continue
    return None


def parses(code, cmd):
    """Ask node, not the stripper, whether this is still JavaScript."""
    fd, tmp = tempfile.mkstemp(suffix=".js")
    os.close(fd)
    try:
        with io.open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(code)
        r = subprocess.run([cmd, "--check", tmp], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return r.returncode == 0, (r.stderr or "").strip()
    finally:
        os.unlink(tmp)


# THE CASES ARE THE POINT. Each is something in these files today that a
# regex-based strip gets wrong, with the expected output written by hand.
CASES = [
    ("a // inside a string is not a comment",
     'var u = "http://example.com/x"; // gone\n',
     'var u = "http://example.com/x"; \n'),
    ("a /* inside a string is not a comment",
     "var s = 'a /* b */ c';\n",
     "var s = 'a /* b */ c';\n"),
    ("a regex literal containing a slash survives",
     "var re = /a\\/b/g; // gone\n",
     "var re = /a\\/b/g; \n"),
    ("a regex character class containing a slash survives",
     "var re = /[/]/; // gone\n",
     "var re = /[/]/; \n"),
    ("division is not a regex",
     "var x = a / b; // gone\n",
     "var x = a / b; \n"),
    ("a comment inside a template literal is TEXT, not a comment",
     "var t = `keep // this and /* this */`;\n",
     "var t = `keep // this and /* this */`;\n"),
    ("a comment inside a template EXPRESSION is a comment",
     "var t = `x${ a /* gone */ }y`;\n",
     "var t = `x${ a  }y`;\n"),
    ("a nested brace inside a template expression does not end it",
     "var t = `${ {a:1}.a }` ; // gone\n",
     "var t = `${ {a:1}.a }` ; \n"),
    ("@license survives",
     "/* @license MIT */\nvar a = 1; /* gone */\n",
     "/* @license MIT */\nvar a = 1; \n"),
    ("@preserve survives",
     "/*! @preserve keep me */\nvar a = 1;\n",
     "/*! @preserve keep me */\nvar a = 1;\n"),
    ("a block comment leaves its newlines behind",
     "var a = 1;\n/* one\ntwo\nthree */\nvar b = 2;\n",
     "var a = 1;\n\n\n\nvar b = 2;\n"),
    ("an escaped quote does not end a string",
     'var s = "he said \\" // not a comment";\n',
     'var s = "he said \\" // not a comment";\n'),
]

HTML_CASES = [
    ("a markup comment goes",
     "<p>a</p><!-- gone --><p>b</p>",
     "<p>a</p><p>b</p>"),
    ("a conditional comment stays - it is an instruction, not prose",
     "<!--[if IE]><p>x</p><![endif]-->",
     "<!--[if IE]><p>x</p><![endif]-->"),
    ("a JSON data island is left completely alone",
     '<script type="application/json">{"a":"// not a comment"}</script>',
     '<script type="application/json">{"a":"// not a comment"}</script>'),
    ("script bodies are stripped as JavaScript",
     "<script>var a = 1; // gone\n</script>",
     "<script>var a = 1; \n</script>"),
    ("style bodies are stripped as CSS",
     "<style>a{color:red} /* gone */</style>",
     "<style>a{color:red} </style>"),
    ("a comment marker inside a style STRING is not a comment",
     '<style>a{content:"/* keep */"}</style>',
     '<style>a{content:"/* keep */"}</style>'),
]


def main():
    try:
        import strip_comments as sc
    except Exception as exc:
        print("NOT PERFORMED - testing/_src/strip_comments.py could not be "
              "imported (%s). Reported, never passed." % exc)
        return 2

    print("1. THE CASES A REGEX GETS WRONG")
    for label, src, want in CASES:
        got, _n = sc.strip_js(src)
        if not check(label, got == want) and not SELFTEST:
            print("        want %r" % want)
            print("        got  %r" % got)

    print("\n2. HTML, CSS AND DATA ISLANDS")
    for label, src, want in HTML_CASES:
        got, _n = sc.strip_html(src)
        if not check(label, got == want) and not SELFTEST:
            print("        want %r" % want)
            print("        got  %r" % got)

    print("\n3. AN UNTERMINATED BLOCK COMMENT IS REFUSED, NOT GUESSED AT")
    try:
        sc.strip_js("var a = 1;\n/* never closed\n")
        refused = False
    except ValueError:
        refused = True
    check("a /* with no */ raises rather than eating the rest of the file",
          refused)

    print("\n4. EVERY REAL FILE STILL PARSES - ASKED OF NODE, NOT OF THE STRIPPER")
    cmd = node()
    if cmd is None:
        print("NOT PERFORMED - node is not on PATH, so nothing here can be "
              "told whether the stripped JavaScript is still JavaScript.")
        print("Reported as NOT PERFORMED, never as a pass.")
        return 2

    js = [n for n in sorted(os.listdir(SRC)) if n.endswith(".js")]
    if not js:
        print("NO .js FILES FOUND in _src - refusing to report a pass on an "
              "empty set.")
        return 1
    bad, total = [], 0
    for name in js:
        text = io.open(os.path.join(SRC, name), encoding="utf-8",
                       errors="replace").read()
        try:
            stripped, n = sc.strip_js(text)
        except ValueError as exc:
            bad.append("%s: %s" % (name, exc)); continue
        total += n
        ok, err = parses(stripped, cmd)
        if not ok:
            bad.append("%s: %s" % (name, err.splitlines()[0] if err else "?"))
    check("every stripped .js in _src still parses (%d file(s), %d comment(s) "
          "removed)%s" % (len(js), total,
                          "" if not bad else " - " + "; ".join(bad[:3])),
          not bad)

    print("\n5. THE STRIP IS NOT ALLOWED TO DO NOTHING")
    # A strip that silently no-ops would leave the traces in place and this
    # control would otherwise be perfectly happy. The count is the evidence
    # that it ran at all.
    check("it actually removed something (%d comment(s) across _src)" % total,
          total > 0)

    print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
    if _failed:
        print("FAILED:")
        for f in _failed:
            print("  " + f)
    if SELFTEST:
        print("\n--self-test: expectations were inverted, so a non-zero exit "
              "is the correct outcome.")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
