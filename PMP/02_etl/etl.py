from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "00_source_documents" / "narmada-basin-volume-ii.pdf"
DEFAULT_DB = ROOT / "01_database" / "pmp_atlas.sqlite"
DEFAULT_EXPORT = ROOT / "04_exports"


def clean(value):
    if value is None:
        return None
    value = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return value or None


def num(value):
    value = clean(value)
    if value is None:
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def db_schema(conn):
    conn.executescript("""
    PRAGMA foreign_keys = ON;
    DROP TABLE IF EXISTS grid_pmp_estimate;
    DROP TABLE IF EXISTS grid_point;
    DROP TABLE IF EXISTS station_extreme_rainfall;
    DROP TABLE IF EXISTS rainfall_station;
    DROP TABLE IF EXISTS rainfall_storm;
    DROP TABLE IF EXISTS catchment;
    DROP TABLE IF EXISTS provenance;
    DROP TABLE IF EXISTS atlas_page;
    DROP TABLE IF EXISTS atlas_document;
    CREATE TABLE IF NOT EXISTS atlas_document(document_id INTEGER PRIMARY KEY, document_key TEXT UNIQUE NOT NULL, title TEXT NOT NULL, volume_label TEXT, source_path TEXT NOT NULL, sha256 TEXT NOT NULL, pdf_page_count INTEGER NOT NULL, loaded_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS atlas_page(page_id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES atlas_document, pdf_page_number INTEGER NOT NULL, printed_page_number INTEGER, page_role TEXT NOT NULL, source_label TEXT, UNIQUE(document_id,pdf_page_number));
    CREATE TABLE IF NOT EXISTS provenance(provenance_id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES atlas_document, pdf_page_number INTEGER NOT NULL, source_label TEXT NOT NULL, extraction_method TEXT NOT NULL, extraction_run_id TEXT NOT NULL, validation_status TEXT NOT NULL DEFAULT 'validated');
    CREATE TABLE IF NOT EXISTS catchment(catchment_code TEXT PRIMARY KEY, name TEXT NOT NULL, area_km2 REAL, source_provenance_id INTEGER NOT NULL REFERENCES provenance);
    CREATE TABLE IF NOT EXISTS rainfall_station(station_key TEXT PRIMARY KEY, serial_no INTEGER, catchment_code TEXT NOT NULL, district_name TEXT, station_name TEXT NOT NULL, station_type TEXT, latitude_deg REAL, longitude_deg REAL, data_length_years REAL, source_provenance_id INTEGER NOT NULL REFERENCES provenance);
    CREATE TABLE IF NOT EXISTS station_extreme_rainfall(station_key TEXT NOT NULL REFERENCES rainfall_station, duration_hours INTEGER NOT NULL, rainfall_mm REAL NOT NULL, event_date_text TEXT, source_provenance_id INTEGER NOT NULL REFERENCES provenance, PRIMARY KEY(station_key,duration_hours));
    CREATE TABLE IF NOT EXISTS rainfall_storm(storm_key TEXT PRIMARY KEY, serial_no INTEGER, storm_id TEXT, year INTEGER, storm_date_text TEXT, duration_hours INTEGER, storm_duration_text TEXT, storm_centre_name TEXT, latitude_deg REAL, longitude_deg REAL, peak_rainfall_mm REAL, source_provenance_id INTEGER NOT NULL REFERENCES provenance);
    CREATE TABLE IF NOT EXISTS grid_point(grid_id TEXT PRIMARY KEY, catchment_code TEXT, latitude_deg REAL, longitude_deg REAL, source_provenance_id INTEGER NOT NULL REFERENCES provenance);
    CREATE TABLE IF NOT EXISTS grid_pmp_estimate(grid_id TEXT NOT NULL REFERENCES grid_point, duration_hours INTEGER NOT NULL, area_km2 REAL NOT NULL, grid_rain_depth_mm REAL, storm_date_text TEXT, taf REAL, sps_mm REAL, mmf REAL, pmp_mm REAL, source_provenance_id INTEGER NOT NULL REFERENCES provenance, PRIMARY KEY(grid_id,duration_hours,area_km2));
    CREATE INDEX IF NOT EXISTS station_catchment_ix ON rainfall_station(catchment_code);
    CREATE INDEX IF NOT EXISTS grid_pmp_lookup_ix ON grid_pmp_estimate(grid_id,duration_hours,area_km2);
    """)


