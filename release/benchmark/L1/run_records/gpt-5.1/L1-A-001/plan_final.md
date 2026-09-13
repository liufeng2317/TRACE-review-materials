**Top-level objective**

Implement a single Python script that uses the `seismostats` library to query an FDSN event service at the specified URL, retrieve earthquake events in batches for a given time–space–magnitude window, assemble them into a pandas DataFrame and a `seismostats.Catalog` object, save the catalog to `earthquake_catalog.csv`, and plot the epicenters in space to `earthquake_catalog.png`.

---

## 1. Overall script structure (single file)

All steps are implemented in one Python script, organized into logical blocks:

1. Imports and parameter definitions.
2. Time parsing and basic validity checks.
3. FDSN event client initialization.
4. Batched catalog download using `seismostats`.
5. DataFrame assembly and minimal validation.
6. `seismostats.Catalog` construction.
7. Catalog export to CSV.
8. Spatial plotting of epicenters and saving to PNG.
9. Basic error handling and informative console output.

---

## 2. Inputs, parameters, and outputs

### 2.1 Fixed query parameters (from user)

Define these as constants at the top of the script:

- Time window:
  - `START_TIME_STR = "2020-01-01T00:00:00"`
  - `END_TIME_STR   = "2022-01-01T00:00:00"`

- Spatial bounds (geographic box):
  - `MIN_LONGITUDE = 5.0`
  - `MAX_LONGITUDE = 11.0`
  - `MIN_LATITUDE  = 45.0`
  - `MAX_LATITUDE  = 48.0`

- Magnitude threshold:
  - `MIN_MAGNITUDE = 0.5`

- Batch size:
  - `BATCH_SIZE = 1000`

- FDSN URL:
  - `FDSN_URL = "http://eida.ethz.ch/fdsnws/event/1/query"`

### 2.2 Output products

Also define:

- `CATALOG_CSV = "earthquake_catalog.csv"`
- `CATALOG_PNG = "earthquake_catalog.png"`

These names are used consistently in the script when saving outputs.

---

## 3. Libraries and key objects

### 3.1 Required imports

At the top of the script, import:

- `pandas as pd` — for time parsing and DataFrame handling.
- `matplotlib.pyplot as plt` — for plotting and saving figures.
- From `seismostats`:
  - `from seismostats.catalogs.client import FDSNWSEventClient` — to query FDSN.
  - `from seismostats import Catalog` — catalog container and plotting.

Optionally import:

- `sys` — for clean exit on fatal errors.
- `logging` — if you want structured messages; otherwise plain `print` is sufficient.

---

## 4. Time parsing and parameter sanity checks

### 4.1 Time conversion

Within `main()` (or top-level):

1. Convert time strings to pandas `Timestamp`:

   - `start_time = pd.to_datetime(START_TIME_STR)`
   - `end_time   = pd.to_datetime(END_TIME_STR)`

2. Check ordering:

   - If `start_time >= end_time`, print an error and terminate.

### 4.2 Spatial and magnitude checks

Before querying:

- Confirm numeric parameters are sensible (no code here, just logic):
  - `MIN_LONGITUDE < MAX_LONGITUDE`
  - `MIN_LATITUDE < MAX_LATITUDE`
  - `MIN_MAGNITUDE >= 0.0`

If any condition fails, report and stop.

This avoids sending clearly invalid requests to the server.

---

## 5. FDSN event client initialization

Create an FDSN client pointing to the user-specified endpoint:

1. Instantiate:

   - `client = FDSNWSEventClient(FDSN_URL)`

2. Optionally print:

   - `"Initialized FDSN client for URL: http://eida.ethz.ch/fdsnws/event/1/query"`

This is the only client object; no additional configuration is necessary.

---

## 6. Batched event download with `seismostats`

### 6.1 Main query via `get_events`

Use the `FDSNWSEventClient.get_events` method, exploiting its built‑in batching:

- Call:

  - `df_events = client.get_events( start_time=start_time, end_time=end_time, min_magnitude=MIN_MAGNITUDE, min_longitude=MIN_LONGITUDE, max_longitude=MAX_LONGITUDE, min_latitude=MIN_LATITUDE, max_latitude=MAX_LATITUDE, batch_size=BATCH_SIZE )`

Key points:

- `batch_size=BATCH_SIZE` ensures the client requests up to 1000 events per batch and internally loops over pages if necessary.
- The time, spatial, and magnitude filters are passed directly to the FDSN service.

### 6.2 Handling connectivity and server errors

Wrap the call in a try–except block:

- Catch network-related exceptions (e.g., HTTP errors, timeouts).
- On failure:
  - Print a meaningful message including the time window and URL.
  - Exit the script gracefully (no CSV or PNG written).

### 6.3 Result validation

After `get_events` returns:

1. Confirm result type:

   - Expect a pandas `DataFrame`. If not, convert to DataFrame if it is Catalog or similar.

2. Check emptiness:

   - If `df_events` is empty (`df_events.empty`):
     - Print `"No events found for the specified constraints."`
     - Still write an empty CSV (with column headers if possible).
     - Skip plotting or create a degenerate plot with a note (simpler: skip plot and inform user).

