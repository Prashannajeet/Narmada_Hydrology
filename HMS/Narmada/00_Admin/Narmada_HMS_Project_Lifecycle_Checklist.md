# Narmada HMS Project Lifecycle Progress Checklist

Project folder:

`D:\01 Project\Development\HMS\Narmada`

Use this checklist as the permanent progress-monitoring reference for the Narmada HEC-HMS modelling lifecycle. Update the status column during every working session.

Status options:

- `Not Started`
- `In Progress`
- `Blocked`
- `Under Review`
- `Complete`
- `Rework Required`

## 1. Project Administration

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| ADM-01 | Confirm project objective and modelling scope | Complete | `00_Admin\Narmada_HMS_Development_Workflow.md`; `04_Calibration_Validation\Stage_06_Three_Branch_Modelling_Framework` | Scope confirmed: Narmada HMS with observed calibration, SCS-CN comparison, design/reservoir branch |
| ADM-02 | Confirm HEC-HMS version | Complete | `00_Admin\HEC_HMS_4_13_Setup_Reference.md` | HEC-HMS 4.13 |
| ADM-03 | Create project folder structure | Complete | Project root | Folder skeleton created |
| ADM-04 | Create workflow reference document | Complete | `00_Admin\Narmada_HMS_Development_Workflow.md`; `04_Calibration_Validation\Stage_27_Reservoir_AEC_Integration_and_Troubleshooting` | Permanent workflow reference |
| ADM-05 | Create progress checklist | Complete | `00_Admin\Narmada_HMS_Project_Lifecycle_Checklist.md` | This document |
| ADM-06 | Maintain data inventory | Complete | `00_Admin\data_inventory.csv` | Expanded project data inventory generated from current project files |
| ADM-07 | Record assumptions and modelling decisions | Complete | `04_Calibration_Validation\Stage_06_Three_Branch_Modelling_Framework`; `04_Calibration_Validation\Stage_27_Reservoir_AEC_Integration_and_Troubleshooting` | Three-branch modelling decision recorded |

## 2. Source Data Collection

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| DAT-01 | DEM source identified | Complete | `01_Raw_Data\DEM\DEM_SOURCE_REFERENCE.txt` | FABDEM source referenced |
| DAT-02 | Sub-basin shapefile extracted | Complete | `01_Raw_Data\SubBasins`; `02_GIS_Preprocessing\HMS_Reviewed_Source\Extracted\HMS\Sub Basin.shp` | Reviewed HMS source has 51 subbasins |
| DAT-03 | Rainfall data collected | Complete | `01_Raw_Data\Rainfall`; `03_HMS_Project\Narmada_Observed_Rainfall_2025.dss`; `04_Calibration_Validation\Stage_17_LS03A_Gapfilled_Rainfall` | Rainfall reviewed, cleaned, areal IDW package and DSS created |
| DAT-04 | Discharge/gauge data collected | Complete | `04_Calibration_Validation\Discharge_Gauge_Data_Review`; `03_HMS_Project\data\hms_import_package\observed_discharge_2025_07_06_09` | Observed discharge data reviewed and event package prepared |
| DAT-05 | Dam/reservoir inventory collected | Complete | `01_Raw_Data\Dams_Reservoirs\major_dams_in_narmada_basin_active.csv` | Major dam inventory selected for current Narmada model |
| DAT-06 | Elevation-storage curves collected | In Progress | `04_Calibration_Validation\Stage_14_Recovered_Reservoir_AEC`; `04_Calibration_Validation\Stage_19_Barna_DMI_DamBreak_Source`; `04_Calibration_Validation\Stage_24_Barna_OM_Manual_Source`; `04_Calibration_Validation\Stage_21_Tawa_EAP_Source`; `04_Calibration_Validation\Stage_22_Tawa_OM_Manual_Source`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source`; `04_Calibration_Validation\Stage_26_Kolar_NIH_AEC_Verification`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy` | Stage 32 AEC accuracy matrix created: high-confidence AEC for Indira Sagar, Tawa, Barna, Kolar; provisional seed AEC for Bargi, Omkareshwar, Bilgaon, Dejla Dewda, Matiyari, Sukta |
| DAT-07 | Elevation-discharge/outlet curves collected | In Progress | `04_Calibration_Validation\Stage_07_Branch1_Active_Methods\reservoir_required_data_register.csv`; `04_Calibration_Validation\Stage_19_Barna_DMI_DamBreak_Source`; `04_Calibration_Validation\Stage_21_Tawa_EAP_Source`; `04_Calibration_Validation\Stage_22_Tawa_OM_Manual_Source` | Outlet/elevation-discharge requirement register/template prepared; actual curves still needed |
| DAT-08 | Land use / land cover collected | In Progress | `04_Calibration_Validation\Stage_04_CN_SCS_Alternative` | Global CN raster product processed as SCS-CN alternative support; native LULC still useful for QA |
| DAT-09 | Soil / hydrologic soil group collected | Complete | `04_Calibration_Validation\Stage_12_Thiessen_HSG_LS02` | Global HSG 250 m raster zonal fractions computed for all 51 HMS subbasins |
| DAT-10 | Gauge and dam locations verified | In Progress | `02_GIS_Preprocessing\CWC_Data_Review`; `02_GIS_Preprocessing\Reservoir_Snapping_HMS_Reviewed`; `04_Calibration_Validation\Stage_29_Dam_Resnap_QA_Maps`; `04_Calibration_Validation\Stage_30_Corrected_Dam_Coordinates_Resnap` | Gauge coordinate review and dam snapping prepared; final HMS topology insertion pending |
| DAT-11 | CWC/NCA coordinate review completed | Complete | `02_GIS_Preprocessing\CWC_Data_Review` | 74 active station-dataset points retained for current basin; 18 outside-basin points separated for future extension |

