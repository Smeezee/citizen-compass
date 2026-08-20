import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    Ship,
    ShipDealerListing,
    ShipHardpoint,
    ShipHardpointCoverage,
)
from app.schemas import ShipHardpointsOut, ShipHardpointSlotOut, ShipOut

router = APIRouter(prefix="/api/v1/ships", tags=["ships"])


def _serialize(ship: Ship) -> ShipOut:
    pledge = ship.pledge_links[0] if ship.pledge_links else None
    auec_prices = [
        listing.in_game_price_auec
        for listing in ship.dealer_listings
        if listing.in_game_price_auec is not None
    ]
    return ShipOut(
        id=ship.id,
        name=ship.name,
        manufacturer=ship.manufacturer.name,
        role=ship.role,
        notes=ship.notes,
        status=ship.status,
        auec_price=auec_prices[0] if auec_prices else None,
        dealers=[listing.dealer.name for listing in ship.dealer_listings],
        pledge_price_usd=float(pledge.price_usd) if pledge and pledge.price_usd is not None else None,
        pledge_url=pledge.url if pledge else None,
        confidence=ship.confidence,
        last_verified_patch=ship.verified_patch.version if ship.verified_patch else None,
    )


@router.get("", response_model=list[ShipOut])
def list_ships(db: Session = Depends(get_db)):
    ships = (
        db.query(Ship)
        .options(
            joinedload(Ship.manufacturer),
            joinedload(Ship.dealer_listings).joinedload(ShipDealerListing.dealer),
            joinedload(Ship.pledge_links),
            joinedload(Ship.verified_patch),
        )
        .order_by(Ship.name)
        .all()
    )
    return [_serialize(ship) for ship in ships]


# ---------------------------------------------------------------------------
# G8 - the ship page's Loadout panel, which has been promising this since it
# was written: "slot structure shown, no invented values".
#
# KEYED BY MODEL, NOT BY SHIP, and the site asks with the key it already holds
# to load the 3D view - so no new ship-to-model matching is invented here. See
# the note on ShipHardpoint for why the underlying facts belong to a mesh
# rather than to a ship.
#
# THE THREE ANSWERS, WHICH MUST STAY THREE:
#
#   200 with slots      we measured this hull and here is what is on it
#   200 with no slots   we know about this hull and we have NO slot data,
#                       plus the build's own reason why
#   404                 we have never heard of this model
#
# Collapsing the middle one into either neighbour is the whole failure this
# endpoint exists to avoid. A 404 for "no data" tells the page the ship does
# not exist; an empty 200 with no reason gives it nothing to say. The panel's
# own text promises no invented values, and "we do not know" is the honest
# thing to render - but only if the API bothers to distinguish it.
# ---------------------------------------------------------------------------


def _model_key(raw: str) -> str:
    """The same spelling rule the importer uses. A rule, not a matcher."""
    return re.sub(r"[^a-z0-9]+", " ", (raw or "").lower()).strip()


@router.get("/models/{model_name}/hardpoints", response_model=ShipHardpointsOut)
def get_model_hardpoints(model_name: str, db: Session = Depends(get_db)):
    key = _model_key(model_name)

    coverage = db.execute(
        select(ShipHardpointCoverage).where(
            ShipHardpointCoverage.model_key == key
        )
    ).scalar_one_or_none()

    if coverage is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No model named {model_name!r} is known to the hardpoint "
                f"dataset. This is not the same as a model with no hardpoints - "
                f"that answers 200 with an empty slot list and a reason."
            ),
        )

    slots = db.execute(
        select(ShipHardpoint)
        .where(ShipHardpoint.model_key == key)
        .order_by(ShipHardpoint.kind, ShipHardpoint.port)
    ).scalars().all()

    return ShipHardpointsOut(
        model=model_name,
        model_key=key,
        status=coverage.status,
        reason=coverage.reason,
        slot_count=coverage.slot_count,
        source_dataset=coverage.source_dataset,
        slots=[
            ShipHardpointSlotOut(
                port=slot.port,
                kind=slot.kind,
                size=slot.size,
                stock_item_name=slot.stock_item_name,
                stock_item_type=slot.stock_item_type,
                where=(slot.detail or {}).get("where"),
            )
            for slot in slots
        ],
    )
