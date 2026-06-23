from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db.session import get_db
from app.models.dam import AuditLog, User, UserRole
from app.schemas.dam import AuditOut


router = APIRouter()


@router.get("", response_model=list[AuditOut])
def list_audit(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer))],
    dam_id: str | None = None,
    limit: int = Query(default=50, le=200),
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if dam_id:
        query = query.where(AuditLog.dam_id == dam_id)
    return list(db.scalars(query).all())

