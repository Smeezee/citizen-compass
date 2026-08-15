#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pull_and_clear.py - bring the uploads down, then clear the bucket.

    python scripts/pull_and_clear.py                  # DRY RUN. Changes nothing.
    python scripts/pull_and_clear.py --apply --out D  # download, verify, delete

WHY THIS EXISTS
---------------
R2 holds 10 GB, which is roughly 3,400 frames at ~3 MB each. Nothing removed
them, so the bucket was a one-way pipe that eventually fills and starts refusing
the uploads people took the trouble to send.

WHY IT DOES NOT GO THROUGH THE WORKER
-------------------------------------
The receiver is proven to refuse GET, HEAD, DELETE and PUT - there is no route
on it that can list or return data, and that is the point of it. Adding an admin
route would undo the exact property that was just verified. So this tool talks
to the R2 admin API with Sleven's account credentials, from his machine. The
public endpoint stays write-only, permanently.

THE ONE RULE THAT MATTERS
-------------------------
**Nothing is deleted that was not first downloaded AND verified.**

This step destroys the only copy of data that has already left a contributor's
machine - their collector cleared its local copy when the receiver confirmed the
hash. If this tool deletes something it did not really fetch, that data is gone
from everywhere in the world. So deletion is per-object and strictly ordered:

    download -> verify -> write -> re-read -> delete THAT object -> next

A crash, a network drop, or a failed verification at any point leaves every
remaining object exactly where it was. There is no batch delete, and no path
that deletes on a count rather than on a per-file proof.

WHAT "VERIFIED" MEANS, AND WHEN IT REFUSES
------------------------------------------
Three independent things are checked, and the strongest available must pass:

  1. SIZE against the listing.
  2. sha256 against `custom_metadata.sha256` - the hash THE RECEIVER computed
     over the bytes that actually arrived. This is the strongest check, because
     a different program produced it at a different time.
  3. md5 against the ETag, which R2 sets itself for single-part uploads.

If neither (2) nor (3) is usable - no receiver hash, and a multipart ETag, which
is not an MD5 and must never be compared as one - the object is KEPT, not
deleted, and reported. An unverifiable object is a reason to stop, not a
rounding error.

