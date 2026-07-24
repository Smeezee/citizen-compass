from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Dealer
from app.schemas import DealerOut

router = APIRouter(prefix="/api/v1/dealers", tags=["dealers"])


@router.get("", response_model=list[DealerOut])
def list_dealers(db: Session = Depends(get_db)):
    return db.query(Dealer).order_by(Dealer.name).all()
