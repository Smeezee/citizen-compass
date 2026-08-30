#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""strip_comments.py - remove comments on the way into _deploy, and nothing else.

Q31, 2026-08-30. Sleven's instruction: nothing on the public site may hint it
was built by anything other than a person - not the pages, and not the source
behind them. The pages were already clean; view-source was not. 1,114 comment
blocks and ~315,000 characters shipped to every visitor, and 45 of them read as
a conversation between a person and several named agents.

THE COMMENTS STAY IN _src. They are the best documentation this project has.
This runs on the way INTO _deploy and touches nothing else.

WHAT THIS IS REALLY RISKING, WHICH IS NOT THE TRACES
====================================================
Stripping comments out of working HTML and JavaScript is a text transform on
shipping code, and the careless version breaks a page in a way that still looks
fine. Every one of these is a real hazard in these files today:

    "http://example.com"        a // inside a string is not a comment
    /pattern[/]with/            a regex literal containing a slash
    a template literal          437 of them in loadout.html alone, and an
                                expression inside one can contain anything
    a / b // comment            division, then a real comment
    <!-- --> inside <script>    markup rules do not apply in there

So this is a scanner with the same states the language has, not a regular
expression. A regex that "mostly works" here would delete a line of code and
ship a page that still renders.

NEWLINES ARE PRESERVED. A removed block comment leaves its newlines behind, so
every line in the output keeps the line number it had in _src. That keeps the
build's own inline-JS syntax check reporting positions a person can find, and
it keeps this transform boring - which is the thing you want from something
that edits shipped code.

@license AND @preserve SURVIVE, and that is not politeness. holo.html carries
three.js's MIT header; removing it would breach the licence the library is used
under. It is the convention every minifier already follows.

