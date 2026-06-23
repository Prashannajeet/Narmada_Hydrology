from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.dam import DamStatus, RiskClass, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    email: str
    full_name: str
    role: UserRole


class LoginRequest(BaseModel):
    email: str
    password: str


class DamEngineeringIn(BaseModel):
    height_m: float | None = None
    length_m: float | None = None
    crest_level_m: float | None = None
    spillway_type: str | None = None
    spillway_capacity_cumecs: float | None = None
    design_flood_cumecs: float | None = None
    foundation_type: str | None = None
    seismic_zone: str | None = None
    instrumentation: dict[str, Any] = Field(default_factory=dict)


class DamReservoirIn(BaseModel):
    reservoir_name: str | None = None
    gross_storage_mcm: float | None = None
    live_storage_mcm: float | None = None
    current_storage_mcm: float | None = None
    frl_m: float | None = None
    mwl_m: float | None = None
    catchment_area_sqkm: float | None = None
    command_area_sqkm: float | None = None


class DamCreate(BaseModel):
    dam_id: str
    dam_name: str
    state: str
    district: str | None = None
    river_basin: str | None = None
    river_name: str | None = None
    owner_agency: str | None = None
    dam_type: str | None = None
    construction_year: int | None = None
    status: DamStatus = DamStatus.operational
    risk_class: RiskClass = RiskClass.moderate
    safety_score: float = Field(default=70, ge=0, le=100)
    last_inspection_date: date | None = None
    next_inspection_due: date | None = None
    longitude: float | None = Field(default=None, ge=-180, le=180)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    engineering: DamEngineeringIn = Field(default_factory=DamEngineeringIn)
    reservoir: DamReservoirIn = Field(default_factory=DamReservoirIn)


class DamUpdate(BaseModel):
    dam_name: str | None = None
    state: str | None = None
    district: str | None = None
    river_basin: str | None = None
    river_name: str | None = None
    owner_agency: str | None = None
    dam_type: str | None = None
    construction_year: int | None = None
    status: DamStatus | None = None
    risk_class: RiskClass | None = None
    safety_score: float | None = Field(default=None, ge=0, le=100)
    last_inspection_date: date | None = None
    next_inspection_due: date | None = None
    engineering: DamEngineeringIn | None = None
    reservoir: DamReservoirIn | None = None


class DamDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: UUID
    dam_id: str
    document_type: str
    title: str
    file_url: str
    file_name: str | None = None
    mime_type: str | None = None
    uploaded_at: datetime


class DamOut(BaseModel):
    dam_id: str
    dam_name: str
    state: str
    district: str | None
    river_basin: str | None
    river_name: str | None
    owner_agency: str | None
    dam_type: str | None
    construction_year: int | None
    status: DamStatus
    risk_class: RiskClass
    safety_score: float
    last_inspection_date: date | None
    next_inspection_due: date | None
    longitude: float | None = None
    latitude: float | None = None
    reservoir_area_sqkm: float | None = None
    engineering: dict[str, Any] | None = None
    reservoir: dict[str, Any] | None = None
    documents: list[DamDocumentOut] = Field(default_factory=list)


class PaginatedDams(BaseModel):
    items: list[DamOut]
    total: int
    limit: int
    offset: int


class AnalyticsOut(BaseModel):
    total_dams: int
    critical_dams: int
    high_risk_dams: int
    overdue_inspections: int
    total_live_storage_mcm: float
    by_risk: list[dict[str, Any]]
    by_status: list[dict[str, Any]]
    by_state: list[dict[str, Any]]


class UploadResult(BaseModel):
    dam_id: str
    geometry_updated: bool
    source_file_name: str
    feature_count: int


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    user_id: UUID | None
    dam_id: str | None
    action: str
    resource_type: str
    resource_id: str | None
    created_at: datetime
