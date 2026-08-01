import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

CONFIDENCE_LEVELS = ("unverified", "low", "medium", "high", "verified")
SHIP_STATUSES = ("purchasable", "pledge_only")


class VerifiableMixin:
    """Common provenance/audit columns shared by every reference table."""

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    verification_source: Mapped[str | None] = mapped_column(String(255))
    confidence: Mapped[str] = mapped_column(
        String(20), server_default="unverified", nullable=False
    )

    @staticmethod
    def confidence_check(table_name: str) -> CheckConstraint:
        return CheckConstraint(
            f"confidence IN {CONFIDENCE_LEVELS}",
            name=f"ck_{table_name}_confidence_valid",
        )


class Patch(VerifiableMixin, Base):
    __tablename__ = "patches"
    __table_args__ = (VerifiableMixin.confidence_check("patches"),)

    version: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255))
    released_on: Mapped[datetime.date | None] = mapped_column(Date)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )


class System(VerifiableMixin, Base):
    __tablename__ = "systems"
    __table_args__ = (VerifiableMixin.confidence_check("systems"),)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(20))
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )


class Manufacturer(VerifiableMixin, Base):
    __tablename__ = "manufacturers"
    __table_args__ = (VerifiableMixin.confidence_check("manufacturers"),)

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(20))
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )


class Ship(VerifiableMixin, Base):
    __tablename__ = "ships"
    __table_args__ = (
        VerifiableMixin.confidence_check("ships"),
        CheckConstraint(
            f"status IN {SHIP_STATUSES}", name="ck_ships_status_valid"
        ),
        Index(
            "ix_ships_name_trgm", "name",
            postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
        ),
        Index(
            "ix_ships_role_trgm", "role",
            postgresql_using="gin", postgresql_ops={"role": "gin_trgm_ops"},
        ),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), nullable=False, index=True
    )
    role: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    manufacturer: Mapped["Manufacturer"] = relationship()
    dealer_listings: Mapped[list["ShipDealerListing"]] = relationship()
    pledge_links: Mapped[list["PledgeLink"]] = relationship()
    verified_patch: Mapped["Patch | None"] = relationship()


class Dealer(VerifiableMixin, Base):
    __tablename__ = "dealers"
    __table_args__ = (VerifiableMixin.confidence_check("dealers"),)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    system_id: Mapped[int | None] = mapped_column(ForeignKey("systems.id"))
    location: Mapped[str | None] = mapped_column(String(200))
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )


class ShipDealerListing(VerifiableMixin, Base):
    __tablename__ = "ship_dealer_listings"
    __table_args__ = (
        UniqueConstraint("ship_id", "dealer_id", name="uq_ship_dealer"),
        VerifiableMixin.confidence_check("ship_dealer_listings"),
    )

    ship_id: Mapped[int] = mapped_column(ForeignKey("ships.id"), nullable=False, index=True)
    dealer_id: Mapped[int] = mapped_column(ForeignKey("dealers.id"), nullable=False, index=True)
    in_game_price_auec: Mapped[int | None] = mapped_column()
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    dealer: Mapped["Dealer"] = relationship()


