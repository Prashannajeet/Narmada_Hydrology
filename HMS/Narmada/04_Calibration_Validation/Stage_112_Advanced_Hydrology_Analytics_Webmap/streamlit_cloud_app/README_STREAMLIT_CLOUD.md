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
