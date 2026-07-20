ÃƒÂ¯Ã‚Â»Ã‚Â¿# Narmada HMS Modelling Troubleshooting and Future Basin Reference

This is a living reference for the Narmada HMS model and for future river-basin HMS modelling systems. Update it whenever a modelling decision, data issue, fix, or calibration lesson is discovered.

## Current Model Philosophy

The Narmada model is being built in three branches:

1. Observed-event calibration branch: CWC Initial/Constant loss, Snyder/CWC transform, estimated baseflow, observed rainfall, observed discharge.
2. Comparison branch: SCS-CN loss with the same transform/rainfall/discharge calibration framework.
3. Design branch: CWC flood estimation formulas, PMP/design rainfall, reservoir routing scenarios, and dam-break/emergency references where available.

## Major Steps Completed So Far

1. Project setup: HEC-HMS 4.13 path confirmed, project folder created, workflow and lifecycle checklist prepared.
2. GIS setup: 51 reviewed HMS subbasins and 53 reaches identified; DEM terrain preprocessing performed with sink filling and hydrology derivatives.
3. Gauge and rainfall review: CWC/NCA station data checked, inside/outside basin split prepared, rainfall no-go high hourly values flagged, and gap-filled rainfall package created.
4. Initial model runs: Branch 1 active methods were computed with CWC Initial/Constant loss, Snyder transform, recession baseflow, and lag reach routing.
5. Discharge mismatch diagnosis: early simulated peaks were much higher than observed, indicating rainfall weighting, loss/baseflow, and missing reservoir routing all needed review.
6. Spatial rainfall and loss improvements: Thiessen/IDW rainfall weighting and HSG-guided loss sensitivity were prepared before increasing losses blindly.
7. Reservoir evidence collection: Indira Sagar, Tawa, Barna, Kolar, Bargi, Omkareshwar, and other reservoir AEC/rating sources were collected or recovered.
8. Kolar AEC QA: the O&M AEC table column ambiguity was resolved using NIH/EAP 2021 verification.

## Key Challenges and Fixes

### Rainfall Extremes

Problem: Hourly rainfall contained physically suspicious values above the selected no-go threshold.

Fix: Flag values above 150 mm/hr as no-go, avoid using them directly in HMS, and gap-fill missing/non-peak values only where physically reasonable.

Future-basin rule: Always review station time series before HMS import. A clean spatial rainfall field is better than a dense but contaminated field.

### Missing Subbasin-Hour Rainfall Cells

Problem: Rainfall package had missing subbasin-hour cells.

Fix: Interpolate from adjacent values only where not near peak rainfall and where nearby station behavior is consistent. Keep a provenance field for observed, temporal-filled, spatial-filled, and zero/assumed values.

Future-basin rule: Never hide gap filling. Keep the fill method visible in a QA table.

### Simulated Discharge Much Higher Than Observed

Problem: Initial simulated peaks exceeded observed peaks by several times at Barmanghat, Handia, Narmadapuram, and Sandia.

Likely causes:

- missing reservoir attenuation,
- rainfall spatial weighting issues,
- insufficient loss/infiltration in some soil zones,
- baseflow not represented or not separated from direct runoff,
- routing parameters too fast,
- event rainfall not representative for the contributing area.

Fix path:

1. Review rainfall weighting first.
2. Use HSG-guided spatial losses.
3. Add realistic baseflow.
4. Add reservoir AEC and outlet routing.
5. Calibrate losses and routing only after the physical controls are present.

### Baseflow

Problem: Baseflow was initially absent or underrepresented.

Fix: Use observed discharge recession and soil/HSG context to estimate baseflow. A 15-35 percent contribution can be plausible in some basins, but must be checked against recession behavior and event season.

Future-basin rule: Baseflow should be estimated from observed hydrographs, not inserted as a blanket percentage without checks.

### AEC Table Ambiguity

Problem: Kolar O&M printed an AEC table where area/capacity headings conflicted with known gross storage and submergence area.

Fix: Cross-check against NIH/EAP 2021 report. Correct HMS-ready interpretation is area about 22.7-24.44 Msqm and capacity about 265-325 MCM near FRL/MWL range.

Future-basin rule: Always cross-check AEC curves against:

- gross/live/dead storage,
- FRL/MWL/MDDL,
- submergence area,
- independent DPR/EAP/O&M reports,
- plotted elevation-storage shape.

### Reservoir Routing

Problem: Reservoirs were known but not yet active in the HMS basin branch.

Fix: Prepare AEC, outlet/rating, initial pool, and release-rule matrix before insertion. Use verified sources first and provisional seed curves only with QA labels.

Future-basin rule: Reservoir routing needs four parts: storage-elevation, outlet/release rating, initial pool, and operating rule/observed releases.

## Recommended Troubleshooting Sequence for Future Basins

1. Confirm basin boundary, DEM, streams, subbasins, and reaches.
2. Verify gauge/dam/rainfall point coordinates on a map.
3. Clean rainfall and discharge before HMS import.
4. Prepare a method branch using regional standards.
5. Run a simple baseline model.
6. Compare observed vs simulated peaks, timing, and volume.
7. Diagnose data problems before over-calibrating parameters.
8. Add baseflow and reservoir routing.
9. Calibrate losses, transform, routing, and reservoir releases separately.
10. Validate against an independent event.

## Current Next Stage

Stage 27 starts the reservoir AEC integration step. The immediate purpose is to move from "reservoir data collected" to "reservoir data actively controlling HMS routing".

## Stage 28 Note - Reservoir Branch Staging

The LS03B reservoir-AEC branch package was prepared as an import-ready staging package instead of directly editing HMS topology. This is intentional because several dam points have large snap distances from the derived stream/reach network. Forced reach replacement before visual QA can break routing topology.

Recommended rule for future basins: create storage/release/import tables first, confirm dam placement on map, then edit the HMS basin. Keep the previous pre-reservoir run as a comparison baseline.

## Stage 29 Note - Dam Re-Snapping QA

Large reservoir snap distances must be corrected before active HMS reservoir topology insertion. Stage 29 created individual maps for Kolar, Sukta, Dejla Dewda, Matiyari, and Bilgaon. Use these maps to manually choose the correct drainage/reach point, then update reservoir insertion coordinates before LS03B topology editing.

