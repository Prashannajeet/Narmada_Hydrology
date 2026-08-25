const fs = require("fs");
const path = require("path");

const basinWiseRoot = process.argv[2] || "E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/01 Basin Wise";
const deliverablesRoot = process.argv[3] || "E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/Deliverables";
const outputPath = process.argv[4] || "outputs/chambal-betwa-spatial-data.js";

const BASINS = {
  betwa: {
    label: "Betwa",
    boundary: path.join(basinWiseRoot, "Betwa", "Sub Basin Betwa.shp"),
    drainage: path.join(basinWiseRoot, "Betwa", "Drainage_Betwa.shp"),
  },
  chambal: {
    label: "Chambal",
    boundary: path.join(basinWiseRoot, "Chambal", "Sub Basin Chambal.shp"),
    drainage: path.join(basinWiseRoot, "Chambal", "Drainage_Chambal.shp"),
  },
};

const SUPPORT_LAYERS = [
  {
    id: "gdSites",
    label: "GD Sites SWEDES",
    source: path.join(deliverablesRoot, "Task 5", "GD Sites SWEDES.shp"),
    type: "point",
    nameFields: ["Station Na", "Station_Na", "Sation_Nam", "Station Co"],
  },
  {
    id: "raingauges",
    label: "Raingauge SWEDES",
    source: path.join(deliverablesRoot, "Task 5", "Raingauge SWEDES.shp"),
    type: "point",
    nameFields: ["Station Na", "Station_Na", "Station Co"],
  },
  {
    id: "dams",
    label: "54 Dams",
    source: path.join(deliverablesRoot, "Task 3", "Dams_EinC_54_R2", "Dams_EinC_54_R2.shp"),
    type: "point",
    nameFields: ["Dam_Name", "DamName", "Name", "DAM_NAME", "PROJECT"],
  },
  {
    id: "districts",
    label: "Districts",
    source: path.join(deliverablesRoot, "Task 4", "District.shp"),
    type: "polygon",
    nameFields: ["dist_nm_e", "District", "NAME"],
  },
];

function readDbf(dbfPath) {
  const raw = fs.readFileSync(dbfPath);
  const headerLength = raw.readUInt16LE(8);
  const recordLength = raw.readUInt16LE(10);
  const fields = [];
  let offset = 32;
  while (offset < headerLength - 1 && raw[offset] !== 0x0d) {
    const name = raw.subarray(offset, offset + 11).toString("latin1").replace(/\0/g, "").trim();
    if (name) {
      fields.push({
        name,
        type: String.fromCharCode(raw[offset + 11]),
        length: raw[offset + 16],
        decimals: raw[offset + 17],
      });
    }
    offset += 32;
  }

  const rows = [];
  for (let pos = headerLength; pos + recordLength <= raw.length; pos += recordLength) {
    if (raw[pos] === 0x2a) continue;
    const row = {};
    let cursor = pos + 1;
    for (const field of fields) {
      const text = raw.subarray(cursor, cursor + field.length).toString("latin1").replace(/\0/g, "").trim();
      cursor += field.length;
      if (field.type === "N" || field.type === "F") {
        const num = Number(text);
        row[field.name] = Number.isFinite(num) ? num : text;
      } else {
        row[field.name] = text;
      }
    }
    rows.push(row);
  }
  return rows;
}

