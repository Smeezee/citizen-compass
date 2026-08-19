"""
The shop and price API - Phase D of the 2026-08-19 order.

    D1  generic list + filter + detail over Terminal, ShopItem, ItemCategory
    D2  item -> every terminal selling it
    D3  terminal -> what it sells
    D4  search by name substring, category, price range

THE LOCKED CONTRACT
-------------------
D1 asks to lock the response envelope "now, in writing, before there are three
consumers of it". The envelope is `app.schemas.Page`, which was already locked
by ARCHITECTURE_DECISIONS section 3 - a second one for these endpoints would
hand the site two pagination conventions to remember, which is exactly what
locking one is meant to prevent. The full contract, including why `total`
ignores limit/offset and why ordering always carries a unique tiebreaker, is
written out at the top of the shop section in app/schemas.py.

IDENTIFIERS, AND WHY THIS IS NOT JUST "look it up by uuid"
-----------------------------------------------------------
§D2 says "item uuid -> every terminal selling it". Taken literally that
endpoint cannot work for this data, for the reasons measured at A4:

    2,162 of 7,932 items have NO uuid       -> unreachable by uuid
    120 uuids are shared by up to 10 items  -> ambiguous by uuid

So `{identifier}` accepts EITHER a uuid or a UEX item id, and the ambiguous
case is handled explicitly rather than by picking one:

    unknown identifier      -> 404, naming what was tried
    uuid matching 1 item    -> 200
    uuid matching N items   -> 409 CONFLICT, listing every candidate with its
                               uex_id, so the caller can re-ask unambiguously

A 409 there is the whole point. Returning the first match would be the silent
version of the same bug the uuid collision causes upstream, and this layer is
the last place it can be caught before it reaches a page.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (  # noqa: F401
    SHOP_ITEM_SOURCE_KINDS,
    ItemCategory,
    ItemPrice,
    Location,
    ShopItem,
    Snapshot,
    Terminal,
)
from app.schemas import (
    ItemCategoryOut,
    ItemPricesOut,
    Page,
    PriceAtTerminalOut,
    SearchResultOut,
    ShopItemOut,
    TerminalInventoryOut,
    TerminalItemOut,
    TerminalOut,
)

router = APIRouter(prefix="/api/v1/shop", tags=["shop"])

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


def _clamp(limit: int) -> int:
    """Bound the page size, and return what was ACTUALLY applied.

    The response echoes this rather than the requested value, so a caller who
    asks for 5,000 rows is told they got 200 instead of quietly receiving a
    short page and concluding there is no more data.
    """
    return max(1, min(limit, MAX_LIMIT))


def _iso(value):
    return value.isoformat() if value is not None else None


# ---------------------------------------------------------------------------
# D1 - list + filter + detail over the three simple entities
# ---------------------------------------------------------------------------

@router.get("/categories", response_model=Page[ItemCategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    section: str | None = Query(None, description="exact section, e.g. 'Armor'"),
    is_game_related: bool | None = Query(None),
    is_mining: bool | None = Query(None),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    offset: int = Query(0, ge=0),
):
    limit = _clamp(limit)
    query = db.query(ItemCategory)
    if section is not None:
        query = query.filter(ItemCategory.section == section)
    if is_game_related is not None:
        query = query.filter(ItemCategory.is_game_related.is_(is_game_related))
    if is_mining is not None:
        query = query.filter(ItemCategory.is_mining.is_(is_mining))

    total = query.count()
    rows = (
        query.order_by(ItemCategory.section, ItemCategory.name, ItemCategory.id)
        .limit(limit).offset(offset).all()
    )
    return Page[ItemCategoryOut](
        items=[ItemCategoryOut.model_validate(r) for r in rows],
        total=total, limit=limit, offset=offset,
    )


@router.get("/terminals", response_model=Page[TerminalOut])
def list_terminals(
    db: Session = Depends(get_db),
    type: str | None = Query(None, description="terminal type, e.g. 'item'"),
    star_system: str | None = Query(None, description="star system name"),
    is_available: bool | None = Query(None),
    name: str | None = Query(None, description="case-insensitive substring"),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    offset: int = Query(0, ge=0),
):
    limit = _clamp(limit)
    query = db.query(Terminal)
    if type is not None:
        query = query.filter(Terminal.type == type)
    if is_available is not None:
        query = query.filter(Terminal.is_available.is_(is_available))
    if name:
        query = query.filter(Terminal.name.ilike(f"%{name}%"))
    if star_system:
        query = (
            query.join(Location, Terminal.star_system_id == Location.id)
            .filter(Location.name.ilike(star_system))
        )

    total = query.count()
    # Terminal names collide (20 of 803), so id is the tiebreaker. Without it
    # pagination silently repeats and skips rows across pages.
    rows = query.order_by(Terminal.name, Terminal.id).limit(limit).offset(offset).all()
    return Page[TerminalOut](
        items=[TerminalOut.model_validate(r) for r in rows],
        total=total, limit=limit, offset=offset,
    )


@router.get("/terminals/{uex_id}", response_model=TerminalOut)
def get_terminal(uex_id: int, db: Session = Depends(get_db)):
    row = db.query(Terminal).filter(Terminal.uex_id == uex_id).one_or_none()
    if row is None:
        raise HTTPException(404, f"no terminal with uex_id {uex_id}")
    return TerminalOut.model_validate(row)


@router.get("/items", response_model=Page[ShopItemOut])
def list_items(
    db: Session = Depends(get_db),
    category: str | None = Query(None, description="exact category name"),
    section: str | None = Query(None),
    source_kind: str | None = Query(None, description="'item' or 'commodity'"),
    name: str | None = Query(None, description="case-insensitive substring"),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    offset: int = Query(0, ge=0),
):
    limit = _clamp(limit)
    query = db.query(ShopItem)
    if category is not None:
        query = query.filter(ShopItem.category_name == category)
    if section is not None:
        query = query.filter(ShopItem.section == section)
    if source_kind is not None:
        query = query.filter(ShopItem.source_kind == source_kind)
    if name:
        query = query.filter(ShopItem.name.ilike(f"%{name}%"))

    total = query.count()
    rows = query.order_by(ShopItem.name, ShopItem.id).limit(limit).offset(offset).all()
    return Page[ShopItemOut](
        items=[ShopItemOut.model_validate(r) for r in rows],
        total=total, limit=limit, offset=offset,
    )


# ---------------------------------------------------------------------------
# identifier resolution, shared by D2
# ---------------------------------------------------------------------------

def _resolve_item(db: Session, identifier: str,
                  source_kind: str | None = None) -> ShopItem:
    """One item from a uuid or a UEX id, or a precise HTTP error.

    Never returns "the first match".

    THREE ACCEPTED FORMS, and the third exists because testing the running
    API found the first one ambiguous:

        "926"           a UEX id. AMBIGUOUS ON ITS OWN - the real key is
                        (source_kind, uex_id), and 200 of the 204 commodity
                        ids collide with item ids. `GET /items/1/prices`
                        matches BOTH the "Omnisky III Cannon" (item 1) and
                        "Agricium" (commodity 1).
        "item:926"      the key, written out. Unambiguous.
        "<uuid>"        a uuid. Unambiguous only if nothing else wears it,
                        which is untrue for 120 of them.

    `?source_kind=` does the same job as the prefix, for callers who would
    rather pass it as a parameter than build a compound path segment.

    Anything still ambiguous after all that gets a 409 listing every
    candidate - with advice that depends on WHICH form was ambiguous, because
    telling someone who already passed a uex_id to "re-request by uex_id" is
    worse than saying nothing.
    """
    query = db.query(ShopItem)
    tried = identifier
    prefix_used = False

    # "item:926" / "commodity:1"
    if ":" in identifier:
        head, _, tail = identifier.partition(":")
        if head in SHOP_ITEM_SOURCE_KINDS:
            source_kind, identifier, prefix_used = head, tail, True

    if source_kind is not None:
        if source_kind not in SHOP_ITEM_SOURCE_KINDS:
            raise HTTPException(
                422,
                f"source_kind must be one of {list(SHOP_ITEM_SOURCE_KINDS)}, "
                f"got {source_kind!r}",
            )
        query = query.filter(ShopItem.source_kind == source_kind)

    candidates = []
    if identifier.isdigit():
        candidates = query.filter(ShopItem.uex_id == int(identifier)).all()
    if not candidates:
        candidates = query.filter(ShopItem.uuid == identifier).all()

    if not candidates:
        raise HTTPException(
            404,
            f"no item matches {tried!r}"
            + (f" with source_kind={source_kind!r}" if source_kind else "")
            + ". Tried it as a UEX item id and as a uuid. Note that 2,162 of "
              "this dataset's items carry no uuid at all and can only be "
              "addressed by uex_id.",
        )

    if len(candidates) > 1:
        by_kind = {c.source_kind for c in candidates}
        if len(by_kind) > 1 and not prefix_used and source_kind is None:
            advice = (
                f"This is a source_kind collision, not a uuid one: UEX numbers "
                f"commodities in a separate id space and 200 of the 204 "
                f"commodity ids also exist as item ids. Re-request as "
                f"'item:{identifier}' or 'commodity:{identifier}', or pass "
                f"?source_kind="
            )
        else:
            advice = (
                "This dataset has 120 uuids worn by up to ten different "
                "products, so no single item can be returned. Re-request by "
                "uex_id, using the uex_id of the candidate you meant."
            )
        raise HTTPException(
            409,
            {
                "error": "ambiguous identifier",
                "detail": f"{len(candidates)} items match {tried!r}. {advice}",
                "candidates": [
                    {"uex_id": c.uex_id, "name": c.name,
                     "category": c.category_name, "source_kind": c.source_kind}
                    for c in candidates
                ],
            },
        )

    return candidates[0]


# ---------------------------------------------------------------------------
# D2 - item -> every terminal selling it
# ---------------------------------------------------------------------------

@router.get("/items/{identifier}/prices", response_model=ItemPricesOut)
def item_prices(
    identifier: str,
    db: Session = Depends(get_db),
    source_kind: str | None = Query(
        None, description="'item' or 'commodity' - disambiguates a uex_id "
                          "that exists in both id spaces"),
):
    item = _resolve_item(db, identifier, source_kind)

    rows = (
        db.query(ItemPrice, Terminal, Snapshot)
        .join(Terminal, ItemPrice.terminal_id == Terminal.id)
        .join(Snapshot, ItemPrice.snapshot_id == Snapshot.id)
        .filter(ItemPrice.shop_item_id == item.id)
        # Cheapest buy first, but nulls last - a terminal that does not sell
        # the item must not sort to the top of a "where is this cheapest"
        # list just because its buy price is absent.
        .order_by(ItemPrice.price_buy.asc().nullslast(), Terminal.name,
                  ItemPrice.id)
        .all()
    )

    prices = [
        PriceAtTerminalOut(
            terminal_id=terminal.id,
            terminal_uex_id=terminal.uex_id,
            terminal_name=terminal.name,
            terminal_type=terminal.type,
            location=terminal.resolved_path,
            price_buy=price.price_buy,
            price_sell=price.price_sell,
            snapshot_key=snapshot.snapshot_key,
            snapshot_captured_at=_iso(snapshot.captured_at),
            source_date_modified=_iso(price.source_date_modified),
            last_verified_patch=item.last_verified_patch,
        )
        for price, terminal, snapshot in rows
    ]

    return ItemPricesOut(
        item=ShopItemOut.model_validate(item),
        prices=prices,
        price_count=len(prices),
        # Stated outright rather than left for the caller to infer from an
        # empty list. §3.6 - absence is data, and "nobody sells this" is an
        # answer the site must be able to give.
        sold_anywhere=bool(prices),
    )


# ---------------------------------------------------------------------------
# D3 - terminal -> what it sells
# ---------------------------------------------------------------------------

@router.get("/terminals/{uex_id}/inventory", response_model=TerminalInventoryOut)
def terminal_inventory(
    uex_id: int,
    db: Session = Depends(get_db),
    category: str | None = Query(None),
    source_kind: str | None = Query(None),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    offset: int = Query(0, ge=0),
):
    limit = _clamp(limit)
    terminal = db.query(Terminal).filter(Terminal.uex_id == uex_id).one_or_none()
    if terminal is None:
        raise HTTPException(404, f"no terminal with uex_id {uex_id}")

    query = (
        db.query(ItemPrice, ShopItem, Snapshot)
        .join(ShopItem, ItemPrice.shop_item_id == ShopItem.id)
        .join(Snapshot, ItemPrice.snapshot_id == Snapshot.id)
        .filter(ItemPrice.terminal_id == terminal.id)
    )
    if category is not None:
        query = query.filter(ShopItem.category_name == category)
    if source_kind is not None:
        query = query.filter(ShopItem.source_kind == source_kind)

    total = query.count()
    rows = (
        query.order_by(ShopItem.name, ShopItem.id, ItemPrice.id)
        .limit(limit).offset(offset).all()
    )

    return TerminalInventoryOut(
        terminal=TerminalOut.model_validate(terminal),
        items=[
            TerminalItemOut(
                item_id=item.id,
                item_uex_id=item.uex_id,
                item_uuid=item.uuid,
                item_name=item.name,
                source_kind=item.source_kind,
                category_name=item.category_name,
                section=item.section,
                price_buy=price.price_buy,
                price_sell=price.price_sell,
                snapshot_key=snapshot.snapshot_key,
                source_date_modified=_iso(price.source_date_modified),
                last_verified_patch=item.last_verified_patch,
            )
            for price, item, snapshot in rows
        ],
        total=total, limit=limit, offset=offset,
    )


# ---------------------------------------------------------------------------
# D4 - search
# ---------------------------------------------------------------------------

@router.get("/search", response_model=Page[SearchResultOut])
def search(
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="case-insensitive name substring"),
    category: str | None = Query(None),
    section: str | None = Query(None),
    source_kind: str | None = Query(None),
    min_price: int | None = Query(None, ge=0, description="min BUY price, aUEC"),
    max_price: int | None = Query(None, ge=0, description="max BUY price, aUEC"),
    priced_only: bool = Query(False, description="exclude items nobody sells"),
    limit: int = Query(DEFAULT_LIMIT, ge=1),
    offset: int = Query(0, ge=0),
):
    limit = _clamp(limit)

    if (min_price is not None and max_price is not None
            and min_price > max_price):
        raise HTTPException(
            422,
            f"min_price ({min_price}) is above max_price ({max_price}), which "
            f"can never match anything. Refusing rather than returning an "
            f"empty result that looks like 'nothing is priced in that range'.",
        )

    # Aggregate prices per item first. A RANGE, never an average - §3.1.
    price_agg = (
        select(
            ItemPrice.shop_item_id.label("item_id"),
            func.count(func.distinct(ItemPrice.terminal_id)).label("terminals"),
            func.min(ItemPrice.price_buy).label("buy_min"),
            func.max(ItemPrice.price_buy).label("buy_max"),
            func.min(ItemPrice.price_sell).label("sell_min"),
            func.max(ItemPrice.price_sell).label("sell_max"),
        )
        .group_by(ItemPrice.shop_item_id)
        .subquery()
    )

    query = db.query(ShopItem, price_agg).outerjoin(
        price_agg, price_agg.c.item_id == ShopItem.id
    )

    if q:
        query = query.filter(
            or_(ShopItem.name.ilike(f"%{q}%"), ShopItem.slug.ilike(f"%{q}%"))
        )
    if category is not None:
        query = query.filter(ShopItem.category_name == category)
    if section is not None:
        query = query.filter(ShopItem.section == section)
    if source_kind is not None:
        query = query.filter(ShopItem.source_kind == source_kind)
    if priced_only:
        query = query.filter(price_agg.c.item_id.isnot(None))
    # A price filter implicitly requires a price. An item nobody sells cannot
    # satisfy "costs under 5,000 aUEC", and including it with nulls would be
    # a row the caller has to filter out themselves.
    if min_price is not None:
        query = query.filter(price_agg.c.buy_max >= min_price)
    if max_price is not None:
        query = query.filter(price_agg.c.buy_min <= max_price)

    total = query.count()
    rows = (
        query.order_by(ShopItem.name, ShopItem.id).limit(limit).offset(offset).all()
    )

    return Page[SearchResultOut](
        items=[
            SearchResultOut(
                item=ShopItemOut.model_validate(row[0]),
                terminal_count=row[2] or 0,
                price_buy_min=row[3],
                price_buy_max=row[4],
                price_sell_min=row[5],
                price_sell_max=row[6],
            )
            for row in rows
        ],
        total=total, limit=limit, offset=offset,
    )
