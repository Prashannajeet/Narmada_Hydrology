from datetime import date, datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_roles
from app.db.session import get_db
from app.models.dam import Dam, User, UserRole
from app.schemas.risk_register import PaginatedRiskRegister, RiskRegisterCreate, RiskRegisterItem, RiskRegisterSummary, RiskRegisterUpdate
from app.services import log_audit


router = APIRouter()
LEVELS = {"low", "moderate", "high", "critical"}
STATUSES = {"open", "monitoring", "mitigating", "closed", "accepted"}
PRIORITIES = {"low", "medium", "high", "urgent"}


@router.get("", response_model=PaginatedRiskRegister)
def list_risks(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    q: str | None = None,
    state: str | None = None,
    level: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    category: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
) -> PaginatedRiskRegister:
    where, params = _risk_filters(q, state, level, status_filter, category)
    total = db.execute(text(f"SELECT count(*) FROM risk_register risks JOIN dams ON dams.dam_id = risks.dam_id {where}"), params).scalar_one()
    rows = db.execute(
        text(
            f"""
            SELECT risks.*, dams.dam_name, dams.state, dams.district,
              defects.defect_type,
              inspections.status AS inspection_status
            FROM risk_register risks
            JOIN dams ON dams.dam_id = risks.dam_id
            LEFT JOIN geo_tagged_defects defects ON defects.defect_id = risks.defect_id
            LEFT JOIN field_inspections inspections ON inspections.inspection_id = risks.inspection_id
            {where}
            ORDER BY
              CASE risks.risk_level WHEN 'critical' THEN 4 WHEN 'high' THEN 3 WHEN 'moderate' THEN 2 ELSE 1 END DESC,
              risks.risk_score DESC,
              risks.updated_at DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        params | {"limit": limit, "offset": offset},
    ).mappings().all()
    return PaginatedRiskRegister(
        items=[_risk_item(dict(row)) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
        summary=_summary(db, where, params),
    )


@router.post("", response_model=RiskRegisterItem, status_code=status.HTTP_201_CREATED)
def create_risk(
    payload: RiskRegisterCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
) -> RiskRegisterItem:
    if not db.get(Dam, payload.dam_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dam not found")
    _validate_payload(payload.risk_level, payload.status, payload.priority)
    now_code = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    row = db.execute(
        text(
            """
            INSERT INTO risk_register (
              dam_id, inspection_id, defect_id, risk_code, risk_title, risk_category, risk_source,
              trigger_event, likelihood, consequence, risk_level, status, priority, owner_role,
              mitigation_plan, due_date, review_date, compliance_flag, ai_flag, maintenance_required, created_by
            ) VALUES (
              :dam_id, :inspection_id, cast(:defect_id AS uuid), :risk_code, :risk_title, :risk_category, :risk_source,
              :trigger_event, :likelihood, :consequence, :risk_level, :status, :priority, :owner_role,
              :mitigation_plan, :due_date, :review_date, :compliance_flag, :ai_flag, :maintenance_required, :created_by
            )
            RETURNING risk_id
            """
        ),
        payload.model_dump() | {"risk_code": f"RR-{payload.dam_id}-{now_code}", "created_by": current_user.user_id},
    ).scalar_one()
    log_audit(db, request, current_user, "create_risk", "risk_register", str(row), payload.dam_id, after_state=payload.model_dump(mode="json"))
    db.commit()
    return _get_risk(db, str(row))


@router.post("/sync", response_model=PaginatedRiskRegister)
def sync_risk_engine(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer))],
) -> PaginatedRiskRegister:
    db.execute(text(BASELINE_SYNC_SQL))
    db.execute(text(DEFECT_SYNC_SQL))
    log_audit(db, request, current_user, "sync_risk_engine", "risk_register", "risk-engine", None, after_state={"source": "dams, field_inspections, geo_tagged_defects"})
    db.commit()
    return list_risks(db, current_user, q=None, state=None, level=None, status_filter=None, category=None, limit=50, offset=0)


@router.patch("/{risk_id}", response_model=RiskRegisterItem)
def update_risk(
    risk_id: str,
    payload: RiskRegisterUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.engineer, UserRole.inspector))],
) -> RiskRegisterItem:
    existing = db.execute(text("SELECT * FROM risk_register WHERE risk_id = cast(:risk_id AS uuid)"), {"risk_id": risk_id}).mappings().first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found")
    values = payload.model_dump(exclude_unset=True)
    if "status" in values and values["status"] not in STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported risk status")
    if "priority" in values and values["priority"] not in PRIORITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported risk priority")
    if not values:
        return _get_risk(db, risk_id)
    set_clause = ", ".join(f"{key} = :{key}" for key in values)
    db.execute(text(f"UPDATE risk_register SET {set_clause}, updated_at = now() WHERE risk_id = cast(:risk_id AS uuid)"), values | {"risk_id": risk_id})
    log_audit(db, request, current_user, "update_risk", "risk_register", risk_id, existing["dam_id"], before_state=_serialize(dict(existing)), after_state=payload.model_dump(mode="json", exclude_unset=True))
    db.commit()
    return _get_risk(db, risk_id)


def _risk_filters(q: str | None, state: str | None, level: str | None, status_filter: str | None, category: str | None) -> tuple[str, dict[str, Any]]:
    filters = []
    params: dict[str, Any] = {}
    if q:
        filters.append("(dams.dam_name ILIKE :q OR dams.dam_id ILIKE :q OR risks.risk_title ILIKE :q OR risks.risk_code ILIKE :q)")
        params["q"] = f"%{q}%"
    if state:
        filters.append("dams.state = :state")
        params["state"] = state
    if level:
        filters.append("risks.risk_level = :level")
        params["level"] = level
    if status_filter:
        filters.append("risks.status = :status")
        params["status"] = status_filter
    if category:
        filters.append("risks.risk_category = :category")
        params["category"] = category
    return (f"WHERE {' AND '.join(filters)}" if filters else "", params)


def _summary(db: Session, where: str, params: dict[str, Any]) -> RiskRegisterSummary:
    row = db.execute(
        text(
            f"""
            SELECT
              count(*)::int AS total,
              count(*) FILTER (WHERE risks.risk_level = 'critical')::int AS critical,
              count(*) FILTER (WHERE risks.risk_level = 'high')::int AS high,
              count(*) FILTER (WHERE risks.due_date < CURRENT_DATE AND risks.status NOT IN ('closed', 'accepted'))::int AS overdue,
              count(*) FILTER (WHERE risks.due_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days' AND risks.status NOT IN ('closed', 'accepted'))::int AS due_soon,
              count(*) FILTER (WHERE risks.status = 'open')::int AS open,
              count(*) FILTER (WHERE risks.status = 'mitigating')::int AS mitigating,
              count(*) FILTER (WHERE risks.compliance_flag)::int AS compliance_flags,
              count(*) FILTER (WHERE risks.ai_flag)::int AS ai_flags,
              count(*) FILTER (WHERE risks.maintenance_required)::int AS maintenance_required
            FROM risk_register risks
            JOIN dams ON dams.dam_id = risks.dam_id
            {where}
            """
        ),
        params,
    ).mappings().one()
    return RiskRegisterSummary(
        **_serialize(dict(row)),
        by_level=_group(db, "risks.risk_level", where, params),
        by_category=_group(db, "risks.risk_category", where, params, limit=8),
        by_state=_group(db, "dams.state", where, params, limit=8),
    )


def _group(db: Session, column: str, where: str, params: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            f"""
            SELECT {column} AS key, count(*)::int AS count
            FROM risk_register risks
            JOIN dams ON dams.dam_id = risks.dam_id
            {where}
            GROUP BY {column}
            ORDER BY count(*) DESC
            LIMIT :limit
            """
        ),
        params | {"limit": limit},
    ).mappings().all()
    return [{"key": row["key"] or "Not set", "count": row["count"]} for row in rows]


def _get_risk(db: Session, risk_id: str) -> RiskRegisterItem:
    row = db.execute(
        text(
            """
            SELECT risks.*, dams.dam_name, dams.state, dams.district,
              defects.defect_type,
              inspections.status AS inspection_status
            FROM risk_register risks
            JOIN dams ON dams.dam_id = risks.dam_id
            LEFT JOIN geo_tagged_defects defects ON defects.defect_id = risks.defect_id
            LEFT JOIN field_inspections inspections ON inspections.inspection_id = risks.inspection_id
            WHERE risks.risk_id = cast(:risk_id AS uuid)
            """
        ),
        {"risk_id": risk_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk not found")
    return _risk_item(dict(row))


def _risk_item(row: dict[str, Any]) -> RiskRegisterItem:
    return RiskRegisterItem(**_serialize(row))


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _value(value) for key, value in row.items() if key != "created_by"}


def _value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "as_integer_ratio") and not isinstance(value, int):
        return float(value)
    return str(value) if value.__class__.__name__ == "UUID" else value


def _validate_payload(level: str, status_value: str, priority: str) -> None:
    if level not in LEVELS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported risk level")
    if status_value not in STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported risk status")
    if priority not in PRIORITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported risk priority")


BASELINE_SYNC_SQL = """
INSERT INTO risk_register (
  dam_id, risk_code, risk_title, risk_category, risk_source, trigger_event,
  likelihood, consequence, risk_level, status, priority, owner_role,
  mitigation_plan, due_date, review_date, compliance_flag, maintenance_required
)
SELECT
  dams.dam_id,
  concat('RR-', dams.dam_id, '-BASELINE'),
  concat(dams.dam_name, ' baseline dam safety risk'),
  CASE
    WHEN dams.next_inspection_due < CURRENT_DATE THEN 'inspection_overdue'
    WHEN dams.safety_score < 55 THEN 'structural_safety'
    ELSE 'portfolio_risk'
  END,
  'registry_baseline',
  concat('Risk class ', dams.risk_class::text, '; safety score ', dams.safety_score::text),
  CASE dams.risk_class::text WHEN 'critical' THEN 5 WHEN 'high' THEN 4 WHEN 'moderate' THEN 3 ELSE 2 END,
  CASE WHEN dams.safety_score < 50 THEN 5 WHEN dams.safety_score < 65 THEN 4 WHEN dams.safety_score < 80 THEN 3 ELSE 2 END,
  dams.risk_class::text,
  'open',
  CASE dams.risk_class::text WHEN 'critical' THEN 'urgent' WHEN 'high' THEN 'high' WHEN 'moderate' THEN 'medium' ELSE 'low' END,
  'State Dam Safety Engineer',
  'Confirm latest inspection evidence, review instrumentation trend, and assign mitigation owner.',
  COALESCE(dams.next_inspection_due, CURRENT_DATE + INTERVAL '90 days')::date,
  (CURRENT_DATE + INTERVAL '30 days')::date,
  COALESCE(dams.next_inspection_due < CURRENT_DATE, false),
  COALESCE(dams.status::text = 'under_maintenance', false)
FROM dams
WHERE dams.risk_class IN ('critical', 'high')
ON CONFLICT (risk_code) DO UPDATE
SET trigger_event = EXCLUDED.trigger_event,
    likelihood = EXCLUDED.likelihood,
    consequence = EXCLUDED.consequence,
    risk_level = EXCLUDED.risk_level,
    priority = EXCLUDED.priority,
    due_date = EXCLUDED.due_date,
    compliance_flag = EXCLUDED.compliance_flag,
    maintenance_required = EXCLUDED.maintenance_required,
    updated_at = now();
"""

DEFECT_SYNC_SQL = """
INSERT INTO risk_register (
  dam_id, inspection_id, defect_id, risk_code, risk_title, risk_category, risk_source,
  trigger_event, likelihood, consequence, risk_level, status, priority, owner_role,
  mitigation_plan, due_date, review_date, compliance_flag, ai_flag, maintenance_required
)
SELECT
  inspections.dam_id,
  defects.inspection_id,
  defects.defect_id,
  concat('RR-', inspections.dam_id, '-', defects.defect_id::text),
  concat(initcap(replace(defects.defect_type, '_', ' ')), ' observed at ', dams.dam_name),
  defects.defect_type,
  'field_inspection',
  coalesce(defects.description, 'Geo-tagged defect captured in Module 3'),
  CASE defects.severity_rating WHEN 'critical' THEN 5 WHEN 'high' THEN 4 WHEN 'moderate' THEN 3 ELSE 2 END,
  CASE defects.defect_type WHEN 'seepage' THEN 5 WHEN 'crack' THEN 4 WHEN 'erosion' THEN 4 ELSE 3 END,
  defects.severity_rating,
  'open',
  CASE defects.severity_rating WHEN 'critical' THEN 'urgent' WHEN 'high' THEN 'high' WHEN 'moderate' THEN 'medium' ELSE 'low' END,
  'Inspection Review Engineer',
  'Validate defect, compare with previous inspection evidence, and assign maintenance action if progression is confirmed.',
  (CURRENT_DATE + CASE defects.severity_rating WHEN 'critical' THEN INTERVAL '7 days' WHEN 'high' THEN INTERVAL '15 days' ELSE INTERVAL '45 days' END)::date,
  (CURRENT_DATE + INTERVAL '15 days')::date,
  defects.severity_rating IN ('critical', 'high'),
  true,
  true
FROM geo_tagged_defects defects
JOIN field_inspections inspections ON inspections.inspection_id = defects.inspection_id
JOIN dams ON dams.dam_id = inspections.dam_id
WHERE defects.status <> 'closed'
ON CONFLICT (risk_code) DO UPDATE
SET trigger_event = EXCLUDED.trigger_event,
    likelihood = EXCLUDED.likelihood,
    consequence = EXCLUDED.consequence,
    risk_level = EXCLUDED.risk_level,
    priority = EXCLUDED.priority,
    due_date = EXCLUDED.due_date,
    ai_flag = true,
    maintenance_required = true,
    updated_at = now();
"""
