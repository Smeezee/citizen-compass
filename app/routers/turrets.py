from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Component, TurretDetail
from app.routers.component_factory import DEFAULT_LIMIT, MAX_LIMIT, make_component_router
from app.schemas import Page, TurretOut


def _serialize(c: Component) -> TurretOut:
    d = c.turret_detail
    return TurretOut(
        id=c.id,
        name=c.name,
        class_name=c.class_name,
        size=c.size,
        grade=c.grade,
        manufacturer=c.manufacturer.name if c.manufacturer else None,
        notes=c.notes,
        confidence=c.confidence,
        last_verified_patch=c.verified_patch.version if c.verified_patch else None,
        weapon_slots=d.weapon_slots if d else None,
        slot_weapon_size=d.slot_weapon_size if d else None,
        manned=d.manned if d else None,
    )


router = make_component_router(
    prefix="/api/v1/turrets",
    tags=["turrets"],
    component_type_key="turret",
    detail_relationship="turret_detail",
    serialize=_serialize,
)


@router.get("", response_model=Page[TurretOut], summary="List turrets")
def list_turrets(
    db: Session = Depends(get_db),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    manufacturer: str | None = Query(None, description="Case-insensitive substring match on manufacturer name"),
    size: int | None = Query(None, description="Exact match on component size"),
    grade: str | None = Query(None, description="Case-insensitive substring match on grade"),
    confidence: str | None = Query(None, description="Exact match; one of the standard confidence levels"),
    manned: bool | None = Query(None, description="Exact match: true for manned turrets, false for remote"),
):
    def extra(query):
        query = query.join(TurretDetail)
        if manned is not None:
            query = query.filter(TurretDetail.manned == manned)
        return query

    return router.helpers.list_page(
        db,
        limit=limit,
        offset=offset,
        manufacturer=manufacturer,
        size=size,
        grade=grade,
        confidence=confidence,
        extra=extra if manned is not None else None,
    )


@router.get("/{identifier}", response_model=TurretOut, summary="Get one turret by id or class_name")
def get_turret(identifier: str, db: Session = Depends(get_db)):
    return router.helpers.get_one(db, identifier)
