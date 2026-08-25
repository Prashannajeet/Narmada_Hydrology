# NITA AI & GEOANALYTICS Hydrology Workspace

This folder contains the NITA AI & GEOANALYTICS (OPC) PVT LTD hydrology and geospatial decision-support workspace. It converts scanned CWC Flood Estimation Reports, HMS/spatial layers, rainfall inputs, basin boundaries, GD sites, drainage, and dam datasets into browser-based tools for unit hydrograph modelling, flood return-period screening, and dam/project planning.

## Company Positioning

NITA AI & GEOANALYTICS (OPC) PVT LTD works at the intersection of artificial intelligence, geospatial analytics, hydrology, and infrastructure planning. The platform vision is to turn complex engineering datasets into transparent, presentation-ready, and decision-oriented applications for water-resource agencies, dam planners, consultants, and basin managers.

## Applications

- `outputs/betwa-hydrograph-app.html` - Betwa subzone 1(c) synthetic unit hydrograph and design flood calculator.
- `outputs/lower-narmada-tapi-hydrograph-app.html` - Lower Narmada and Tapi subzone 3(b) calculator with bridge No. 485/4 defaults and report-derived Q25/Q50/Q100 formula comparison.
- `outputs/narmada-tapi-hydrograph-app.html` - Upper Narmada and Tapi subzone 3(c) calculator with Q25/Q50/Q100 report formula comparison.
- `outputs/hms-narmada-model-tool.html` - Narmada HMS model-development tool using `HMS.zip` sub-basins, reaches, junctions, and physiographic parameters.
- `outputs/hms-narmada-model-data.js` - Extracted HMS model attributes used by the model-development tool.
- `outputs/index.html` - Landing page linking both applications.

## Use

Open `outputs/index.html` in a browser, then select the required subzone app.

## Engineering Note

The source PDFs are scanned, so the applications are suitable for screening, workflow setup, and coefficient calibration. Before final DPR or statutory dam-safety use, verify all coefficients, rainfall maps, areal reduction factors, loss rates, base flow assumptions, routing, and applicable design-flood criteria against the original CWC report and current standards.

## Current Method Coverage

Included:

- Synthetic unit hydrograph rainfall-excess convolution.
- Return-period rainfall input for design flood hydrograph generation.
- Loss rate, areal reduction, base flow, and storm peaking controls.
- Flood formula comparison for the Lower/Upper Narmada and Tapi subzone apps.
- Visible report-data panels showing storm-event coverage status and SUG relationship parameters.
- HMS sub-basin/reach browsing and parameter handoff into the Upper/Lower Narmada SUG calculators.
- SUG parameter table for all retained Narmada HMS sub-basins.
- Basin-wise unit hydrograph and peak-flood screening table for each retained HMS sub-basin.
- OpenLayers map with clickable HMS sub-basin shapefile polygons, reach network, and HMS junction/site markers.

Not fully included yet:

- Complete digitized historical storm-event tables from scanned annexures.
- Complete observed UG/RUG-to-SUG calibration datasets.
- All plotted SUG relationship curves as editable data.
- Reservoir/channel routing, PMF, dam-break, and HFL/stage-discharge rating modules.
- Native HEC-HMS simulation execution, DSS output reading, meteorologic model control, and calibrated routing parameters.

## HMS Integration Notes

The current HMS integration reads the GIS/model-preparation layers from `HMS.zip`, including sub-basins, reaches, junctions, longest flowpaths, centroidal flowpaths, and the sub-basin characteristics workbook. It does not yet contain a complete runnable HEC-HMS `.hms` project with basin model, meteorologic model, control specifications, time-series gauges, and DSS output.

`Subbasin-2` is included in the active model dataset using a centroid calculated from `HMS/Sub Basin_HM_Narmada.shp`, because its workbook centroid coordinates were `0,0` and its workbook area attribute was blank/zero. The active model now contains 51 sub-basins.

For SUG handoff, the HMS model tool passes:

- `A` from polygon geometry area calculated directly from the sub-basin shapefile.
- `L` from longest flowpath length.
- `Lc` from centroidal flowpath length.
- `S` from longest flowpath slope converted to m/km.

The tool also displays the workbook area separately because the workbook `Area` field is much smaller than the geometry-derived basin polygon area for the available HMS dataset. The polygon geometry area is used for basin-scale flood estimation.

SUG parameters are computed for each retained sub-basin using report-region defaults:

- Lower/western candidate sub-basins: subzone 3(b), `Ct = 0.70`, `Cp = 2.10`.
- Upper/eastern candidate sub-basins: subzone 3(c), `Ct = 0.72`, `Cp = 2.05`.

The HMS model tool now also computes a selected-basin hydrograph chart and an all-sub-basin peak-flood table using the same synthetic unit hydrograph and rainfall-excess convolution method as the subzone calculators. Return period, Lower/Upper rainfall, areal reduction, phi-index loss, base flow intensity, and storm timing remain editable for screening.

The HMS map displays 51 sub-basin polygon boundaries extracted from `HMS/Sub Basin_HM_Narmada.shp` and 26 junction/site markers extracted from `HMS/Junctions.shp`. These are shown as HMS network/site points. Confirmed GD station metadata should be added as a separate layer when available.

These are development defaults and should be replaced with digitized report relationship equations and calibrated event parameters as the model matures.
