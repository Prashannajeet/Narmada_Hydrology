import re
from datetime import date
from difflib import SequenceMatcher
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import bindparam, func, or_, select, text
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.dam import Dam, DamEngineering, DamReservoir, DamStatus, RiskClass, User
from app.schemas.dam import AnalyticsOut


router = APIRouter()


@router.get("", response_model=AnalyticsOut)
def registry_analytics(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    q: str | None = None,
    state: str | None = None,
    basin: str | None = None,
    risk: RiskClass | None = None,
    status_filter: DamStatus | None = Query(default=None, alias="status"),
) -> AnalyticsOut:
    filters = _build_filters(q=q, state=state, basin=basin, risk=risk, status_filter=status_filter)
    total = db.scalar(select(func.count()).select_from(Dam).where(*filters)) or 0
    critical = db.scalar(select(func.count()).select_from(Dam).where(*filters, Dam.risk_class == RiskClass.critical)) or 0
    high = db.scalar(select(func.count()).select_from(Dam).where(*filters, Dam.risk_class == RiskClass.high)) or 0
    overdue = db.scalar(select(func.count()).select_from(Dam).where(*filters, Dam.next_inspection_due < date.today())) or 0
    live_storage = (
        db.scalar(
            select(func.coalesce(func.sum(DamReservoir.live_storage_mcm), 0))
            .select_from(Dam)
            .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
            .where(*filters)
        )
        or 0
    )
    return AnalyticsOut(
        total_dams=total,
        critical_dams=critical,
        high_risk_dams=high,
        overdue_inspections=overdue,
        total_live_storage_mcm=float(live_storage),
        by_risk=_group_counts(db, Dam.risk_class, filters),
        by_status=_group_counts(db, Dam.status, filters),
        by_state=_group_counts(db, Dam.state, filters),
    )


