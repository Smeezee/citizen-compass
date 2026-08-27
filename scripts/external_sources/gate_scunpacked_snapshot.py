#!/usr/bin/env python3
"""
C6 - run the five gates on a freshly cloned scunpacked-data snapshot, in order,
and finalize it only if every one of them passes.

    python scripts/external_sources/gate_scunpacked_snapshot.py <run_id>

THE ORDER OF THESE STEPS IS THE POINT, not a preference:

  git metadata is captured BEFORE .git is stripped. Reversing those two loses
  the provenance permanently, and provenance is the whole reason this snapshot
  is worth more than a folder of JSON.

  the LFS pointer scan runs BEFORE anything trusts the file sizes. A clone made
  without git-lfs replaces items.json - 128 MB - with a 130 byte text stub
  describing itself. File count unchanged, directory structure unchanged,
  nothing missing. That is the silent success this gate exists for.

  the malware scan runs BEFORE the rename out of .partial, and the tree is
  re-hashed AFTER, so the bytes that were scanned are provably the bytes that
  were finalized. Scanning and then finalizing something else is not a scan.

  the rename happens ONLY when all five have passed. A snapshot that is not
  sealed does not get a name that says it is.

NOTHING IS DELETED. .git is MOVED to _to_delete/, per CLAUDE.md rule 1.
"""
import datetime
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SNAPS = os.path.join(REPO, "data-layer", "external-sources",
                     "scunpacked-data", "snapshots")
MANS = os.path.join(REPO, "data-layer", "external-source-manifests")
VERIF = os.path.join(REPO, "data-layer", "external-source-verification")

results = {}
failed = []


