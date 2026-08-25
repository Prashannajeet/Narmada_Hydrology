const fs = require("fs");

const html = fs.readFileSync("outputs/narmada-tapi-hydrograph-app.html", "utf8");
const scripts = [...html.matchAll(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/g)]
  .map((match) => match[1])
  .filter(Boolean);

scripts.forEach((script) => new Function(script));

console.log(JSON.stringify({
  inlineScripts: scripts.length,
  hasDropdown: html.includes('id="siteSelect"'),
  loadsHms: html.includes('src="hms-narmada-model-data.js"'),
  hasSitePopulation: html.includes("populateSiteDropdown"),
  hasNearestSiteLogic: html.includes("nearestSubbasin")
}, null, 2));
