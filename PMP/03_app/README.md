# PMP Atlas database and app

## Build the database

From the project root:

```powershell
python .\02_etl\etl.py
```

This reads the registered Volume I PDF, creates `01_database/pmp_atlas.sqlite`, and writes NITA-compatible exports under `04_exports/`.

## Run the app

```powershell
streamlit run .\03_app\app.py
```

The app provides station-extreme, grid-PMP, storm-catalogue, map, table, CSV-download, and NITA-export views.

## Current extraction coverage

- 1,165 station records from Table 2-5, representing 694 source serial numbers across the atlas catchment systems;
- station 24/48/72-hour extreme rainfall records;
- historical rainstorm catalogue from Table 3-2;
- 10 atlas catchments;
- grid point locations from Table 3-35;
- grid-wise PMP estimates from Tables 3-42, 3-43 and 3-44;
- source page and provenance IDs for every extracted record.

Map plates, isohyetal contours, time-distribution coefficients, ARFs, and MAF tables remain separate controlled extraction modules because their PDF layouts contain merged cells, graphics, color coding, or footnotes that should not be flattened without validation.
