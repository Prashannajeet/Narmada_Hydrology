from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models.dam import Dam, DamEngineering, DamReservoir, DamStatus, RiskClass, User, UserRole
from app.schemas.dam import DamCreate, DamOut, DamUpdate, PaginatedDams
from app.services import create_dam, dam_query_with_children, log_audit, serialize_dam


router = APIRouter()


@router.get("", response_model=PaginatedDams)
def list_dams(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    q: str | None = None,
    state: str | None = None,
    basin: str | None = None,
    risk: RiskClass | None = None,
    status_filter: DamStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=25, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedDams:
    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(or_(Dam.dam_name.ilike(pattern), Dam.dam_id.ilike(pattern), Dam.state.ilike(pattern), Dam.river_basin.ilike(pattern)))
    if state:
        filters.append(Dam.state == state)
    if basin:
        filters.append(Dam.river_basin == basin)
    if risk:
        filters.append(Dam.risk_class == risk)
    if status_filter:
        filters.append(Dam.status == status_filter)

    total = db.scalar(select(func.count()).select_from(Dam).where(*filters)) or 0
    dams = db.scalars(dam_query_with_children().where(*filters).order_by(Dam.risk_class.desc(), Dam.dam_name).limit(limit).offset(offset)).unique().all()
    return PaginatedDams(items=[serialize_dam(dam, db) for dam in dams], total=total, limit=limit, offset=offset)


@router.post("", response_model=DamOut, status_code=status.HTTP_201_CREATED)
def create_dam_endpoint(
    payload: DamCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer))],
) -> DamOut:
    if db.get(Dam, payload.dam_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="dam_id already exists")
    dam = create_dam(payload, db)
    db.flush()
    log_audit(db, request, current_user, "create", "dam", payload.dam_id, payload.dam_id, after_state=payload.model_dump(mode="json"))
    db.commit()
    db.refresh(dam)
    return serialize_dam(db.scalars(dam_query_with_children().where(Dam.dam_id == dam.dam_id)).unique().one(), db)


@router.get("/{dam_id}", response_model=DamOut)
def get_dam(dam_id: str, db: Annotated[Session, Depends(get_db)], _: Annotated[User, Depends(get_current_user)]) -> DamOut:
    dam = db.scalars(dam_query_with_children().where(Dam.dam_id == dam_id)).unique().first()
    if not dam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")
    return serialize_dam(dam, db)


@router.patch("/{dam_id}", response_model=DamOut)
def update_dam(
    dam_id: str,
    payload: DamUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
) -> DamOut:
    dam = db.scalars(dam_query_with_children().where(Dam.dam_id == dam_id)).unique().first()
    if not dam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")
    before = serialize_dam(dam, db).model_dump(mode="json")
    values = payload.model_dump(exclude_unset=True, exclude={"engineering", "reservoir"})
    for key, value in values.items():
        setattr(dam, key, value)
    if payload.engineering:
        dam.engineering = dam.engineering or DamEngineering(dam_id=dam_id)
        for key, value in payload.engineering.model_dump(exclude_unset=True).items():
            setattr(dam.engineering, key, value)
    if payload.reservoir:
        dam.reservoir = dam.reservoir or DamReservoir(dam_id=dam_id)
        for key, value in payload.reservoir.model_dump(exclude_unset=True).items():
            setattr(dam.reservoir, key, value)
    log_audit(db, request, current_user, "update", "dam", dam_id, dam_id, before_state=before, after_state=payload.model_dump(mode="json", exclude_unset=True))
    db.commit()
    return serialize_dam(db.scalars(dam_query_with_children().where(Dam.dam_id == dam_id)).unique().one(), db)


@router.delete("/{dam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dam(
    dam_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin))],
) -> None:
    dam = db.get(Dam, dam_id)
    if not dam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")
    log_audit(db, request, current_user, "delete", "dam", dam_id, None)
    db.execute(delete(Dam).where(Dam.dam_id == dam_id))
    db.commit()