def register_document(conn, path, label, pages):
    conn.execute("DELETE FROM atlas_page WHERE document_id IN (SELECT document_id FROM atlas_document WHERE document_key='narmada_pmp_main_report')")
    conn.execute("DELETE FROM atlas_document WHERE document_key='narmada_pmp_main_report'")
    conn.execute("INSERT INTO atlas_document(document_key,title,volume_label,source_path,sha256,pdf_page_count,loaded_at) VALUES (?,?,?,?,?,?,?)", ('narmada_pmp_main_report', 'PMP Atlas for Narmada, Tapi and Other Adjoining River Basins', label, str(path), sha256(path), pages, datetime.now(timezone.utc).isoformat()))
    doc_id = conn.execute("SELECT document_id FROM atlas_document WHERE document_key='narmada_pmp_main_report'").fetchone()[0]
    conn.executemany("INSERT INTO atlas_page(document_id,pdf_page_number,printed_page_number,page_role,source_label) VALUES (?,?,?,?,?)", [(doc_id, i, None, 'table', label) for i in range(1, pages + 1)])
    return doc_id


def provenance(conn, doc_id, page, label, run_id):
    cur = conn.execute("INSERT INTO provenance(document_id,pdf_page_number,source_label,extraction_method,extraction_run_id) VALUES (?,?,?,?,?)", (doc_id, page, label, 'pdfplumber table extraction with row validation', run_id))
    return cur.lastrowid


def extract_stations(conn, pdf, doc_id, run_id):
    count = 0
    for page_no in range(50, 81):
        for table in pdf.pages[page_no - 1].extract_tables():
            prov = provenance(conn, doc_id, page_no, 'Table 2-5: highest 1/2/3-day rainfall', run_id)
            for row in table[2:]:
                if not row or len(row) < 14 or not clean(row[0]) or not clean(row[0]).isdigit():
                    continue
                serial = int(clean(row[0]))
                station_key = f'{clean(row[1])}:{clean(row[3])}:{clean(row[4])}:{serial}'
                conn.execute('INSERT OR REPLACE INTO rainfall_station VALUES (?,?,?,?,?,?,?,?,?,?)', (station_key, serial, clean(row[1]), clean(row[2]), clean(row[3]), clean(row[4]), num(row[5]), num(row[6]), num(row[7]), prov))
                for duration, value_idx, date_idx in ((24, 8, 9), (48, 10, 11), (72, 12, 13)):
                    if num(row[value_idx]) is not None:
                        conn.execute('INSERT OR REPLACE INTO station_extreme_rainfall VALUES (?,?,?,?,?)', (station_key, duration, num(row[value_idx]), clean(row[date_idx]), prov))
                count += 1
    return count


