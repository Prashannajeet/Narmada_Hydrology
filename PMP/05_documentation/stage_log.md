# PMP Atlas project stage log

| Stage | Status | Output | Validation |
|---|---|---|---|
| 00 Source registration | Complete | Two original PDFs copied into `00_source_documents` | Page counts and file sizes recorded |
| 01 Source assessment | Complete | `pmp_atlas_source_inventory.md` | Volume labels checked against covers; filenames are reversed |
| 02 Data model | Complete | `pmp_atlas_data_model.md`, `pmp_atlas_schema.sql` | Provenance, units, spatial and NITA fields defined |
| 03 Numeric ETL MVP | Complete | SQLite database in `01_database` | 1,165 station records; 3,495 extremes; 288 storms; 10 catchments; 40 grid points; 1,379 PMP rows |
| 04 NITA export layer | Complete | CSV, GeoJSON, and `nita_export_manifest.json` | Stable keys, UTF-8, EPSG:4326 exchange coordinates |
| 05 Query/map app | Complete | Streamlit app in `03_app` | Application startup tested locally |
| 05A Mohanpura flood-module layout alignment | Complete | NITA-style hero, scenario controls, three-column workspace, bordered cards and map/results hierarchy | Python syntax check passed; Streamlit endpoint returned HTTP 200 |
| 05B ArcGIS basemap integration | Complete | Esri World Topographic, World Imagery and Boundaries & Places layer stack | CartoDB dependency removed; LayerControl added |
| 05C Full-width branding and map workspace | Complete | Full-width NITA wordmark header and dedicated 760px map canvas | Map moved outside result columns; wide layout and ArcGIS layer switcher retained |
| 05D Responsive viewport layout | Complete | Compact header, viewport-constrained content shell, internal result scrolling, tablet/mobile breakpoints | Page chrome no longer expands as an uncontrolled long document |
| 05E Hydrology analysis workspace | Complete | Added station observed-extreme charts, regional storm-catalogue Gumbel screening, return-period curve, Gumbel parameters and DAD/PMP charts | Station annual-maxima frequency tables are not yet present; regional estimates are explicitly labelled screening-only |
| 05F Compact viewport density | Complete | Reduced shell, branding, hero, cards, tables, charts and map heights for single-viewport operation while retaining responsive breakpoints | Detailed records remain internally scrollable where necessary |
| 05G Analysis-map and footer layout | Complete | Placed station data table beside the ArcGIS map and moved project status, provenance and NITA handoff cards into a bottom footer row | Main workspace now prioritizes data-to-map comparison |
| 05H Mohanpura-style compact masthead | Complete | Replaced the oversized hero header with a thin tab line and compact white NITA AI report masthead modelled on the Mohanpura reference app | Header now uses a one-line title, report label and concise subtitle |
| 05I Tabbed hydrology workspace | Complete | Added separate Storm frequency & Gumbel, DAD/PMP curves and Station map tabs; narrowed scope rail, reduced table height and expanded map canvases | Hydrology analysis is now separated from the atlas explorer to reduce visual crowding |
| 05J Runtime compatibility repair | Complete | Removed Plotly Express import path that pulled NumPy-1.x compiled xarray/cftime modules; chart rendering now uses Plotly Graph Objects | Streamlit starts cleanly under the installed NumPy 2.0.2 environment |
| 05K Professional presentation theme | Complete | Reworked visual system with NITA AI navy/teal/lime palette, scientific dashboard cards, stronger typography, map/chart framing and responsive styling | Functionality and source-linked data retained while improving executive and technical presentation quality |
| 05L Filter rail and evidence canvas | Complete | Moved scenario/query controls into a collapsible sidebar and expanded station evidence table to 360px and map to 600px | Main workspace now prioritizes station records and geographic interpretation |
| 05M Evidence panel height alignment | Complete | Increased station extremes table from 360px to 600px to align with the map canvas and use the highlighted empty area | Table and map now occupy a balanced shared analysis band |
| 05N Context-sensitive table filters | Complete | Added sidebar filters for station name/district/type/rainfall, grid ID/area/PMP and storm centre/year/peak rainfall | Filtered station records also control the station map markers |
| 05O Main-window dashboard controls | Complete | Replaced sidebar filtering with a compact main-window workspace dock and Filter data popover; removed the left rail for a full-width evidence canvas | Dashboard now keeps controls discoverable without consuming the station/map workspace |
| 05P Map interaction controls | Complete | Collapsed ArcGIS layer switcher to the default layer icon and disabled wheel zoom propagation | Prevents rapid zoom/page movement; map zoom remains available through the controlled +/− buttons |
| 05Q Streamlit Community Cloud deployment | Complete | Public app at `https://narmada-pmp-atlas.streamlit.app/` from GitHub branch `pmp-atlas-live` | Cloud dependency installation completed and branded dashboard verified live; source PDFs remain excluded from the repository |
| 06 Map product extraction | Pending | `06_spatial_products` | Requires georeferencing and control-point QA |
| 07 Remaining table extraction | Pending | TD coefficients, ARFs, MAF and related tables | Requires merged-cell/footnote validation |
| 08 Model-input publication | Pending | Approved scenario packages in `07_model_inputs` | Requires hydrologist/model-owner review |
| 09 NITA workspace integration | Pending | Upload/API adapter configuration | Confirm authorized-workspace limits, MIME types, auth and persistence |

## Migration record

On 2026-10-16, the operational PMP artifacts were consolidated from the HMS workspace and the original `F:` source location into this project root. The original source PDFs were copied, not modified.

## Integrity rules

- Never edit files in `00_source_documents`.
- Re-run ETL only from `02_etl` and record the run in `08_runs`.
- Do not publish map-derived values as exact numeric observations without georeferencing and uncertainty metadata.
- Keep NITA-specific formats in `04_exports`; the canonical database remains independent of upload format.
