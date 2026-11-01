# examples/scripts/threading/main_thread_trace_isolation.py

"""
MonitAudit thread trace-isolation example.

Purpose
-------
Demonstrates that multiple traced root functions can execute concurrently
on separate ThreadPoolExecutor workers while maintaining independent trace
contexts.

The example starts three independent root tasks. Each root task calls one
nested traced child function.

Every child trace should use the active root call_id as its parent_call_id
without sharing trace context with another worker.
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def child(
        task_id: int,
    ) -> dict[str, Any]:
        """
        Execute one nested child operation.

        The active root trace should automatically become this child's
        parent trace.
        """

        thread = threading.current_thread()

        mta.info(
            "Child running",
            task_id=task_id,
            worker_count=WORKERS,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        # Keep the worker busy briefly so concurrent execution is easier
        # to observe in the configured sinks.
        time.sleep(0.40)

        mta.info(
            "Child completed",
            task_id=task_id,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        return {
            "task_id": task_id,
            "thread_name": thread.name,
            "thread_id": thread.ident,
        }

    @mta.trace
    def root(
        task_id: int,
    ) -> dict[str, Any]:
        """
        Execute one independent root trace on an executor worker.
        """

        thread = threading.current_thread()

        mta.info(
            "Root running",
            task_id=task_id,
            worker_count=WORKERS,
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        child_result = child(
            task_id
        )

        mta.info(
            "Root completed",
            task_id=task_id,
            child_task_id=child_result["task_id"],
            thread_name=thread.name,
            thread_id=thread.ident,
        )

        return {
            "task_id": task_id,
            "thread_name": thread.name,
            "thread_id": thread.ident,
            "child_thread_name": child_result[
                "thread_name"
            ],
            "child_thread_id": child_result[
                "thread_id"
            ],
        }

    mta.info(
        "Thread trace isolation example started",
        example="main_thread_trace_isolation",
        worker_count=WORKERS,
        task_count=TASK_COUNT,
    )

    futures: list[
        Future[dict[str, Any]]
    ] = []

    with ThreadPoolExecutor(
        max_workers=WORKERS,
        thread_name_prefix="trace-worker",
    ) as executor:
        for task_id in range(
            1,
            TASK_COUNT + 1,
        ):
            future = executor.submit(
                root,
                task_id,
            )

            futures.append(
                future
            )

        mta.info(
            "All root tasks submitted",
            worker_count=WORKERS,
            submitted_tasks=len(futures),
        )

        completed_tasks = 0
        completed_task_ids: list[int] = []
        used_threads: set[str] = set()

        for future in as_completed(
            futures
        ):
            result = future.result()

            task_id = int(
                result["task_id"]
            )

            root_thread_name = str(
                result["thread_name"]
            )

            root_thread_id = result[
                "thread_id"
            ]

            child_thread_name = str(
                result["child_thread_name"]
            )

            child_thread_id = result[
                "child_thread_id"
            ]

            completed_tasks += 1

            completed_task_ids.append(
                task_id
            )

            used_threads.add(
                root_thread_name
            )

            # root() calls child() synchronously. Both functions must execute
            # on the same executor worker.
            if root_thread_name != child_thread_name:
                raise AssertionError(
                    f"Root task {task_id} ran on {root_thread_name}, "
                    f"but its child ran on {child_thread_name}."
                )

            if root_thread_id != child_thread_id:
                raise AssertionError(
                    f"Root task {task_id} and its child have different "
                    "thread IDs."
                )

            mta.info(
                "Root task result received",
                task_id=task_id,
                completed_tasks=completed_tasks,
                thread_name=root_thread_name,
                thread_id=root_thread_id,
            )

    mta.info(
        "Thread trace isolation example completed",
        example="main_thread_trace_isolation",
        worker_count=WORKERS,
        submitted_tasks=len(futures),
        completed_tasks=completed_tasks,
        completed_task_ids=sorted(
            completed_task_ids
        ),
        used_thread_count=len(used_threads),
        used_threads=sorted(
            used_threads
        ),
    )

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    if completed_tasks != TASK_COUNT:
        raise AssertionError(
            f"Expected {TASK_COUNT} completed tasks, "
            f"got {completed_tasks}."
        )

    expected_task_ids = list(
        range(
            1,
            TASK_COUNT + 1,
        )
    )

    actual_task_ids = sorted(
        completed_task_ids
    )

    if actual_task_ids != expected_task_ids:
        raise AssertionError(
            "Unexpected completed task IDs: "
            f"{actual_task_ids}"
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
        "=== Example completed: thread trace isolation ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ThreadPoolExecutor\n"
        f"  - max_workers = {WORKERS}\n"
        f"  - {TASK_COUNT} concurrent root tasks\n"
        "  - one nested child trace per root\n"
        "  - independent root trace contexts\n"
        "  - unique root call_id values\n"
        "  - child parent_call_id relationships\n"
        "  - ContextVar isolation between workers\n"
        "  - root and child execute on the same worker\n"
        "  - thread_name logging\n"
        "  - thread_id logging\n"
        "  - automatic parameter capture\n"
        "  - function_start and function_end\n"
        "  - duration_ms\n"
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
        f"  tasks   = {TASK_COUNT}\n"
        "\n"
        "Expected worker names may include:\n"
        "  trace-worker_0\n"
        "  trace-worker_1\n"
        "  trace-worker_2\n"
        "\n"
        "Expected trace structure:\n"
        "  root(1)\n"
        "    child(1)\n"
        "\n"
        "  root(2)\n"
        "    child(2)\n"
        "\n"
        "  root(3)\n"
        "    child(3)\n"
        "\n"
        "Expected root relationship:\n"
        "  root.call_id:\n"
        "    unique per root invocation\n"
        "\n"
        "  root.parent_call_id:\n"
        "    null\n"
        "\n"
        "Expected child relationship:\n"
        "  child.call_id:\n"
        "    unique per child invocation\n"
        "\n"
        "  child.parent_call_id:\n"
        "    equals its matching root.call_id\n"
        "\n"
        "  child.parameters.task_id:\n"
        "    equals its matching root.parameters.task_id\n"
        "\n"
        "Expected trace counts:\n"
        f"  root function_start  = {TASK_COUNT}\n"
        f"  root function_end    = {TASK_COUNT}\n"
        f"  child function_start = {TASK_COUNT}\n"
        f"  child function_end   = {TASK_COUNT}\n"
        "  function_error       = 0\n"
        "\n"
        "Expected thread relationship:\n"
        "  A root and its child execute synchronously on the same\n"
        "  executor worker thread.\n"
        "\n"
        "Isolation verification:\n"
        "  - all root call_id values are different\n"
        "  - every root has parent_call_id = null\n"
        "  - every child points to its own root call_id\n"
        "  - no child points to another task's root call_id\n"
        "\n"
        "Important:\n"
        "  The Python runtime and operating system determine the exact\n"
        "  task-to-worker assignment. The relationship to verify is\n"
        "  trace isolation, not a fixed assignment to worker numbers.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect concurrent nested trace output\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()