# Narmada Hydrology Command Webmap - Streamlit Cloud App

Created: 2026-07-20 15:02

## Files

- `streamlit_app.py` - Streamlit entrypoint.
- `requirements.txt` - Python dependencies for Streamlit Cloud.
- `.streamlit/config.toml` - light theme configuration.
- `narmada-advanced-hydrology-analytics-webmap.html` - embedded Stage112 OpenLayers dashboard.

## Branding and layout

The dashboard is branded as `Nita AI & Geoanalytics` and embedded with `scrolling=False` for a non-scrollable cloud presentation window. The app uses a fixed-height full-width Streamlit component; if your deployed monitor is shorter than the default view, adjust `height=980` in `streamlit_app.py`.

## Local test

From this folder:

```bash
streamlit run streamlit_app.py
```

## Streamlit Community Cloud deployment

1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create a new app.
3. Select the repository, branch, and entrypoint file path:

```text
streamlit_cloud_app/streamlit_app.py
```

4. Keep `requirements.txt` in this same folder or in the repository root.
5. Deploy.

## Important model QA note

The embedded dashboard now reads corrected LS04G topology. `SB_Sub_54` is verified as:

```text
SB_Sub_54 -> R_Sub_14 -> R_R_26 -> R_R_9
```

The stale wrong route `SB_Sub_54 -> R_Sub_1` is documented only as a historical QA issue and is not used in this cloud dashboard.


## Google Flood API secrets

Google Flood Forecasting API access is currently limited to approved pilot
participants. After approval, create or reuse a Google Cloud API key, enable
the Flood Forecasting API in that Cloud project, then add secrets in Streamlit
Cloud:

```toml
[google_flood]
api_key = "YOUR_GOOGLE_FLOOD_API_KEY"
cloud_project_id = "YOUR_GOOGLE_CLOUD_PROJECT_ID"
base_url = "PASTE_OFFICIAL_GOOGLE_FLOOD_API_BASE_URL_AFTER_APPROVAL"
include_non_quality_verified = "true"
```

In Streamlit Cloud, open the app, go to `Settings` -> `Secrets`, paste the TOML
block, save, and reboot the app. Do not put the real key in GitHub or inside
`streamlit_app.py`.
