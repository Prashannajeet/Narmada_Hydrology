# UHC Subzone Ollama Lab

Independent local LLM test app for the existing UHC Subzone hydrology project.

## Run

Serve the `UHC_Subzone` root so this app can load the existing files under `outputs`:

```powershell
cd "D:\01 Project\Development\UHC_Subzone"
python -m http.server 8788
```

Open:

```text
http://127.0.0.1:8788/ollama_lab/
```

Use the `http://127.0.0.1:8788/ollama_lab/` URL, not `file:///.../index.html`, when asking Ollama questions. Browsers can block direct `file://` calls to the Ollama API.

## What It Uses

- `outputs/hms-narmada-model-data.js`
- `outputs/chambal-betwa-spatial-data.js`
- Existing UHC Subzone HTML tools under `outputs`
- Ollama API at `http://127.0.0.1:11434`

## Current Capabilities

- Select UHC project, basin map, HMS model, largest sub-basins, or a specific HMS sub-basin as the local LLM context.
- Use a native Narmada HMS + SUG brain panel instead of opening older linked pages.
- View a full-width Narmada HMS geometry map inside the same app.
- Use rainfall/PMP review context from reference `019f59c9-e4fe-7732-83d6-05e5022fff79`.
- Compute a browser-side design-flood screening scenario for the selected HMS sub-basin.
- Adjust rainfall depth, storm duration, areal reduction factor, loss rate, baseflow, storm centering, hydrograph shape, and time step.
- Push observed-event, 24-hour PMP, or 72-hour PMP reference rainfall into the scenario inputs.
- Draw a quick synthetic unit hydrograph proxy and report effective rainfall, peak flow, time to peak, and runoff volume.
- Send both the project context and computed scenario to Ollama for hydrology/GIS review.

## Absorbed Narmada SUG Module

The app now absorbs the Narmada HMS/SUG workflow directly into the Ollama lab:

- No internal cards or top navigation links open the older output pages.
- The Narmada HMS + SUG Brain ranks sub-basins by current scenario peak, area, unit peak, time to peak, slope, or name.
- Clicking a ranked sub-basin makes it the active design-flood target.
- The local LLM prompt includes the selected basin, filtered ranking sample, SUG coefficients, computed peak, rainfall/PMP reference, and known validation gaps.

## Full-Width Geometry Map

The app now renders local Narmada HMS geometry directly from `outputs/hms-narmada-model-data.js`:

- 51 sub-basin polygon geometries.
- Reach-link lines derived from HMS downstream link fields.
- HMS junction/site points.
- Layer toggles for basins, reaches, sites, and labels.
- Click any basin polygon to make it the active SUG and design-flood target.
- Geometry context is included in the Ollama prompt.

## Integrated Reference

The app now includes a compact summary from:

```text
C:\Users\Welcome\.codex\visualizations\2026\07\13\019f59c9-e4fe-7732-83d6-05e5022fff79
```

Included reference signals:

- Observed 06-09 Jul 2025 sub-basin rainfall range and top totals.
- PMP 24-hour, 48-hour, and 72-hour ARF scenario maxima.
- PMP hyetograph row count and closure QA.
- Accepted and rejected station counts for HMS event search.
- PMP zone counts for 104L, 104M, and 104U.

The app builds compact local context and sends it to the selected Ollama model for hydrology/GIS review. The screening calculation is for capability testing and engineering review support, not final statutory design.
