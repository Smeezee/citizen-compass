from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated-list envelope. Locked as the standard shape for
    every new list endpoint per docs/ARCHITECTURE_DECISIONS.md section 3 -
    total/limit/offset are always present so a client can page reliably
    without guessing at conventions per-endpoint.

    Deliberately NOT retrofitted onto the existing `/api/v1/ships`,
    `/api/v1/dealers`, `/api/v1/manufacturers` endpoints in this pass -
    those are already-live endpoints outside tonight's explicit scope, and
    changing their response shape needs a deliberate decision, not a side
    effect of adding new ones. Flagged in the handoff for that call.
    """

    items: list[T]
    total: int
    limit: int
    offset: int


class ManufacturerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str | None


class DealerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str | None


class ShipOut(BaseModel):
    id: int
    name: str
    manufacturer: str
    role: str | None
    notes: str | None
    status: Literal["purchasable", "pledge_only"]
    auec_price: int | None
    dealers: list[str]
    pledge_price_usd: float | None
    pledge_url: str | None
    confidence: str
    last_verified_patch: str | None


# ---------------------------------------------------------------------------
# Ship Items domain - response models for the generic component router
# factory (app/routers/component_factory.py). Fields here are a 1:1 mirror
# of the actual columns on `components` + the matching typed detail table
# (app/models.py) - no speculative/derived fields added just to look
# complete. Detail fields are `| None` even though every real row is
# expected to have exactly one matching detail row, because a data-quality
# gap (missing detail row) should serialize as nulls, not a 500 - the
# Step 3 auditor is what's responsible for flagging that gap, not the API.
# ---------------------------------------------------------------------------


class ComponentBaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    class_name: str | None
    size: int | None
    grade: str | None
    manufacturer: str | None
    notes: str | None
    confidence: str
    last_verified_patch: str | None


class WeaponOut(ComponentBaseOut):
    damage_type: str | None
    fire_mode: str | None
    rpm: int | None
    damage_per_shot: float | None
    dps: float | None
    ammo_capacity: int | None
    velocity_mps: float | None
    range_m: float | None


class MissileOut(ComponentBaseOut):
    damage: float | None
    guidance_type: str | None
    tracking_range_m: float | None
    lock_time_s: float | None
    speed_mps: float | None


class TurretOut(ComponentBaseOut):
    weapon_slots: int | None
    slot_weapon_size: int | None
    manned: bool | None


# ---------------------------------------------------------------------------
# Shop and price layer (Phase D, 2026-08-19).
#
# THE RESPONSE ENVELOPE IS `Page`, ABOVE. D1 asks to "lock the response
# envelope and pagination format now, in writing, before there are three
# consumers of it" - and the right way to do that turned out to be to NOT
# invent one. `Page` is already locked by ARCHITECTURE_DECISIONS section 3 and
# already carries total/limit/offset. A second envelope for the shop endpoints
# would give the site two pagination conventions to remember, which is the
# thing locking one is supposed to prevent.
#
# So the locked contract for every shop list endpoint is:
#
#     {"items": [...], "total": <int>, "limit": <int>, "offset": <int>}
#
#     total   - rows matching the filter, IGNORING limit/offset. A client can
#               compute page count from it without fetching anything.
#     limit   - what was actually applied, not what was asked for. Requests
#               above MAX_LIMIT are clamped, and the response says so rather
#               than silently returning fewer rows than the caller thinks.
#     offset  - echoed back, so a response is interpretable on its own.
#
# Ordering is ALWAYS deterministic and always includes a unique tiebreaker.
# Paginating an unordered query silently repeats and skips rows, and it looks
# fine until someone reads page 4.
#
# PRICES: buy and sell are ALWAYS separate fields and either may be null.
# null means "no data" and is never rendered as 0 (§3.1). There is deliberately
# no combined or averaged price field anywhere in these schemas - the surest
# way to never show an average as a price is for the API to not have one.
# ---------------------------------------------------------------------------


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    kind: str
    name: str
    # The readable place, most specific first: "ARC-L1 Wide Forest Station,
    # ArcCorp, Stanton". Never contains a "None" segment - a missing level is
    # skipped rather than rendered.
    resolved_path: str | None


class ItemCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uex_id: int
    section: str | None
    name: str
    is_game_related: bool | None
    is_mining: bool | None


class TerminalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uex_id: int
    name: str
    nickname: str | None
    code: str | None
    type: str | None
    resolved_path: str | None
    company_name: str | None
    is_available: bool | None
    last_verified_patch: int | None
    # Standing rule: the front end flags unverified data, so the API has to
    # hand it something to flag on.
    confidence: str


class ShopItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uex_id: int
    source_kind: str
    # Present but NOT an identifier. 2,162 items have none and 120 uuids are
    # shared by up to ten items - see A4. Exposed because other UEX-derived
    # data cross-references it.
    uuid: str | None
    name: str
    category_name: str | None
    section: str | None
    company_name: str | None
    vehicle_name: str | None
    size: str | None
    slug: str | None
    url_store: str | None
    last_verified_patch: int | None
    confidence: str


class PriceAtTerminalOut(BaseModel):
    """One terminal's price for one item. D2's row shape."""

    terminal_id: int
    terminal_uex_id: int
    terminal_name: str
    terminal_type: str | None
    location: str | None
    # Separate, always. Either may be null, and null means no data (§3.1).
    price_buy: int | None
    price_sell: int | None
    # Provenance, per E4: every row must be able to show where it came from
    # and how old it is.
    snapshot_key: str
    snapshot_captured_at: str | None
    source_date_modified: str | None
    last_verified_patch: int | None


class ItemPricesOut(BaseModel):
    """D2: one item, and every terminal selling it."""

    item: ShopItemOut
    prices: list[PriceAtTerminalOut]
    # Explicit rather than implied by an empty list. "Nobody sells this" is a
    # real answer (§3.6) and the front end must be able to say it without
    # guessing whether the query failed.
    price_count: int
    sold_anywhere: bool


class TerminalItemOut(BaseModel):
    """One item at one terminal. D3's row shape."""

    item_id: int
    item_uex_id: int
    item_uuid: str | None
    item_name: str
    source_kind: str
    category_name: str | None
    section: str | None
    price_buy: int | None
    price_sell: int | None
    snapshot_key: str
    source_date_modified: str | None
    last_verified_patch: int | None


class TerminalInventoryOut(BaseModel):
    """D3: one terminal, and what it sells."""

    terminal: TerminalOut
    items: list[TerminalItemOut]
    total: int
    limit: int
    offset: int


class SearchResultOut(BaseModel):
    """D4: one search hit, with its price range across all terminals.

    `price_buy_min` / `price_buy_max` are a RANGE, not an average. §3.1 says a
    blended average is never shown as if it were a price, and a range is an
    honest summary of many terminals in a way a mean is not - the two numbers
    are both real prices that really exist somewhere.
    """

    item: ShopItemOut
    terminal_count: int
    price_buy_min: int | None
    price_buy_max: int | None
    price_sell_min: int | None
    price_sell_max: int | None
