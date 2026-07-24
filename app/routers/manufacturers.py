from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Manufacturer
from app.schemas import ManufacturerOut

router = APIRouter(prefix="/api/v1/manufacturers", tags=["manufacturers"])


@router.get("", response_model=list[ManufacturerOut])
def list_manufacturers(db: Session = Depends(get_db)):
    return db.query(Manufacturer).order_by(Manufacturer.name).all()
