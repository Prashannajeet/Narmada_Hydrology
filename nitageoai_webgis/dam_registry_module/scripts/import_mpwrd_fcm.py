from __future__ import annotations

import argparse
import html
import json
import re
import ssl
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.request import Request, urlopen


SOURCE_REGISTRY = "MPWRD"
SOURCE_URL = "https://eims1.mpwrd.gov.in/fcmreport/control/main"


@dataclass
class ReservoirReading:
    report_date: date
    reservoir_code: str
    reservoir_name: str
    basin_office: str | None
    reading_time: str | None
    district: str | None
    frl_m: Decimal | None
    live_capacity_at_frl_mcm: Decimal | None
    this_year_level_m: Decimal | None
    this_year_live_capacity_mcm: Decimal | None
    this_year_live_storage_percent: Decimal | None
    this_year_level_observed_date: date | None
    this_year_is_stale: bool
    gate_count_open: Decimal | None
    gate_discharge_cumec: Decimal | None
    last_year_level_m: Decimal | None
    last_year_live_capacity_mcm: Decimal | None
    last_year_live_storage_percent: Decimal | None
    raw: dict[str, str | None]

    @property
    def dam_id(self) -> str:
        return f"MPWRD-{self.reservoir_code}"


TAG_RE = re.compile(r"<[^>]+>")
TD_RE = re.compile(r"<td\b[^>]*>(.*?)</td>", re.IGNORECASE | re.DOTALL)
TR_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
TIMEWISE_RE = re.compile(r"timewise\('([^']+)'\)")
SPAN_TITLE_RE = re.compile(r"<span\b[^>]*title=['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE)


def clean_cell(value: str) -> str:
    text = TAG_RE.sub(" ", value)
    text = html.unescape(text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    value = value.replace(",", "").replace("*", "").strip()
    if value.upper() in {"N/A", "N-A", "NA", "-"}:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", value)
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except InvalidOperation:
        return None


def parse_date(value: str) -> date:
    value = html.unescape(value).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Could not parse date: {value}")


def sql_text(value: str | None) -> str:
    if value is None or value == "":
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def sql_date(value: date | None) -> str:
    return sql_text(value.isoformat() if value else None)


def sql_num(value: Decimal | None) -> str:
    return "NULL" if value is None else str(value)


def sql_bool(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def risk_from_storage(percent: Decimal | None) -> str:
    if percent is None:
        return "moderate"
    if percent < 25:
        return "high"
    if percent < 50:
        return "moderate"
    return "low"


def safety_from_storage(percent: Decimal | None) -> Decimal:
    if percent is None:
        return Decimal("70.00")
    return max(Decimal("0.00"), min(Decimal("100.00"), percent)).quantize(Decimal("0.01"))


def fetch_html(url: str) -> str:
    request = Request(url, headers={"User-Agent": "NitageoAI MPWRD importer/1.0"})
    context = ssl._create_unverified_context()
    with urlopen(request, timeout=45, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_report(page: str) -> list[ReservoirReading]:
    report_match = re.search(r"Report as on\s*([0-9]{2}&#47;[0-9]{2}&#47;[0-9]{4})", page)
    if not report_match:
        raise ValueError("Could not find report date in MPWRD page")
    report_date = parse_date(report_match.group(1))

    all_reservoirs = page.split('<div class="tabcontent paddingAll" id="TWO"', 1)[0]
    readings: list[ReservoirReading] = []
    current_basin: str | None = None

    for row_html in TR_RE.findall(all_reservoirs):
        basin_match = TIMEWISE_RE.search(row_html)
        if basin_match:
            current_basin = html.unescape(basin_match.group(1)).strip()
            continue

        cells_html = TD_RE.findall(row_html)
        cells = [clean_cell(cell) for cell in cells_html]
        if len(cells) < 15 or not re.fullmatch(r"\d+\.?", cells[0]):
            continue
        if cells[:15] == [str(index) for index in range(1, 16)]:
            continue

        name_cell = cells[1]
        code_match = re.search(r"\[([0-9A-Za-z_-]+)\]\s*$", name_cell)
        code = code_match.group(1) if code_match else re.sub(r"\W+", "-", name_cell).strip("-").upper()
        name = re.sub(r"\s*\[[^\]]+\]\s*$", "", name_cell).strip()
        observed_date_match = SPAN_TITLE_RE.search(cells_html[6])
        observed_date = parse_date(observed_date_match.group(1)) if observed_date_match else report_date

        raw = {
            "serial": cells[0],
            "reservoir": cells[1],
            "time": cells[2],
            "district": cells[3],
            "frl_m": cells[4],
            "live_capacity_at_frl_mcm": cells[5],
            "this_year_level_m": cells[6],
            "this_year_live_capacity_mcm": cells[7],
            "this_year_live_storage_percent": cells[8],
            "gate_count_open": cells[10],
            "gate_discharge_cumec": cells[11],
            "last_year_level_m": cells[12],
            "last_year_live_capacity_mcm": cells[13],
            "last_year_live_storage_percent": cells[14],
        }
        readings.append(
            ReservoirReading(
                report_date=report_date,
                reservoir_code=code,
                reservoir_name=name,
                basin_office=current_basin,
                reading_time=cells[2] or None,
                district=cells[3] or None,
                frl_m=parse_decimal(cells[4]),
                live_capacity_at_frl_mcm=parse_decimal(cells[5]),
                this_year_level_m=parse_decimal(cells[6]),
                this_year_live_capacity_mcm=parse_decimal(cells[7]),
                this_year_live_storage_percent=parse_decimal(cells[8]),
                this_year_level_observed_date=observed_date,
                this_year_is_stale=observed_date != report_date or "*" in cells[6],
                gate_count_open=parse_decimal(cells[10]),
                gate_discharge_cumec=parse_decimal(cells[11]),
                last_year_level_m=parse_decimal(cells[12]),
                last_year_live_capacity_mcm=parse_decimal(cells[13]),
                last_year_live_storage_percent=parse_decimal(cells[14]),
                raw=raw,
            )
        )

    code_counts = Counter(reading.reservoir_code for reading in readings)
    for reading in readings:
        if code_counts[reading.reservoir_code] > 1:
            serial = str(reading.raw.get("serial") or "").replace(".", "").strip()
            reading.raw["mpwrd_reservoir_code"] = reading.reservoir_code
            reading.reservoir_code = f"{reading.reservoir_code}-{serial}"

    return readings


def build_sql(readings: list[ReservoirReading]) -> str:
    lines = [
        "BEGIN;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_registry TEXT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_record_id TEXT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_publication_year INT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_url TEXT;",
        Path("database/init/003_mpwrd_reservoir_levels.sql").read_text(encoding="utf-8"),
        f"DELETE FROM mpwrd_reservoir_levels WHERE source_registry = '{SOURCE_REGISTRY}';",
        f"DELETE FROM dams WHERE source_registry = '{SOURCE_REGISTRY}';",
    ]

    for item in readings:
        risk = risk_from_storage(item.this_year_live_storage_percent)
        safety = safety_from_storage(item.this_year_live_storage_percent)
        raw_json = json.dumps(item.raw, ensure_ascii=False, sort_keys=True)
        instrumentation_json = json.dumps(
            {
                "basin_office": item.basin_office,
                "mpwrd_reservoir_code": item.reservoir_code,
                "reading_time": item.reading_time,
                "this_year_level_observed_date": item.this_year_level_observed_date.isoformat()
                if item.this_year_level_observed_date
                else None,
                "this_year_is_stale": item.this_year_is_stale,
                "gate_count_open": str(item.gate_count_open) if item.gate_count_open is not None else None,
                "gate_discharge_cumec": str(item.gate_discharge_cumec) if item.gate_discharge_cumec is not None else None,
                "last_year_level_m": str(item.last_year_level_m) if item.last_year_level_m is not None else None,
                "last_year_live_capacity_mcm": str(item.last_year_live_capacity_mcm)
                if item.last_year_live_capacity_mcm is not None
                else None,
                "last_year_live_storage_percent": str(item.last_year_live_storage_percent)
                if item.last_year_live_storage_percent is not None
                else None,
            },
            sort_keys=True,
        )
        lines.append(
            "INSERT INTO dams "
            "(dam_id, dam_name, state, district, river_basin, owner_agency, status, risk_class, safety_score, "
            "source_registry, source_record_id, source_publication_year, source_url, updated_at) VALUES "
            f"({sql_text(item.dam_id)}, {sql_text(item.reservoir_name)}, 'Madhya Pradesh', {sql_text(item.district)}, "
            f"{sql_text(item.basin_office)}, 'Madhya Pradesh Water Resources Department', 'operational'::dam_status, "
            f"'{risk}'::risk_class, {sql_num(safety)}, '{SOURCE_REGISTRY}', {sql_text(item.reservoir_code)}, "
            f"{item.report_date.year}, {sql_text(SOURCE_URL)}, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET "
            "dam_name = EXCLUDED.dam_name, state = EXCLUDED.state, district = EXCLUDED.district, "
            "river_basin = EXCLUDED.river_basin, owner_agency = EXCLUDED.owner_agency, status = EXCLUDED.status, "
            "risk_class = EXCLUDED.risk_class, safety_score = EXCLUDED.safety_score, "
            "source_registry = EXCLUDED.source_registry, source_record_id = EXCLUDED.source_record_id, "
            "source_publication_year = EXCLUDED.source_publication_year, source_url = EXCLUDED.source_url, updated_at = now();"
        )
        lines.append(
            "INSERT INTO dam_reservoir "
            "(dam_id, reservoir_name, live_storage_mcm, current_storage_mcm, frl_m, updated_at) VALUES "
            f"({sql_text(item.dam_id)}, {sql_text(item.reservoir_name)}, {sql_num(item.live_capacity_at_frl_mcm)}, "
            f"{sql_num(item.this_year_live_capacity_mcm)}, {sql_num(item.frl_m)}, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET "
            "reservoir_name = EXCLUDED.reservoir_name, live_storage_mcm = EXCLUDED.live_storage_mcm, "
            "current_storage_mcm = EXCLUDED.current_storage_mcm, frl_m = EXCLUDED.frl_m, updated_at = now();"
        )
        lines.append(
            "INSERT INTO dam_engineering (dam_id, instrumentation, updated_at) VALUES "
            f"({sql_text(item.dam_id)}, {sql_text(instrumentation_json)}::jsonb, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET instrumentation = EXCLUDED.instrumentation, updated_at = now();"
        )
        lines.append(
            "INSERT INTO mpwrd_reservoir_levels "
            "(source_registry, report_date, reservoir_code, dam_id, basin_office, reservoir_name, reading_time, district, "
            "frl_m, live_capacity_at_frl_mcm, this_year_level_m, this_year_live_capacity_mcm, this_year_live_storage_percent, "
            "this_year_level_observed_date, this_year_is_stale, gate_count_open, gate_discharge_cumec, last_year_level_m, "
            "last_year_live_capacity_mcm, last_year_live_storage_percent, source_url, raw, fetched_at) VALUES "
            f"('{SOURCE_REGISTRY}', {sql_date(item.report_date)}, {sql_text(item.reservoir_code)}, {sql_text(item.dam_id)}, "
            f"{sql_text(item.basin_office)}, {sql_text(item.reservoir_name)}, {sql_text(item.reading_time)}, {sql_text(item.district)}, "
            f"{sql_num(item.frl_m)}, {sql_num(item.live_capacity_at_frl_mcm)}, {sql_num(item.this_year_level_m)}, "
            f"{sql_num(item.this_year_live_capacity_mcm)}, {sql_num(item.this_year_live_storage_percent)}, "
            f"{sql_date(item.this_year_level_observed_date)}, {sql_bool(item.this_year_is_stale)}, "
            f"{sql_num(item.gate_count_open)}, {sql_num(item.gate_discharge_cumec)}, {sql_num(item.last_year_level_m)}, "
            f"{sql_num(item.last_year_live_capacity_mcm)}, {sql_num(item.last_year_live_storage_percent)}, "
            f"{sql_text(SOURCE_URL)}, {sql_text(raw_json)}::jsonb, now()) "
            "ON CONFLICT (source_registry, report_date, reservoir_code) DO UPDATE SET "
            "dam_id = EXCLUDED.dam_id, basin_office = EXCLUDED.basin_office, reservoir_name = EXCLUDED.reservoir_name, "
            "reading_time = EXCLUDED.reading_time, district = EXCLUDED.district, frl_m = EXCLUDED.frl_m, "
            "live_capacity_at_frl_mcm = EXCLUDED.live_capacity_at_frl_mcm, this_year_level_m = EXCLUDED.this_year_level_m, "
            "this_year_live_capacity_mcm = EXCLUDED.this_year_live_capacity_mcm, "
            "this_year_live_storage_percent = EXCLUDED.this_year_live_storage_percent, "
            "this_year_level_observed_date = EXCLUDED.this_year_level_observed_date, "
            "this_year_is_stale = EXCLUDED.this_year_is_stale, gate_count_open = EXCLUDED.gate_count_open, "
            "gate_discharge_cumec = EXCLUDED.gate_discharge_cumec, last_year_level_m = EXCLUDED.last_year_level_m, "
            "last_year_live_capacity_mcm = EXCLUDED.last_year_live_capacity_mcm, "
            "last_year_live_storage_percent = EXCLUDED.last_year_live_storage_percent, source_url = EXCLUDED.source_url, "
            "raw = EXCLUDED.raw, fetched_at = now();"
        )

    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Import MPWRD FCM reservoir readings into NITA dam registry SQL.")
    parser.add_argument("--html", type=Path, help="Saved MPWRD HTML file. If omitted, fetches the live page.")
    parser.add_argument("--out", type=Path, default=Path("data/mpwrd_fcm_import.sql"))
    args = parser.parse_args()

    page = args.html.read_text(encoding="utf-8", errors="replace") if args.html else fetch_html(SOURCE_URL)
    readings = parse_report(page)
    if not readings:
        raise SystemExit("No MPWRD reservoir rows were parsed")
    args.out.write_text(build_sql(readings), encoding="utf-8")
    print(f"Parsed {len(readings)} MPWRD reservoirs for {readings[0].report_date.isoformat()} -> {args.out}")


if __name__ == "__main__":
    main()
