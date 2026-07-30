from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Component, MissileDetail
from app.routers.component_factory import DEFAULT_LIMIT, MAX_LIMIT, make_component_router
from app.schemas import MissileOut, Page


def _serialize(c: Component) -> MissileOut:
    d = c.missile_detail
    return MissileOut(
        id=c.id,
        name=c.name,
        class_name=c.class_name,
        size=c.size,
        grade=c.grade,
        manufacturer=c.manufacturer.name if c.manufacturer else None,
        notes=c.notes,
        confidence=c.confidence,
        last_verified_patch=c.verified_patch.version if c.verified_patch else None,
        damage=float(d.damage) if d and d.damage is not None else None,
        guidance_type=d.guidance_type if d else None,
        tracking_range_m=float(d.tracking_range_m) if d and d.tracking_range_m is not None else None,
        lock_time_s=float(d.lock_time_s) if d and d.lock_time_s is not None else None,
        speed_mps=float(d.speed_mps) if d and d.speed_mps is not None else None,
    )


router = make_component_router(
    prefix="/api/v1/missiles",
    tags=["missiles"],
    component_type_key="missile",
    detail_relationship="missile_detail",
    serialize=_serialize,
)


@router.get("", response_model=Page[MissileOut], summary="List missiles")
def list_missiles(
    db: Session = Depends(get_db),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    manufacturer: str | None = Query(None, description="Case-insensitive substring match on manufacturer name"),
    size: int | None = Query(None, description="Exact match on component size"),
    grade: str | None = Query(None, description="Case-insensitive substring match on grade"),
    confidence: str | None = Query(None, description="Exact match; one of the standard confidence levels"),
    guidance_type: str | None = Query(None, description="Exact match, e.g. 'ir', 'em', 'cross_section', 'none'"),
):
    def extra(query):
        query = query.join(MissileDetail)
        if guidance_type is not None:
            query = query.filter(MissileDetail.guidance_type == guidance_type)
        return query

    return router.helpers.list_page(
        db,
        limit=limit,
        offset=offset,
        manufacturer=manufacturer,
        size=size,
        grade=grade,
        confidence=confidence,
        extra=extra if guidance_type is not None else None,
    )


@router.get("/{identifier}", response_model=MissileOut, summary="Get one missile by id or class_name")
def get_missile(identifier: str, db: Session = Depends(get_db)):
    return router.helpers.get_one(db, identifier)