function readShapeFile(shpPath) {
  const raw = fs.readFileSync(shpPath);
  const records = [];
  let offset = 100;
  while (offset + 8 <= raw.length) {
    const contentLength = raw.readInt32BE(offset + 4) * 2;
    const content = raw.subarray(offset + 8, offset + 8 + contentLength);
    if (content.length >= 4) {
      const shapeType = content.readInt32LE(0);
      if (shapeType === 1 || shapeType === 11 || shapeType === 21) {
        records.push({ shapeType, type: "Point", coordinates: [content.readDoubleLE(4), content.readDoubleLE(12)] });
      } else if ([3, 5, 13, 15, 23, 25].includes(shapeType) && content.length >= 44) {
        const numParts = content.readInt32LE(36);
        const numPoints = content.readInt32LE(40);
        const parts = [];
        let cursor = 44;
        for (let i = 0; i < numParts; i += 1) parts.push(content.readInt32LE(cursor + i * 4));
        cursor += numParts * 4;
        const points = [];
        for (let i = 0; i < numPoints; i += 1) {
          points.push([content.readDoubleLE(cursor + i * 16), content.readDoubleLE(cursor + i * 16 + 8)]);
        }
        const lines = parts.map((start, i) => points.slice(start, parts[i + 1] ?? points.length));
        records.push({
          shapeType,
          type: [5, 15, 25].includes(shapeType) ? "Polygon" : "LineString",
          coordinates: lines,
        });
      }
    }
    offset += 8 + contentLength;
  }
  return records;
}

function readPrj(shpPath) {
  const prjPath = `${shpPath.slice(0, -4)}.prj`;
  return fs.existsSync(prjPath) ? fs.readFileSync(prjPath, "utf8") : "";
}

function webMercatorToLonLat(point) {
  const radius = 6378137;
  const lon = (point[0] / radius) * (180 / Math.PI);
  const lat = (Math.atan(Math.sinh(point[1] / radius))) * (180 / Math.PI);
  return [lon, lat];
}

function transformCoords(coords, transform) {
  if (typeof coords[0] === "number") return transform(coords);
  return coords.map((child) => transformCoords(child, transform));
}

function projectionTransformFor(shpPath) {
  const prj = readPrj(shpPath);
  if (/Web_Mercator|Mercator_Auxiliary_Sphere/i.test(prj)) return webMercatorToLonLat;
  return null;
}

function readFeatures(shpPath, nameFields = []) {
  const dbfPath = `${shpPath.slice(0, -4)}.dbf`;
  const transform = projectionTransformFor(shpPath);
  const shapes = readShapeFile(shpPath).map((shape) => transform
    ? { ...shape, coordinates: transformCoords(shape.coordinates, transform) }
    : shape);
  const attrs = fs.existsSync(dbfPath) ? readDbf(dbfPath) : [];
  return shapes.map((shape, index) => {
    const properties = attrs[index] || {};
    const name = nameFields.map((field) => properties[field]).find((value) => String(value || "").trim()) ||
      properties.SubSubBas || properties.SubSubBasi || properties.SUB_NAME || properties.Dam_Name || properties["Station Na"] ||
      `${path.basename(shpPath, ".shp")}-${index + 1}`;
    return { ...shape, properties: { ...properties, name: String(name).trim() } };
  });
}

function bboxForCoords(coords, bbox = [Infinity, Infinity, -Infinity, -Infinity]) {
  if (typeof coords[0] === "number") {
    bbox[0] = Math.min(bbox[0], coords[0]);
    bbox[1] = Math.min(bbox[1], coords[1]);
    bbox[2] = Math.max(bbox[2], coords[0]);
    bbox[3] = Math.max(bbox[3], coords[1]);
  } else {
    coords.forEach((child) => bboxForCoords(child, bbox));
  }
  return bbox;
}

function bboxIntersects(a, b) {
  return a[0] <= b[2] && a[2] >= b[0] && a[1] <= b[3] && a[3] >= b[1];
}

function pointInRing(point, ring) {
  const [x, y] = point;
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i, i += 1) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    const intersects = ((yi > y) !== (yj > y)) && x < ((xj - xi) * (y - yi)) / ((yj - yi) || Number.EPSILON) + xi;
    if (intersects) inside = !inside;
  }
  return inside;
}

function pointInPolygon(point, polygonFeature) {
  return polygonFeature.coordinates.some((ring, index) => {
    if (index === 0) return pointInRing(point, ring);
    return false;
  });
}

