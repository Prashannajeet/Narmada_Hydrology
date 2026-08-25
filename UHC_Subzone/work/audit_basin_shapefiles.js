const fs = require("fs");
const path = require("path");

const root = process.argv[2];
const basinNames = process.argv.slice(3);

if (!root || !basinNames.length) {
  console.error("Usage: node work/audit_basin_shapefiles.js <root> <basin...>");
  process.exit(1);
}

const shapeTypes = {
  0: "Null",
  1: "Point",
  3: "Polyline",
  5: "Polygon",
  8: "MultiPoint",
  11: "PointZ",
  13: "PolylineZ",
  15: "PolygonZ",
  18: "MultiPointZ",
  21: "PointM",
  23: "PolylineM",
  25: "PolygonM",
  28: "MultiPointM",
  31: "MultiPatch",
};

function readShpMeta(shpPath) {
  const buffer = fs.readFileSync(shpPath);
  return {
    shapeType: shapeTypes[buffer.readInt32LE(32)] || `Type ${buffer.readInt32LE(32)}`,
    bbox: {
      xmin: buffer.readDoubleLE(36),
      ymin: buffer.readDoubleLE(44),
      xmax: buffer.readDoubleLE(52),
      ymax: buffer.readDoubleLE(60),
    },
  };
}

function readDbfMeta(dbfPath) {
  const buffer = fs.readFileSync(dbfPath);
  const records = buffer.readUInt32LE(4);
  const headerLength = buffer.readUInt16LE(8);
  const recordLength = buffer.readUInt16LE(10);
  const fields = [];
  for (let offset = 32; offset < headerLength - 1; offset += 32) {
    if (buffer[offset] === 0x0d) break;
    const rawName = buffer.subarray(offset, offset + 11).toString("ascii");
    const name = rawName.replace(/\0/g, "").trim();
    if (!name) continue;
    fields.push({
      name,
      type: String.fromCharCode(buffer[offset + 11]),
      length: buffer[offset + 16],
      decimals: buffer[offset + 17],
    });
  }
  const rows = [];
  for (let record = 0; record < Math.min(records, 8); record += 1) {
    const rowOffset = headerLength + (record * recordLength);
    if (buffer[rowOffset] === 0x2a) continue;
    const row = {};
    let fieldOffset = rowOffset + 1;
    for (const field of fields) {
      const value = buffer.subarray(fieldOffset, fieldOffset + field.length).toString("latin1").trim();
      row[field.name] = value;
      fieldOffset += field.length;
    }
    rows.push(row);
  }
  return { records, headerLength, recordLength, fields, rows };
}

function projectionName(prjPath) {
  if (!fs.existsSync(prjPath)) return null;
  const prj = fs.readFileSync(prjPath, "utf8");
  const match = prj.match(/PROJCS\["([^"]+)"/) || prj.match(/GEOGCS\["([^"]+)"/);
  return match ? match[1] : prj.slice(0, 120);
}

for (const basin of basinNames) {
  const basinDir = path.join(root, basin);
  const shpFiles = fs.readdirSync(basinDir)
    .filter((file) => file.toLowerCase().endsWith(".shp"))
    .sort();

  console.log(`\n# ${basin}`);
  for (const file of shpFiles) {
    const base = path.join(basinDir, file.slice(0, -4));
    const shpPath = `${base}.shp`;
    const dbfPath = `${base}.dbf`;
    const prjPath = `${base}.prj`;
    const shp = readShpMeta(shpPath);
    const dbf = fs.existsSync(dbfPath) ? readDbfMeta(dbfPath) : null;

    console.log(JSON.stringify({
      file,
      shapeType: shp.shapeType,
      records: dbf?.records ?? null,
      bbox: shp.bbox,
      projection: projectionName(prjPath),
      fields: dbf?.fields.map((field) => field.name) ?? [],
      sampleRows: shp.shapeType.includes("Polygon") ? dbf?.rows ?? [] : undefined,
      sizeBytes: fs.statSync(shpPath).size,
    }));
  }
}
