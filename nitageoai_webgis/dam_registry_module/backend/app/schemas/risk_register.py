from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class RiskRegisterCreate(BaseModel):
    dam_id: str
    inspection_id: str | None = None
    defect_id: str | None = None
    risk_title: str
    risk_category: str
    risk_source: str = "manual"
    trigger_event: str | None = None
    likelihood: int = 3
    consequence: int = 3
    risk_level: str = "moderate"
    status: str = "open"
    priority: str = "medium"
    owner_role: str | None = None
    mitigation_plan: str | None = None
    due_date: date | None = None
    review_date: date | None = None
    compliance_flag: bool = False
    ai_flag: bool = False
    maintenance_required: bool = False


class RiskRegisterUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    owner_role: str | None = None
    mitigation_plan: str | None = None
    due_date: date | None = None
    review_date: date | None = None
    compliance_flag: bool | None = None
    ai_flag: bool | None = None
    maintenance_required: bool | None = None


class RiskRegisterItem(BaseModel):
    risk_id: str
    dam_id: str
    dam_name: str | None = None
    state: str | None = None
    district: str | None = None
    risk_code: str | None = None
    risk_title: str
    risk_category: str
    risk_source: str
    trigger_event: str | None = None
    likelihood: int
    consequence: int
    risk_score: int
    risk_level: str
    status: str
    priority: str
    owner_role: str | None = None
    mitigation_plan: str | None = None
    due_date: date | None = None
    review_date: date | None = None
    compliance_flag: bool
    ai_flag: bool
    maintenance_required: bool
    inspection_id: str | None = None
    defect_id: str | None = None
    defect_type: str | None = None
    inspection_status: str | None = None
    created_at: datetime
    updated_at: datetime


class RiskRegisterSummary(BaseModel):
    total: int
    critical: int
    high: int
    overdue: int
    due_soon: int
    open: int
    mitigating: int
    compliance_flags: int
    ai_flags: int
    maintenance_required: int
    by_level: list[dict[str, Any]]
    by_category: list[dict[str, Any]]
    by_state: list[dict[str, Any]]


class PaginatedRiskRegister(BaseModel):
    items: list[RiskRegisterItem]
    total: int
    limit: int
    offset: int
    summary: RiskRegisterSummary
