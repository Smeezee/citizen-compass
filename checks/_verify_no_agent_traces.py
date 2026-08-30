#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nothing in the published payload may reveal how the site is built.

RULE16: INDEPENDENT - it reads testing/_deploy, the bytes a visitor is served,
    and knows nothing about testing/_src or the queue those bytes came from. A
    trace that never reaches the deploy is not this control's business, and a
    trace the sources do not contain is still caught if the build emits it.

WHY THIS EXISTS
===============
Sleven's instruction, 2026-08-29: nothing on the public site may hint that it
was built by anything other than a person. Not the pages, not the source a
visitor sees with Ctrl+U.

On the day this was written the deployed payload carried 1,114 comment blocks
and around 315,000 characters of internal engineering commentary, including
sentences one working session had written to another:

    "it is C1's file and not mine to edit"
    "loadout can point at this file whenever C1 wants. IT WANTS."
    "Agreeing with C1's call here, not overriding it."
    "C3's brief proposed shipping ..."

- and the site owner quoted giving instructions. Anyone opening view-source read
a conversation between a person and several named agents.

WHAT IT LOOKS FOR, AND WHAT IT DELIBERATELY DOES NOT
====================================================
Only two places can carry a trace: comments, and text a visitor reads. Data
values are excluded on purpose, because that is where the false positives live:

    "C1 Spirit"        a Crusader ship, 28 times in the ship list
    "Copilot turret"   a real seat name
    "DRACOWorker"      three.js, and it contains the letters c-o-w-o-r-k

A control that flagged those would be turned off within a week. Every pattern
here is anchored so it cannot match them.

WHAT MUST SURVIVE
=================
`@license` and `@preserve` blocks. holo.html carries three.js's MIT header and
removing it would breach the licence the library is used under. A strip that
takes it is a worse failure than the one this control exists to prevent.

Rule 15: every file is opened utf-8 with errors=replace.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY = os.path.join(ROOT, "testing", "_deploy")
SELFTEST = "--self-test" in sys.argv

TEXT_EXT = (".html", ".js", ".txt", ".css", ".json", ".svg")

# Anchored so a ship name or a library symbol cannot trip them.
RULES = [
    ("an AI vendor or product is named",
     re.compile(r"\b(claude|anthropic|chatgpt|openai|gpt-[0-9]|copilot\b(?!\s*turret)"
                r"|large language model|language model|\bLLM\b)\b", re.I)),
    ("a working session is named as an author",
     re.compile(r"\b(C1|C2|C3|CIC)\b(?=\s*(?:'s\b|/[A-Z][0-9]\b|,?\s*(?:built|wrote|"
                r"made|measured|gave|lost|reverses|wants|wanted|chose|called|said|"
                r"is right|was right|will|can|could|had|has|and I|and me)))", re.I)),
    ("an internal document is cited",
     re.compile(r"\b(ORDER|WORKORDER|FINDING|DECISION|HANDOFF|BRIEF|ERRATUM|"
                r"PROPOSAL|AMENDS|RULING|ACCEPTANCE|PROTOCOL)_[a-z0-9-]{4,}", re.I)),
    ("the internal rule numbering is quoted",
     re.compile(r"\b(hard )?rule\s+1[0-9]\b", re.I)),
    ("the site owner is quoted giving instructions",
     re.compile(r"\bSleven('s)?\b\s*(,|:|-|—)?\s*(said|says|on the|in his|"
                r"own words|call|decision|instruction|rule|test|told)", re.I)),
    ("a build or handoff artefact is named",
     re.compile(r"\b(build_deploy\.py|NEXT\.md|OWNERS\.md|LIVE\.md|"
                r"session-handoff|LATEST_HANDOFF|inbox/)", re.I)),
]

KEEP = re.compile(r"@license|@preserve", re.I)


def comments_and_text(src, path):
    """(label, chunk) pairs: comment blocks, plus visible text for .html.

    Data values are never returned. The ship list, the item catalogue and the
    keybind tables are where the false positives are and none of them is a
    place a trace can hide in prose.
    """
    out = []
    for m in re.finditer(r"<!--(.*?)-->", src, re.S):
        out.append(("comment", m.group(1), m.start()))
    for m in re.finditer(r"/\*(.*?)\*/", src, re.S):
        out.append(("comment", m.group(1), m.start()))
    if path.endswith(".html"):
        body = re.sub(r"<script\b.*?</script>", " ", src, flags=re.S | re.I)
        body = re.sub(r"<style\b.*?</style>", " ", body, flags=re.S | re.I)
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        for m in re.finditer(r">([^<>{}]{25,})<", body):
            out.append(("visible text", m.group(1), m.start()))
    return out


