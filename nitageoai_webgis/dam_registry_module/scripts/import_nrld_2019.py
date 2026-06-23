from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from import_nrld_2023 import (
    SOURCE_REGISTRY,
    clean_text,
    parse_coord,
    parse_decimal,
    parse_year,
    risk_from_metrics,
    sql_num,
    sql_text,
)


SOURCE_URL = "https://cwc.gov.in/sites/default/files/nrld-2019.pdf"
SOURCE_YEAR = 2019

STATE_BY_PIC = {
    "AN": "Andaman and Nicobar Islands",
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chhattisgarh",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "OD": "Odisha",
    "PB": "Punjab",
    "PJ": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TG": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "UA": "Uttarakhand",
    "WB": "West Bengal",
}

COLUMNS = {
    "serial": (84, 112),
    "pic": (112, 145),
    "name": (145, 187),
    "owner": (187, 235),
    "lat": (235, 263),
    "lon": (263, 281),
    "year": (281, 309),
    "basin": (309, 375),
    "river": (375, 414),
    "city": (414, 453),
    "zone": (453, 465),
    "type": (465, 545),
    "height": (545, 586),
    "length": (586, 606),
    "volume": (606, 631),
    "gross": (631, 660),
    "area": (660, 686),
    "live": (686, 730),
    "purpose": (730, 748),
    "spillway": (748, 790),
}

PIC_RE = re.compile(r"^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$")


def ordered_text(items: list[tuple[float, float, str]]) -> str | None:
    if not items:
        return None
    return clean_text(" ".join(text for y, x, text in sorted(items, key=lambda item: (-item[0], item[1]))))


def collect(items: list[tuple[float, float, str]], column: str) -> str | None:
    x_min, x_max = COLUMNS[column]
    return ordered_text([(y, x, text) for y, x, text in items if x_min <= x < x_max])


def first_number(value: str | None) -> Decimal | None:
    if not value:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", value.replace(",", ""))
    return parse_decimal(match.group(0)) if match else None


