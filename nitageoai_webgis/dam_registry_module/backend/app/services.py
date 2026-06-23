import json
from typing import Any

from fastapi import HTTPException, Request, UploadFile, status
from geoalchemy2.shape import to_shape
from shapely.geometry import GeometryCollection, MultiPolygon, Point, Polygon, shape
from shapely.ops import unary_union
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.dam import AuditLog, Dam, DamDocument, DamEngineering, DamGeometry, DamReservoir, User
from app.schemas.dam import DamCreate, DamOut


def serialize_dam(dam: Dam, db: Session) -> DamOut:
    longitude = latitude = reservoir_area_sqkm = None
    if dam.geometry and dam.geometry.dam_point:
        point = to_shape(dam.geometry.dam_point)
        longitude, latitude = point.x, point.y
    if dam.geometry and dam.geometry.reservoir_polygon:
        reservoir_area_sqkm = db.scalar(
            select(func.ST_Area(func.ST_Transform(DamGeometry.reservoir_polygon, 3857)) / 1_000_000).where(DamGeometry.dam_id == dam.dam_id)
        )

    return DamOut(
        dam_id=dam.dam_id,
        dam_name=dam.dam_name,
        state=dam.state,
        district=dam.district,
        river_basin=dam.river_basin,
        river_name=dam.river_name,
        owner_agency=dam.owner_agency,
        dam_type=dam.dam_type,
        construction_year=dam.construction_year,
        status=dam.status,
        risk_class=dam.risk_class,
        safety_score=float(dam.safety_score),
        last_inspection_date=dam.last_inspection_date,
        next_inspection_due=dam.next_inspection_due,
        longitude=longitude,
        latitude=latitude,
        reservoir_area_sqkm=float(reservoir_area_sqkm) if reservoir_area_sqkm is not None else None,
        engineering=_model_dict(dam.engineering),
        reservoir=_model_dict(dam.reservoir),
        documents=list(dam.documents),
    )


def create_dam(payload: DamCreate, db: Session) -> Dam:
    dam = Dam(**payload.model_dump(exclude={"engineering", "reservoir", "longitude", "latitude"}))
    dam.engineering = DamEngineering(dam_id=payload.dam_id, **payload.engineering.model_dump())
    dam.reservoir = DamReservoir(dam_id=payload.dam_id, **payload.reservoir.model_dump())
    if payload.longitude is not None and payload.latitude is not None:
        dam.geometry = DamGeometry(
            dam_id=payload.dam_id,
            dam_point=f"SRID=4326;POINT({payload.longitude} {payload.latitude})",
            source_format="manual",
        )
    db.add(dam)
    return dam


async def parse_reservoir_upload(file: UploadFile) -> tuple[MultiPolygon, int]:
    raw = await file.read()
    try:
        geojson = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload must be valid GeoJSON") from exc

    features = geojson.get("features") if geojson.get("type") == "FeatureCollection" else [geojson]
    geometries = []
    for feature in features:
        geom_payload = feature.get("geometry") if feature.get("type") == "Feature" else feature
        if not geom_payload:
            continue
        geom = shape(geom_payload)
        if isinstance(geom, (Polygon, MultiPolygon)):
            geometries.append(geom)

    if not geometries:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GeoJSON must contain at least one polygon or multipolygon")

    merged = unary_union(geometries)
    if isinstance(merged, Polygon):
        merged = MultiPolygon([merged])
    if isinstance(merged, GeometryCollection):
        polygons = [geom for geom in merged.geoms if isinstance(geom, Polygon)]
        merged = MultiPolygon(polygons)
    if not isinstance(merged, MultiPolygon) or not merged.is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reservoir polygon is invalid")
    return merged, len(geometries)


def log_audit(
    db: Session,
    request: Request,
    user: User | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    dam_id: str | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user.user_id if user else None,
            dam_id=dam_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            before_state=before_state,
            after_state=after_state,
        )
    )


def dam_query_with_children():
    return select(Dam).options(joinedload(Dam.engineering), joinedload(Dam.reservoir), joinedload(Dam.geometry), joinedload(Dam.documents))


def _model_dict(model: Any) -> dict[str, Any] | None:
    if not model:
        return None
    data = {}
    for column in model.__table__.columns:
        if column.name in {"dam_id", "updated_at"}:
            continue
        value = getattr(model, column.name)
        data[column.name] = float(value) if hasattr(value, "as_integer_ratio") else value
    return data

