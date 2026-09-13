#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_share_card.py - the loadout page's built share card says exactly what
Design locked, points at an image that is really there, and leaks no marker.

RULE16: INDEPENDENT - the expected strings are Design's locked copy, restated
here from `2026-09-13_memo_design_discord-share-card-copy-shape-a-owner-said-build.md`,
and the two origins are LIVE.md's; the subject is the page build_deploy.py
wrote. The patch VALUE is not checked (it reaches the page from the snapshot
manifest and would reach this file by the same path) - only its shape is.

Shape A, Owner's order of 2026-09-13: one set of tags, the same for every build,
no ship name, one static image. A share card is only seen by a crawler, so
nothing on the page would ever show that it had gone wrong - a lost marker, a
relative image URL or a missing PNG produces a blank Discord embed and no error.

WHAT IT REFUSES
  a locked tag missing, or its value not exactly Design's string
  a description suffix that is not ` · Patch <major>.<minor>` or nothing
  og:url / og:image / twitter:image not absolute on ONE of the two origins
  the image not in the payload, or not a 1200x630 PNG
  a __CC_ORIGIN__ or __CC_PATCH__ marker left in the page

NOT PERFORMED, never passed: no built loadout.html to read.

Rule 15: every text open states encoding="utf-8".

Usage:
    python checks/_verify_share_card.py
    python checks/_verify_share_card.py --self-test
