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

THE REBUILD IS DESTRUCTIVE, SO IT GOES LAST. Everything that can be checked
without one is checked first. If a hand edit exists, it is named before
anything overwrites it, and a copy is preserved under _to_delete/ (hard rule 1 -
nothing here deletes).

`--self-test` inverts every expectation and must exit 1.

Rule 15: every open states its encoding.
"""

import ast
import hashlib
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
INJECTION_MARKERS = (
    (ATTR_SENTINEL, "attribution"),
    (VENDOR_MARKER, "vendor"),
    (DISC_MARKER, "disclosure"),
)


def declared_transforms(s_text):
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
        if gap != text_of(DISC_CSS_PATH):
            return ("what was substituted is not _disc.css byte for byte - it "
                    "was edited in _deploy, or the build substituted something "
                    "else")
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


def page_problems(src_name, out_name, ship_pages):
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
    if out_name in SEAM_FILES:
        prefix, dev, dep = SEAM_FILES[out_name]
        s_lines = text_of(s_path).split("\n")
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
        if read_bytes(s_path) != read_bytes(d_path):
            return ["%s differs from _src/%s  [%s]"
                    % (out_name, src_name, owner_note(src_name))]
        return []
    # TRANSFORMED. Every injection the build makes is declared, and the source
    # text either side of every one of them must still be there, byte for byte,
    # anchored at BOTH ends of the file.
    s_text = text_of(s_path)
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
    segments, gap_names = declared_transforms(s_text)
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


def main():
    print("\n1. THE BUILD'S OWN LIST OF WHAT IT COPIES")
    pages = build_pages()
    if not pages:
        print("NOT PERFORMED: could not read PAGES out of %s, so there is no "
              "list of what _deploy should contain. Reported as not performed, "
              "never as passed." % os.path.relpath(PAGES_SRC, ROOT))
        return 1
    check("PAGES read from deploy_pages.py without running the build "
          "(%d entries)" % len(pages), len(pages) > 5)
    check("and every source it names exists in _src",
          all(os.path.exists(os.path.join(SRC, s)) for s, _ in pages))

    print("\n2. EVERY FILE IN _deploy HAS A PRODUCER")
    # Not the same question as check_deploy_clean's "is it allowed" - this asks
    # whether anything in there is something the build would not have put there.
    produced = {"index.html"} | {out for _, out in pages}
    strays, dirs = [], []
    for name in sorted(os.listdir(DEPLOY)):
        full = os.path.join(DEPLOY, name)
        if os.path.isdir(full):
            dirs.append(name)
        elif name not in produced:
            strays.append(name)
    check("no file in _deploy is unaccounted for"
          + (" (found %s)" % ", ".join(strays) if strays else ""), not strays)
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
    drifted = []
    for src_name, out_name in pages:
        drifted.extend(page_problems(src_name, out_name, ships))
    check("every copied file in _deploy is its _src source byte for byte, "
          "outside the injections declared above"
          + ("\n         " + "\n         ".join(drifted) if drifted else ""),
          not drifted)

    print("\n4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING")
    before = sha(os.path.join(DEPLOY, "index.html"))
    before_all = {out: sha(os.path.join(DEPLOY, out))
                  for _, out in pages if os.path.exists(os.path.join(DEPLOY, out))}
    proc = subprocess.run([sys.executable, BUILD], capture_output=True,
                          text=True, cwd=ROOT)
    if proc.returncode != 0:
        print("NOT PERFORMED: the build failed, so the rebuild half could not "
              "run. This needs PostgreSQL and node.")
        for line in ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-8:]:
            print("       " + line)
        return 1
    after = sha(os.path.join(DEPLOY, "index.html"))
    check("index.html is byte-identical after a rebuild - it is what the build "
          "produces, not something anybody edited", before == after,
          )
    moved = [out for out, h in before_all.items()
             if sha(os.path.join(DEPLOY, out)) != h]
    check("and so is every copied file"
          + (" (moved: %s)" % ", ".join(moved) if moved else ""), not moved)

    print("\n5. THE CHECK CAN FAIL - A HAND EDIT IS PLANTED AND FOUND")
    # Exactly the defect this item names: something typed into _deploy that
    # exists nowhere in _src. A drift check that has only ever passed has not
    # been shown to work.
    victim_src, victim_out = next(
        (s, o) for s, o in pages
        if o.endswith(".html") and o not in SEAM_FILES)
    victim = os.path.join(DEPLOY, victim_out)
    original = read_bytes(victim)
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
            found = page_problems(victim_src, victim_out, ships)
            shutil.copyfile(victim, os.path.join(keep, "%s__%s" % (tag, victim_out)))
            return changed, found
        finally:
            with open(victim, "wb") as fh:
                fh.write(original)

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

    check("and the file was restored byte for byte after every plant",
          read_bytes(victim) == original)
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
