from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from pypdf import PdfReader


SOURCE_URL = "https://cwc.gov.in/publication/nrld"
SOURCE_REGISTRY = "CWC NRLD"
SOURCE_YEAR = 2023

STATE_ALIASES = {
    "Andhra Pradesh": "Andhra Pradesh",
    "Arunachal Pradesh": "Arunachal Pradesh",
    "Assam": "Assam",
    "Bihar": "Bihar",
    "Chhattisgarh": "Chhattisgarh",
    "Goa": "Goa",
    "Gujarat": "Gujarat",
    "Haryana": "Haryana",
    "Himachal Pradesh": "Himachal Pradesh",
    "Jharkhand": "Jharkhand",
    "Karnataka": "Karnataka",
    "Kerala": "Kerala",
    "Madhya Pradesh": "Madhya Pradesh",
    "Maharashtra": "Maharashtra",
    "Manipur": "Manipur",
    "Meghalaya": "Meghalaya",
    "Mizoram": "Mizoram",
    "Nagaland": "Nagaland",
    "Odisha": "Odisha",
    "Orissa": "Odisha",
    "Punjab": "Punjab",
    "Rajasthan": "Rajasthan",
    "Sikkim": "Sikkim",
    "Tamil Nadu": "Tamil Nadu",
    "Telangana": "Telangana",
    "Tripura": "Tripura",
    "Uttar Pradesh": "Uttar Pradesh",
    "Uttarakhand": "Uttarakhand",
    "West Bengal": "West Bengal",
}

STATE_OCR = {
    "Aseam": "Assam",
    "Chhatllagam": "Chhattisgarh",
    "Chhatllsgam": "Chhattisgarh",
    "Chhattisgartl": "Chhattisgarh",
    "GuJaret": "Gujarat",
    "GuJarat": "Gujarat",
    "Gujaret": "Gujarat",
    "Gujarel": "Gujarat",
    "UUarakhand": "Uttarakhand",
    "UUar Pradesh": "Uttar Pradesh",
    "UUat Pradesh": "Uttar Pradesh",
    "Wast Bengal": "West Bengal",
}

OWNER_MARKERS = (
    "Department",
    "Corporation",
    "Limited",
    "Authority",
    "Board",
    "Nigam",
    "UPIWRD",
    "WRD",
    "Irrigation",
    "Water",
    "Resources",
    "Government",
    "Municipal",
    "Hydro",
    "Power",
    "Project",
    "BBMB",
    "NHPC",
    "DVC",
)

ROW_START_RE = re.compile(r"(?m)(?=^\d{1,5}\s+)")
HEADER_STATE_RE = re.compile(r"NRLD'23\s+(.+?)\s+National Dam Safety", re.I)
PIC_RE = re.compile(r"\b[A-Z]{2}[A-Z0-9oOlIl]{2,4}[A-Z]{0,2}[A-Z0-9oOlIl]{3,7}\b")
DECIMAL_COORD_RE = re.compile(
    r"(?P<lat>\d{1,2}\.\d+)\s+(?P<lon>\d{2,3}\.\d+)\s+(?P<year>\d{4}|[uU][cC])\b"
)
DMS_COORD_RE = re.compile(
    r"(?P<lat>\d{1,2}\s*[\"'°\.]\s*\d{1,2}\s*[\"'°\.]\s*\d{1,2}(?:\.\d+)?\s*[\"']?\s*[Nn]?)"
    r"\s+"
    r"(?P<lon>\d{2,3}\s*[\"'°\.]\s*\d{1,2}\s*[\"'°\.]\s*\d{1,2}(?:\.\d+)?\s*[\"']?\s*[Ee]?)"
    r"(?:\s+\.\s+\.)?\s+(?P<year>\d{4}|[uU][cC])\b"
)
NUMBER_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:E[+-]?\d+)?", re.I)
YEAR_MIN = 1800
YEAR_MAX = 2026
COORD_HINT_RE = re.compile(r"\d{1,3}\s*[\"'°]\s*\d{1,2}\s*[\"'°]")
ROMAN_ZONES = {"I", "II", "III", "IV", "V"}
ROW_NO_X_MIN = 125
ROW_NO_X_MAX = 156
ROW_TOP_PADDING = 26


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\s+", " ", value)
    value = value.replace(" ,", ",").strip(" ;,")
    return value or None


def sql_text(value: str | None) -> str:
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def sql_num(value: Decimal | int | float | None) -> str:
    if value is None:
        return "NULL"
    return str(value)