## 3. GIS Preprocessing

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| GIS-01 | Confirm source projection | Complete | `02_GIS_Preprocessing\source_projection.prj` | Sub-basins are WGS84 |
| GIS-02 | Select project CRS for processing | Complete | `02_GIS_Preprocessing\source_projection.prj`; reviewed source UTM 44N layers | Processing CRS established from metre-based reviewed HMS source |
| GIS-03 | Reproject DEM and sub-basins | In Progress | `02_GIS_Preprocessing\DEM_Terrain`; `02_GIS_Preprocessing\HMS_Reviewed_Source` | DEM terrain and reviewed HMS layers exist; refined reprojection/clip QA remains |
| GIS-04 | Clip DEM to basin area | In Progress | `02_GIS_Preprocessing\DEM_Terrain`; `03_HMS_Project\terrain` | Terrain loaded/processed for HMS; final clipped/refined DEM QA remains |
| GIS-05 | Fill DEM sinks | Complete | `02_GIS_Preprocessing\DEM_Terrain\05_TauDEM_Products\narmada_fabdem_pit_removed.tif` | TauDEM pit removal completed |
| GIS-06 | Generate flow direction | Complete | `02_GIS_Preprocessing\DEM_Terrain\03_Hydrology` | SAGA flow direction generated from pit-removed DEM |
| GIS-07 | Generate flow accumulation | Complete | `02_GIS_Preprocessing\DEM_Terrain\03_Hydrology\narmada_flow_accumulation_cells.sgrd` | D8 cell-count accumulation generated |
| GIS-08 | Derive stream network | Under Review | `02_GIS_Preprocessing\DEM_Terrain\03_Hydrology\narmada_channel_network_acc10000.shp` | First-pass stream network exists and needs visual/topology review |
| GIS-09 | Snap outlets/gauges/dams | In Progress | `02_GIS_Preprocessing\Reservoir_Snapping_HMS_Reviewed`; `02_GIS_Preprocessing\CWC_Data_Review`; `04_Calibration_Validation\Stage_29_Dam_Resnap_QA_Maps`; `04_Calibration_Validation\Stage_30_Corrected_Dam_Coordinates_Resnap`; `04_Calibration_Validation\Stage_31_Updated_Drainage_Layer_QA`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy` | Final snap points prepared for Kolar, Matiyari, Bilgaon, Dejla Dewda, and Sukta using updated drainage; all are within about 1 km |
| GIS-10 | Derive reaches | Complete | `02_GIS_Preprocessing\HMS_Reviewed_Source\Extracted\HMS\Reach.shp`; `03_HMS_Project\Narmada_Basin_HMS_Reviewed_51Subbasins.basin` | Reviewed HMS basin includes 53 reach elements |
| GIS-11 | Compute sub-basin slopes and flow paths | Complete | `04_Calibration_Validation\Initial_HMS_Parameters\initial_subbasin_parameters_cwc_subzone.csv` | Subbasin length/slope-derived CWC/Snyder parameters computed |
| GIS-12 | Prepare HMS mapping table | Complete | `02_GIS_Preprocessing\subbasin_hms_mapping.csv` | Generated from supplied layer |

## 4. HMS Basin Model Setup

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| HMS-01 | Create HMS project shell | Complete | `03_HMS_Project\Narmada_HMS.hms` | Starter project created |
| HMS-02 | Create initial basin model | Complete | `03_HMS_Project\Narmada_Basin_Initial.basin` | 16 sub-basins generated |
| HMS-03 | Verify basin model opens in HEC-HMS | Complete | `03_HMS_Project\*.log`; computed HMS run outputs | HMS project has been computed successfully in HEC-HMS 4.13 |
| HMS-04 | Add river reaches | Complete | `03_HMS_Project\Narmada_Basin_HMS_Reviewed_51Subbasins.basin` | Reviewed 51-subbasin basin includes reach elements |
| HMS-05 | Add junctions and outlet review | Complete | `03_HMS_Project\Narmada_Basin_HMS_Reviewed_51Subbasins.basin` | Junctions/outlet topology present in reviewed HMS basin |
| HMS-06 | Add dam/reservoir elements | In Progress | `03_HMS_Project\Narmada_Reservoir_Insertion_Plan.csv`; `02_GIS_Preprocessing\Reservoir_Snapping_HMS_Reviewed` | Reservoir candidate/snap plan prepared; HMS reservoir elements not yet active |
| HMS-07 | Assign loss method | Complete | `03_HMS_Project\Narmada_B1_CWC_Start.basin` | Branch 1 loss activated: Initial+Constant for 51 subbasins |
| HMS-08 | Assign transform method | Complete | `03_HMS_Project\Narmada_B1_CWC_Start.basin`; `03_HMS_Project\B1_CWC_Observed_2025.log` | Branch 1 transform activated: Snyder for 51 subbasins; HMS-compatible Cp used |
| HMS-09 | Assign baseflow method | Complete | `03_HMS_Project\Narmada_B1_CWC_Start.basin` | Branch 1 estimated baseflow activated as Recession initial baseflow for 51 subbasins |
| HMS-10 | Assign reach routing method | Complete | `03_HMS_Project\Narmada_B1_CWC_Start.basin` | First-pass reach routing activated: Lag routing for 53 reaches |
| HMS-11 | Assign reservoir routing method | In Progress | `04_Calibration_Validation\Stage_15_LS03_Reservoir_Routing_Package`; `04_Calibration_Validation\Stage_18_LS03A_HMS_Met_Package`; `04_Calibration_Validation\Stage_27_Reservoir_AEC_Integration_and_Troubleshooting`; `04_Calibration_Validation\Stage_28_LS03B_Reservoir_AEC_Branch_Package`; `04_Calibration_Validation\Stage_31_Updated_Drainage_Layer_QA`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy`; `04_Calibration_Validation\Stage_33_LS03B_HMS_Branch_Anchor` | LS03B branch anchor and met-bound run validated in HMS; active reservoir element insertion remains pending |

## 5. Meteorology and Control Setup

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| MET-01 | Create placeholder meteorologic model | Complete | `03_HMS_Project\Narmada_Met_Placeholder.met` | Replace with real rainfall |
| MET-02 | Prepare rainfall time series | In Progress | `01_Raw_Data\Rainfall\NCA_Hourly_Rainfall_HMS_Strict_Event`; `03_HMS_Project\Narmada_Observed_Rainfall_2025.dss` | Observed rainfall time series prepared for HMS; LS03A 2023 gap-filled package prepared for reservoir-routing branch |
| MET-03 | Create rainfall gages or gridded precipitation | In Progress | `03_HMS_Project\Narmada_HMS.gage`; `03_HMS_Project\Narmada_LS03A_2023_Gapfilled_Rainfall.dss` | Rainfall gages created; LS03A 2023 gap-filled DSS/met package prepared pending reservoir-run QA |
| MET-04 | Assign rainfall to sub-basins | In Progress | `03_HMS_Project\Narmada_NCA_Strict_Areal_Met.met` | Rainfall gages assigned to all 51 subbasins; LS03A subbasin-hour rainfall prepared as gap-filled CSV pending DSS/met import |
| MET-05 | Create placeholder control specification | Complete | `03_HMS_Project\Narmada_Control_Placeholder.control`; `03_HMS_Project\Narmada_LS03A_2023_Reservoir_Event.control` | Placeholder plus September 2023 reservoir-event control prepared |
| MET-06 | Set calibration event control dates | Complete | `03_HMS_Project\Narmada_Initial_Event_2024.control`; observed event package 06-09 July 2025 | Calibration/control window selected for observed event workflow |

## 6. Dam and Reservoir Routing

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| DAM-01 | Create dam inventory | Complete | `01_Raw_Data\Dams_Reservoirs\major_dams_in_narmada_basin_active.csv` | Major dam inventory created |
| DAM-02 | Confirm priority dams for first model version | Complete | `01_Raw_Data\Dams_Reservoirs\Major_Dams_Narmada_Active_Set_Summary.md` | Priority major dams confirmed; Dahod excluded |
| DAM-03 | Collect storage-elevation tables | In Progress | `04_Calibration_Validation\Stage_14_Recovered_Reservoir_AEC\hms_reservoir_storage_curve_seed_long.csv`; `04_Calibration_Validation\Stage_19_Barna_DMI_DamBreak_Source\barna_dmi_elevation_volume_curve.csv`; `04_Calibration_Validation\Stage_24_Barna_OM_Manual_Source\barna_om_area_capacity_curve.csv`; `04_Calibration_Validation\Stage_21_Tawa_EAP_Source\tawa_eap_salient_features.csv`; `04_Calibration_Validation\Stage_22_Tawa_OM_Manual_Source\tawa_om_area_capacity_curve.csv`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source`; `04_Calibration_Validation\Stage_26_Kolar_NIH_AEC_Verification`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy` | AEC accuracy/readiness matrix created; verified sources prioritized and seed curves explicitly labelled provisional |
| DAM-04 | Collect discharge-elevation/release tables | In Progress | `04_Calibration_Validation\Stage_07_Branch1_Active_Methods\reservoir_elevation_discharge_collection_template.csv`; `04_Calibration_Validation\Stage_19_Barna_DMI_DamBreak_Source\barna_dmi_pmf_inflow_hydrograph.csv`; `04_Calibration_Validation\Stage_24_Barna_OM_Manual_Source\barna_om_spillway_gate_rating_cumec.csv`; `04_Calibration_Validation\Stage_21_Tawa_EAP_Source\tawa_eap_qa_flags.csv`; `04_Calibration_Validation\Stage_22_Tawa_OM_Manual_Source\tawa_om_spillway_single_gate_rating_cumec.csv`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source\kolar_om_spillway_gate_rating_cumec.csv`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source\kolar_om_head_sluice_rating_cumec.csv`; `04_Calibration_Validation\Stage_28_LS03B_Reservoir_AEC_Branch_Package` | Kolar O&M spillway and head-sluice rating tables captured; event-specific gate/pool logs still needed |
| DAM-05 | Define initial pool levels | In Progress | `04_Calibration_Validation\Stage_15_LS03_Reservoir_Routing_Package\reservoir_initial_pool_2023_09_10.csv`; `04_Calibration_Validation\Stage_28_LS03B_Reservoir_AEC_Branch_Package` | 2023 initial pool package promoted for LS03B; Kolar pool remains missing |
| DAM-06 | Add reservoir elements to HMS | In Progress | `03_HMS_Project\Narmada_B1_LS03B_Reservoir_Topology_Draft.basin`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy`; `04_Calibration_Validation\Stage_33_LS03B_HMS_Branch_Anchor`; `04_Calibration_Validation\Stage_34_Reservoir_Element_Insertion_Edit_Package` | Stage 34 reservoir insertion edit package and before-edit backup created; active HMS reservoir element insertion remains pending |
| DAM-07 | Configure reservoir routing | In Progress | `04_Calibration_Validation\Stage_20_Barna_Optimization_OperatingRules`; `04_Calibration_Validation\Stage_24_Barna_OM_Manual_Source`; `04_Calibration_Validation\Stage_21_Tawa_EAP_Source`; `04_Calibration_Validation\Stage_22_Tawa_OM_Manual_Source`; `04_Calibration_Validation\Stage_23_Tawa_EAP_Hazard_Inundation_Source`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source`; `04_Calibration_Validation\Stage_32_Final_Reservoir_Insertion_and_AEC_Accuracy`; `04_Calibration_Validation\Stage_35_Reservoir_Routing_Data_Entry_Package` | Kolar ready for first active level-pool routing test; Bilgaon, Dejla Dewda, Matiyari, and Sukta storage-ready but outlet/release data missing |
| DAM-08 | Verify reservoir inflow/outflow behavior | In Progress | `04_Calibration_Validation\Stage_23_Tawa_EAP_Hazard_Inundation_Source`; `05_Results`; `04_Calibration_Validation\Stage_28_LS03B_Reservoir_AEC_Branch_Package` | Next run should compare LS03B reservoir branch against LS03A pre-reservoir hydrographs |

