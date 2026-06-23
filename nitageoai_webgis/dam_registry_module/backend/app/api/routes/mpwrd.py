from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter()


@router.get("")
def mpwrd_overview(
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, Any]:
    report_date = db.execute(text("SELECT max(report_date) FROM mpwrd_reservoir_levels")).scalar_one_or_none()
    if not report_date:
        return {"summary": None, "basins": [], "readings": []}

    summary = db.execute(
        text(
            """
            SELECT
              count(*)::int AS total_readings,
              count(DISTINCT dam_id)::int AS linked_dams,
              count(*) FILTER (WHERE this_year_is_stale)::int AS stale_readings,
              coalesce(sum(live_capacity_at_frl_mcm), 0) AS total_live_capacity_mcm,
              coalesce(sum(this_year_live_capacity_mcm), 0) AS current_live_storage_mcm,
              avg(this_year_live_storage_percent) AS avg_storage_percent,
              max(fetched_at) AS fetched_at
            FROM mpwrd_reservoir_levels
            WHERE report_date = :report_date
            """
        ),
        {"report_date": report_date},
    ).mappings().one()

    basins = db.execute(
        text(
            """
            SELECT
              coalesce(basin_office, 'Unassigned') AS basin_office,
              count(*)::int AS reservoir_count,
              coalesce(sum(live_capacity_at_frl_mcm), 0) AS live_capacity_mcm,
              coalesce(sum(this_year_live_capacity_mcm), 0) AS current_storage_mcm,
              avg(this_year_live_storage_percent) AS avg_storage_percent,
              count(*) FILTER (WHERE this_year_is_stale)::int AS stale_count
            FROM mpwrd_reservoir_levels
            WHERE report_date = :report_date
            GROUP BY coalesce(basin_office, 'Unassigned')
            ORDER BY reservoir_count DESC, basin_office
            """
        ),
        {"report_date": report_date},
    ).mappings().all()

    readings = db.execute(
        text(
            """
            SELECT
              levels.reservoir_code,
              levels.dam_id,
              levels.reservoir_name,
              levels.basin_office,
              levels.district,
              levels.reading_time,
              levels.frl_m,
              levels.live_capacity_at_frl_mcm,
              levels.this_year_level_m,
              levels.this_year_live_capacity_mcm,
              levels.this_year_live_storage_percent,
              levels.this_year_level_observed_date,
              levels.this_year_is_stale,
              levels.gate_count_open,
              levels.gate_discharge_cumec,
              dams.risk_class::text AS risk_class,
              dams.safety_score,
              dams.source_registry
            FROM mpwrd_reservoir_levels levels
            LEFT JOIN dams ON dams.dam_id = levels.dam_id
            WHERE levels.report_date = :report_date
            ORDER BY levels.this_year_live_storage_percent DESC NULLS LAST, levels.reservoir_name
            """
        ),
        {"report_date": report_date},
    ).mappings().all()

    return {
        "summary": serialize_row({"report_date": report_date, **dict(summary)}),
        "basins": [serialize_row(dict(row)) for row in basins],
        "readings": [serialize_row(dict(row)) for row in readings],
    }


def serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: serialize_value(value) for key, value in row.items()}


def serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