def step(name, ok, detail=""):
    results[name] = {"result": "PASS" if ok else "FAIL", "detail": detail}
    print("  %-4s %s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        failed.append(name)
    return ok


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


def sha_tree(root):
    """sha256 of every file, by repo-relative path."""
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            h = hashlib.sha256()
            try:
                with open(p, "rb") as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
            except OSError as e:
                out[rel] = "READ_ERROR: %s" % e
                continue
            out[rel] = h.hexdigest()
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: gate_scunpacked_snapshot.py <run_id>")
        return 2
    run_id = sys.argv[1]
    partial = os.path.join(SNAPS, run_id + ".partial")
    final = os.path.join(SNAPS, run_id)
    if not os.path.isdir(partial):
        print("STOPPED: no %s" % partial)
        return 2
    if os.path.exists(final):
        print("STOPPED: %s already exists - refusing to overwrite a sealed "
              "snapshot." % final)
        return 2

    print("=" * 70)
    print("C6 - gating %s" % run_id)
    print("=" * 70)

    # ---------------------------------------- git metadata, BEFORE stripping
    print("\n--- git metadata, captured before .git is stripped ---")
    git_dir = os.path.join(partial, ".git")
    if not os.path.isdir(git_dir):
        print("STOPPED: no .git in the partial. Provenance cannot be captured "
              "after the fact, so nothing is finalized.")
        return 2

    def g(*args):
        r = run(["git", "-C", partial] + list(args))
        return r.stdout.strip() if r.returncode == 0 else None

    meta = {
        "git_head_commit": g("rev-parse", "HEAD"),
        "git_branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "git_head_subject": g("log", "-1", "--pretty=%s"),
        "git_commit_date": g("log", "-1", "--pretty=%cI"),
        "git_author_date": g("log", "-1", "--pretty=%aI"),
        "git_origin_url": g("config", "--get", "remote.origin.url"),
        "git_version": run(["git", "--version"]).stdout.strip(),
        "git_lfs_version": run(["git", "lfs", "version"]).stdout.strip(),
        "ordering_note": "Captured BEFORE .git was stripped. Reversing those "
                         "two steps would lose the provenance permanently.",
    }
    for k in ("git_head_commit", "git_head_subject"):
        if not meta[k]:
            print("STOPPED: could not read %s - the clone may be incomplete." % k)
            return 2
    print("  head    %s" % meta["git_head_commit"])
    print("  subject %s" % meta["git_head_subject"])
    print("  date    %s" % meta["git_commit_date"])

    lfs_ls = run(["git", "-C", partial, "lfs", "ls-files"]).stdout.strip()

    # --------------------------------------------------- LFS pointer stubs
    print("\n--- LFS pointer stubs (before anything trusts a file size) ---")
    r = run([sys.executable, os.path.join(HERE, "lfs_pointer_scan.py"), partial,
             # THE THRESHOLD GUARDS AGAINST A ~130 BYTE POINTER STUB, and
             # that is the only thing it should be sized against. It was first
             # set to 104,857,600 - pegged to the byte count of the previous
             # snapshot, where items.json was 128 MB PRETTY-PRINTED. Upstream
             # minified the file between 12232306 and 12344265: 66.4 MB of the
             # SAME data, 21,849 records becoming 21,855. The gate correctly
             # refused to seal, and the threshold was the thing that was wrong.
             # 10 MB is four orders of magnitude above a stub and does not
             # encode last month's whitespace as a requirement.
             "--expect-large", "items.json:10485760"])
    try:
        lfs_report = json.loads(r.stdout)
    except Exception:
        lfs_report = {"parse_error": r.stdout[:400], "stderr": r.stderr[:400]}
    stubs = lfs_report.get("pointer_stubs_found")
    step("lfs_pointer_scan", r.returncode == 0 and stubs == 0,
         "stubs found: %s, exit %d" % (stubs, r.returncode))

    # ------------------------------------------------ strip .git (MOVE it)
    print("\n--- stripping .git (moved, never deleted - rule 1) ---")
    dest = os.path.join(REPO, "_to_delete", "%s_source1_git" % run_id)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(git_dir, dest)
    step("git_directory_absent", not os.path.exists(git_dir),
         "moved to _to_delete/%s_source1_git" % run_id)

    # ------------------------------------------------------ GATE 1: present
    print("\n--- gate 1: the files that must be there, are ---")
    expect = {"items.json": os.path.isfile(os.path.join(partial, "items.json")),
              ".gitattributes": os.path.isfile(os.path.join(partial, ".gitattributes")),
              "ships/": os.path.isdir(os.path.join(partial, "ships"))}
    zero, readerr, total_files, total_bytes = [], [], 0, 0
    for dp, dn, fns in os.walk(partial):
        for fn in fns:
            p = os.path.join(dp, fn)
            total_files += 1
            try:
                sz = os.path.getsize(p)
                total_bytes += sz
                if sz == 0:
                    zero.append(os.path.relpath(p, partial))
            except OSError as e:
                readerr.append("%s: %s" % (os.path.relpath(p, partial), e))
    ok1 = all(expect.values()) and not readerr
    step("gate_1_files_present", ok1,
         "%d files, %.1f GB, %d zero-byte, %d read errors, %s"
         % (total_files, total_bytes / 1e9, len(zero), len(readerr),
            ", ".join("%s=%s" % kv for kv in expect.items())))

    # -------------------------------------------------- GATE 2: JSON parses
    print("\n--- gate 2: every .json parses, individually ---")
    n_json, n_ok, bad = 0, 0, []
    for dp, dn, fns in os.walk(partial):
        for fn in fns:
            if not fn.lower().endswith(".json"):
                continue
            n_json += 1
            p = os.path.join(dp, fn)
            try:
                with io.open(p, encoding="utf-8") as f:
                    json.load(f)
                n_ok += 1
            except Exception as e:
                bad.append("%s: %s" % (os.path.relpath(p, partial), str(e)[:80]))
    step("gate_2_json_parses", n_json > 0 and n_ok == n_json,
         "%d of %d parsed%s" % (n_ok, n_json,
                                ("; first bad: " + bad[0]) if bad else ""))

    # ------------------------------------------- GATE 3: file type inspection
    print("\n--- gate 3: file types - anything executable or hook-shaped ---")
    SUSPECT = (".exe", ".dll", ".bat", ".cmd", ".ps1", ".sh", ".py", ".js",
               ".vbs", ".scr", ".msi", ".jar", ".com")
    flagged = []
    for dp, dn, fns in os.walk(partial):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), partial).replace("\\", "/")
            if fn.lower().endswith(SUSPECT) or "/hooks/" in rel:
                flagged.append(rel)
    step("gate_3_file_type_inspection", not flagged,
         "%d files inspected, %d flagged%s"
         % (total_files, len(flagged),
            (": " + ", ".join(flagged[:5])) if flagged else ""))

    # ----------------------------------------------- pre-scan hashes
    print("\n--- hashing the tree before the scan ---")
    prescan = sha_tree(partial)
    print("  %d files hashed" % len(prescan))

    # ------------------------------------------------- GATE 4: malware scan
    print("\n--- gate 4: malware scan, BEFORE the rename ---")
    plat = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"),
                        "Microsoft", "Windows Defender", "Platform")
    mp = None
    if os.path.isdir(plat):
        for d in sorted(os.listdir(plat), reverse=True):
            c = os.path.join(plat, d, "MpCmdRun.exe")
            if os.path.exists(c):
                mp = c
                break
    if not mp:
        step("gate_4_malware_scan", False,
             "NOT PERFORMED - no MpCmdRun.exe found. Reported as not "
             "performed, never as passed.")
        scan = {"attempted": False}
    else:
        t0 = datetime.datetime.utcnow()
        r = run([mp, "-Scan", "-ScanType", "3", "-File", partial,
                 "-DisableRemediation"])
        t1 = datetime.datetime.utcnow()
        out = (r.stdout or "") + (r.stderr or "")
        clean = r.returncode == 0 and "found no threats" in out.lower()
        scan = {"attempted": True, "scanner": mp, "exit_code": r.returncode,
                "output": out.strip()[:400],
                "started_utc": t0.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "finished_utc": t1.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "elapsed_seconds": round((t1 - t0).total_seconds(), 1),
                "report_only": "-DisableRemediation was passed"}
        step("gate_4_malware_scan", clean,
             "exit %d in %.1fs: %s" % (r.returncode, scan["elapsed_seconds"],
                                       out.strip()[:90]))

    # ----------------------------------------- post-scan hashes must match
    print("\n--- re-hashing: the scanned bytes must be the finalized bytes ---")
    postscan = sha_tree(partial)
    same = prescan == postscan
    step("scanned_bytes_are_finalized_bytes", same,
         "%d files, %s" % (len(postscan),
                           "identical" if same else "TREE CHANGED DURING SCAN"))

    # ------------------------------------ GATE 5: content indicator scan
    print("\n--- gate 5: content indicators and unexpected domains ---")
    r = run([sys.executable, os.path.join(HERE, "integrity_scan.py"), partial])
    try:
        rep = json.loads(r.stdout)
    except Exception:
        rep = {}
    files = rep.get("files") or []
    unscanned = [f for f in files if not f.get("scanned")]
    hits = sum(len(f.get("content_indicator_hits") or {}) for f in files)
    unexpected = sum(len(f.get("unexpected_domains") or {}) for f in files)
    step("gate_5_content_indicator_scan",
         r.returncode == 0 and not unscanned and hits == 0 and unexpected == 0,
         "%d files seen, %d unscanned, %d indicator hits, %d unexpected domains"
         % (len(files), len(unscanned), hits, unexpected))

    # ---------------------------------------------------------- finalize
    print("\n" + "=" * 70)
    if failed:
        print("GATES FAILED: %s" % ", ".join(failed))
        print("The snapshot stays as %s.partial and is NOT sealed. A snapshot "
              "that did not pass does not get a name saying it did." % run_id)
        return 1

    os.rename(partial, final)
    print("all gates passed in order - renamed to %s" % run_id)

    os.makedirs(os.path.join(MANS, run_id), exist_ok=True)
    os.makedirs(os.path.join(VERIF, run_id), exist_ok=True)
    with io.open(os.path.join(VERIF, run_id, "01_postscan_sha256.json"), "w",
                 encoding="utf-8", newline="\n") as f:
        json.dump(postscan, f, indent=1, sort_keys=True)
    man = {
        "manifest_schema_version": "1.0",
        "run_id": run_id,
        "source_number": 1,
        "source_name": "scunpacked-data",
        "source_type": "Git repository clone (GitHub, Git LFS in use)",
        "canonical_source_url": "https://github.com/StarCitizenWiki/scunpacked-data",
        "run_context": "C6 - acquired to prove the C5 patch diff on a real "
                       "pair before 4.10 lands. NOT PROMOTED: the site keeps "
                       "serving 20260801T204744Z and keeps saying 4.9.",
        "snapshot_status": "complete",
        "snapshot_path": os.path.relpath(final, REPO).replace("\\", "/"),
        "previous_snapshot_run_id": "20260801T204744Z",
        "git_metadata_captured_before_stripping": meta,
        "lfs_handling": {"lfs_ls_files_output": lfs_ls,
                         "lfs_availability_checked_before_cloning": True,
                         "pointer_stub_scan": lfs_report},
        "git_directory_disposal": {
            "stripped": True,
            "method": "moved, NOT deleted - CLAUDE.md rule 1",
            "moved_to": "_to_delete/%s_source1_git" % run_id},
        "file_inventory": {"total_files": total_files,
                           "total_bytes": total_bytes},
        "gates": results,
        "gate_order_note": "Run strictly in order. The malware scan preceded "
                           "the rename out of .partial and the tree was "
                           "re-hashed afterwards, so the scanned bytes are "
                           "provably the finalized bytes.",
        "malware_scan": scan,
        "gates_all_passed_in_order": True,
        "sealed_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with io.open(os.path.join(MANS, run_id, "01_scunpacked-data_manifest.json"),
                 "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("manifest: data-layer/external-source-manifests/%s/" % run_id)
    print("build   : %s" % meta["git_head_subject"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