## Stage 30 Note - Corrected Dam Coordinates

Corrected coordinates were registered for Kolar, Sukta, Dejla Dewda, Matiyari, and Bilgaon. Corrected coordinates should be used before reservoir insertion into LS03B; maps and suggested nearest drainage/HMS reach distances are in Stage 30.

## Stage 31 Note - Updated Drainage Layer QA

The updated `Narmada_Drainage.zip` layer was checked as a reservoir placement reference. It is a WGS 84 line layer with 6,151 drainage features and about 24,155.704 km total mapped line length. After the revised Dejla Dewda coordinate, Kolar, Matiyari, Bilgaon, Dejla Dewda, and Sukta are all within about 1 km of the updated drainage and can move to visual confirmation before HMS reservoir insertion.

Future-basin rule: when DEM-derived HMS reaches do not pass near a known reservoir location, check an independent drainage layer before changing hydrologic parameters or forcing reservoir insertion. Use the best drainage evidence to correct topology first, then calibrate routing.

## Stage 32 Note - Final Reservoir Insertion and AEC Accuracy

Stage 32 created final reservoir snap points and an LS03B topology insertion package for Kolar, Matiyari, Bilgaon, Dejla Dewda, and Sukta using the updated drainage layer. All five are within about 1 km of the updated drainage reference and can proceed to visual confirmation before HMS topology editing.

AEC accuracy was split into two classes. High-confidence AEC reservoirs are Indira Sagar, Tawa, Barna, and Kolar because they are supported by user workbook, O&M/EAP, NIH/EAP, or other verified sources. Provisional AEC reservoirs are Bargi, Omkareshwar, Bilgaon, Dejla Dewda, Matiyari, and Sukta because they use recovered/app-calibrated seed curves. Use provisional AEC curves for attenuation sensitivity, but do not over-calibrate final loss/routing parameters from them until official AEC/outlet/release records are found.

Future-basin rule: separate "topology readiness" from "AEC confidence". A dam can be correctly snapped but still have provisional storage/rating data; this should be visible in every modelling report.

## Stage 33 Note - LS03B Branch Anchor Validation

Stage 33 created `Narmada_B1_LS03B_Reservoir_Topology_Draft` as a separate HMS basin branch and `LS03B_2023_Reservoir_Topology_Draft` as a comparable September 2023 run. The first compute attempt failed because the LS03A meteorologic model was still bound to the LS02 basin. The fix was to clone the meteorologic model as `Narmada_LS03B_2023_Gapfilled_Met` and set `Use Basin Model: Narmada_B1_LS03B_Reservoir_Topology_Draft`.

After the met binding fix, HMS computed the LS03B branch anchor successfully. Reservoir elements are not yet active; this branch is the validated container where Stage 32 reservoir elements should be inserted.

Future-basin rule: when cloning HMS basin branches, clone and rebind the meteorologic model too. A run can fail even when the basin is valid if the met model is locked to another basin.

## Stage 34 Note - Reservoir Insertion Edit Package

Stage 34 created the guarded HMS reservoir insertion edit package for `Narmada_B1_LS03B_Reservoir_Topology_Draft`. A before-edit backup was saved before any active reservoir insertion. The package identifies current upstream/downstream connectivity for Kolar, Matiyari, Bilgaon, Dejla Dewda, and Sukta and provides HMS GUI insertion steps.

Important topology note: Matiyari targets `R_R_22`, which currently receives `SB_Sub_32`, `R_Sub_7`, and `R_R_24`. Bilgaon targets `R_Sub_7`, which then drains into `R_R_22`. Therefore Bilgaon and Matiyari must be inserted with care so Bilgaon outflow continues through the Matiyari-controlled downstream path where appropriate.

Future-basin rule: do not insert reservoirs only by point distance. Always inspect the existing upstream elements and downstream receiving element for each target reach, especially when two reservoirs are in series or one target reach receives multiple upstream branches.

## Stage 35 Note - Reservoir Routing Data Entry Package

Stage 35 prepared storage curves, initial-pool scenarios, routing readiness, and missing-data requests for the five Stage 34 reservoirs. Kolar is ready for the first active level-pool routing test because it has high-confidence AEC plus verified O&M spillway/head-sluice ratings. The provisional monsoon screening initial pool for Kolar is 461.787 m and 260.0 MCM, unless an observed event pool level is supplied.

Bilgaon, Dejla Dewda, Matiyari, and Sukta have storage curves but no verified outlet/release data yet. They should be treated as sensitivity/provisional routing elements, not final calibration controls, until official outlet rating, gate operation, release hydrograph, or observed event pool records are added.

Future-basin rule: storage curves alone do not make reservoir routing reliable. At minimum, active routing needs storage-elevation, initial pool, and an outflow/release rule. Missing outflow data should be visible before calibration.

## Stage 36 Note - Tawa Data Verification

Tawa data were verified against O&M, EAP, hazard/inundation, and Stage 28 reservoir event sources. Tawa is richer than Kolar for active reservoir routing: 1,207 extracted rows were found for Tawa versus 542 for Kolar in the checked datasets. Tawa has verified AEC, 762 spillway rating rows, canal outlet data, operation rules, hazard/inundation references, a 2023 initial pool seed, and 8 observed 2023 release rows.

Use the O&M/user-confirmed 20,500 m3/s as the controlling Tawa spillway capacity reference. Do not use the unclear EAP 8,397 cusecs interpretation as spillway capacity; keep it only as a QA note.

Future-basin rule: when multiple reservoirs are candidates for first active routing, prioritize by both data completeness and downstream hydrograph impact. Tawa should be promoted ahead of Kolar for basin-scale Narmada calibration because it has richer routing data and stronger influence near Narmadapuram/Handia.

## Stage 37 Note - Reservoir Ranking Before Next Routing Stage

Stage 37 compared Barna, Bargi, Indira Sagar Project, and Maheshwar before moving to the next HMS routing stage. Tawa and Kolar were retained as references. The recommended ranking is Tawa, Barna, Indira Sagar, Kolar, Bargi, and Maheshwar.

