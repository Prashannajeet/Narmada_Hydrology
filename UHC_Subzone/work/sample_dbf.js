const fs = require("fs");

const dbfPath = process.argv[2];
const limit = Number(process.argv[3] || 5);

if (!dbfPath) {
  console.error("Usage: node work/sample_dbf.js <file.dbf> [limit]");
  process.exit(1);
}

const buffer = fs.readFileSync(dbfPath);
const records = buffer.readUInt32LE(4);
const headerLength = buffer.readUInt16LE(8);
const recordLength = buffer.readUInt16LE(10);
const fields = [];

for (let offset = 32; offset < headerLength - 1; offset += 32) {
  if (buffer[offset] === 0x0d) break;
  const name = buffer.subarray(offset, offset + 11).toString("ascii").replace(/\0/g, "").trim();
  if (!name) continue;
  fields.push({
    name,
    type: String.fromCharCode(buffer[offset + 11]),
    length: buffer[offset + 16],
  });
}

console.log(JSON.stringify({ file: dbfPath, records, fields: fields.map((field) => field.name) }));

for (let record = 0, emitted = 0; record < records && emitted < limit; record += 1) {
  const rowOffset = headerLength + (record * recordLength);
  if (buffer[rowOffset] === 0x2a) continue;
  const row = {};
  let fieldOffset = rowOffset + 1;
  for (const field of fields) {
    row[field.name] = buffer.subarray(fieldOffset, fieldOffset + field.length).toString("latin1").trim();
    fieldOffset += field.length;
  }
  console.log(JSON.stringify(row));
  emitted += 1;
}