def parse_decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    value = value.replace(",", "")
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def parse_year(value: str | None) -> tuple[int | None, str]:
    if not value or value.lower() == "uc":
        return None, "proposed"
    year = int(value)
    if YEAR_MIN <= year <= YEAR_MAX:
        return year, "operational"
    return None, "operational"


def parse_coord(value: str | None, *, is_lon: bool) -> Decimal | None:
    if not value:
        return None
    raw = value.strip().upper().replace("O", "0")
    sign = -1 if ("S" in raw or "W" in raw) else 1
    nums = [Decimal(part) for part in re.findall(r"\d+(?:\.\d+)?", raw)]
    if not nums:
        return None
    if len(nums) == 1:
        coord = nums[0]
    elif len(nums) == 2:
        coord = nums[0] + (nums[1] / Decimal(60))
    else:
        coord = nums[0] + (nums[1] / Decimal(60)) + (nums[2] / Decimal(3600))
    coord *= sign
    if is_lon and not (Decimal(60) <= coord <= Decimal(100)):
        return None
    if not is_lon and not (Decimal(5) <= coord <= Decimal(40)):
        return None
    return coord.quantize(Decimal("0.000001"))


def normalize_state(candidate: str | None, page_state: str | None) -> str | None:
    if candidate:
        compact = clean_text(candidate)
        if compact in STATE_OCR:
            return STATE_OCR[compact]
        if compact in STATE_ALIASES:
            return STATE_ALIASES[compact]
    return page_state


def page_state(text: str) -> str | None:
    first_line = (text.splitlines() or [""])[0]
    match = HEADER_STATE_RE.search(first_line)
    if not match:
        return None
    candidate = clean_text(match.group(1))
    if not candidate:
        return None
    for state in sorted(STATE_ALIASES, key=len, reverse=True):
        if state.lower() in candidate.lower():
            return STATE_ALIASES[state]
    return candidate if candidate not in {"Important Dams of India", "Dams for which NDSA is SDSO"} else None


def normalize_pic(value: str | None, serial_no: int) -> str:
    if not value:
        return f"NRLD2023-{serial_no:05d}"
    normalized = (
        value.upper()
        .replace("O", "0")
        .replace("I", "1")
        .replace("L", "1")
        .replace("|", "1")
    )
    normalized = re.sub(r"[^A-Z0-9]", "", normalized)
    if len(normalized) < 8:
        return f"NRLD2023-{serial_no:05d}"
    return normalized[:20]


def split_name_owner(value: str | None) -> tuple[str | None, str | None]:
    value = clean_text(value)
    if not value:
        return None, None
    marker_positions = [value.find(marker) for marker in OWNER_MARKERS if value.find(marker) > 4]
    if marker_positions:
        position = min(marker_positions)
        return clean_text(value[:position]), clean_text(value[position:])
    words = value.split()
    if len(words) > 8:
        return clean_text(" ".join(words[:6])), clean_text(" ".join(words[6:]))
    return value, None


def risk_from_metrics(height: Decimal | None, gross_storage: Decimal | None) -> str:
    if (height and height >= Decimal(100)) or (gross_storage and gross_storage >= Decimal(1000)):
        return "high"
    if (height and height >= Decimal(50)) or (gross_storage and gross_storage >= Decimal(100)):
        return "moderate"
    return "low"


