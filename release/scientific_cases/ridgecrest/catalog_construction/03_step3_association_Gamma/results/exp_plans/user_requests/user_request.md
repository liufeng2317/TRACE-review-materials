
You are a senior seismologist. You are given a task to associate the seismic phase and locate the earthquake using the `gamma` package.

## 1. Data

### 1.1 Processed Waveform Data for Magnitude Estimation (Miniseed)
- Base Directory: `<CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/magnitude_wood_anderson`
    - Structure: Subfolders named by start date (e.g. 20190704), each containing processed MiniSEED files for specific 24-hour ranges.
    - Naming: `{network}.{station}.{start_time}.{end_time}.mseed` (e.g., `CI.CCC.20190704T000000Z.20190705T000000Z.mseed`)
    - Introduction: The data has been preprocessed for magnitude estimation: including detrend, taper, instrument response removal to displacement, and Wood–Anderson simulation.

### 1.2 Picks Data from PhaseNet
- Directory: <CASE_ROOT>/catalog_construction/01_step2_phase_picking_PhaseNet/exp_run/outputs/01_phasenet_phase_picking
- File: picks_YYYYMMDD.csv

### 1.3 Station Metadata 
- File: <CASE_ROOT>/catalog_construction/01_step1_data_preprocessing_for_phasepicking/exp_run/outputs/01_preprocess_ridgecrest_stationday_waveforms/station.sta

## 2. Phase association and earthquake location
use `gamma` package to associate P and S picks from the picks data and locate the earthquake at each day, with following parameters and settings:
- the longitude/latitude range is calculated from the station coordinate, the depth range is [0, 30] km
- the x(km), y(km) is projected from the longitude/latitude
- the velocity model is 
    - {"z": [0.0, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0], "p": [4.96, 5.14, 5.45, 6.07, 6.12, 6.24, 7.12], "s": [v / 1.73 for v in [4.96, 5.14, 5.45, 6.07, 6.12, 6.24, 7.12]]}

## 3. Output requirements
- exatract and reformat the event and the associated phase information (`phase_YYYYMMDD.dat`) and event catalog (`catalog_YYYYMMDD.dat`) for each day
- example of the `phase_YYYYMMDD.dat`
    ```
        2019-07-04T21:44:09.228888Z,35.69,-117.49,14,0.86
        CI.SRT,-1,2019-07-04T21:44:17.648300Z,3.141505421970662e-08
        CI.WVP2,2019-07-04T21:44:16.590000Z,-1,6.704140174780469e-09
    ```
    - event information: `event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`
    - corresponding phase information: `net.sta, p_pick_time, s_pick_time, s_amplitude`
        - the `s_amplitude` is the amplitude of the S phase
            - if the `s_pick_time` and `p_pick_time` are both not exist, set it to -1.0
            - otherwise, use the `s_amplitude` if exist, otherwise use the `p_amplitude`
    - Make sure the phase information is paired with the event information!!! (important)
- example of the `catalog_YYYYMMDD.dat` 
    ```
        2019-07-04T21:44:09.228888Z,35.69,-117.49,14,0.86
        2019-07-04T17:09:19.450065Z,35.71,-117.47,14,0.84
        2019-07-04T17:40:18.052418Z,35.71,-117.49,16,2.55
    ```
    - event information: `event_origin_time, event_latitude, event_longitude, event_depth, event_magnitude`

The event magnitude is not accurate, so we need to estimate the magnitude at step 4.

## 4. Magnitude estimation for the located earthquake
- use the processed waveform to retrieve the amplitude of the S phase at the picked time
- estimate the magnitude for the located earthquake
- rewrite the `phase_YYYYMMDD.dat` and `catalog_YYYYMMDD.dat` with the correct magnitude information

## 5. visualization
- plot a figure to visualize the association results of the associated picks (one case is enough)
- plot a figure to visualize the event location results
- plot a figure to visualize the event location statistical results

## Notes
- Process the full Ridgecrest analysis window from 2019-07-04 to 2019-07-26 (222 daily windows); date range must be explicitly defined in the script.
- Use parallel computation (up to 64 cores) for phase association, earthquake location, and magnitude estimation.
- All the time should be `obspy.UTCDateTime` format (e.g. `2019-07-04T16:13:43.44Z`), do not transformed to the UNIX timestamp!
- Show the progress of the processing.