class PledgeLink(VerifiableMixin, Base):
    __tablename__ = "pledge_links"
    __table_args__ = (VerifiableMixin.confidence_check("pledge_links"),)

    ship_id: Mapped[int] = mapped_column(ForeignKey("ships.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    price_usd: Mapped[float | None] = mapped_column(Numeric(10, 2))
    warbond: Mapped[bool | None] = mapped_column()
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )


# ---------------------------------------------------------------------------
# Ship Items domain — mountable ship components (weapons, missiles, missile
# racks, gimbal mounts, turrets). Class Table Inheritance per
# docs/ARCHITECTURE_DECISIONS.md section 1 (LOCKED): a shared `components`
# base table holds common fields, with one 1:1 typed detail table per
# category. Hardpoint/loadout mount references (Priority 9, not built yet)
# will point at `components.id` — never at a typed detail table — so any
# component can occupy any compatible hardpoint without a schema change.
#
# Ship paints are a deliberately SEPARATE sibling table in this same Ship
# Items domain, not part of this base table — see the architecture doc for
# why (a hardpoint FK must not be able to reference a paint).
#
# Component category taxonomy is a lookup table (`component_types`), not a
# hardcoded enum/free-text column, so adding shields/coolers/power plants/
# quantum drives later is a data insert, not a migration.
# ---------------------------------------------------------------------------


class ComponentType(Base):
    """Lookup table for component categories (weapon, missile, missile_rack,
    gimbal_mount, turret, ...). Deliberately NOT a VerifiableMixin table -
    this is app-owned taxonomy, not community-sourced ship data."""

    __tablename__ = "component_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class Component(VerifiableMixin, Base):
    """Shared base table for every ship-mountable component, regardless of
    category. Common fields only - category-specific stats live in the
    matching *_details table joined 1:1 by this row's id."""

    __tablename__ = "components"
    __table_args__ = (
        VerifiableMixin.confidence_check("components"),
        UniqueConstraint("class_name", name="uq_components_class_name"),
    )

    component_type_id: Mapped[int] = mapped_column(
        ForeignKey("component_types.id"), nullable=False, index=True
    )
    manufacturer_id: Mapped[int | None] = mapped_column(
        ForeignKey("manufacturers.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    # In-game internal class name (e.g. "MRCK_S03_BEHR_Dual_S02") - not
    # always known yet, but when present it's the natural key importers
    # upsert on (per ARCHITECTURE_DECISIONS.md section 2's pipeline contract)
    # and it's unique per Star Citizen's own data model.
    class_name: Mapped[str | None] = mapped_column(String(150))
    size: Mapped[int | None] = mapped_column()
    grade: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component_type: Mapped["ComponentType"] = relationship()
    manufacturer: Mapped["Manufacturer | None"] = relationship()
    # Bug found 2026-07-30 running the API layer against real data: this
    # relationship was missing even though the FK column has always been
    # here (importer only ever set the raw column, never read the
    # relationship, so it went unnoticed). Ship has the equivalent
    # `verified_patch` relationship on the same last_verified_patch pattern -
    # added here to match, since the component API needs to resolve the FK
    # to a human-readable patch version string.
    verified_patch: Mapped["Patch | None"] = relationship()
    weapon_detail: Mapped["WeaponDetail | None"] = relationship(
        back_populates="component", cascade="all, delete-orphan", uselist=False
    )
    missile_detail: Mapped["MissileDetail | None"] = relationship(
        back_populates="component", cascade="all, delete-orphan", uselist=False
    )
    missile_rack_detail: Mapped["MissileRackDetail | None"] = relationship(
        back_populates="component", cascade="all, delete-orphan", uselist=False
    )
    gimbal_mount_detail: Mapped["GimbalMountDetail | None"] = relationship(
        back_populates="component", cascade="all, delete-orphan", uselist=False
    )
    turret_detail: Mapped["TurretDetail | None"] = relationship(
        back_populates="component", cascade="all, delete-orphan", uselist=False
    )


class WeaponDetail(Base):
    """Typed detail table for component_type='weapon' (the gun itself -
    ballistic/energy/distortion cannons and repeaters, fixed or gimballed)."""

    __tablename__ = "weapon_details"

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    damage_type: Mapped[str | None] = mapped_column(String(30))  # ballistic/energy/distortion/plasma
    fire_mode: Mapped[str | None] = mapped_column(String(30))  # sustained/burst/charge
    rpm: Mapped[int | None] = mapped_column()
    damage_per_shot: Mapped[float | None] = mapped_column(Numeric(10, 2))
    dps: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ammo_capacity: Mapped[int | None] = mapped_column()
    velocity_mps: Mapped[float | None] = mapped_column(Numeric(10, 2))
    range_m: Mapped[float | None] = mapped_column(Numeric(10, 2))

    component: Mapped["Component"] = relationship(back_populates="weapon_detail")


class MissileDetail(Base):
    """Typed detail table for component_type='missile' (the ordnance itself,
    not the rack that launches it)."""

    __tablename__ = "missile_details"

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    damage: Mapped[float | None] = mapped_column(Numeric(10, 2))
    guidance_type: Mapped[str | None] = mapped_column(String(30))  # ir/em/cross_section/none
    tracking_range_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    lock_time_s: Mapped[float | None] = mapped_column(Numeric(6, 2))
    speed_mps: Mapped[float | None] = mapped_column(Numeric(10, 2))

    component: Mapped["Component"] = relationship(back_populates="missile_detail")


class MissileRackDetail(Base):
    """Typed detail table for component_type='missile_rack' (the launcher
    hardware, distinct from the missiles it holds). native_missile_size and
    missile_capacity together describe what this specific rack SKU carries -
    e.g. a rack mounted at a Size 3 hardpoint may itself be a
    native_missile_size=2, missile_capacity=2 rack (confirmed real for the
    Arrow's wing-root mounts, see data-layer/raw/arrow/arrow_api_raw.json).
    Whether OTHER rack SKUs exist for the same hardpoint (e.g. a
    native_missile_size=3, missile_capacity=1 alternative) is Loadout System/
    hardpoint-compatibility territory (Priority 9, deliberately deferred) -
    this table only describes the rack item itself, not hardpoint fit."""

    __tablename__ = "missile_rack_details"

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    native_missile_size: Mapped[int | None] = mapped_column()
    missile_capacity: Mapped[int | None] = mapped_column()

    component: Mapped["Component"] = relationship(back_populates="missile_rack_detail")


class GimbalMountDetail(Base):
    """Typed detail table for component_type='gimbal_mount' (an accessory
    item installed between a weapon and its hardpoint - e.g. "VariPuck S3
    Gimbal Mount"). Per docs/HARDPOINT_MOUNT_TYPES.md, a gimbal mount only
    accepts a weapon smaller than its own size (a Size 3 gimbal takes a
    Size 2 or smaller gun) - accepts_weapon_size records that reduced size
    for this specific mount SKU."""

    __tablename__ = "gimbal_mount_details"

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    accepts_weapon_size: Mapped[int | None] = mapped_column()

    component: Mapped["Component"] = relationship(back_populates="gimbal_mount_detail")


class TurretDetail(Base):
    """Typed detail table for component_type='turret' (a separate rotating
    mount - manned or remote - mechanically distinct from a fixed/gimbal
    position, per docs/HARDPOINT_MOUNT_TYPES.md). weapon_slots x
    slot_weapon_size describes what this turret SKU holds - e.g. the
    Arrow's default top turret is weapon_slots=2, slot_weapon_size=1,
    manned=False."""

    __tablename__ = "turret_details"

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    weapon_slots: Mapped[int | None] = mapped_column()
    slot_weapon_size: Mapped[int | None] = mapped_column()
    manned: Mapped[bool | None] = mapped_column()

    component: Mapped["Component"] = relationship(back_populates="turret_detail")
