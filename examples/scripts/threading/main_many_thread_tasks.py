# examples/scripts/threading/main_many_thread_tasks.py

"""
MonitAudit many-thread-tasks example.

Purpose
-------
Demonstrates how a ThreadPoolExecutor with three worker threads processes
more tasks than there are workers.

The example creates 20 independent traced tasks. Because there are more tasks
than workers, worker threads are reused throughout the execution.

Every task is an independent root trace.
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
TASKS = 20


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
        Process one numbered task.

        Every invocation is an independent root trace.
        """

        thread = threading.current_thread()

        mta.info(
            "Task running",
            task_number=number,
            worker_count=WORKERS,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        # Simulate processing.
        #
        # The short delay makes concurrent execution and worker reuse
        # easier to observe in the configured sinks.
        time.sleep(0.05)

        mta.info(
            "Task completed",
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
        "Many-thread-tasks example started",
        example="main_many_thread_tasks",
        worker_count=WORKERS,
        task_count=TASKS,
    )

    futures: list[
        Future[dict[str, Any]]
    ] = []

    with ThreadPoolExecutor(
        max_workers=WORKERS,
        thread_name_prefix="many-task-worker",
    ) as executor:
        for number in range(TASKS):
            future = executor.submit(
                task,
                number,
            )

            futures.append(
                future
            )

        mta.info(
            "All tasks submitted",
            worker_count=WORKERS,
            submitted_tasks=len(futures),
        )

        completed_tasks = 0
        completed_numbers: list[int] = []
        used_threads: set[str] = set()
        thread_task_counts: dict[str, int] = {}

        for future in as_completed(
            futures
        ):
            result = future.result()

            completed_tasks += 1

            task_number = int(
                result["task_number"]
            )

            thread_name = str(
                result["thread_name"]
            )

            completed_numbers.append(
                task_number
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
                "Task result received",
                task_number=task_number,
                completed_tasks=completed_tasks,
                thread_name=thread_name,
                thread_id=result["thread_id"],
            )

    mta.info(
        "Many-thread-tasks example completed",
        example="main_many_thread_tasks",
        worker_count=WORKERS,
        submitted_tasks=len(futures),
        completed_tasks=completed_tasks,
        used_thread_count=len(used_threads),
        used_threads=sorted(
            used_threads
        ),
        thread_task_counts=thread_task_counts,
    )

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    if completed_tasks != TASKS:
        raise AssertionError(
            f"Expected {TASKS} completed tasks, "
            f"got {completed_tasks}."
        )

    expected_numbers = list(
        range(TASKS)
    )

    actual_numbers = sorted(
        completed_numbers
    )

    if actual_numbers != expected_numbers:
        raise AssertionError(
            "Unexpected completed task numbers: "
            f"{actual_numbers}"
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
        "=== Example completed: many thread tasks ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ThreadPoolExecutor\n"
        f"  - max_workers = {WORKERS}\n"
        f"  - {TASKS} submitted tasks\n"
        "  - worker reuse\n"
        "  - concurrent traced functions\n"
        "  - independent root traces\n"
        "  - automatic parameter capture\n"
        "  - thread names\n"
        "  - thread IDs\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - duration_ms\n"
        "  - result collection with as_completed()\n"
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
        "Executor configuration:\n"
        f"  workers = {WORKERS}\n"
        f"  tasks   = {TASKS}\n"
        "\n"
        "Expected worker names may include:\n"
        "  many-task-worker_0\n"
        "  many-task-worker_1\n"
        "  many-task-worker_2\n"
        "\n"
        "Expected trace counts:\n"
        f"  task function_start = {TASKS}\n"
        f"  task function_end   = {TASKS}\n"
        "  task function_error = 0\n"
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
        "Expected task parameters:\n"
        "  task(0)  -> number = 0\n"
        "  task(1)  -> number = 1\n"
        "  ...\n"
        f"  task({TASKS - 1}) -> number = {TASKS - 1}\n"
        "\n"
        "Worker reuse:\n"
        f"  {TASKS} tasks are processed by at most {WORKERS} workers.\n"
        "  Workers therefore process multiple tasks during the\n"
        "  lifetime of the executor.\n"
        "\n"
        "  The final log record contains thread_task_counts showing\n"
        "  the actual task distribution for the current execution.\n"
        "\n"
        "Important:\n"
        "  Thread scheduling is controlled by Python and the operating\n"
        "  system. max_workers limits concurrency but does not guarantee\n"
        "  a particular task-to-thread assignment.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect interleaved task execution\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()