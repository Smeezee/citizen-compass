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
