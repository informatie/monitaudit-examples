# examples/scripts/threading/main_order_thread_executor.py

"""
MonitAudit order-level ThreadPoolExecutor example.

Purpose
-------
Demonstrates concurrent order processing using exactly three worker threads.

Unlike the customer-level executor example, individual order tasks are
submitted directly to the ThreadPoolExecutor.

Every task is traced independently with @mta.trace. Because the tasks are
submitted directly to worker threads, each task represents an independent
root trace.
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
TASKS = 9


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
        Process one order task as an independent root trace.
        """

        thread = threading.current_thread()

        mta.info(
            "Order processing started",
            task_number=number,
            worker_count=WORKERS,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        # Simulate order processing so concurrency and worker reuse
        # become visible in the logs.
        time.sleep(0.10)

        mta.info(
            "Order processing completed",
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
        "Order thread executor example started",
        example="main_order_thread_executor",
        worker_count=WORKERS,
        task_count=TASKS,
    )

    futures: list[
        Future[dict[str, Any]]
    ] = []

    results: list[
        dict[str, Any]
    ] = []

    with ThreadPoolExecutor(
        max_workers=WORKERS,
        thread_name_prefix="order-worker",
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
            "All order tasks submitted",
            worker_count=WORKERS,
            submitted_tasks=len(futures),
        )

        completed_tasks = 0
        used_threads: set[str] = set()
        thread_task_counts: dict[str, int] = {}

        for future in as_completed(
            futures
        ):
            result = future.result()

            results.append(
                result
            )

            completed_tasks += 1

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
                "Order result received",
                task_number=result["task_number"],
                completed_tasks=completed_tasks,
                thread_name=thread_name,
                thread_id=result["thread_id"],
            )

    task_numbers = sorted(
        int(result["task_number"])
        for result in results
    )

    mta.info(
        "Order thread executor example completed",
        example="main_order_thread_executor",
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

    if task_numbers != list(range(TASKS)):
        raise AssertionError(
            "Unexpected task results: "
            f"{task_numbers}"
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
        "=== Example completed: order ThreadPoolExecutor ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ThreadPoolExecutor\n"
        f"  - max_workers = {WORKERS}\n"
        f"  - {TASKS} order tasks submitted\n"
        "  - concurrent order processing\n"
        "  - worker reuse\n"
        "  - @mta.trace inside executor workers\n"
        "  - independent root traces\n"
        "  - unique call_id values\n"
        "  - automatic parameter capture\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - duration_ms\n"
        "  - thread_name\n"
        "  - thread_id\n"
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
        "  order-worker_0\n"
        "  order-worker_1\n"
        "  order-worker_2\n"
        "\n"
        "Expected trace counts:\n"
        f"  task function_start = {TASKS}\n"
        f"  task function_end   = {TASKS}\n"
        "  task function_error = 0\n"
        "\n"
        "Expected trace relationship:\n"
        "  Every task is submitted directly to the executor.\n"
        "  Each task is therefore an independent root trace.\n"
        "\n"
        "  task.call_id:\n"
        "    unique per task\n"
        "\n"
        "  task.parent_call_id:\n"
        "    null\n"
        "\n"
        "Expected captured parameters:\n"
        "  task(0) -> number = 0\n"
        "  task(1) -> number = 1\n"
        "  task(2) -> number = 2\n"
        "  ...\n"
        f"  task({TASKS - 1}) -> number = {TASKS - 1}\n"
        "\n"
        "Worker reuse:\n"
        f"  {TASKS} tasks are processed by at most {WORKERS} workers.\n"
        "  The final log record contains thread_task_counts showing\n"
        "  the actual task distribution for this execution.\n"
        "\n"
        "Important:\n"
        "  Thread scheduling is controlled by Python and the operating\n"
        "  system. max_workers limits concurrency but does not guarantee\n"
        "  a particular task-to-thread assignment.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect interleaved task processing\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()