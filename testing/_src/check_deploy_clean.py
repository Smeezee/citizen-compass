"""Refuse to ship anything in testing/_deploy that is not a known asset.

WHY THIS EXISTS
---------------
Everything in testing/_deploy is uploaded and served publicly. On 2026-08-06 a
failed `wrangler pages deploy` run, executed from inside _deploy, created a
`.wrangler/cache/` folder there. The next deploy published it:

    /.wrangler/cache/wrangler-account.json   -> account id + account name
    /.wrangler/cache/pages.json              -> account id

No tokens, and the account name is already implied by the workers.dev
subdomain, so the damage was small. The mechanism is not small: _deploy is a
directory on disk that any tool, any half-finished command, any editor swap
file can write into, and whatever lands there goes to the internet on the next
deploy without anyone looking at it.

So the allowed contents are declared, and anything else is a hard failure.

FAILS CLOSED, AND BY WHITELIST
------------------------------
A denylist of "things we don't want published" would stop `.wrangler` and
silently permit the next surprise. This lists what MAY be there; everything
else is refused by default. Dot-entries are called out separately because they
are the ones that are invisible in a file browser - which is precisely why the
last one went unnoticed.

Run standalone before deploying:

    python testing/_src/check_deploy_clean.py

Exit 0 = clean and safe to deploy. Exit 1 = something unexpected is present.
Exit 2 = could not check (never reported as clean).
"""

import os
import sys

# The only files permitted at the top level of _deploy. Keep this in step with
# PAGES in build_deploy.py - build_deploy passes its own list in, so the two
# cannot drift when the check runs as part of a build.
DEFAULT_ALLOWED_FILES = {
    "index.html",
    "keybinds.html",
    "loadout.html",
    "find.html",
    "kb_modes.gen.js",
    # Kept in step with PAGES in build_deploy.py BY HAND - this set is only
    # used when the guard runs standalone, and it does not derive from PAGES.
    # Letting the two drift produces a standalone "unexpected file" failure
    # that flatly contradicts a clean build, which is worse than either alone.
    "sc_export.js",
    "kb_actions.gen.js",
    "holo.html",
    # /loadout's real ship data, added 2026-08-13 with build_loadout_data.py.
    "loadout_data.gen.js",
    # /find's price data, added 2026-08-20 with build_find_data.py. The page
    # reads this instead of calling an API, so without it /find has nothing to
    # search - and this guard, running standalone before a deploy, is the last
    # thing that would notice.
    "find_data.gen.js",
    # Its published sha256, added 2026-08-20 (R7/H5). Without it the page
    # refuses to offer the download at all, rather than offering a file with
    # no way to check it.
    "find_checksum.gen.js",
    # The ship page's hardpoint data, added 2026-08-21 with
    # build_hardpoint_data.py (I1). index.html loads it with a <script src>;
    # without it the Loadout panel falls back to the API, which is the exact
    # outage this file exists to end.
    "hardpoint_data.gen.js",
    "holo_data.gen.js",
    "stick-test.html",
    # The public collector download page, added 2026-08-15 with
    # download.src.html. IT WAS ALREADY LIVE and this list had not been told -
    # /download returns 200 on the testing site while this guard called the file
    # unexpected. Exactly the drift the note above warns about: the standalone
    # guard flatly contradicting a clean build, which is worse than either
    # alone. Recorded here rather than fixed silently, because the next person
    # to add a page will hit it the same way.
    "download.html",
}

# The only directories permitted. Their CONTENTS are asset payloads (347 MB of
# ship models and images) and are not enumerated - but they are still checked
# for dot-entries, because that is how the last leak arrived.
# "fonts" added 2026-08-09, DELIBERATELY, for the Star Citizen typefaces on
# the keybind page. Served as files rather than base64-inlined, matching how
# images/ and models/ are already served - inlining three families would add
# six figures of base64 to keybinds.html on every build for something that
# never changes between builds. A new top-level allowed directory is exactly
# the kind of change a future session needs to know was intentional.
DEFAULT_ALLOWED_DIRS = {"images", "models", "fonts"}


