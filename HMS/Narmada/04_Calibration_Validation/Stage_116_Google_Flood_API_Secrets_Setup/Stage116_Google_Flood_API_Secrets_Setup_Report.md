# Stage116 Google Flood API Secrets Setup

Created: 2026-07-20 23:25

## Purpose

Stage116 prepares the Narmada Streamlit forecast app for Google Flood
Forecasting API credentials without hardcoding any secret value.

## What Changed

- Added a Streamlit secrets status panel under `Google Flood API`.
- Added safe reading from `st.secrets` first, then environment variables.
- Added `.streamlit/secrets.example.toml` as a template only.
- Updated the Streamlit Cloud README with exact secrets instructions.
- Refreshed the deployable Streamlit zip package.

## Required Secrets

```toml
[google_flood]
api_key = "YOUR_GOOGLE_FLOOD_API_KEY"
cloud_project_id = "YOUR_GOOGLE_CLOUD_PROJECT_ID"
base_url = "PASTE_OFFICIAL_GOOGLE_FLOOD_API_BASE_URL_AFTER_APPROVAL"
include_non_quality_verified = "true"
```

## Important Note

Google Flood Forecasting API access requires pilot approval, API key creation,
and enabling the Flood Forecasting API in the selected Google Cloud project. The
official endpoint/base URL should come from Google's approval material or
verification notebook; it has not been guessed in code.
