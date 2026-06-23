from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from geoalchemy2.shape import from_shape
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.db.session import get_db
from app.models.dam import Dam, DamGeometry, User, UserRole
from app.schemas.dam import UploadResult
from app.services import log_audit, parse_reservoir_upload


router = APIRouter()


@router.post("/{dam_id}/reservoir-polygon", response_model=UploadResult)
async def upload_reservoir_polygon(
    dam_id: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
    file: UploadFile = File(...),
) -> UploadResult:
    if not db.get(Dam, dam_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")
    polygon, feature_count = await parse_reservoir_upload(file)
    geometry = db.get(DamGeometry, dam_id) or DamGeometry(dam_id=dam_id)
    geometry.reservoir_polygon = from_shape(polygon, srid=4326)
    geometry.source_file_name = file.filename
    geometry.source_format = "GeoJSON"
    geometry.uploaded_by = current_user.user_id
    db.add(geometry)
    log_audit(db, request, current_user, "upload_reservoir_polygon", "dam_geometry", dam_id, dam_id, after_state={"file_name": file.filename})
    db.commit()
    return UploadResult(dam_id=dam_id, geometry_updated=True, source_file_name=file.filename or "upload.geojson", feature_count=feature_count)