3. Ensure key columns exist:

   - Required: `"time"`, `"latitude"`, `"longitude"`.
   - Preferred for plotting and later use: `"magnitude"`.
   - If any required column is missing, print a warning and stop (no plot; optional CSV).

4. Normalize dtypes:

   - Ensure `df_events["time"]` is datetime (apply `pd.to_datetime` if needed).
   - Convert `latitude`, `longitude`, `magnitude` to numeric (`pd.to_numeric(..., errors="coerce")`) and optionally drop rows where these are missing.

---

## 7. Constructing the `seismostats.Catalog`

### 7.1 Catalog construction

Create a `Catalog` from the validated DataFrame:

- `catalog = Catalog(df_events)`

This object behaves like a pandas DataFrame but is tailored for seismic catalogs and supports convenient plotting methods.

### 7.2 Basic checks on Catalog

Perform simple checks:

- `n_events = len(catalog)`
- Print `"Downloaded N events in total."`

Optionally verify that:

- All `latitude` are within `[MIN_LATITUDE, MAX_LATITUDE]`.
- All `longitude` are within `[MIN_LONGITUDE, MAX_LONGITUDE]`.
- All `magnitude` (if present) are ≥ `MIN_MAGNITUDE`.

If out-of-range events appear, print a warning (this would indicate unusual server behavior).

---

## 8. Saving the catalog to CSV

### 8.1 CSV export

Use the DataFrame-like interface of `Catalog`:

- `catalog.to_csv(CATALOG_CSV, index=False)`

Behavior:

- Writes all columns returned by the FDSN service (times, coordinates, depths, magnitudes, IDs, etc.).
- Omits the index column for a clean file.

### 8.2 Error handling

Wrap CSV writing in try–except:

- If file writing fails (e.g., permission issues), print a clear message and stop.
- Do not attempt plotting if the catalog could not be saved (optional but cleaner).

---

## 9. Spatial plotting of the catalog

You can leverage either the `Catalog.plot_in_space` helper (if available in the installed `seismostats` version) or manual plotting with `matplotlib`. The improved plan uses `Catalog.plot_in_space` for convenience but outlines a fallback.

### 9.1 Prepare data

Before plotting, ensure there are events:

- If `len(catalog) == 0`, do not plot; print `"Catalog is empty, skipping plot."`.

If plotting manually, you may want a subset without NaNs in coordinates:

- `catalog_nonan = catalog.dropna(subset=["longitude", "latitude"])`

### 9.2 Option A: Use `Catalog.plot_in_space` (preferred)

If your `seismostats` version provides this method:

1. Call:

   - `fig = catalog.plot_in_space(include_map=True)`

   or, if it does not return a figure, assume it draws on the current axes.

   - Optional arguments (not required, but conceptually possible):
     - Bounding box specific to the region.
     - Color options or symbol sizing by magnitude.

2. After plotting, save:

   - If `fig` is returned:
     - `fig.savefig(CATALOG_PNG)`
   - Otherwise:
     - `plt.savefig(CATALOG_PNG)`

3. Close figure:

   - `plt.close()` to free resources.

### 9.3 Option B: Manual longitude–latitude scatter plot (fallback)

If `plot_in_space` is unavailable or you prefer explicit control:

1. Extract columns:

   - `lons = catalog["longitude"]`
   - `lats = catalog["latitude"]`
   - Optionally `mags = catalog["magnitude"]` for color or size scaling.

2. Create scatter plot:

   - Initialize a figure and axis.
   - Plot `ax.scatter(lons, lats, s=5, alpha=0.7)` or similar.
   - Set labels:
     - X label: `"Longitude (°)"`
     - Y label: `"Latitude (°)"`.
   - Axis limits:
     - `ax.set_xlim(MIN_LONGITUDE, MAX_LONGITUDE)`
     - `ax.set_ylim(MIN_LATITUDE, MAX_LATITUDE)`
   - Title:
     - e.g., `"Earthquakes 2020-01-01–2022-01-01, M≥0.5"`

3. Save and close:

   - `plt.savefig(CATALOG_PNG)`
   - `plt.close()`

Either plotting path satisfies the requirement to show the catalog in space.

---

## 10. Script flow and main entry point

Organize the code in a `main()` function and call it under a standard main guard:

1. **Imports and constants definition**
2. **`main()` function**:
   - Parse/validate times and parameters.
   - Initialize `FDSNWSEventClient`.
   - Download events with `get_events` and `batch_size=BATCH_SIZE`.
   - Validate and clean `df_events`.
   - Build `Catalog`.
   - Save to `earthquake_catalog.csv`.
   - Plot epicenters and save `earthquake_catalog.png`.
   - Print a concise summary: number of events, output filenames.

3. **Main guard**:

   - `if __name__ == "__main__": main()`

This satisfies the user’s request for a single script that:

- Uses `seismostats` and an FDSN event service.
- Applies the specified temporal, spatial, and magnitude constraints.
- Uses batched retrieval.
- Produces a pandas DataFrame and `seismostats.Catalog`.
- Saves the catalog as `earthquake_catalog.csv`.
- Plots and saves the spatial distribution as `earthquake_catalog.png`.