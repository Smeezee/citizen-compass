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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

CONFIDENCE_LEVELS = ("unverified", "low", "medium", "high", "verified")
SHIP_STATUSES = ("purchasable", "pledge_only")

# LIFECYCLE_STATUSES answers "does this still exist in the game?".
# SHIP_STATUSES above answers "can you buy it?". They are ORTHOGONAL and must
# never be merged: the Aurora Mk I was pledge_only AND is now retired, and
# collapsing them would lose the ability to say a thing was buyable while it
# existed. "retired AND was purchasable" is a real query.
#
# `unknown` is load-bearing, not a placeholder. An entity that vanished before
# we started sealing snapshots (2026-07-31) must NOT be labelled `retired` - we
# do not know it was retired rather than renamed. Guessing there manufactures
# false history on a site whose whole premise is provenance.
LIFECYCLE_STATUSES = (
    "live",
    "retired",
    "renamed",
    "replaced",
    "never_released",
    "unknown",
)

# How much the reader should trust what is on the page.
#   sealed    - present in a snapshot we hold. Authoritative.
#   external  - from an outside source. Carries a rights question (rule 8).
#   testimony - remembered, never in any file. Cannot be verified against one.
EVIDENCE_TIERS = ("sealed", "external", "testimony")

# CC-12 natural-key fallback. components.class_name is NOT NULL and unique
# because it is what importers upsert on. When a component's real in-game class
# name is genuinely absent upstream, importers must mint a deterministic
# synthetic key rather than leaving the column NULL - a NULL would silently
# re-open the duplicate-row hole the NOT NULL closed, because Postgres allows
# unlimited NULLs under a unique constraint.
#
# Form: CC_SYNTH_<component_type_key>_<slugified name>. Deterministic, so the
# same component yields the same key on every run and upserts idempotently.
# A synthetic key is always visibly synthetic - it is never presented as a real
# in-game identifier, per rule 11.
SYNTHETIC_CLASS_NAME_PREFIX = "CC_SYNTH_"


class ProvenanceMixin:
    """Provenance/audit columns, WITHOUT a primary key.

    Split out of VerifiableMixin 2026-08-01 for CC-10. The detail tables
    (weapon_details, missile_details, ...) key on component_id, so inheriting
    VerifiableMixin directly would add its `id` alongside component_id and
    produce a COMPOSITE primary key ['component_id', 'id'] - and
    Base.metadata.create_all() accepts that silently rather than raising. That
    silent acceptance is itself a rule 12 case: nothing in checks/ touches those
    tables, so no existing check would have caught it.

    Tables that want provenance AND a surrogate id keep using VerifiableMixin,
    which is unchanged. Tables that already have their own primary key use this.
    """

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


class LifecycleMixin:
    """When did this exist, and what happened to it?

    Separate from `last_verified_patch`, which answers "is this current?".
    Preservation needs the other question, and the two are not the same: a row
    can be freshly verified AND describe something CIG removed.

    Why this is a mixin rather than columns on Ship: paints, items and locations
    all need it and none of them have it yet. Writing it once means the next
    table cannot get a subtly different version.
    """

    # Patch VERSION STRINGS (e.g. "4.9"), not FKs to patches.id. A retired
    # entity's last patch may predate any row we hold in `patches`, and a FK
    # would make the honest answer unstorable.
    first_seen_patch: Mapped[str | None] = mapped_column(String(50))
    last_seen_patch: Mapped[str | None] = mapped_column(String(50))

    # Indexed: "show me everything retired" and "show me only what we can
    # prove" are both routine filters, and they get run together.
    lifecycle_status: Mapped[str] = mapped_column(
        String(20), server_default="live", nullable=False, index=True
    )
    evidence_tier: Mapped[str] = mapped_column(
        String(20), server_default="sealed", nullable=False, index=True
    )

    # Citizen Compass's own words, not CIG's. Nullable: most rows never need one.
    removal_note: Mapped[str | None] = mapped_column(Text)

    @staticmethod
    def lifecycle_checks(table_name: str) -> tuple:
        return (
            CheckConstraint(
                f"lifecycle_status IN {LIFECYCLE_STATUSES}",
                name=f"ck_{table_name}_lifecycle_status_valid",
            ),
            CheckConstraint(
                f"evidence_tier IN {EVIDENCE_TIERS}",
                name=f"ck_{table_name}_evidence_tier_valid",
            ),
        )