def extract_tail_metrics(rest: str) -> dict[str, Any]:
    tokens = rest.split()
    number_matches = list(NUMBER_RE.finditer(rest))
    metrics: dict[str, Any] = {
        "river_basin": None,
        "river_name": None,
        "district": None,
        "seismic_zone": None,
        "foundation_type": None,
        "height_m": None,
        "length_m": None,
        "volume_content": None,
        "gross_storage_mcm": None,
        "reservoir_area_sqkm": None,
        "live_storage_mcm": None,
        "purpose": None,
        "spillway_capacity_cumecs": None,
    }
    if len(number_matches) < 2:
        return metrics

    numeric_values = [parse_decimal(match.group(0)) for match in number_matches]
    numeric_values = [value for value in numeric_values if value is not None]
    if len(numeric_values) >= 7:
        metrics["height_m"] = numeric_values[-7]
        metrics["length_m"] = numeric_values[-6]
        metrics["volume_content"] = numeric_values[-5]
        metrics["gross_storage_mcm"] = numeric_values[-4]
        metrics["reservoir_area_sqkm"] = numeric_values[-3]
        metrics["live_storage_mcm"] = numeric_values[-2]
        metrics["spillway_capacity_cumecs"] = numeric_values[-1]
        first_metric_pos = number_matches[-7].start()
    elif len(numeric_values) >= 4:
        metrics["height_m"] = numeric_values[-4]
        metrics["length_m"] = numeric_values[-3]
        metrics["gross_storage_mcm"] = numeric_values[-2]
        metrics["spillway_capacity_cumecs"] = numeric_values[-1]
        first_metric_pos = number_matches[-4].start()
    else:
        first_metric_pos = number_matches[0].start()

    before_metrics = rest[:first_metric_pos].strip()
    after_live = rest[number_matches[-2].end() : number_matches[-1].start()].strip() if len(number_matches) >= 7 else ""
    metrics["purpose"] = clean_text(after_live)

    before_tokens = before_metrics.split()
    zone_index = None
    for idx, token in enumerate(before_tokens):
        token_clean = token.strip(".,;").upper()
        if token_clean in ROMAN_ZONES:
            zone_index = idx
    if zone_index is not None:
        metrics["seismic_zone"] = before_tokens[zone_index].strip(".,;").upper()
        river_tokens = before_tokens[:zone_index]
        type_tokens = before_tokens[zone_index + 1 :]
        metrics["foundation_type"] = clean_text(" ".join(type_tokens))
    else:
        river_tokens = before_tokens

    if len(river_tokens) >= 3:
        metrics["district"] = clean_text(river_tokens[-1])
        metrics["river_name"] = clean_text(river_tokens[-2])
        metrics["river_basin"] = clean_text(" ".join(river_tokens[:-2]))
    elif len(river_tokens) == 2:
        metrics["river_name"] = clean_text(river_tokens[1])
        metrics["river_basin"] = clean_text(river_tokens[0])
    elif len(river_tokens) == 1:
        metrics["river_basin"] = clean_text(river_tokens[0])

    return metrics


def parse_row(chunk: str, page_state_name: str | None) -> dict[str, Any] | None:
    chunk = clean_text(chunk)
    if not chunk:
        return None
    row_match = re.match(r"^(?P<serial>\d{1,5})\s+(?P<body>.+)$", chunk)
    if not row_match:
        return None
    serial_no = int(row_match.group("serial"))
    body = row_match.group("body")

    coord_match = DECIMAL_COORD_RE.search(body) or DMS_COORD_RE.search(body)
    if not coord_match:
        return None

    before_coords = body[: coord_match.start()].strip()
    rest = body[coord_match.end() :].strip()
    year_value = coord_match.group("year")
    construction_year, status = parse_year(year_value)

    pic_match = PIC_RE.search(before_coords)
    pic_raw = pic_match.group(0) if pic_match else None
    dam_id = normalize_pic(pic_raw, serial_no)

    state_prefix = before_coords[: pic_match.start()].strip() if pic_match else ""
    state_name = normalize_state(state_prefix, page_state_name)
    name_owner = before_coords[pic_match.end() :].strip() if pic_match else before_coords
    dam_name, owner_agency = split_name_owner(name_owner)
    if not state_name or not dam_name:
        return None

    latitude = parse_coord(coord_match.group("lat"), is_lon=False)
    longitude = parse_coord(coord_match.group("lon"), is_lon=True)
    tail = extract_tail_metrics(rest)
    risk_class = risk_from_metrics(tail["height_m"], tail["gross_storage_mcm"])

    return {
        "serial_no": serial_no,
        "dam_id": dam_id,
        "source_record_id": pic_raw or f"Serial {serial_no}",
        "dam_name": dam_name[:240],
        "state": state_name,
        "district": tail["district"],
        "river_basin": tail["river_basin"],
        "river_name": tail["river_name"],
        "owner_agency": owner_agency,
        "dam_type": tail["foundation_type"],
        "construction_year": construction_year,
        "status": status,
        "risk_class": risk_class,
        "safety_score": Decimal("70.00"),
        "latitude": latitude,
        "longitude": longitude,
        "height_m": tail["height_m"],
        "length_m": tail["length_m"],
        "spillway_capacity_cumecs": tail["spillway_capacity_cumecs"],
        "foundation_type": tail["foundation_type"],
        "seismic_zone": tail["seismic_zone"],
        "reservoir_name": f"{dam_name} Reservoir"[:240],
        "gross_storage_mcm": tail["gross_storage_mcm"],
        "live_storage_mcm": tail["live_storage_mcm"],
        "current_storage_mcm": None,
        "extra": {
            "nrld_serial_no": serial_no,
            "volume_content": str(tail["volume_content"]) if tail["volume_content"] is not None else None,
            "reservoir_area_sqkm": str(tail["reservoir_area_sqkm"]) if tail["reservoir_area_sqkm"] is not None else None,
            "purpose": tail["purpose"],
        },
    }


