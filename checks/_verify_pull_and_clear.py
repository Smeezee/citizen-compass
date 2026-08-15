#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove pull_and_clear's verification can FAIL. Hard rule 12.

`verify()` decides whether a file is safe to delete from the only other place it
exists. If it can only ever return True, then pull_and_clear is not a careful
tool - it is `rm` with a progress bar and a reassuring name.

So every refusal path is driven here with input that MUST fail it, and the
acceptance paths are driven with input that must pass. Both directions, because
a checker that fails everything is as useless as one that passes everything.

Run:  python checks/_verify_pull_and_clear.py

Rule 15: encodings stated.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from pull_and_clear import verify, safe_local_path  # noqa: E402

BODY = b"the bytes that really arrived"
SHA = hashlib.sha256(BODY).hexdigest()
MD5 = hashlib.md5(BODY).hexdigest()

failures = []


def expect_reject(name, local, listed, want_method):
    ok, method, detail = verify(local, listed)
    if ok:
        failures.append("%s: verify() ACCEPTED input that must be rejected. "
                        "This path would delete unverified data." % name)
    elif method != want_method:
        failures.append("%s: rejected, but for the wrong reason (%s, expected %s)"
                        % (name, method, want_method))
    else:
        print("  refused as it must  : %-34s (%s)" % (name, method))


def expect_accept(name, local, listed, want_method):
    ok, method, detail = verify(local, listed)
    if not ok:
        failures.append("%s: verify() REJECTED input that is genuinely fine (%s: %s). "
                        "The tool would never clear anything." % (name, method, detail))
    elif method != want_method:
        failures.append("%s: accepted via %s, expected %s" % (name, method, want_method))
    else:
        print("  accepted as it must : %-34s (%s)" % (name, method))


print("REFUSALS - each of these must NOT be deleted:")

# The one that matters most: bytes that are not the bytes the receiver hashed.
expect_reject("corrupted body, receiver sha256",
              b"tampered-with", {"size": len(b"tampered-with"), "custom_metadata": {"sha256": SHA}},
              "sha256")

# A truncated download that still reports the right hash target.
expect_reject("truncated download",
              BODY[:10], {"size": len(BODY), "custom_metadata": {"sha256": SHA}},
              "size")

# Wrong bytes, no receiver hash, so the ETag is the only guard left.
expect_reject("corrupted body, ETag only",
              b"x" * len(BODY), {"size": len(BODY), "etag": MD5},
              "etag-md5")

# THE FAIL-CLOSED CASE. A multipart ETag is not an md5. With no receiver hash
# there is nothing to check against, and "nothing to check" must never mean "ok".
expect_reject("multipart ETag, no receiver hash",
              BODY, {"size": len(BODY), "etag": "d41d8cd98f00b204e9800998ecf8427e-3"},
              "nothing-to-verify-against")

expect_reject("no ETag and no receiver hash",
              BODY, {"size": len(BODY)},
              "nothing-to-verify-against")

# An empty sha256 string must not be treated as a hash that matched.
expect_reject("blank receiver hash, no usable ETag",
              BODY, {"size": len(BODY), "custom_metadata": {"sha256": "   "}, "etag": "not-a-hash"},
              "nothing-to-verify-against")

print("")
print("ACCEPTANCES - refusing these would make the tool useless:")

expect_accept("genuine file, receiver sha256",
              BODY, {"size": len(BODY), "custom_metadata": {"sha256": SHA}}, "sha256")

expect_accept("genuine file, receiver sha256 upper-case",
              BODY, {"size": len(BODY), "custom_metadata": {"sha256": SHA.upper()}}, "sha256")

expect_accept("genuine file, quoted ETag only",
              BODY, {"size": len(BODY), "etag": '"%s"' % MD5}, "etag-md5")

# The receiver hash must win when both are present, because it is the stronger
# statement - a different program computed it over the bytes that arrived.
expect_accept("both present, receiver hash preferred",
              BODY, {"size": len(BODY), "custom_metadata": {"sha256": SHA}, "etag": MD5}, "sha256")

print("")
print("PATH ESCAPES - a remote key must not write outside the download folder:")
for bad in ("../../evil.zip", "uploads/../../evil.zip", "/etc/passwd", "..\\..\\evil.zip"):
    try:
        dest = safe_local_path("collector-inbox", bad)
        root = os.path.abspath("collector-inbox")
        if not dest.startswith(root + os.sep) and dest != root:
            failures.append("safe_local_path(%r) escaped to %s" % (bad, dest))
        else:
            print("  contained           : %-34s -> %s" % (bad, os.path.relpath(dest, root)))
    except Exception as e:
        print("  refused outright    : %-34s (%s)" % (bad, e))

print("")
if failures:
    print("VERIFICATION FAILED - pull_and_clear must not be trusted with --apply:")
    for f in failures:
        print("  - %s" % f)
    sys.exit(1)

print("pull_and_clear's guard was driven into every refusal path and refused each")
print("one, and accepted every genuinely-good case. It can fail, so its passes mean")
print("something.")
sys.exit(0)