The ranking uses both modelling impact and data readiness. Indira Sagar has the largest storage and verified user-workbook AEC, so it is a high-impact reservoir. However, its outlet/gate operating rule is still incomplete. Barna ranks above it for immediate routing readiness because the O&M, DMI dam-break, operation, AEC, and design/rating sources are stronger. Bargi has high basin importance and observed release rows, but its AEC/rating package remains provisional. Maheshwar should not be used as an active HMS reservoir until AEC, outlet/gate rating, event pool, and release data are collected.

Future-basin rule: do not rank reservoirs only by storage size. For active HMS routing, a smaller reservoir with verified AEC, rating, operation rules, and event pool can improve calibration more reliably than a larger reservoir with missing outlet controls.

## Stage 38 Note - Updated Drainage Re-Snap for Ranked Reservoirs

Stage 38 re-snapped the ranked reservoir list to the updated Narmada drainage layer before HMS topology editing. This resolved the earlier large snap-distance concern for most priority reservoirs. Updated distances are Tawa 0.185 km, Barna 0.491 km, Indira Sagar 1.040 km, Kolar 0.033 km, Bargi 0.237 km, and Maheshwar 0.954 km.

Tawa and Barna are now the first practical active-routing candidates because they have both strong data packages and acceptable updated-drainage placement. Indira Sagar is close enough for manual review, but its outlet/gate rule limitation should be documented before final calibration. Bargi is spatially acceptable but remains provisional because AEC/outlet data are weaker. Maheshwar should not be inserted into the active routing branch yet, even though the snap distance is acceptable, because storage, outlet, pool, and release data are missing.

Future-basin rule: a good snap distance is necessary but not sufficient. Active reservoir routing should pass three checks together: spatial snap, AEC/rating completeness, and event-specific pool/release evidence.

## Stage 39 Note - Tawa First Active Routing Package

Stage 39 prepared Tawa as the first LS03C active reservoir-routing candidate. The package contains 29 storage-curve rows, initial pool 355.090 m with storage 2027.407 MCM for the 2023 event, 7 observed release target rows, a 39-level rating envelope, and 762 gate-opening rating rows from the Tawa O&M spillway table.

For the first calibration test, observed releases should be used as the target or as a specified-release sensitivity where the HMS setup supports it. The all-13-gate rating envelope is useful for capacity checks and gate-operation scenarios, but it should not be used as an automatic outflow rule unless the gate-opening scenario is explicitly documented.

Future-basin rule: separate capacity from operation. A spillway rating table describes what the structure can pass; it does not by itself describe what the dam operator released during a flood event.

## Stage 40 Note - LS03C Tawa Branch Shell Validation

Stage 40 created a dedicated `Narmada_B1_LS03C_Tawa_Only` branch shell, a bound `Narmada_LS03C_2023_Tawa_Only_Met` meteorologic model, and the `LS03C_2023_Tawa_Only` run. This branch is intentionally a pre-insertion shell: it validates that the branch, met model, control, and run registration work before `R_TAWA` is inserted.

The first compute attempt failed because the temporary script used `OpenProject(project_file)` instead of the HMS 4.13 script syntax used elsewhere in this project. The fix was `OpenProject("Narmada_HMS", project_folder)` followed by `Compute("LS03C_2023_Tawa_Only")`. After this correction, HMS computed the LS03C shell successfully with runtime 00:02.

Future-basin rule: before editing a working HMS topology, clone the basin/met/run into a branch shell and compute it once. That confirms the failure surface is reservoir insertion itself, not a met-model binding or run-registration problem.
## Stage 44-46 Notes - Active Reservoir Routing Branches

Tawa insertion showed that HEC-HMS 4.13 is strict about storage-outflow paired-data units. The project source curves may remain metric in CSV, but the HMS `Storage-Outflow` table in `.pdata` and DSS should use `ACRE-FT` and `CFS`. `M3` and `1000 M3` were rejected for this table type. Paired-data rows must also be strictly increasing in both storage and discharge; flat/duplicate values need tiny documented epsilon adjustments for HMS acceptance.

Barna insertion showed two common branch-cloning pitfalls. First, a new reach must be inserted inside the basin element list, not after basin schematic/spatial properties. Second, a cloned meteorologic model must be rebound with `Use Basin Model: <new basin name>`. Reusing the previous met model caused HMS to reject the new run even though the rainfall gages were identical.

Routing interpretation: Tawa and Barna both work structurally, but downstream outlet peak reduction remains small. This is not a sign that the reservoirs failed; it shows that the dominant mismatch is still controlled by basin-wide runoff volume, rainfall weighting/losses, and missing high-impact mainstem storage such as Indira Sagar/Omkareshwar/Bargi.
## Stage 47 Note - ISP Mainstem Routing and AEC Range Failure

Indira Sagar Project insertion demonstrated a different class of HMS reservoir issue. The topology and paired-data table were accepted, but the first compute failed because computed storage in `R_ISP` exceeded the storage-outflow table range. This happened because the physical AEC curve ended at FRL/storage 9585.091 MCM while the model inflow volume remained extremely large.

The temporary fix was to add synthetic high-storage bounds to the Modified Puls table. These bounds are explicitly marked as HMS stability rows and are not physical AEC points. If a reservoir requires these rows to compute, the result should be treated as a sensitivity/calibration diagnostic, not a final regulated hydrograph.

Future-basin rule: for large mainstem reservoirs, static storage-outflow routing can be misleading when releases are controlled operationally. Prefer observed release hydrographs or gate-operation rules for calibration events. Use high-storage bounds only to diagnose volume and routing sensitivity, and document them prominently.
## Stage 49 Note - ISP Specified Release Mass-Balance Gate

Stage 49 tested whether Indira Sagar Project could be moved from the LS03E synthetic Modified Puls sensitivity into an observed/specified-release branch. The release package was created successfully, but the mass balance failed the physical-readiness check.

Key result: starting from 260.850 m / 8541.883 MCM, the verified ISP AEC provides only about 1043.208 MCM of available storage up to FRL 262.130 m / 9585.091 MCM. The current HMS inflow at `R_R_8` contributes about 39582.948 MCM during the 384-hour event, while the gap-filled observed release package releases about 16853.184 MCM. The remaining volume would push computed storage to about 31271.647 MCM, far beyond the verified AEC range.

