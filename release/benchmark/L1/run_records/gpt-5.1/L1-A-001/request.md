Please write python scripts to solve the task `Download_Event_Catalog_from_FDSN_Server` with the following specifications:
## User Request
Using `seismostats` library to download the earthquake catalog from the FDSN server at {fdsn_url}. Fetch earthquake events between {start_time} and {end_time} within the geographic box defined by latitudes {min_latitude}-{max_latitude} and longitudes {min_longitude}-{max_longitude}, only returning events of magnitude ≥ {min_magnitude}. Retrieve data in batches of {batch_size}, assemble into a pandas DataFrame, and create a `seismostats` Catalog object. Save the download catalog, and plot a figure to show the catalog in space.
## Details of the input and parameters
{
    "start_time": "2020-01-01T00:00:00",
    "end_time": "2022-01-01T00:00:00",
    "min_longitude": 5,
    "max_longitude": 11,
    "min_latitude": 45,
    "max_latitude": 48,
    "min_magnitude": 0.5,
    "batch_size": 1000,
    "fdsn_url": "http://eida.ethz.ch/fdsnws/event/1/query"
}
## Requirements for the output
{
    "catalog_file": "earthquake_catalog.csv",
    "catalog_plot": "earthquake_catalog.png"
}
## Note
1. if the task is straightforward, complete it within a single script.