class VerifiableMixin(ProvenanceMixin):
    """Common provenance/audit columns shared by every reference table.

    ProvenanceMixin plus a surrogate integer primary key. Behaviour is
    identical to before the 2026-08-01 split - every table already using this
    is unaffected.
    """

    id: Mapped[int] = mapped_column(primary_key=True)


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


class Ship(LifecycleMixin, VerifiableMixin, Base):
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
        # CC-12 (2026-08-01): ships had no unique constraint at all, so an
        # importer run twice produced duplicate ships. Both columns are already
        # NOT NULL, so this constraint has no NULL-escape hatch.
        UniqueConstraint(
            "name", "manufacturer_id", name="uq_ships_name_manufacturer_id"
        ),
        # Lifecycle (2026-08-08). Deliberately NOT folded into
        # ck_ships_status_valid: `status` is commercial availability and
        # `lifecycle_status` is existence. A ship can be pledge_only AND
        # retired, and each constraint must reject only its own bad values.
        *LifecycleMixin.lifecycle_checks("ships"),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(
        ForeignKey("manufacturers.id"), nullable=False, index=True
    )
    role: Mapped[str | None] = mapped_column(String(100))
    size: Mapped[str | None] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # Aurora Mk I -> Aurora Mk II. Self-referential and nullable: most ships
    # never have a successor, and a successor may not exist yet when the
    # predecessor is retired.
    successor_id: Mapped[int | None] = mapped_column(
        ForeignKey("ships.id"), nullable=True, index=True
    )
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    manufacturer: Mapped["Manufacturer"] = relationship()
    successor: Mapped["Ship | None"] = relationship(
        "Ship", remote_side="Ship.id", foreign_keys=[successor_id]
    )
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
    # In-game internal class name (e.g. "MRCK_S03_BEHR_Dual_S02"). This is the
    # natural key importers upsert on (per ARCHITECTURE_DECISIONS.md section 2's
    # pipeline contract) and it is unique per Star Citizen's own data model.
    #
    # NOT NULL since CC-12 (2026-08-01). It was previously nullable while
    # sitting under uq_components_class_name, and Postgres permits unlimited
    # NULLs in a unique constraint - so the constraint allowed unlimited
    # duplicate rows on the very field importers dedupe by. Nothing in the
    # pipeline was idempotent: run an importer twice, get two rows.
    #
    # Where the real class name is genuinely not known upstream, the defined
    # fallback is a synthetic key - see SYNTHETIC_CLASS_NAME_PREFIX below.
    # NULL is never the fallback.
    class_name: Mapped[str] = mapped_column(String(150), nullable=False)
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


class WeaponDetail(ProvenanceMixin, Base):
    """Typed detail table for component_type='weapon' (the gun itself -
    ballistic/energy/distortion cannons and repeaters, fixed or gimballed)."""

    __tablename__ = "weapon_details"
    __table_args__ = (ProvenanceMixin.confidence_check("weapon_details"),)

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

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component: Mapped["Component"] = relationship(back_populates="weapon_detail")


class MissileDetail(ProvenanceMixin, Base):
    """Typed detail table for component_type='missile' (the ordnance itself,
    not the rack that launches it)."""

    __tablename__ = "missile_details"
    __table_args__ = (ProvenanceMixin.confidence_check("missile_details"),)

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    damage: Mapped[float | None] = mapped_column(Numeric(10, 2))
    guidance_type: Mapped[str | None] = mapped_column(String(30))  # ir/em/cross_section/none
    tracking_range_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    lock_time_s: Mapped[float | None] = mapped_column(Numeric(6, 2))
    speed_mps: Mapped[float | None] = mapped_column(Numeric(10, 2))

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component: Mapped["Component"] = relationship(back_populates="missile_detail")


