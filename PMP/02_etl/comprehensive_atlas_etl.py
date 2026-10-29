from __future__ import annotations

"""Supplemental, provenance-first extraction for the complete PMP Atlas.

The original MVP ETL is intentionally preserved. This module adds the products
that are not represented by the first numeric extraction: page/asset inventory,
station climatology, DAD values, return-period estimates and raw table evidence.
It is idempotent and keeps the source PDFs immutable.
"""

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "00_source_documents"
DB = ROOT / "01_database" / "pmp_atlas.sqlite"

DOCS = [
    ("volume_i_maps_tables", SOURCE / "narmada-basin-volume-i.pdf", "Volume II: Maps and Tables"),
    ("volume_ii_main_report", SOURCE / "narmada-basin-volume-ii.pdf", "Volume I: Main Report"),
]


def clean(value):
    if value is None:
        return None
    value = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return value or None


def number(value):
    value = clean(value)
    if not value:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def station_key(catchment, station, station_type, serial):
    return f"{clean(catchment)}:{clean(station)}:{clean(station_type)}:{serial}"


def setup(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS atlas_source_document (
            document_key TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            volume_label TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            pdf_page_count INTEGER NOT NULL,
            indexed_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS source_page_catalog (
            document_key TEXT NOT NULL,
            pdf_page_number INTEGER NOT NULL,
            volume_label TEXT NOT NULL,
            page_role TEXT NOT NULL,
            page_title TEXT,
            page_text TEXT,
            extraction_status TEXT NOT NULL DEFAULT 'indexed',
            PRIMARY KEY(document_key, pdf_page_number)
        );
        CREATE TABLE IF NOT EXISTS source_asset_registry (
            asset_key TEXT PRIMARY KEY,
            document_key TEXT NOT NULL,
            pdf_page_number INTEGER NOT NULL,
            asset_type TEXT NOT NULL,
            asset_label TEXT,
            asset_title TEXT,
            extraction_status TEXT NOT NULL DEFAULT 'source_reference',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS raw_extracted_table (
            table_key TEXT PRIMARY KEY,
            document_key TEXT NOT NULL,
            pdf_page_number INTEGER NOT NULL,
            table_index INTEGER NOT NULL,
            table_label TEXT,
            header_json TEXT,
            rows_json TEXT NOT NULL,
            extraction_method TEXT NOT NULL,
            validation_status TEXT NOT NULL DEFAULT 'unreviewed'
        );
        CREATE TABLE IF NOT EXISTS station_climatology (
            station_key TEXT PRIMARY KEY,
            serial_no INTEGER,
            catchment_code TEXT,
            district_name TEXT,
            station_name TEXT,
            station_type TEXT,
            latitude_deg REAL,
            longitude_deg REAL,
            elevation_m REAL,
            record_period TEXT,
            years_of_record REAL,
            monsoon_mean_mm REAL,
            monsoon_stddev_mm REAL,
            monsoon_cv_pct REAL,
            annual_mean_mm REAL,
            annual_stddev_mm REAL,
            annual_cv_pct REAL,
            source_document_key TEXT NOT NULL,
            source_pdf_page INTEGER NOT NULL,
            source_table_label TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dad_storm_value (
            dad_id INTEGER PRIMARY KEY,
            duration_hours INTEGER NOT NULL,
            storm_serial_no INTEGER,
            storm_date_text TEXT,
            storm_centre TEXT,
            peak_rainfall_mm REAL,
            area_km2 REAL,
            depth_mm REAL,
            source_document_key TEXT NOT NULL,
            source_pdf_page INTEGER NOT NULL,
            source_table_label TEXT NOT NULL,
            UNIQUE(duration_hours, storm_serial_no, area_km2, source_pdf_page)
        );
        CREATE TABLE IF NOT EXISTS return_period_estimate (
            return_id INTEGER PRIMARY KEY,
            station_key TEXT NOT NULL,
            serial_no INTEGER,
            catchment_code TEXT,
            district_name TEXT,
            station_name TEXT,
            station_type TEXT,
            duration_hours INTEGER NOT NULL,
            parameter_xi REAL,
            parameter_alpha REAL,
            estimate_class TEXT NOT NULL,
            return_period_years REAL NOT NULL,
            rainfall_mm REAL,
            source_document_key TEXT NOT NULL,
            source_pdf_page INTEGER NOT NULL,
            source_table_label TEXT NOT NULL,
            UNIQUE(station_key, duration_hours, estimate_class, return_period_years)
        );
        CREATE INDEX IF NOT EXISTS source_page_role_ix ON source_page_catalog(page_role);
        CREATE INDEX IF NOT EXISTS source_asset_type_ix ON source_asset_registry(asset_type);
        CREATE INDEX IF NOT EXISTS dad_lookup_ix ON dad_storm_value(duration_hours, area_km2);
        CREATE INDEX IF NOT EXISTS return_period_lookup_ix ON return_period_estimate(station_key, duration_hours, return_period_years);
        """
    )


def page_role(text: str, tables: list) -> str:
    value = text.lower()
    if "figure" in value or "map" in value:
        return "map" if "map" in value else "figure"
    if tables:
        return "table"
    if not text.strip():
        return "blank"
    return "text"


def page_title(text: str) -> str | None:
    for line in (text or "").splitlines():
        line = clean(line)
        if not line:
            continue
        if re.match(r"^(Figure|Table)\s+[^:]+:", line, re.I):
            return line
        if re.match(r"^\d+(?:\.\d+)*\s+", line):
            return line
    return None


def register_pages(conn):
    for key, path, label in DOCS:
        with pdfplumber.open(path) as pdf:
            conn.execute(
                "INSERT OR REPLACE INTO atlas_source_document VALUES (?,?,?,?,?,?)",
                (key, path.name, label, sha256(path), len(pdf.pages), datetime.now(timezone.utc).isoformat()),
            )
            for n, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                tables = page.extract_tables()
                conn.execute(
                    "INSERT OR REPLACE INTO source_page_catalog VALUES (?,?,?,?,?,?,?)",
                    (key, n, label, page_role(text, tables), page_title(text), text, "indexed"),
                )
                for match in re.finditer(r"(Figure|Table)\s+([0-9][\w.-]*):\s*(.+)", text, re.I):
                    kind, label_number, title = match.groups()
                    asset_key = f"{key}:{n}:{kind.lower()}:{label_number}"
                    conn.execute(
                        "INSERT OR REPLACE INTO source_asset_registry VALUES (?,?,?,?,?,?,?,?)",
                        (asset_key, key, n, kind.lower(), f"{kind} {label_number}", clean(title), "source_reference", "Figure/table retained as a source-linked atlas asset; numeric digitization is tracked separately."),
                    )
    conn.commit()


def register_raw_tables(conn):
    for key, path, _ in DOCS:
        with pdfplumber.open(path) as pdf:
            for n, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                for idx, table in enumerate(tables):
                    if not table:
                        continue
                    text = page.extract_text() or ""
                    label = page_title(text)
                    rows = [[clean(cell) for cell in row] for row in table]
                    table_key = f"{key}:{n}:{idx}"
                    conn.execute(
                        "INSERT OR REPLACE INTO raw_extracted_table VALUES (?,?,?,?,?,?,?,?,?)",
                        (table_key, key, n, idx, label, json.dumps(rows[:2], ensure_ascii=False), json.dumps(rows[2:] if len(rows) > 2 else [], ensure_ascii=False), "pdfplumber table extraction; raw cells retained", "unreviewed"),
                    )
    conn.commit()


def extract_climatology(conn):
    key = "volume_i_maps_tables"
    path = dict((k, p) for k, p, _ in DOCS)[key]
    with pdfplumber.open(path) as pdf:
        for page_no in range(22, 33):
            for table in pdf.pages[page_no - 1].extract_tables():
                for row in table[2:]:
                    if not row or len(row) < 16 or not (clean(row[0]) or "").isdigit():
                        continue
                    serial = int(clean(row[0]))
                    skey = station_key(row[1], row[3], row[4], serial)
                    conn.execute(
                        "INSERT OR REPLACE INTO station_climatology VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (skey, serial, clean(row[1]), clean(row[2]), clean(row[3]), clean(row[4]), number(row[5]), number(row[6]), number(row[7]), clean(row[8]), number(row[9]), number(row[10]), number(row[11]), number(row[12]), number(row[13]), number(row[14]), number(row[15]), key, page_no, "Table 1-1: List of rainfall stations used for the study"),
                    )
    conn.commit()


def extract_dad(conn):
    key = "volume_ii_main_report"
    path = dict((k, p) for k, p, _ in DOCS)[key]
    with pdfplumber.open(path) as pdf:
        for page_no in range(130, 138):
            tables = pdf.pages[page_no - 1].extract_tables()
            for idx, table in enumerate(tables):
                if not table or len(table[0]) < 17:
                    continue
                if page_no <= 134 and idx == 0:
                    duration = 24
                    label = "Table 3-3: DAD values, 1-day duration"
                elif page_no <= 136:
                    duration = 48
                    label = "Table 3-4: DAD values, 2-day duration"
                else:
                    duration = 72
                    label = "Table 3-5: DAD values, 3-day duration"
                header = table[1] if len(table) > 1 else []
                areas = [number(x) for x in header[4:17]]
                for row in table[2:]:
                    if not row or len(row) < 17 or not (clean(row[0]) or "").isdigit():
                        continue
                    serial = int(clean(row[0]))
                    for area, depth in zip(areas, row[4:17]):
                        if area is None or number(depth) is None:
                            continue
                        conn.execute(
                            "INSERT OR REPLACE INTO dad_storm_value(dad_id,duration_hours,storm_serial_no,storm_date_text,storm_centre,peak_rainfall_mm,area_km2,depth_mm,source_document_key,source_pdf_page,source_table_label) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (None, duration, serial, clean(row[1]), clean(row[2]), number(row[3]), area, number(depth), key, page_no, label),
                        )
    conn.commit()


def extract_return_periods(conn):
    key = "volume_i_maps_tables"
    path = dict((k, p) for k, p, _ in DOCS)[key]
    periods = [2.33, 5, 10, 25, 50, 100, 500, 1000, 5000, 10000]
    with pdfplumber.open(path) as pdf:
        for page_no in range(191, 255):
            duration = 24 if page_no <= 212 else 48 if page_no <= 233 else 72
            tables = pdf.pages[page_no - 1].extract_tables()
            for table in tables:
                if not table or len(table[0]) < 18 or "Gumbel" not in " ".join(clean(x) or "" for x in table[0]):
                    continue
                current = None
                for row in table[2:]:
                    if not row or len(row) < 18:
                        continue
                    if clean(row[0]) and (clean(row[0]).isdigit()):
                        current = {
                            "serial": int(clean(row[0])), "catchment": clean(row[1]), "district": clean(row[2]), "station": clean(row[3]), "type": clean(row[4]), "xi": number(row[5]), "alpha": number(row[6]),
                        }
                    if not current or clean(row[7]) not in {"EST", "LL", "UL"}:
                        continue
                    skey = station_key(current["catchment"], current["station"], current["type"], current["serial"])
                    for period, rainfall in zip(periods, row[8:18]):
                        conn.execute(
                            "INSERT OR REPLACE INTO return_period_estimate(station_key,serial_no,catchment_code,district_name,station_name,station_type,duration_hours,parameter_xi,parameter_alpha,estimate_class,return_period_years,rainfall_mm,source_document_key,source_pdf_page,source_table_label) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (skey, current["serial"], current["catchment"], current["district"], current["station"], current["type"], duration, current["xi"], current["alpha"], clean(row[7]), period, number(rainfall), key, page_no, f"Table 6-{1 if duration == 24 else 2 if duration == 48 else 3}: Return period values with 95% confidence limits"),
                        )
    conn.commit()


def main():
    with sqlite3.connect(DB) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        setup(conn)
        register_pages(conn)
        register_raw_tables(conn)
        extract_climatology(conn)
        extract_dad(conn)
        extract_return_periods(conn)
        counts = {}
        for table in ("atlas_source_document", "source_page_catalog", "source_asset_registry", "raw_extracted_table", "station_climatology", "dad_storm_value", "return_period_estimate"):
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