Future-basin rule: observed releases are not a magic fix if the upstream inflow volume is unrealistic. Before using specified release as final physics, run a reservoir mass-balance check against AEC, initial pool, inflow volume, release volume, and observed water levels. If storage exceeds physical AEC by a large amount, calibrate rainfall/loss/baseflow/upstream topology first.
## Stage 50 Note - Upstream Volume Calibration Before Reservoir Fixes

Stage 50 showed that the `R_R_8` inflow problem is concentrated enough to calibrate systematically. The upstream area feeding ISP contains 35 subbasins and about 63,086.1 sq.km. Current upstream rainfall volume is about 50,306.8 MCM, while HMS inflow at `R_R_8` is about 39,582.9 MCM, giving an event runoff coefficient of about 0.787 at the ISP inflow point. The ISP release plus observed storage-gain target implies a coefficient closer to 0.352.

Future-basin rule: when reservoir routing looks impossible, calculate the target inflow from release plus observed storage change before changing reservoir tables. If the required correction is hundreds of millimeters over a large upstream area, prioritize rainfall weighting, loss model, and baseflow volume before modifying reservoir outlet curves.
## Stage 51 Note - Reverse Rainfall from Reservoir AEC

Stage 51 used a reservoir mass-balance reverse process to check rainfall plausibility. The control equation was target inflow = observed/gap-filled release volume + storage change from the ISP AEC and observed water levels. This gave a target of about 17,689.6 MCM, compared with current HMS inflow of about 39,582.9 MCM.

The reverse rainfall check found no upstream hourly cell above 150 mm/hr, but it found an event-total problem: the upstream mean rainfall was about 797.4 mm, while strict AEC-compatible reverse rainfall was about 356.4 mm. Therefore, for future basins, do not rely only on hourly intensity filters. Always check event-total volume against reservoir AEC and observed pool/release data where available.
## Stage 52 Note - Hourly vs Daily Rainfall QA

Stage 52 compared hourly rainfall summed to daily totals. The result did not indicate a simple hourly/daily unit-conversion mistake. Instead, the high event rainfall comes from sparse observed-hour coverage and spatial/temporal gap-fill accumulation. For `R_R_8`, observed-available hours explain about 331.2 mm of the 797.4 mm event total; about 466.3 mm is added through the filling process.

Future-basin rule: before using gap-filled hourly rainfall in HMS, aggregate it to daily totals and check observed-hour support. A subbasin can have no extreme hourly value but still become implausible when many missing hours are filled from nearby stations during a long event.
## Stage 53 Note - Daily-Controlled Hourly Gap-Fill

Stage 53 implemented a safer gap-fill correction: observed hourly values are preserved, while filled/interpolated hours are scaled to a daily reference derived from the ISP AEC reverse-rainfall check. This reduced `R_R_8` upstream event rainfall from about 797.4 mm to about 478.7 mm.

Future-basin rule: when correcting hourly rainfall, do not reduce measured observations simply to satisfy a basin outlet or reservoir mass balance. Keep observations as the lower bound, scale only missing/fill values, and flag days where observed rainfall itself exceeds the independent water-balance reference.
## Stage 54 Note - Upstream-Only Recalibration with Missing Rainfall Columns

Stage 54 showed a common branch-building issue: the HMS basin/met model may contain a subbasin that is not present in a revised rainfall package. `SB_Sub_54` existed in the LS03E basin/met setup, but the Stage 53 corrected rainfall table did not include an `SB_Sub_54` column. The first LS03F compute failed with HMS gage-data errors for `SB_Sub_54`.

The first fallback was to keep missing-rainfall subbasins on their previous valid P23 gap-filled gage. The corrected modelling decision is to map `SB_Subbasin_2` from the Stage 53 rainfall table to the HMS element `SB_Sub_54`, write the same ordinates to `/NARMADA/SB_Sub_54/PRECIP-INC/10SEP2023/1HOUR/LS03F_RAINQA/`, and bind `SB_Sub_54` to `P53_SB_SUB_54`. After this correction, LS03F computed successfully.

Future-basin rule: before running a rainfall-replacement branch, compare basin subbasin names, meteorologic-model gage references, gage-file entries, and rainfall-table columns. Missing revised-rainfall columns should be handled explicitly: preserve prior valid rainfall, assign documented neighbor rainfall, or remove/deactivate the element only if topology confirms it is not part of the active model.

## Issue: High Constant Loss Values in HSG-D Dominant Subbasins

Observed in Stage 55/56: 14 subbasins have calibrated constant loss >= 5.5 mm/hr while the soil audit shows the basin is HSG-D/dual-D dominated. These values should be treated as **effective calibrated loss**, not fully field-accurate ground percolation.

Recommended handling:

- Keep a lower physical infiltration/percolation band for HSG-D dominant areas.
- Put remaining mismatch into explicitly named calibration terms: rainfall bias/gap-fill uncertainty, depression storage, disconnected impervious area, reservoir accounting, or routing/storage uncertainty.
- Use Planet LULC to assign roughness priors, then perform clipped subbasin/reach-buffer zonal extraction before applying Manning values in HMS.
- For baseflow, follow HEC-HMS recession calibration using observed hydrograph recession limbs. Current 0.85-0.90 recession constants are closer to interflow/mixed shallow baseflow than slow groundwater.

Reference output: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_56_Planet_LULC_Manning_Baseflow_Audit\Stage56_Planet_LULC_Manning_Baseflow_Audit_Report.md`

## Issue: Lithology Report Use in Loss and Baseflow Calibration

The lithological profile supports zoned calibration, but it should not be used as a direct numeric HMS parameter table. The report identifies dominant basalt, fine black smectitic soils, alluvial/sandstone/limestone aquifers, fault-controlled drainage, and groundwater stress zones. Use this information to constrain loss/baseflow/routing priors, then verify with GIS layers and observed discharge.

Watch-outs:

- High constant losses in basalt/HSG-D areas should be documented as effective calibrated loss, not pure percolation.
- Alluvium, sandstone, and limestone zones may justify higher baseflow or transmission loss only after gauge recession confirmation.
- Soil-depth and soil-texture tables contain apparent inconsistencies; verify numeric areas from source GIS before importing values.

Reference output: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_57_Lithological_Profile_Audit\Stage57_Narmada_Lithological_Profile_HMS_Audit.md`

