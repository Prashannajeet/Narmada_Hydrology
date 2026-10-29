# Source inventory

| source key | file | PDF pages | PDF page size | interpreted volume |
|---|---|---:|---|---|
| `narmada_pmp_maps_tables` | `F:\05 Knowledge\CWC\PMP\narmada-basin-volume-i.pdf` | 399 | A3 landscape | Volume II: Maps and Tables |
| `narmada_pmp_main_report` | `F:\05 Knowledge\CWC\PMP\narmada-basin-volume-ii.pdf` | 344 | A4 portrait | Volume I: Main Report |

## Extracted structure observed

### Volume I: Main Report

- Foreword, study area and climatology.
- Station table with catchment number, district, station, station type, latitude, longitude, data length, and highest 1/2/3-day rainfall with dates.
- Historical rainstorm catalogue and storm-centre/dew-point/precipitable-water information.
- Catchment-wise storm screening and DAD/PMP calculations.
- Grid point locations and assigned codes.
- Grid-wise 1/2/3-day contributing storm, grid rainfall depth, TAF, SPS, MMF and PMP estimates.
- 12/24/48/72-hour rainspell lists and smoothened time-distribution coefficients.
- Selected, envelope and average area-reduction factors.
- Station-wise return-period and point-PMP statistical estimates.

### Volume II: Maps and Tables

- Basin, station, climatology, topography and storm-centre maps.
- Storm isohyetal maps.
- Grid areal PMP maps for selected durations/areas.
- Return-period/PMP tables and maps.
- Depth-area-duration curves.
- Precipitable-water and MAF computation tables.

## Extraction risks

1. The user filenames are reversed relative to the cover labels: the file named `volume-i` contains the cover labelled Volume II, while `volume-ii` contains the cover labelled Volume I. Use the cover-derived `volume_label` in the database, not the filename alone.
2. Text extraction preserves many tables but can flatten multi-row headers, merged cells, footnotes and color-coded matrices. Table extraction requires header mapping and row-level validation.
3. Maps are embedded as page graphics. They must be retained as source page images and separately georeferenced/digitized with control points, CRS and uncertainty metadata.
4. Source coordinates are printed in degrees; each map layer needs independent CRS verification.
5. Method parameters and source values must be separated from derived online-model inputs.
