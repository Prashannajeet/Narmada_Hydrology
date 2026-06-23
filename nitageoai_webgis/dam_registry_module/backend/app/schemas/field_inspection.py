from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class InspectionObservationIn(BaseModel):
    section: str
    condition_rating: str = "satisfactory"
    severity_rating: str = "low"
    finding_type: str | None = None
    description: str | None = None
    recommended_action: str | None = None
    requires_maintenance: bool = False


class InspectionPhotoIn(BaseModel):
    observation_section: str | None = None
    file_url: str | None = None
    file_name: str | None = None
    mime_type: str | None = None
    caption: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    captured_at: datetime | None = None
    ai_labels: list[str] = Field(default_factory=list)


class AssetConditionIn(BaseModel):
    asset_tag: str
    asset_type: str
    asset_name: str | None = None
    condition_rating: str = "satisfactory"
    severity_rating: str = "low"
    operational_status: str | None = None
    remarks: str | None = None
    maintenance_priority: str | None = None


class GeoTaggedDefectIn(BaseModel):
    observation_section: str | None = None
    defect_type: str
    severity_rating: str = "moderate"
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    chainage_m: float | None = None
    size_estimate: str | None = None
    status: str = "open"


class FieldInspectionCreate(BaseModel):
    dam_id: str
    inspection_type: str = "routine"
    inspection_date: date | None = None
    severity_rating: str = "moderate"
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    gps_accuracy_m: float | None = None
    gps_timestamp: datetime | None = None
    offline_created: bool = False
    device_id: str | None = None
    qr_asset_tag: str | None = None
    emergency_readiness: str | None = None
    engineer_remarks: str | None = None
    observations: list[InspectionObservationIn] = Field(default_factory=list)
    photos: list[InspectionPhotoIn] = Field(default_factory=list)
    asset_conditions: list[AssetConditionIn] = Field(default_factory=list)
    defects: list[GeoTaggedDefectIn] = Field(default_factory=list)


class InspectionWorkflowUpdate(BaseModel):
    status: str
    reviewer_remarks: str | None = None


class FieldInspectionOut(BaseModel):
    inspection_id: str
    dam_id: str
    dam_name: str | None = None
    state: str | None = None
    district: str | None = None
    inspection_type: str
    inspection_date: date
    status: str
    severity_rating: str
    engineer_name: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    gps_timestamp: datetime | None = None
    offline_created: bool
    qr_asset_tag: str | None = None
    emergency_readiness: str | None = None
    engineer_remarks: str | None = None
    reviewer_remarks: str | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    observation_count: int = 0
    defect_count: int = 0
    photo_count: int = 0
    asset_count: int = 0


class FieldInspectionDetail(FieldInspectionOut):
    observations: list[dict[str, Any]] = Field(default_factory=list)
    photos: list[dict[str, Any]] = Field(default_factory=list)
    asset_conditions: list[dict[str, Any]] = Field(default_factory=list)
    defects: list[dict[str, Any]] = Field(default_factory=list)


class PaginatedFieldInspections(BaseModel):
    items: list[FieldInspectionOut]
    total: int
    limit: int
    offset: int
