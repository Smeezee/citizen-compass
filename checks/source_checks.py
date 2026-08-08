"""
Auditors for the Stage 1 external sources (Part C of the Path C order).

Phase 1 landed five sources and ruled two out. Nothing checked them AGAINST
EACH OTHER, and that is where the value is.

Three checkers, all findings-only, all stdlib. They never modify a snapshot, a
manifest, or project data - and in particular `cross_source_disagreement`
NEVER picks a winner. Choosing between sources is Stage 2's job under the
canonical-source decision; this layer's job is to say "these two disagree, here
are both values". Flagging and resolving are different responsibilities, and
merging them is how an audit layer quietly becomes an import path.
"""

import hashlib
import json
import os
from pathlib import Path

from checks.framework import Finding

MANIFEST_ROOT = Path("data-layer") / "external-source-manifests"
VERIFICATION_ROOT = Path("data-layer") / "external-source-verification"

# Hashing 4.5 GB across 28,960 files is minutes, not seconds. The limit is
# configurable, but exceeding it is reported as a LIMITATION naming the exact
# coverage - never as a PASS. A partial check reported as success is the
# silent-success failure this project keeps finding.
MAX_BYTES_ENV = "CC_SNAPSHOT_INTEGRITY_MAX_BYTES"


def _sha256(path: Path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def _expected_hashes(manifest: dict, repo_root: Path, run_dir: str, source_no: str):
    """Return {relpath: sha256} or None if this manifest records no per-file
    hashes. Two recorded formats exist and both are supported."""
    inv = manifest.get("file_inventory") or {}

    files = inv.get("files")
    if isinstance(files, list) and files:
        return {
            f["file"]: f["sha256"]
            for f in files
            if isinstance(f, dict) and f.get("file") and f.get("sha256")
        }

    # Large snapshots record hashes in a sidecar file instead of inline.
    vdir = repo_root / VERIFICATION_ROOT / run_dir
    if vdir.is_dir():
        for candidate in sorted(vdir.glob(f"{source_no}_postscan_sha256.json")):
            try:
                raw = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                return None
            if isinstance(raw, dict):
                out = {}
                for rel, val in raw.items():
                    # recorded as [size, sha256]
                    if isinstance(val, (list, tuple)) and len(val) >= 2:
                        out[rel] = val[1]
                    elif isinstance(val, str):
                        out[rel] = val
                return out or None
    return None


def snapshot_integrity_check(repo_root: Path) -> list[Finding]:
    """Re-verify every sealed snapshot against its recorded hashes.

    Sealed snapshots are never modified, so ANY difference is either corruption
    or a broken rule. The order requires three problems to stay distinct,
    because they have three different causes and three different responses:

      * manifest unreadable  - the record itself is gone or broken
      * file missing         - something deleted from a sealed snapshot
      * file changed         - contents differ from what was sealed
    """
    findings = []
    manifest_root = repo_root / MANIFEST_ROOT
    if not manifest_root.is_dir():
        return [Finding("snapshot_integrity", None, "LIMITATION",
                        f"{MANIFEST_ROOT} does not exist - no sealed snapshots to verify")]

    try:
        max_bytes = int(os.environ.get(MAX_BYTES_ENV, "0")) or None
    except ValueError:
        max_bytes = None

    manifests = sorted(manifest_root.glob("*/*_manifest.json"))
    if not manifests:
        return [Finding("snapshot_integrity", None, "LIMITATION",
                        "no *_manifest.json files found")]

    for mpath in manifests:
        run_dir = mpath.parent.name
        subject = f"{run_dir}/{mpath.name}"
        source_no = mpath.name.split("_", 1)[0]

        try:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception as e:
            findings.append(Finding("snapshot_integrity", subject, "DEFECT",
                                     f"manifest unreadable: {type(e).__name__}: {e}"))
            continue

        status = manifest.get("snapshot_status")
        snap_rel = manifest.get("snapshot_path")
        if not snap_rel:
            findings.append(Finding("snapshot_integrity", subject, "LIMITATION",
                                     f"no snapshot_path recorded (snapshot_status={status!r}) - "
                                     f"nothing was landed, so there is nothing to verify"))
            continue

        snap_dir = repo_root / snap_rel
        if not snap_dir.is_dir():
            result = "DEFECT" if status == "complete" else "LIMITATION"
            findings.append(Finding("snapshot_integrity", subject, result,
                                     f"snapshot directory {snap_rel} does not exist "
                                     f"(snapshot_status={status!r})"))
            continue

        expected = _expected_hashes(manifest, repo_root, run_dir, source_no)
        if not expected:
            findings.append(Finding("snapshot_integrity", subject, "LIMITATION",
                                     f"no per-file hashes recorded for this snapshot "
                                     f"(snapshot_status={status!r}) - integrity cannot be verified"))
            continue

        total_bytes = (manifest.get("file_inventory") or {}).get("total_bytes")
        if max_bytes and isinstance(total_bytes, int) and total_bytes > max_bytes:
            findings.append(Finding("snapshot_integrity", subject, "LIMITATION",
                                     f"snapshot is {total_bytes} bytes across {len(expected)} files, "
                                     f"over the {max_bytes}-byte limit for this run - NOT verified. "
                                     f"Unset {MAX_BYTES_ENV} to verify it."))
            continue

        missing, changed, unreadable = [], [], []
        for rel, want in expected.items():
            fpath = snap_dir / rel
            if not fpath.is_file():
                missing.append(rel)
                continue
            try:
                got = _sha256(fpath)
            except Exception as e:
                unreadable.append(f"{rel} ({type(e).__name__})")
                continue
            if got != want:
                changed.append(rel)

        # Three problems, three findings - never merged into one "integrity" line.
        if missing:
            findings.append(Finding("snapshot_integrity", subject, "DEFECT",
                                     f"{len(missing)} file(s) recorded in the manifest are MISSING from "
                                     f"the sealed snapshot: {sorted(missing)[:10]}"))
        if changed:
            findings.append(Finding("snapshot_integrity", subject, "DEFECT",
                                     f"{len(changed)} file(s) have CHANGED since sealing - sha256 differs "
                                     f"from the manifest: {sorted(changed)[:10]}"))
        if unreadable:
            findings.append(Finding("snapshot_integrity", subject, "WARNING",
                                     f"{len(unreadable)} file(s) could not be read to verify: "
                                     f"{sorted(unreadable)[:10]}"))
        if not (missing or changed or unreadable):
            findings.append(Finding("snapshot_integrity", subject, "PASS",
                                     f"all {len(expected)} files match their recorded sha256"))

    return findings


# --------------------------------------------------------------------------
# C2 - cross-source disagreement
# --------------------------------------------------------------------------
def _norm_name(s) -> str:
    return " ".join(str(s or "").split()).strip().lower()


def _first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def _load_scunpacked_com_ships(repo_root: Path):
    base = repo_root / "data-layer" / "external-sources" / "scunpacked.com" / "snapshots"
    if not base.is_dir():
        return None, None
    for snap in sorted(base.iterdir(), reverse=True):
        f = snap / "ships.json"
        if f.is_file():
            try:
                return json.loads(f.read_text(encoding="utf-8")), snap.name
            except Exception:
                return None, snap.name
    return None, None


def _load_wiki_vehicles(repo_root: Path):
    base = repo_root / "data-layer" / "external-sources" / "api.star-citizen.wiki" / "snapshots"
    if not base.is_dir():
        return None, None
    for snap in sorted(base.iterdir(), reverse=True):
        pages = sorted(snap.glob("vehicles_page_*.json"))
        if not pages:
            continue
        records = []
        for p in pages:
            try:
                doc = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            data = doc.get("data") if isinstance(doc, dict) else doc
            if isinstance(data, list):
                records.extend(data)
        if records:
            return records, snap.name
    return None, None


def _wiki_manufacturer(rec):
    m = rec.get("manufacturer")
    if isinstance(m, dict):
        return m.get("name") or m.get("code")
    return m


def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return None


def cross_source_disagreement_check(repo_root: Path) -> list[Finding]:
    """Where two sources describe the same ship, compare them and report the
    disagreements with BOTH values and BOTH sources named.

    Never picks a winner. Under the canonical-source decision the tiers set
    SEVERITY, not truth: a disagreement between two high-tier sources is worth
    more attention than one involving a lower tier, but neither is resolved
    here. Stage 2 resolves; this layer only flags.
    """
    findings = []

    com_ships, com_snap = _load_scunpacked_com_ships(repo_root)
    wiki_vehicles, wiki_snap = _load_wiki_vehicles(repo_root)

    if com_ships is None or wiki_vehicles is None:
        missing = []
        if com_ships is None:
            missing.append("scunpacked.com ships.json")
        if wiki_vehicles is None:
            missing.append("api.star-citizen.wiki vehicles_page_*.json")
        return [Finding("cross_source_disagreement", None, "LIMITATION",
                        f"cannot compare - not landed or unreadable: {', '.join(missing)}")]

    com_by_name = {}
    for s in com_ships:
        if isinstance(s, dict) and s.get("Name"):
            com_by_name.setdefault(_norm_name(s["Name"]), s)

    wiki_by_name = {}
    for v in wiki_vehicles:
        if not isinstance(v, dict):
            continue
        for key in (v.get("name"), v.get("shipmatrix_name"), v.get("game_name")):
            if key:
                wiki_by_name.setdefault(_norm_name(key), v)

    overlap = sorted(set(com_by_name) & set(wiki_by_name))
    if not overlap:
        return [Finding("cross_source_disagreement", None, "LIMITATION",
                        f"no ship names overlap between scunpacked.com ({len(com_by_name)}) "
                        f"and the wiki API ({len(wiki_by_name)}) - nothing comparable")]

    # Each comparison returns (disagrees, shown_a, shown_b) or None to skip.
    #
    # PICKING THE RIGHT COUNTERPART FIELD IS MOST OF THE WORK, and getting it
    # wrong produces confident nonsense. The first version of this checker
    # compared scunpacked.com's numeric `Size` (2) against the wiki's `size`,
    # which is a LOCALISED LABEL DICT ({'en_EN': 'Small', ...}). That flagged
    # all 117 shared ships as disagreeing. The real counterpart is `size_class`,
    # against which 115 of 117 agree - so the correct field turns 117 fabricated
    # findings into 2 genuine ones.
    def cmp_manufacturer(s, v):
        a, b = s.get("Manufacturer"), _wiki_manufacturer(v)
        if not a or not b:
            return None
        na, nb = _norm_name(a), _norm_name(b)
        # "RSI" vs "Roberts Space Industries" is a naming form, not a conflict.
        if na == nb or na in nb or nb in na:
            return None
        return (True, a, b)

    def cmp_size(s, v):
        a, b = _num(s.get("Size")), _num(v.get("size_class"))
        if a is None or b is None:
            return None
        return None if a == b else (True, a, b)

    def cmp_cargo(s, v):
        a, b = _num(s.get("Cargo")), _num(v.get("cargo_capacity"))
        if a is None or b is None:
            return None
        scale = max(abs(a), abs(b), 1.0)
        return None if abs(a - b) / scale <= 0.10 else (True, a, b)

    def cmp_mass(s, v):
        """Mass is bracketed, not point-compared, and that is a measurement
        decision rather than a tolerance that was loosened until findings went
        away.

        The wiki publishes mass_hull AND mass_total (hull plus loadout);
        scunpacked.com publishes a single Mass whose definition is not stated.
        Measured across the 117 shared ships, the median difference is 9.5%
        against hull and 7.1% against total - a systematic offset, which means
        these are different quantities rather than occasional disagreements.
        Point-comparing them would report ~50 disagreements caused entirely by
        definition.

        So a value is only flagged when it falls outside the whole hull..total
        range with 10% slack - i.e. no reading of "mass" explains it. That
        still catches the real ones: the Anvil Carrack is 97,858 here and
        3,275,858 there, a 33x difference.
        """
        a = _num(s.get("Mass"))
        vals = [x for x in (_num(v.get("mass_hull")), _num(v.get("mass_total"))) if x is not None]
        if a is None or not vals:
            return None
        lo, hi = min(vals) * 0.9, max(vals) * 1.1
        if lo <= a <= hi:
            return None
        return (True, a, f"hull={min(vals)} total={max(vals)}")

    COMPARISONS = [
        ("manufacturer", cmp_manufacturer),
        ("size", cmp_size),
        ("cargo", cmp_cargo),
        ("mass", cmp_mass),
    ]

    disagreements = 0
    for name in overlap:
        s, v = com_by_name[name], wiki_by_name[name]
        for label, fn in COMPARISONS:
            outcome = fn(s, v)
            if not outcome:
                continue
            _, shown_a, shown_b = outcome
            disagreements += 1
            findings.append(Finding(
                "cross_source_disagreement", f"{name}:{label}", "WARNING",
                f"{label} disagrees: scunpacked.com (snapshot {com_snap}) says {shown_a!r}; "
                f"api.star-citizen.wiki (snapshot {wiki_snap}) says {shown_b!r}. "
                f"Reported only - this layer does not choose between sources."
            ))

    findings.append(Finding(
        "cross_source_disagreement", "mass:definition", "LIMITATION",
        "scunpacked.com publishes one unlabelled Mass; the wiki publishes mass_hull and "
        "mass_total. Median difference across shared ships is 9.5% against hull and 7.1% "
        "against total, so these are different measurements rather than a data conflict. "
        "Mass is therefore bracketed against hull..total, and only values no definition "
        "explains are reported above."
    ))

    if not disagreements:
        findings.append(Finding("cross_source_disagreement", None, "PASS",
                                 f"compared {len(overlap)} ships present in both sources across "
                                 f"{len(COMPARISONS)} fields, no disagreements beyond tolerance"))
    else:
        findings.append(Finding("cross_source_disagreement", None, "LIMITATION",
                                 f"compared {len(overlap)} ships common to both sources; "
                                 f"{len(com_by_name)} scunpacked.com and {len(wiki_by_name)} wiki "
                                 f"entries had no counterpart and were not compared"))
    return findings


# --------------------------------------------------------------------------
# C3 - UEX join health
# --------------------------------------------------------------------------
# UEX states its own tolerances: +/-20% on commodities, +/-100% on items. A
# price outside a plausible absolute band is a different claim from a price
# outside UEX's stated tolerance, and only the first can be checked without a
# second price source - so that is what is checked, and it is labelled as such.
UEX_MIN_PRICE = 1
UEX_MAX_PRICE = 100_000_000


def uex_join_health_check(repo_root: Path) -> list[Finding]:
    """UEX is Tier C and the whole point of the source is the item -> shop ->
    price link. Measure what fraction of items.uuid actually joins to
    fps-items.json, and report it as a tracked number.

    The manifest claims 5,566 of 7,728 records carry a UUID. That is CONFIRMED
    FROM THE DATA here rather than trusted - a manifest is a record of what a
    run believed, not evidence.
    """
    findings = []
    base = repo_root / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
    if not base.is_dir():
        return [Finding("uex_join_health", None, "LIMITATION",
                        "no uexcorp snapshots landed")]

    snap = None
    for cand in sorted(base.iterdir(), reverse=True):
        if list(cand.glob("items_category_*.json")):
            snap = cand
            break
    if snap is None:
        return [Finding("uex_join_health", None, "LIMITATION",
                        "no items_category_*.json in any uexcorp snapshot")]

    items, unreadable = [], []
    for p in sorted(snap.glob("items_category_*.json")):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            unreadable.append(f"{p.name} ({type(e).__name__})")
            continue
        data = doc.get("data") if isinstance(doc, dict) else doc
        if isinstance(data, list):
            items.extend(x for x in data if isinstance(x, dict))

    if unreadable:
        findings.append(Finding("uex_join_health", snap.name, "WARNING",
                                 f"{len(unreadable)} item file(s) unreadable and excluded from the "
                                 f"join rate, so the rate below understates coverage: {unreadable[:5]}"))

    if not items:
        return findings + [Finding("uex_join_health", snap.name, "LIMITATION",
                                   "no item records could be read")]

    with_uuid = [i for i in items if i.get("uuid")]
    findings.append(Finding(
        "uex_join_health", f"{snap.name}:uuid-presence",
        "PASS" if with_uuid else "DEFECT",
        f"{len(with_uuid)} of {len(items)} UEX item records carry a uuid "
        f"({100.0 * len(with_uuid) / len(items):.1f}%) - measured from the data, not the manifest"
    ))

    # The join target: fps-items.json from source 1's snapshot.
    sc_base = repo_root / "data-layer" / "external-sources" / "scunpacked-data" / "snapshots"
    fps = None
    if sc_base.is_dir():
        for cand in sorted(sc_base.iterdir(), reverse=True):
            f = cand / "fps-items.json"
            if f.is_file():
                fps = f
                break
    if fps is None:
        findings.append(Finding("uex_join_health", snap.name, "LIMITATION",
                                 "fps-items.json not found in any scunpacked-data snapshot - "
                                 "the join rate cannot be measured"))
        return findings

    try:
        fps_doc = json.loads(fps.read_text(encoding="utf-8"))
    except Exception as e:
        findings.append(Finding("uex_join_health", snap.name, "WARNING",
                                 f"fps-items.json unreadable: {type(e).__name__}: {e}"))
        return findings

    target_uuids = set()
    records = fps_doc if isinstance(fps_doc, list) else fps_doc.get("data", [])
    for r in records if isinstance(records, list) else []:
        if not isinstance(r, dict):
            continue
        if r.get("reference"):
            target_uuids.add(str(r["reference"]).lower())
        std = r.get("stdItem")
        if isinstance(std, dict) and std.get("UUID"):
            target_uuids.add(str(std["UUID"]).lower())

    if not target_uuids:
        findings.append(Finding("uex_join_health", snap.name, "DEFECT",
                                 f"fps-items.json ({fps.parent.name}) yielded no UUIDs from "
                                 f"`reference` or `stdItem.UUID` - the documented join key is absent, "
                                 f"so the item->shop->price link cannot be built"))
        return findings

    joined = [i for i in with_uuid if str(i["uuid"]).lower() in target_uuids]
    rate = 100.0 * len(joined) / len(with_uuid) if with_uuid else 0.0
    result = "PASS" if rate >= 50 else ("WARNING" if rate > 0 else "DEFECT")
    findings.append(Finding(
        "uex_join_health", f"{snap.name}:join-rate", result,
        f"{len(joined)} of {len(with_uuid)} UEX items with a uuid join to fps-items.json "
        f"({rate:.1f}%); fps-items.json contributed {len(target_uuids)} distinct UUIDs. "
        f"Tracked number - UEX is Tier C and this link is the source's entire purpose."
    ))

    prices = []
    for i in items:
        for key in ("price_buy", "price_sell", "price"):
            v = _num(i.get(key))
            if v is not None and v > 0:
                prices.append((i.get("name"), key, v))
    implausible = [p for p in prices if p[2] < UEX_MIN_PRICE or p[2] > UEX_MAX_PRICE]
    if implausible:
        findings.append(Finding("uex_join_health", f"{snap.name}:price-bounds", "WARNING",
                                 f"{len(implausible)} price value(s) outside the plausible "
                                 f"{UEX_MIN_PRICE}-{UEX_MAX_PRICE} aUEC band: {implausible[:5]}"))
    elif prices:
        findings.append(Finding("uex_join_health", f"{snap.name}:price-bounds", "PASS",
                                 f"all {len(prices)} price values fall inside the plausible "
                                 f"{UEX_MIN_PRICE}-{UEX_MAX_PRICE} aUEC band"))
    else:
        findings.append(Finding("uex_join_health", f"{snap.name}:price-bounds", "LIMITATION",
                                 "no price fields present on these item records - the items "
                                 "endpoints carry catalogue data; prices live on other endpoints"))

    return findings


SNAPSHOT_SOURCES_ROOT = Path("data-layer") / "external-sources"

# A hard cap so a runaway tree cannot turn an auditor into an hours-long walk.
# Exceeding it is reported as a LIMITATION naming the exact coverage, never as a
# PASS - same rule as snapshot_integrity_check above.
SHAPE_MAX_FILES_ENV = "CC_SNAPSHOT_SHAPE_MAX_FILES"
SHAPE_MAX_FILES_DEFAULT = 250_000


def snapshot_shape_check(repo_root: Path) -> list[Finding]:
    """Structural audit of the snapshot tree. Two distinct defects, kept apart.

    1. LOOSE FILES directly inside a `snapshots/` directory.

       `snapshots/` holds sealed snapshot DIRECTORIES and nothing else. On
       2026-08-06 an aborted UEX pull left these as SIBLINGS of the snapshot
       directories rather than inside one:

           uexcorp/snapshots/20260806T033217Z.pullstderr.log    98 bytes
           uexcorp/snapshots/20260806T033217Z.pullsummary.json   0 bytes

       The intended paths were `20260806T033217Z/_pull_stderr.log` and
       `.../_pull_summary.json` - the separator AND the leading underscore are
       both gone. `uex_corp.py` writes neither file: it prints the summary to
       stdout and diagnostics to stderr, so the redirect is done by the CALLER.
       There is no runner script in this repo, which means the malformed names
       came from a hand-typed redirect and there is no committed code carrying
       this bug to fix. That is exactly why it needs a CHECK rather than a
       patch - nothing in the repo can be corrected to prevent a recurrence, so
       the only durable guard is one that catches the result.

       It matters beyond tidiness: a sealed-snapshot model whose snapshot
       directory can contain loose files is one bad glob away from a gate
       enumerating a file where it expected a snapshot.

    2. ZERO-BYTE files anywhere inside the snapshot tree.

       A separate defect that survives fixing the first one. Two of the three
       empty artifacts found on 2026-08-07 sit at entirely CORRECT paths:

           api.star-citizen.wiki/snapshots/20260731T031754Z.partial/
                                                   _fetch_metadata.json  0 bytes
           api.star-citizen.wiki/snapshots/
               20260801T015346Z.partial.aborted__pagesize50/
                                                   _pull_summary.json    0 bytes

       An artifact that exists, is readable, parses as nothing and reports no
       failure is the silent-success shape this project keeps finding. A run
       that dies partway leaves no recoverable record of what it did, while
       looking from the outside like a run that produced one.

    Findings-only. This never deletes, moves or rewrites anything - per hard
    rule 1 the cleanup of anything it reports is Sleven's.
    """
    findings: list[Finding] = []
    root = repo_root / SNAPSHOT_SOURCES_ROOT

    if not root.is_dir():
        return [Finding("snapshot_shape", str(SNAPSHOT_SOURCES_ROOT), "LIMITATION",
                        "external-sources root not present, so no snapshot shape "
                        "check was performed. This is reported as NOT PERFORMED, "
                        "never as a pass.")]

    try:
        max_files = int(os.environ.get(SHAPE_MAX_FILES_ENV, SHAPE_MAX_FILES_DEFAULT))
    except ValueError:
        max_files = SHAPE_MAX_FILES_DEFAULT

    snapshot_dirs = sorted(root.glob("*/snapshots"))
    if not snapshot_dirs:
        return [Finding("snapshot_shape", str(SNAPSHOT_SOURCES_ROOT), "LIMITATION",
                        "no */snapshots directories found under the external-sources "
                        "root, so nothing was checked.")]

    seen_files = 0
    truncated = False

    for snaps in snapshot_dirs:
        source = snaps.parent.name

        # --- 1. loose files sitting directly in snapshots/ -------------------
        try:
            entries = sorted(snaps.iterdir())
        except OSError as e:
            findings.append(Finding("snapshot_shape", f"{source}:snapshots", "LIMITATION",
                                    f"could not read {snaps}: {type(e).__name__}: {e}. "
                                    f"Reported as not performed, not as a pass."))
            continue

        loose = [p for p in entries if p.is_file()]
        if loose:
            findings.append(Finding(
                "snapshot_shape", f"{source}:loose-files", "DEFECT",
                f"{len(loose)} file(s) sit directly inside {snaps.as_posix()}, which "
                f"must contain snapshot DIRECTORIES only. Anything enumerating this "
                f"directory expecting snapshots will read a file instead. Files: "
                f"{[p.name for p in loose][:10]}"))
        else:
            findings.append(Finding(
                "snapshot_shape", f"{source}:loose-files", "PASS",
                f"{snaps.as_posix()} contains only directories "
                f"({len([p for p in entries if p.is_dir()])} snapshot(s))"))

        # --- 2. zero-byte files anywhere in the tree -------------------------
        empties = []
        try:
            for p in snaps.rglob("*"):
                if truncated:
                    break
                if not p.is_file():
                    continue
                seen_files += 1
                if seen_files > max_files:
                    truncated = True
                    break
                if p.stat().st_size == 0:
                    empties.append(p.relative_to(snaps).as_posix())
        except OSError as e:
            findings.append(Finding("snapshot_shape", f"{source}:zero-byte", "LIMITATION",
                                    f"walk of {snaps} failed: {type(e).__name__}: {e}. "
                                    f"Reported as not performed, not as a pass."))
            continue

        if empties:
            findings.append(Finding(
                "snapshot_shape", f"{source}:zero-byte", "DEFECT",
                f"{len(empties)} zero-byte file(s) inside {snaps.as_posix()}. An "
                f"artifact that exists, reads clean and contains nothing reports no "
                f"failure while recording none of what the run did. Files: "
                f"{empties[:10]}"))
        else:
            findings.append(Finding(
                "snapshot_shape", f"{source}:zero-byte", "PASS",
                f"no zero-byte files under {snaps.as_posix()}"))

    if truncated:
        findings.append(Finding(
            "snapshot_shape", str(SNAPSHOT_SOURCES_ROOT), "LIMITATION",
            f"stopped after {max_files} files ({SHAPE_MAX_FILES_ENV}). Coverage is "
            f"PARTIAL and the unwalked remainder was NOT checked - this is not a pass "
            f"over the whole tree."))

    return findings


CHECKERS = [
    ("snapshot_integrity", snapshot_integrity_check),
    ("cross_source_disagreement", cross_source_disagreement_check),
    ("uex_join_health", uex_join_health_check),
    ("snapshot_shape", snapshot_shape_check),
]