def m3_to_mcm(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return (value / Decimal(1000000)).quantize(Decimal("0.001"))


def bounded_metric(value: Decimal | None, maximum: Decimal) -> Decimal | None:
    if value is None or value < 0 or value > maximum:
        return None
    return value


def year_from_column(value: str | None) -> tuple[int | None, str]:
    if not value:
        return None, "operational"
    if value.strip().lower() == "uc":
        return None, "proposed"
    candidates = re.findall(r"(?:18|19|20)\d{2}", value)
    return parse_year(candidates[-1]) if candidates else (None, "operational")


def state_from_pic(pic: str) -> str | None:
    return STATE_BY_PIC.get(pic[:2])


def extract_page_items(page: Any) -> list[tuple[float, float, str]]:
    items: list[tuple[float, float, str]] = []

    def visitor(text: str, _cm: Any, tm: Any, _font_dict: Any, _font_size: float) -> None:
        cleaned = clean_text(text.replace("\n", " "))
        if cleaned:
            items.append((float(tm[5]), float(tm[4]), cleaned))

    page.extract_text(visitor_text=visitor)
    return items


def parse_page(page: Any) -> list[dict[str, Any]]:
    items = extract_page_items(page)
    anchors = sorted(
        [(y, x, text) for y, x, text in items if COLUMNS["serial"][0] <= x < COLUMNS["serial"][1] and text.isdigit()],
        key=lambda item: item[0],
        reverse=True,
    )
    records: list[dict[str, Any]] = []
    for index, (row_y, _x, serial_text) in enumerate(anchors):
        lower_bound = anchors[index + 1][0] + 1 if index + 1 < len(anchors) else 40
        upper_bound = anchors[index - 1][0] - 1 if index > 0 else row_y + 22
        block = [(y, x, text) for y, x, text in items if lower_bound < y <= upper_bound]
        pic = collect(block, "pic")
        if not pic:
            continue
        pic = re.sub(r"[^A-Z0-9]", "", pic.upper())
        if not PIC_RE.match(pic):
            continue
        dam_name = collect(block, "name")
        state = state_from_pic(pic)
        if not dam_name or not state:
            continue
        construction_year, status = year_from_column(collect(block, "year"))
        height_m = bounded_metric(first_number(collect(block, "height")), Decimal(350))
        length_m = bounded_metric(first_number(collect(block, "length")), Decimal(20000))
        gross_storage_mcm = m3_to_mcm(first_number(collect(block, "gross")))
        live_storage_mcm = m3_to_mcm(first_number(collect(block, "live")))
        spillway_capacity = bounded_metric(first_number(collect(block, "spillway")), Decimal(200000))
        latitude = parse_coord(collect(block, "lat"), is_lon=False)
        longitude = parse_coord(collect(block, "lon"), is_lon=True)
        risk_class = risk_from_metrics(height_m, gross_storage_mcm)
        records.append(
            {
                "serial_no": int(serial_text),
                "dam_id": pic,
                "source_record_id": pic,
                "dam_name": dam_name[:240],
                "state": state,
                "district": collect(block, "city"),
                "river_basin": collect(block, "basin"),
                "river_name": collect(block, "river"),
                "owner_agency": collect(block, "owner"),
                "dam_type": collect(block, "type"),
                "construction_year": construction_year,
                "status": status,
                "risk_class": risk_class,
                "safety_score": Decimal("70.00"),
                "latitude": latitude,
                "longitude": longitude,
                "height_m": height_m,
                "length_m": length_m,
                "spillway_capacity_cumecs": spillway_capacity,
                "foundation_type": collect(block, "type"),
                "seismic_zone": collect(block, "zone"),
                "reservoir_name": f"{dam_name} Reservoir"[:240],
                "gross_storage_mcm": gross_storage_mcm,
                "live_storage_mcm": live_storage_mcm,
                "current_storage_mcm": None,
                "extra": {
                    "nrld_serial_no": int(serial_text),
                    "volume_content_m3": str(first_number(collect(block, "volume"))) if first_number(collect(block, "volume")) else None,
                    "reservoir_area_m2": str(first_number(collect(block, "area"))) if first_number(collect(block, "area")) else None,
                    "purpose": collect(block, "purpose"),
                },
            }
        )
    return records


def parse_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(pdf_path))
    records: dict[str, dict[str, Any]] = {}
    for page_number, page in enumerate(reader.pages, start=1):
        if page_number < 57 or page_number > 287:
            continue
        for record in parse_page(page):
            records[record["dam_id"]] = record
    return sorted(records.values(), key=lambda row: (row["state"], row["serial_no"], row["dam_id"]))


