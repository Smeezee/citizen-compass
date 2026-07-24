from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Ship, ShipDealerListing
from app.schemas import ShipOut

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
