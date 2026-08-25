# Chambal and Betwa SUG + Map Dashboard Scope

## Development Focus

Proceed with Chambal and Betwa only before adding additional basins.

Excluded for this phase:
- Narmada changes except as a reference template.
- Other basin modules.
- `Deliverables/Geotagging` data.

Approved supporting data folders:
- `E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/01 Basin Wise`
- `E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/Deliverables/Task 3`
- `E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/Deliverables/Task 4`
- `E:/01 Projects/03 MPWRD/14 Digitial Atlas/01 Data/01 SHP/Deliverables/Task 5`

## Chambal Readiness

Chambal is ready for the first map-dashboard conversion.

Available basin-wise layers:
- `Sub Basin Chambal.shp`: 6 polygon records.
- `Drainage_Chambal.shp`: 4414 drainage line records.

Usable Chambal polygon names:
- Kuno
- Parbati
- Kalisindh
- Chambal Upper 1
- Chambal Upper 2
- Mej

Recommended Chambal next step:
1. Convert Chambal polygons and drainage to lightweight GeoJSON.
2. Filter GD sites, raingauge sites, and dam points from Task 3/5 by Chambal extent/polygon.
3. Add OpenLayers map panel to `chambal-hydrograph-app.html`.
4. Let polygon/site clicks populate the SUG input panel.
5. Keep report-derived SUG coefficients visible and editable.

## Betwa Readiness

Betwa is ready for basin-level mapping but not true sub-basin polygon selection.

Available basin-wise layers:
- `Sub Basin Betwa.shp`: 1 polygon record for Betwa.
- `Drainage_Betwa.shp`: 2610 drainage line records.

Task 5 provides useful Betwa GD sites. Sample records identified:
- Betwa
- Kurwai
- Neemkheda
- Kuakhedi

Recommended Betwa next step:
1. Convert Betwa basin polygon and drainage to lightweight GeoJSON.
2. Filter GD sites, raingauge sites, and dam points from Task 3/5 by Betwa polygon.
3. Add OpenLayers map panel to `betwa-hydrograph-app.html`.
4. Use site/project selection to populate the SUG input panel.
5. Flag that detailed Betwa sub-basin polygons are not yet available.

## Shared Implementation Direction

Create a common GIS preparation script that:
- Reads shapefile headers and DBF attributes.
- Converts WGS84 layers directly.
- Reprojects non-WGS84 layers only when needed.
- Uses the Betwa and Chambal basin boundary polygons as the authoritative filter.
- Applies a bounding-box prefilter first, then exact polygon containment.
- Keeps Task 3/4/5 point features only when the point falls inside the relevant basin polygon.
- Keeps line/polygon features only when their representative geometry/vertices intersect the basin polygon.
- Simplifies drainage and polygon geometry for browser use.
- Outputs browser-ready JS/GeoJSON files per basin.

Target browser layer groups:
- Basin/sub-basin polygons.
- Drainage.
- GD sites.
- Raingauge sites.
- Dam/project locations.
- Optional district/admin reference layer.

Filtering rule:
- Do not rely on basin-name attributes alone because statewide layers can contain mixed basin data.
- Do not include `Deliverables/Geotagging`.
- Do not include out-of-basin records from Task 3, Task 4, or Task 5.
- For this phase, prioritize WGS84 layers. Non-WGS84 layers should be added only after reprojection support is verified.

## Priority Order

1. Finish Chambal SUG + sub-basin map integration.
2. Finish Betwa SUG + basin/site map integration.
3. Validate both pages and sync to `D:/01 Project/Development/UHC_Subzone/outputs`.
4. Move to the next basin only after the above is stable.
