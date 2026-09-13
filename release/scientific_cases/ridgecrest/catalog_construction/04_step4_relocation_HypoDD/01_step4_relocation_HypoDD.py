import os
import sys
sys.path.append("<PROJECT_ROOT>/")
from seismoagent.runing import run_seismoagent


user_request = """

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
- File: <PROJECT_ROOT>/examples/ridgecrest/data/station/station.sta

## 3. Relocate using HypoDD
- using `HypoDD` to relocate the earthquake event:
    - velocity model settings:
        - layer top depths: `[0, 1, 2, 3, 4, 5, 6, 7, 8, 16, 32]` km
        - Vp: `[4.80, 5.00, 5.20, 5.38, 5.55, 5.72, 5.88, 6.02, 6.12, 6.24, 7.12]` km/s
        - Vp/Vs: `1.73`
    - `ph2dt` parameters: `MINWGHT=0`, `MAXDIST=80`, `MAXSEP=8`, `MAXNGH=20`, `MINLNK=6`, `MINOBS=6`, `MAXOBS=40`
    - HypoDD controls: `IDAT=2`, `IPHA=3`, `DIST=80`, `OBSCC=0`, `OBSCT=8`, `ISTART=2`, `ISOLV=2`, `NSET=2`, `CID=0`
    - weighting stages:
        - stage 1: `NITER=4`, `WTCTP=1.0`, `WTCTS=0.5`, `WRCT=6`, `WDCT=20`, `DAMP=120`
        - stage 2: `NITER=8`, `WTCTP=0.7`, `WTCTS=0.3`, `WRCT=4`, `WDCT=15`, `DAMP=80`
- statistic the relocated event location results (e.g. number of events, event location distribution, etc.) and show the result in the figure
- plot the event location results using the original catalog and the relocated catalog to show the difference
- The public release distinguishes the native agent output from the final
  manuscript-analysis catalog. The latter is the agent output after final
  expert validation and selection, reported as 84,474 events.

## 4. Notes and requirements
- Process the full Ridgecrest analysis window `2019-07-04` to `2019-07-26` (222 daily windows).  
- All the time should be `obspy.UTCDateTime` format (e.g. `2019-07-04T16:13:43.44Z`), do not transformed to the timestamp!
- Show the run progress of the script.
- All the parameter and setting should be defined in the script.
"""

if __name__ == "__main__":

    run_name = "01_step4_relocation_HypoDD"
    output_dir = "<CASE_ROOT>/catalog_construction/run"

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name),
        # resume_stage="workflow"
    )