## 7. Calibration and Validation

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| CAL-01 | Create calibration event register | Complete | `04_Calibration_Validation\calibration_event_register.csv` | Template created |
| CAL-02 | Select first calibration event | Complete | `03_HMS_Project\data\hms_import_package\observed_2025_07_06_09`; `04_Calibration_Validation\Discharge_Gauge_Data_Review` | Observed event selected for 06-09 July 2025 |
| CAL-03 | Run initial simulation | Complete | `03_HMS_Project\B1_CWC_Observed_2025.dss`; `04_Calibration_Validation\Stage_07_Branch1_Active_Methods` | Initial active-method Branch 1 simulation completed successfully |
| CAL-04 | Calibrate runoff volume | In Progress | `04_Calibration_Validation\Stage_12_Thiessen_HSG_LS02` | LS02 Thiessen rainfall + HSG-guided loss run reduced peaks further; reservoir routing and event/gauge calibration still required |
| CAL-05 | Calibrate peak timing | In Progress | `04_Calibration_Validation\Stage_06_Three_Branch_Modelling_Framework` | Use CWC/Snyder transform first, then routing calibration |
| CAL-06 | Calibrate baseflow/recession | In Progress | `04_Calibration_Validation\Stage_13_Reservoir_Baseflow_Calibration` | Observed daily discharge baseflow screening and current LS02 baseflow contribution prepared; hourly/longer recession data needed for final calibration |
| CAL-07 | Calibrate reservoir releases | In Progress | `04_Calibration_Validation\Stage_13_Reservoir_Baseflow_Calibration`; `04_Calibration_Validation\Stage_20_Barna_Optimization_OperatingRules`; `04_Calibration_Validation\Stage_24_Barna_OM_Manual_Source`; `04_Calibration_Validation\Stage_25_Kolar_OM_Manual_Source`; `04_Calibration_Validation\Stage_28_LS03B_Reservoir_AEC_Branch_Package` | Reservoir calibration package now has AEC, selected initial pools, and release/rating sources; event-specific gaps remain |
| CAL-08 | Validate against independent event | In Progress | `04_Calibration_Validation\Stage_07_Branch1_Active_Methods\independent_validation_event_register.csv` | Validation-event register prepared; independent event still to be selected |
| CAL-09 | Record performance statistics | In Progress | `04_Calibration_Validation\Stage_08_Branch1_Observed_Simulated_Comparison` | Branch 1 first-pass observed-vs-simulated peak and volume diagnostics generated; detailed hydrograph timing/NSE pending gauge-element insertion/export |

## 8. Scenario Modelling and Reporting

| ID | Task | Status | Evidence / File Location | Remarks |
|---|---|---|---|---|
| SCN-01 | Define scenario list | Complete | `05_Results\Scenario_Register\narmada_hms_scenario_register.csv` | Scenario register created for B1/B2/B3 and validation event |
| SCN-02 | Run historical flood scenario | Not Started | `05_Results` | After validation |
| SCN-03 | Run design storm scenario | In Progress | `04_Calibration_Validation\PMP_Atlas_Review`; `03_HMS_Project\data\hms_import_package\pmp_design_storms` | PMP/design rainfall inputs prepared; design branch not run |
| SCN-04 | Run dam operation scenario | Not Started | `05_Results` | Needs operation assumptions |
| SCN-05 | Compare scenario peak flows | Not Started | `05_Results` | Summary table |
| RPT-01 | Prepare interim setup report | Complete | `06_Reports\Narmada_HMS_Interim_Setup_Report.md`; `04_Calibration_Validation\Stage_27_Reservoir_AEC_Integration_and_Troubleshooting` | Troubleshooting and future-basin reference document created and should be maintained every session |
| RPT-02 | Prepare calibration report | Not Started | `06_Reports` | After calibration |
| RPT-03 | Prepare final model report | Not Started | `06_Reports` | After validation/scenarios |

## Latest Session Update

- Area-elevation-capacity data path explicitly added for reservoir storage curve preparation.
- Branch 1 active-method run is complete; next action is observed-vs-simulated gauge comparison.
- Reservoir routing remains open until storage/capacity curves, outlet curves, and event initial pool levels are collected.

## 9. Recurring Follow-Up Checklist

Use this at the start and end of every project session:

| Follow-Up Item | Status | Notes |
|---|---|---|
| Review latest checklist status | In Progress | Update this document |
| Add newly received data to inventory | Not Started | Update `data_inventory.csv` |
| Record data gaps/blockers | Not Started | Keep blockers visible |
| Save generated outputs in correct folder | In Progress | Do not mix raw and processed data |
| Note assumptions made during modelling | Not Started | Required for report |
| Back up changed HMS files | Not Started | Before major edits |
| Update next-session priorities | In Progress | Keep top 3 actions current |

## 10. Current Top 3 Next Actions

1. Insert `R_TAWA` in the validated LS03C branch shell using the Stage 39 storage, initial pool, observed release target, and rating-envelope package.
2. Rerun LS03C after Tawa insertion and compare with the no-reservoir LS03C shell/LS03B baseline.
3. After Tawa-only QA, add Barna next; keep Indira Sagar, Bargi, and Maheshwar limitations visible before treating them as final calibration controls.

## 11. Lifecycle Gate Summary

| Gate | Required Before Moving Forward | Current Status |
|---|---|---|
| Gate 1: Project initialized | Folder structure, workflow, inventory, checklist, HMS version reference | Complete |
| Gate 2: Source data ready | DEM, sub-basins, rainfall, discharge, dam data, land use, soil | In Progress; rainfall/discharge reviewed, CN raster alternative processed, dam operation data still pending |
| Gate 3: GIS preprocessing complete | Streams, reaches, slopes, flow paths, snapped outlets/dams | Not Started |
| Gate 4: HMS model build complete | Sub-basins, reaches, reservoirs, methods, meteorology, controls | In Progress; Branch 1 loss, transform, baseflow, and reach routing are active; reservoir routing still pending data |
| Gate 5: Calibration complete | Calibrated parameters and performance statistics | In Progress; Branch 1 run completed and now needs observed-vs-simulated performance statistics |
| Gate 6: Validation complete | Independent event validation | Not Started |
| Gate 7: Scenario/reporting complete | Scenario outputs and final report | Not Started |




- Stage 27 added reservoir AEC integration matrix and future-basin troubleshooting reference.

- Stage 28 created LS03B reservoir-AEC staging package for active reservoir routing preparation.

- Stage 29 created individual dam re-snap QA maps for large snap-distance reservoirs.


- Stage 30 registered corrected coordinates for Kolar, Sukta, Dejla Dewda, Matiyari, and Bilgaon.

- Stage 31 checked the updated `Narmada_Drainage.zip` layer. The layer is WGS 84 line drainage with 6,151 features and about 24,155.704 km total line length. After the revised Dejla Dewda coordinate, all five corrected large-offset dams are within about 1 km of the updated drainage and can proceed to visual confirmation before reservoir insertion.

- Stage 32 created final reservoir snap points, LS03B topology insertion package, combined HMS-ready storage-curve addendum, and AEC accuracy matrix. High-confidence AEC: Indira Sagar, Tawa, Barna, Kolar. Provisional seed AEC: Bargi, Omkareshwar, Bilgaon, Dejla Dewda, Matiyari, Sukta.

