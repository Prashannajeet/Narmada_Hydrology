# NITA AI Dam Registry Module

Production-grade module scaffold for the NITA AI Dam Safety Intelligence Platform.

## Stack

- Next.js frontend with Leaflet GIS map integration
- FastAPI backend with REST APIs
- PostgreSQL + PostGIS schema and spatial indexes
- JWT authentication and role-based access control
- Reservoir polygon upload through GeoJSON
- Audit logging for create, update, delete, upload, and document events
- Docker Compose deployment for frontend, backend, and PostGIS

## Core Tables

All domain tables use `dam_id` as the shared primary key or foreign key:

- `dams`
- `dam_engineering`
- `dam_reservoir`
- `dam_geometry`
- `dam_documents`

Supporting production tables:

- `users`
- `audit_log`

## Run

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

Frontend: http://localhost:13000  
Backend OpenAPI: http://localhost:18080/docs  
Streamlit Risk Register: http://localhost:18501  
PostGIS: localhost:5434

Demo login:

- Email: `admin@nita.ai`
- Password: `nita-admin`

## API Surface

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/dams`
- `POST /api/dams`
- `GET /api/dams/{dam_id}`
- `PATCH /api/dams/{dam_id}`
- `DELETE /api/dams/{dam_id}`
- `POST /api/dams/{dam_id}/reservoir-polygon`
- `POST /api/dams/{dam_id}/documents`
- `GET /api/analytics/dams`
- `GET /api/audit`

## NRLD Data Import

Official CWC National Register of Large Dams PDFs are kept under `data/`.

- `scripts/import_nrld_2019.py` extracts the cleaner NRLD 2019 table into `data/nrld_2019_import.sql`.
- `scripts/import_nrld_2023.py` extracts a 2023 reference import from `data/nrld-2023.pdf`; the 2023 PDF text is noisier, so use it as a refresh/parser reference until a cleaner official machine-readable source is available.
- Imported rows are tagged with `source_registry`, `source_record_id`, `source_publication_year`, and `source_url`.

To refresh the running PostGIS database:

```powershell
pip install -r requirements-import.txt
python scripts\import_nrld_2019.py
docker compose cp data\nrld_2019_import.sql db:/tmp/nrld_2019_import.sql
docker compose exec -T db psql -U nita_dam_user -d nita_dam_registry -f /tmp/nrld_2019_import.sql
```

## Integration Notes

The module is self-contained under `dam_registry_module` so it can be mounted into the existing NitageoAI WebGIS platform or deployed independently. Use the REST API as the integration boundary for other dam-safety services such as instrumentation telemetry, inspection workflows, breach modeling, satellite reservoir monitoring, and compliance reporting.

## Online Deployment

This repo includes a Render Blueprint at `render.yaml` for deploying:

- `nita-dam-risk-api` FastAPI backend
- `nita-dam-risk-register` Streamlit Risk Register app
- `nita-dam-risk-db` managed PostgreSQL database

The Render backend image runs the database bootstrap SQL on startup, then starts FastAPI. The Streamlit service points to the public backend URL.

Deployment steps:

1. Push this folder to a GitHub/GitLab/Bitbucket repository.
2. Open Render Blueprint deployment:
   `https://dashboard.render.com/blueprint/new`
3. Select the repository containing `render.yaml`.
4. Review the three resources and click **Apply**.
5. After deployment, open:
   `https://nita-dam-risk-register.onrender.com`

Demo login remains:

- Email: `admin@nita.ai`
- Password: `nita-admin`
