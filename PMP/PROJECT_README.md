# PMP Atlas Database and NITA GeoAI Project

## Operational root

`D:\01 Project\Development\PMP`

## Folder structure

- `00_source_documents` - original PMP Atlas PDFs and source checksums
- `01_database` - SQLite MVP database and future PostGIS deployment files
- `02_etl` - repeatable extraction and loading scripts
- `03_app` - Streamlit query and map application
- `04_exports` - NITA-compatible CSV, GeoJSON, and manifest outputs
- `05_documentation` - schema, data model, source inventory, conversion plan, and integration contract
- `06_spatial_products` - raw map pages and georeferenced/digitized products
- `07_model_inputs` - approved hydrology and inundation model inputs
- `08_runs` - ETL, QA, and modelling run logs
- `09_quality_assurance` - validation reports and rejected-record reports

## Run from this project root

```powershell
Set-Location 'D:\01 Project\Development\PMP'
python .\02_etl\etl.py
streamlit run .\03_app\app.py
```

## Stage status

See `05_documentation/stage_log.md`. Every stage records its purpose, inputs, outputs, validation, and remaining risks.
