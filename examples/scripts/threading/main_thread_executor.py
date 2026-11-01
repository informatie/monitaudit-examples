# examples/scripts/threading/main_thread_executor.py

"""
MonitAudit ThreadPoolExecutor example.

Purpose
-------
Demonstrates concurrent order processing using exactly three worker threads.

The customer/order dataset is loaded from:

    data/example_dataset.yaml

Individual orders are submitted directly to the ThreadPoolExecutor and each
order-processing function is traced independently with @mta.trace.

Every order-processing log includes executor and thread information so worker
activity can be inspected in the configured MonitAudit sinks.
"""

from __future__ import annotations

import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any

import yaml

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
DATASET_PATH = DATA_DIR / "example_dataset.yaml"


# ---------------------------------------------------------------------------
# Executor configuration
# ---------------------------------------------------------------------------

EXECUTOR_NAME = "order-worker"
EXECUTOR_COUNT = 3


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

def load_dataset() -> dict[str, Any]:
    if not DATASET_PATH.is_file():
        raise FileNotFoundError(
            f"Example dataset not found: {DATASET_PATH}"
        )

    with DATASET_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Invalid dataset format: {DATASET_PATH}"
        )

    customers = data.get("customers")

    if not isinstance(customers, list):
        raise ValueError(
            "Dataset field 'customers' must be a list: "
            f"{DATASET_PATH}"
        )

    return data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def process_order(
        cust_nummer: int,
        cust_naam: str,
        order_code: str,
        order_name: str,
    ) -> dict[str, Any]:
        thread = threading.current_thread()

        mta.info(
            "Order processing started on worker",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            thread_name=thread.name,
            thread_id=thread.ident,
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_code=order_code,
            order_name=order_name,
        )

        # Simulate work long enough for concurrent worker activity
        # to become visible in the configured sinks.
        time.sleep(0.20)

        mta.info(
            "Order processing completed on worker",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            thread_name=thread.name,
            thread_id=thread.ident,
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_code=order_code,
            order_name=order_name,
        )

        return {
            "cust_nummer": cust_nummer,
            "order_code": order_code,
            "thread_name": thread.name,
            "thread_id": thread.ident,
        }

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Thread executor example started",
        example="main_thread_executor",
        executor_name=EXECUTOR_NAME,
        executor_count=EXECUTOR_COUNT,
        customer_count=len(customers),
    )

    futures: list[
        Future[dict[str, Any]]
    ] = []

    with ThreadPoolExecutor(
        max_workers=EXECUTOR_COUNT,
        thread_name_prefix=EXECUTOR_NAME,
    ) as executor:
        for customer in customers:
            if not isinstance(customer, dict):
                raise ValueError(
                    "Each customer must be a mapping."
                )

            cust_nummer = customer["cust_nummer"]
            cust_naam = customer["cust_naam"]
            orders = customer["orders"]

            if not isinstance(orders, list):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "'orders' must be a list."
                )

            mta.info(
                "Submitting customer orders",
                executor_name=EXECUTOR_NAME,
                executor_count=EXECUTOR_COUNT,
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
                order_count=len(orders),
            )

            for order in orders:
                if not isinstance(order, dict):
                    raise ValueError(
                        f"Customer {cust_nummer!r} "
                        "contains an invalid order."
                    )

                future = executor.submit(
                    process_order,
                    cust_nummer,
                    cust_naam,
                    order["order_code"],
                    order["order_name"],
                )

                futures.append(
                    future
                )

        mta.info(
            "All orders submitted",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            submitted_tasks=len(futures),
        )

        completed_tasks = 0
        used_threads: set[str] = set()
        thread_task_counts: dict[str, int] = {}

        for future in as_completed(
            futures
        ):
            result = future.result()

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
                "Worker result received",
                executor_name=EXECUTOR_NAME,
                executor_count=EXECUTOR_COUNT,
                completed_tasks=completed_tasks,
                cust_nummer=result["cust_nummer"],
                order_code=result["order_code"],
                worker_thread=thread_name,
                worker_thread_id=result["thread_id"],
            )

    mta.info(
        "Thread executor example completed",
        example="main_thread_executor",
        executor_name=EXECUTOR_NAME,
        executor_count=EXECUTOR_COUNT,
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

    if completed_tasks != len(futures):
        raise AssertionError(
            f"Expected {len(futures)} completed tasks, "
            f"got {completed_tasks}."
        )

    if len(used_threads) > EXECUTOR_COUNT:
        raise AssertionError(
            f"Executor used {len(used_threads)} threads "
            f"with max_workers={EXECUTOR_COUNT}."
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: ThreadPoolExecutor ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ThreadPoolExecutor\n"
        f"  - max_workers = {EXECUTOR_COUNT}\n"
        "  - concurrent order processing\n"
        "  - traced worker functions\n"
        "  - independent order root traces\n"
        "  - worker thread names in structured logging\n"
        "  - worker thread IDs in structured logging\n"
        "  - automatic parameter capture\n"
        "  - call_id\n"
        "  - duration_ms\n"
        "  - futures collected with as_completed()\n"
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
        "Dataset:\n"
        f"  {DATASET_PATH}\n"
        "\n"
        "Executor configuration:\n"
        f"  executor_name  = {EXECUTOR_NAME}\n"
        f"  executor_count = {EXECUTOR_COUNT}\n"
        "\n"
        "Expected worker names may include:\n"
        "  order-worker_0\n"
        "  order-worker_1\n"
        "  order-worker_2\n"
        "\n"
        "Expected trace relationship:\n"
        "  Every process_order invocation is submitted directly\n"
        "  to the executor and therefore starts independently.\n"
        "\n"
        "  process_order.call_id:\n"
        "    unique per invocation\n"
        "\n"
        "  process_order.parent_call_id:\n"
        "    null\n"
        "\n"
        "Expected captured parameters:\n"
        "  - cust_nummer\n"
        "  - cust_naam\n"
        "  - order_code\n"
        "  - order_name\n"
        "\n"
        "Thread information:\n"
        "  - executor_name\n"
        "  - executor_count\n"
        "  - thread_name\n"
        "  - thread_id\n"
        "\n"
        "Important:\n"
        "  Thread scheduling is controlled by Python and the operating\n"
        "  system. max_workers limits concurrency but does not guarantee\n"
        "  that every worker receives the same number of orders.\n"
        "\n"
        "  The final log record contains thread_task_counts showing\n"
        "  the actual task distribution for the current execution.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect interleaved order processing\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()