"use client";

import "leaflet/dist/leaflet.css";
import { useEffect, useMemo, useState } from "react";
import type { Dispatch, MouseEvent, SetStateAction } from "react";
import { CircleMarker, GeoJSON, MapContainer, Marker, Popup, TileLayer, Tooltip, useMap, useMapEvents } from "react-leaflet";
import type { Feature, FeatureCollection, Geometry } from "geojson";
import L, { LatLngBounds } from "leaflet";
import type { Layer } from "leaflet";
import type { Dam } from "../lib/api";

const LIVING_ATLAS_DAMS_URL = "https://livingatlas.esri.in/server1/rest/services/India/IN_Dams/MapServer/0/query";
const ADMIN_BOUNDARY_STATE_URL = "https://livingatlas.esri.in/server/rest/services/LivingAtlas/IND_AdminBoundary/MapServer/1/query";
const ADMIN_BOUNDARY_DISTRICT_URL = "https://livingatlas.esri.in/server/rest/services/LivingAtlas/IND_AdminBoundary/MapServer/2/query";
const LIVING_ATLAS_ID_BATCH_SIZE = 250;
const ADMIN_BOUNDARY_ID_BATCH_SIZE = 3;
const ADMIN_BOUNDARY_CONCURRENCY = 8;
const RESERVOIR_MIN_ZOOM = 7;
const LABEL_MIN_ZOOM = 10;

const riskColor: Record<string, string> = {
  critical: "#dc2626",
  high: "#f59e0b",
  moderate: "#14b8a6",
  low: "#16a34a"
};

type LivingAtlasProperties = {
  objectid?: number;
  uid?: string;
  state?: string;
  district?: string;
  name?: string;
  pic?: string;
  operated_maintain?: string;
  year_completion?: number;
  river_basin?: string;
  river?: string;
  dam_type?: string;
  height_lowest_level?: number;
  dam_length?: number;
  grosss_rage_capacity?: number;
  effective_storage_capacity?: number;
};

type LivingAtlasFeature = Feature<Geometry, LivingAtlasProperties>;
type LivingAtlasFeatureCollection = FeatureCollection<Geometry, LivingAtlasProperties>;
type AdminBoundaryProperties = {
  objectid?: number;
  state?: string;
  district?: string;
  country?: string;
};
type AdminBoundaryFeature = Feature<Geometry, AdminBoundaryProperties>;
type AdminBoundaryFeatureCollection = FeatureCollection<Geometry, AdminBoundaryProperties>;
type AdminBoundaryBatchResult = { features: AdminBoundaryFeature[]; skipped: number };
type LayerVisibility = {
  reservoirs: boolean;
  dams: boolean;
  stateBoundaries: boolean;
  districtBoundaries: boolean;
  labels: boolean;
};