Rule 15: this module opens no files. It takes text and returns text, which is
the other way of satisfying that rule.
"""

KEEP_MARKERS = ("@license", "@preserve")


def _keep(comment_text):
    return any(m in comment_text for m in KEEP_MARKERS)


def _blanks(text):
    """What a removed comment leaves behind: its newlines, and nothing else."""
    return "\n" * text.count("\n")


# A slash CANNOT start a regex when the previous significant character could
# end an expression - an identifier, a number, or a closing bracket. This is
# the standard heuristic and it is why `prev` is tracked at all.
_REGEX_CANNOT_FOLLOW = set("_$)]}") | set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


def strip_js(src):
    """Remove JS comments. Strings, template literals and regex literals are
    copied through untouched. Returns (text, removed_count)."""
    out, i, n, removed = [], 0, len(src), 0
    prev = ""           # last significant character, for the regex decision
    stack = []          # "tpl" = inside template text; int = ${ } brace depth

    while i < n:
        # --- inside the TEXT of a template literal --------------------------
        if stack and stack[-1] == "tpl":
            c = src[i]
            if c == "\\":
                out.append(src[i:i + 2]); i += 2; continue
            if c == "`":
                stack.pop(); out.append(c); prev = c; i += 1; continue
            if src.startswith("${", i):
                stack.append(0); out.append("${"); prev = "{"; i += 2; continue
            out.append(c); i += 1; continue

        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""

        # --- comments --------------------------------------------------------
        if c == "/" and nxt == "/":
            j = src.find("\n", i)
            j = n if j == -1 else j
            text = src[i:j]
            if _keep(text):
                out.append(text)
            else:
                removed += 1
            i = j
            continue
        if c == "/" and nxt == "*":
            j = src.find("*/", i + 2)
            if j == -1:
                # AN UNTERMINATED BLOCK COMMENT EATS THE REST OF THE FILE.
                # Refusing is the only safe answer: the input is not what this
                # thinks it is, and guessing would ship a truncated page.
                raise ValueError("unterminated /* block comment at offset %d" % i)
            j += 2
            text = src[i:j]
            if _keep(text):
                out.append(text)
            else:
                out.append(_blanks(text)); removed += 1
            i = j
            continue

        # --- string literals --------------------------------------------------
        if c in "'\"":
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2; continue
                if src[j] == c:
                    j += 1; break
                if src[j] == "\n":
                    # Unterminated. Copy what is there and let node --check be
                    # the one to complain; this is not the tool for that.
                    break
                j += 1
            out.append(src[i:j]); prev = c; i = j; continue

        # --- a template literal opens -----------------------------------------
        if c == "`":
            stack.append("tpl"); out.append(c); i += 1; continue

        # --- regex literal ------------------------------------------------------
        if c == "/" and prev not in _REGEX_CANNOT_FOLLOW:
            j, in_class, ok = i + 1, False, False
            while j < n:
                d = src[j]
                if d == "\\":
                    j += 2; continue
                if d == "\n":
                    break                       # a regex cannot span lines
                if d == "[":
                    in_class = True
                elif d == "]":
                    in_class = False
                elif d == "/" and not in_class:
                    j += 1; ok = True; break
                j += 1
            if ok:
                while j < n and src[j].isalpha():        # flags
                    j += 1
                out.append(src[i:j]); prev = "/"; i = j; continue
            # not a regex after all - fall through and treat it as a bare slash

        # --- braces, only to know when a ${ } expression ends --------------------
        if stack and isinstance(stack[-1], int):
            if c == "{":
                stack[-1] += 1
            elif c == "}":
                if stack[-1] == 0:
                    stack.pop()                 # back into the template text
                    out.append(c); prev = c; i += 1; continue
                stack[-1] -= 1

        out.append(c)
        if not c.isspace():
            prev = c
        i += 1

    return "".join(out), removed


def strip_css(src):
    """CSS has one comment form and string literals that can contain it."""
    out, i, n, removed = [], 0, len(src), 0
    while i < n:
        c = src[i]
        if c in "'\"":
            j = i + 1
            while j < n:
                if src[j] == "\\":
                    j += 2; continue
                if src[j] == c:
                    j += 1; break
                j += 1
            out.append(src[i:j]); i = j; continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            if j == -1:
                raise ValueError("unterminated /* in CSS at offset %d" % i)
            j += 2
            text = src[i:j]
            if _keep(text):
                out.append(text)
            else:
                out.append(_blanks(text)); removed += 1
            i = j; continue
        out.append(c); i += 1
    return "".join(out), removed


_JS_TYPES = {"", "text/javascript", "application/javascript", "module",
             "application/ecmascript", "text/ecmascript"}


def strip_html(src):
    """Markup comments outside script/style, and the right language inside them.

    <script type="application/json"> is DATA, not JavaScript, and is left
    exactly alone - running a JS scanner over a data island would be the same
    class of mistake as running a regex over the JavaScript.
    """
    import re
    out, removed, pos = [], 0, 0
    tag = re.compile(r"<(script|style)\b([^>]*)>", re.I)
    typ = re.compile(r"""\btype\s*=\s*["']?([^"'\s>]+)""", re.I)

    while True:
        m = tag.search(src, pos)
        end = m.start() if m else len(src)
        chunk, k = _strip_html_comments(src[pos:end])
        out.append(chunk); removed += k
        if not m:
            break
        close = re.compile(r"</%s\s*>" % m.group(1), re.I).search(src, m.end())
        body_end = close.start() if close else len(src)
        body = src[m.end():body_end]
        out.append(m.group(0))
        if m.group(1).lower() == "style":
            body, k = strip_css(body)
        else:
            t = typ.search(m.group(2) or "")
            kind = (t.group(1).strip().lower() if t else "")
            if kind in _JS_TYPES:
                body, k = strip_js(body)
            else:
                k = 0                           # a data island; left alone
        out.append(body); removed += k
        if close:
            out.append(close.group(0))
            pos = close.end()
        else:
            pos = len(src)
    return "".join(out), removed


def _strip_html_comments(text):
    out, i, n, removed = [], 0, len(text), 0
    while i < n:
        j = text.find("<!--", i)
        if j == -1:
            out.append(text[i:]); break
        out.append(text[i:j])
        k = text.find("-->", j + 4)
        if k == -1:
            # Unterminated. Copy the rest verbatim rather than guess where it
            # was meant to end.
            out.append(text[j:]); break
        k += 3
        block = text[j:k]
        # Conditional comments are markup instructions, not prose.
        if _keep(block) or block.startswith("<!--[if"):
            out.append(block)
        else:
            out.append(_blanks(block)); removed += 1
        i = k
    return "".join(out), removed


def strip_for(name, text):
    """Dispatch on file extension. Anything unrecognised is returned UNTOUCHED
    rather than guessed at."""
    low = name.lower()
    if low.endswith((".html", ".htm")):
        return strip_html(text)
    if low.endswith((".js", ".mjs")):
        return strip_js(text)
    if low.endswith(".css"):
        return strip_css(text)
    return text, 0
