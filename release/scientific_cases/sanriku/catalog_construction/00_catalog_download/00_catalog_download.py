import os
import sys
sys.path.append("<REPO_ROOT>")
from seismoagent.runing import run_seismoagent

user_request = """
Implement and validate a JMA unified hypocenter catalog download workflow for
the Sanriku, northeast Japan study region.

## Task objective

1. Use the NIED Hi-net JMA catalog service:
   - Login endpoint: https://hinetwww11.bosai.go.jp/auth/?LANG=en
   - Catalog endpoint: https://hinetwww11.bosai.go.jp/auth/JMA/jmalist.php
2. Use the manuscript-aligned time interval:
   - start date: 2025-06-01
   - end date: 2026-05-02
   - treat the end date as exclusive when constructing requests, so the
     requested records cover 2025-06-01 through 2026-05-01.
   - do not replace this interval with a current-date or 2026-only default.
3. Use the Sanriku regional bounds:
   - latitude: 38.50 to 42.50 degrees N
   - longitude: 141.00 to 144.50 degrees E
   - apply the bounds inclusively after parsing the catalog.
4. Split requests into chunks of no more than 7 days because of the JMA
   service limit. Record the exact chunk boundaries and actual returned dates.
5. Output an ASPECT-ready CSV with exactly:
   datetime,lat,lon,dep,mag
6. Use the filename pattern:
   Snet_catalog_YYYYMMDD_YYYYMMDD.csv

## Implementation requirements

- Prefer reading HINET_USERNAME and HINET_PASSWORD from the .env file;
  command-line arguments may override them.
  - <CASE_ROOT>/data/hinet_account/.env
- Use requests.Session to maintain the authenticated session.
- Add retry and backoff for network requests.
- If an HTML response cannot be parsed, save the original failed response to a
  debug/raw file and state the saved path in the error message.
- Parse the JMA fixed-width catalog table; do not use fragile comma splitting.
- During cleaning:
  - parse datetime as time;
  - convert lat/lon/dep/mag to numeric values;
  - remove rows with missing values;
  - filter by the Sanriku spatial range;
  - sort by datetime;
  - remove duplicates.
- Keep the optional raw-dir argument for saving the raw text from each time
  chunk.

## Required outputs

- The cleaned catalog CSV file.
- A catalog distribution figure.
"""

if __name__ == "__main__":

    run_name = "00_catalog_download"
    output_dir = "<CASE_ROOT>/run"

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name)
    )