def write_sql(records: list[dict[str, Any]], output_path: Path, *, replace_seed: bool) -> None:
    lines: list[str] = [
        "BEGIN;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_registry TEXT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_record_id TEXT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_publication_year INT;",
        "ALTER TABLE dams ADD COLUMN IF NOT EXISTS source_url TEXT;",
        "CREATE INDEX IF NOT EXISTS idx_dams_source_registry ON dams(source_registry, source_publication_year);",
    ]
    if replace_seed:
        lines.append("DELETE FROM dams WHERE dam_id IN ('DAM-MP-0001', 'DAM-MP-0002', 'DAM-MH-0001');")

    for record in records:
        lines.append(
            "INSERT INTO dams (dam_id, dam_name, state, district, river_basin, river_name, owner_agency, dam_type, "
            "construction_year, status, risk_class, safety_score, source_registry, source_record_id, "
            "source_publication_year, source_url, updated_at) VALUES ("
            f"{sql_text(record['dam_id'])}, {sql_text(record['dam_name'])}, {sql_text(record['state'])}, "
            f"{sql_text(record['district'])}, {sql_text(record['river_basin'])}, {sql_text(record['river_name'])}, "
            f"{sql_text(record['owner_agency'])}, {sql_text(record['dam_type'])}, {sql_num(record['construction_year'])}, "
            f"{sql_text(record['status'])}::dam_status, {sql_text(record['risk_class'])}::risk_class, {sql_num(record['safety_score'])}, "
            f"{sql_text(SOURCE_REGISTRY)}, {sql_text(record['source_record_id'])}, {SOURCE_YEAR}, {sql_text(SOURCE_URL)}, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET "
            "dam_name = EXCLUDED.dam_name, state = EXCLUDED.state, district = EXCLUDED.district, "
            "river_basin = EXCLUDED.river_basin, river_name = EXCLUDED.river_name, owner_agency = EXCLUDED.owner_agency, "
            "dam_type = EXCLUDED.dam_type, construction_year = EXCLUDED.construction_year, status = EXCLUDED.status, "
            "risk_class = EXCLUDED.risk_class, safety_score = EXCLUDED.safety_score, source_registry = EXCLUDED.source_registry, "
            "source_record_id = EXCLUDED.source_record_id, source_publication_year = EXCLUDED.source_publication_year, "
            "source_url = EXCLUDED.source_url, updated_at = now();"
        )
        lines.append(
            "INSERT INTO dam_engineering (dam_id, height_m, length_m, spillway_capacity_cumecs, foundation_type, seismic_zone, instrumentation, updated_at) "
            "VALUES ("
            f"{sql_text(record['dam_id'])}, {sql_num(record['height_m'])}, {sql_num(record['length_m'])}, "
            f"{sql_num(record['spillway_capacity_cumecs'])}, {sql_text(record['foundation_type'])}, "
            f"{sql_text(record['seismic_zone'])}, {sql_text(json.dumps(record['extra'], sort_keys=True))}::jsonb, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET height_m = EXCLUDED.height_m, length_m = EXCLUDED.length_m, "
            "spillway_capacity_cumecs = EXCLUDED.spillway_capacity_cumecs, foundation_type = EXCLUDED.foundation_type, "
            "seismic_zone = EXCLUDED.seismic_zone, instrumentation = EXCLUDED.instrumentation, updated_at = now();"
        )
        lines.append(
            "INSERT INTO dam_reservoir (dam_id, reservoir_name, gross_storage_mcm, live_storage_mcm, current_storage_mcm, updated_at) "
            "VALUES ("
            f"{sql_text(record['dam_id'])}, {sql_text(record['reservoir_name'])}, {sql_num(record['gross_storage_mcm'])}, "
            f"{sql_num(record['live_storage_mcm'])}, {sql_num(record['current_storage_mcm'])}, now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET reservoir_name = EXCLUDED.reservoir_name, "
            "gross_storage_mcm = EXCLUDED.gross_storage_mcm, live_storage_mcm = EXCLUDED.live_storage_mcm, "
            "current_storage_mcm = EXCLUDED.current_storage_mcm, updated_at = now();"
        )
        point_sql = (
            "NULL"
            if record["latitude"] is None or record["longitude"] is None
            else f"ST_SetSRID(ST_MakePoint({record['longitude']}, {record['latitude']}), 4326)"
        )
        lines.append(
            "INSERT INTO dam_geometry (dam_id, dam_point, source_file_name, source_format, uploaded_at) "
            f"VALUES ({sql_text(record['dam_id'])}, {point_sql}, 'nrld-2019.pdf', 'CWC PDF positioned text extraction', now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET dam_point = EXCLUDED.dam_point, source_file_name = EXCLUDED.source_file_name, "
            "source_format = EXCLUDED.source_format, uploaded_at = now();"
        )

    lines.extend(["COMMIT;", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract CWC NRLD 2019 PDF rows into an idempotent PostGIS SQL import.")
    parser.add_argument("--pdf", default="data/nrld-2019.pdf", type=Path)
    parser.add_argument("--out", default="data/nrld_2019_import.sql", type=Path)
    parser.add_argument("--keep-seed", action="store_true")
    args = parser.parse_args()
    records = parse_pdf(args.pdf)
    write_sql(records, args.out, replace_seed=not args.keep_seed)
    summary = {
        "source": SOURCE_URL,
        "publication_year": SOURCE_YEAR,
        "records": len(records),
        "with_geometry": sum(1 for record in records if record["latitude"] and record["longitude"]),
        "states": sorted({record["state"] for record in records}),
    }
    args.out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} NRLD records to {args.out}")


if __name__ == "__main__":
    main()
