import os
import sys
sys.path.append("<PROJECT_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
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
- Final production pick threshold: use `P >= 0.4` and `S >= 0.4`.

### 1.3 Station Metadata 
- Station
  `<PROJECT_ROOT>/examples/ridgecrest/data/station/station.sta`
- Station allowlist:
  `<PROJECT_ROOT>/examples/ridgecrest/data/station/ridgecrest_core30_station_allowlist.txt`
  Use the station in the allowlist to do the phase association & locatoin.

## 2. Phase association and earthquake location
### 2.1 Phase association and location using `gamma` package
use `gamma` package to associate P and S picks from the picks data and locate the earthquake at each day, with following parameters and settings:
- use only picks and stations in the allowlist
- use the fixed production geographic association bounds: longitude [-118.0, -117.0], latitude [35.25, 36.25], depth range [0, 30] km
- project longitude/latitude to local x(km), y(km) using an azimuthal-equidistant projection centered near longitude -117.598605 and latitude 35.71
- setting the parameter `eps=10, oversampling=3`
- use amplitude-free association (`use_amplitude=False` / no amplitude term in GaMMA association)
- use the current production gradual 1-D velocity model. This same velocity model is used later by the selected HypoDD production route, so do not replace it with the older 7-layer model:
    - ```
    {
        "z": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 16.0, 32.0],
        "p": [4.80, 5.00, 5.20, 5.38, 5.55, 5.72, 5.88, 6.02, 6.12, 6.24, 7.12],
        "s": [v / 1.73 for v in [4.80, 5.00, 5.20, 5.38, 5.55, 5.72, 5.88, 6.02, 6.12, 6.24, 7.12]]
    }
    ```

### 2.2 Output requirements
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

The event magnitude is not accurate, so we need to estimate the magnitude at step 3.
The 140,505-event GaMMA catalog is the agent-generated catalog submitted to
the final relocation route. The manuscript result is the subsequently
validated final catalog described by the HypoDD release.

## 3. Magnitude estimation for the located earthquake
- Use the processed Wood-Anderson waveform to measure station-level peak amplitude near the associated picks.
- Use phase-dependent amplitude windows:
    - If an S pick exists, use the S-centered window `[-0.5, +3.0]` seconds.
    - If only a P pick exists, use the P-centered window `[-1.0, +6.0]` seconds to avoid underestimating larger events with a too-short P window.
    - Prefer S-window station magnitude when both P and S are available for the same station-event pair.
- Convert station amplitude to local-magnitude-style `ML` using:
    ```
    ML = log10(A_mm) + 1.11 * log10(R_km / 100) + 0.00189 * (R_km - 100) + 3.0
    ```
    where `A_mm` is the Wood-Anderson peak amplitude in millimeters and `R_km` is hypocentral distance in kilometers.
- Estimate event magnitude as the median of valid station magnitudes
- Rewrite the `phase_YYYYMMDD.dat` and `catalog_YYYYMMDD.dat` with the recomputed magnitude information.

## 5. visualization
- plot a figure to visualize the association results of the associated picks (one case is enough)
- plot a figure to visualize the event location results
- plot a figure to visualize the event location statistical results

## Notes
- Process the full Ridgecrest analysis window from 2019-07-04 to 2019-07-26 (222 daily windows); date range must be explicitly defined in the script.
- Use parallel computation (up to 64 cores) for phase association, earthquake location, and magnitude estimation.
- All the time should be `obspy.UTCDateTime` format (e.g. `2019-07-04T16:13:43.44Z`), do not transformed to the UNIX timestamp!
- Show the progress of the processing.
"""

if __name__ == "__main__":

    run_name = "01_step3_association_Gamma"
    output_dir = "<CASE_ROOT>/catalog_construction/run"

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name)
    )