export default function DamMap({
  dams,
  selectedDamId,
  stateFilter,
  onSelect
}: {
  dams: Dam[];
  selectedDamId?: string;
  stateFilter?: string;
  onSelect: (dam: Dam) => void;
}) {
  const mappedDams = dams.filter((dam) => dam.latitude && dam.longitude);
  const [livingAtlas, setLivingAtlas] = useState<LivingAtlasFeatureCollection | null>(null);
  const [livingAtlasStatus, setLivingAtlasStatus] = useState("Loading Living Atlas dams...");
  const [stateBoundaries, setStateBoundaries] = useState<AdminBoundaryFeatureCollection | null>(null);
  const [districtBoundaries, setDistrictBoundaries] = useState<AdminBoundaryFeatureCollection | null>(null);
  const [boundaryStatus, setBoundaryStatus] = useState("Loading state and district boundaries...");
  const [zoom, setZoom] = useState(5);
  const [layers, setLayers] = useState<LayerVisibility>({
    reservoirs: true,
    dams: true,
    stateBoundaries: true,
    districtBoundaries: true,
    labels: true
  });
  const initialCenter = getStateCenter(stateFilter);
  const roundedZoom = Math.round(zoom);
  const showReservoirs = layers.reservoirs && roundedZoom >= RESERVOIR_MIN_ZOOM;
  const showLabels = layers.labels && roundedZoom >= LABEL_MIN_ZOOM;

  useEffect(() => {
    setZoom(stateFilter ? RESERVOIR_MIN_ZOOM : 5);
  }, [stateFilter]);

  useEffect(() => {
    const controller = new AbortController();
    async function loadLivingAtlasLayer() {
      if (!showReservoirs) {
        setLivingAtlas(null);
        setLivingAtlasStatus(`Zoom to level ${RESERVOIR_MIN_ZOOM}+ to display reservoir polygons`);
        return;
      }
      try {
        setLivingAtlasStatus("Loading Living Atlas dams...");
        const where = stateFilter ? `state='${stateFilter.replace(/'/g, "''")}'` : "1=1";
        const idResponse = await fetch(buildLivingAtlasIdsUrl(where), { signal: controller.signal });
        if (!idResponse.ok) throw new Error(`ID request failed with ${idResponse.status}`);
        const idData = (await idResponse.json()) as { objectIds?: number[] };
        const objectIds = idData.objectIds ?? [];
        const features: LivingAtlasFeature[] = [];
        for (let index = 0; index < objectIds.length; index += LIVING_ATLAS_ID_BATCH_SIZE) {
          const ids = objectIds.slice(index, index + LIVING_ATLAS_ID_BATCH_SIZE);
          const response = await fetch(buildLivingAtlasFeaturesUrl(where, ids), { signal: controller.signal });
          if (!response.ok) throw new Error(`Feature request failed with ${response.status}`);
          const data = (await response.json()) as LivingAtlasFeatureCollection;
          features.push(...(data.features ?? []));
          setLivingAtlasStatus(`Loaded ${features.length.toLocaleString("en-IN")} of ${objectIds.length.toLocaleString("en-IN")} Living Atlas polygons`);
        }
        setLivingAtlas({ type: "FeatureCollection", features });
        setLivingAtlasStatus(`${features.length.toLocaleString("en-IN")} Living Atlas dam polygons`);
      } catch (error) {
        if (controller.signal.aborted) return;
        setLivingAtlas(null);
        setLivingAtlasStatus(error instanceof Error ? error.message : "Living Atlas layer unavailable");
      }
    }

    void loadLivingAtlasLayer();
    return () => controller.abort();
  }, [stateFilter, showReservoirs]);

  const livingAtlasKey = useMemo(() => `${stateFilter || "india"}-${livingAtlas?.features.length ?? 0}`, [livingAtlas, stateFilter]);
  const stateBoundaryKey = useMemo(() => `states-${stateFilter || "india"}-${stateBoundaries?.features.length ?? 0}`, [stateBoundaries, stateFilter]);
  const districtBoundaryKey = useMemo(
    () => `districts-${stateFilter || "india"}-${districtBoundaries?.features.length ?? 0}`,
    [districtBoundaries, stateFilter]
  );

  useEffect(() => {
    const controller = new AbortController();
    async function loadAdminBoundaries() {
      try {
        setBoundaryStatus("Loading state and district boundaries...");
        const where = stateFilter ? `state='${stateFilter.replace(/'/g, "''")}'` : "1=1";
        const [stateResult, districtResult] = await Promise.all([
          fetchAdminBoundaryLayer(ADMIN_BOUNDARY_STATE_URL, where, "objectid,state,country", controller.signal),
          fetchAdminBoundaryLayer(ADMIN_BOUNDARY_DISTRICT_URL, where, "objectid,district,state,country", controller.signal)
        ]);
        const stateFeatures = stateResult.features;
        const districtFeatures = districtResult.features;
        const skipped = stateResult.skipped + districtResult.skipped;
        setStateBoundaries({ type: "FeatureCollection", features: stateFeatures });
        setDistrictBoundaries({ type: "FeatureCollection", features: districtFeatures });
        setBoundaryStatus(
          `${stateFeatures.length.toLocaleString("en-IN")} state / ${districtFeatures.length.toLocaleString("en-IN")} district boundaries${skipped ? ` (${skipped} skipped)` : ""}`
        );
      } catch (error) {
        if (controller.signal.aborted) return;
        setStateBoundaries(null);
        setDistrictBoundaries(null);
        setBoundaryStatus(error instanceof Error ? error.message : "Boundary layers unavailable");
      }
    }

    void loadAdminBoundaries();
    return () => controller.abort();
  }, [stateFilter]);

  return (
    <MapContainer key={stateFilter || "india"} center={initialCenter} zoom={stateFilter ? RESERVOIR_MIN_ZOOM : 5} scrollWheelZoom className="dam-map">
      <MapInteractionController
        dams={mappedDams}
        selectedDamId={selectedDamId}
        stateFilter={stateFilter}
        stateBoundaries={stateBoundaries}
        districtBoundaries={districtBoundaries}
        onZoomChange={setZoom}
      />
      <MapZoomButtons />
      <TileLayer
        attribution="Tiles &copy; Esri"
        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}"
      />
      {layers.districtBoundaries && districtBoundaries ? (
        <GeoJSON
          key={districtBoundaryKey}
          data={districtBoundaries}
          style={{
            color: "#64748b",
            weight: 0.8,
            opacity: 0.75,
            fillOpacity: 0
          }}
          onEachFeature={(feature: AdminBoundaryFeature, layer: Layer) => {
            const properties = feature.properties ?? {};
            layer.bindPopup(renderBoundaryPopup("District Boundary", properties));
          }}
        />
      ) : null}
      {showReservoirs && livingAtlas ? (
        <GeoJSON
          key={livingAtlasKey}
          data={livingAtlas}
          style={{
            color: "#0f766e",
            weight: 1,
            fillColor: "#22d3ee",
            fillOpacity: 0.22
          }}
          onEachFeature={(feature: LivingAtlasFeature, layer: Layer) => {
            const properties = feature.properties ?? {};
            layer.bindPopup(renderLivingAtlasPopup(properties));
          }}
        />
      ) : null}
      {layers.stateBoundaries && stateBoundaries ? (
        <GeoJSON
          key={stateBoundaryKey}
          data={stateBoundaries}
          style={{
            color: "#bae6fd",
            weight: 2.8,
            opacity: 0.96,
            fillOpacity: 0
          }}
          onEachFeature={(feature: AdminBoundaryFeature, layer: Layer) => {
            const properties = feature.properties ?? {};
            layer.bindPopup(renderBoundaryPopup("State Boundary", properties));
          }}
        />
      ) : null}
      {layers.dams ? mappedDams.map((dam) => (
        <CircleMarker
          key={dam.dam_id}
          center={[dam.latitude as number, dam.longitude as number]}
          radius={dam.dam_id === selectedDamId ? 12 : 8}
          pathOptions={{
            color: "#0f172a",
            weight: dam.dam_id === selectedDamId ? 3 : 1,
            fillColor: riskColor[dam.risk_class],
            fillOpacity: 0.86
          }}
          eventHandlers={{ click: () => onSelect(dam) }}
        >
          <Popup>
            <strong>{dam.dam_name}</strong>
            <span>{dam.dam_id}</span>
            <span>{dam.state}</span>
          </Popup>
        </CircleMarker>
      )) : null}
      {showLabels ? mappedDams.map((dam) => (
        <Marker
          key={`${dam.dam_id}-label`}
          position={[dam.latitude as number, dam.longitude as number]}
          icon={labelIcon}
          interactive={false}
        >
          <Tooltip permanent direction="top" offset={[0, -8]} opacity={0.94} className="dam-name-label">
            {dam.dam_name}
          </Tooltip>
        </Marker>
      )) : null}
      <div className="map-layer-control">
        <strong>Layers</strong>
        <label><input type="checkbox" checked={layers.dams} onChange={() => toggleLayer(setLayers, "dams")} /> Dams</label>
        <label><input type="checkbox" checked={layers.reservoirs} onChange={() => toggleLayer(setLayers, "reservoirs")} /> Reservoirs <small>z{RESERVOIR_MIN_ZOOM}+</small></label>
        <label><input type="checkbox" checked={layers.stateBoundaries} onChange={() => toggleLayer(setLayers, "stateBoundaries")} /> State boundary</label>
        <label><input type="checkbox" checked={layers.districtBoundaries} onChange={() => toggleLayer(setLayers, "districtBoundaries")} /> District boundary</label>
        <label><input type="checkbox" checked={layers.labels} onChange={() => toggleLayer(setLayers, "labels")} /> Labels <small>z{LABEL_MIN_ZOOM}+</small></label>
      </div>
      <div className="map-zoom-status">Zoom {roundedZoom}</div>
      <div className="living-atlas-status">
        <strong>Living Atlas IN_Dams</strong>
        <span>{livingAtlasStatus}</span>
      </div>
      <div className="boundary-layer-status">
        <strong>Admin Boundaries</strong>
        <span>{boundaryStatus}</span>
      </div>
    </MapContainer>
  );
}