function pointInAnyBoundary(point, boundaryFeatures) {
  return boundaryFeatures.some((feature) => pointInPolygon(point, feature));
}

function representativePoints(feature) {
  if (feature.type === "Point") return [feature.coordinates];
  const points = [];
  const visit = (coords) => {
    if (typeof coords[0] === "number") points.push(coords);
    else coords.forEach(visit);
  };
  visit(feature.coordinates);
  const stride = Math.max(1, Math.floor(points.length / 60));
  return points.filter((_, index) => index % stride === 0);
}

function featureInsideBoundary(feature, boundaryFeatures, boundaryBbox) {
  const featureBbox = bboxForCoords(feature.coordinates);
  if (!bboxIntersects(featureBbox, boundaryBbox)) return false;
  return representativePoints(feature).some((point) => pointInAnyBoundary(point, boundaryFeatures));
}

function simplifyLine(line, maxPoints = 240) {
  if (line.length <= maxPoints) return line;
  const stride = Math.ceil(line.length / maxPoints);
  const sampled = line.filter((_, index) => index % stride === 0);
  if (sampled[sampled.length - 1] !== line[line.length - 1]) sampled.push(line[line.length - 1]);
  return sampled;
}

function toGeoJsonFeature(feature) {
  if (feature.type === "Point") {
    return { type: "Feature", properties: feature.properties, geometry: { type: "Point", coordinates: feature.coordinates } };
  }
  if (feature.type === "LineString") {
    const lines = feature.coordinates.map((line) => simplifyLine(line)).filter((line) => line.length > 1);
    return {
      type: "Feature",
      properties: feature.properties,
      geometry: lines.length === 1 ? { type: "LineString", coordinates: lines[0] } : { type: "MultiLineString", coordinates: lines },
    };
  }
  return {
    type: "Feature",
    properties: feature.properties,
    geometry: { type: "Polygon", coordinates: feature.coordinates.map((ring) => simplifyLine(ring, 420)) },
  };
}

function featureCollection(features) {
  return { type: "FeatureCollection", features: features.map(toGeoJsonFeature) };
}

function featureSummary(features) {
  return {
    count: features.length,
    sample: features.slice(0, 6).map((feature) => feature.properties.name),
  };
}

function build() {
  const data = {
    sourceRule: "Task 3/4/5 support layers are filtered by the authoritative Betwa/Chambal basin boundary polygons; Geotagging is excluded.",
    generatedAt: new Date().toISOString(),
    basins: {},
  };
  const summary = {};

  for (const [basinId, basin] of Object.entries(BASINS)) {
    const boundary = readFeatures(basin.boundary, ["SubSubBas", "Sub_Basin", "Basin_NM"]);
    const boundaryBbox = bboxForCoords(boundary.map((feature) => feature.coordinates));
    const drainage = readFeatures(basin.drainage, ["SubSubBas", "Sub_Basin", "Basin_NM", "ORD_STRA"])
      .filter((feature) => featureInsideBoundary(feature, boundary, boundaryBbox));

    const layers = {
      boundary: featureCollection(boundary),
      drainage: featureCollection(drainage),
    };
    summary[basinId] = {
      boundary: featureSummary(boundary),
      drainage: featureSummary(drainage),
      support: {},
    };

    for (const layer of SUPPORT_LAYERS) {
      if (!fs.existsSync(layer.source)) continue;
      const features = readFeatures(layer.source, layer.nameFields)
        .filter((feature) => featureInsideBoundary(feature, boundary, boundaryBbox));
      layers[layer.id] = featureCollection(features);
      summary[basinId].support[layer.id] = featureSummary(features);
    }

    data.basins[basinId] = {
      label: basin.label,
      boundaryBbox,
      layers,
    };
  }

  fs.writeFileSync(outputPath, `window.UHC_BASIN_SPATIAL_DATA = ${JSON.stringify(data)};\n`, "utf8");
  console.log(JSON.stringify({ outputPath, summary }, null, 2));
}

build();