def ordered_text(items: list[tuple[float, float, str]]) -> str | None:
    if not items:
        return None
    text = " ".join(text for _y, _x, text in sorted(items, key=lambda item: (-item[0], item[1])))
    return clean_text(text)


def split_pic_column(value: str | None, serial_no: int) -> tuple[str | None, str, str | None]:
    value = clean_text(value)
    if not value:
        return None, normalize_pic(None, serial_no), None
    pic_match = PIC_RE.search(value)
    if not pic_match:
        return None, normalize_pic(None, serial_no), value
    state_name = clean_text(value[: pic_match.start()])
    dam_id = normalize_pic(pic_match.group(0), serial_no)
    remainder = clean_text(value[pic_match.end() :])
    return state_name, dam_id, remainder


def parse_positioned_row(block_items: list[tuple[float, float, str]], page_state_name: str | None) -> dict[str, Any] | None:
    serial_items = [(y, x, text) for y, x, text in block_items if ROW_NO_X_MIN <= x <= ROW_NO_X_MAX and text.isdigit()]
    if not serial_items:
        return None
    serial_no = int(sorted(serial_items, key=lambda item: item[0])[0][2])

    pic_col = ordered_text([(y, x, text) for y, x, text in block_items if 150 <= x < 247])
    name_col = ordered_text([(y, x, text) for y, x, text in block_items if 247 <= x < 294])
    owner_col = ordered_text([(y, x, text) for y, x, text in block_items if 294 <= x < 340])
    right_col = ordered_text([(y, x, text) for y, x, text in block_items if 340 <= x < 1120])

    state_raw, dam_id, pic_remainder = split_pic_column(pic_col, serial_no)
    state_name = normalize_state(state_raw, page_state_name)
    if not state_name:
        return None

    extra_name, extra_owner = split_name_owner(pic_remainder)
    dam_name = clean_text(" ".join(part for part in (name_col, extra_name) if part))
    owner_agency = clean_text(" ".join(part for part in (owner_col, extra_owner) if part))
    if not dam_name:
        return None

    coord_match = None
    if right_col:
        coord_match = DECIMAL_COORD_RE.search(right_col) or DMS_COORD_RE.search(right_col)
    if not coord_match:
        return None

    year_value = coord_match.group("year")
    construction_year, status = parse_year(year_value)
    latitude = parse_coord(coord_match.group("lat"), is_lon=False)
    longitude = parse_coord(coord_match.group("lon"), is_lon=True)
    rest = right_col[coord_match.end() :].strip()
    tail = extract_tail_metrics(rest)
    risk_class = risk_from_metrics(tail["height_m"], tail["gross_storage_mcm"])

    return {
        "serial_no": serial_no,
        "dam_id": dam_id,
        "source_record_id": dam_id if not dam_id.startswith("NRLD2023-") else f"Serial {serial_no}",
        "dam_name": dam_name[:240],
        "state": state_name,
        "district": tail["district"],
        "river_basin": tail["river_basin"],
        "river_name": tail["river_name"],
        "owner_agency": owner_agency,
        "dam_type": tail["foundation_type"],
        "construction_year": construction_year,
        "status": status,
        "risk_class": risk_class,
        "safety_score": Decimal("70.00"),
        "latitude": latitude,
        "longitude": longitude,
        "height_m": tail["height_m"],
        "length_m": tail["length_m"],
        "spillway_capacity_cumecs": tail["spillway_capacity_cumecs"],
        "foundation_type": tail["foundation_type"],
        "seismic_zone": tail["seismic_zone"],
        "reservoir_name": f"{dam_name} Reservoir"[:240],
        "gross_storage_mcm": tail["gross_storage_mcm"],
        "live_storage_mcm": tail["live_storage_mcm"],
        "current_storage_mcm": None,
        "extra": {
            "nrld_serial_no": serial_no,
            "volume_content": str(tail["volume_content"]) if tail["volume_content"] is not None else None,
            "reservoir_area_sqkm": str(tail["reservoir_area_sqkm"]) if tail["reservoir_area_sqkm"] is not None else None,
            "purpose": tail["purpose"],
        },
    }


