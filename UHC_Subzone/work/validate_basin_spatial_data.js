const fs = require("fs");
const vm = require("vm");

const script = fs.readFileSync("outputs/chambal-betwa-spatial-data.js", "utf8");
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(script, sandbox);

const data = sandbox.window.UHC_BASIN_SPATIAL_DATA;
if (!data) throw new Error("Missing UHC_BASIN_SPATIAL_DATA");

const expected = {
  betwa: { boundary: 1, drainage: 2610, gdSites: 16, raingauges: 59, dams: 8 },
  chambal: { boundary: 6, drainage: 4413, gdSites: 17, raingauges: 97, dams: 10 },
};

for (const [basin, layers] of Object.entries(expected)) {
  const actual = data.basins?.[basin]?.layers;
  if (!actual) throw new Error(`Missing basin ${basin}`);
  for (const [layer, count] of Object.entries(layers)) {
    const got = actual[layer]?.features?.length;
    if (got !== count) throw new Error(`${basin}.${layer}: expected ${count}, got ${got}`);
  }
}

console.log(JSON.stringify({
  basins: Object.keys(data.basins),
  rule: data.sourceRule,
  betwa: Object.fromEntries(Object.keys(expected.betwa).map((layer) => [layer, data.basins.betwa.layers[layer].features.length])),
  chambal: Object.fromEntries(Object.keys(expected.chambal).map((layer) => [layer, data.basins.chambal.layers[layer].features.length])),
}, null, 2));
