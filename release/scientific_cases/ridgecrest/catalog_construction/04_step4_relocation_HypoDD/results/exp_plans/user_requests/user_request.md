

you are a senior seismologist, and you are given a task to relocate the earthquake event using the `PAL_HypoDD` package.

## 1. Data
### 1.1 Phase and Location Catalog from Gamma
- Directory: <CASE_ROOT>/catalog_construction/01_step3_association_Gamma/exp_run/outputs/01_gamma_association_location_magnitude
- Phase File: phase_YYYYMMDD.dat
    - Example content contain event information and corresponding phase information:
        - event information: `EVENT, event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`
        - corresponding phase information: `STATION, net.sta, p_pick_time, s_pick_time, s_amplitude`
        ```
            EVENT,2019-07-04T17:48:57.839000Z,35.5988,-117.5883,12.52,3.76
            STATION,CI.CCC,2019-07-04T17:49:02.398300Z,2019-07-04T17:49:05.638300Z,16823.96728514338
            STATION,CI.DTP,-1,2019-07-04T17:49:10.888300Z,1942.8700799410976
        ```
- Location Catalog: `catalog_YYYYMMDD.dat` with columns: `event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`

### 1.2 Station Metadata 
- File: <CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta

## 3. Relocate using HypoDD
- using `HypoDD` to relocate the earthquake event:
    - the lon_range and lat_range is calculated by the station's range to add some padding (0.1), do not need to keep the grids
- statistic the relocated event location results (e.g. number of events, event location distribution, etc.) and show the result in the figure
- plot the event location results using the original catalog and the relocated catalog to show the difference

## 4. Notes and requirements
- Process the full Ridgecrest analysis window `2019-07-04` to `2019-07-26` (222 daily windows).  
- All the time should be `obspy.UTCDateTime` format (e.g. `2019-07-04T16:13:43.44Z`), do not transformed to the timestamp!
- Show the run progress of the script.
- All the parameter and setting should be defined in the script.
