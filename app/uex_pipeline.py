"""
The shared parts of the UEX importers, extracted from B1-B3 after they existed.

B4 of docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md, and the
order is emphatic that this file must not have been written first: "Do not
design it before B1-B3 exist - the abstraction guessed in advance is always
wrong." That turned out to be exactly right here, and the specific way it was
right is recorded below rather than in a commit message nobody will find.

WHAT THE THREE IMPORTERS GENUINELY SHARED
-----------------------------------------
1. `load_envelope()` - reading a UEX file and refusing a broken one. Identical
   in all three, and the only one already proven against known-bad input.
2. The coercions: `to_dt`, `to_bool`, `clean`. Small, boring, and each one had
   started to drift - `to_bool` existed in two files with the same body, and
   `clean` in one that needed it and not in another that also did.
3. `make_logger()` - one prefixed line per event, appended to one log file.
   Four copies existed, differing only in a string.
4. `split_detail()` - promoted columns out, everything else into JSONB. The
   same three lines in every importer, and the place where a dropped field
   would be silently lost.
5. `upsert_by_key()` - load what is stored, diff each row, insert or update,
   count all three outcomes. B1 (twice), B2 and the categories loader all do
   precisely this.

WHAT I EXPECTED THEM TO SHARE AND THEY DID NOT
-----------------------------------------------
**The write strategy, and this is the one that matters.** I would have
written a single generic importer where every table upserts on a natural key,
because that is what B1 and B2 do and they were written first. B3 does not
upsert at all - it is insert-only, keyed by (item, terminal, snapshot), and an
upsert there would silently overwrite price history. That is the §3.4 failure
this whole layer is built to avoid, and a generic importer designed after B1
and B2 would have walked straight into it while looking perfectly reasonable.
So `upsert_by_key()` is offered and `append_only()` is a separate function,
and neither pretends to be the other.

**The shape of a key.** B1 and B2 key on one integer from the source. B3 keys
on a three-part tuple of RESOLVED FOREIGN KEYS - database ids that do not
exist in the source file at all. A "key_column" parameter would have covered
the first two and been useless for the third.

**Foreign-key resolution.** B1 resolves parents inside its own pass, against
rows it is inserting in the same transaction. B2 resolves one lookup. B3
resolves two lookups plus a snapshot. Generalising this would have meant
inventing a small configuration language, and a configuration language is what
this rule exists to prevent.

**Deferral.** Only B3 has the notion of a row that cannot be placed YET and
must be reported as incomplete rather than failed. B1 and B2 have no such
state and would never have grown one.

So what is here is a toolkit, not a framework. Nothing in this file knows what
a terminal or a price is, and no importer is obliged to use all of it.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

# One log for the whole shop layer, matching the project's per-tool convention.
DEFAULT_LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "shop_layer_import.log"


# ---------------------------------------------------------------------------
# Reading a source file
# ---------------------------------------------------------------------------

def load_envelope(path: Path) -> list:
    """The rows in a UEX file, or a loud, explained failure.

    This is the guard §B5 asks for: "a malformed category file fails loudly,
    and does not silently import zero rows and report success."

    The distinction that took measurement to get right is between BROKEN and
    EMPTY. `{"status":"ok","http_code":200,"data":null}` is not a broken file -
    44 of the 100 category files in 20260801T235530Z look exactly like that,
    all of them HTTP 200 with envelope status "ok", and they are genuinely
    empty categories. Rejecting those would block a third of the catalogue.
    Accepting a truncated file as "empty" would hide real data loss. So the
    two are separated deliberately, and both directions are proven in
    checks/_verify_shop_importers.py.
    """
    if not path.exists():
        raise SystemExit(f"MALFORMED SOURCE: {path} does not exist")
    try:
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"MALFORMED SOURCE: {path} is not valid JSON - {exc}")

    if not isinstance(payload, dict) or "data" not in payload:
        raise SystemExit(
            f"MALFORMED SOURCE: {path} has no 'data' key - this is not a UEX "
            f"envelope and its shape will not be guessed at"
        )
    rows = payload["data"]
    if rows is None:
        return []
    if not isinstance(rows, list):
        raise SystemExit(
            f"MALFORMED SOURCE: {path} has 'data' as "
            f"{type(rows).__name__}, not a list"
        )
    return rows


# ---------------------------------------------------------------------------
# Coercions
# ---------------------------------------------------------------------------

def to_dt(value):
    """A UEX unix timestamp as a naive UTC datetime, or None.

    0 means "never", not 1970-01-01. Storing the epoch would put a real-looking
    date on a row that has none, and every staleness bucket downstream would
    then report it as 56 years old.
    """
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return None
    if seconds <= 0:
        return None
    return datetime.datetime.fromtimestamp(
        seconds, tz=datetime.timezone.utc
    ).replace(tzinfo=None)


def to_bool(value):
    """UEX's 0/1 integers as a bool, or None when genuinely absent."""
    if value is None:
        return None
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return None


