import json
import math
import zipfile
from pathlib import Path

from add_hms_basin_geojson import DBF_NAME, SHAPE_NAME, read_polygon_shapes, signed_area
from add_hms_junction_sites import ZIP_PATH, read_dbf_records, utm44n_to_lonlat


SUMMARY_PATH = Path("work/hms_model_summary.json")
DATA_JS_PATH = Path("outputs/hms-narmada-model-data.js")


def polygon_centroid(points):
    area_twice = 0.0
    cx = 0.0
    cy = 0.0
    for idx, (x1, y1) in enumerate(points):
        x2, y2 = points[(idx + 1) % len(points)]
        cross = x1 * y2 - x2 * y1
        area_twice += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(area_twice) < 1e-9:
        return points[len(points) // 2]
    return cx / (3 * area_twice), cy / (3 * area_twice)


def find_shape_centroid(target_name):
    with zipfile.ZipFile(ZIP_PATH) as zf:
        shp = zf.read(SHAPE_NAME)
        dbf = zf.read(DBF_NAME)

    records = read_dbf_records(dbf)
    shapes = read_polygon_shapes(shp)
    for (_rec_num, rings), attrs in zip(shapes, records):
        name = attrs.get("name") or attrs.get("Name") or attrs.get("NAME") or attrs.get("subbasin")
        if name != target_name:
            continue
        ring = max(rings, key=lambda item: abs(signed_area(item)))
        x, y = polygon_centroid(ring)
        lat, lon = utm44n_to_lonlat(x, y)
        return lat, lon
    raise SystemExit(f"Could not find polygon for {target_name}")


def compute_sug(row):
    region = row.get("region") or ("upper" if row["lon"] >= 78.5 else "lower")
    ct = 0.72 if region == "upper" else 0.70
    cp = 2.05 if region == "upper" else 2.10
    area = float(row.get("gisAreaSqKm") or row.get("geometryAreaSqKm") or row.get("hmsAreaSqKm") or 0)
    length = max(1.0, float(row.get("longestFlowpathKm") or 0))
    centroid = max(1.0, float(row.get("centroidalFlowpathKm") or 0))
    slope_m_per_km = max(0.01, float(row.get("longestFlowpathSlope") or 0) * 1000)
    basin_term = (length * centroid) / math.sqrt(slope_m_per_km)
    lag = ct * basin_term**0.33
    tp = lag + 0.5
    base_time = tp * 3.5
    unit_peak = 2.78 * cp * area / tp
    return {
        "subzone": region,
        "ct": ct,
        "cp": cp,
        "lagHr": lag,
        "timeToPeakHr": tp,
        "baseTimeHr": base_time,
        "unitPeakCumec": unit_peak,
        "areaSqKm": area,
        "lengthKm": length,
        "centroidalLengthKm": centroid,
        "slopeMPerKm": slope_m_per_km,
    }


def main():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    if any(row["name"] == "Subbasin-2" for row in summary["subbasins"]):
        print("Subbasin-2 is already active.")
        return

    removed = summary.get("removedSubbasins", [])
    restored = next((row for row in removed if row.get("name") == "Subbasin-2"), None)
    if not restored:
        raise SystemExit("Subbasin-2 was not found in removedSubbasins")

    lat, lon = find_shape_centroid("Subbasin-2")
    restored = dict(restored)
    restored["lat"] = lat
    restored["lon"] = lon
    restored["region"] = "upper" if lon >= 78.5 else "lower"
    restored["centroidSource"] = "Calculated from HMS/Sub Basin_HM_Narmada.shp polygon geometry; workbook centroid was 0,0."
    restored["sug"] = compute_sug(restored)

    summary["subbasins"].append(restored)
    summary["subbasins"].sort(key=lambda row: row["name"])
    summary["removedSubbasins"] = [row for row in removed if row.get("name") != "Subbasin-2"]
    summary["subbasinCount"] = len(summary["subbasins"])
    summary["totalGisAreaSqKm"] = sum(float(row.get("gisAreaSqKm") or row.get("geometryAreaSqKm") or 0) for row in summary["subbasins"])
    summary["totalGeometryAreaSqKm"] = summary["totalGisAreaSqKm"]
    summary["areaSource"] = (
        "Calculated from polygon geometry in HMS/Sub Basin_HM_Narmada.shp; "
        "Subbasin-2 restored with polygon-derived centroid because workbook centroid was 0,0."
    )

    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    DATA_JS_PATH.write_text(
        "window.HMS_NARMADA_DATA = "
        + json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Restored Subbasin-2 at lat={lat:.6f}, lon={lon:.6f}; active basins={summary['subbasinCount']}.")


if __name__ == "__main__":
    main()
