import json
import math
import struct
import zipfile
from pathlib import Path


ZIP_PATH = Path(r"E:\01 Projects\03 MPWRD\14 Digitial Atlas\01 Data\01 SHP\01 Basin Wise\Narmada\HMS.zip")
SUMMARY_PATH = Path("work/hms_model_summary.json")
DATA_JS_PATH = Path("outputs/hms-narmada-model-data.js")


def read_dbf_records(raw):
    header_len = int.from_bytes(raw[8:10], "little")
    record_len = int.from_bytes(raw[10:12], "little")
    fields = []
    offset = 32
    while raw[offset] != 0x0D:
        name = raw[offset : offset + 11].split(b"\x00", 1)[0].decode("latin1").strip()
        ftype = chr(raw[offset + 11])
        length = raw[offset + 16]
        fields.append((name, ftype, length))
        offset += 32

    records = []
    pos = header_len
    while pos + record_len <= len(raw):
        if raw[pos] != 0x2A:
            cursor = pos + 1
            item = {}
            for name, ftype, length in fields:
                text = raw[cursor : cursor + length].decode("latin1", errors="ignore").strip()
                cursor += length
                if ftype in {"N", "F"} and text:
                    try:
                        item[name] = float(text) if "." in text else int(text)
                    except ValueError:
                        item[name] = text
                else:
                    item[name] = text
            records.append(item)
        pos += record_len
    return records


def utm44n_to_lonlat(easting, northing):
    # WGS84 / UTM Zone 44N inverse conversion.
    a = 6378137.0
    f = 1 / 298.257223563
    k0 = 0.9996
    e = math.sqrt(f * (2 - f))
    e1sq = e * e / (1 - e * e)
    x = easting - 500000.0
    y = northing
    lon0 = math.radians(81)

    m = y / k0
    mu = m / (a * (1 - e**2 / 4 - 3 * e**4 / 64 - 5 * e**6 / 256))
    e1 = (1 - math.sqrt(1 - e * e)) / (1 + math.sqrt(1 - e * e))

    j1 = 3 * e1 / 2 - 27 * e1**3 / 32
    j2 = 21 * e1**2 / 16 - 55 * e1**4 / 32
    j3 = 151 * e1**3 / 96
    j4 = 1097 * e1**4 / 512
    fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)

    sin_fp = math.sin(fp)
    cos_fp = math.cos(fp)
    tan_fp = math.tan(fp)
    c1 = e1sq * cos_fp**2
    t1 = tan_fp**2
    r1 = a * (1 - e * e) / ((1 - e * e * sin_fp**2) ** 1.5)
    n1 = a / math.sqrt(1 - e * e * sin_fp**2)
    d = x / (n1 * k0)

    lat = fp - (n1 * tan_fp / r1) * (
        d**2 / 2
        - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * e1sq) * d**4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * e1sq - 3 * c1**2) * d**6 / 720
    )
    lon = lon0 + (
        d
        - (1 + 2 * t1 + c1) * d**3 / 6
        + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * e1sq + 24 * t1**2) * d**5 / 120
    ) / cos_fp

    return math.degrees(lat), math.degrees(lon)


def read_point_shapes(raw):
    points = []
    offset = 100
    while offset + 8 <= len(raw):
        rec_num, content_words = struct.unpack(">2i", raw[offset : offset + 8])
        content_len = content_words * 2
        content = raw[offset + 8 : offset + 8 + content_len]
        if len(content) >= 20:
            shape_type = struct.unpack("<i", content[:4])[0]
            if shape_type == 1:
                x, y = struct.unpack("<2d", content[4:20])
                points.append((rec_num, x, y))
        offset += 8 + content_len
    return points


def main():
    with zipfile.ZipFile(ZIP_PATH) as zf:
        shp = zf.read("HMS/Junctions.shp")
        dbf = zf.read("HMS/Junctions.dbf")

    records = read_dbf_records(dbf)
    points = read_point_shapes(shp)
    sites = []
    for idx, ((rec_num, x, y), attrs) in enumerate(zip(points, records), start=1):
        lat, lon = utm44n_to_lonlat(x, y)
        name = attrs.get("junction") or attrs.get("Name") or attrs.get("name") or attrs.get("NAME") or f"Junction-{idx}"
        link = attrs.get("LINKNO", attrs.get("LinkNo", attrs.get("linkno", "")))
        sites.append({
            "name": str(name) if str(name).strip() else f"Junction-{idx}",
            "siteType": "HMS junction/site",
            "lat": lat,
            "lon": lon,
            "utmX": x,
            "utmY": y,
            "linkNo": link,
            "attributes": attrs,
        })

    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    summary["junctionSites"] = sites
    summary["junctionSiteSource"] = "Extracted from HMS/Junctions.shp in HMS.zip; displayed as HMS network/site markers. Confirmed GD station metadata can be added when available."
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = "window.HMS_NARMADA_DATA = "
    data_text = DATA_JS_PATH.read_text(encoding="utf-8").strip()
    if data_text.startswith(payload):
        data = json.loads(data_text[len(payload) :].rstrip(";"))
    else:
        raise ValueError("Unexpected HMS data JS wrapper")
    data["junctionSites"] = sites
    data["junctionSiteSource"] = summary["junctionSiteSource"]
    DATA_JS_PATH.write_text(payload + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")

    print(json.dumps({"junctionSites": len(sites), "sample": sites[:3]}, indent=2))


if __name__ == "__main__":
    main()
