import os
import sys
sys.path.append("<PROJECT_ROOT>/")
from seismoagent.runing import run_seismoagent

user_request = """
You are a seismologist, and you are given a task to preprocess the seismic data for seismic monitoring and analysis.

**Used data range**: 2019-07-04 to 2019-07-26 (22 daily windows), date range must be explicitly defined in the script.

## 1. Data Sources
### 1.1 Continuous Seismic Waveform Data
- Base Directory: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/waveforms_raw`
- Folder Structure:
    - Subdirectories for each station named `network.station` (e.g., `CI.CCC/`)
        - Files at the subdirectory: 
            - format: `{network}.{station}.{location}.{channel}__{start_time}__{end_time}.mseed`
            - Example: `CI.CCC..HHE__20190704T000000Z__20190705T000000Z.mseed`

### 1.2 Station Metadata
- Directory: `<DATA_ROOT>/Science2019_Ross_Ridgecrest/data/stationxml/`
- Each station's StationXML file: 
    - filename: `{network}.{station}.xml`
    - format: StationXML

## 2. Station Information Retrieval and Formatting
- Save the station information to a csv file: `station.sta`
    - Format: `network.station,latitude,longitude,elevation,gain`
        - elevation in meters
        - gain is averaging the gain of three channels (HH* or EH*)

## 3. Waveform Data Standardization and Preprocessing for later **phase picking** and **magnitude estimation** usage
- For each station, each full UTC day in used data range (each station-day):
    1. Load the trace and check the trace completeness and merge the segmented trace into one trace if needed.
    2. Standardize the sampling rate before later windowing/output:
        - Resample the trace to 100 Hz.
    3. Design and apply a preprocessing pipeline for each trace.
        - Note: To avoid the edge influence of the processing process, use padded processing windows for response removal, filtering, and tapering, then trim back to the exact UTC station-day interval before saving.
    4. Aggregate the processed trace into a three-component stream for later deep-learning based phase picking usage.
    5. Save processed three-component waveform per station-day:
        - Format: `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
        - No temporary/intermediate files.
        - Use the precise day start/end times in filename.
        - The saved product must be exactly the station-day interval after the padded operations have been trimmed away.
    6. Plot a figure to show the preprocessing process (one case is enough).

Note: You can save the processed data for phase picking and magnitude estimation separately.
- For the phase picking, there is no need to do response removal and normalization.
- For the phase picking product, still avoid filtering/tapering directly on a tightly clipped day window if those operations are used; process with padding and trim back to the day.
- For the magnitude estimation, remove the instrument response and simulate to the Wood-Anderson instrument response. This product is especially sensitive to edge artifacts, so response removal, filtering/pre-filtering, tapering, and Wood-Anderson simulation should be done on padded data before final trimming.

## 4. Computational & software requirements
- Process the full production window from 2019-07-04 to 2019-07-26 (22 daily windows); date range must be explicitly defined in the script.
- Use parallel computation (up to 64 cores) for data loading, preprocessing, and statistics.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
- All time variables should use `obspy.UTCDateTime`.
"""
if __name__ == "__main__":

    run_name = "01_step1_data_preprocessing_for_phasepicking"
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