def check_deploy_dir(out_dir, allowed_files=None, allowed_dirs=None):
    """Return a list of problem strings. Empty list means clean."""
    allowed_files = set(allowed_files or DEFAULT_ALLOWED_FILES)
    allowed_dirs = set(allowed_dirs or DEFAULT_ALLOWED_DIRS)

    if not os.path.isdir(out_dir):
        return ["deploy directory does not exist: %s" % out_dir]

    problems = []

    for name in sorted(os.listdir(out_dir)):
        full = os.path.join(out_dir, name)
        if os.path.isdir(full):
            if name.startswith("."):
                problems.append(
                    "hidden directory would be PUBLISHED: %s/  "
                    "(this is how .wrangler/ leaked on 2026-08-06)" % name)
            elif name not in allowed_dirs:
                problems.append(
                    "unexpected directory would be PUBLISHED: %s/  "
                    "(allowed: %s)" % (name, ", ".join(sorted(allowed_dirs))))
        else:
            if name.startswith("."):
                problems.append("hidden file would be PUBLISHED: %s" % name)
            elif name not in allowed_files:
                problems.append(
                    "unexpected file would be PUBLISHED: %s  (allowed: %s)"
                    % (name, ", ".join(sorted(allowed_files))))

    # Dot-entries nested inside the permitted asset directories. Their normal
    # contents are not enumerated - there are tens of thousands of asset files
    # and listing them would make this check unmaintainable and therefore
    # eventually switched off - but a dot-entry in there is never legitimate.
    for d in sorted(allowed_dirs):
        root_dir = os.path.join(out_dir, d)
        if not os.path.isdir(root_dir):
            continue
        for root, dirs, files in os.walk(root_dir):
            for nm in list(dirs):
                if nm.startswith("."):
                    rel = os.path.relpath(os.path.join(root, nm), out_dir)
                    problems.append("hidden directory would be PUBLISHED: %s/" % rel)
                    dirs.remove(nm)  # do not descend; one report is enough
            for nm in files:
                if nm.startswith("."):
                    rel = os.path.relpath(os.path.join(root, nm), out_dir)
                    problems.append("hidden file would be PUBLISHED: %s" % rel)

    return problems


def enforce(out_dir, allowed_files=None, allowed_dirs=None):
    """Print the verdict. Returns the number of problems (0 = clean)."""
    problems = check_deploy_dir(out_dir, allowed_files, allowed_dirs)
    if not problems:
        print("deploy guard: _deploy contains only known assets - safe to deploy")
        return 0

    print("")
    print("DEPLOY REFUSED - _deploy contains %d thing(s) that would be published:"
          % len(problems))
    for p in problems:
        print("   - %s" % p)
    print("")
    print("Everything in testing/_deploy is served publicly. Move the offending")
    print("entries out (never delete - see hard rule 1), or add them to the")
    print("allow-list in check_deploy_clean.py if they genuinely belong.")
    return len(problems)


def _selftest():
    """Negative control: the guard must FAIL on a planted file.

    A guard that has only ever passed has not been shown to work, and this one
    protects a public endpoint.
    """
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="deployguard-")
    ok = True
    try:
        # A clean, legitimate tree.
        for f in ("index.html", "keybinds.html", "kb_modes.gen.js"):
            with open(os.path.join(tmp, f), "w", encoding="utf-8") as fh:
                fh.write("x")
        os.makedirs(os.path.join(tmp, "images"))
        os.makedirs(os.path.join(tmp, "models", "Liberator"))
        with open(os.path.join(tmp, "models", "Liberator", "model.glb"),
                  "w", encoding="utf-8") as fh:
            fh.write("x")

        clean = check_deploy_dir(tmp)
        print("  [%s] clean tree passes (%d problems)"
              % ("ok  " if not clean else "FAIL", len(clean)))
        ok = ok and not clean

        # 1. the exact defect that happened: a hidden directory
        os.makedirs(os.path.join(tmp, ".wrangler", "cache"))
        with open(os.path.join(tmp, ".wrangler", "cache", "wrangler-account.json"),
                  "w", encoding="utf-8") as fh:
            fh.write("{}")
        got = check_deploy_dir(tmp)
        hit = any(".wrangler" in p for p in got)
        print("  [%s] hidden .wrangler/ directory is REFUSED" % ("ok  " if hit else "FAIL"))
        ok = ok and hit
        shutil.rmtree(os.path.join(tmp, ".wrangler"))

        # 2. an unexpected ordinary file
        with open(os.path.join(tmp, "notes.txt"), "w", encoding="utf-8") as fh:
            fh.write("secret plans")
        got = check_deploy_dir(tmp)
        hit = any("notes.txt" in p for p in got)
        print("  [%s] unexpected file notes.txt is REFUSED" % ("ok  " if hit else "FAIL"))
        ok = ok and hit
        os.remove(os.path.join(tmp, "notes.txt"))

        # 3. an unexpected directory
        os.makedirs(os.path.join(tmp, "backup"))
        got = check_deploy_dir(tmp)
        hit = any("backup" in p for p in got)
        print("  [%s] unexpected directory backup/ is REFUSED" % ("ok  " if hit else "FAIL"))
        ok = ok and hit
        os.rmdir(os.path.join(tmp, "backup"))

        # 4. a dot-file NESTED inside a permitted asset directory
        with open(os.path.join(tmp, "models", "Liberator", ".DS_Store"),
                  "w", encoding="utf-8") as fh:
            fh.write("x")
        got = check_deploy_dir(tmp)
        hit = any(".DS_Store" in p for p in got)
        print("  [%s] nested dot-file inside models/ is REFUSED" % ("ok  " if hit else "FAIL"))
        ok = ok and hit
        os.remove(os.path.join(tmp, "models", "Liberator", ".DS_Store"))

        # 5. and it must go back to clean afterwards, so the checks above were
        #    detecting the plant and not simply always failing.
        got = check_deploy_dir(tmp)
        print("  [%s] tree is clean again once the plants are removed (%d problems)"
              % ("ok  " if not got else "FAIL", len(got)))
        ok = ok and not got
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("deploy guard selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())

    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = os.path.join(repo, "testing", "_deploy")
    sys.exit(1 if enforce(out) else 0)