## Stage 67 Note - IMD NetCDF Verification of Rainfall Timing

Stage 67 checked the suspicious September 2023 rainfall dates against the independent IMD 0.25 degree observed daily NetCDF file `RF25_ind2023_rfp25.nc`. The active 51-feature HMS subbasin polygon layer was confirmed from the reviewed HMS source, and IMD daily values were extracted for 2023-09-13 to 2023-09-19 and 2023-09-21 to 2023-09-27.

The IMD dataset supports a real basin rainfall peak on 2023-09-16: the maximum IMD grid-cell value in the checked Narmada points was 380.565 mm, compared with the HMS adjusted daily subbasin maximum of 271.504 mm at `SB_Sub_27`. This means the 15-16 September daily event should not be rejected simply as an HMS rainfall magnitude error.

However, IMD does not support the later 23-24 September HMS rainfall pulse as strongly. On 2023-09-24, HMS has a 78.813 mm subbasin maximum while IMD grid-cell maximum is 39.341 mm in the extracted points. For future basins, verify both magnitude and timing against independent gridded observations before tuning loss rates to match a delayed gauge peak.

Future-basin rule: use an external daily gridded rainfall check before final calibration whenever hourly station/gap-filled data produces large HMS discharge mismatch. If daily observed gridded rainfall confirms the event magnitude, tune loss/baseflow/routing. If it does not, rebuild rainfall weighting and gap filling before touching hydrologic parameters.

## Stage 68 Note - Peak-Based Rainfall QA Against IMD

Stage 68 compared HMS daily-controlled rainfall peaks against IMD observed daily NetCDF extraction for each 51-feature HMS subbasin polygon. The result confirms that 2023-09-16 is a real observed rainfall event, but the HMS rainfall package over-concentrates rainfall in several subbasins and spreads too much filled rainfall into some dates/subbasins.

Priority rainfall correction cases are led by `SB_Sub_32`, `SB_Sub_1`, `SB_Sub_30`, `SB_Sub_5`, `SB_Sub_38`, `SB_Sub_33`, `SB_Sub_7`, `SB_Sub_11`, `SB_Sub_27`, `SB_Sub_36`, `SB_Sub_34`, `SB_Sub_37`, `SB_Sub_8`, and `SB_Sub_35`. These have HMS peak rainfall far above the IMD polygon mean peak and should be corrected before hydrologic loss/routing calibration is continued.

Future-basin rule: when observed discharge is much lower than HMS simulation, compare rainfall forcing against independent gridded daily rainfall before increasing losses. Preserve measured observations, but scale/reweight filled or interpolated rainfall using independent daily controls and station-support diagnostics.

## Stage 69 Note - Priority Subbasin Rainfall Comparison

Stage 69 checked the 14 priority subbasins requested for direct comparison of present HMS-used rainfall against IMD observed rainfall. The comparison used Stage 53 daily-controlled rainfall, Stage 61 cap75 hourly reference, and Stage 67 IMD polygon mean/max extraction.

All 14 priority subbasins remain above the IMD polygon mean peak by more than 2.3x. The strongest mismatches are `SB_Sub_32` at 7.639x peak ratio and 7.758x event-total ratio, `SB_Sub_1` at 4.816x peak ratio and 5.541x event-total ratio, and `SB_Sub_30` at 4.354x peak ratio and 4.634x event-total ratio.

Important nuance: this is not purely a filled-rainfall issue. The adjusted filled-used share ranges from about 5.6% in `SB_Sub_8` to about 64.2% in `SB_Sub_27`. Therefore, correction should compare station evidence, daily totals, and IMD envelope; do not simply remove all filled rainfall.

Future-basin rule: when priority subbasins show high HMS/IMD rainfall ratios, report both raw filled rainfall and adjusted filled-used rainfall. Raw filled values can exceed final used rainfall after scaling and should not be used directly as the modelled filled share.

## Stage 70 Note - IMD Priority Rainfall Cap Sensitivity

Stage 70 implemented the user's proposed correction: use IMD observed rainfall to attenuate abrupt HMS rainfall peaks. A separate rainfall-only HMS branch `LS03J_2023_IMDPriorityCap` was created on the `LS03I3` basin. The 14 priority subbasins were capped to IMD polygon/grid maximum on problem days, while other subbasins remained unchanged from Stage 61 cap75 rainfall.

This worked directionally: major gauge-element peaks fell by about 36-51% for Handia, Narmadapuram, Barmanghat, and Sandia. However, the simulated peaks remain above observed CWC peaks by about 2.5x to 5.2x. Therefore, the corrected rainfall branch improves the model but does not solve the mismatch alone.

Future-basin rule: use independent gridded rainfall as a sensitivity/QA cap for abrupt station-gap-filled rainfall peaks, but do not treat rainfall correction as a substitute for loss/baseflow/reservoir-routing calibration. If an IMD-capped branch remains several times above observed discharge, the remaining error is likely distributed across runoff partitioning, routing/storage, reservoir operation, and gauge-element mapping.

### Stage 73 Rainfall Diagnostic

LS03K tested whether oversized discharge peaks are rainfall-volume driven in the 14 high-peak subbasins. It should be used as a diagnostic rainfall branch, not yet as final calibration.

| Station | Observed | LS03K | LS03K/Obs |
|---|---:|---:|---:|
| Barmanghat | 3838.100 | 17094.884 | 4.454x |
| Handia | 12800.000 | 38083.566 | 2.975x |
| Narmadapuram | 14706.000 | 33011.506 | 2.245x |
| Sandia | 5595.000 | 19415.357 | 3.470x |

### Stage 75 Routing Diagnostic

LS03L tested whether synchronized 1-hour reach lag was causing unrealistic flood-wave stacking. Treat this as a routing sensitivity branch, not final calibrated routing. Further improvement should use surveyed/derived channel length, slope, Manning roughness, and reservoir release rules.

