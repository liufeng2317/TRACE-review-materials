# TRACE Benchmark

This directory contains the public benchmark definitions, evaluation procedure,
model scores, expert scores, and a minimal example run record.

## Contents

```text
benchmark/
├── L1/
│   ├── task_index.csv
│   ├── tasks/
│   └── run_records/
├── L2/
│   ├── task_index.csv
│   └── tasks/
├── evaluation/
│   ├── evaluation_results_summary.json
│   ├── evaluation_metadata_definitions.json
│   └── model_index.yaml
└── scripts/
    └── run_task.py
```

The benchmark contains 104 tasks: 74 Level 1 tasks and 30 Level 2 tasks.
The reported model comparison contains 312 task-model records for the three
models listed in `evaluation/model_index.yaml`.

## Evaluation procedure

Each task is defined by a scientific objective, input specification, prompt,
and expected outputs. Models were evaluated by running the task workflows and
checking the generated outputs against the task-specific evaluation criteria.
The criteria include output validity, numerical or structural agreement, and
visual agreement when a figure is required.

For the 90 tasks that include visualization outputs, the manual-reference
visualization score is based on five expert scores on a 1–5 scale. In
`evaluation/evaluation_results_summary.json`, each
`manual_reference.visualization_rating` contains the five scores, and
`manual_reference.score` contains their arithmetic mean. The remaining 14
tasks do not require visual evaluation and therefore have no manual-reference
score.

Task definitions use public placeholders such as `<DATA_ROOT>` and
`<OUTPUT_ROOT>`, so the benchmark can be connected to a local dataset package
without changing the task specifications.

## Run one task

```bash
python release/benchmark/scripts/run_task.py \
  --task release/benchmark/L1/tasks/a_data_access_retrieval/L1-A-001.json \
  --output-dir /tmp/trace-run/L1-A-001 \
  --enable-trajectory
```

The output directory is separate from the release. The included example run
record contains the request, final plan, workflow, generated script, and
status metadata.
