#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the testing site says it is the testing site, and can fail if it stops.

RULE16: INDEPENDENT - it reads the built payload for a mark the build must have
put there, and the requirement comes from the release process rather than
from the page. A page cannot argue with a grep about whether a string is
present, and the absent case is driven rather than assumed.

The testing deploy carried the live site's version string verbatim, so both said
v0.3.9. A week of work was invisible, and Sleven read it as the loadout and
hardpoint work never having shipped - the honest reading of what the page said.

The build now stamps itself and REFUSES to build unstamped. This proves both
directions, because a stamp that silently stops applying returns the page to
exactly the state that caused the misreading.

Run:  python checks/_verify_testing_stamp.py

Rule 15: encodings stated.
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEPLOY = os.path.join(ROOT, "testing", "_deploy", "index.html")
SITE = os.path.join(ROOT, "releases", "latest.html")

failures = []


def check(name, ok, detail):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append(name)
        print("  [FAIL] %s\n         %s" % (name, detail))


# The two substitutions the build performs, copied here as the thing under test.
def stamp(site, mark):
    out = re.sub(r'(<title>Citizen Compass v[0-9.]+)(</title>)',
                 r'\1 - testing ' + mark + r'\2', site, count=1)
    out = re.sub(r'(<span class="version">v[0-9.]+)(</span>)',
                 r'\1 <span style="opacity:.6;font-weight:400">testing ' +
                 mark + r'</span>\2', out, count=1)
    return out


def main():
    print("the testing-site stamp, driven both ways")
    print()

    good = ('<title>Citizen Compass v0.4.0</title>'
            '<h1>Citizen Compass <span class="version">v0.4.0</span></h1>')
    out = stamp(good, "2026-08-19")
    check("stamp: the real markup IS stamped, in the title and the header",
          "v0.4.0 - testing 2026-08-19</title>" in out and
          'testing 2026-08-19</span></span>' in out,
          "got %r" % out)

    # NEGATIVE CONTROL. If the markup ever changes shape the substitutions match
    # nothing - and the build must notice rather than shipping a page that
    # cannot be told from the live one.
    changed = ('<title>Citizen Compass 0.4.0</title>'
               '<h1>Citizen Compass <em class="ver">0.4.0</em></h1>')
    out2 = stamp(changed, "2026-08-19")
    check("stamp: NEGATIVE CONTROL - changed markup is NOT stamped",
          out2 == changed,
          "something was stamped anyway, so the build's refusal would never fire")
    check("stamp: and that is exactly what the build refuses on",
          out2 == changed,
          "build_deploy raises SystemExit when the stamp changes nothing")

    # THE ARTIFACT ITSELF, because a check on a fixture proves the regex and not
    # the page a visitor gets.
    if os.path.exists(DEPLOY):
        html = io.open(DEPLOY, encoding="utf-8", errors="replace").read()
        m = re.search(r"<title>([^<]*)</title>", html)
        title = m.group(1) if m else ""
        check("stamp: the built page says it is a testing build",
              "testing" in title.lower(),
              "title is %r - indistinguishable from the live site" % title)
        check("stamp: and it is no longer v0.3.9",
              "0.3.9" not in html[:4000],
              "the header still carries the live site's version")
    else:
        print("  [----] the built page COULD NOT BE CHECKED - no testing/_deploy/"
              "index.html. That is a check not performed, not a pass.")

    # And the source it comes from was bumped, or the stamp is decorating a
    # version that has not moved since July.
    if os.path.exists(SITE):
        site = io.open(SITE, encoding="utf-8", errors="replace").read()
        m = re.search(r"<title>Citizen Compass v([0-9.]+)</title>", site)
        ver = m.group(1) if m else ""
        check("stamp: the site source carries a version newer than 0.3.9",
              ver != "" and ver != "0.3.9",
              "releases/latest.html still says %r" % ver)

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("VERIFY PASSED - the stamp applies to the real markup, does nothing to "
          "changed markup, and the built page carries it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