def clean(value):
    """Empty and whitespace-only strings become None.

    UEX uses "" where it means "not set". Stored as "", every downstream
    `IS NOT NULL` is quietly wrong and every "do we have a code for this?"
    answers yes.
    """
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def split_detail(row: dict, promoted: set) -> dict | None:
    """Everything in the source row that is not a real column.

    §3.5: a field whose meaning is unclear is preserved verbatim in `detail`,
    never dropped and never given a guessed column. Returns None rather than
    {} so an empty tail stores as SQL NULL instead of an empty object.
    """
    tail = {k: v for k, v in row.items() if k not in promoted}
    return tail or None


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def make_logger(prefix: str, log_path: Path = DEFAULT_LOG_PATH):
    """A one-line-per-event logger, prefixed and appended to one file.

    No Unicode symbols anywhere in this project's log strings - per the known
    caveat in CLAUDE.md, print() can fail on them with no console attached and
    take the file write down with it.
    """
    def log(message: str) -> None:
        stamp = datetime.datetime.now().isoformat(timespec="seconds")
        line = f"[{stamp}] {prefix}: {message}"
        print(line)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    return log


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

class UpsertResult:
    """Counts from an upsert pass. Named rather than a bare tuple because
    three integers in a row is exactly the shape that gets swapped."""

    __slots__ = ("inserted", "updated", "unchanged")

    def __init__(self):
        self.inserted = 0
        self.updated = 0
        self.unchanged = 0

    @property
    def touched(self) -> int:
        return self.inserted + self.updated + self.unchanged

    def __str__(self) -> str:
        return (f"inserted {self.inserted}, updated {self.updated}, "
                f"unchanged {self.unchanged}")


def upsert_by_key(session, model, key_attr, rows, build_values,
                  dry_run=False, flush_each=False):
    """Insert or update `rows` on a single-column natural key.

    B1 (locations and terminals), B2 and the categories loader all do exactly
    this. B3 does NOT - see append_only() and the module docstring for why
    that distinction is load-bearing rather than tidy.

    `build_values(row)` returns either a dict of column values or None to skip
    the row. Returns (UpsertResult, index) where index maps key -> instance.
    """
    result = UpsertResult()
    index = {
        getattr(obj, key_attr): obj
        for obj in session.query(model).all()
    }

    for row in rows:
        key, values = build_values(row)
        if key is None or values is None:
            continue

        current = index.get(key)
        if current is None:
            current = model(**{key_attr: key}, **values)
            index[key] = current
            result.inserted += 1
            if not dry_run:
                session.add(current)
                if flush_each:
                    # B1 needs this: a child row in a later file must point at
                    # this row's real primary key, not at a pending object.
                    session.flush()
        elif any(getattr(current, k) != v for k, v in values.items()):
            result.updated += 1
            if not dry_run:
                for k, v in values.items():
                    setattr(current, k, v)
        else:
            result.unchanged += 1

    return result, index


def append_only(session, model, pending, batch_size=2000, dry_run=False):
    """Bulk-insert rows that must never overwrite what is already stored.

    Deliberately a separate function from upsert_by_key() rather than a flag on
    it. A flag would mean the destructive behaviour is one argument away from
    the append-only one, on the table where overwriting silently destroys
    history - and §3.4 exists because that has already happened once on this
    project. Two functions cannot be confused by a default.

    De-duplication against what is already stored is the CALLER's job, because
    only the caller knows the natural key.
    """
    from sqlalchemy import insert

    if dry_run or not pending:
        return 0
    for start in range(0, len(pending), batch_size):
        session.execute(insert(model), pending[start:start + batch_size])
    return len(pending)