- Stage 33 created and validated the `Narmada_B1_LS03B_Reservoir_Topology_Draft` HMS branch anchor plus `Narmada_LS03B_2023_Gapfilled_Met`. The branch computes successfully; active reservoir element insertion is the next modelling step.

- Stage 34 created the guarded reservoir element insertion edit package for the LS03B branch. A before-edit backup was saved. Kolar is high-confidence for active insertion; Matiyari, Bilgaon, Dejla Dewda, and Sukta are topology-ready but use provisional AEC/rating data.

- Stage 35 created the reservoir routing data-entry package. Kolar has high-confidence AEC plus verified O&M spillway/head-sluice ratings and can be used for the first active level-pool routing test after selecting an initial pool scenario. Bilgaon, Dejla Dewda, Matiyari, and Sukta have storage curves but still need outlet/release records.

- Stage 36 verified Tawa data and found it richer than Kolar for active reservoir routing: 1,207 extracted Tawa rows vs 542 Kolar rows in checked datasets. Tawa has verified AEC, spillway rating, canal outlets, operation rules, hazard/inundation data, 2023 initial pool, and observed release rows. Promote Tawa ahead of Kolar for the main LS03B active reservoir routing branch.

- Stage 37 compared Barna, Bargi, Indira Sagar Project, and Maheshwar with Tawa/Kolar references before the next active routing stage. Recommended active-routing priority is: 1) Tawa, 2) Barna, 3) Indira Sagar, 4) Kolar, 5) Bargi, 6) Maheshwar. Indira Sagar is physically dominant and has verified AEC, but needs stronger outlet/gate rule data. Barna is smaller but has the strongest official engineering package among the newly reviewed reservoirs. Bargi remains important but provisional. Maheshwar should stay in future expansion until AEC, outlet/gate rating, initial pool, and release data are supplied.

- Stage 38 re-snapped the Stage 37 priority reservoirs to the updated Narmada drainage layer and created the HMS insertion-readiness package. Updated snap distances are: Tawa 0.185 km, Barna 0.491 km, Indira Sagar 1.040 km, Kolar 0.033 km, Bargi 0.237 km, Maheshwar 0.954 km. Tawa, Barna, Kolar, and Bargi are ready after visual QA; Indira Sagar needs moderate placement review plus outlet/gate assumptions; Maheshwar remains outside active routing because reservoir data are missing.

- Stage 39 created the Tawa active reservoir-routing package for LS03C. Tawa package includes 29 storage-curve rows, 2023 initial pool 355.090 m / 2027.407 MCM, 7 observed release target rows, 39 rating-envelope levels, and 762 gate-opening rating rows. Use observed releases as calibration target or specified-release sensitivity first. Do not use the full 13-gate maximum rating envelope as the automatic event operation rule.

- Stage 40 created the `Narmada_B1_LS03C_Tawa_Only` HMS branch shell, `Narmada_LS03C_2023_Tawa_Only_Met` meteorologic model, and `LS03C_2023_Tawa_Only` run. After patching the compute script to match HMS 4.13 `OpenProject("Narmada_HMS", project_folder)` syntax, the pre-insertion shell computed successfully at 15Jul2026 20:41:24 with runtime 00:02. `R_TAWA` still requires controlled HMS GUI/topology insertion.
- Stage 44 inserted `R_TAWA` into the validated LS03C branch as a Modified Puls storage-outflow routing reach. HMS accepted the Tawa paired-data table only after converting storage/outflow to HMS-compatible `ACRE-FT` and `CFS` units and enforcing strictly increasing paired-data rows. The successful topology is `SB_Sub_10 -> R_TAWA -> R_Sub_10`.

- Stage 45 computed and exported the LS03C Tawa-only results. Tawa locally reduced `R_Sub_10` peak from about 5,055.1 to 366.0 m3/s and reduced `R_R_23` peak by about 22.65 percent, but the final outlet peak reduced only about 0.74 percent. This confirmed that one reservoir cannot correct the basin-scale discharge mismatch.

- Stage 46 created and computed `LS03D_2023_Tawa_Barna`, adding `R_BARNA` using the Barna O&M AEC and verified spillway rating envelope. Topology is `R_Sub_4 -> R_BARNA -> R_R_14`. Barna reduced `R_R_14` peak by about 970 m3/s, but the final outlet peak changed only from 162,193.6 to 162,185.7 m3/s. Next recommended active routing stage is Indira Sagar Project because mainstem storage controls are now the stronger remaining need.

## Current Top 3 Next Actions - Updated 18 July 2026

1. Insert Indira Sagar Project in the next LS03E branch using the verified user-supplied AEC workbook and available observed release records; document outlet/gate-rule uncertainty separately.
2. Compare LS03D Tawa+Barna against LS03C Tawa-only and observed CWC gauges in the calibration report, especially at Barmanghat, Handia, Narmadapuram, and Sandia.
3. Continue loss/rainfall-volume calibration after mainstem reservoir controls are active; do not increase losses blindly to compensate for missing reservoir routing.
- Stage 47 created and computed `LS03E_2023_Tawa_Barna_ISP`, adding Indira Sagar Project after the successful Tawa+Barna LS03D branch. Topology is `R_R_8 -> R_ISP -> R_R_7`. The user-supplied ISP AEC curve was used as the physical storage curve through FRL, and the observed 2023 release values were converted into a first-pass release envelope for Modified Puls routing.

- The first LS03E compute failed because computed ISP storage exceeded the available physical AEC table range. This was resolved by adding clearly marked synthetic high-storage HMS stability bounds. These rows are not physical AEC survey points and must not be used as final reservoir geometry.

- LS03E reduced the final outlet peak from about 162,185.7 m3/s in LS03D to about 102,975.4 m3/s, a reduction of about 36.5 percent. This confirms that high-impact mainstem reservoir operation strongly affects the downstream mismatch. However, final calibration still needs actual ISP operating/release rules or observed release hydrograph handling.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 47

1. Decide whether ISP should be represented by observed release hydrograph/time series rather than a static Modified Puls storage-outflow envelope.
2. Add Omkareshwar next only as a linked downstream mainstem operation sensitivity, because its AEC is provisional and its releases are coupled to ISP.
3. Continue rainfall/loss-volume calibration after active mainstem routing assumptions are stabilized; do not treat synthetic high-storage bounds as physical reservoir capacity.
- Stage 49 created the ISP specified-release prelaunch package and exported the 384-hour `R_R_8/FLOW` inflow series from LS03E for mass-balance checking. The observed ISP release record was converted into daily and hourly HMS-ready tables with quality flags for observed and interpolated values.

- Stage 49 mass balance showed that the current upstream model volume into ISP is still not physically reconciled: inflow volume is about 39,582.9 MCM, gap-filled release volume is about 16,853.2 MCM, and the computed storage would rise to about 31,271.6 MCM. This exceeds the verified FRL AEC capacity of 9,585.1 MCM by about 21,686.6 MCM, with first FRL exceedance on 15 September 2023 at 16:00 IST.

- Decision after Stage 49: do not insert ISP specified release as final launch physics until upstream hydrology volume or actual ISP operation data is reconciled. Keep LS03E as sensitivity only and use Stage 49 as the LS03F quality gate.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 49

1. Calibrate the upstream hydrology feeding `R_R_8` before final ISP routing: recheck Thiessen rainfall weighting, HSG/CN-guided spatial losses, baseflow contribution, and observed upstream gauge/storage evidence.
2. Prepare `LS03F` only after the ISP mass balance is credible; use observed/specified ISP release as a calibration/control option, not a final reservoir rule while storage exceeds the physical AEC.
3. Keep Omkareshwar/Bargi/Maheshwar as downstream or future sensitivity branches until the mainstem volume problem at ISP is controlled.
- Stage 50 created the `R_R_8` upstream volume calibration gate. The topology audit found 74 upstream elements and 35 upstream subbasins draining to `R_R_8`, with total contributing area about 63,086.1 sq.km.

- Stage 50 quantified the ISP-ready target: current `R_R_8` inflow volume is about 39,582.9 MCM, while release plus observed ISP storage gain implies about 17,689.6 MCM. Required volume reduction is about 21,893.3 MCM, or 55.31 percent. This is equivalent to about 347.0 mm over the upstream `R_R_8` area.