class MissileRackDetail(ProvenanceMixin, Base):
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
    __table_args__ = (ProvenanceMixin.confidence_check("missile_rack_details"),)

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    native_missile_size: Mapped[int | None] = mapped_column()
    missile_capacity: Mapped[int | None] = mapped_column()

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component: Mapped["Component"] = relationship(back_populates="missile_rack_detail")


class GimbalMountDetail(ProvenanceMixin, Base):
    """Typed detail table for component_type='gimbal_mount' (an accessory
    item installed between a weapon and its hardpoint - e.g. "VariPuck S3
    Gimbal Mount"). Per docs/HARDPOINT_MOUNT_TYPES.md, a gimbal mount only
    accepts a weapon smaller than its own size (a Size 3 gimbal takes a
    Size 2 or smaller gun) - accepts_weapon_size records that reduced size
    for this specific mount SKU."""

    __tablename__ = "gimbal_mount_details"
    __table_args__ = (ProvenanceMixin.confidence_check("gimbal_mount_details"),)

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    accepts_weapon_size: Mapped[int | None] = mapped_column()

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component: Mapped["Component"] = relationship(back_populates="gimbal_mount_detail")


class TurretDetail(ProvenanceMixin, Base):
    """Typed detail table for component_type='turret' (a separate rotating
    mount - manned or remote - mechanically distinct from a fixed/gimbal
    position, per docs/HARDPOINT_MOUNT_TYPES.md). weapon_slots x
    slot_weapon_size describes what this turret SKU holds - e.g. the
    Arrow's default top turret is weapon_slots=2, slot_weapon_size=1,
    manned=False."""

    __tablename__ = "turret_details"
    __table_args__ = (ProvenanceMixin.confidence_check("turret_details"),)

    component_id: Mapped[int] = mapped_column(
        ForeignKey("components.id", ondelete="CASCADE"), primary_key=True
    )
    weapon_slots: Mapped[int | None] = mapped_column()
    slot_weapon_size: Mapped[int | None] = mapped_column()
    manned: Mapped[bool | None] = mapped_column()

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    component: Mapped["Component"] = relationship(back_populates="turret_detail")


# ---------------------------------------------------------------------------
# Ship registry — declared here 2026-08-02 to close a real hazard.
#
# This table existed in the database but in no SQLAlchemy model, so
# `alembic revision --autogenerate` proposed `remove_table:ship_registry`
# along with three pipeline_* tables — a migration that would have dropped
# 295 registry rows and 3,456 rows of checker findings. Autogenerate output
# looks like ordinary work; nothing in it announces that.
#
# It is domain data — it is what `registry_sync` compares the database
# against — so alembic owns it, per the 2026-08-02 ruling. The DDL below
# mirrors registry-builder/main.go's ensureSchema() exactly; a mismatch
# would make autogenerate propose ALTERs instead of drops, which is quieter
# and equally wrong.
#
# Deliberately NOT a VerifiableMixin table: this is a generated cross-index
# rebuilt from source, not community-sourced ship data with a provenance
# story of its own.
# ---------------------------------------------------------------------------


class ShipRegistry(Base):
    __tablename__ = "ship_registry"

    id: Mapped[int] = mapped_column(primary_key=True)
    ship_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    manufacturer_code: Mapped[str] = mapped_column(String(10), nullable=False)
    manufacturer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    ship_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_slug: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    folder_slug: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Shop and price layer — added 2026-08-19 for
# docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
#
# A1. LOCATION HIERARCHY.
#
# UEX terminals carry eight separate location ids: id_star_system, id_planet,
# id_orbit, id_moon, id_space_station, id_outpost, id_poi, id_city. Every one
# of them is an integer, and UEX uses 0 (not NULL) to mean "not applicable" —
# ARC-L1 Wide Forest Station has id_space_station=1 and id_moon=0, because a
# Lagrange station orbits a planet and never a moon.
#
# WHY ONE SELF-REFERENTIAL TABLE rather than eight tables:
# the levels are not a fixed ladder. A terminal can hang off a city (Area 18),
# an outpost (ArcCorp Mining Area 045), a space station (ARC-L1), a planet, or
# a bare star system, and the levels it skips differ per branch. Eight tables
# would need eight nullable FKs on Terminal and a resolver that knows the
# precedence order anyway; one table with a parent pointer stores the same
# facts and makes "everything under Stanton" a single recursive query.
#
# WHY DENORMALISED ANCESTOR COLUMNS (star_system_id, planet_id) EXIST ANYWAY:
# per §3.9 of the order, anything queried gets a real indexed column. "Show me
# prices in Stanton" is the single most likely filter on this whole layer, and
# making it a recursive CTE every time is the wrong trade. These two are
# maintained by the importer, not by the database, and checks/db_checks.py
# gains an auditor for drift rather than a trigger that hides it.
#
# ORBITS ARE A KNOWN GAP, recorded rather than invented: terminals, planets,
# moons and outposts all carry `id_orbit`, but the 20260801T235530Z snapshot
# contains no orbits.json — UEX was never asked for that endpoint. Orbit ids
# are therefore preserved verbatim in `detail` and NEVER resolved to a name.
# An unresolvable id is stored as the id, never as a guess (rule 11).
# ---------------------------------------------------------------------------

# The kinds of place a terminal can sit at, ordered LEAST to MOST specific.
# The order is load-bearing: resolve_terminal_location() walks it backwards to
# find the most specific level a terminal actually names. "poi" and "orbit" are
# listed because UEX terminals reference them, not because this snapshot can
# resolve them — see the module docstring above.
LOCATION_KINDS = (
    "star_system",
    "planet",
    "orbit",
    "moon",
    "space_station",
    "outpost",
    "poi",
    "city",
)


class Location(VerifiableMixin, Base):
    """One place in the Star Citizen location hierarchy, at any level.

    `kind` says which level this row is; `parent_id` says what it hangs off.
    A row's uex_id is only unique WITHIN its kind — UEX numbers each endpoint
    from 1, so star_system 1 and planet 1 are different places. The unique
    constraint is therefore on the pair, and anything that joins on uex_id
    alone without also matching kind is a bug.
    """

    __tablename__ = "locations"
    __table_args__ = (
        VerifiableMixin.confidence_check("locations"),
        CheckConstraint(
            f"kind IN {LOCATION_KINDS}", name="ck_locations_kind_valid"
        ),
        # See the class docstring: uex_id alone is NOT unique across kinds.
        UniqueConstraint("kind", "uex_id", name="uq_locations_kind_uex_id"),
    )

    uex_id: Mapped[int] = mapped_column(nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str | None] = mapped_column(String(20))
    nickname: Mapped[str | None] = mapped_column(String(200))

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), index=True
    )
    # Denormalised ancestors — see the module comment for why these are real
    # columns. Both are nullable: a star_system row has neither, and a planet
    # row has no planet_id of its own.
    star_system_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), index=True
    )
    planet_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), index=True
    )

    # The readable string, materialised at import so the front end never pays
    # for a parent walk. app.locations.resolve_path() is the single writer of
    # this column and the only definition of the format.
    resolved_path: Mapped[str | None] = mapped_column(Text)

    # Everything UEX sends that this project has not ruled a meaning for —
    # is_available, has_refinery, pad_types, jurisdiction ids, the orbit id.
    # Per §3.5: preserved verbatim, never dropped, never given a guessed column.
    detail: Mapped[dict | None] = mapped_column(JSONB)

    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    parent: Mapped["Location | None"] = relationship(
        "Location", remote_side="Location.id", foreign_keys=[parent_id]
    )
    verified_patch: Mapped["Patch | None"] = relationship()


