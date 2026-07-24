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