- Priority recalibration subbasins by simulated volume are `SB_Sub_33`, `SB_Sub_7`, `SB_Sub_22`, `SB_Sub_23`, `SB_Sub_26`, `SB_Sub_1`, `SB_Sub_11`, `SB_Sub_43`, `SB_Sub_6`, `SB_Sub_13`, `SB_Sub_41`, `SB_Sub_5`, and `SB_Sub_30`. These first 13 subbasins account for about 70.7 percent of upstream subbasin flow volume.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 50

1. Create an upstream-only `R_R_8` recalibration branch that adjusts rainfall weighting, HSG/CN-guided loss, and baseflow for the Stage 50 priority subbasins before rechecking ISP mass balance.
2. Review the very high event rainfall and high runoff coefficients in `SB_Sub_33`, `SB_Sub_7`, `SB_Sub_22`, `SB_Sub_23`, `SB_Sub_11`, `SB_Sub_13`, and `SB_Sub_30`.
3. Re-run the ISP mass-balance gate after the upstream recalibration branch; only then prepare final `LS03F` observed/specified ISP release routing.
- Stage 51 created the ISP AEC reverse-rainfall QA package. Using ISP release plus observed storage gain as the control volume, the AEC-implied target inflow is about 17,689.6 MCM versus current `R_R_8` inflow of about 39,582.9 MCM.

- Stage 51 found no `R_R_8` upstream subbasin-hour rainfall cell above 150 mm/hr in the Stage 17 hourly data. The rainfall concern is event accumulation, not a single-hour spike: current upstream mean event rainfall is about 797.4 mm, while strict ISP AEC-compatible reverse rainfall is about 356.4 mm.

- High event-total rainfall flags were raised for `SB_Sub_7`, `SB_Sub_11`, `SB_Sub_13`, `SB_Sub_22`, `SB_Sub_23`, `SB_Sub_30`, `SB_Sub_32`, and `SB_Sub_33`. Use Stage 51 reverse rainfall only as QA/sensitivity, not final design rainfall.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 51

1. Build an `LS03F-RainQA` sensitivity using the Stage 51 reverse-scaled hourly rainfall to test whether `R_R_8` inflow and ISP storage return to the AEC-compatible range.
2. Separately review raw hourly station data and Thiessen/gap-fill sources feeding the flagged subbasins with event totals above about 950 mm.
3. Combine rainfall QA with baseflow/loss sensitivity; do not solve the mismatch by rainfall scaling alone unless raw-station evidence supports it.
- Stage 52 compared hourly HMS rainfall aggregated to daily totals before proceeding to `LS03F-RainQA`. The independent SWDES daily archive did not show 2023 records in the checked daily CSVs, so September 2023 could not be verified against that archive.

- Stage 52 found that `R_R_8` upstream event rainfall is about 797.4 mm from the Stage 17 gap-filled hourly package, while observed-available hours account for only about 331.2 mm. The remaining about 466.3 mm comes from the fill/interpolation process.

- Daily warning dates are 15 September 2023 with about 190.1 mm `R_R_8` upstream areal rainfall and 16 September 2023 with about 120.5 mm. Critical subbasins with high totals and low observed-hour support are `SB_Sub_7`, `SB_Sub_11`, `SB_Sub_13`, `SB_Sub_22`, `SB_Sub_23`, `SB_Sub_30`, and `SB_Sub_32`; `SB_Sub_33` remains a high-total warning.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 52

1. Before `LS03F-RainQA`, review raw station support for 15-16 September 2023, especially Panchmari, Khandwa, Bamni Banjar, Dharampuri, Jobat, Rajpur, Dhulsar, New Harsud, and Khargone.
2. Rebuild rainfall using a stricter gap-fill rule for low-observed-hour subbasins; do not let spatial fill dominate event totals where observed support is below about 15 percent.
3. Run `LS03F-RainQA` only after the daily event-total QA is accepted, then recheck `R_R_8` inflow and ISP AEC mass balance.
- Stage 53 created a daily-controlled hourly gap-fill rainfall candidate. The method keeps observed hourly values unchanged and scales only filled/interpolated hours using the ISP AEC reverse-rainfall daily reference from Stage 51.

- For the `R_R_8` upstream area, original Stage 17 event rainfall was about 797.4 mm. The daily-controlled candidate reduces this to about 478.7 mm, compared with an observed-hour lower bound of about 331.2 mm and a strict AEC-scaled reference of about 356.4 mm.

- Stage 53 found 159 subbasin-day cases where observed hourly rainfall already exceeds the AEC-scaled daily reference. These observed values were retained and flagged rather than reduced. Therefore, the Stage 53 rainfall is a QA candidate, not a final corrected rainfall product.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 53

1. Write the Stage 53 daily-controlled rainfall to HMS DSS and create an `LS03F-RainQA` run branch for sensitivity testing.
2. Compare `LS03F-RainQA` against LS03E at `R_R_8`, ISP mass balance, and the main CWC gauges.
3. If `R_R_8` volume is still high, combine Stage 53 rainfall with baseflow and HSG/CN loss recalibration rather than further suppressing observed rainfall.
- Stage 54 created and computed `LS03F_2023_RainQA_UpstreamCal`, an upstream-only recalibration branch using the Stage 53 daily-controlled hourly rainfall, stronger HSG/CN-guided Initial/Constant losses, and reduced event baseflow for the Stage 50/52 priority upstream subbasins. `SB_Sub_54` is connected to the Stage 53 `SB_Subbasin_2` rainfall series through the P53 rainfall gage alias, because that corrected data belongs to the HMS `SB_Sub_54` element.

- LS03F reduced `R_R_8` inflow volume from about 39,582.9 MCM to about 20,304.1 MCM, a 48.7 percent reduction. The ISP AEC mass-balance target remains about 17,689.6 MCM, so the branch is still about 2,614.5 MCM wet. Maximum computed ISP storage is about 11,992.8 MCM, still about 2,407.7 MCM above the verified FRL AEC capacity.

- Decision after Stage 54: LS03F is a major improvement and should be retained as the next calibration baseline, but it is not yet final-launch hydrology. The next correction should be a smaller, evidence-controlled refinement of rainfall weighting/loss/baseflow for the remaining wet upstream contributors, followed by CWC gauge comparison and another ISP mass-balance gate.

## Current Top 3 Next Actions - Updated 18 July 2026 after Stage 54

1. Identify the remaining upstream elements contributing to the 2,614.5 MCM excess at `R_R_8`, using LS03F subbasin flow/excess/loss summaries rather than basin-wide blanket loss increases.
2. Recheck 15-16 September 2023 rainfall weighting for the remaining wet priority subbasins against station support, daily totals, and HSG/CN loss reasonableness.
3. Run one more LS03G refinement before final ISP specified-release routing; final run should pass the ISP AEC mass-balance gate and then be compared against observed CWC gauges.

## Stage 56 - Planet LULC Manning and Baseflow Audit

- Status: completed initial audit on 2026-07-18.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_56_Planet_LULC_Manning_Baseflow_Audit`
- Decision: high constant loss values, especially 5.5-6.8 mm/hr, are calibrated/effective loss parameters and should not be labelled as pure soil percolation for HSG-D dominant subbasins.
- LULC use: Planet LULC area summary now provides Manning n priors by class; subbasin/reach zonal extraction is still required for field-style parameter assignment.
- Baseflow use: HEC recession guidance supports calibrating recession constants from observed hydrographs; current 0.85-0.90 values behave like interflow/mixed shallow baseflow more than pure groundwater.

## Stage 57 - Lithological Profile HMS Audit

- Status: completed source-document audit on 2026-07-18.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_57_Lithological_Profile_Audit`
- Decision: use lithology for parameter zoning and QA, not direct field-final HMS values.
- Critical modelling point: basalt/fine black soil conditions support high initial abstraction in places, but do not support documenting 5.5-6.8 mm/hr constant loss as pure HSG-D soil percolation.
- Next action: generate subbasin lithology-zonal table and merge it with HSG/CN, Planet LULC, rainfall QA, and observed gauge recession analysis.

## Stage 58 - Zonal Parameter Table