## Stage 79 LS03O Local Calibration Note

When a downstream gauge remains high after basin-wide rainfall and mainstem routing correction, isolate upstream contributors before increasing losses everywhere. Stage 79 created `LS03O_Local_Sandia_Barmanghat_Cal` as a local-only branch around the Stage 78 contributors. Barmanghat was retained as QA-only because its observed peak date does not align with the modeled storm pulse; this prevents incorrect parameter tuning to a likely mapping/event-window issue.


## Stage 83 - SB_Sub_54 Data Integrity Repair (2026-07-19 12:15)

- Confirmed `SB_Sub_2` and `SB_Sub_54` as separate active HMS IDs using the LS03O basin file and GIS geometry QA map where available.
- Marked `SB_Subbasin_2` as a legacy alias for canonical `SB_Sub_54`; it should remain only as source lineage for older CWC/SUG and UHC rows.
- Generated canonicalized CWC/SUG and UHC tables for `SB_Sub_54` in `Stage_83_SB_Sub54_Data_Integrity_Repair`.
- Recomputed/QA-checked HSG zonal fractions for `SB_Sub_54` from the Global HSG 250 m raster.
- Verified `P73_SB_SUB_54` rainfall against IMD/daily comparison tables and local neighbour subbasins.

Status: completed_with_rainfall_and_alias_QA.


### Stage 84 - LS03P SB_Sub_54 Canonical IMD Redistribution

- [x] Created `LS03P_SB54_Canonical_IMDRedistribution` branch from LS03O.
- [x] Promoted Stage83 canonical `SB_Sub_54` alias/CWC/UHC/HSG repair package into the branch audit folder.
- [x] Created `P84_SB_SUB_54` rainfall gage and corrected only SB_Sub_54 daily rainfall using IMD daily targets where available.
- [ ] Compute LS03P and compare against LS03O at SB_Sub_54, Sandia, Barmanghat, Handia, Narmadapuram, and ISP before further loss tuning.


### Stage 85 - LS03Q SB_Sub_54 Sub-Daily Smoothing

- [x] Created `LS03Q_SB54_SubdailySmoothed` branch from LS03P.
- [x] Preserved LS03P daily rainfall totals for `SB_Sub_54`.
- [x] Smoothed only `SB_Sub_54` hourly shape using local-neighbour timing, 3-hour smoothing, and 20 mm/hr ceiling.
- [ ] Compute and compare LS03Q against LS03P before any further loss/baseflow tuning.

### Stage 85 - LS03Q SB_Sub_54 Sub-Daily Smoothing Completed

- [x] DSS write completed for `P85_SB_SUB_54`.
- [x] HMS run `LS03Q_SB54_SubdailySmoothed` computed successfully.
- [x] Results compared against LS03P in `04_Calibration_Validation\Stage_85_LS03Q_SB54_Subdaily_Smoothing\Stage85_LS03Q_Result_Comparison_Report.md`.
- [x] Rainfall total preserved at `457.884` mm and hourly cap held at `20.000` mm/hr.


### Stage 86 - LS03R SB_Sub_54 Pattern-Selected Rainfall

- [x] Created `LS03R_SB54_PatternSelectedRainfall` branch from LS03P.
- [x] Preserved accepted daily rainfall total for `SB_Sub_54`: `457.884` mm.
- [x] Replaced simple smoothing with reliability-screened neighbor temporal-pattern selection and 18 mm/hr cap.
- [ ] Compute and compare LS03R against LS03P and LS03Q before loss/baseflow tuning.

### Stage 86 - LS03R SB_Sub_54 Pattern-Selected Rainfall Completed

- [x] DSS write, HMS compute, and result extraction completed for `LS03R_SB54_PatternSelectedRainfall`.
- [x] Rainfall total preserved at `457.884` mm with max hour `18.000` mm/hr.
- [x] `SB_Sub_54` peak changed `-31.59%` vs LS03P and `-14.07%` vs LS03Q.
- [x] Result report: `04_Calibration_Validation\Stage_86_LS03R_SB54_Pattern_Selected_Rainfall\Stage86_LS03R_Result_Comparison_Report.md`.


### Stage 87 - LS03S Multi-Contributor Pattern Rainfall

- [x] Created `LS03S_MultiContributorPatternRainfall` branch from LS03P.
- [x] Applied pattern-selected rainfall to `SB_Sub_23, SB_Sub_33, SB_Sub_54, SB_Sub_6, SB_Sub_13`.
- [x] Preserved target-group accepted daily rainfall totals: `2189.679` mm summed across target subbasins.
- [ ] Write DSS, compute HMS, and compare against LS03P/LS03R before loss/baseflow tuning.

### Stage 87 - LS03S Multi-Contributor Pattern Rainfall Completed

- [x] DSS write, HMS compute, and result extraction completed for `LS03S_MultiContributorPatternRainfall`.
- [x] Compared LS03S against LS03P and LS03R.
- [x] `R_R_17` peak change: `-24.58%` vs LS03P and `-19.97%` vs LS03R.
- [x] `R_R_20` peak change: `-26.92%` vs LS03P and `-21.06%` vs LS03R.
- [x] Result report: `04_Calibration_Validation\Stage_87_LS03S_MultiContributor_Pattern_Rainfall\Stage87_LS03S_Result_Comparison_Report.md`.


### Stage 88 - LS03T Upstream Priority Pattern Rainfall

- [x] Created `LS03T_UpstreamPriorityPatternRainfall` branch from LS03S.
- [x] Applied pattern-selected rainfall to Stage69 priority upstream subbasins.
- [x] Preserved target-group accepted daily rainfall totals: `3256.467` mm summed across target subbasins.
- [ ] Write DSS, compute HMS, and compare against LS03P/LS03S before loss/baseflow tuning.

### Stage 88 - LS03T Upstream Priority Pattern Rainfall Completed

- [x] DSS write, HMS compute, and result extraction completed for `LS03T_UpstreamPriorityPatternRainfall`.
- [x] Compared LS03T against LS03P and LS03S.
- [x] `R_ISP` peak change: `-7.30%` vs LS03P and `-4.92%` vs LS03S.
- [x] Outlet peak change: `-4.02%` vs LS03P and `-2.82%` vs LS03S.
- [x] Result report: `04_Calibration_Validation\Stage_88_LS03T_UpstreamPriority_Pattern_Rainfall\Stage88_LS03T_Result_Comparison_Report.md`.