function MapInteractionController({
  dams,
  selectedDamId,
  stateFilter,
  stateBoundaries,
  districtBoundaries,
  onZoomChange
}: {
  dams: Dam[];
  selectedDamId?: string;
  stateFilter?: string;
  stateBoundaries: AdminBoundaryFeatureCollection | null;
  districtBoundaries: AdminBoundaryFeatureCollection | null;
  onZoomChange: (zoom: number) => void;
}) {
  const map = useMap();
  useMapEvents({
    zoomend: () => onZoomChange(map.getZoom())
  });

  useEffect(() => {
    onZoomChange(map.getZoom());
  }, [map, onZoomChange]);

  useEffect(() => {
    const selectedDam = dams.find((dam) => dam.dam_id === selectedDamId);
    if (selectedDam?.latitude && selectedDam.longitude) {
      map.flyTo([selectedDam.latitude, selectedDam.longitude], Math.max(map.getZoom(), 9), { duration: 0.8 });
    }
  }, [dams, map, selectedDamId]);

  useEffect(() => {
    const boundaryBounds = stateFilter
      ? boundsFromFeatures(stateBoundaries?.features.length ? stateBoundaries.features : districtBoundaries?.features)
      : null;
    const damBounds = boundsFromDams(dams);
    const targetBounds = boundaryBounds ?? damBounds;
    if (targetBounds?.isValid()) {
      if (stateFilter) {
        map.flyTo(targetBounds.getCenter(), RESERVOIR_MIN_ZOOM, { duration: 0.8 });
        window.setTimeout(() => onZoomChange(map.getZoom()), 900);
        return;
      }
      map.fitBounds(targetBounds, {
        animate: true,
        duration: 0.8,
        maxZoom: 6,
        padding: [28, 28]
      });
    }
  }, [dams, districtBoundaries, map, onZoomChange, stateBoundaries, stateFilter]);

  return null;
}