def scan(root):
    findings = []
    files = 0
    for dirpath, _d, names in os.walk(root):
        for n in sorted(names):
            if not n.endswith(TEXT_EXT):
                continue
            p = os.path.join(dirpath, n)
            rel = os.path.relpath(p, root)
            src = open(p, encoding="utf-8", errors="replace").read()
            files += 1
            for kind, chunk, _at in comments_and_text(src, n):
                if KEEP.search(chunk):
                    continue
                for why, rx in RULES:
                    m = rx.search(chunk)
                    if m:
                        ctx = " ".join(chunk.split())
                        i = ctx.lower().find(m.group(0).split()[0].lower())
                        i = max(0, i - 45)
                        findings.append((rel, kind, why, ctx[i:i + 130]))
    return findings, files


def report(findings, files):
    print("no agent traces: %d text file(s) in %s"
          % (files, os.path.relpath(DEPLOY, ROOT)))
    if not findings:
        print()
        print("PASS - nothing in the published payload says how it was built.")
        return True
    byfile = {}
    for rel, kind, why, ctx in findings:
        byfile.setdefault(rel, []).append((kind, why, ctx))
    print()
    print("  REFUSED - %d trace(s) in %d file(s) a visitor can fetch:"
          % (len(findings), len(byfile)))
    for rel in sorted(byfile):
        print("   %s" % rel)
        seen = set()
        for kind, why, ctx in byfile[rel]:
            if why in seen:
                continue
            seen.add(why)
            print("      %-42s (%s)" % (why, kind))
            print("         ...%s..." % ctx)
        if len(byfile[rel]) > len(seen):
            print("      + %d more of the same kinds"
                  % (len(byfile[rel]) - len(seen)))
    return False


def main():
    if not os.path.isdir(DEPLOY):
        print("NOT PERFORMED - no %s. Nothing has been built." % DEPLOY)
        return 2
    findings, files = scan(DEPLOY)
    clean = report(findings, files)
    if SELFTEST:
        return selftest(clean)
    return 0 if clean else 1


def selftest(clean_now):
    """RULE 12. Plant each kind of trace and require this control to see it."""
    print()
    print("SELF-TEST")
    # THE NEGATIVE CONTROL IS ONE ASSERTION, NOT A GATE ON THE OTHERS. An
    # earlier draft returned here when the payload was dirty, which meant that
    # on the day this control was written - the one day the payload was
    # guaranteed dirty - it could not demonstrate that it detects anything at
    # all. The planted strings are self-contained and do not care what the
    # payload contains, so they run either way and the negative control is
    # reported for what it is.
    ok_neg = clean_now
    print("  negative control: the real payload passes             %s"
          % ("ok" if clean_now else "NOT YET - payload still carries traces"))

    planted = [
        ("an AI vendor or product is named",
         "<!-- generated with Claude -->"),
        ("a working session is named as an author",
         "<!-- it is C1's file and not mine to edit -->"),
        ("an internal document is cited",
         "<!-- see ORDER_the-disclosure-bar for the table -->"),
        ("the internal rule numbering is quoted",
         "<!-- rule 14 says one writer per artifact -->"),
        ("the site owner is quoted giving instructions",
         "<!-- Sleven said: make the hull more solid -->"),
        ("a build or handoff artefact is named",
         "<!-- emitted by build_deploy.py PAGES -->"),
        ("an AI vendor named in VISIBLE text, not a comment",
         "<p>This page was written by ChatGPT and reviewed by a human.</p>"),
    ]
    ok = True
    for label, blob in planted:
        hits = []
        for kind, chunk, _a in comments_and_text(blob, "planted.html"):
            for why, rx in RULES:
                if rx.search(chunk):
                    hits.append(why)
        caught = bool(hits)
        print("  plant %-52s %s" % (label[:52], "caught" if caught else "NOT CAUGHT"))
        ok = ok and caught

    # AND THE FALSE POSITIVES IT MUST NOT FIRE ON. A control that flagged the
    # ship list would be switched off, and then it protects nothing.
    safe = [
        ('<!-- the C1 Spirit is a Crusader cargo ship -->', "the C1 Spirit ship name"),
        ('<p>Copilot turret hangar</p>', "a Copilot turret seat"),
        ('/* DRACOWorker decodes the mesh */', "three.js DRACOWorker"),
        ('<p>Built by Sleven. Not affiliated with CIG.</p>', "the site credit"),
        ('/* @license Copyright 2010-2021 Three.js Authors */', "an MIT licence header"),
    ]
    for blob, label in safe:
        fired = []
        for kind, chunk, _a in comments_and_text(blob, "safe.html"):
            if KEEP.search(chunk):
                continue
            for why, rx in RULES:
                if rx.search(chunk):
                    fired.append(why)
        print("  allow %-52s %s" % (label[:52],
                                    "correctly quiet" if not fired
                                    else "WRONGLY FLAGGED: %s" % fired[0]))
        ok = ok and not fired

    print()
    if ok and not ok_neg:
        print("DETECTION PROVEN - every planted trace is caught and no safe "
              "string is flagged - but the real payload is not clean yet, so "
              "this is not yet a passing self-test.")
        print("Exiting NON-ZERO: detection works, the payload does not.")
        return 9
    if ok:
        print("SELF-TEST PASSED - every planted trace is caught, no safe "
              "string is flagged, and the real payload is clean.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - this is not currently a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
