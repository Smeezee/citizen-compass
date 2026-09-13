#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_deploy_drift.py - _deploy is BUILT from _src, and nothing else.

RULE16: UNPROVEN - the byte comparison IS independent: _src and _deploy are two
artifacts, and a hand edit to one shows against the other. The trademark
assertion is not. It imports attribution.TRADEMARK_HTML from the module
the BUILD uses, deliberately - rule 8 and rule 14 both forbid a second
copy of that text - so the strip is judged against the build's own
definition, and a change to that definition passes here unremarked.

I7 of the 2026-08-21 order: "Confirm _deploy is genuinely built from _src and
nothing was hand-edited into _deploy only. Anything found there would be
silently destroyed by the next build, and it would look like a regression
nobody could explain."

That last sentence is the whole reason this exists. A hand edit in _deploy
WORKS. It deploys, it serves, it looks right - and then somebody runs the build
and it is gone, with no error, no warning, and nothing in the diff to explain
why a working feature stopped working.

HOW EACH FILE IS PROVEN, AND THEY ARE NOT ALL PROVEN THE SAME WAY
==================================================================
The build produces three kinds of file, and lumping them together would mean
proving the easy ones and quietly assuming the hard one:

  COPIED VERBATIM   the .gen.js files. Proven by comparing bytes against
                    their _src source. Non-destructive: a hand edit is
                    REPORTED rather than overwritten, so the evidence survives
                    being found.
  TRANSFORMED       every .html page. Two injections, and BOTH ARE DECLARED
                    HERE INDIVIDUALLY rather than the file being exempted:
                      - the attribution block (A1/A3, 2026-08-22) - the
                        trademark strip and, on ship pages, the source and
                        contact notice - appended by _with_attribution at the
                        end of every page;
                      - three.js, inlined at CC_VENDOR_THREE on the pages that
                        ask for it.
                    Everything either side of every declared injection is still
                    compared byte for byte, so a hand edit anywhere outside
                    them is caught. Before 2026-08-22 the pages really were
                    copied verbatim and were checked as such; the attribution
                    injection made that premise false, and the check reported
                    six pages as drifted until it was taught the new transform.
                    That is the check working - it noticed the build had
                    changed underneath it.
  ASSEMBLED         index.html, which is built from releases/latest.html plus
                    the layer plus a dozen substitutions. There is no way to
                    compare it to a source, so it is proven the only honest
                    way: REBUILD, and require the bytes not to move.

  ASSET PAYLOAD     models/, images/, fonts/. These have NO generator - they
                    are inputs that happen to live in the output directory, and
                    the build even READS models/ to decide which ships have a
                    3D view. Nothing here can prove their provenance and this
                    says so rather than counting them as checked.

THE REBUILD NO LONGER KEEPS WHAT IT WRITES, AND IT STILL GOES LAST.
Everything that can be checked without a rebuild is checked first. Until
2026-08-29 the rebuild wrote into the live testing/_deploy and into four
generated files in testing/_src, and the rest of the sweep reads both - so a
control's result depended on where its name sorted relative to "d", a "before"
copy taken that night was really an "after", and the deploy gate once refused a
real upload because this control had moved the payload underneath it.

Section 4 now SNAPSHOTS every file the rebuild can write, rebuilds, compares,
and PUTS THEM BACK - and then asserts that it put them back, because every
other assertion in that section is measured before the restore runs and would
pass whether or not it worked. A payload that has genuinely drifted is reported
and left exactly as found, with both versions preserved under _to_delete/.
A checker is not a writer of the artifact it audits (rule 14); testing/_deploy
has one writer and it is build_deploy.py.

If a hand edit exists, it is named before anything overwrites it, and a copy is
preserved under _to_delete/ (hard rule 1 - nothing here deletes).

`--self-test` inverts every expectation and must exit 1.