def extract_storms(conn, pdf, doc_id, run_id):
    count = 0
    for page_no in range(91, 96):
        for table in pdf.pages[page_no - 1].extract_tables():
            prov = provenance(conn, doc_id, page_no, 'Table 3-2: rainstorms affecting the study area', run_id)
            for row in table[1:]:
                if not row or len(row) < 9 or not clean(row[0]) or not clean(row[0]).isdigit():
                    continue
                serial = int(clean(row[0])); duration_text = clean(row[4])
                duration = {'1-day': 24, '2-day': 48, '3-day': 72}.get(duration_text)
                conn.execute('INSERT OR REPLACE INTO rainfall_storm VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (f'storm-{serial}', serial, clean(row[1]), int(num(row[2]) or 0), clean(row[3]), duration, duration_text, clean(row[5]), num(row[6]), num(row[7]), num(row[8]), prov))
                count += 1
    return count


def extract_catchments_and_grids(conn, pdf, doc_id, run_id):
    catchments = 0; grids = 0; prov = provenance(conn, doc_id, 198, 'Tables 3-34 and 3-35', run_id)
    tables = pdf.pages[197].extract_tables()
    for row in tables[0][2:]:
        if row and len(row) >= 3 and clean(row[1]):
            conn.execute('INSERT OR REPLACE INTO catchment VALUES (?,?,?,?)', (clean(row[1]), clean(row[0]).replace('\n', ' '), num(row[2]), prov)); catchments += 1
    for page_no in (198, 199):
        for table in pdf.pages[page_no - 1].extract_tables():
            if not table or 'Grid ID' not in ' '.join(clean(x) or '' for x in table[0]):
                continue
            current = None
            for row in table[1:]:
                if not row or len(row) < 4 or not clean(row[1]):
                    continue
                current = clean(row[0]) or current
                conn.execute('INSERT OR REPLACE INTO grid_point VALUES (?,?,?,?,?)', (clean(row[1]), current, num(row[2]), num(row[3]), prov)); grids += 1
    return catchments, grids


def extract_grid_pmp(conn, pdf, doc_id, run_id):
    count = 0
    for page_no in range(217, 243):
        tables = pdf.pages[page_no - 1].extract_tables()
        default_duration = 24 if page_no < 225 else 48 if page_no < 234 else 72
        for table_index, table in enumerate(tables):
            if not table or 'Grid ID' not in (clean(table[0][0]) or ''):
                continue
            duration = default_duration
            if page_no == 225 and table_index == 1: duration = 48
            if page_no == 234 and table_index == 1: duration = 72
            prov = provenance(conn, doc_id, page_no, f'PMP grid table for {duration}-hour duration', run_id)
            current_grid = None
            for row in table[1:]:
                if not row or len(row) < 8 or not clean(row[1]):
                    continue
                if clean(row[0]): current_grid = clean(row[0])
                if not current_grid or current_grid.lower() == 'grid id': continue
                area = num(row[1])
                if area is None: continue
                conn.execute('INSERT OR REPLACE INTO grid_pmp_estimate VALUES (?,?,?,?,?,?,?,?,?,?)', (current_grid, duration, area, num(row[2]), clean(row[3]), num(row[4]), num(row[5]), num(row[6]), num(row[7]), prov)); count += 1
    return count


def export_files(conn, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    datasets = {'stations': 'SELECT * FROM rainfall_station ORDER BY serial_no', 'station_extremes': 'SELECT * FROM station_extreme_rainfall ORDER BY station_key,duration_hours', 'storms': 'SELECT * FROM rainfall_storm ORDER BY serial_no', 'grid_pmp_estimates': 'SELECT * FROM grid_pmp_estimate ORDER BY grid_id,duration_hours,area_km2', 'catchments': 'SELECT * FROM catchment ORDER BY catchment_code'}
    for name, sql in datasets.items(): pd.read_sql_query(sql, conn).to_csv(out_dir / f'{name}.csv', index=False, encoding='utf-8')
    stations = pd.read_sql_query(datasets['stations'], conn)
    features = []
    for row in stations.to_dict('records'):
        if pd.isna(row['latitude_deg']) or pd.isna(row['longitude_deg']): continue
        features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [row['longitude_deg'], row['latitude_deg']]}, 'properties': row})
    (out_dir / 'stations.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': features}, default=str), encoding='utf-8')
    files = [{'file': p.name, 'format': p.suffix.lstrip('.') or 'json'} for p in out_dir.iterdir() if p.is_file()]
    (out_dir / 'nita_export_manifest.json').write_text(json.dumps({'adapter': 'nita-geoai', 'adapter_version': '1.0', 'crs': 'EPSG:4326', 'packages': files}, indent=2), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--report-pdf', type=Path, default=DEFAULT_REPORT); ap.add_argument('--db', type=Path, default=DEFAULT_DB); ap.add_argument('--exports', type=Path, default=DEFAULT_EXPORT); args = ap.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True); run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    with sqlite3.connect(args.db) as conn, pdfplumber.open(args.report_pdf) as report:
        db_schema(conn); doc_id = register_document(conn, args.report_pdf, 'Volume I: Main Report', len(report.pages)); stations = extract_stations(conn, report, doc_id, run_id); storms = extract_storms(conn, report, doc_id, run_id); catchments, grids = extract_catchments_and_grids(conn, report, doc_id, run_id); grid_pmp = extract_grid_pmp(conn, report, doc_id, run_id); conn.commit(); export_files(conn, args.exports)
    print(json.dumps({'db': str(args.db), 'stations': stations, 'storms': storms, 'catchments': catchments, 'grid_points': grids, 'grid_pmp_rows': grid_pmp, 'exports': str(args.exports)}, indent=2))


if __name__ == '__main__': main()
