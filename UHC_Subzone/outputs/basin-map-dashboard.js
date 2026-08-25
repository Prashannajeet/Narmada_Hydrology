(function () {
  const fmt = new Intl.NumberFormat("en-IN", { maximumFractionDigits: 1 });

  function $(root, selector) {
    return root.querySelector(selector);
  }

  function layerCount(data, layerId) {
    return data?.layers?.[layerId]?.features?.length || 0;
  }

  function setText(root, selector, value) {
    const node = $(root, selector);
    if (node) node.textContent = value;
  }

  function styleFor(kind, selected) {
    if (!window.ol) return null;
    const palette = {
      boundary: { fill: "rgba(111, 159, 212, 0.22)", stroke: selected ? "#d88491" : "#5f91c7" },
      drainage: { stroke: "#75a9a1" },
      gdSites: { fill: "#d88491", stroke: "#fffdfa", points: 4 },
      raingauges: { fill: "#f0ad98", stroke: "#fffdfa", points: 3 },
      dams: { fill: "#ffd98f", stroke: "#6f7f95", points: 5 },
      districts: { fill: "rgba(238, 232, 251, 0.16)", stroke: "rgba(111, 127, 149, 0.48)" },
    };
    const color = palette[kind] || palette.boundary;
    if (kind === "drainage") {
      return new ol.style.Style({
        stroke: new ol.style.Stroke({ color: color.stroke, width: selected ? 2.6 : 1.1 }),
      });
    }
    if (["gdSites", "raingauges", "dams"].includes(kind)) {
      return new ol.style.Style({
        image: new ol.style.Circle({
          radius: selected ? (color.points || 4) + 2 : color.points || 4,
          fill: new ol.style.Fill({ color: color.fill }),
          stroke: new ol.style.Stroke({ color: color.stroke, width: selected ? 2.4 : 1.3 }),
        }),
      });
    }
    return new ol.style.Style({
      fill: new ol.style.Fill({ color: color.fill }),
      stroke: new ol.style.Stroke({ color: color.stroke, width: selected ? 2.4 : 1.1 }),
    });
  }

  function firstValue(properties, names) {
    for (const name of names) {
      const value = properties?.[name];
      if (value !== undefined && value !== null && String(value).trim()) return String(value).trim();
    }
    return "";
  }

  function featureLabel(feature) {
    const p = feature.getProperties();
    return firstValue(p, ["name", "Station Na", "Station_Na", "Dam_Name", "Reservoir", "SubSubBas", "dist_nm_e"]) || "Map feature";
  }

  function featureType(kind) {
    return {
      boundary: "Basin / sub-basin",
      drainage: "Drainage",
      gdSites: "GD site",
      raingauges: "Raingauge",
      dams: "54 Dams",
      districts: "District context",
    }[kind] || "Spatial feature";
  }

  function updateHydrologyInputs(feature) {
    const p = feature.getProperties();
    const kind = feature.get("layerKind");
    const name = featureLabel(feature);
    const project = document.getElementById("project");
    if (project) project.value = name;

    const areaValue = Number(p.SUB_AREA || p.Catchment || p.CATCH_SKM || p.area_sqkm || 0);
    if (Number.isFinite(areaValue) && areaValue > 0 && kind !== "districts") {
      const area = document.getElementById("area");
      if (area) area.value = String(Math.round(areaValue * 10) / 10);
    }

    const calculate = document.getElementById("calculate");
    if (calculate) calculate.click();
  }

  function initMap(root) {
    const basinId = root.dataset.basinMap;
    const data = window.UHC_BASIN_SPATIAL_DATA?.basins?.[basinId];
    if (!data) {
      setText(root, "[data-map-status]", "Spatial data not found.");
      return;
    }
    if (!window.ol) {
      setText(root, "[data-map-status]", "OpenLayers library not loaded.");
      return;
    }

    setText(root, "[data-boundary-count]", layerCount(data, "boundary"));
    setText(root, "[data-drainage-count]", layerCount(data, "drainage"));
    setText(root, "[data-gd-count]", layerCount(data, "gdSites"));
    setText(root, "[data-rain-count]", layerCount(data, "raingauges"));
    setText(root, "[data-dam-count]", layerCount(data, "dams"));

    let selectedFeature = null;
    const layers = {};
    const geoJson = new ol.format.GeoJSON();

    function makeVectorLayer(kind, zIndex, visible) {
      const source = new ol.source.Vector({
        features: geoJson.readFeatures(data.layers[kind] || { type: "FeatureCollection", features: [] }, {
          featureProjection: "EPSG:3857",
        }),
      });
      source.getFeatures().forEach((feature) => feature.set("layerKind", kind));
      const layer = new ol.layer.Vector({
        source,
        visible,
        zIndex,
        style: (feature) => styleFor(kind, feature === selectedFeature),
      });
      layers[kind] = layer;
      return layer;
    }

    const map = new ol.Map({
      target: $ (root, "[data-map-target]"),
      layers: [
        new ol.layer.Tile({ source: new ol.source.OSM() }),
        makeVectorLayer("districts", 2, false),
        makeVectorLayer("boundary", 4, true),
        makeVectorLayer("drainage", 5, true),
        makeVectorLayer("gdSites", 8, true),
        makeVectorLayer("raingauges", 7, false),
        makeVectorLayer("dams", 9, true),
      ],
      view: new ol.View({ center: ol.proj.fromLonLat([(data.boundaryBbox[0] + data.boundaryBbox[2]) / 2, (data.boundaryBbox[1] + data.boundaryBbox[3]) / 2]), zoom: 7 }),
      controls: ol.control.defaults.defaults({ attribution: false }).extend([new ol.control.ScaleLine()]),
    });

    const boundaryExtent = layers.boundary.getSource().getExtent();
    if (boundaryExtent && boundaryExtent.every(Number.isFinite)) {
      map.getView().fit(boundaryExtent, { padding: [18, 18, 18, 18], maxZoom: 9 });
    }

    root.querySelectorAll("[data-layer-toggle]").forEach((input) => {
      const layer = layers[input.dataset.layerToggle];
      if (!layer) return;
      input.checked = layer.getVisible();
      input.addEventListener("change", () => layer.setVisible(input.checked));
    });

    map.on("singleclick", (event) => {
      const feature = map.forEachFeatureAtPixel(event.pixel, (item) => item, { hitTolerance: 6 });
      if (!feature) return;
      if (selectedFeature) layers[selectedFeature.get("layerKind")]?.changed();
      selectedFeature = feature;
      layers[selectedFeature.get("layerKind")]?.changed();
      const p = feature.getProperties();
      const kind = feature.get("layerKind");
      setText(root, "[data-selected-name]", featureLabel(feature));
      setText(root, "[data-selected-type]", featureType(kind));
      setText(root, "[data-selected-area]", firstValue(p, ["SUB_AREA", "Catchment", "CATCH_SKM", "area_sqkm"]) || "-");
      setText(root, "[data-selected-river]", firstValue(p, ["River", "Tributary", "Sub Tribut", "SubSubBas", "SubSubBasi"]) || "-");
      updateHydrologyInputs(feature);
    });

    setText(root, "[data-map-status]", `${data.label} layers clipped to basin boundary. Click a polygon or point to update the calculator.`);
  }

  window.initUhcBasinMaps = function initUhcBasinMaps() {
    document.querySelectorAll("[data-basin-map]").forEach(initMap);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", window.initUhcBasinMaps);
  } else {
    window.initUhcBasinMaps();
  }
}());