Rule 15: encodings stated. Rule 5: dry run first, and the dry run writes nothing.
"""

import argparse
import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.cloudflare.com/client/v4"
MD5_RE = re.compile(r"^[0-9a-f]{32}$")


# ---------------------------------------------------------------------------
# VERIFICATION - a pure function, so it can be fed known-bad input and proven to
# fail. See checks/_verify_pull_and_clear.py. A guard whose failure path has
# never executed is not a guard (hard rule 12).
# ---------------------------------------------------------------------------
def verify(local, listed):
    """Return (ok, method, detail). ok=False means DO NOT DELETE."""
    size = listed.get("size")
    if size is not None and len(local) != int(size):
        return False, "size", "listing says %s bytes, %d arrived" % (size, len(local))

    meta = listed.get("custom_metadata") or {}
    want_sha = (meta.get("sha256") or "").strip().lower()
    if want_sha:
        got = hashlib.sha256(local).hexdigest()
        if got != want_sha:
            return False, "sha256", "receiver recorded %s..., downloaded bytes are %s..." % (
                want_sha[:16], got[:16])
        return True, "sha256", "matches the hash the receiver computed on arrival"

    etag = (listed.get("etag") or "").strip().strip('"').lower()
    if MD5_RE.match(etag):
        got = hashlib.md5(local).hexdigest()
        if got != etag:
            return False, "etag-md5", "R2 recorded %s..., downloaded bytes are %s..." % (
                etag[:16], got[:16])
        return True, "etag-md5", "matches R2's own ETag"

    # FAIL CLOSED. A multipart ETag ("<hex>-3") is NOT an md5 of the content;
    # comparing it as one would fail every time, and treating its absence as a
    # pass would delete unverified data. Neither is acceptable, so: keep it.
    return False, "nothing-to-verify-against", (
        "no receiver sha256, and ETag %r is not a plain MD5 (multipart?), so "
        "there is nothing to check the download against" % (etag or "<none>"))


# ---------------------------------------------------------------------------
# R2 admin API
# ---------------------------------------------------------------------------
class R2(object):
    def __init__(self, account, bucket, token):
        self.base = "%s/accounts/%s/r2/buckets/%s" % (API, account, bucket)
        self.token = token

    def _call(self, method, path, data=None, headers=None):
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_header("Authorization", "Bearer " + self.token)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def list_all(self):
        """Every object, following the cursor.

        PAGINATION IS NOT OPTIONAL. R2 returns a page at a time; a tool that
        read only the first page would report a clean sweep having never seen
        most of the bucket, and it would look exactly like success.
        """
        out, cursor, pages = [], None, 0
        while True:
            q = "?per_page=1000"
            if cursor:
                q += "&cursor=" + urllib.parse.quote(cursor, safe="")
            st, body = self._call("GET", "/objects" + q)
            if st != 200:
                raise RuntimeError("list failed HTTP %d: %s" % (st, body[:300]))
            d = json.loads(body.decode("utf-8"))
            # BRANCH ON THE ENVELOPE, NOT ON HTTP 200. Cloudflare returns 200
            # with success:false; reading the status alone reports a clean list
            # for a call that actually failed.
            if not d.get("success"):
                raise RuntimeError("list refused: %s" % d.get("errors"))
            out.extend(d.get("result") or [])
            pages += 1
            cursor = (d.get("result_info") or {}).get("cursor")
            if not cursor:
                return out, pages

    def get(self, key):
        st, body = self._call("GET", "/objects/" + urllib.parse.quote(key, safe=""))
        if st != 200:
            raise RuntimeError("download failed HTTP %d: %s" % (st, body[:200]))
        return body

    def delete(self, key):
        st, body = self._call("DELETE", "/objects/" + urllib.parse.quote(key, safe=""))
        if st != 200:
            raise RuntimeError("delete failed HTTP %d: %s" % (st, body[:200]))
        d = json.loads(body.decode("utf-8"))
        if not d.get("success"):
            raise RuntimeError("delete refused: %s" % d.get("errors"))


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return "%d B" % n if u == "B" else "%.1f %s" % (n, u)
        n /= 1024.0


def read_token(explicit):
    if explicit:
        return explicit
    if os.environ.get("CLOUDFLARE_API_TOKEN"):
        return os.environ["CLOUDFLARE_API_TOKEN"]
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (".env", os.path.join(here, "..", ".env")):
        if os.path.exists(cand):
            for ln in io.open(cand, encoding="utf-8"):
                if ln.startswith("CLOUDFLARE_API_TOKEN="):
                    return ln.split("=", 1)[1].strip()
    return None


def safe_local_path(out_dir, key):
    """Map an object key to a local file, refusing anything that escapes out_dir.

    The key comes from a remote service, and anyone holding the upload key picks
    part of it. A `..` in a key must not write outside the download folder.
    """
    parts = [p for p in key.replace("\\", "/").split("/") if p not in ("", ".", "..")]
    if not parts:
        parts = ["unnamed"]
    dest = os.path.abspath(os.path.join(out_dir, *parts))
    root = os.path.abspath(out_dir)
    if not (dest == root or dest.startswith(root + os.sep)):
        raise RuntimeError("object key %r would write outside %s" % (key, root))
    return dest


def main():
    ap = argparse.ArgumentParser(description="Pull uploads down from R2, then clear them.")
    ap.add_argument("--apply", action="store_true",
                    help="actually download and DELETE. Without this, nothing changes.")
    ap.add_argument("--out", default="collector-inbox",
                    help="folder to download into (default: collector-inbox)")
    ap.add_argument("--account",
                    default=os.environ.get("CF_ACCOUNT_ID", "ad974500ce73c9694e94213c4d762f3e"))
    ap.add_argument("--bucket", default="collector-uploads")
    ap.add_argument("--token", default=None)
    ap.add_argument("--keep", action="store_true",
                    help="download everything but delete NOTHING (a backup, not a clear)")
    args = ap.parse_args()

    token = read_token(args.token)
    if not token:
        print("No CLOUDFLARE_API_TOKEN found. Nothing was listed, downloaded or deleted.")
        return 2

    r2 = R2(args.account, args.bucket, token)
    try:
        objs, pages = r2.list_all()
    except Exception as e:
        print("COULD NOT LIST THE BUCKET: %s" % e)
        print("Nothing was downloaded and nothing was deleted.")
        return 2

    total = sum(int(o.get("size") or 0) for o in objs)
    print("bucket   : %s" % args.bucket)
    print("contents : %d object(s), %s, read over %d page(s)" % (len(objs), human(total), pages))

    if not objs:
        print("")
        print("The bucket is empty. Nothing to do.")
        return 0

    if not args.apply:
        print("")
        print("DRY RUN - nothing has been downloaded, written or deleted.")
        print("It would download into %s\\ and then delete each object it verified:"
              % os.path.abspath(args.out))
        print("")
        for o in objs[:50]:
            meta = o.get("custom_metadata") or {}
            if meta.get("sha256"):
                how = "receiver sha256"
            elif MD5_RE.match((o.get("etag") or "").strip('"').lower()):
                how = "ETag md5"
            else:
                how = "NOTHING TO VERIFY AGAINST - would be KEPT, not deleted"
            print("    %-52s %10s  verify by %s"
                  % (o["key"][:52], human(int(o.get("size") or 0)), how))
        if len(objs) > 50:
            print("    ... and %d more" % (len(objs) - 50))
        print("")
        print("Re-run with --apply when you have read that list.")
        return 0

    os.makedirs(args.out, exist_ok=True)
    got_n = got_b = del_n = del_b = 0
    kept = []

    for o in objs:
        key = o["key"]
        try:
            data = r2.get(key)
        except Exception as e:
            kept.append((key, "download failed: %s" % e))
            continue

        ok, method, detail = verify(data, o)
        if not ok:
            # KEEP IT. A file we could not prove we have is a file we must not
            # remove from the only other place it exists.
            kept.append((key, "NOT VERIFIED (%s): %s" % (method, detail)))
            continue

        try:
            dest = safe_local_path(args.out, key)
        except Exception as e:
            kept.append((key, str(e)))
            continue
        d = os.path.dirname(dest)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)

        # RE-READ FROM DISK BEFORE DELETING. Holding correct bytes in memory is
        # not the same as having them on disk - a full disk, a short write, or an
        # antivirus quarantine all produce a file that is not what was verified.
        with open(dest, "rb") as f:
            on_disk = f.read()
        if on_disk != data:
            kept.append((key, "the written file does not match what was downloaded"))
            continue

        got_n += 1
        got_b += len(data)

        if args.keep:
            continue
        try:
            r2.delete(key)
            del_n += 1
            del_b += len(data)
        except Exception as e:
            kept.append((key, "downloaded and verified, but the delete failed: %s" % e))

    print("")
    print("downloaded : %d file(s), %s -> %s" % (got_n, human(got_b), os.path.abspath(args.out)))
    if args.keep:
        print("deleted    : 0 - --keep was given, so the bucket is untouched")
    else:
        print("deleted    : %d object(s), %s" % (del_n, human(del_b)))

    if kept:
        print("")
        print("KEPT IN THE BUCKET (%d) - each failed a check, so nothing was removed:" % len(kept))
        for k, why in kept:
            print("    %s" % k)
            print("        %s" % why)

    # COUNT BOTH WAYS, FROM THE SERVER. Re-listing is the only honest
    # confirmation - our own tally cannot disagree with itself, so on its own it
    # proves nothing at all.
    try:
        after, _ = r2.list_all()
        expected = len(objs) if args.keep else len(kept)
        print("")
        print("re-listed  : %d object(s) remain in the bucket" % len(after))
        if len(after) != expected:
            print("    MISMATCH: expected %d to remain. Investigate before running this again."
                  % expected)
            return 1
        print("    matches what this run intended to leave behind")
    except Exception as e:
        print("")
        print("could not re-list to confirm: %s" % e)
        return 1

    return 0 if not kept else 1


if __name__ == "__main__":
    sys.exit(main())
