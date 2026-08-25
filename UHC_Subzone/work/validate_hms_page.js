const fs = require("fs");

const html = fs.readFileSync("outputs/hms-narmada-model-tool.html", "utf8");
const scripts = [...html.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)]
  .map((match) => match[1])
  .filter(Boolean);
const ids = [...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]);
const elements = {};

function makeElement(id, value = "") {
  return {
    id,
    value,
    checked: false,
    textContent: "",
    innerHTML: "",
    href: "",
    addEventListener() {}
  };
}

ids.forEach((id) => {
  elements[id] = makeElement(id);
});

Object.assign(elements, {
  search: makeElement("search", ""),
  region: makeElement("region", "all"),
  sort: makeElement("sort", "name"),
  target: makeElement("target", "upper"),
  floodReturnPeriod: makeElement("floodReturnPeriod", "50"),
  stormShape: makeElement("stormShape", "middle"),
  arealFactor: makeElement("arealFactor", "0.90"),
  loss: makeElement("loss", "2.5"),
  baseflowRate: makeElement("baseflowRate", "0.050"),
  baseFactor: makeElement("baseFactor", "3.5"),
  lowerRain25: makeElement("lowerRain25", "18.0"),
  lowerRain50: makeElement("lowerRain50", "21.0"),
  lowerRain100: makeElement("lowerRain100", "24.0"),
  upperRain25: makeElement("upperRain25", "24.0"),
  upperRain50: makeElement("upperRain50", "28.0"),
  upperRain100: makeElement("upperRain100", "32.0"),
  showBasins: makeElement("showBasins"),
  showSites: makeElement("showSites"),
  showLabels: makeElement("showLabels")
});

elements.showBasins.checked = true;
elements.showSites.checked = true;
elements.showLabels.checked = true;

global.window = {};
global.document = {
  getElementById(id) {
    if (!elements[id]) elements[id] = makeElement(id);
    return elements[id];
  },
  querySelectorAll() {
    return [];
  }
};

scripts.forEach((script) => Function(script)());

const data = window.HMS_NARMADA_DATA;
const result = {
  subbasins: data.subbasinCount,
  floodRowsRendered: elements.floodRows.innerHTML.includes("Sub-7") || elements.floodRows.innerHTML.includes("Sub-1"),
  chartRendered: elements.floodChart.innerHTML.includes("Flood peak"),
  mapRendered: elements.map.innerHTML.includes("HMS site"),
  mapReadoutRendered: elements.mapSelection.textContent.length > 0,
  selectedPeak: elements.dFloodPeak.textContent,
  junctionSites: data.junctionSites?.length || 0,
  hasRestoredSubbasin2: data.subbasins.some((subbasin) => subbasin.name === "Subbasin-2" && subbasin.lat !== 0 && subbasin.lon !== 0),
  removedSubbasins: data.removedSubbasins?.length || 0,
  hasValidSub2: data.subbasins.some((subbasin) => subbasin.name === "Sub-2")
};

console.log(JSON.stringify(result, null, 2));
