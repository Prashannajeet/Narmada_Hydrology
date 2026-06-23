import enum
import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, Text, func
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DamStatus(str, enum.Enum):
    operational = "operational"
    under_maintenance = "under_maintenance"
    decommissioned = "decommissioned"
    proposed = "proposed"


class RiskClass(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class UserRole(str, enum.Enum):
    admin = "admin"
    engineer = "engineer"
    inspector = "inspector"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.viewer)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Dam(Base):
    __tablename__ = "dams"

    dam_id: Mapped[str] = mapped_column(Text, primary_key=True)
    dam_name: Mapped[str] = mapped_column(Text, nullable=False)
    state: Mapped[str] = mapped_column(Text, nullable=False)
    district: Mapped[str | None] = mapped_column(Text)
    river_basin: Mapped[str | None] = mapped_column(Text)
    river_name: Mapped[str | None] = mapped_column(Text)
    owner_agency: Mapped[str | None] = mapped_column(Text)
    dam_type: Mapped[str | None] = mapped_column(Text)
    construction_year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[DamStatus] = mapped_column(Enum(DamStatus, name="dam_status"), nullable=False, default=DamStatus.operational)
    risk_class: Mapped[RiskClass] = mapped_column(Enum(RiskClass, name="risk_class"), nullable=False, default=RiskClass.moderate)
    safety_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=70)
    last_inspection_date: Mapped[date | None] = mapped_column(Date)
    next_inspection_due: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    engineering: Mapped["DamEngineering"] = relationship(back_populates="dam", cascade="all, delete-orphan", uselist=False)
    reservoir: Mapped["DamReservoir"] = relationship(back_populates="dam", cascade="all, delete-orphan", uselist=False)
    geometry: Mapped["DamGeometry"] = relationship(back_populates="dam", cascade="all, delete-orphan", uselist=False)
    documents: Mapped[list["DamDocument"]] = relationship(back_populates="dam", cascade="all, delete-orphan")


class DamEngineering(Base):
    __tablename__ = "dam_engineering"

    dam_id: Mapped[str] = mapped_column(ForeignKey("dams.dam_id", ondelete="CASCADE"), primary_key=True)
    height_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    length_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    crest_level_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    spillway_type: Mapped[str | None] = mapped_column(Text)
    spillway_capacity_cumecs: Mapped[float | None] = mapped_column(Numeric(12, 2))
    design_flood_cumecs: Mapped[float | None] = mapped_column(Numeric(12, 2))
    foundation_type: Mapped[str | None] = mapped_column(Text)
    seismic_zone: Mapped[str | None] = mapped_column(Text)
    instrumentation: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    dam: Mapped[Dam] = relationship(back_populates="engineering")


class DamReservoir(Base):
    __tablename__ = "dam_reservoir"

    dam_id: Mapped[str] = mapped_column(ForeignKey("dams.dam_id", ondelete="CASCADE"), primary_key=True)
    reservoir_name: Mapped[str | None] = mapped_column(Text)
    gross_storage_mcm: Mapped[float | None] = mapped_column(Numeric(12, 3))
    live_storage_mcm: Mapped[float | None] = mapped_column(Numeric(12, 3))
    current_storage_mcm: Mapped[float | None] = mapped_column(Numeric(12, 3))
    frl_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    mwl_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    catchment_area_sqkm: Mapped[float | None] = mapped_column(Numeric(12, 3))
    command_area_sqkm: Mapped[float | None] = mapped_column(Numeric(12, 3))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    dam: Mapped[Dam] = relationship(back_populates="reservoir")


class DamGeometry(Base):
    __tablename__ = "dam_geometry"

    dam_id: Mapped[str] = mapped_column(ForeignKey("dams.dam_id", ondelete="CASCADE"), primary_key=True)
    dam_point = mapped_column(Geometry("POINT", srid=4326))
    reservoir_polygon = mapped_column(Geometry("MULTIPOLYGON", srid=4326))
    source_file_name: Mapped[str | None] = mapped_column(Text)
    source_format: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    dam: Mapped[Dam] = relationship(back_populates="geometry")


class DamDocument(Base):
    __tablename__ = "dam_documents"

    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    dam_id: Mapped[str] = mapped_column(ForeignKey("dams.dam_id", ondelete="CASCADE"), nullable=False)
    document_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_name: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    dam: Mapped[Dam] = relationship(back_populates="documents")


class AuditLog(Base):
    __tablename__ = "audit_log"

    audit_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    dam_id: Mapped[str | None] = mapped_column(ForeignKey("dams.dam_id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(INET)
    user_agent: Mapped[str | None] = mapped_column(Text)
    before_state: Mapped[dict | None] = mapped_column(JSONB)
    after_state: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("idx_dams_filters_orm", Dam.state, Dam.river_basin, Dam.risk_class, Dam.status)