function MapZoomButtons() {
  const map = useMap();
  const zoom = (direction: 1 | -1, event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    if (direction === 1) {
      map.setZoom(map.getZoom() + 1);
    } else {
      map.setZoom(map.getZoom() - 1);
    }
  };
  return (
    <div className="map-zoom-buttons">
      <button type="button" aria-label="Zoom in" onMouseDown={(event) => event.stopPropagation()} onClick={(event) => zoom(1, event)}>+</button>
      <button type="button" aria-label="Zoom out" onMouseDown={(event) => event.stopPropagation()} onClick={(event) => zoom(-1, event)}>-</button>
    </div>
  );
}

const labelIcon = L.divIcon({
  className: "dam-label-anchor",
  html: "",
  iconSize: [0, 0]
});

function toggleLayer(setLayers: Dispatch<SetStateAction<LayerVisibility>>, key: keyof LayerVisibility) {
  setLayers((current) => ({ ...current, [key]: !current[key] }));
}

function boundsFromDams(dams: Dam[]) {
  const bounds = new LatLngBounds([]);
  dams.forEach((dam) => {
    if (dam.latitude && dam.longitude) {
      bounds.extend([dam.latitude, dam.longitude]);
    }
  });
  return bounds.isValid() ? bounds : null;
}

function boundsFromFeatures(features?: Feature<Geometry, Record<string, unknown>>[] | null) {
  if (!features?.length) return null;
  const bounds = new LatLngBounds([]);
  features.forEach((feature) => {
    try {
      const featureBounds = L.geoJSON(feature).getBounds();
      if (featureBounds.isValid()) bounds.extend(featureBounds);
    } catch {
      // Skip invalid geometries returned by remote services.
    }
  });
  return bounds.isValid() ? bounds : null;
}