# ---------------------------------------------------------------------------
# A2. TERMINAL.
#
# The 823 places that actually sell something. UEX calls them terminals and
# gives each one a `type`: measured across the snapshot, that is
#   item 479, commodity 161, fuel 98, vehicle_rent 32, commodity_raw 23,
#   refinery 21, vehicle_buy 9.
#
# WHY `type` IS INDEXED BUT NOT CONSTRAINED TO THOSE SEVEN VALUES:
# a CHECK constraint here would mean that the day UEX adds an eighth terminal
# type, the importer stops dead on a row it could have stored perfectly well.
# That is the wrong failure. §3.8 of the order already rules the pattern for
# this exact situation - `is_game_related = 0` categories are "imported and
# flagged, not skipped" - and an unrecognised terminal type is the same shape
# of problem. So: import it, and let an auditor report it. The constraint that
# WOULD be right here is one that cannot be satisfied by new upstream data, and
# there isn't one.
#
# WHY is_available AND is_available_live ARE REAL COLUMNS while the other
# nineteen is_*/has_* flags are not: those two decide whether a terminal
# appears on the site at all, so they are on every query. `is_refinery`,
# `has_freight_elevator` and the rest are facts nobody has asked a question
# about yet, and §3.9 says JSONB is for exactly that tail.
# ---------------------------------------------------------------------------


class Terminal(VerifiableMixin, Base):
    """A place that buys or sells something, at a resolved location."""

    __tablename__ = "terminals"
    __table_args__ = (
        VerifiableMixin.confidence_check("terminals"),
        # THE key. UEX terminal ids are unique across all types, unlike
        # location ids which are only unique within their endpoint.
        UniqueConstraint("uex_id", name="uq_terminals_uex_id"),
        Index(
            "ix_terminals_name_trgm", "name",
            postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    uex_id: Mapped[int] = mapped_column(nullable=False)

    # UEX ships four different names per terminal and they are not
    # interchangeable: name="Admin - ARC-L1", fullname="Commodity Shop - Admin
    # - ARC-L1", nickname="ARC-L1", displayname="ARC-L1 Wide Forest Station".
    # All four are kept because the site needs different ones in different
    # places, and picking one now would be a guess about a UI that does not
    # exist yet.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fullname: Mapped[str | None] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(255))
    displayname: Mapped[str | None] = mapped_column(String(255))
    code: Mapped[str | None] = mapped_column(String(50))
    type: Mapped[str | None] = mapped_column(String(50), index=True)

    # Nullable even though all 823 rows in this snapshot resolve. A terminal
    # whose location cannot be resolved is a real future case, and the honest
    # storage for it is a NULL plus a finding - not a row silently parented to
    # whatever system happened to be first.
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), index=True
    )
    # Denormalised for "everything in Stanton", same reasoning as Location.
    star_system_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"), index=True
    )
    # Materialised readable place, written by app.locations.resolve_path().
    resolved_path: Mapped[str | None] = mapped_column(Text)

    company_name: Mapped[str | None] = mapped_column(String(255))

    # Whether the site should show this terminal at all - on every query, so a
    # real column rather than a JSONB lookup.
    is_available: Mapped[bool | None] = mapped_column(index=True)
    is_available_live: Mapped[bool | None] = mapped_column()

    # UEX's own last-modified for this terminal, as a real timestamp. C5
    # (staleness) buckets on this, so it is a column and not a JSONB field.
    source_date_modified: Mapped[datetime.datetime | None] = mapped_column(
        index=True
    )

    detail: Mapped[dict | None] = mapped_column(JSONB)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    location: Mapped["Location | None"] = relationship(
        foreign_keys=[location_id]
    )
    star_system: Mapped["Location | None"] = relationship(
        foreign_keys=[star_system_id]
    )
    verified_patch: Mapped["Patch | None"] = relationship()


