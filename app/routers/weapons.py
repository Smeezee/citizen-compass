from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Component, WeaponDetail
from app.routers.component_factory import DEFAULT_LIMIT, MAX_LIMIT, make_component_router
from app.schemas import Page, WeaponOut


def _serialize(c: Component) -> WeaponOut:
    d = c.weapon_detail
    return WeaponOut(
        id=c.id,
        name=c.name,
        class_name=c.class_name,
        size=c.size,
        grade=c.grade,
        manufacturer=c.manufacturer.name if c.manufacturer else None,
        notes=c.notes,
        confidence=c.confidence,
        last_verified_patch=c.verified_patch.version if c.verified_patch else None,
        damage_type=d.damage_type if d else None,
        fire_mode=d.fire_mode if d else None,
        rpm=d.rpm if d else None,
        damage_per_shot=float(d.damage_per_shot) if d and d.damage_per_shot is not None else None,
        dps=float(d.dps) if d and d.dps is not None else None,
        ammo_capacity=d.ammo_capacity if d else None,
        velocity_mps=float(d.velocity_mps) if d and d.velocity_mps is not None else None,
        range_m=float(d.range_m) if d and d.range_m is not None else None,
    )


router = make_component_router(
    prefix="/api/v1/weapons",
    tags=["weapons"],
    component_type_key="weapon",
    detail_relationship="weapon_detail",
    serialize=_serialize,
)


@router.get("", response_model=Page[WeaponOut], summary="List weapons")
def list_weapons(
    db: Session = Depends(get_db),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    manufacturer: str | None = Query(None, description="Case-insensitive substring match on manufacturer name"),
    size: int | None = Query(None, description="Exact match on component size"),
    grade: str | None = Query(None, description="Case-insensitive substring match on grade"),
    confidence: str | None = Query(None, description="Exact match; one of the standard confidence levels"),
    damage_type: str | None = Query(None, description="Exact match, e.g. 'ballistic', 'energy', 'distortion'"),
    fire_mode: str | None = Query(None, description="Exact match, e.g. 'sustained', 'burst', 'charge'"),
):
    def extra(query):
        query = query.join(WeaponDetail)
        if damage_type is not None:
            query = query.filter(WeaponDetail.damage_type == damage_type)
        if fire_mode is not None:
            query = query.filter(WeaponDetail.fire_mode == fire_mode)
        return query

    has_extra = damage_type is not None or fire_mode is not None
    return router.helpers.list_page(
        db,
        limit=limit,
        offset=offset,
        manufacturer=manufacturer,
        size=size,
        grade=grade,
        confidence=confidence,
        extra=extra if has_extra else None,
    )


@router.get("/{identifier}", response_model=WeaponOut, summary="Get one weapon by id or class_name")
def get_weapon(identifier: str, db: Session = Depends(get_db)):
    return router.helpers.get_one(db, identifier)
