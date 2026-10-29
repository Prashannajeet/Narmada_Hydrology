# PMP Atlas live deployment

## Streamlit Community Cloud

- Repository: `Prashannajeet/Narmada_Hydrology`
- Main file: `PMP/03_app/app.py`
- Python dependencies: `PMP/requirements.txt`
- SQLite database: `PMP/01_database/pmp_atlas.sqlite`

The hosted app uses only the canonical SQLite database and exports committed
under `PMP/`. The source PDFs remain local and are intentionally excluded from
the deployment branch.

## Local validation

```powershell
python -m py_compile .\03_app\app.py
python -m streamlit run .\03_app\app.py --server.headless true --server.port 8507
```
