"""Resolving a UEX location reference to a readable place.

A1 of docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.

THE PROBLEM THIS SOLVES
-----------------------
A UEX terminal names its position with eight integers::

    {"id_star_system": 68, "id_planet": 4, "id_orbit": 326, "id_moon": 0,
     "id_space_station": 1, "id_outpost": 0, "id_poi": 0, "id_city": 0, ...}

Zero means "not applicable", not "unknown", and the levels that are zero differ
per branch: a Lagrange station has a planet and no moon, a mining outpost has a
moon and no station, a city has neither. There is no fixed ladder to walk.

So resolution is: take the MOST SPECIFIC level the record actually names, and
build the readable string by walking that row's parents upward.

WHY THIS IS NOT A ONE-LINER, AND WHY IT HAS ITS OWN CONTROL
------------------------------------------------------------
The failure this guards against is emitting the literal text ``None`` — or
``0``, or ``ARC-L1, None, Stanton`` — into a location string on a live page.
That is exactly the class of thing that looks fine in the happy path and ships
broken, because the happy path (Area 18: city -> planet -> system, every level
present) never exercises a gap. Every function here is written so that a
missing level is SKIPPED, never rendered, and checks/_verify_location_hierarchy.py
proves it by feeding gaps in deliberately.

Rule 11 applies to the unresolvable case: `id_orbit` cannot be resolved from
the 20260801T235530Z snapshot because it holds no orbits.json. An orbit is
therefore never named and never guessed — it is preserved as an id in `detail`
and omitted from the readable string.
"""

from __future__ import annotations

# Least to most specific. Mirrors app.models.LOCATION_KINDS and is asserted
# against it in checks/_verify_location_hierarchy.py, so the two cannot drift.
KIND_BY_UEX_FIELD = (
    ("id_star_system", "star_system"),
    ("id_planet", "planet"),
    ("id_orbit", "orbit"),
    ("id_moon", "moon"),
    ("id_space_station", "space_station"),
    ("id_outpost", "outpost"),
    ("id_poi", "poi"),
    ("id_city", "city"),
)

# Kinds this project can name from the snapshots it holds. `orbit` and `poi`
# are deliberately absent: terminals reference them, and no endpoint in
# 20260801T235530Z resolves them. Selecting an unresolvable kind as a
# terminal's location would produce a row pointing at nothing, so the resolver
# steps past them to the deepest level it can actually name.
RESOLVABLE_KINDS = frozenset(
    {"star_system", "planet", "moon", "space_station", "outpost", "city"}
)

# Separator for the readable string, most specific first:
#   "ARC-L1 Wide Forest Station, ArcCorp, Stanton"
PATH_SEPARATOR = ", "

# How deep a parent walk may go before we call it a cycle. The real hierarchy
# is six levels; anything past this is corrupt data, and a resolver that spins
# forever on it is worse than one that reports the corruption.
MAX_DEPTH = 16


def _clean(value) -> str | None:
    """A name we are willing to print, or None.

    Rejects None, non-strings, empty strings, whitespace, and the literal
    strings "None"/"null"/"0" — UEX and several intermediate JSON layers all
    stringify absence differently, and every one of those has shown up in this
    project's data at least once.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    if not value or value.lower() in {"none", "null", "0", "-"}:
        return None
    return value


def most_specific_reference(record: dict) -> tuple[str, int] | None:
    """The (kind, uex_id) a UEX record most specifically sits at.

    Walks KIND_BY_UEX_FIELD backwards — most specific first — and returns the
    first level that is both non-zero and resolvable. Returns None when the
    record names no resolvable level at all, which is a real case and is
    reported by the importer rather than defaulted to a system.
    """
    for field, kind in reversed(KIND_BY_UEX_FIELD):
        if kind not in RESOLVABLE_KINDS:
            continue
        raw = record.get(field)
        try:
            uex_id = int(raw) if raw is not None else 0
        except (TypeError, ValueError):
            # A non-numeric id is corrupt, not a location. Skip rather than
            # crash — the importer counts these and the count reaches the
            # ledger.
            continue
        if uex_id > 0:
            return (kind, uex_id)
    return None


def unresolvable_references(record: dict) -> dict:
    """Non-zero ids for levels this project cannot name, kept as ids.

    Rule 11: the honest form of "we have an orbit id and no orbit table" is to
    keep the number and say what it is, not to drop it and not to invent a
    name for it. The importer puts this dict into Terminal.detail.
    """
    out = {}
    for field, kind in KIND_BY_UEX_FIELD:
        if kind in RESOLVABLE_KINDS:
            continue
        raw = record.get(field)
        try:
            uex_id = int(raw) if raw is not None else 0
        except (TypeError, ValueError):
            continue
        if uex_id > 0:
            out[field] = uex_id
    return out


def resolve_path(location, separator: str = PATH_SEPARATOR) -> str:
    """A readable place string for a Location, most specific first.

    Walks `location.parent` upward, keeps every level that has a printable
    name, and joins them. A level whose name is missing is SKIPPED, never
    rendered — that is the whole point of this function.

    Returns "" (empty string, never "None") when nothing at all is printable.
    An empty string is a display decision the caller can make honestly; the
    string "None" is a lie about a place.
    """
    if location is None:
        return ""

    parts: list[str] = []
    seen: set[int] = set()
    node = location
    depth = 0

    while node is not None and depth < MAX_DEPTH:
        # Cycle guard. A self-parented row would otherwise hang the importer,
        # and rows are parented by an importer reading third-party ids.
        node_key = id(node) if getattr(node, "id", None) is None else node.id
        if node_key in seen:
            break
        seen.add(node_key)

        name = _clean(getattr(node, "name", None))
        if name is not None and name not in parts:
            parts.append(name)

        node = getattr(node, "parent", None)
        depth += 1

    return separator.join(parts)


def resolve_path_from_chain(chain, separator: str = PATH_SEPARATOR) -> str:
    """resolve_path() for an already-materialised list, most specific first.

    The importer builds locations in one pass with a plain dict index and has
    no ORM objects to walk, so it uses this. Same skipping rules, same
    guarantee: no level ever renders as "None".
    """
    parts: list[str] = []
    for node in chain or ():
        name = _clean(getattr(node, "name", None) if not isinstance(node, str) else node)
        if name is not None and name not in parts:
            parts.append(name)
    return separator.join(parts)
