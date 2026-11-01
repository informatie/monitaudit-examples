# examples/scripts/threading/main_thread_failure.py

"""
MonitAudit ThreadPoolExecutor failure-handling example.

Purpose
-------
Demonstrates what happens when one traced worker task fails while other
worker tasks complete successfully.

Three tasks run through a ThreadPoolExecutor with three workers. Task 2
deliberately raises RuntimeError, while tasks 1 and 3 complete successfully.

The worker exception is stored in its Future and re-raised in the main thread
when future.result() is called. The application handles that failure and
continues processing the remaining futures.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any

from main_load_config import (
    CONFIG_DIR,
    DATA_DIR,
    EXAMPLES_DIR,
    OUTPUT_DIR,
    SCRIPTS_DIR,
    get_config_path,
)
from monitaudit.utilities.build_monitaudit import build_monitaudit


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CONFIG_PATH = get_config_path(__file__)


# ---------------------------------------------------------------------------
# Executor configuration
# ---------------------------------------------------------------------------

WORKERS = 3
TASK_COUNT = 3
FAILING_TASK = 2


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def task(
        number: int,
    ) -> dict[str, Any]:
        """
        Execute one worker task.

        Task 2 deliberately fails. Tasks 1 and 3 complete successfully.
        """

        thread = threading.current_thread()

        mta.info(
            "Worker task started",
            task_number=number,
            worker_count=WORKERS,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        # Simulate work so concurrent worker activity is visible.
        time.sleep(0.10)

        if number == FAILING_TASK:
            raise RuntimeError(
                "Deliberate worker failure"
            )

        mta.info(
            "Worker task completed",
            task_number=number,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        return {
            "task_number": number,
            "thread_name": thread.name,
            "thread_id": thread.ident,
        }

    mta.info(
        "Thread failure example started",
        example="main_thread_failure",
        worker_count=WORKERS,
        task_count=TASK_COUNT,
        failing_task=FAILING_TASK,
    )

    futures: dict[
        Future[dict[str, Any]],
        int,
    ] = {}

    successful_tasks = 0
    failed_tasks = 0

    completed_task_numbers: list[int] = []
    failed_task_numbers: list[int] = []

    used_threads: set[str] = set()
    thread_task_counts: dict[str, int] = {}

    with ThreadPoolExecutor(
        max_workers=WORKERS,
        thread_name_prefix="failure-worker",
    ) as executor:
        for number in range(
            1,
            TASK_COUNT + 1,
        ):
            future = executor.submit(
                task,
                number,
            )

            futures[future] = number

        mta.info(
            "All worker tasks submitted",
            submitted_tasks=len(futures),
            worker_count=WORKERS,
        )

        for future in as_completed(
            futures
        ):
            task_number = futures[future]

            try:
                result = future.result()

            except RuntimeError as exception:
                failed_tasks += 1

                failed_task_numbers.append(
                    task_number
                )

                mta.warning(
                    "Worker failure handled",
                    task_number=task_number,
                    error_type=type(exception).__name__,
                    error_message=str(exception),
                )

            else:
                successful_tasks += 1

                completed_task_numbers.append(
                    task_number
                )

                thread_name = str(
                    result["thread_name"]
                )

                used_threads.add(
                    thread_name
                )

                thread_task_counts[
                    thread_name
                ] = (
                    thread_task_counts.get(
                        thread_name,
                        0,
                    )
                    + 1
                )

                mta.info(
                    "Worker result received",
                    task_number=result["task_number"],
                    thread_name=thread_name,
                    thread_id=result["thread_id"],
                )

    mta.info(
        "Thread failure example completed",
        example="main_thread_failure",
        submitted_tasks=len(futures),
        successful_tasks=successful_tasks,
        failed_tasks=failed_tasks,
        completed_task_numbers=sorted(
            completed_task_numbers
        ),
        failed_task_numbers=sorted(
            failed_task_numbers
        ),
        used_thread_count=len(used_threads),
        used_threads=sorted(
            used_threads
        ),
        thread_task_counts=thread_task_counts,
    )

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    expected_successful_tasks = (
        TASK_COUNT - 1
    )

    if successful_tasks != expected_successful_tasks:
        raise AssertionError(
            f"Expected {expected_successful_tasks} successful tasks, "
            f"got {successful_tasks}."
        )

    if failed_tasks != 1:
        raise AssertionError(
            f"Expected 1 failed task, got {failed_tasks}."
        )

    expected_completed_tasks = [
        number
        for number in range(
            1,
            TASK_COUNT + 1,
        )
        if number != FAILING_TASK
    ]

    actual_completed_tasks = sorted(
        completed_task_numbers
    )

    if actual_completed_tasks != expected_completed_tasks:
        raise AssertionError(
            "Unexpected successful task numbers: "
            f"{actual_completed_tasks}"
        )

    if failed_task_numbers != [
        FAILING_TASK
    ]:
        raise AssertionError(
            "Unexpected failed task numbers: "
            f"{failed_task_numbers}"
        )

    if len(used_threads) > WORKERS:
        raise AssertionError(
            f"Executor used {len(used_threads)} threads "
            f"with max_workers={WORKERS}."
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: ThreadPoolExecutor failure ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ThreadPoolExecutor\n"
        f"  - max_workers = {WORKERS}\n"
        f"  - {TASK_COUNT} traced worker tasks\n"
        "  - successful worker execution\n"
        "  - deliberate worker failure\n"
        "  - Future exception propagation\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - function_error\n"
        "  - error_type\n"
        "  - error_message\n"
        "  - traceback\n"
        "  - main thread handles expected worker failure\n"
        "  - remaining futures continue processing\n"
        "\n"
        "Directories:\n"
        f"  Examples : {EXAMPLES_DIR}\n"
        f"  Config   : {CONFIG_DIR}\n"
        f"  Data     : {DATA_DIR}\n"
        f"  Scripts  : {SCRIPTS_DIR}\n"
        f"  Output   : {OUTPUT_DIR}\n"
        "\n"
        "Configuration:\n"
        f"  {CONFIG_PATH}\n"
        "\n"
        "Expected task results:\n"
        "  task(1) -> SUCCESS\n"
        f"  task({FAILING_TASK}) -> FAILURE\n"
        "  task(3) -> SUCCESS\n"
        "\n"
        "Expected total trace events:\n"
        f"  function_start = {TASK_COUNT}\n"
        f"  function_end   = {TASK_COUNT - 1}\n"
        "  function_error = 1\n"
        "\n"
        "Expected failed trace:\n"
        "  function      = task\n"
        f"  task number   = {FAILING_TASK}\n"
        "  error_type    = RuntimeError\n"
        "  error_message = Deliberate worker failure\n"
        "  traceback     = populated\n"
        "\n"
        "Expected trace relationship:\n"
        "  Every task is submitted directly to the executor.\n"
        "  Every task is therefore an independent root trace.\n"
        "\n"
        "  task.call_id:\n"
        "    unique per task\n"
        "\n"
        "  task.parent_call_id:\n"
        "    null\n"
        "\n"
        "Expected execution flow:\n"
        "  executor submits task(1)\n"
        "  executor submits task(2)\n"
        "  executor submits task(3)\n"
        "\n"
        "  task(1) -> function_end\n"
        "  task(2) -> function_error\n"
        "  task(3) -> function_end\n"
        "\n"
        "  main thread collects Future results\n"
        "  RuntimeError from task(2) is handled\n"
        "  application completes normally\n"
        "\n"
        "Important:\n"
        "  @mta.trace records function_error and then re-raises the\n"
        "  original exception. ThreadPoolExecutor stores that exception\n"
        "  in the Future until future.result() is called.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect concurrent worker output\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()