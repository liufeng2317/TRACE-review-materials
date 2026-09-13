import os
import sys
sys.path.append("<REPO_ROOT>")
from seismoagent.runing import run_seismoagent


user_request = """
You are a senior seismologist and seismic workflow engineer.

You are given a task to relocate events in the Sanriku regional JMA catalog
with `hypodd_runner`.

## 1. Input data

Use the canonical expert-processed handoff directory:

<data_dir>: `<CASE_ROOT>/run/00_travel_time_download/exp_run/expert/outputs`

The available input files are:
- `<data_dir>/events.csv`: catalog of events
- `<data_dir>/picks.csv`: picks of events
- `<data_dir>/phase.dat`: phase data
- `<data_dir>/station.sta`: station data
- `<data_dir>/summary.txt`: statistics of the catalog
- `<data_dir>/main_earthquake.csv`: main earthquake information (just for plotting)

Uses the following regional bounds and time range:
- latitude: 38.50 to 42.50 degrees N
- longitude: 141.00 to 144.50 degrees E
- time range: 2025-06-01 through 2026-05-01, with 2026-05-02 as the exclusive upper bound.

Station codes must remain internally consistent between station and phase files. For this catalog-only task, prefer preserving the original station IDs when they already match between `phase.dat` and `station.sta`. Add a synthetic network prefix such as `J.` only if the selected `hypodd_runner` API path explicitly requires `NET.STA`, and apply the same mapping consistently to all generated inputs. Preserve event IDs and UTC-compatible ISO time strings throughout the workflow.

Use the provided `phase.dat` as the primary phase input when it validates successfully. Do not rebuild it from `picks.csv` by default.

## 2. Velocity model
Use this 1-D velocity model for the relocation:
- layer tops in km: `[0.0, 5.0, 10.0, 20.0, 35.0, 50.0, 90.0]`
- Vp in km/s: `[5.4, 5.8, 6.2, 6.6, 7.2, 7.6, 8.05]`
- Use a documented Vp/Vs ratio suitable for HypoDD, with `1.73` as the default if no better value is estimated.

## 3. Experiment design requirements
Use the Python package `hypodd_runner` as the relocation package.

This is a full-catalog catalog-only relocation task.

Use the documented `hypodd_runner` catalog-only relocation API and write a
self-contained execution script.

Use exactly 12 non-overlapping calendar-month windows covering
2025-06-01 through 2026-05-01. Use the package auto-window entry point with
`min_events_per_window=100`, `max_events_per_window=10800`, and
`allow_partial=False`.

Use catalog-derived P and S differential times only. Use these ph2dt
parameters:
`MAXSEP=20 km`, `MAXDIST=180 km`, `MAXNGH=12`, `MINLNK=8`, `MINOBS=6`,
and `MAXOBS=40`.

Use these HypoDD settings:
`IDAT=2`, `IPHA=3`, `MAXDIST=180`, `OBSCC=0`, `OBSCT=0`, `ISTART=2`,
`ISOLV=2`, `NSET=2`, and `CID=0`.

Use the following iteration rows:
`8 -9 -9 -9 -9 1.0 0.7 0.03 8 120`
and
`12 -9 -9 -9 -9 0.7 0.3 0.02 5 80`.

Use `Vp/Vs=1.73` and the supplied seven-layer velocity model. Set the catalog
code/output prefix to `japan_aomori_nocc_full`.

## 4. Success criteria and outputs

Full-run success means a real full-catalog relocation product:
- all input events are accounted for as relocated, unrelocated, or failed with explicit reasons;
- every attempted package run has a status, input counts, key parameter summary, output folder, native log paths, and failure evidence if applicable;
- successful package runs have real non-empty native outputs;
- the final merged relocated catalog is built from real native outputs and preserves event IDs or a verified event identity mapping;
- failed or unrelocated events are recorded separately and are not counted as relocated results.
- The final merged `.reloc` file must be built from real native HypoDD outputs.
  Report its row count and any failed or unrelocated events explicitly; do not
  edit the output to force agreement with an external reference.

Do not treat fallback, mock, skipped, no-op, unchanged original catalog, empty files, plotting-only output, or schema-only checks as success.

"""

if __name__ == "__main__":

    run_name = "01_relocation_HypoDD"
    output_dir = "<CASE_ROOT>/run"

    run_seismoagent(
        request=user_request,
        run_name=run_name,
        output_dir=output_dir,
        disable_refinement=False,
        max_refinement_rounds=3,
        enable_trajectory=True,
        # resume=os.path.join(output_dir, run_name),
        # resume_stage="coding",
        # resume_coding_step=1
    )