@router.get("/important-dams")
def important_dams_analytics(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(get_current_user)],
    q: str | None = None,
    state: str | None = None,
    basin: str | None = None,
    risk: RiskClass | None = None,
    status_filter: DamStatus | None = Query(default=None, alias="status"),
) -> dict:
    filters = _build_filters(q=q, state=state, basin=basin, risk=risk, status_filter=status_filter)
    important_filter = or_(DamEngineering.height_m >= 100, DamReservoir.gross_storage_mcm >= 1000)
    base = (
        select(Dam)
        .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
        .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
        .where(*filters, important_filter)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    high_by_height = (
        db.scalar(
            select(func.count())
            .select_from(Dam)
            .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
            .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
            .where(*filters, important_filter, DamEngineering.height_m >= 100)
        )
        or 0
    )
    high_by_storage = (
        db.scalar(
            select(func.count())
            .select_from(Dam)
            .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
            .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
            .where(*filters, important_filter, DamReservoir.gross_storage_mcm >= 1000)
        )
        or 0
    )
    both = (
        db.scalar(
            select(func.count())
            .select_from(Dam)
            .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
            .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
            .where(*filters, DamEngineering.height_m >= 100, DamReservoir.gross_storage_mcm >= 1000)
        )
        or 0
    )
    totals = db.execute(
        select(
            func.coalesce(func.sum(DamReservoir.gross_storage_mcm), 0),
            func.coalesce(func.sum(DamReservoir.live_storage_mcm), 0),
            func.coalesce(func.max(DamEngineering.height_m), 0),
            func.coalesce(func.max(DamReservoir.gross_storage_mcm), 0),
        )
        .select_from(Dam)
        .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
        .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
        .where(*filters, important_filter)
    ).one()
    top_states = db.execute(
        select(Dam.state, func.count())
        .select_from(Dam)
        .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
        .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
        .where(*filters, important_filter)
        .group_by(Dam.state)
        .order_by(func.count().desc())
        .limit(6)
    ).all()
    top_basins = db.execute(
        select(Dam.river_basin, func.count())
        .select_from(Dam)
        .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
        .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
        .where(*filters, important_filter)
        .group_by(Dam.river_basin)
        .order_by(func.count().desc())
        .limit(6)
    ).all()
    rows = db.execute(
        select(
            Dam.dam_id,
            Dam.dam_name,
            Dam.state,
            Dam.district,
            Dam.river_basin,
            Dam.river_name,
            Dam.dam_type,
            Dam.construction_year,
            DamEngineering.height_m,
            DamEngineering.length_m,
            DamEngineering.spillway_capacity_cumecs,
            DamReservoir.gross_storage_mcm,
            DamReservoir.live_storage_mcm,
        )
        .select_from(Dam)
        .join(DamEngineering, DamEngineering.dam_id == Dam.dam_id, isouter=True)
        .join(DamReservoir, DamReservoir.dam_id == Dam.dam_id, isouter=True)
        .where(*filters, important_filter)
        .order_by(func.coalesce(DamEngineering.height_m, 0).desc(), func.coalesce(DamReservoir.gross_storage_mcm, 0).desc())
        .limit(250)
    ).all()
    wims_readings = _latest_wims_readings(db, [row._mapping for row in rows])
    items = []
    for row in rows:
        item = row._mapping
        wims = wims_readings.get(item["dam_id"])
        items.append(
            {
                "dam_id": item["dam_id"],
                "dam_name": item["dam_name"],
                "state": item["state"],
                "district": item["district"],
                "river_basin": item["river_basin"],
                "river_name": item["river_name"],
                "dam_type": item["dam_type"],
                "construction_year": item["construction_year"],
                "height_m": float(item["height_m"] or 0),
                "length_m": float(item["length_m"] or 0),
                "spillway_capacity_cumecs": float(item["spillway_capacity_cumecs"] or 0),
                "gross_storage_mcm": float(item["gross_storage_mcm"] or 0),
                "live_storage_mcm": float(item["live_storage_mcm"] or 0),
                "wims_current_storage_mcm": float(wims["current_storage_mcm"]) if wims and wims["current_storage_mcm"] is not None else None,
                "wims_storage_percent": float(wims["storage_percent"]) if wims and wims["storage_percent"] is not None else None,
                "wims_level_m": float(wims["level_m"]) if wims and wims["level_m"] is not None else None,
                "wims_observed_at": wims["observed_at"].isoformat() if wims and wims["observed_at"] else None,
                "wims_report_date": wims["report_date"].isoformat() if wims and wims["report_date"] else None,
                "wims_source_url": wims["source_url"] if wims else None,
                "wims_lookup_url": wims["source_url"] if wims else _wims_lookup_url(item["dam_name"]),
                "wims_reservoir_code": wims["reservoir_code"] if wims else None,
                "wims_source_registry": wims["source_registry"] if wims else None,
                "wims_is_stale": bool(wims["is_stale"]) if wims else False,
            }
        )
    items.sort(
        key=lambda item: (
            item["wims_current_storage_mcm"] is not None,
            item["height_m"],
            item["gross_storage_mcm"],
        ),
        reverse=True,
    )

    return {
        "source": "Reports/Dam with 100m ht.pdf",
        "criteria": "Height >= 100 m or gross storage >= 1 BCM",
        "total": total,
        "height_qualified": high_by_height,
        "storage_qualified": high_by_storage,
        "both_qualified": both,
        "gross_storage_mcm": float(totals[0] or 0),
        "live_storage_mcm": float(totals[1] or 0),
        "max_height_m": float(totals[2] or 0),
        "max_gross_storage_mcm": float(totals[3] or 0),
        "wims_linked_count": len(wims_readings),
        "by_state": [{"key": key or "Not set", "count": count} for key, count in top_states],
        "by_basin": [{"key": key or "Not set", "count": count} for key, count in top_basins],
        "items": items[:12],
    }


def _build_filters(
    q: str | None,
    state: str | None,
    basin: str | None,
    risk: RiskClass | None,
    status_filter: DamStatus | None,
) -> list:
    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(or_(Dam.dam_name.ilike(pattern), Dam.dam_id.ilike(pattern), Dam.state.ilike(pattern), Dam.river_basin.ilike(pattern)))
    if state:
        filters.append(Dam.state == state)
    if basin:
        filters.append(Dam.river_basin == basin)
    if risk:
        filters.append(Dam.risk_class == risk)
    if status_filter:
        filters.append(Dam.status == status_filter)
    return filters


def _group_counts(db: Session, column, filters: list) -> list[dict]:
    rows = db.execute(select(column, func.count()).select_from(Dam).where(*filters).group_by(column).order_by(func.count().desc())).all()
    return [{"key": str(key.value if hasattr(key, "value") else key), "count": count} for key, count in rows]


def _latest_wims_readings(db: Session, dams: list[dict]) -> dict[str, dict]:
    if not dams:
        return {}
    dam_ids = [dam["dam_id"] for dam in dams]
    rows = db.execute(
        text(
            """
            SELECT DISTINCT ON (dam_id)
              dam_id,
              source_registry,
              source_url,
              report_date,
              reservoir_code,
              this_year_live_capacity_mcm AS current_storage_mcm,
              this_year_live_storage_percent AS storage_percent,
              this_year_level_m AS level_m,
              this_year_level_observed_date AS observed_at,
              this_year_is_stale AS is_stale
            FROM mpwrd_reservoir_levels
            WHERE dam_id IN :dam_ids
            ORDER BY dam_id, report_date DESC, fetched_at DESC
            """
        ).bindparams(bindparam("dam_ids", expanding=True)),
        {"dam_ids": dam_ids},
    ).mappings()
    readings = {row["dam_id"]: dict(row) for row in rows}

    missing_mp_dams = [dam for dam in dams if dam["dam_id"] not in readings and dam["state"] == "Madhya Pradesh"]
    if not missing_mp_dams:
        return readings

    mp_rows = db.execute(
        text(
            """
            SELECT DISTINCT ON (dam_id)
              dam_id,
              source_registry,
              source_url,
              report_date,
              reservoir_code,
              reservoir_name,
              this_year_live_capacity_mcm AS current_storage_mcm,
              this_year_live_storage_percent AS storage_percent,
              this_year_level_m AS level_m,
              this_year_level_observed_date AS observed_at,
              this_year_is_stale AS is_stale
            FROM mpwrd_reservoir_levels
            ORDER BY dam_id, report_date DESC, fetched_at DESC
            """
        )
    ).mappings().all()
    candidates = [dict(row) | {"tokens": _name_tokens(row["reservoir_name"])} for row in mp_rows]
    for dam in missing_mp_dams:
        dam_tokens = _name_tokens(dam["dam_name"])
        dam_compact = _compact_name(dam["dam_name"])
        if not dam_tokens:
            continue
        best_match = None
        best_score = 0
        for candidate in candidates:
            candidate_compact = _compact_name(candidate["reservoir_name"])
            score = len(dam_tokens & candidate["tokens"]) * 2
            if dam_compact and (dam_compact in candidate_compact or candidate_compact in dam_compact):
                score += 6
            if dam_compact and SequenceMatcher(None, dam_compact, candidate_compact).ratio() >= 0.72:
                score += 5
            if score > best_score:
                best_score = score
                best_match = candidate
        if best_match and best_score >= 2:
            readings[dam["dam_id"]] = {key: value for key, value in best_match.items() if key != "tokens"}
    return readings


def _compact_name(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def _name_tokens(value: str | None) -> set[str]:
    ignored = {"dam", "tank", "project", "reservoir", "sagar", "minor", "major"}
    return {token for token in re.findall(r"[a-z0-9]+", (value or "").lower()) if len(token) > 2 and token not in ignored}


def _wims_lookup_url(dam_name: str | None) -> str:
    name = re.sub(r"\s+", "%20", (dam_name or "").strip())
    return f"https://indiawris.gov.in/wris/#/Reservoir?search={name}" if name else "https://indiawris.gov.in/wris/#/Reservoir"