- Status: completed on 2026-07-18.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_58_Zonal_Parameter_Table`
- Decision: use the corrected subbasin parameter table to revise loss/baseflow/Manning; keep physical infiltration separate from effective calibrated loss.
- Extraction: Planet LULC clipped/extracted by 51 subbasins and 500 m reach buffers using QGIS/GDAL.
- Limitation: lithology is currently PDF-derived screening prior; true lithology GIS zonal extraction is pending a Bhukosh/GSI layer.

## Stage 59 - LS03G Physical Loss and Baseflow Cap Branch

- Status: branch created, computed, and compared on 2026-07-18.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_59_LS03G_PhysicalLoss_BaseflowCap`
- Basin branch: `Narmada_B1_LS03G_PhysicalLoss_BaseflowCap`
- Run: `LS03G_2023_PhysicalLoss_BaseflowCap`
- Decision: diagnostic branch separates physical constant loss from effective calibrated residual loss and caps baseflow initial ratio where Stage 58 flagged high baseflow.
- Next action: create LS03H residual-calibration branch: restore physical loss caps plus explicit residual loss/rainfall-routing correction, then compare gauges and ISP mass-balance gate.

### 2026-07-18 - Stage 60 Daily vs Hourly Rainfall Mode QA
- Status: Completed rainfall-mode QA comparing daily-controlled rainfall against hourly peaking behavior.
- Decision: Use daily rainfall as the controlling depth, retain corrected hourly distribution for HMS flood routing, and keep pure daily rainfall as a water-balance check branch.
- Outputs: `04_Calibration_Validation/Stage_60_Daily_vs_Hourly_Rainfall_Mode_QA/Stage60_Daily_vs_Hourly_Rainfall_Mode_QA_Report.md`.
- Next: Build LS03H with daily-controlled hourly precipitation, rerun ISP mass-balance and priority CWC gauge comparison.


### 2026-07-19 - Stage 61 Rainfall Cap 75 mm/hr Test
- Status: Created capped-rainfall sensitivity branch using daily-controlled hourly rainfall with 75 mm/hr maximum and daily volume preservation.
- HMS test: HMS compute completed and LS03H Cap75 results were summarized.
- Outputs: `04_Calibration_Validation/Stage_61_Rainfall_Cap75_Test/Stage61_Rainfall_Cap75_Test_Report.md`.
- Next: Review LS03H vs LS03G peak changes at ISP and priority CWC gauges before adjusting loss/baseflow again.


### 2026-07-19 - Stage 62 Transform Method Audit
- Status: Completed direct basin-file and compute-log audit for all HMS basin branches.
- Finding: LS03G/LS03H basin files use Snyder for all 51 subbasins; HMS log Clark messages are not proof of Clark being selected.
- Next: Build LS03I transform-sensitivity branch to calibrate Snyder/CWC Tp and Cp against observed gauge timing and peaks.


### 2026-07-19 - Stage 63 LS03I Snyder Transform Sensitivity
- Status: Completed Snyder Tp/Cp sensitivity setup and HMS runs using unchanged LS03H cap75 rainfall plus unchanged losses/baseflow.
- Branches: LS03I1 Tp*1.25 Cp*0.90, LS03I2 Tp*1.50 Cp*0.80, LS03I3 Tp*1.75 Cp*0.70.
- Outputs: `04_Calibration_Validation/Stage_63_LS03I_Snyder_Transform_Sensitivity/Stage63_LS03I_Snyder_Transform_Sensitivity_Report.md`.
- Next: Select preferred transform variant and then recalibrate effective loss/reservoir routing only after reviewing peak and timing response.


### 2026-07-19 - Stage 64 Runoff Volume and Attenuation Diagnostic
- Status: Completed diagnostic showing remaining mismatch after LS03H/LS03I3 is still dominated by runoff volume/baseflow and simplified attenuation, not transform alone.
- Key decision: Use LS03I3 as transform base, then build LS03J focused on priority subbasin volume/baseflow correction plus mainstem/reservoir attenuation review.
- Outputs: `04_Calibration_Validation/Stage_64_Runoff_Volume_Attenuation_Diagnostic/Stage64_Runoff_Volume_Attenuation_Diagnostic_Report.md`.


### 2026-07-19 - Stage 65 Subbasin CN and Runoff Category Table
- Status: Completed subbasin-wise CN-I/CN-II/CN-III, HSG, LULC, and runoff category table.
- Decision: Keep Initial+Constant active for LS03 branches; use CN-III as wet/flood screening category for September 2023 SCS-CN comparison.
- Outputs: `04_Calibration_Validation/Stage_65_Subbasin_CN_Runoff_Category/Stage65_Subbasin_CN_Runoff_Category_Report.md`.


### 2026-07-19 - Stage 66 Daily vs Hourly Rainfall Peak Comparison
- Status: Completed daily/hourly rainfall peak comparison for all 51 HMS subbasins.
- Scope: Stage 53 daily-controlled rainfall and Stage 61 cap75 hourly rainfall.
- Outputs: `04_Calibration_Validation/Stage_66_Daily_Hourly_Rainfall_Peak_Comparison/Stage66_Daily_Hourly_Rainfall_Peak_Comparison_Report.md`.

### 2026-07-19 - Stage 67 IMD NetCDF Observed Rainfall Verification
- Status: Completed +/- 3 day independent rainfall check using IMD daily gridded NetCDF.
- IMD source: `E:\01 Projects\03 MPWRD\14 Digitial Atlas\01 Data\02 Raster\02 IMD Gridded Data\RF25_ind2023_rfp25.nc`.
- Active polygon layer confirmed: `02_GIS_Preprocessing/HMS_Reviewed_Source/Extracted/HMS/Sub Basin.shp` with 51 features.
- Key result: IMD observed rainfall also peaks on 2023-09-16; IMD grid-cell maximum is 380.565 mm versus HMS adjusted subbasin maximum 271.504 mm.
- Calibration decision: the 15-16 September event is independently plausible in daily magnitude; next corrections should focus on spatial rainfall weighting, effective loss/baseflow partitioning, reservoir routing/release assumptions, and attenuation. The 23-24 September HMS rainfall pulse is weaker in IMD and should be treated as timing/distribution QA before using it to explain Barmanghat response.
- Outputs: `04_Calibration_Validation/Stage_67_IMD_NetCDF_Rainfall_Verification/Stage67_IMD_Observed_Rainfall_Extraction_Report.md`.

### 2026-07-19 - Stage 68 IMD Peak-Based Rainfall QA
- Status: Completed subbasin-wise HMS rainfall peak comparison against IMD observed daily NetCDF extraction.
- Analysis window: 2023-09-13 to 2023-09-25.
- Result: 14 subbasins have reasonable HMS/IMD peak alignment; 14 are peak-too-high against IMD; 15 have event total too high; 6 underrepresent IMD peak; 2 need spatial-weighting review.
- Priority correction subbasins: `SB_Sub_32`, `SB_Sub_1`, `SB_Sub_30`, `SB_Sub_5`, `SB_Sub_38`, `SB_Sub_33`, `SB_Sub_7`, `SB_Sub_11`, `SB_Sub_27`, `SB_Sub_36`, `SB_Sub_34`, `SB_Sub_37`, `SB_Sub_8`, `SB_Sub_35`.
- Decision: Build next rainfall branch by preserving measured station-hour values and correcting only filled/interpolated rainfall using IMD daily polygon controls and station support. Do not increase losses to hide rainfall QA errors.
- Outputs: `04_Calibration_Validation/Stage_68_IMD_Peak_Based_Rainfall_QA/Stage68_HMS_Rainfall_Peaks_Against_IMD_Report.md`.

### 2026-07-19 - Stage 69 Priority Subbasin IMD vs Present Used Rainfall Check
- Status: Completed detailed daily comparison for 14 priority subbasins: `SB_Sub_32`, `SB_Sub_1`, `SB_Sub_30`, `SB_Sub_5`, `SB_Sub_38`, `SB_Sub_33`, `SB_Sub_7`, `SB_Sub_11`, `SB_Sub_27`, `SB_Sub_36`, `SB_Sub_34`, `SB_Sub_37`, `SB_Sub_8`, `SB_Sub_35`.
- Compared: present HMS-used daily rainfall, cap75 hourly reference, IMD polygon mean/max, observed-hour support, raw filled hours, and adjusted filled-used share.
- Main finding: all 14 priority subbasins exceed IMD polygon mean peak by 2.318x to 7.639x. Highest peak/event-ratio cases are `SB_Sub_32`, `SB_Sub_1`, and `SB_Sub_30`.
- Accuracy note: `SB_Sub_32`, `SB_Sub_36`, and `SB_Sub_34` use nearest IMD grid center because no IMD grid center fell inside the polygon; review with station/local grid support before final correction.
- Decision: Build a corrected rainfall branch that scales daily present-used rainfall toward the IMD mean-to-max envelope, preserving measured station-hour observations and correcting the adjusted filled/interpolated portion first.
- Outputs: `04_Calibration_Validation/Stage_69_Priority_Subbasin_IMD_vs_Used_Rainfall_Check/Stage69_Priority_Subbasin_IMD_vs_Used_Rainfall_Report.md`.