function getStateCenter(state?: string): [number, number] {
  const centers: Record<string, [number, number]> = {
    "Andaman and Nicobar Islands": [11.7, 92.7],
    "Andhra Pradesh": [15.9, 80.3],
    "Arunachal Pradesh": [28.2, 94.7],
    Assam: [26.2, 92.9],
    Bihar: [25.9, 85.3],
    Chhattisgarh: [21.3, 82.0],
    Goa: [15.3, 74.1],
    Gujarat: [22.4, 71.7],
    "Himachal Pradesh": [31.9, 77.2],
    "Jammu and Kashmir": [33.7, 75.3],
    Jharkhand: [23.6, 85.3],
    Karnataka: [14.8, 75.7],
    Kerala: [10.4, 76.4],
    "Madhya Pradesh": [23.5, 78.5],
    Maharashtra: [19.7, 75.7],
    Manipur: [24.7, 93.9],
    Meghalaya: [25.5, 91.3],
    Odisha: [20.6, 84.4],
    Punjab: [31.0, 75.4],
    Rajasthan: [26.9, 74.2],
    Sikkim: [27.5, 88.5],
    "Tamil Nadu": [11.1, 78.7],
    Telangana: [17.9, 79.6],
    "Uttar Pradesh": [26.8, 80.9],
    Uttarakhand: [30.1, 79.1],
    "West Bengal": [23.7, 87.8]
  };
  return state && centers[state] ? centers[state] : [22.8, 78.8];
}

function buildLivingAtlasIdsUrl(where: string) {
  const params = new URLSearchParams({
    where,
    f: "pjson",
    returnIdsOnly: "true"
  });
  return `${LIVING_ATLAS_DAMS_URL}?${params.toString()}`;
}

function buildLivingAtlasFeaturesUrl(where: string, objectIds: number[]) {
  const params = new URLSearchParams({
    where,
    objectIds: objectIds.join(","),
    f: "geojson",
    returnGeometry: "true",
    geometryPrecision: "5",
    outFields: [
      "objectid",
      "uid",
      "state",
      "district",
      "pic",
      "name",
      "operated_maintain",
      "year_completion",
      "river_basin",
      "river",
      "dam_type",
      "height_lowest_level",
      "dam_length",
      "grosss_rage_capacity",
      "effective_storage_capacity"
    ].join(","),
    outSR: "4326"
  });
  return `${LIVING_ATLAS_DAMS_URL}?${params.toString()}`;
}

async function fetchAdminBoundaryLayer(url: string, where: string, outFields: string, signal: AbortSignal) {
  const idResponse = await fetch(buildAdminIdsUrl(url, where), { signal });
  if (!idResponse.ok) throw new Error(`Boundary ID request failed with ${idResponse.status}`);
  const idData = (await idResponse.json()) as { objectIds?: number[] };
  const objectIds = idData.objectIds ?? [];
  const features: AdminBoundaryFeature[] = [];
  let skipped = 0;
  const batches = [];
  for (let index = 0; index < objectIds.length; index += ADMIN_BOUNDARY_ID_BATCH_SIZE) {
    batches.push(objectIds.slice(index, index + ADMIN_BOUNDARY_ID_BATCH_SIZE));
  }
  for (let index = 0; index < batches.length; index += ADMIN_BOUNDARY_CONCURRENCY) {
    const chunk = batches.slice(index, index + ADMIN_BOUNDARY_CONCURRENCY);
    const collections = await Promise.all(
      chunk.map((ids) => fetchAdminFeatureBatch(url, outFields, ids, signal))
    );
    features.push(...collections.flatMap((collection) => collection.features));
    skipped += collections.reduce((total, collection) => total + collection.skipped, 0);
  }
  return { features, skipped };
}