### Stage 89 - LS03U SB_Sub_27 Source Shape Isolation

- [x] Created `LS03U_SB27_SourceShapeIsolation` branch from LS03T.
- [x] Reverted only `SB_Sub_27` rainfall to accepted source hourly shape through `P89_SB_SUB_27`.
- [ ] Write DSS, compute, summarize, and compare against LS03T to determine whether SB_Sub_27 timing correction should be accepted or rejected.


### Stage 89 - LS03U Result Completed

- [x] DSS write, HMS compute, and result extraction completed for `LS03U_SB27_SourceShapeIsolation`.
- [x] `SB_Sub_27` peak change versus LS03T: `-20.67%`.
- [x] `R_ISP` peak change versus LS03T: `0.00%`.
- [x] Outlet peak change versus LS03T: `0.56%`.
- [x] Result report: `04_Calibration_Validation\Stage_89_LS03U_SB27_SourceShape_Isolation\Stage89_LS03U_SB27_SourceShape_Isolation_Result_Report.md`.


### Stage 91 - LS03V Downstream Attenuation Sensitivity

- [x] Created `LS03V1`, `LS03V2`, and `LS03V3` downstream attenuation branches from LS03U.
- [x] Rainfall, losses, transform, baseflow, and reservoir storage-outflow tables retained unchanged.
- [ ] Compute all variants, summarize, and compare outlet response before editing losses or reservoir curves.


### Stage 91 - LS03V Result Completed

- [x] Computed and summarized `LS03V1`, `LS03V2`, and `LS03V3`.
- [x] Compared downstream attenuation response against LS03U.
- [x] Result report: `04_Calibration_Validation\Stage_91_LS03V_Downstream_Attenuation_Sensitivity\Stage91_LS03V_Downstream_Attenuation_Result_Report.md`.


### Stage 93 - LS04A Canonical Rebuild Seed

- [x] Created `LS04A_Canonical_Rebuild_Seed` from `Narmada_B1_LS03I3_Tp175_Cp070`.
- [x] Bound to cloned LS03K meteorology with all subbasins using `P73` rainfall gages.
- [x] No `P87`, `P88`, or `P89` experimental rainfall patterns carried forward.
- [ ] Compute, summarize, and treat LS04A as the new clean baseline before reapplying any later correction.


### Stage 94 - LS04B All-51 IMD Daily Controlled Rainfall

- [x] Built all-51 IMD daily controlled hourly rainfall product.
- [x] Created `LS04B_All51_IMD_Daily_Controlled_Rainfall` from LS04A with basin parameters unchanged.
- [x] Added `P94_*` precipitation gages for all 51 subbasins.
- [ ] Write DSS, compute, summarize, and compare against LS04A/LS03U.

## Stage 101 Troubleshooting Note - Corridor Accumulation Before Calibration

When a mainstem gauge is over-predicted, first separate direct lateral subbasin inflow from already-accumulated upstream reach packages. In this case, `R_R_13` and `R_R_11` remain high after the `SB_Sub_54` topology repair because large upstream packages enter through `R_R_14`, `R_R_23`, `R_R_12`, and `R_Sub_18`.

Do not apply bias correction or blanket loss increases at Handia/Narmadapuram until:

- observed gauge coordinates are matched against candidate HMS reaches,
- `R_R_23` and `R_Sub_18` upstream hydrograph timing is reviewed,
- direct lateral subbasins `SB_Sub_41`, `SB_Sub_43`, and small-but-flagged `SB_Sub_42` are checked against rainfall, CN/HSG, and baseflow diagnostics.

Reference output: `04_Calibration_Validation\Stage_101_Handia_Narmadapuram_Corridor_Contributor_Audit`.

## Stage 102 Troubleshooting Note - Gauge Mapping Before Bias Correction

For over-predicted mainstem gauges, compare observed peaks against neighboring candidate HMS reaches before applying bias correction. In LS04C, `Narmadapuram` improves from current `R_R_13` to candidate `R_R_14`, while `Handia` improves from current `R_R_11` to `R_R_12` but remains too high.

This means:

- `Narmadapuram` likely has a station-to-reach mapping issue that can materially affect reporting.
- `Handia` still needs corridor inflow/timing review even after candidate mapping.
- bias correction should remain blocked until gauge placement is verified spatially.

Reference output: `04_Calibration_Validation\Stage_102_LS04D_Gauge_Mapping_Diagnostic`.

## Stage 103 Troubleshooting Note - Peak Match Can Conflict With Spatial Match

For `Narmadapuram`, Stage102 showed `R_R_14` has the better peak ratio, but Stage103 spatial verification found the gauge point is nearest to `R_R_13` at about `0.37 km`; `R_R_14` is about `6.47 km` away. Therefore, do not accept `R_R_14` as the calibration/reporting reach only because the peak matches better.

Use this rule for future basins: peak-ratio candidate mapping must be confirmed against station coordinates and reach geometry. If spatial and peak-match evidence conflict, preserve the spatial mapping and investigate rainfall/loss/baseflow/routing/attenuation unless the gauge coordinate or reach naming is proven wrong.

Reference output: `04_Calibration_Validation\Stage_103_Narmadapuram_Spatial_Gauge_Reach_Check`.

## Stage 104 Troubleshooting Note - Synchronous Inflow Can Masquerade As Gauge Error

After Stage103 confirmed that Narmadapuram is spatially closest to `R_R_13`, Stage104 checked the hydrograph mechanics. At the `R_R_13` peak hour, the direct upstream inflows nearly equal the outflow: `R_R_14` contributes about `14,702` cumec, `R_R_23` contributes about `5,829` cumec, and `SB_Sub_41` contributes about `1,524` cumec; the direct inflow sum is about `22,055` cumec against `R_R_13` peak `22,053` cumec.

