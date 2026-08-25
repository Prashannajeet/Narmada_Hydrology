const fs = require("fs");
const path = require("path");

const root = process.argv[2];

if (!root) {
  console.error("Usage: node work/audit_deliverables_shapefiles.js <deliverables-root>");
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

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(fullPath, files);
    else if (entry.isFile() && entry.name.toLowerCase().endsWith(".shp")) files.push(fullPath);
  }
  return files;
}

function readShpMeta(shpPath) {
  const buffer = fs.readFileSync(shpPath);
  if (buffer.length < 100) return { shapeType: "Invalid/empty", bbox: null };
  const typeCode = buffer.readInt32LE(32);
  return {
    shapeType: shapeTypes[typeCode] || `Type ${typeCode}`,
    bbox: {
      xmin: buffer.readDoubleLE(36),
      ymin: buffer.readDoubleLE(44),
      xmax: buffer.readDoubleLE(52),
      ymax: buffer.readDoubleLE(60),
    },
  };
}

function readDbfMeta(dbfPath) {
  if (!fs.existsSync(dbfPath)) return null;
  const buffer = fs.readFileSync(dbfPath);
  if (buffer.length < 32) return { records: 0, fields: [] };
  const records = buffer.readUInt32LE(4);
  const headerLength = buffer.readUInt16LE(8);
  const fields = [];
  for (let offset = 32; offset < headerLength - 1; offset += 32) {
    if (buffer[offset] === 0x0d) break;
    const name = buffer.subarray(offset, offset + 11).toString("ascii").replace(/\0/g, "").trim();
    if (name) fields.push(name);
  }
  return { records, fields };
}

function projectionName(prjPath) {
  if (!fs.existsSync(prjPath)) return "Missing";
  const prj = fs.readFileSync(prjPath, "utf8");
  const match = prj.match(/PROJCS\["([^"]+)"/) || prj.match(/GEOGCS\["([^"]+)"/);
  return match ? match[1] : "Unknown";
}

const rows = walk(root)
  .filter((file) => !file.includes(".sr.lock"))
  .map((shpPath) => {
    const base = shpPath.slice(0, -4);
    const shp = readShpMeta(shpPath);
    const dbf = readDbfMeta(`${base}.dbf`);
    return {
      group: path.relative(root, path.dirname(shpPath)).split(path.sep)[0] || ".",
      folder: path.relative(root, path.dirname(shpPath)),
      file: path.basename(shpPath),
      shapeType: shp.shapeType,
      records: dbf?.records ?? null,
      projection: projectionName(`${base}.prj`),
      fields: dbf?.fields ?? [],
      sizeBytes: fs.statSync(shpPath).size,
      bbox: shp.bbox,
    };
  })
  .sort((a, b) => `${a.group}/${a.folder}/${a.file}`.localeCompare(`${b.group}/${b.folder}/${b.file}`));

const summary = {};
for (const row of rows) {
  summary[row.group] ||= { shapefiles: 0, points: 0, lines: 0, polygons: 0, emptyOrTiny: 0 };
  summary[row.group].shapefiles += 1;
  if (row.shapeType.includes("Point")) summary[row.group].points += 1;
  if (row.shapeType.includes("Polyline")) summary[row.group].lines += 1;
  if (row.shapeType.includes("Polygon")) summary[row.group].polygons += 1;
  if (!row.records || row.sizeBytes < 120) summary[row.group].emptyOrTiny += 1;
}

console.log("# SUMMARY");
for (const [group, value] of Object.entries(summary)) {
  console.log(JSON.stringify({ group, ...value }));
}

console.log("\n# LAYERS");
for (const row of rows) {
  console.log(JSON.stringify({
    folder: row.folder,
    file: row.file,
    shapeType: row.shapeType,
    records: row.records,
    projection: row.projection,
    fields: row.fields.slice(0, 16),
    sizeBytes: row.sizeBytes,
    bbox: row.bbox,
  }));
}