# ---------------------------------------------------------------------------
# A3. ITEM CATEGORY.
#
# UEX's own taxonomy: 100 rows, each with a `section` that groups them
# ("Armor" contains Arms, Legs, Torso, Undersuit; "Weapons" contains several
# more). The section is a real column and not a separate table because it is
# a plain string on UEX's side with no id of its own - inventing a sections
# table would mean inventing ids UEX does not have, and §3.5 rules against
# giving upstream data a shape it does not actually possess.
#
# `is_game_related = 0` rows are IMPORTED AND FLAGGED, never skipped (§3.8).
# The column is here precisely so that hiding them stays a display decision
# Sleven makes later, rather than a silent data loss decided by an importer.
# ---------------------------------------------------------------------------


class ItemCategory(VerifiableMixin, Base):
    """One of UEX's 100 item categories, e.g. section='Armor', name='Arms'."""

    __tablename__ = "item_categories"
    __table_args__ = (
        VerifiableMixin.confidence_check("item_categories"),
        UniqueConstraint("uex_id", name="uq_item_categories_uex_id"),
    )

    uex_id: Mapped[int] = mapped_column(nullable=False)
    # UEX's `type` field: "item" for nearly all of them. Kept as-is.
    type: Mapped[str | None] = mapped_column(String(50), index=True)
    section: Mapped[str | None] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    # Both indexed: "only things that exist in the game" and "only mining
    # gear" are both routine filters, and C4 groups coverage by them.
    is_game_related: Mapped[bool | None] = mapped_column(index=True)
    is_mining: Mapped[bool | None] = mapped_column(index=True)

    source_date_modified: Mapped[datetime.datetime | None] = mapped_column()
    detail: Mapped[dict | None] = mapped_column(JSONB)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    verified_patch: Mapped["Patch | None"] = relationship()


# ---------------------------------------------------------------------------
# A4. SHOP ITEM.
#
# THE ORDER SAYS "uuid UNIQUE (the join key)". THE DATA SAYS OTHERWISE, AND
# THIS IS THE ONE PLACE IN THE SHOP LAYER WHERE I HAVE NOT DONE AS TOLD.
# Everything below is measured against 20260801T235530Z, not remembered:
#
#   7,728 item rows across the 100 category files
#   7,728 distinct UEX `id` values          <- a perfect key, zero collisions
#   5,566 rows carry a uuid; 2,162 (27.98%) carry NONE
#   5,356 distinct uuids, of which 120 are SHARED BY MORE THAN ONE ITEM
#   worst case: TEN different items share one uuid
#
# The shared ones are not duplicate rows of the same product. uuid
# 7bd374e9-9d2f-4659-94cf-840e79d23b34 is worn by "Attrition-4 Repeater" AND
# "BRRA LaserCannon AP Automated Turret (Point Defense Turret)", across two
# different categories. uuid 0cced6b1-... is worn by "Jericho", "Jericho X"
# and "Jericho XL" - three different guns.
#
# So a UNIQUE constraint on uuid cannot be created against this data at all,
# and joining prices on uuid would do the precise damage §3.2 was written to
# prevent: it MERGES DISTINCT PRODUCTS. Measured both ways -
#
#   items with at least one price row, joined on id:    2,798
#   items with at least one price row, joined on uuid:  2,424
#
# - joining on uuid also silently loses 374 priced items, because a quarter of
# the catalogue has no uuid to join on.
#
# WHAT IS BUILT INSTEAD: `uex_id` is the key and the upsert target. `uuid` is
# kept, indexed, and exposed - it is what other UEX-derived data cross-
# references - but it is never identity. This is the same call CC-12 made for
# components.class_name: the key is the field that is actually unique, and a
# unique constraint over a nullable column is the hole, not the fix.
#
# §3.2's real instruction - "never join on display name" - is untouched and
# still right. Measured there too: 7 display names of 7,721 map to more than
# one item, worst case 2. (The order's "up to 12 records" is not true of items
# in this snapshot; it may well be true of something else.)
#
# REVERSES CHEAPLY: the uuid column is present and indexed. If Sleven wants
# uuid as the key, the 120 collisions are already enumerated by the C3
# auditor and the change is a constraint plus a re-run.
# ---------------------------------------------------------------------------