This means `R_R_13` is not the source of unexplained volume. The practical problem is synchronized inflow and weak attenuation, with active reach routing set to `Lag = 1.000 hr` through this corridor. For future basin models, if a reach peak equals the same-hour sum of direct inflows, do not immediately increase losses or remap gauges. First test reach lag/Muskingum attenuation and upstream hydrograph timing.

Reference output: `04_Calibration_Validation\Stage_104_RR13_Hydrograph_Generation_Attenuation_Check`.

## Stage 105 Troubleshooting Note - Bounded Routing Exit Criterion

Stage105 was created to avoid looping after Stage104. The only allowed change was reach routing in the Narmadapuram-Handia corridor. No rainfall, loss, baseflow, Snyder transform, or reservoir parameters were changed.

The best tested branch by four-gauge log-error score was `LS04E3`. Use this rule in future basin models: once a bounded routing-only branch is tested, either adopt the materially improved branch or document the residual mismatch as a launch limitation. Do not continue cycling through rainfall/loss/baseflow tuning unless a new independent data issue is proven.

Reference output: `04_Calibration_Validation\Stage_105_LS04E_Corridor_Attenuation_Exit_Branch`.

## Stage 106 Troubleshooting Note - Public Launch Branch Point

Stage106 is the stop point for pre-launch tuning. The public launch branch is `LS04C_SB54_Topology_QA`. `LS04E3_Corridor_Muskingum_Strong` is kept as evidence that corridor routing attenuation was tested, but it is not promoted because the improvement was modest and outlet peak increased slightly.

Future data/model improvement must resume from `04_Calibration_Validation\Stage_106_Public_Launch_Branch_Point_Version`, not from an ad hoc later state. This avoids restarting the same tuning loop.

## Stage 107 Troubleshooting Note - Launch And Improvement Tracks Are Separate

Stage107 separates public launch reporting from future model improvement. The launch branch is `LS04C_SB54_Topology_QA`. Future revisions must resume from Stage106 rather than changing the launch package directly.

## Stage 108 Troubleshooting Note - Decompose Upstream Packages Before Downstream Tuning

When a downstream gauge remains high, decompose the upstream reach package first. Stage108 does this for `R_R_23`, one of the main contributors into `R_R_13`. Future corrections should target dominant contributors identified in Stage108 before changing Handia/Narmadapuram calibration parameters.

Reference output: `04_Calibration_Validation\Stage_108_RR23_Upstream_Contributor_Decomposition`.

## Stage109: SB_Sub_22 / R_Sub_22 Attenuation Diagnostic

Stage108 isolated `R_R_23` over-peak to direct same-hour inflow, dominated by `R_Sub_22` carrying `SB_Sub_22` runoff. Stage109 therefore creates `LS04F_SB22_RSub22_Attenuation` from the Stage106 launch branch point (`LS04C`) and changes only `R_Sub_22` routing from 1-hour Lag to Muskingum K=4.0 hr, x=0.15, steps=3. Active rainfall is kept unchanged because the LS04B/LS04C IMD daily-controlled rainfall for `SB_Sub_22` is already lower than the earlier source rainfall. This stage is intended to test travel-time/storage attenuation before any further rainfall or loss tuning.

## Stage110: LS04G Combined Attenuation Decision Point

`LS04G_Combined_SB22_Corridor_Attenuation` combines the Stage109 `R_Sub_22` local Muskingum routing with the LS04E3 corridor Muskingum routing while keeping rainfall, losses, transform, baseflow, topology, and reservoir tables unchanged. This avoids another parameter-tuning loop and isolates the effect of travel-time/storage routing.

Key results: `R_R_23` peak reduced from LS04C by -10.137 percent; Narmadapuram ratio improved from 1.861 to 1.791; Handia ratio improved from 2.781 to 2.548. Barmanghat and Sandia remain unchanged because the branch targets the `R_R_23 -> R_R_13 -> R_R_11` corridor. Keep LS04C as the public launch freeze unless the team accepts routing-only sensitivity promotion; retain LS04G as the best tested post-launch improvement candidate and return point for future refinement.

## Stage112: Advanced Hydrology Analytics Webmap

Stage112 creates the integrated command webmap requested for public demonstration and internal QA. It links HMS reviewed subbasins, active node connections, GD sites, rainfall stations, dams/reservoirs, snap QA, LS04G hydrographs, model parameter diagnostics, rainfall QA, HSG/CN/loss/baseflow fields, and reservoir ranking into one click-driven surface.

Use it to avoid future looped tuning: when Handia, Narmadapuram, ISP, or outlet peaks look wrong, first click the connected reach/gauge/subbasin/dam path and review topology, rainfall QA, loss/baseflow, snap distance, and hydrograph timing together before changing parameters. The webmap is a QA and communication layer; final parameter edits still need HMS/QGIS confirmation.

Reference output: `04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap`.

## Stage112 SB_Sub_54 Topology Correction Note

A critical QA issue was found in the Stage112 dashboard: the app was reading stale Stage98 topology where `SB_Sub_54 -> R_Sub_1`. This route is physically wrong because it moves a downstream/intermediate subbasin into the uppermost reach network.

The corrected HMS branch `Narmada_B1_LS04G_Combined_SB22_Corridor_Attenuation.basin` has the intended route: `SB_Sub_54 -> R_Sub_14 -> R_R_26 -> R_R_9`, with `SB_Sub_45 -> R_R_9`. The Stage112 dashboard builder now reads topology directly from the corrected HMS basin file, not the stale Stage98 CSV.

Rule for future basin projects: dashboard topology must be generated from the active HMS basin file used for the run, not from older exported topology CSVs. If a subbasin appears far outside its drainage position, first compare the visualization source against the active `.basin` file before changing hydrologic parameters.

Reference output: `04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap\stage112_sb54_topology_status.csv`.

## Stage113 Forecast Integration Note

Forecast integration must not bypass local HMS calibration. GEOGLOWS, GloFAS, and Google Flood forecasts should enter the workflow as external inflow/alert evidence, then be bias checked against observed CWC/reservoir inflow before reservoir routing decisions. GEOGLOWS is the quickest public API path; GloFAS requires Copernicus credentials and should be treated as an independent comparison source; Google Flood API requires pilot access and an API key.

Reference output: `04_Calibration_Validation\Stage_113_Forecast_API_Integration`.