### 2026-07-19 - Stage 70 LS03J IMD Priority Rainfall Correction
- Status: Created and computed rainfall-only branch `LS03J_2023_IMDPriorityCap`.
- Base: `Narmada_B1_LS03I3_Tp175_Cp070`; losses/baseflow/routing unchanged.
- Rainfall change: 14 abrupt-peak priority subbasins were capped to IMD polygon/grid maximum where Stage 61 daily rainfall exceeded IMD max by >1.10x.
- Result: 120 priority subbasin-days changed; priority rainfall reduced from 7189.682 to 3169.688 mm-sum, reduction 4019.994 mm-sum.
- Flow attenuation versus LS03I3: Sandia `-50.583%`, Barmanghat `-47.724%`, Narmadapuram `-39.504%`, Handia `-36.487%`, R_R_8 `-30.102%`, ISP flow peak `-8.986%`.
- Observed comparison after IMD cap: Barmanghat still 5.215x observed, Handia 3.299x, Narmadapuram 2.527x, Sandia 4.175x.
- Decision: IMD correction is useful and should be retained as a sensitivity, but rainfall correction alone does not close the discharge mismatch. Next calibration must combine corrected rainfall with effective loss/baseflow, reservoir/reach attenuation, and gauge/reach mapping checks.
- Outputs: `04_Calibration_Validation/Stage_70_LS03J_IMD_Priority_Rainfall_Correction/Stage70_LS03J_IMD_Priority_Rainfall_Correction_Report.md`.

### Stage 73 - LS03K IMD Daily Controlled Hourly Rainfall

- Status: Complete
- Scope: 14 high-peak subbasins only.
- Branch: `LS03K_IMD_Daily_Controlled_Hourly` using `Narmada_LS03K_IMD_Daily_Controlled_Hourly_Met` and unchanged `Narmada_B1_LS03I3_Tp175_Cp070` parameters.
- Method: scaled each priority subbasin daily rainfall total to IMD Daily NetCDF polygon mean, while preserving the existing hourly distribution shape.
- Priority rainfall before/after: 7189.682 / 3256.467 mm-sum.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_73_LS03K_IMD_Daily_Controlled_Hourly`

### Stage 74 - Dynamic Lag Timing Diagnostic

- Status: Complete
- Scope: LS03K timing, hydrograph shape, observed daily gauge comparison, and reach-routing audit.
- Key issue: many reaches use simple 1-hour lag routing, which can synchronize tributary peaks too sharply.
- Next branch recommendation: create `LS03L_Dynamic_Lag_Routing` with spatial Snyder `Tp`, travel-time-based reach lag/Muskingum routing, and reviewed reservoir release timing.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_74_Dynamic_Lag_Timing_Diagnostic`

### Stage 75 - LS03L Dynamic Lag Routing

- Status: Complete
- Scope: Separate HMS branch using LS03K rainfall and unchanged loss/baseflow/reservoir tables.
- Change: replaced blanket 1-hour lag on Lag reaches with spatially varied reach lag values.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_75_LS03L_Dynamic_Lag_Routing`

### Stage 76 - LS03M Mainstem Muskingum Routing

- Status: Complete
- Scope: Mainstem routing attenuation sensitivity after LS03L lag-only test.
- Change: converted mainstem `R_R_*` Lag reaches to Muskingum routing while keeping rainfall/loss/baseflow/reservoir tables unchanged.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_76_LS03M_Mainstem_Muskingum_Routing`

### Stage 77 - LS03N Targeted Muskingum Tuning