async function fetchAdminFeatureBatch(
  url: string,
  outFields: string,
  objectIds: number[],
  signal: AbortSignal
): Promise<AdminBoundaryBatchResult> {
  try {
    const response = await fetch(buildAdminFeaturesUrl(url, outFields, objectIds), { signal });
    if (!response.ok) throw new Error(`Boundary feature request failed with ${response.status}`);
    const data = (await response.json()) as AdminBoundaryFeatureCollection;
    return { features: data.features ?? [], skipped: 0 };
  } catch (error) {
    if (objectIds.length === 1) {
      return { features: [], skipped: 1 };
    }
    const results = await Promise.all(objectIds.map((id) => fetchAdminFeatureBatch(url, outFields, [id], signal)));
    return {
      features: results.flatMap((result) => result.features),
      skipped: results.reduce((total, result) => total + result.skipped, 0)
    };
  }
}

function buildAdminIdsUrl(url: string, where: string) {
  const params = new URLSearchParams({
    where,
    f: "pjson",
    returnIdsOnly: "true"
  });
  return `${url}?${params.toString()}`;
}

function buildAdminFeaturesUrl(url: string, outFields: string, objectIds: number[]) {
  const params = new URLSearchParams({
    where: "1=1",
    objectIds: objectIds.join(","),
    f: "geojson",
    returnGeometry: "true",
    geometryPrecision: "5",
    outFields,
    outSR: "4326"
  });
  return `${url}?${params.toString()}`;
}

function renderLivingAtlasPopup(properties: LivingAtlasProperties) {
  const rows = [
    ["UID", properties.uid],
    ["PIC", properties.pic],
    ["State", properties.state],
    ["District", properties.district],
    ["River", properties.river],
    ["Basin", properties.river_basin],
    ["Dam type", properties.dam_type],
    ["Year", properties.year_completion],
    ["Height", formatMapNumber(properties.height_lowest_level, " m")],
    ["Length", formatMapNumber(properties.dam_length, " m")],
    ["Gross storage", formatMapNumber(properties.grosss_rage_capacity, " m3")],
    ["Effective storage", formatMapNumber(properties.effective_storage_capacity, " m3")]
  ].filter(([, value]) => value !== undefined && value !== null && value !== "");
  return `
    <section class="living-atlas-popup">
      <strong>${escapeHtml(properties.name ?? "Living Atlas dam")}</strong>
      ${rows.map(([label, value]) => `<span><b>${escapeHtml(String(label))}</b>${escapeHtml(String(value))}</span>`).join("")}
    </section>
  `;
}

function renderBoundaryPopup(title: string, properties: AdminBoundaryProperties) {
  const rows = [
    ["State", properties.state],
    ["District", properties.district],
    ["Country", properties.country]
  ].filter(([, value]) => value !== undefined && value !== null && value !== "");
  return `
    <section class="living-atlas-popup">
      <strong>${escapeHtml(title)}</strong>
      ${rows.map(([label, value]) => `<span><b>${escapeHtml(String(label))}</b>${escapeHtml(String(value))}</span>`).join("")}
    </section>
  `;
}

function formatMapNumber(value: number | undefined, suffix: string) {
  return typeof value === "number" && Number.isFinite(value) ? `${new Intl.NumberFormat("en-IN").format(value)}${suffix}` : undefined;
}

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;"
    };
    return entities[char];
  });
}
