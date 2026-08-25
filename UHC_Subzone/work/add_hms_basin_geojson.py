import json
import math
import struct
import zipfile
from pathlib import Path

from add_hms_junction_sites import read_dbf_records, utm44n_to_lonlat


ZIP_PATH = Path(r"E:\01 Projects\03 MPWRD\14 Digitial Atlas\01 Data\01 SHP\01 Basin Wise\Narmada\HMS.zip")
SUMMARY_PATH = Path("work/hms_model_summary.json")
DATA_JS_PATH = Path("outputs/hms-narmada-model-data.js")
SHAPE_NAME = "HMS/Sub Basin_HM_Narmada.shp"
DBF_NAME = "HMS/Sub Basin_HM_Narmada.dbf"


def signed_area(points):
    area = 0.0
    for idx, (x1, y1) in enumerate(points):
        x2, y2 = points[(idx + 1) % len(points)]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def simplify_ring(points, max_points=180):
    if len(points) <= max_points:
        return points
    step = max(1, math.ceil(len(points) / max_points))
    sampled = points[::step]
    if sampled[0] != sampled[-1]:
        sampled.append(sampled[0])
    return sampled


def read_polygon_shapes(raw):
    shapes = []
    offset = 100
    while offset + 8 <= len(raw):
        rec_num, content_words = struct.unpack(">2i", raw[offset : offset + 8])
        content_len = content_words * 2
        content = raw[offset + 8 : offset + 8 + content_len]
        if len(content) >= 44:
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type in (5, 15, 25, 31):
                num_parts, num_points = struct.unpack("<2i", content[36:44])
                parts_start = 44
                points_start = parts_start + num_parts * 4
                parts = list(struct.unpack(f"<{num_parts}i", content[parts_start:points_start]))
                xy = []
                for idx in range(num_points):
                    start = points_start + idx * 16
                    xy.append(struct.unpack("<2d", content[start : start + 16]))
                rings = []
                for part_idx, start in enumerate(parts):
                    end = parts[part_idx + 1] if part_idx + 1 < len(parts) else len(xy)
                    ring = xy[start:end]
                    if len(ring) >= 4:
                        rings.append(ring)
                shapes.append((rec_num, rings))
        offset += 8 + content_len
    return shapes


def main():
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    active_names = {s["name"] for s in summary["subbasins"]}

    with zipfile.ZipFile(ZIP_PATH) as zf:
        shp = zf.read(SHAPE_NAME)
        dbf = zf.read(DBF_NAME)

    records = read_dbf_records(dbf)
    shapes = read_polygon_shapes(shp)
    features = []

    for (rec_num, rings), attrs in zip(shapes, records):
        name = attrs.get("name") or attrs.get("Name") or attrs.get("NAME") or attrs.get("subbasin")
        basin_id = attrs.get("basinid") or attrs.get("BASINID") or attrs.get("BasinID")
        if name not in active_names:
            continue

        ordered = sorted(rings, key=lambda ring: abs(signed_area(ring)), reverse=True)
        lonlat_rings = []
        for ring in ordered[:3]:
            simplified = simplify_ring(ring)
            coords = []
            for x, y in simplified:
                lat, lon = utm44n_to_lonlat(x, y)
                coords.append([round(lon, 6), round(lat, 6)])
            if coords and coords[0] != coords[-1]:
                coords.append(coords[0])
            if len(coords) >= 4:
                lonlat_rings.append(coords)

        if not lonlat_rings:
            continue

        features.append({
            "type": "Feature",
            "properties": {
                "name": name,
                "basinId": str(basin_id),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": lonlat_rings,
            },
        })

    summary["basinGeoJson"] = {
        "type": "FeatureCollection",
        "features": features,
    }
    summary["basinGeoJsonSource"] = (
        "Sub-basin polygon boundaries extracted from HMS/Sub Basin_HM_Narmada.shp, "
        "converted from WGS84 UTM Zone 44N to lon/lat and simplified for browser display."
    )
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    DATA_JS_PATH.write_text(
        "window.HMS_NARMADA_DATA = "
        + json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Embedded {len(features)} basin polygon features.")


if __name__ == "__main__":
    main()