def parse_positioned_page(page: Any, page_state_name: str | None) -> list[dict[str, Any]]:
    items: list[tuple[float, float, str]] = []

    def visitor(text: str, _cm: Any, tm: Any, _font_dict: Any, _font_size: float) -> None:
        cleaned = clean_text(text.replace("\n", " "))
        if cleaned:
            items.append((float(tm[5]), float(tm[4]), cleaned))

    page.extract_text(visitor_text=visitor)
    row_anchors = sorted(
        [(y, x, text) for y, x, text in items if ROW_NO_X_MIN <= x <= ROW_NO_X_MAX and text.isdigit()],
        key=lambda item: item[0],
        reverse=True,
    )
    records: list[dict[str, Any]] = []
    for index, (row_y, _x, _text) in enumerate(row_anchors):
        lower_bound = row_anchors[index + 1][0] + 2 if index + 1 < len(row_anchors) else 80
        upper_bound = row_y + ROW_TOP_PADDING
        block = [(y, x, text) for y, x, text in items if lower_bound < y <= upper_bound and y < 720]
        record = parse_positioned_row(block, page_state_name)
        if record:
            records.append(record)
    return records


def is_suspicious_record(record: dict[str, Any]) -> bool:
    dam_name = record.get("dam_name") or ""
    owner = record.get("owner_agency") or ""
    if len(dam_name) > 90:
        return True
    if COORD_HINT_RE.search(dam_name) or COORD_HINT_RE.search(owner):
        return True
    if PIC_RE.search(dam_name):
        return True
    if owner and len(owner) > 180:
        return True
    height = record.get("height_m")
    if height and height > Decimal(350):
        return True
    return False


def parse_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(pdf_path))
    records: dict[str, dict[str, Any]] = {}
    current_state: str | None = None
    for page_number, page in enumerate(reader.pages, start=1):
        if page_number < 34 or page_number > 344:
            continue
        text = page.extract_text() or ""
        state = page_state(text)
        if state:
            current_state = state
        if not current_state:
            continue
        for record in parse_positioned_page(page, current_state):
            if is_suspicious_record(record):
                continue
            key = record["dam_id"]
            records[key] = record
        for chunk in ROW_START_RE.split(text):
            record = parse_row(chunk, current_state)
            if not record:
                continue
            key = record["dam_id"]
            if key.startswith("NRLD2023-") and record["serial_no"] in {r["serial_no"] for r in records.values()}:
                continue
            if not is_suspicious_record(record):
                records.setdefault(key, record)
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
            f"VALUES ({sql_text(record['dam_id'])}, {point_sql}, 'nrld-2023.pdf', 'CWC PDF text extraction', now()) "
            "ON CONFLICT (dam_id) DO UPDATE SET dam_point = EXCLUDED.dam_point, source_file_name = EXCLUDED.source_file_name, "
            "source_format = EXCLUDED.source_format, uploaded_at = now();"
        )

    lines.extend(["COMMIT;", ""])
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_geometry_sql(records: list[dict[str, Any]], output_path: Path) -> None:
    lines = [
        "BEGIN;",
        "UPDATE dam_geometry AS geometry SET dam_point = imported.dam_point, source_file_name = 'nrld-2023.pdf', "
        "source_format = 'CWC NRLD 2023 geometry refresh', uploaded_at = now() "
        "FROM (VALUES",
    ]
    value_lines = []
    for record in records:
        if record["latitude"] is None or record["longitude"] is None:
            continue
        value_lines.append(
            f"({sql_text(record['dam_id'])}, ST_SetSRID(ST_MakePoint({record['longitude']}, {record['latitude']}), 4326))"
        )
    lines.append(",\n".join(value_lines))
    lines.extend(
        [
            ") AS imported(dam_id, dam_point) WHERE geometry.dam_id = imported.dam_id;",
            "COMMIT;",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract CWC NRLD 2023 PDF rows into an idempotent PostGIS SQL import.")
    parser.add_argument("--pdf", default="data/nrld-2023.pdf", type=Path)
    parser.add_argument("--out", default="data/nrld_2023_import.sql", type=Path)
    parser.add_argument("--keep-seed", action="store_true", help="Keep the initial demo rows instead of replacing them.")
    parser.add_argument("--geometry-only", action="store_true", help="Write only dam_geometry point updates for matching dam_id rows.")
    args = parser.parse_args()

    records = parse_pdf(args.pdf)
    if args.geometry_only:
        write_geometry_sql(records, args.out)
    else:
        write_sql(records, args.out, replace_seed=not args.keep_seed)
    with (args.out.with_suffix(".summary.json")).open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "source": SOURCE_URL,
                "publication_year": SOURCE_YEAR,
                "records": len(records),
                "with_geometry": sum(1 for record in records if record["latitude"] and record["longitude"]),
                "states": sorted({record["state"] for record in records}),
            },
            handle,
            indent=2,
        )
    print(f"Wrote {len(records)} NRLD records to {args.out}")


if __name__ == "__main__":
    main()