"""
import html
import io
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEPLOY = os.path.join(ROOT, "testing", "_deploy")

TITLE = "Citizen Compass — ship loadout"
DESC = ("Fit a ship, see what changes, know where to buy — before you fly. "
        "Shared builds open ready to tweak.")
ORIGINS = ("https://citizencompasstesting.citizencompass-contact.workers.dev",
           "https://citizencompass.netlify.app")
EXACT = {
    ("property", "og:type"): "website",
    ("property", "og:site_name"): "Citizen Compass",
    ("property", "og:title"): TITLE,
    ("name", "twitter:card"): "summary_large_image",
    ("name", "twitter:title"): TITLE,
}
DESCRIBED = [("property", "og:description"), ("name", "twitter:description")]
URLS = [("property", "og:url"), ("property", "og:image"), ("name", "twitter:image")]
RE_META = re.compile(r'<meta\s+(property|name)="([^"]+)"\s+content="([^"]*)"\s*/?>')
RE_SUFFIX = re.compile(r"^( · Patch \d+\.\d+)?$")


def tags(text):
    out = {}
    for kind, key, val in RE_META.findall(text):
        out.setdefault((kind, key), []).append(html.unescape(val))
    return out


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


def judge(deploy):
    page = os.path.join(deploy, "loadout.html")
    if not os.path.isfile(page):
        return None
    text = io.open(page, encoding="utf-8", errors="replace").read()
    t = tags(text)
    fails = []
    for marker in ("__CC_ORIGIN__", "__CC_PATCH__"):
        if marker in text:
            fails.append("MARKER LEFT - %s is still in the built page" % marker)
    for key, want in EXACT.items():
        got = t.get(key)
        if got != [want]:
            fails.append("%s=%s: want exactly %r, got %r" % (key[0], key[1], want, got))
    for key in DESCRIBED:
        got = t.get(key)
        if not got or len(got) != 1 or not got[0].startswith(DESC) \
                or not RE_SUFFIX.match(got[0][len(DESC):]):
            fails.append("%s=%s: want Design's description plus an optional "
                         "' · Patch N.N', got %r" % (key[0], key[1], got))
    urls = {}
    for key in URLS:
        got = t.get(key)
        if not got or len(got) != 1:
            fails.append("%s=%s: missing or repeated, got %r" % (key[0], key[1], got))
            continue
        origin = next((o for o in ORIGINS if got[0].startswith(o + "/")), None)
        if origin is None:
            fails.append("%s=%s: %r is not absolute on %s" % (key[0], key[1], got[0],
                                                            " or ".join(ORIGINS)))
        urls[key[1]] = (origin, got[0])
    if len({o for o, _u in urls.values() if o}) > 1:
        fails.append("MIXED ORIGINS - %r" % sorted(u for _o, u in urls.values()))
    if "og:url" in urls and urls["og:url"][0] and urls["og:url"][1] != urls["og:url"][0] + "/loadout":
        fails.append("og:url is %r; the served canonical path is /loadout" % urls["og:url"][1])
    for key in ("og:image", "twitter:image"):
        if key in urls and urls[key][0]:
            rel = urls[key][1][len(urls[key][0]) + 1:]
            img = os.path.join(deploy, *rel.split("/"))
            size = png_size(img) if os.path.isfile(img) else None
            if size != (1200, 630):
                fails.append("%s: %s is %s, not a 1200x630 PNG in the payload"
                             % (key, rel, repr(size) if os.path.isfile(img) else "MISSING"))
    return fails


def self_test():
    import tempfile
    import shutil
    good_head = (
        '<title>x</title>\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="Citizen Compass">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s · Patch 4.10">\n'
        '<meta property="og:url" content="%s/loadout">\n'
        '<meta property="og:image" content="%s/og-loadout.png">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<meta name="twitter:title" content="%s">\n'
        '<meta name="twitter:description" content="%s">\n'
        '<meta name="twitter:image" content="%s/og-loadout.png">\n'
        % (TITLE, DESC, ORIGINS[0], ORIGINS[0], TITLE, DESC, ORIGINS[0]))
    png = (b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 1200, 630)
           + b"\x08\x02\x00\x00\x00")
    cases = [
        ("clean page, patch on one description only", good_head, png, False),
        ("a marker left", good_head.replace("4.10", "4.10__CC_PATCH__"), png, True),
        ("a marker left outside every checked tag", good_head + "<p>__CC_ORIGIN__</p>\n", png, True),
        ("the title reworded", good_head.replace(TITLE, "Citizen Compass - ship loadout", 1), png, True),
        ("a ship name in the title", good_head.replace(TITLE, TITLE + ": Polaris", 1), png, True),
        ("the description suffix invented", good_head.replace("Patch 4.10", "Patch 4.x"), png, True),
        ("twitter:card dropped", good_head.replace('<meta name="twitter:card" content="summary_large_image">\n', ""), png, True),
        ("a relative image URL", good_head.replace(ORIGINS[0] + "/og-loadout.png", "/og-loadout.png", 1), png, True),
        ("mixed origins", good_head.replace(ORIGINS[0] + "/og-loadout.png", ORIGINS[1] + "/og-loadout.png", 1), png, True),
        ("og:url with .html", good_head.replace("/loadout\"", "/loadout.html\""), png, True),
        ("the image missing", good_head, None, True),
        ("the image the wrong size", good_head, png[:16] + struct.pack(">II", 800, 600) + png[24:], True),
    ]
    caught = 0
    for label, head, img, must_fail in cases:
        tmp = tempfile.mkdtemp(prefix="cc-share-card-")
        try:
            io.open(os.path.join(tmp, "loadout.html"), "w", encoding="utf-8",
                    newline="").write("<!doctype html>\n" + head + "<body></body>\n")
            if img is not None:
                with open(os.path.join(tmp, "og-loadout.png"), "wb") as fh:
                    fh.write(img)
            fails = judge(tmp)
            ok = bool(fails) == must_fail
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        caught += ok
        print("  %-7s %-44s %s" % ("caught" if ok else "MISSED", label,
                                   "must fail" if must_fail else "must pass"))
    tmp = tempfile.mkdtemp(prefix="cc-share-card-")
    try:
        np_ok = judge(tmp) is None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    caught += np_ok
    print("  %-7s %-44s %s" % ("caught" if np_ok else "MISSED", "no built page",
                               "must be NOT PERFORMED"))
    total = len(cases) + 1
    print("\n%d of %d cases landed." % (caught, total))
    if caught != total:
        print("SELF-TEST FAILED - this control must not be trusted.")
        return 3
    print("SELF-TEST PASSED. Exiting NON-ZERO on purpose: the suite requires a "
          "control's self-test to be rejected. This is the GOOD outcome.")
    return 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    fails = judge(DEPLOY)
    if fails is None:
        print("NOT PERFORMED - testing/_deploy/loadout.html is not built, so the "
              "share card was not read.")
        return 2
    if fails:
        print("share card: %d finding(s):" % len(fails))
        for f in fails:
            print("  - %s" % f)
        print("RED.")
        return 1
    print("PASS - the loadout page's share card is Design's locked copy, absolute "
          "on one origin, and its image is a 1200x630 PNG in the payload.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
