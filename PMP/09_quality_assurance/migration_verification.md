# Migration verification

Verified project root: `D:\01 Project\Development\PMP`

- Source PDFs are present under `00_source_documents`.
- SQLite database is present under `01_database`.
- ETL and app are present under `02_etl` and `03_app`.
- NITA exports are present under `04_exports`.
- Documentation and stage log are present under `05_documentation`.
- Spatial, model-input, run, and QA folders are present for subsequent stages.
- SQLite `PRAGMA integrity_check` returned `ok` before migration.
- Source PDF checksums are recorded in `00_source_documents/SHA256SUMS.txt`.
