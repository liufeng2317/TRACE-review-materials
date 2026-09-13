"""Run one released benchmark task with the TRACE framework."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_request(task: dict) -> str:
    definition = task["task_definition"]
    description = definition["task_description"]
    request = (
        f"Please write python scripts to solve the task "
        f"`{definition['task_name']}` with the following specifications:\n"
        f"## User Request\n{definition['agent_prompt']}\n"
        f"## Details of the input and parameters\n"
        f"{json.dumps(description.get('input_data', {}), indent=2)}\n"
    )
    if "output_data" in description:
        request += (
            "## Requirements for the output\n"
            f"{json.dumps(description['output_data'], indent=2)}\n"
        )
    return request + "## Note\n1. Complete straightforward tasks in one script.\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--config")
    parser.add_argument("--enable-trajectory", action="store_true")
    args = parser.parse_args()

    from seismoagent.runing import run_seismoagent

    task = json.loads(args.task.read_text(encoding="utf-8"))
    run_seismoagent(
        request=build_request(task),
        config=args.config,
        run_name=task["task_id"],
        output_dir=str(args.output_dir),
        enable_trajectory=args.enable_trajectory,
    )


if __name__ == "__main__":
    main()
