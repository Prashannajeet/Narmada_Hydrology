# PMP Atlas database and app

## Build the database

From the project root:

```powershell
python .\02_etl\etl.py
python .\02_etl\comprehensive_atlas_etl.py
```

This reads the registered Volume I PDF, creates `01_database/pmp_atlas.sqlite`, and writes NITA-compatible exports under `04_exports/`.

## Run the app

```powershell
streamlit run .\03_app\app.py
```

The app provides station-extreme, station-climatology, source Gumbel return-period, DAD storm-evidence, grid-PMP, storm-catalogue, source-atlas, map, table, CSV-download, and NITA-export workspaces.

## Current extraction coverage

- 1,165 station records from Table 2-5, representing 694 source serial numbers across the atlas catchment systems;
- station 24/48/72-hour extreme rainfall records;
- historical rainstorm catalogue from Table 3-2;
- 10 atlas catchments;
- grid point locations from Table 3-35;
- grid-wise PMP estimates from Tables 3-42, 3-43 and 3-44;
- source page and provenance IDs for every extracted record.
- both volumes indexed at page level: 743 pages and 1,240 figure/table/map references;
- 375 raw extracted table payloads retained for audit and future query/RAG retrieval;
- 647 station climatology records from Table 1-1;
- 3,635 source DAD points from Tables 3-3 to 3-5;
- 37,110 station-wise Gumbel return-period records with EST, LL and UL rows from Tables 6-1 to 6-3.

Map plates, isohyetal contours, time-distribution curves, ARF curves, and MAF/precipitable-water tables are retained in the page/asset/raw-table layer and remain separate controlled digitization modules because their PDF layouts contain merged cells, graphics, color coding, or footnotes that should not be flattened without validation.
