
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
    1. Load the trace and check the trace completeness and merge the segmented trace into one trace if needed
    2. design and apply a preprocessing pipeline for each trace
    3. aggregate the processed trace into a three-component stream for later deep leanring based phase picking usage
    4. save processed three-component waveform per station-day:  
        - Format: `YYYYMMDD/{network}.{station}.{starttime}.{endtime}.mseed`
        - No temporary/intermediate files.
        - Use the precise day's start/end times in filename.
    5. plot a figure to show the preprocessing process (one case is enough)

Note: You can save the processed data for phase picking and magnitude estimation separately.
- For the phase picking, there is no need to do response removal and normalization.
- For the magnitude estimation, remove the instrument response and simulate to the Wood-Anderson instrument resposne is needed.

Add comments for the following usage of the processed data

## 4. Computational & software requirements
- Process only the data from 2019-07-04 to 2019-07-26 (22 daily windows); date range must be explicitly defined in the script.
- Use parallel computation (up to 64 cores) for data loading, preprocessing, and statistics.
- Display progress information (e.g., progress bars or logs) during long computations whenever possible.
- All time variables should use `obspy.UTCDateTime`.