Rule 15: every open states its encoding.
"""

import ast
import hashlib
import json
import re
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "testing", "_src")

# Q13: WHO OWNS THE FILE THAT MOVED, read from OWNERS.md.
#
# On 2026-08-27 this control fired on two writes to testing/_src and the finding
# was written up as a rule 14 breach. It was not: both files were already C1's,
# in NEXT.md and in CURRENT-STATE.md, and had been for weeks. The detector was
# right to fire - the payload really was behind its source - and wrong only in
# what the READER concluded, because ownership lived in prose no program could
# read.
#
# So drift now says WHOSE source moved. A file with a declared owner is a stale
# payload and says so; a file with NO declared owner is a gap in OWNERS.md, and
# OWNERS.md's own text calls finding one worth reporting. Neither is asserted -
# this control's subject is whether _deploy was built from _src, not who typed
# the source - but a reader gets the answer without having to guess at it.
OWNERS_MD = os.path.join(ROOT, "OWNERS.md")


def owner_of(rel_path):
    """The declared owner of a repo-relative path, or None. Never raises."""
    try:
        with open(OWNERS_MD, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return None
    who, best, best_len = None, None, -1
    for line in lines:
        if line.startswith("## "):
            who = line[3:].split()[0].strip().rstrip(".")
            continue
        if who and line.startswith("    ") and line.strip():
            claim = line.strip()
            if claim.startswith("#") or " " in claim:
                continue
            norm = rel_path.replace(os.sep, "/")
            hit = norm == claim or (claim.endswith("/") and norm.startswith(claim))
            if hit and len(claim) > best_len:
                best, best_len = who, len(claim)
    return best


def owner_note(src_name):
    rel = "testing/_src/" + src_name
    who = owner_of(rel)
    if who:
        return ("%s is owned by %s - this is a payload behind its source, "
                "not an unowned write" % (rel, who))
    return ("%s has NO declared owner in OWNERS.md - that is a gap rather than "
            "permission, and is worth reporting" % rel)

DEPLOY = os.path.join(ROOT, "testing", "_deploy")
BUILD = os.path.join(SRC, "build_deploy.py")

SELFTEST = "--self-test" in sys.argv

ASSET_DIRS = ("models", "images", "fonts")
VENDOR_MARKER = "<!-- CC_VENDOR_THREE -->"

# THE DISCLOSURE-BAR CSS, THE THIRD DECLARED INJECTION.
#
# Added to the build on 2026-08-27 - one `_disc.css`, substituted into four
# pages so the bars cannot drift into five variations. This control did not
# know about it, so from that morning section 3 reported keybinds.html,
# loadout.html and find.html as no longer containing their source text.
#
# THAT IS WORSE THAN A MISSING CHECK. This section is what makes an
# unauthorised write to _deploy loud (rule 14). A red-by-default section is one
# nobody can read a real hand edit out of - the noise and the signal look the
# same. Declared here for exactly that reason, and pinned as narrowly as the
# vendor marker is: the gap must be the CSS file byte for byte, not "some CSS".
DISC_MARKER = "/* CC_DISC_CSS */"
DISC_CSS_PATH = os.path.join(SRC, "_disc.css")

# THE GLOSSARY, DECLARED 2026-08-30 - AND THIS CONTROL FOUND IT FIRST.
#
# Q35 moved the glossary into one shared include and build_deploy.py began
# substituting it wherever a page carries the marker. I added that injection and
# did not declare it here, and the very next sweep went red on loadout.html:
#
#     loadout.html no longer contains its _src/loadout.src.html text outside the
#     declared injections (disclosure and vendor and attribution)
#
# WHICH IS THE CONTROL DOING EXACTLY ITS JOB. An injection nobody declared and a
# hand edit in _deploy are the same shape from the outside, and this section
# exists so the second one is loud. Declaring it is the fix; widening the test
# would have removed the only thing that noticed.
GLOSS_MARKER = "<!-- CC_GLOSSARY -->"
GLOSS_INC_PATH = os.path.join(SRC, "cc_glossary.inc.html")

# THE ONE LINE THE BUILD IS ALLOWED TO REWRITE ON THE WAY INTO _deploy.
#
# `loadout_model.gen.js` names where a 3D model lives, and that differs between
# the two worlds: in _src the ship page reads `../sc-ships/`, in _deploy the
# models are siblings under `models/`. build_deploy.py swaps exactly one line.
#
# DECLARED HERE, NARROWLY, AND THE REST STILL COMPARED BYTE FOR BYTE - the same
# treatment the vendor marker gets. The alternative is exempting the whole file,
# which would mean a hand edit anywhere in it went unnoticed. What is checked is
# that the ONLY difference is this line, and that the deployed value is the
# deploy one rather than something else entirely.
SEAM_FILES = {
    "loadout_model.gen.js": (
        "const LOADOUT_MODEL_URL=",
        '"../sc-ships/{dir}/model_scaled.glb"',
        '"models/{file}"',
    ),
}

# THE TRADEMARK LINE IS READ FROM THE BUILD'S OWN CONSTANT, NEVER RESTATED.
#
# Hard rule 8 - legal text is Sleven's alone, and a checker carrying its own
# copy of it would be a second writer for that fact (rule 14). It would also be
# the worst kind of useless: it would keep passing while the page said
# something different, because both sides would be reading the checker's copy
# of the wording rather than the page's. attribution.py is where the build gets
# this string, so it is where this gets it.
#
# _with_attribution itself is NOT imported - it lives in build_deploy.py, which
# is a script that runs a full build on import. Its placement rule is mirrored
# in attribution_point() below, and section 4's rebuild is what proves the two
# still agree.
sys.path.insert(0, SRC)

# THE COMMENT STRIP IS THE FOURTH TRANSFORM  (Q31, 2026-08-30).
#
# The build removes every comment on the way into _deploy - Sleven's
# instruction that nothing public may hint at how the site was built. That made
# every copied file differ from its source and this control said so, which is
# what it is for. Reconciling it is not the same as exempting it.
#
# NOT AN EXEMPTION. "Comment-shaped regions may differ" would be a hole the
# width of any comment anybody cares to add. Instead the SAME function the
# build uses is applied to the _src side, so everything outside comments is
# still held to byte equality - and a comment HAND-ADDED to _deploy still
# shows, because the _deploy side is never stripped here.
#
# RULE 16: this shares a source with the build, deliberately, the same trade
# attribution.TRADEMARK_HTML makes below. A change to the stripper itself
# passes here unremarked; checks/_verify_comment_strip.py is what closes that,
# by proving the stripper against node rather than against itself.
try:
    import strip_comments as _strip
    STRIP_ERROR = None
except Exception as _exc:                      # pragma: no cover - reported
    _strip = None
    STRIP_ERROR = ("NOT PERFORMED - testing/_src/strip_comments.py could not "
                   "be imported (%s), so what the build removes is unknown. "
                   "Reported, never passed." % _exc)

try:
    import attribution as _attr
    TRADEMARK_HTML = _attr.TRADEMARK_HTML
    ATTR_IMPORT_ERROR = None
except Exception as _exc:                      # pragma: no cover - reported
    TRADEMARK_HTML = None
    ATTR_IMPORT_ERROR = (
        "NOT PERFORMED - testing/_src/attribution.py could not be imported "
        "(%s), so what the build injects is unknown and the injected block "
        "cannot be checked. Reported, never passed." % _exc)


_passed = []
_failed = []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def text_of(path):
    """Deliberately NOT named after pathlib's read-text method.

    checks/file_checks.py's missing_encoding checker matches on the CALL SITE
    NAME, so a helper with that name makes every use of it look like a
    pathlib call with no encoding= - four false findings in this file alone,
    on lines that do specify utf-8 one frame down.

    A checker that cries wolf is a checker somebody eventually silences, and
    this one is what makes hard rule 15 machine-enforced. Shadowing its
    subject's name is not worth it.
    """
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def sha(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()


PAGES_SRC = os.path.join(SRC, "deploy_pages.py")


def build_pages():
    """The one PAGES list, read WITHOUT running the build.

    Parsed out of the source rather than duplicated here. A copy of this list
    living in a checker is a second writer for the same fact (rule 14), and it
    would drift the first time a page was added.

    IT MOVED ON 2026-08-22, and this function moved with it. PAGES used to be
    declared in build_deploy.py and hand-mirrored in check_deploy_clean.py's
    allow-list; those two drifted twice, so the list was extracted to
    testing/_src/deploy_pages.py and both now import it. This parser followed.

    Note what happened in between, because it is the point of writing checks
    this way: when the list moved, THIS CHECK REPORTED "NOT PERFORMED" rather
    than finding nothing and calling _deploy clean. A parser that returned an
    empty list would have passed every assertion below it vacuously.
    """
    if not os.path.exists(PAGES_SRC):
        return None
    tree = ast.parse(text_of(PAGES_SRC), filename=PAGES_SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PAGES":
                    return [tuple(ast.literal_eval(e)) for e in node.value.elts]
    return None


def assembled_files():
    """The files the build ASSEMBLES rather than copies, read out of
    deploy_pages.py.

    Q54, 2026-09-11. This existed as a hand-written {"index.html"} in THREE
    places - here, in build_deploy.py's deploy-guard call, and in
    deploy_pages.py itself. Two of the three were copies, and the day Q54
    added classic.html and _redirects to the real one the build refused its
    own payload while this control called the two files strays. Both were
    correct about what they had been told and both had been told something
    stale, which is the two-lists defect deploy_pages.py was created to end.

    Returns None if it cannot be read, which the caller reports rather than
    treating as an empty set - an empty set here would call every assembled
    file a stray and bury the real answer in noise.
    """
    if not os.path.exists(PAGES_SRC):
        return None
    tree = ast.parse(text_of(PAGES_SRC), filename=PAGES_SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ASSEMBLED":
                    return set(ast.literal_eval(node.value))
    return None


def front_door_page():
    """WHICH page the front door serves, read out of deploy_pages.py.

    Q54, 2026-09-11. That page - and only that page - has the password gate
    injected into it by the build, so this control has to expect the gate
    there and to go on refusing it everywhere else. Parsed rather than
    restated, for the same reason PAGES is: a literal here would be a second
    writer for the same fact, and the day the front door moves again this
    check would still be checking yesterday's answer while PASSING.

    Returns None if the name is absent, which the caller reports as NOT
    PERFORMED. A None that quietly meant "no page is gated" would pass a
    payload whose gate had been stripped.
    """
    if not os.path.exists(PAGES_SRC):
        return None
    tree = ast.parse(text_of(PAGES_SRC), filename=PAGES_SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and \
                        target.id == "FRONT_DOOR_PAGE":
                    return ast.literal_eval(node.value)
    return None


BUILD_SRC = os.path.join(SRC, "build_deploy.py")


def ship_content_pages():
    """WHICH pages carry A3's source-and-contact notice, read out of the build.

    Parsed, not restated, for the same reason PAGES is: a copy of this set
    living in a checker is a second writer for the same fact (rule 14), and the
    day a page starts showing ship content the checker would still be checking
    yesterday's answer - and PASSING, which is worse than failing.

    ast.parse does not execute build_deploy.py. Importing it would: it is a
    script that runs a full build at module level.
    """
    if not os.path.exists(BUILD_SRC):
        return None
    tree = ast.parse(text_of(BUILD_SRC), filename=BUILD_SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and \
                        target.id == "_SHIP_CONTENT_PAGES":
                    return set(ast.literal_eval(node.value))
    return None


def attribution_point(s_text):
    """WHERE the build appends the attribution block, by the build's own rule.

    build_deploy._with_attribution inserts before the first </body>, else
    before the first </html>, else appends after rstrip(). That three-way rule
    exists because only ONE of the seven pages writes a </body> and two close
    with neither tag - a rule that assumed </body> would have put the legal
    notice on one page and silently skipped the rest.

    Returns the source text split either side of the insertion point.
    """
    for tag in ("</body>", "</html>"):
        i = s_text.find(tag)
        if i != -1:
            return s_text[:i], s_text[i:]
    return s_text.rstrip() + "\n", ""


# The attribution block is appended at a POSITION rather than at a marker, so
# it is given one here and spliced into the source text. That lets every
# injection be found the same way - by where it appears - instead of each new
# one needing another hand-written ordering case. The sentinel is a byte pair
# no HTML source contains.
ATTR_SENTINEL = "\x00CC_ATTRIBUTION_POINT\x00"
def src_as_deployed(src_name, text):
    """The _src text as the build leaves it: comments gone, markers intact.

    THE MARKERS ARE THEMSELVES COMMENTS - <!-- CC_VENDOR_THREE --> and
    /* CC_DISC_CSS */ - so a plain strip deletes the very anchors the
    segmentation is built on, and every page then diverges at the first one.
    Measured on 2026-08-30: keybinds.html and loadout.html both diverged
    exactly at the disclosure marker, which is what sent the first attempt at
    this looking for a drift that was not there.

    Stripping the segments individually instead does not work either: a segment
    can begin inside a <script> block, and the stripper then reads JavaScript
    as markup. loadout.html, with 437 template literals, is where that showed.

    So the markers are protected, the WHOLE document is stripped exactly as the
    build strips it, and the markers are put back.
    """
    if _strip is None:
        return text
    guard = {}
    for n, (lit, _nm) in enumerate(INJECTION_MARKERS):
        if lit and lit in text:
            token = "@@CCMARK%d@@" % n
            guard[token] = lit
            text = text.replace(lit, token)
    try:
        out, _n = _strip.strip_for(src_name, text)
    except ValueError:
        # Malformed for the stripper. Return the text UNCHANGED so the
        # comparison fails loudly rather than passing something never compared.
        for token, lit in guard.items():
            text = text.replace(token, lit)
        return text
    for token, lit in guard.items():
        out = out.replace(token, lit)
    return _share_card_values(out)


# THE SHARE CARD, DECLARED 2026-09-13 - AND THIS CONTROL FOUND IT FIRST, AGAIN.
# build_deploy.py fills two VALUE markers in loadout.src.html's Open Graph tags:
# __CC_ORIGIN__ with the host the payload is served from, and __CC_PATCH__ with
# " · Patch <n>" from the snapshot manifest. They are substitutions of a value
# rather than injections of a block, so they are applied to the SOURCE here,
# before it is compared - with the TESTING origin, because _deploy is the
# testing payload, and the patch read the way the build reads it. Every other
# byte of those tags is still held to equality, so a hand edit still fails.
# If the patch cannot be read, the markers are left in place and the comparison
# fails loudly rather than passing something that was never compared.
SHARE_ORIGIN_MARKER = "__CC_ORIGIN__"
SHARE_PATCH_MARKER = "__CC_PATCH__"
SHARE_TESTING_ORIGIN = "https://citizencompasstesting.citizencompass-contact.workers.dev"
_share_patch_cache = []


def _share_card_values(text):
    if SHARE_ORIGIN_MARKER not in text and SHARE_PATCH_MARKER not in text:
        return text
    if not _share_patch_cache:
        try:
            if ROOT not in sys.path:
                sys.path.insert(0, ROOT)
            import build_loadout_data as _bl
            _share_patch_cache.append(" · Patch %s" % _bl.LAST_VERIFIED_PATCH
                                      if _bl.LAST_VERIFIED_PATCH else "")
        except BaseException:                     # noqa: BLE001 - incl. its sys.exit
            _share_patch_cache.append(None)
    patch = _share_patch_cache[0]
    if patch is None:
        return text
    return (text.replace(SHARE_ORIGIN_MARKER, SHARE_TESTING_ORIGIN)
                .replace(SHARE_PATCH_MARKER, patch))


# The password gate is injected at a POSITION too, like attribution, so it
# gets a sentinel on the same principle. Q54, 2026-09-11.
GATE_SENTINEL = "\x00CC_GATE_POINT\x00"


def gate_point(s_text):
    """WHERE the build injects the password gate, by the build's own rule.

    build_deploy inserts it immediately after the first `<body ...>` tag
    closes, because the gate has to be the first thing in the body for its
    `body > *:not(#cc-gate)` rule to hide everything else.

    Returns the index, or None if there is no <body> - which the build itself
    refuses to proceed past, so this returning None means the source changed
    shape and the caller must report rather than assume.
    """
    i = s_text.lower().find("<body")
    if i == -1:
        return None
    j = s_text.find(">", i)
    if j == -1:
        return None
    return j + 1


# The testing stamp is the front door's second positional injection, added
# 2026-09-11 when Q54's front-door move left the served entry point with no
# stamp on it while index.html went on carrying one.
STAMP_SENTINEL = "\x00CC_STAMP_POINT\x00"


def stamp_point(s_text):
    """WHERE the build injects the testing stamp, by the build's own rule.

    build_deploy puts it immediately AFTER `<span id="ver">` closes - a sibling
    of the version, not a child of it.

    IT USED TO GO INSIDE. That put it under `@media(max-width:560px){#top
    span{display:none}}`, so on a phone the stamp was in the bytes and not on
    the screen, and the deploy guard - which reads bytes - passed anyway.

    Returns the index, or None if that span is not there - which the build
    itself refuses to proceed past, so None means the source changed shape and
    the caller must report rather than assume.
    """
    m = re.search(r'(<span id="ver">.*?)(</span>)', s_text, re.S)
    return m.end(2) if m else None


INJECTION_MARKERS = (
    (ATTR_SENTINEL, "attribution"),
    (VENDOR_MARKER, "vendor"),
    (DISC_MARKER, "disclosure"),
    (GLOSS_MARKER, "glossary"),
    (GATE_SENTINEL, "gate"),
    (STAMP_SENTINEL, "stamp"),
)


def declared_transforms(s_text, gated=False):
    """The source text cut into the literal segments the deploy file MUST
    still contain, in order, with one declared injection between each pair.

    Returns (segments, gap_names) where len(segments) == len(gap_names) + 1.

    REWRITTEN 2026-08-27, when the disclosure CSS became a third injection.
    The old form enumerated the two possible orderings of vendor-vs-attribution
    by hand; a third marker would have needed six, and the day somebody added a
    fourth the check would have started reporting drift that was not there.
    This finds every marker by POSITION, in source order, however many there
    are - and a marker appearing TWICE now yields two gaps rather than leaving
    the second copy stranded in a segment that can never match.
    """
    before, after = attribution_point(s_text)
    rest = before + ATTR_SENTINEL + after
    # The gate, for the one page that becomes the front door. Spliced after
    # the attribution sentinel because its position is EARLY in the body and
    # attribution's is at the closing tag - so the two never collide, and
    # finding the <body> in `rest` finds the same place it is in s_text.
    if gated:
        gp = gate_point(rest)
        if gp is not None:
            rest = rest[:gp] + GATE_SENTINEL + rest[gp:]
        # AFTER the gate, and searched afresh, because splicing the gate
        # sentinel in shifts every index after it. The stamp point is inside
        # the masthead and the gate point is the top of <body>, so the order
        # is fixed and they cannot collide.
        sp = stamp_point(rest)
        if sp is not None:
            rest = rest[:sp] + STAMP_SENTINEL + rest[sp:]
    segments, names = [], []
    while True:
        hit = None
        for lit, nm in INJECTION_MARKERS:
            i = rest.find(lit)
            if i != -1 and (hit is None or i < hit[0]):
                hit = (i, lit, nm)
        if hit is None:
            segments.append(rest)
            return segments, names
        i, lit, nm = hit
        segments.append(rest[:i])
        names.append(nm)
        rest = rest[i + len(lit):]


def split_by_declared(d_text, segments):
    """Match d_text as segments[0] + gap + segments[1] + gap + ... in order,
    anchored at BOTH ends. Returns the gap contents, or None if the deployed
    file no longer contains its source text where it should.

    Anchoring both ends is the point: content appended past the last segment,
    or prepended before the first, is a hand edit and must not be absorbed
    into a gap.
    """
    if not d_text.startswith(segments[0]):
        return None
    if segments[-1] and not d_text.endswith(segments[-1]):
        return None
    pos = len(segments[0])
    end = len(d_text) - len(segments[-1])
    if end < pos:
        return None
    gaps = []
    for seg in segments[1:-1]:
        i = d_text.find(seg, pos, end)
        if i == -1:
            return None
        gaps.append(d_text[pos:i])
        pos = i + len(seg)
    gaps.append(d_text[pos:end])
    return gaps


def gap_problem(name, gap, out_name, ship_pages):
    """What is wrong with what the build put in a declared gap, or None.

    A gap is DECLARED, not unexamined. "The build may inject here" is not the
    same as "anything may appear here", and the difference is the whole value
    of declaring it narrowly. Two things would walk straight through a gap that
    merely had to CONTAIN the trademark line: text appended after the strip on
    the two pages that close with no tag at all, and a hand edit to the wording
    of the strip itself - which is precisely the text hard rule 8 says nobody
    but Sleven may touch.

    So the attribution gap is pinned at both ends:

      not a ship page   the gap must be EXACTLY attribution.trademark_block(),
                        byte for byte, and nothing else.
      a ship page       the gap must END with that same block and START with
                        SOURCE_NOTICE_CSS. Only the notice body between them is
                        unpinned, because the contact address inside it is
                        configuration rather than source - and that body is
                        _verify_attribution's subject, not this one's.
    """
    if name == "gate":
        # PINNED BY SHAPE AND BY ONE SPECIFIC FAILURE, not byte for byte.
        #
        # Byte equality would need the build's own GATE literal, and importing
        # build_deploy.py to get it runs a full build. Parsing it out is
        # possible but the string is assembled with a substitution, so what
        # ships is not what the literal says - the expectation would have to
        # reimplement the substitution, which is the same source proving
        # itself (rule 16). So this pins the three things that actually go
        # wrong, and says plainly that it is not byte equality.
        g = gap.strip()
        if not g:
            return ("the front door's password gate is MISSING - the bare URL "
                    "would serve the site to anyone, and nothing else would "
                    "have said so")
        if 'id="cc-gate"' not in g:
            return "what was injected at the front door's body is not the gate"
        if "cc-locked" not in g:
            return ("the gate is there but carries no cc-locked rule, so it "
                    "would render ON TOP OF a fully visible page")
        if "__GATEHASH__" in g:
            # The one that would look completely fine and let nobody in.
            return ("the gate shipped with __GATEHASH__ unsubstituted - the "
                    "password could never match and the front door would be "
                    "shut to everyone including Sleven")
        if not g.startswith("<style"):
            return ("something is in front of the gate inside <body> - the "
                    "gap is the gate's and nothing else's")
        if not g.endswith("</script>"):
            return ("something follows the gate inside its own gap - text "
                    "appended here is exactly what a hand edit looks like")
        return None
    if name == "stamp":
        # PINNED TO THE SHAPE THE BUILD WRITES, including the date format.
        # "a stamp is there" would pass a stamp whose date had been hand-edited
        # in _deploy, and the whole point of the stamp is that its date is
        # derived from the clock rather than typed.
        g = gap.strip()
        if not g:
            return ("the front door carries NO testing stamp - it would be "
                    "indistinguishable from the live site, which is the defect "
                    "the stamp exists to prevent")
        m = re.match(r'^<span class="cc-teststamp" style="([^"]*)">'
                     r'testing (\d{4}-\d{2}-\d{2})</span>$', g)
        if not m:
            return ("what was injected beside the version is not the testing "
                    "stamp the build writes: %r" % g[:80])
        # THE ONE DECLARATION THAT DOES THE WORK, pinned by itself.
        # Everything else in that style attribute is appearance. `display:
        # inline` is what beats `#top span{display:none}` at phone width, and
        # without it the stamp is present in the bytes and invisible on a
        # phone - which is the exact defect this stamp was moved to fix, and
        # which every byte-level check would still have called a pass.
        if 'display:inline' not in m.group(1):
            return ("the testing stamp carries no display:inline, so the "
                    "page's own max-width:560px rule hides it on a phone - "
                    "present in the bytes, invisible on the screen")
        # THE DATE, AGAINST THE OTHER STAMPED PAGE IN THE SAME PAYLOAD.
        # One build stamps both from one clock read, so they agree or something
        # edited one of them. The expectation comes from a different file than
        # the subject, which is the only way this check is worth anything.
        _idx = os.path.join(DEPLOY, "index.html")
        if not os.path.exists(_idx):
            return ("NOT PERFORMED - index.html is absent, so the front door's "
                    "stamp date cannot be checked against anything. Reported, "
                    "never passed.")
        _other = re.search(r'>testing (\d{4}-\d{2}-\d{2})<', text_of(_idx))
        if not _other:
            return ("NOT PERFORMED - index.html carries no testing stamp, so "
                    "the front door's stamp date has nothing to agree with. "
                    "Reported, never passed.")
        if m.group(2) != _other.group(1):
            return ("the front door is stamped %s and index.html is stamped "
                    "%s. One build stamps both from one clock read, so one of "
                    "them was edited after the build."
                    % (m.group(2), _other.group(1)))
        return None
    if name == "vendor":
        if not gap.strip():
            return "the vendor marker was replaced with nothing"
        if VENDOR_MARKER in gap:
            return "the vendor marker is still there - three.js was not inlined"
        return None
    if name == "disclosure":
        # Pinned to the file, byte for byte. "Some CSS is there" would pass a
        # page whose bars had been restyled by hand in _deploy only - which is
        # the exact class of change no source diff would ever show.
        if not os.path.exists(DISC_CSS_PATH):
            return ("NOT PERFORMED - testing/_src/_disc.css is missing, so what "
                    "the build substitutes for %s is unknown and the gap cannot "
                    "be checked. Reported, never passed." % DISC_MARKER)
        if not gap.strip():
            return "the disclosure-CSS marker was replaced with nothing"
        if DISC_MARKER in gap:
            return ("the disclosure-CSS marker is still there - the shared CSS "
                    "was not substituted and the bars ship unstyled")
        # AS THE BUILD LEAVES IT: _disc.css is substituted in and the page
        # is then stripped, so what ships is the CSS without its comments.
        # Still byte for byte - against the right expectation.
        _want_css = text_of(DISC_CSS_PATH)
        if _strip is not None:
            try:
                _want_css, _dn = _strip.strip_css(_want_css)
            except ValueError:
                pass
        if gap != _want_css:
            return ("what was substituted is not _disc.css byte for byte - it "
                    "was edited in _deploy, or the build substituted something "
                    "else")
        return None
    if name == "glossary":
        # Pinned to the include byte for byte, for the same reason the
        # disclosure CSS is: "the glossary is there" would pass a page whose
        # TERMS had been edited in _deploy only. A definition changed where no
        # source diff shows it is precisely the class this section exists for,
        # and a wrong definition is worse than none - the site's whole claim is
        # that what it says is checkable.
        if not os.path.exists(GLOSS_INC_PATH):
            return ("NOT PERFORMED - testing/_src/cc_glossary.inc.html is "
                    "missing, so what the build substitutes for %s is unknown "
                    "and the gap cannot be checked. Reported, never passed."
                    % GLOSS_MARKER)
        if not gap.strip():
            return "the glossary marker was replaced with nothing"
        if GLOSS_MARKER in gap:
            return ("the glossary marker is still there - the shared include "
                    "was not substituted and the page explains nothing")
        # AS THE BUILD LEAVES IT. The include is substituted in and the page is
        # then comment-stripped, so what ships is the include without its
        # comments. strip_for dispatches on the .html suffix.
        _want = text_of(GLOSS_INC_PATH)
        if _strip is not None:
            try:
                _want, _gn = _strip.strip_for("cc_glossary.inc.html", _want)
            except ValueError:
                pass
        if gap != _want:
            return ("what was substituted is not cc_glossary.inc.html byte for "
                    "byte - it was edited in _deploy, or the build substituted "
                    "something else")
        return None
    if name == "attribution":
        if ATTR_IMPORT_ERROR:
            return ATTR_IMPORT_ERROR
        if ship_pages is None:
            return ("NOT PERFORMED - _SHIP_CONTENT_PAGES could not be read out "
                    "of build_deploy.py, so which pages carry the source "
                    "notice is unknown. Reported, never passed.")
        if not gap.strip():
            return "nothing was appended - the page carries NO trademark strip"
        expected = _attr.trademark_block() + "\n"
        if gap == expected:
            return None
        if out_name in ship_pages:
            if not gap.endswith("\n" + expected):
                return ("the appended block does not END with "
                        "attribution.trademark_block() - either the strip was "
                        "edited in _deploy, or something was added after it")
            if not gap.startswith(_attr.SOURCE_NOTICE_CSS):
                return ("the appended block does not START with the source "
                        "notice - something was inserted before it")
            return None
        if TRADEMARK_HTML not in gap:
            return "what was appended carries no trademark line at all"
        return ("what was appended is not exactly "
                "attribution.trademark_block() - it was edited in _deploy, or "
                "something was added around it")
    return "unknown transform %r" % name       # pragma: no cover - unreachable


def page_problems(src_name, out_name, ship_pages, front_door=None):
    """THE ONE COMPARISON, in one place.

    Section 3 runs this over _deploy. Section 5 runs THE SAME FUNCTION over
    deliberately corrupted copies. That matters more than it looks: the plant
    test used to re-implement the byte compare inline, so what it proved was
    that a comparison written on the spot could fail - not that the one
    actually guarding the directory could. The two agreed right up until the
    build changed, and then the plant would have gone on passing while
    section 3 was checking something else entirely.
    """
    s_path = os.path.join(SRC, src_name)
    d_path = os.path.join(DEPLOY, out_name)
    if not os.path.exists(d_path):
        return ["%s is MISSING from _deploy" % out_name]
    if src_name.lower().endswith(".png"):
        # BINARY, COPIED BYTE FOR BYTE (build_deploy.py BINARY_EXT, the share
        # card, 2026-09-13). Read as text it crashed this whole check on its
        # first byte (0x89) and took section 3 down with it. No transform is
        # declared for an image, so any difference at all is a hand edit.
        if read_bytes(s_path) != read_bytes(d_path):
            return ["%s differs from _src/%s byte for byte  [%s]"
                    % (out_name, src_name, owner_note(src_name))]
        return []
    if out_name == "find_checksum.gen.js":
        # THE FIFTH DECLARED TRANSFORM, AND IT IS VERIFIED RATHER THAN EXEMPTED.
        #
        # build_find_data.py hashes the _src data file; Q31's comment strip then
        # removes that file's header on the way into _deploy, so the published
        # sha256 described bytes nobody could download. The build now recomputes
        # the checksum over the SERVED bytes, which makes this file legitimately
        # differ from its source.
        #
        # An exemption here would be a hole in the one file whose entire job is
        # to be trustworthy. So instead of tolerating the difference, this
        # RE-DERIVES it: hash what _deploy actually serves and require the
        # published figures to be exactly that. A hand-edited checksum still
        # fails, and so does a stale one.
        import hashlib as _hl
        data = os.path.join(DEPLOY, "find_data.gen.js")
        if not os.path.exists(data):
            return ["find_checksum.gen.js is in _deploy but find_data.gen.js "
                    "is not - a checksum for a file that is not served"]
        raw = read_bytes(data)
        want_sha = _hl.sha256(raw).hexdigest()
        got = text_of(d_path)
        if want_sha not in got:
            return ["find_checksum.gen.js does not carry the sha256 of the "
                    "find_data.gen.js actually in _deploy - the page would tell "
                    "a visitor their correct download is corrupt"]
        if str(len(raw)) not in got:
            return ["find_checksum.gen.js does not carry the byte count of the "
                    "find_data.gen.js actually in _deploy (%d)" % len(raw)]
        return []
    if out_name in SEAM_FILES:
        prefix, dev, dep = SEAM_FILES[out_name]
        s_lines = src_as_deployed(src_name, text_of(s_path)).split(chr(10))
        d_lines = text_of(d_path).split("\n")
        if len(s_lines) != len(d_lines):
            return ["%s has a different number of lines from _src/%s"
                    % (out_name, src_name)]
        bad = [i for i, (a, b) in enumerate(zip(s_lines, d_lines)) if a != b]
        if len(bad) != 1:
            return ["%s differs from _src/%s on %d lines - only the model-path "
                    "seam may differ" % (out_name, src_name, len(bad))]
        i = bad[0]
        if not (s_lines[i].startswith(prefix) and dev in s_lines[i]
                and d_lines[i].startswith(prefix) and dep in d_lines[i]):
            return ["%s's one difference is NOT the model-path seam: "
                    "_src %r vs _deploy %r"
                    % (out_name, s_lines[i][:60], d_lines[i][:60])]
        return []
    if not src_name.endswith(".html"):
        # COPIED VERBATIM. No transform is declared for these, so any
        # difference at all is a hand edit.
        # COMPARED AFTER THE BUILD'S OWN STRIP rather than as raw bytes.
        # Everything outside comments is still held to equality, and a
        # comment hand-added to _deploy still shows - only the _src side
        # is stripped.
        if src_as_deployed(src_name, text_of(s_path)) != text_of(d_path):
            return ["%s differs from _src/%s  [%s]"
                    % (out_name, src_name, owner_note(src_name))]
        return []
    # TRANSFORMED. Every injection the build makes is declared, and the source
    # text either side of every one of them must still be there, byte for byte,
    # anchored at BOTH ends of the file.
    s_text = src_as_deployed(src_name, text_of(s_path))
    d_text = text_of(d_path)
    # THE BUILD NORMALISES LINE ENDINGS - it writes every page with
    # newline='\n' - and `find.src.html` is the one source still saved CRLF.
    # So this control has to model that transform as well, or it reports the
    # entire file as changed from its second byte and says "attribution",
    # which is the least useful true statement available.
    #
    # DECLARED, NOT WAVED THROUGH. What is tolerated is the build's own
    # normalisation, one direction only: CRLF in _src becoming LF in _deploy.
    # A CRLF in _deploy is not that, and is reported - because the build cannot
    # produce one, so something else put it there.
    if "\r\n" in d_text:
        return ["%s contains CRLF line endings, which the build cannot "
                "produce - it writes every page with newline='\\n'. Something "
                "edited it after the build." % out_name]
    s_text = s_text.replace("\r\n", "\n")
    # Q54: only the front-door page carries the gate. Every other page is
    # still held to having NO gate, because `gated` stays False for them and
    # an unexpected gate then lands in no declared gap at all.
    segments, gap_names = declared_transforms(
        s_text, gated=(front_door is not None and out_name == front_door))
    gaps = split_by_declared(d_text, segments)
    if gaps is None:
        return ["%s no longer contains its _src/%s text outside the declared "
                "injections (%s)  [%s]"
                % (out_name, src_name, " and ".join(gap_names),
                   owner_note(src_name))]
    found = []
    for name, gap in zip(gap_names, gaps):
        problem = gap_problem(name, gap, out_name, ship_pages)
        if problem:
            found.append("%s - %s" % (out_name, problem))
    return found


# ---------------------------------------------------------------------------
# THE REBUILD DOES NOT GET TO KEEP WHAT IT WRITES  (2026-08-29)
#
# Section 4 still proves index.html the only honest way an assembled file can
# be proven: REBUILD, and require the bytes not to move. What changed today is
# where the rebuild's output is allowed to land.
#
# Until now the rebuild wrote into the live testing/_deploy AND into four
# generated files in testing/_src, and the whole sweep reads both. That cost
# three separate things, none of them theoretical:
#
#   ORDERING      a control's result depended on where its name sorted relative
#                 to "d". Controls before this one measured one state and
#                 controls after measured another. On 2026-08-28
#                 _verify_marker_provenance and _verify_marker_spread FAILED in
#                 the sweep and passed ten minutes later, while
#                 _verify_marker_census passed in the sweep and failed after.
#                 Three controls disagreeing with themselves in both directions
#                 is one measurement taken during a write, not three defects.
#   EVIDENCE      at 22:23 that night this rebuilt the payload after C1's 22:19
#                 data fix, so a "before" copy taken at 23:37 was an "after".
#                 It reported 0 hulls lost markers while the Tiburon had gone
#                 from seventeen to none.
#   A REAL ABORT  the deploy gate refused an upload because the payload hash
#                 moved between two of Sleven's commands. What moved it was the
#                 sweep's own drift control.
#
# So: SNAPSHOT, REBUILD, COMPARE, RESTORE. The comparison is untouched and
# nothing is exempted from it. Afterwards every file this wrote to is put back
# byte for byte, and THAT IS ASSERTED rather than assumed - if the restore ever
# silently fails, the last check in section 4 goes red. Rule 12: the guard is
# proven by behaviour, not by reading the code that implements it.
#
# It also settles a rule 14 question that should not have been open. A CHECKER
# IS NOT A WRITER OF THE ARTIFACT IT AUDITS. testing/_deploy has one writer,
# build_deploy.py, and this is not it. A payload that has genuinely drifted is
# now REPORTED and left exactly as found - which is what sections 1 to 3
# already did, and what a findings-only auditor is for.
#
# THE RECEIPT IS RESTORED WITH EVERYTHING ELSE, AND THAT MATTERS ON ITS OWN.
# build_deploy.py writes testing/_src/.last_build.json, and
# scripts/deploy_testing.ps1 reads it to decide whether a build succeeded. A
# rebuild run for AUDIT must not leave behind a receipt that authorises an
# upload. Putting the previous receipt back is the difference between "the
# payload was built ok" and "a checker rebuilt something once".
# ---------------------------------------------------------------------------
# THE FOURTH DECLARED INJECTION: THE TESTING DATE STAMP  (2026-08-30)
#
# build_deploy.py:741 stamps the UTC date into index.html - twice, the <title>
# and the <h1> - on the TESTING payload only; `--live` skips it and says so.
# It is the only thing on the page that tells a viewer which build they are
# looking at, and it is worth more than a convenient byte comparison.
#
# BUT IT MAKES THE REBUILD NON-REPRODUCIBLE ACROSS 00:00 UTC. Section 4's whole
# proof of the assembled file is "rebuild and require the bytes not to move",
# and across the boundary they move on their own. A sweep whose snapshot is
# taken before midnight and whose rebuild lands after it would name index.html
# as drifted, preserve both copies as evidence, and go red - for the clock.
#
# Found 2026-08-30 by a payload fingerprint moving when nothing had been built:
# served said `testing 2026-08-29`, local said `testing 2026-08-30`, and the
# other nineteen files were identical.
# docs/FINDING_the-payload-changes-at-utc-midnight-2026-08-30.md
#
# DECLARED AS NARROWLY AS THE VENDOR MARKER AND THE TRADEMARK STRIP, and for
# the same reason: an exemption is a hole, and "ignore anything that looks like
# a date" is the widest kind of hole there is. What is tolerated here is
# EXACTLY this: index.html, the literal text `testing <ISO date>`, the same
# number of occurrences on both sides, and EVERY OTHER BYTE IN THE FILE
# IDENTICAL. A stamp that appeared in a different file, appeared a different
# number of times, or arrived alongside any other change is NOT this and fails.
TESTING_STAMP = re.compile(r"testing \d{4}-\d{2}-\d{2}")


def stamp_only_difference(old_path, new_path):
    """(is_stamp_only, note). True when two files differ ONLY by the stamp.

    Compared as text with the stamps replaced by a fixed token, so the rest of
    the file is still held to byte equality. The occurrence count is checked
    separately: normalising first would happily accept a file that had gained a
    second stamp, which is a change and not this one.
    """
    try:
        old, new = text_of(old_path), text_of(new_path)
    except OSError as exc:
        return False, "could not be read: %s" % exc
    a, b = TESTING_STAMP.findall(old), TESTING_STAMP.findall(new)
    if not a or not b:
        return False, "no date stamp on one side (%d before, %d after)" % (len(a), len(b))
    if len(a) != len(b):
        return False, "the stamp count changed: %d -> %d" % (len(a), len(b))
    if len(set(a)) != 1 or len(set(b)) != 1:
        # A PAGE SHOWING TWO DIFFERENT DATES IS A DEFECT, NOT THIS DECLARATION.
        # The build substitutes both occurrences from one `_stamp`, so they
        # cannot legitimately disagree. Without this, a rebuild that updated
        # the <title> and not the <h1> would be waved through as "only the
        # stamp moved" - which is true, and is also a page telling a viewer two
        # different things about which build they are looking at.
        return False, ("the stamps within one file disagree: %s / %s"
                       % (sorted(set(a)), sorted(set(b))))
    if a == b:
        return False, "the stamps are identical, so they are not the difference"
    if TESTING_STAMP.sub("<STAMP>", old) != TESTING_STAMP.sub("<STAMP>", new):
        return False, "the file changed somewhere other than the stamp"
    return True, "%s -> %s, %d occurrence(s), every other byte identical" % (
        a[0], b[0], len(a))


RESTORE_DIR = os.path.join(ROOT, "_to_delete", "deploy_drift_restore")


def _tag(path):
    """A flat filename that still says which directory the copy came from."""
    return "%s__%s" % (os.path.basename(os.path.dirname(path)),
                       os.path.basename(path))


def watched_files():
    """Every path the rebuild can write, DISCOVERED rather than listed.

    Naming them is the fragile half. build_deploy.py writes four generated
    files into _src today - loadout_model, loadout_marker, loadout_eng and
    craft_data - plus its receipt; a fifth added tomorrow would be outside a
    hand-written list and would slip through the restore in silence, which is
    the whole failure mode this exists against.

    The asset directories are excluded deliberately. models/ is 445 MB and is
    an INPUT - the build globs it to decide which ships have a 3D view - so
    hashing it every run would cost more than the rest of this file put
    together. The withdrawal path in the build can still MOVE an asset out of
    _deploy; section 2 counts the payload and would show it, and this says so
    rather than implying the assets are covered here.
    """
    found = []
    for base in (DEPLOY, SRC):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            p = os.path.join(base, name)
            if os.path.isfile(p):
                found.append(p)
    return found


PENDING = os.path.join(RESTORE_DIR, "restore_pending.json")


def _write_pending(keep):
    """Record that a rebuild is about to happen and has not been undone yet.

    THE RESTORE IS EXCEPTION-SAFE AND WAS NEVER KILL-SAFE, and on 2026-08-29 I
    described it as though it were both. A `finally` runs for an exception; it
    does NOT run when the process is killed. A sweep stopped between the rebuild
    and the restore therefore leaves the rebuilt payload in place, silently -
    which is the exact damage this control was changed to stop causing.

    It happened the same morning: a sweep was killed mid-run and
    testing/_deploy/loadout_marker.gen.js went from ef9be07 to 2536dbd with
    nobody having asked for a build.

    Prevention is not available - no process can guarantee to run code after it
    is killed. So rule 14's other half applies: MAKE IT LOUD AND IMMEDIATE. This
    file is written before the rebuild and cleared after the restore, so the
    next run finds it and says what happened rather than inheriting it quietly.
    """
    rec = {"written_at": time.strftime("%Y-%m-%d %H:%M:%S"),
           "files": {p: [os.path.basename(c), h, m]
                     for p, (c, h, m) in keep.items()}}
    with open(PENDING, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, indent=1))


def _clear_pending():
    """Move the marker aside rather than delete it (rule 1)."""
    if os.path.exists(PENDING):
        os.replace(PENDING, PENDING + ".done")


def recover_interrupted():
    """A previous run was killed between its rebuild and its restore.

    Returns a list of what it put back. Empty list means there was nothing to
    recover, which is the normal case. A `refused` key means the journal was not
    written on this machine and NOTHING was touched.

    IT REFUSES A JOURNAL THAT IS NOT THIS CHECKOUT'S, AND THAT IS THE WHOLE
    POINT OF THE CHECK BELOW.

    On 2026-09-05 a journal written on a Cowork VM was sitting in this repo,
    listing about eighty absolute paths under
    `/sessions/rcw-.../mnt/citizen-compass/`. This function runs FIRST, before
    any assertion, and copies each preserved file back over its target. On
    Windows those paths did not resolve, so it raised FileNotFoundError and
    stopped.

    THE CRASH WAS THE ONLY THING THAT SAVED IT. Had the paths resolved - a
    checkout at a matching location, a mounted share, a rerun on the machine
    that wrote it - this would have silently overwritten eighty source and
    deploy files, including ones two sessions had edited that day, before
    printing a single line.

    "Safe by accident" is not safe. A recovery that acts on absolute paths from
    a file it did not write must check whose paths they are.
    """
    if not os.path.exists(PENDING):
        return None
    with open(PENDING, encoding="utf-8") as fh:
        rec = json.load(fh)

    here = os.path.abspath(ROOT)
    foreign = [p for p in sorted(rec.get("files", {}))
               if os.path.abspath(p) != here
               and not os.path.abspath(p).startswith(here + os.sep)]
    if foreign:
        # NOTHING IS TOUCHED AND THE MARKER IS LEFT ALONE. The journal may still
        # be the live recovery record of the machine that wrote it, and clearing
        # it here would strand that restore. It is reported and left.
        return {"at": rec.get("written_at"), "restored": [],
                "refused": foreign, "root": here,
                "total": len(rec.get("files", {}))}

    put_back = []
    for path, (copy_name, want_hash, want_mtime) in sorted(rec["files"].items()):
        copy_path = os.path.join(RESTORE_DIR, copy_name)
        if not os.path.exists(copy_path):
            put_back.append("%s - NO COPY, cannot recover"
                            % os.path.relpath(path, ROOT))
            continue
        if os.path.exists(path) and sha(path) == want_hash                 and os.stat(path).st_mtime_ns == want_mtime:
            continue
        shutil.copy2(copy_path, path)
        os.utime(path, ns=(want_mtime, want_mtime))
        put_back.append(os.path.relpath(path, ROOT))
    _clear_pending()
    return {"at": rec.get("written_at"), "restored": put_back}


def snapshot(paths):
    """Copy the current bytes aside so the rebuild can be undone.

    The copies go to ONE fixed directory under _to_delete/ rather than a
    timestamped one. This control runs on every scheduled sweep, and a
    per-run copy of ~17 MB would be gigabytes a month of something nobody
    reads. Nothing is deleted - each run writes over its own previous copy,
    and anything that turns out to be REAL drift is preserved separately,
    where it costs nothing because it is normally empty.
    """
    os.makedirs(RESTORE_DIR, exist_ok=True)
    keep = {}
    for p in paths:
        dst = os.path.join(RESTORE_DIR, _tag(p))
        shutil.copy2(p, dst)
        keep[p] = (dst, sha(p), os.stat(p).st_mtime_ns)
    return keep


def restore(keep, evidence_dir):
    """Put every file the rebuild moved back, and preserve BOTH versions of
    anything that really moved.

    Returns the paths the rebuild changed - which is the drift finding itself,
    reported by section 4 rather than swallowed here.

    copy2 RATHER THAN copyfile, AND THAT IS NOT A DETAIL. Restoring the bytes
    while leaving a fresh mtime behind would put this control straight back in
    the business of moving things other things watch: the point-drift detection
    that came out of Q13 reads mtimes to spot a write by a session that does not
    own the path, and "the bytes are the same" is not what it is looking at. A
    file this control put back must look untouched to a reader as well as to a
    hash.
    """
    moved = []
    for p, (copy_path, before_hash, before_mtime) in sorted(keep.items()):
        if not os.path.exists(p):
            shutil.copy2(copy_path, p)
            moved.append(os.path.relpath(p, ROOT) + " (the rebuild removed it)")
            continue
        if sha(p) == before_hash:
            # THE QUIET HALF, AND IT IS THE LARGER ONE. The build rewrites
            # every page and generated file whether or not the content moved,
            # so about twenty-five of these come back byte-identical with a
            # FRESH MTIME. Bytes restored and a new timestamp left behind is
            # still a write as far as anything reading mtimes is concerned -
            # and this control is not entitled to be one. Put the clock back.
            if os.stat(p).st_mtime_ns != before_mtime:
                os.utime(p, ns=(before_mtime, before_mtime))
            continue
        os.makedirs(evidence_dir, exist_ok=True)
        shutil.copy2(p, os.path.join(evidence_dir, "rebuilt__" + _tag(p)))
        shutil.copyfile(copy_path, os.path.join(evidence_dir, "before__" + _tag(p)))
        shutil.copy2(copy_path, p)
        rel = os.path.relpath(p, ROOT)
        if os.path.basename(p) == ".last_build.json":
            # THE RECEIPT MOVES ON EVERY SINGLE RUN, BY CONSTRUCTION. The
            # rebuild writes one and the restore puts the old one back, so it
            # would head this list forever and train the reader to skip the
            # line the real findings appear on.
            rel += "  (the build receipt - expected, it moves every run)"
        moved.append(rel)
    return moved


def park_created(before_paths, evidence_dir):
    """A file the rebuild CREATED is moved aside, never deleted (rule 1).

    Restoring only what existed before would leave a new file behind, and the
    next control would read a directory this one had added to.
    """
    parked = []
    for p in watched_files():
        if p in before_paths:
            continue
        os.makedirs(evidence_dir, exist_ok=True)
        shutil.move(p, os.path.join(evidence_dir, "created__" + _tag(p)))
        parked.append(os.path.relpath(p, ROOT))
    return parked


def still_moved(keep):
    """The assertion that makes the restore a guard rather than a good
    intention: every watched file, re-hashed AFTER the restore, against what
    it was before the rebuild ran.

    MTIME IS PART OF THE ASSERTION, not a nicety. Hashes alone reported this
    control clean while it was still bumping the timestamp on twenty-five
    files it had "restored", which is exactly the kind of pass that looks like
    proof and is not."""
    bad = []
    for p, (_, before_hash, before_mtime) in sorted(keep.items()):
        rel = os.path.relpath(p, ROOT)
        if not os.path.exists(p):
            bad.append(rel + " (missing)")
        elif sha(p) != before_hash:
            bad.append(rel)
        elif os.stat(p).st_mtime_ns != before_mtime:
            bad.append(rel + " (mtime)")
    return bad


def main():
    print("\n1. THE BUILD'S OWN LIST OF WHAT IT COPIES")
    pages = build_pages()
    if not pages:
        print("NOT PERFORMED: could not read PAGES out of %s, so there is no "
              "list of what _deploy should contain. Reported as not performed, "
              "never as passed." % os.path.relpath(PAGES_SRC, ROOT))
        # NOT RUN (exit 2), not FAIL: this could not look, it did not find a
        # defect. run_all_controls.py:381. Still red, still gates the deploy.
        return 2
    check("PAGES read from deploy_pages.py without running the build "
          "(%d entries)" % len(pages), len(pages) > 5)
    check("and every source it names exists in _src",
          all(os.path.exists(os.path.join(SRC, s)) for s, _ in pages))

    print("\n2. EVERY FILE IN _deploy HAS A PRODUCER")
    # Not the same question as check_deploy_clean's "is it allowed" - this asks
    # whether anything in there is something the build would not have put there.
    assembled = assembled_files()
    if assembled is None:
        print("     NOT PERFORMED: ASSEMBLED could not be read out of "
              "deploy_pages.py, so what\n     the build assembles rather than "
              "copies is unknown. Reported, not assumed.")
        return 2
    produced = assembled | {out for _, out in pages}
    strays, dirs = [], []
    for name in sorted(os.listdir(DEPLOY)):
        full = os.path.join(DEPLOY, name)
        if os.path.isdir(full):
            dirs.append(name)
        elif name not in produced:
            strays.append(name)
    check("no file in _deploy is unaccounted for"
          + (" (found %s)" % ", ".join(strays) if strays else ""), not strays)

    # THE TWO FILES Q54 ADDED ARE COVERED, NOT JUST PERMITTED.
    #
    # Being on the ASSEMBLED list only stops them being called strays. Nothing
    # above this would notice classic.html drifting away from the page it is
    # supposed to BE, or the front-door rule losing the one property that makes
    # it serve rather than redirect - and both would look completely normal.
    _front = front_door_page()
    _classic = os.path.join(DEPLOY, "classic.html")
    _index = os.path.join(DEPLOY, "index.html")
    if "classic.html" in assembled and os.path.exists(_classic):
        _same = (os.path.exists(_index)
                 and text_of(_classic) == text_of(_index))
        check("classic.html is the old front page byte for byte - it is "
              "index.html under an address of its own"
              + ("" if _same else "\n         classic.html and index.html "
                                  "DIFFER, so /classic is serving something "
                                  "other than the page it stands in for"),
              _same)
    _red = os.path.join(DEPLOY, "_redirects")
    if "_redirects" in assembled and os.path.exists(_red):
        _txt = text_of(_red)
        _rules = [l.strip() for l in _txt.splitlines()
                  if l.strip() and not l.strip().startswith("#")]
        if _front is None:
            print("     NOT PERFORMED for the front-door rule: "
                  "FRONT_DOOR_PAGE could not be read.")
        else:
            _want = "/ /%s 200" % _front[:-len(".html")]
            _why = ""
            if _rules != [_want]:
                _why = ("\n         _redirects says %r; it must be exactly "
                        "[%r]. A .html on the destination makes Cloudflare "
                        "hand it back to html_handling, and the front door "
                        "silently stops SERVING the new page and starts "
                        "REDIRECTING to it - measured on a fixture "
                        "2026-09-11." % (_rules, _want))
            check("the front door rule serves %s at / with a 200%s"
                  % (_front, _why), _rules == [_want])
    check("and the only directories are the asset payloads (%s)"
          % ", ".join(sorted(dirs)), set(dirs) <= set(ASSET_DIRS))

    counts = {}
    for d in ASSET_DIRS:
        p = os.path.join(DEPLOY, d)
        counts[d] = sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 0
    print("     asset payload, STATED AS UNPROVEN: %s"
          % ", ".join("%s %d files" % (d, counts[d]) for d in ASSET_DIRS))
    print("     These have no generator. models/ is even a build INPUT - the "
          "build globs it\n     to decide which ships have a 3D view. Nothing "
          "here can prove where they\n     came from, and calling them checked "
          "would be a check that never looked.")

    print("\n3. THE COPIED FILES AGAINST _src, EVERY INJECTION DECLARED  "
          "(non-destructive)")
    ships = ship_content_pages()
    if ships is None:
        print("     _SHIP_CONTENT_PAGES could not be read out of "
              "build_deploy.py. Reported per file below rather than assumed.")
    front = front_door_page()
    if front is None:
        print("     NOT PERFORMED for the gate: FRONT_DOOR_PAGE could not be "
              "read out of deploy_pages.py, so which page should carry the "
              "password gate is unknown. Reported, never passed - a missing "
              "name here would otherwise read as 'no page is gated' and pass "
              "a payload whose gate had been stripped.")
    else:
        print("     front door: %s carries the password gate; every other "
              "copied page must not" % front)
    drifted = []
    for src_name, out_name in pages:
        drifted.extend(page_problems(src_name, out_name, ships, front))
    check("every copied file in _deploy is its _src source byte for byte, "
          "outside the injections declared above"
          + ("\n         " + "\n         ".join(drifted) if drifted else ""),
          not drifted)

    print("\n4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING  "
          "(non-destructive since 2026-08-29)")
    recovered = recover_interrupted()
    if recovered is not None and recovered.get("refused"):
        print("     A RESTORE JOURNAL IS PRESENT AND IT IS NOT THIS MACHINE'S "
              "(%s)." % recovered["at"])
        print("     %d of %d recorded paths are outside this checkout:"
              % (len(recovered["refused"]), recovered["total"]))
        for p in recovered["refused"][:5]:
            print("       " + p)
        if len(recovered["refused"]) > 5:
            print("       ... and %d more" % (len(recovered["refused"]) - 5))
        print("     this checkout: " + recovered["root"])
        print("")
        print("     NOTHING WAS RESTORED AND THE JOURNAL WAS LEFT IN PLACE.")
        print("     It may still be the live recovery record of the machine")
        print("     that wrote it; clearing it here would strand that restore.")
        print("     Recover on that machine, or move the marker aside by hand.")
    elif recovered is not None:
        print("     A PREVIOUS RUN WAS INTERRUPTED between its rebuild and its "
              "restore (%s)." % recovered["at"])
        if recovered["restored"]:
            print("     Put back now, before anything else is measured:")
            for r in recovered["restored"]:
                print("       " + r)
        else:
            print("     Nothing needed putting back - the tree already matched "
                  "the snapshot.")
    if recovered is not None and recovered.get("refused"):
        check("the restore journal present was written by THIS checkout",
              "%d of %d paths point somewhere else - refusing to restore"
              % (len(recovered["refused"]), recovered["total"]), False)
    check("no rebuild from a previous run was left sitting in _deploy"
          + ("" if not (recovered and recovered["restored"])
             else " (recovered %d file(s) - see above)"
                  % len(recovered["restored"])),
          not (recovered and recovered["restored"]))

    watched = watched_files()
    keep = snapshot(watched)
    _write_pending(keep)
    evidence = os.path.join(ROOT, "_to_delete",
                            "deploy_drift_%s" % time.strftime("%Y%m%d%H%M%S"))
    index_path = os.path.join(DEPLOY, "index.html")
    before = keep[index_path][1] if index_path in keep else None
    before_all = {out: keep[os.path.join(DEPLOY, out)][1]
                  for _, out in pages
                  if os.path.join(DEPLOY, out) in keep}
    print("     %d file(s) under _deploy and _src copied aside first, so the "
          "rebuild\n     can be undone. %s"
          % (len(watched), os.path.relpath(RESTORE_DIR, ROOT)))

    build_failed = None
    after = None
    moved_pages = []
    stamp_ok, stamp_why = False, None
    try:
        proc = subprocess.run([sys.executable, BUILD], capture_output=True,
                              text=True, cwd=ROOT)
        if proc.returncode != 0:
            build_failed = ((proc.stdout or "") + (proc.stderr or "")).strip()
        else:
            after = sha(index_path) if os.path.exists(index_path) else None
            # MEASURED HERE, INSIDE THE TRY, AND THAT IS NOT A STYLE CHOICE.
            # The finally below RESTORES index.html to the snapshot, so asking
            # this question afterwards compares the snapshot against itself and
            # gets "the stamps are identical" every time. The first version did
            # exactly that and reported a false red on a planted stamp - caught
            # because the plant was supposed to go green and did not.
            if before != after and index_path in keep:
                stamp_ok, stamp_why = stamp_only_difference(
                    keep[index_path][0], index_path)
            moved_pages = [out for out, h in before_all.items()
                           if not os.path.exists(os.path.join(DEPLOY, out))
                           or sha(os.path.join(DEPLOY, out)) != h]
    finally:
        # The restore is in a finally for the same reason section 5's is: a
        # rebuild that raised on its way through would otherwise leave a
        # half-built payload sitting in _deploy for the next thing to publish.
        parked = park_created(set(watched), evidence)
        rebuilt = restore(keep, evidence)
        leftover = still_moved(keep)
        if not leftover:
            _clear_pending()

    if build_failed is not None:
        print("NOT PERFORMED: the build failed, so the rebuild half could not "
              "run. This needs PostgreSQL and node.")
        for line in build_failed.splitlines()[-8:]:
            print("       " + line)
        print("     _deploy and _src were put back regardless - a failed "
              "rebuild does not\n     get to leave its output behind "
              "either.")
        check("and _deploy and _src are byte for byte as this control found "
              "them, even though the build failed"
              + (" (still moved: %s)" % ", ".join(leftover) if leftover else ""),
              not leftover)
        return 1

    stamp_note = None
    if before != after and stamp_why is not None:
        # The one tolerated difference, and it has to be PROVEN to be that
        # difference rather than assumed from the fact that a rebuild happened.
        if stamp_ok:
            stamp_note = stamp_why
            after = before          # the stamp is declared; nothing else moved
        else:
            print("     the rebuild changed index.html and it is NOT the "
                  "declared stamp: %s" % stamp_why)
    check("index.html is byte-identical after a rebuild, outside the declared "
          "date stamp - it is what the build produces, not something anybody "
          "edited", before == after,
          )
    if stamp_note:
        print("     DECLARED: the testing date stamp moved (%s)." % stamp_note)
        print("     build_deploy.py:741 stamps the UTC date, so a rebuild "
              "across 00:00 UTC is not byte-reproducible. Tolerated here "
              "for index.html and the stamp text alone - see "
              "docs/FINDING_the-payload-changes-at-utc-midnight-2026-08-30.md")
    check("and so is every copied file"
          + (" (moved: %s)" % ", ".join(moved_pages) if moved_pages else ""),
          not moved_pages)

    # THE GUARD, PROVEN BY BEHAVIOUR RATHER THAN BY READING THE CODE ABOVE.
    #
    # Every other assertion in section 4 would still pass if the restore
    # silently did nothing - they are all measured BEFORE it runs. This is the
    # one that says the sweep is not being taken during a write, and it is the
    # whole point of the 2026-08-29 change. Rule 12: a safety mechanism nobody
    # has watched work is an untested one.
    check("and _deploy and _src are byte for byte as this control found them - "
          "the rebuild's output was reverted, so nothing downstream is "
          "measuring a moving payload"
          + (" (still moved: %s)" % ", ".join(leftover) if leftover else ""),
          not leftover)
    if rebuilt:
        print("     THE REBUILD CHANGED %d FILE(S), WHICH IS THE FINDING ABOVE "
              "AND NOT A REPAIR:\n       %s"
              % (len(rebuilt), "\n       ".join(rebuilt)))
        print("     both versions preserved under %s - the payload is left "
              "exactly as found."
              % os.path.relpath(evidence, ROOT))
    if parked:
        print("     the rebuild CREATED %s; moved aside, never deleted "
              "(rule 1)" % ", ".join(parked))

    print("\n5. THE CHECK CAN FAIL - A HAND EDIT IS PLANTED AND FOUND")
    # Exactly the defect this item names: something typed into _deploy that
    # exists nowhere in _src. A drift check that has only ever passed has not
    # been shown to work.
    victim_src, victim_out = next(
        (s, o) for s, o in pages
        if o.endswith(".html") and o not in SEAM_FILES)
    victim = os.path.join(DEPLOY, victim_out)
    original = read_bytes(victim)
    original_mtime = os.stat(victim).st_mtime_ns
    original_text = text_of(victim)
    keep = os.path.join(ROOT, "_to_delete",
                        "deploy_drift_plant_%s" % time.strftime("%Y%m%d%H%M%S"))
    os.makedirs(keep, exist_ok=True)

    def plant(tag, text):
        """Corrupt the deployed file, run THE REAL comparison over it, preserve
        the evidence (hard rule 1 - nothing here deletes), restore the original.

        The restore is in a finally, because a plant that raised on its way
        through the comparator would otherwise leave a corrupted page sitting
        in _deploy for the next thing to publish.
        """
        try:
            with open(victim, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)
            changed = read_bytes(victim) != original
            found = page_problems(victim_src, victim_out, ships,
                                  front_door_page())
            shutil.copyfile(victim, os.path.join(keep, "%s__%s" % (tag, victim_out)))
            return changed, found
        finally:
            with open(victim, "wb") as fh:
                fh.write(original)
            # The clock goes back with the bytes, for the same reason
            # section 4's restore does it: a page put back with a fresh
            # timestamp still reads as a write to anything watching mtimes,
            # and this control is not a writer of _deploy. Section 4's
            # manifest caught this one - the bytes matched and the mtime
            # did not.
            os.utime(victim, ns=(original_mtime, original_mtime))

    changed, found = plant(
        "hand_edit",
        text_of(os.path.join(SRC, victim_src))
        + "\n<!-- typed straight into _deploy, by hand -->\n")
    check("the plant really did change the file - otherwise every assertion "
          "below it is checking nothing", changed)
    check("a hand edit in _deploy/%s is REPORTED, not passed over"
          % victim_out, found)

    # THE TWO PLANTS THE DECLARED GAP MADE NECESSARY.
    #
    # Section 3 no longer compares the appended attribution block byte for byte
    # against _src, because it does not exist in _src. That is a region the
    # check tolerates - so it is a region that has to be proven not to be a
    # hole, in both directions: something added after it, and something changed
    # inside it.
    changed, found = plant(
        "after_the_strip",
        original_text + "<!-- appended past the trademark strip -->\n")
    check("text appended AFTER the trademark strip is REPORTED - the tolerated "
          "region is not an open end", changed and found)

    if ATTR_IMPORT_ERROR:
        check("the trademark line's own wording, edited in _deploy only, is "
              "REPORTED - " + ATTR_IMPORT_ERROR, False)
    else:
        reworded = _attr.TRADEMARK_BAR.replace("registered trademarks",
                                               "trademarks", 1)
        changed, found = plant("reworded_strip",
                               original_text.replace(_attr.TRADEMARK_BAR,
                                                     reworded, 1))
        check("and so is the trademark line itself, reworded in _deploy only - "
              "hard rule 8's own text, changed where no source diff would ever "
              "show it", changed and found)

    check("and the file was restored byte for byte after every plant, with "
          "its mtime",
          read_bytes(victim) == original
          and os.stat(victim).st_mtime_ns == original_mtime)
    print("     the planted copies were moved aside to %s, never deleted"
          % os.path.relpath(keep, ROOT))

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
