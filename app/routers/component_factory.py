"""Generic list+detail router factory for Ship Items component categories.

Per docs/ARCHITECTURE_DECISIONS.md section 3 (LOCKED): a generic CRUD/list
router factory for simple list+filter+detail entities, instead of six
hand-written near-identical routers. Custom bespoke routers (`ships`, which
aggregates dealer listings + pledge links) stay hand-written on purpose -
this factory is only for the straightforward "list this component category,
filter it, look at one" case.

Design: this factory owns the genuinely generic parts - base query
construction (join to component_types, eager-load the right typed detail
relationship), the four base filters every category gets for free
(manufacturer/size/grade/confidence), deterministic ordering, bounded
pagination, the Page envelope, and id-or-class_name detail lookup with a
proper 404. Each category's own router file (weapons.py / missiles.py /
turrets.py) stays a thin ~30-line wrapper: it declares its own real,
named, documented FastAPI query params for whatever category-specific
filters make sense (e.g. damage_type on weapons, guidance_type on
missiles), and hands a small callback to the factory to apply them. That
keeps OpenAPI docs accurate per endpoint without hand-writing the
pagination/ordering/serialization logic six times.
"""

from typing import Any, Callable

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import CONFIDENCE_LEVELS, Component, ComponentType, Manufacturer
from app.schemas import Page

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

QueryTransform = Callable[[Any], Any]  # (sqlalchemy Query) -> Query, applies extra filters


def _validate_confidence(value: str | None) -> None:
    if value is not None and value not in CONFIDENCE_LEVELS:
        raise HTTPException(
            status_code=422,
            detail=f"confidence must be one of {CONFIDENCE_LEVELS}, got {value!r}",
        )


class ComponentRouterHelpers:
    """Shared query/serialization logic for one component category. Not a
    router itself - `make_component_router` returns a bare APIRouter with
    this attached as `.helpers`, so each category's thin router file can
    call `router.helpers.list_page(...)` / `.get_one(...)` from its own
    hand-declared endpoint functions.
    """

    def __init__(self, component_type_key: str, detail_relationship: str, serialize: Callable[[Component], Any]):
        self.component_type_key = component_type_key
        self.detail_relationship = detail_relationship
        self.serialize = serialize

    def base_query(self, db: Session):
        return (
            db.query(Component)
            .join(ComponentType, Component.component_type_id == ComponentType.id)
            .filter(ComponentType.key == self.component_type_key)
            .options(
                joinedload(Component.manufacturer),
                joinedload(Component.component_type),
                joinedload(Component.verified_patch),
                joinedload(getattr(Component, self.detail_relationship)),
            )
        )

    def list_page(
        self,
        db: Session,
        *,
        limit: int,
        offset: int,
        manufacturer: str | None = None,
        size: int | None = None,
        grade: str | None = None,
        confidence: str | None = None,
        extra: QueryTransform | None = None,
    ) -> Page:
        _validate_confidence(confidence)
        query = self.base_query(db)

        if manufacturer:
            query = query.join(Component.manufacturer).filter(
                Manufacturer.name.ilike(f"%{manufacturer}%")
            )
        if size is not None:
            query = query.filter(Component.size == size)
        if grade:
            query = query.filter(Component.grade.ilike(f"%{grade}%"))
        if confidence:
            query = query.filter(Component.confidence == confidence)
        if extra is not None:
            query = extra(query)

        total = query.count()
        # Deterministic ordering: name is the natural human sort key, id is
        # a tiebreaker so rows with identical/null names still sort stably
        # instead of relying on undefined DB row order.
        rows = (
            query.order_by(Component.name.asc(), Component.id.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return Page(items=[self.serialize(c) for c in rows], total=total, limit=limit, offset=offset)

    def get_one(self, db: Session, identifier: str):
        query = self.base_query(db)
        try:
            component_id = int(identifier)
        except ValueError:
            component_id = None

        component = (
            query.filter(Component.id == component_id).first()
            if component_id is not None
            else query.filter(Component.class_name == identifier).first()
        )
        if component is None:
            raise HTTPException(
                status_code=404,
                detail=f"No {self.component_type_key} found for identifier {identifier!r}",
            )
        return self.serialize(component)


def make_component_router(
    *,
    prefix: str,
    tags: list[str],
    component_type_key: str,
    detail_relationship: str,
    serialize: Callable[[Component], Any],
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=list(tags))
    router.helpers = ComponentRouterHelpers(component_type_key, detail_relationship, serialize)
    return router

