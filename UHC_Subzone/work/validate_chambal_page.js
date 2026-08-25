const fs = require("fs");

const html = fs.readFileSync("outputs/chambal-hydrograph-app.html", "utf8");
const scripts = [...html.matchAll(/<script(?: [^>]*)?>([\s\S]*?)<\/script>/g)]
  .map((match) => match[1])
  .filter(Boolean);
const ids = [...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]);
const elements = {};

function makeElement(id, value = "") {
  return {
    id,
    value,
    textContent: "",
    innerHTML: "",
    addEventListener() {}
  };
}

ids.forEach((id) => {
  const match = html.match(new RegExp(`id="${id}"[^>]*value="([^"]*)"`));
  elements[id] = makeElement(id, match ? match[1] : "");
});

Object.assign(elements, {
  damClass: makeElement("damClass", "significant"),
  returnPeriod: makeElement("returnPeriod", "50"),
  stormShape: makeElement("stormShape", "middle")
});

global.document = {
  getElementById(id) {
    if (!elements[id]) elements[id] = makeElement(id);
    return elements[id];
  }
};

scripts.forEach((script) => Function(script)());

console.log(JSON.stringify({
  scripts: scripts.length,
  hasChambalTitle: html.includes("Chambal Unit Hydrograph"),
  peakFlood: elements.peakFlood.textContent,
  uhPeak: elements.uhPeak.textContent,
  chartRendered: elements.chart.innerHTML.includes("Peak"),
  rowsRendered: elements.rows.innerHTML.includes("<tr>")
}, null, 2));