- Status: Complete
- Scope: three Muskingum tuning variants after LS03M strong routing delayed hydrographs too much.
- Selected diagnostic variant: `LS03N3 - Moderate_Muskingum`.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_77_LS03N_Targeted_Muskingum_Tuning`

### Stage 78 - Sandia and Barmanghat Upstream Diagnostic

- Status: Complete
- Scope: upstream element, direct inflow, and subbasin-contributor diagnostics for `R_R_16` Sandia and `R_R_19` Barmanghat using LS03N3.
- Outcome: Sandia should move to local upstream calibration; Barmanghat needs gauge/reach/event verification before timing calibration.
- Output folder: `D:\01 Project\Development\HMS\Narmada\04_Calibration_Validation\Stage_78_Sandia_Barmanghat_Upstream_Diagnostic`

### Stage 79 - LS03O Local Sandia/Barmanghat Calibration

- [x] Created HMS branch/run `LS03O_Local_Sandia_Barmanghat_Cal` from selected LS03N3 parent branch.
- [x] Kept rainfall package unchanged; changed only local loss/baseflow/routing parameters around `SB_Sub_23`, `SB_Sub_33`, `SB_Sub_54`, `SB_Sub_6`, `SB_Sub_13`, `R_R_17`, `R_R_20`, `R_Sub_5`, and `R_Sub_6`.
- [x] Used Sandia as active local calibration control and kept Barmanghat as QA-only because of the event timing mismatch.
- [x] HMS compute/summarizer completed with return codes recorded in `Stage79_LS03O_Local_Sandia_Barmanghat_Calibration_Report.md`.
- [ ] Review LS03O hydrograph shape before expanding local calibration to additional upstream contributors.

Stage 79 quick result: Sandia LS03O peak `14812.755` cumec, ratio `2.647x`; Barmanghat LS03O peak `12776.277` cumec, ratio `3.329x` but QA-only.

### Stage 80 - Local Runoff Volume Partition Check

- [x] Extracted LS03O DSS rainfall/loss/excess/direct/baseflow/flow components for `SB_Sub_23`, `SB_Sub_33`, `SB_Sub_54`, `SB_Sub_6`, and `SB_Sub_13`.
- [x] Built individual subbasin water-partition table and issue flags.
- [x] Confirmed remaining high peak is primarily direct-runoff/excess pulse and rainfall partition related, not baseflow dominated.
- [ ] Repair or confirm missing HSG classification for `SB_Sub_54`.
- [ ] Test local rainfall burst smoothing / daily-volume-preserving redistribution before any wider loss increase.

### Stage 81 - CWC/SUG Empirical Runoff Benchmark

- [x] Applied CWC subzone design-loss phi-index to target subbasin hourly rainfall.
- [x] Convolved CWC/SUG 1-hour UH ordinates with empirical effective rainfall.
- [x] Compared CWC/SUG direct peak and regional formula peaks against LS03O HMS generated runoff.
- [ ] Confirm `SB_Sub_54`/`SB_Subbasin_2` CWC parameter mapping before final acceptance.
- [ ] Use results to design a daily-volume-preserving rainfall burst smoothing test branch.

### Stage 82 - SB_Sub_54 Full Model Audit

- [x] Audited `SB_Sub_54`, `SB_Subbasin_2`, and `SB_Sub_2` across basin, met, gage, CWC/SUG, HSG/CN, rainfall, and runoff outputs.
- [x] Confirmed `SB_Sub_54` is a priority data-wiring/rainfall/HSG QA section.
- [ ] Confirm whether `SB_Sub_2` is a valid separate active basin or a duplicate leftover.
- [ ] Regenerate CWC/SUG and HSG rows under canonical `SB_Sub_54`.
- [ ] Verify `P73_SB_SUB_54` rainfall source/weighting before further calibration.


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


Stage 84 LS03P compute completed. Compare file: `04_Calibration_Validation\Stage_84_LS03P_SB54_Canonical_IMDRedistribution\Stage84_LS03P_Result_Comparison_Report.md`.


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

### Stage 101 - Handia/Narmadapuram Corridor Contributor Audit

- [x] Reviewed active LS04C corridor topology for `R_R_13`, `R_R_12`, and `R_R_11`.
- [x] Audited direct contributors: `SB_Sub_41`, `SB_Sub_42`, `SB_Sub_43`, `R_Sub_18`, `R_R_23`, plus upstream mainstem packages.
- [x] Confirmed the remaining over-peak is an accumulation / mapping / timing issue, not a single missing-water issue.
- [x] Identified `R_R_13` increment at about `7,352` cumec over `R_R_14`, and `R_R_11` increment at about `5,494` cumec over `R_R_12`.
- [x] Marked `SB_Sub_42` as small-volume but QA-sensitive due high runoff/baseflow flags.
- [x] Recommended next stage: LS04D diagnostic comparison mapping for Handia/Narmadapuram before loss/baseflow tuning or bias correction.
- Evidence: `04_Calibration_Validation\Stage_101_Handia_Narmadapuram_Corridor_Contributor_Audit`.

### Stage 102 - LS04D Gauge Mapping Diagnostic

- [x] Created diagnostic-only gauge mapping comparison from LS04C results.
- [x] Tested `Narmadapuram` at `R_R_14`, `R_R_13`, and `R_R_12`; best peak match is `R_R_14`.
- [x] Tested `Handia` at `R_R_12`, `R_R_11`, and `R_R_10`; best tested peak match is `R_R_12`, but it remains strongly high.
- [x] Added Stage102 gauge mapping rows into the Stage98 active hydrological interrelation dashboard.
- [ ] Verify station-to-reach placement visually in QGIS/HMS before changing calibration reporting.
- Evidence: `04_Calibration_Validation\Stage_102_LS04D_Gauge_Mapping_Diagnostic`.

### Stage 103 - Narmadapuram Spatial Gauge-Reach Check

- [x] Checked `Narmadapuram` gauge coordinate against reviewed HMS reaches `R_R_14`, `R_R_13`, `R_R_12`, `R_R_11`, and `R_R_10`.
- [x] Found `R_R_13` / `R-13` is spatially nearest to the gauge point at about `0.37 km`.
- [x] Found `R_R_14` is the best peak-ratio candidate but is about `6.47 km` from the gauge point.
- [x] Decision: do not silently remap Narmadapuram to `R_R_14`; keep `R_R_13` as spatial QA mapping unless QGIS/HMS confirms station coordinate or reach naming is wrong.
- [ ] Next: investigate hydrograph generation/attenuation around `R_R_13` rather than using gauge remapping as a calibration shortcut.
- Evidence: `04_Calibration_Validation\Stage_103_Narmadapuram_Spatial_Gauge_Reach_Check`.

### Stage 104 - R_R_13 Hydrograph Generation / Attenuation Check

- [x] Exported targeted LS04C hydrographs for `R_R_14`, `R_R_23`, `SB_Sub_41`, and `R_R_13`.
- [x] Added LS04C met DSS rainfall depths for `SB_Sub_41`, `SB_Sub_42`, and `SB_Sub_43`.
- [x] Confirmed `R_R_13` peak is `22,053` cumec at hour `157`.
- [x] Confirmed direct inflow sum at the same hour is `22,055` cumec, so `R_R_13` is passing the active inflow package rather than creating unexplained water.
- [x] Identified short `Lag = 1.000 hr` routing on `R_R_14 -> R_R_13`, `R_R_23 -> R_R_13`, and `R_R_13 -> R_R_12` as the next correction target.
- [ ] Next: create a diagnostic routing/attenuation branch for the `R_R_23 + R_R_14 -> R_R_13` corridor before changing loss/baseflow parameters.
- Evidence: `04_Calibration_Validation\Stage_104_RR13_Hydrograph_Generation_Attenuation_Check`.

### Stage 105 - LS04E Corridor Attenuation Exit Branch

- [x] Created three routing-only branches from `LS04C_SB54_Topology_QA`.
- [x] Kept rainfall, losses, Snyder transform, baseflow, reservoir routing, and gauge mapping unchanged.
- [x] Tested lag-only and Muskingum corridor attenuation for `R_R_23`, `R_R_14`, `R_R_13`, `R_R_12`, `R_R_11`, and `R_R_10`.
- [x] Computed and summarized all LS04E variants.
- [x] Best tested branch by four-gauge log-error score: `LS04E3`.
- [ ] Next: use the selected LS04E result for public launch reporting if improvement is material; otherwise document remaining mismatch as a limitation and stop tuning before launch.
- Evidence: `04_Calibration_Validation\Stage_105_LS04E_Corridor_Attenuation_Exit_Branch`.

### Stage 106 - Public Launch Branch Point Version

- [x] Created formal public launch branch-point version `NARMADA_HMS_PUBLIC_LAUNCH_BRANCH_POINT_2026-07-20_STAGE106`.
- [x] Frozen public-launch model branch as `LS04C_SB54_Topology_QA`.
- [x] Preserved `LS04E3_Corridor_Muskingum_Strong` as routing sensitivity evidence, not the primary launch model.
- [x] Copied key HMS project files, DSS results, reports, dashboards, and CSV summaries into a versioned snapshot folder.
- [x] Created return note for post-launch data improvement work.
- [ ] After public launch, resume improvement from Stage106 with `R_R_23`, Handia/Narmadapuram mapping, and independent validation-event checks.
- Evidence: `04_Calibration_Validation\Stage_106_Public_Launch_Branch_Point_Version`.

### Stage 107 - Public Launch Outcome From Stage106

- [x] Created public launch outcome package from Stage106 branch point.
- [x] Confirmed launch freeze branch: `LS04C_SB54_Topology_QA`.
- [x] Retained `LS04E3_Corridor_Muskingum_Strong` only as sensitivity evidence.
- [x] Added explicit public limitation for Handia/Narmadapuram over-prediction.
- [x] Preserved Stage106 as the return point for post-launch data improvement.
- Evidence: `04_Calibration_Validation\Stage_107_Public_Launch_Outcome_From_Stage106`.

### Stage 108 - R_R_23 Upstream Contributor Decomposition

- [x] Resumed post-launch improvement track from Stage106 return point.
- [x] Parsed LS04C topology upstream of `R_R_23`.
- [x] Exported LS04C result and met DSS hydrographs/depths for upstream `R_R_23` contributors.
- [x] Created direct contribution and subbasin runoff QA tables.
- [ ] Next: focus correction on the dominant `R_R_23` contributor(s) found in Stage108 before further Handia/Narmadapuram tuning.
- Evidence: `04_Calibration_Validation\Stage_108_RR23_Upstream_Contributor_Decomposition`.
| CAL-34 | Stage109 LS04F SB_Sub_22 / R_Sub_22 attenuation branch | Complete | `04_Calibration_Validation\Stage_109_LS04F_SB22_RSub22_Attenuation` | Single-change diagnostic: R_Sub_22 Lag -> Muskingum K=4.0, x=0.15, steps=3; rainfall/loss/baseflow unchanged |
| CAL-35 | Stage109 LS04F computed and compared | Complete | `04_Calibration_Validation\Stage_109_LS04F_SB22_RSub22_Attenuation` | Single R_Sub_22 attenuation is useful locally but insufficient alone; next branch should combine local and corridor attenuation without changing rainfall/loss/baseflow |
| CAL-36 | Stage110 LS04G combined attenuation branch | Complete | `04_Calibration_Validation\Stage_110_LS04G_Combined_SB22_Corridor_Attenuation` | Combined R_Sub_22 local attenuation with LS04E3 corridor attenuation; compare before any further tuning |
| PUB-04 | Stage111 hydrological webmap showcase | Complete | `04_Calibration_Validation\Stage_111_Hydrological_Webmap_Showcase` | OpenLayers dashboard showcase with gauges, dams, rain gauges, snap QA, topology inset, and LS04G decision dashboards |

| PUB-05 | Stage112 advanced hydrology analytics command webmap | Complete | `04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap` | Consolidated OpenLayers dashboard with 51 basins, active topology, GD sites, dams/reservoir QA, rainfall stations, LS04G hydrographs, and clickable node intelligence for launch showcase and QA review |

| QA-54 | Stage112 SB_Sub_54 dashboard topology correction | Complete | `04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap\stage112_sb54_topology_status.csv` | Dashboard switched from stale Stage98 topology to active LS04G basin topology; verified `SB_Sub_54 -> R_Sub_14 -> R_R_26 -> R_R_9` |

| PUB-06 | Stage112 Streamlit Cloud app package | Complete | `04_Calibration_Validation\Stage_112_Advanced_Hydrology_Analytics_Webmap\streamlit_cloud_app` | Streamlit Cloud-ready wrapper created with entrypoint, requirements, config, embedded dashboard HTML, and deployment notes |