class ShopItem(VerifiableMixin, Base):
    """One buyable thing. Keyed by UEX's own item id, not by uuid - see above."""

    __tablename__ = "shop_items"
    __table_args__ = (
        VerifiableMixin.confidence_check("shop_items"),
        UniqueConstraint("uex_id", name="uq_shop_items_uex_id"),
        Index(
            "ix_shop_items_name_trgm", "name",
            postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    uex_id: Mapped[int] = mapped_column(nullable=False)

    # Indexed, NOT unique, NOT the key. 28% of rows have none and 120 values
    # are shared by up to ten different items.
    uuid: Mapped[str | None] = mapped_column(String(64), index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("item_categories.id"), index=True
    )
    # UEX ships the category and section as strings on the item too. Kept
    # alongside the FK because they are what the source said, and because a
    # row whose category id does not resolve still knows what it called itself.
    category_name: Mapped[str | None] = mapped_column(String(150))
    section: Mapped[str | None] = mapped_column(String(100), index=True)

    company_name: Mapped[str | None] = mapped_column(String(255))
    vehicle_name: Mapped[str | None] = mapped_column(String(255))
    # A STRING, not an int. UEX sends "1", "" and "S3" in this field depending
    # on the category, and coercing that to an integer would either crash or
    # invent a number. §3.5 - store what was sent.
    size: Mapped[str | None] = mapped_column(String(50))
    slug: Mapped[str | None] = mapped_column(String(255), index=True)
    url_store: Mapped[str | None] = mapped_column(Text)

    source_date_modified: Mapped[datetime.datetime | None] = mapped_column(
        index=True
    )
    detail: Mapped[dict | None] = mapped_column(JSONB)
    last_verified_patch: Mapped[int | None] = mapped_column(
        ForeignKey("patches.id")
    )

    category: Mapped["ItemCategory | None"] = relationship()
    verified_patch: Mapped["Patch | None"] = relationship()


# ---------------------------------------------------------------------------
# A6. SNAPSHOT.
#
# One row per sealed UEX snapshot directory. This is the table that makes §3.4
# - "prices are append-only, keyed by snapshot" - a real thing rather than a
# good intention: a price row points at the snapshot it came from, so a later
# pull ADDS rows instead of overwriting them, and "what did this cost in
# August" stays answerable.
#
# The roadmap watcher on this project overwrote history once already and it
# cost a rebuild. A price is a fact with a date attached.
#
# `row_counts` is JSONB rather than columns because the set of files differs
# per snapshot: 20260801T235530Z holds items/terminals/categories, and
# 20260806T033315Z holds commodities and nothing else. Columns would mean a
# migration every time UEX gains an endpoint.
# ---------------------------------------------------------------------------


class Snapshot(Base):
    """A sealed capture of an external source, at a moment, on disk.

    Deliberately NOT a VerifiableMixin table: a snapshot is not community-
    sourced data with a confidence level, it is a record of a file that
    exists. Its trustworthiness is the sha256 in its own pull manifest.
    """

    __tablename__ = "snapshots"
    __table_args__ = (
        UniqueConstraint("source", "snapshot_key",
                         name="uq_snapshots_source_key"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # "uexcorp" today. Named rather than assumed, because scunpacked and the
    # wiki land snapshots the same way and will want rows here.
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # The directory name, e.g. "20260801T235530Z".
    snapshot_key: Mapped[str] = mapped_column(String(64), nullable=False)
    # Repo-relative, so the row survives the repo being moved or restored to a
    # different path from a backup.
    path: Mapped[str] = mapped_column(Text, nullable=False)

    # Parsed from the directory name, which is the only capture time this
    # project actually holds. If it cannot be parsed it stays NULL rather than
    # being filled with the row's own insert time - that would be a fabricated
    # provenance date, which is worse than an absent one (rule 11).
    captured_at: Mapped[datetime.datetime | None] = mapped_column(index=True)

    row_counts: Mapped[dict | None] = mapped_column(JSONB)
    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
