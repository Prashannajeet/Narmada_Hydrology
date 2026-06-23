from datetime import date, datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models.dam import Dam, User, UserRole
from app.schemas.field_inspection import FieldInspectionCreate, FieldInspectionDetail, FieldInspectionOut, InspectionWorkflowUpdate, PaginatedFieldInspections
from app.services import log_audit


router = APIRouter()
SECTIONS = [
    "General inspection",
    "Upstream face",
    "Downstream face",
    "Crest",
    "Spillway",
    "Gates and hoists",
    "Energy dissipation structure",
    "Seepage and drainage",
    "Instrumentation",
    "Downstream hazard",
    "Emergency readiness",
]


@router.get("", response_model=PaginatedFieldInspections)
def list_field_inspections(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    dam_id: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    limit: int = Query(default=25, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedFieldInspections:
    where, params = _inspection_filters(dam_id, status_filter, severity)
    total = db.execute(text(f"SELECT count(*) FROM field_inspections inspections {where}"), params).scalar_one()
    rows = db.execute(
        text(
            f"""
            SELECT inspections.*, dams.dam_name, dams.state, dams.district,
              (SELECT count(*) FROM inspection_observations obs WHERE obs.inspection_id = inspections.inspection_id)::int AS observation_count,
              (SELECT count(*) FROM geo_tagged_defects defects WHERE defects.inspection_id = inspections.inspection_id)::int AS defect_count,
              (SELECT count(*) FROM inspection_photos photos WHERE photos.inspection_id = inspections.inspection_id)::int AS photo_count,
              (SELECT count(*) FROM asset_condition assets WHERE assets.inspection_id = inspections.inspection_id)::int AS asset_count
            FROM field_inspections inspections
            JOIN dams ON dams.dam_id = inspections.dam_id
            {where}
            ORDER BY inspections.inspection_date DESC, inspections.created_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        params | {"limit": limit, "offset": offset},
    ).mappings().all()
    return PaginatedFieldInspections(items=[_inspection_out(dict(row)) for row in rows], total=total, limit=limit, offset=offset)


@router.post("", response_model=FieldInspectionDetail, status_code=status.HTTP_201_CREATED)
def create_field_inspection(
    payload: FieldInspectionCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
) -> FieldInspectionDetail:
    dam = db.get(Dam, payload.dam_id)
    if not dam:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")

    inspection_id = f"FI-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    now = datetime.now(timezone.utc)
    db.execute(
        text(
            """
            INSERT INTO field_inspections (
              inspection_id, dam_id, inspection_type, inspection_date, engineer_id, engineer_name,
              severity_rating, gps_latitude, gps_longitude, gps_accuracy_m, gps_timestamp,
              offline_created, device_id, qr_asset_tag, emergency_readiness, engineer_remarks, synced_at
            ) VALUES (
              :inspection_id, :dam_id, :inspection_type, :inspection_date, :engineer_id, :engineer_name,
              :severity_rating, :gps_latitude, :gps_longitude, :gps_accuracy_m, :gps_timestamp,
              :offline_created, :device_id, :qr_asset_tag, :emergency_readiness, :engineer_remarks, :synced_at
            )
            """
        ),
        {
            "inspection_id": inspection_id,
            "dam_id": payload.dam_id,
            "inspection_type": payload.inspection_type,
            "inspection_date": payload.inspection_date or date.today(),
            "engineer_id": current_user.user_id,
            "engineer_name": current_user.full_name,
            "severity_rating": payload.severity_rating,
            "gps_latitude": payload.gps_latitude,
            "gps_longitude": payload.gps_longitude,
            "gps_accuracy_m": payload.gps_accuracy_m,
            "gps_timestamp": payload.gps_timestamp,
            "offline_created": payload.offline_created,
            "device_id": payload.device_id,
            "qr_asset_tag": payload.qr_asset_tag,
            "emergency_readiness": payload.emergency_readiness,
            "engineer_remarks": payload.engineer_remarks,
            "synced_at": now if payload.offline_created else None,
        },
    )
    observation_ids = _insert_observations(db, inspection_id, payload)
    _insert_photos(db, inspection_id, payload, observation_ids)
    _insert_assets(db, inspection_id, payload)
    _insert_defects(db, inspection_id, payload, observation_ids)
    log_audit(db, request, current_user, "create_field_inspection", "field_inspection", inspection_id, payload.dam_id, after_state=payload.model_dump(mode="json"))
    db.commit()
    return _get_detail(db, inspection_id)


@router.get("/metadata/sections")
def field_inspection_sections(_: Annotated[User, Depends(get_current_user)]) -> dict[str, Any]:
    return {
        "sections": SECTIONS,
        "condition_ratings": ["satisfactory", "fair", "poor", "unsafe", "not_accessible"],
        "severity_ratings": ["low", "moderate", "high", "critical"],
        "defect_types": ["crack", "seepage", "erosion", "settlement", "vegetation", "gate_malfunction", "spillway_damage", "instrument_fault"],
        "asset_types": ["gate", "hoist", "spillway", "embankment", "instrument", "drain", "road", "warning_system"],
        "workflow_statuses": ["draft", "submitted", "approved", "rejected", "requires_action"],
    }


@router.get("/{inspection_id}", response_model=FieldInspectionDetail)
def get_field_inspection(
    inspection_id: str,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
) -> FieldInspectionDetail:
    return _get_detail(db, inspection_id)


@router.patch("/{inspection_id}/workflow", response_model=FieldInspectionDetail)
def update_field_inspection_workflow(
    inspection_id: str,
    payload: InspectionWorkflowUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
) -> FieldInspectionDetail:
    if payload.status not in {"submitted", "approved", "rejected", "requires_action"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported workflow status")
    existing = db.execute(text("SELECT * FROM field_inspections WHERE inspection_id = :inspection_id"), {"inspection_id": inspection_id}).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    if payload.status in {"approved", "rejected"} and current_user.role not in {UserRole.admin, UserRole.engineer}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin or engineer can approve/reject")
    db.execute(
        text(
            """
            UPDATE field_inspections
            SET status = :status,
                reviewer_remarks = coalesce(:reviewer_remarks, reviewer_remarks),
                submitted_at = CASE WHEN :status = 'submitted' THEN now() ELSE submitted_at END,
                completed_at = CASE WHEN :status = 'submitted' THEN now() ELSE completed_at END,
                approved_at = CASE WHEN :status = 'approved' THEN now() ELSE approved_at END,
                approved_by = CASE WHEN :status = 'approved' THEN :user_id ELSE approved_by END,
                updated_at = now()
            WHERE inspection_id = :inspection_id
            """
        ),
        {"inspection_id": inspection_id, "status": payload.status, "reviewer_remarks": payload.reviewer_remarks, "user_id": current_user.user_id},
    )
    log_audit(db, request, current_user, f"field_inspection_{payload.status}", "field_inspection", inspection_id, existing["dam_id"], after_state=payload.model_dump(mode="json"))
    db.commit()
    return _get_detail(db, inspection_id)


def _inspection_filters(dam_id: str | None, status_filter: str | None, severity: str | None) -> tuple[str, dict[str, Any]]:
    filters = []
    params: dict[str, Any] = {}
    if dam_id:
        filters.append("inspections.dam_id = :dam_id")
        params["dam_id"] = dam_id
    if status_filter:
        filters.append("inspections.status = :status")
        params["status"] = status_filter
    if severity:
        filters.append("inspections.severity_rating = :severity")
        params["severity"] = severity
    return (f"WHERE {' AND '.join(filters)}" if filters else "", params)


def _insert_observations(db: Session, inspection_id: str, payload: FieldInspectionCreate) -> dict[str, str]:
    observation_ids = {}
    observations = payload.observations or [InspectionObservationStub(section=section) for section in SECTIONS]
    for observation in observations:
        row = db.execute(
            text(
                """
                INSERT INTO inspection_observations (
                  inspection_id, section, condition_rating, severity_rating, finding_type, description, recommended_action, requires_maintenance
                ) VALUES (
                  :inspection_id, :section, :condition_rating, :severity_rating, :finding_type, :description, :recommended_action, :requires_maintenance
                )
                RETURNING observation_id
                """
            ),
            {"inspection_id": inspection_id, **observation.model_dump()},
        ).scalar_one()
        observation_ids[observation.section] = str(row)
    return observation_ids


def _insert_photos(db: Session, inspection_id: str, payload: FieldInspectionCreate, observation_ids: dict[str, str]) -> None:
    for photo in payload.photos:
        db.execute(
            text(
                """
                INSERT INTO inspection_photos (
                  inspection_id, observation_id, file_url, file_name, mime_type, caption, latitude, longitude, captured_at, ai_labels
                ) VALUES (
                  :inspection_id, :observation_id, :file_url, :file_name, :mime_type, :caption, :latitude, :longitude, :captured_at, cast(:ai_labels AS jsonb)
                )
                """
            ),
            {"inspection_id": inspection_id, "observation_id": observation_ids.get(photo.observation_section or ""), **photo.model_dump(exclude={"observation_section"}), "ai_labels": _json(photo.ai_labels)},
        )


def _insert_assets(db: Session, inspection_id: str, payload: FieldInspectionCreate) -> None:
    for asset in payload.asset_conditions:
        db.execute(
            text(
                """
                INSERT INTO asset_condition (
                  inspection_id, asset_tag, asset_type, asset_name, condition_rating, severity_rating, operational_status, remarks, maintenance_priority
                ) VALUES (
                  :inspection_id, :asset_tag, :asset_type, :asset_name, :condition_rating, :severity_rating, :operational_status, :remarks, :maintenance_priority
                )
                """
            ),
            {"inspection_id": inspection_id, **asset.model_dump()},
        )


def _insert_defects(db: Session, inspection_id: str, payload: FieldInspectionCreate, observation_ids: dict[str, str]) -> None:
    for defect in payload.defects:
        db.execute(
            text(
                """
                INSERT INTO geo_tagged_defects (
                  inspection_id, observation_id, defect_type, severity_rating, description, latitude, longitude, location, chainage_m, size_estimate, status
                ) VALUES (
                  :inspection_id, :observation_id, :defect_type, :severity_rating, :description, :latitude, :longitude,
                  CASE WHEN :latitude IS NOT NULL AND :longitude IS NOT NULL THEN ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326) ELSE NULL END,
                  :chainage_m, :size_estimate, :status
                )
                """
            ),
            {"inspection_id": inspection_id, "observation_id": observation_ids.get(defect.observation_section or ""), **defect.model_dump(exclude={"observation_section"})},
        )


def _get_detail(db: Session, inspection_id: str) -> FieldInspectionDetail:
    row = db.execute(
        text(
            """
            SELECT inspections.*, dams.dam_name, dams.state, dams.district,
              (SELECT count(*) FROM inspection_observations obs WHERE obs.inspection_id = inspections.inspection_id)::int AS observation_count,
              (SELECT count(*) FROM geo_tagged_defects defects WHERE defects.inspection_id = inspections.inspection_id)::int AS defect_count,
              (SELECT count(*) FROM inspection_photos photos WHERE photos.inspection_id = inspections.inspection_id)::int AS photo_count,
              (SELECT count(*) FROM asset_condition assets WHERE assets.inspection_id = inspections.inspection_id)::int AS asset_count
            FROM field_inspections inspections
            JOIN dams ON dams.dam_id = inspections.dam_id
            WHERE inspections.inspection_id = :inspection_id
            """
        ),
        {"inspection_id": inspection_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    detail = _inspection_out(dict(row)).model_dump()
    child_queries = {
        "observations": "SELECT * FROM inspection_observations WHERE inspection_id = :inspection_id ORDER BY created_at",
        "photos": "SELECT * FROM inspection_photos WHERE inspection_id = :inspection_id ORDER BY created_at",
        "asset_conditions": "SELECT * FROM asset_condition WHERE inspection_id = :inspection_id ORDER BY created_at",
        "defects": """
            SELECT defect_id, inspection_id, observation_id, defect_type, severity_rating, description,
              latitude, longitude, ST_AsGeoJSON(location)::json AS location_geojson, chainage_m,
              size_estimate, status, risk_engine_status, maintenance_status, created_at
            FROM geo_tagged_defects
            WHERE inspection_id = :inspection_id
            ORDER BY created_at
        """,
    }
    for key, sql in child_queries.items():
        detail[key] = [_serialize(dict(item)) for item in db.execute(text(sql), {"inspection_id": inspection_id}).mappings().all()]
    return FieldInspectionDetail(**detail)


def _inspection_out(row: dict[str, Any]) -> FieldInspectionOut:
    return FieldInspectionOut(**_serialize(row))


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _value(value) for key, value in row.items() if key not in {"engineer_id", "approved_by"}}


def _value(value: Any) -> Any:
    if hasattr(value, "as_integer_ratio"):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _json(value: Any) -> str:
    import json

    return json.dumps(value)


class InspectionObservationStub:
    def __init__(self, section: str):
        self.section = section
        self.condition_rating = "satisfactory"
        self.severity_rating = "low"
        self.finding_type = None
        self.description = None
        self.recommended_action = None
        self.requires_maintenance = False

    def model_dump(self) -> dict[str, Any]:
        return {
            "section": self.section,
            "condition_rating": self.condition_rating,
            "severity_rating": self.severity_rating,
            "finding_type": self.finding_type,
            "description": self.description,
            "recommended_action": self.recommended_action,
            "requires_maintenance": self.requires_maintenance,
        }
