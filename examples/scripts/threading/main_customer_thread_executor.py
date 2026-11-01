# examples/scripts/threading/main_customer_thread_executor.py

"""
MonitAudit customer-level ThreadPoolExecutor example.

Purpose
-------
Demonstrates parallel customer processing with exactly three worker threads,
with nested order traces under every customer trace.

Each customer is submitted as one task to a ThreadPoolExecutor. Within each
customer worker, orders are processed sequentially as child traces.

Every customer and order log includes thread information so executor activity
is visible in the configured MonitAudit sinks.
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

EXECUTOR_NAME = "customer-worker"
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
        """
        Process one order as a child trace of process_customer.
        """

        thread = threading.current_thread()

        mta.info(
            "Order processing started",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            thread_name=thread.name,
            thread_id=thread.ident,
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_code=order_code,
            order_name=order_name,
        )

        # Simulate order processing.
        time.sleep(0.15)

        mta.info(
            "Order processing completed",
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
            "order_code": order_code,
            "order_name": order_name,
            "thread_name": thread.name,
            "thread_id": thread.ident,
        }

    @mta.trace
    def process_customer(
        cust_nummer: int,
        cust_naam: str,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Process one customer as a root trace in a worker thread.

        Every order is processed through the nested process_order trace.
        """

        thread = threading.current_thread()

        mta.info(
            "Customer processing started on worker",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            thread_name=thread.name,
            thread_id=thread.ident,
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_count=len(orders),
        )

        processed_orders = 0
        processed_order_codes: list[str] = []

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            order_code = order["order_code"]
            order_name = order["order_name"]

            result = process_order(
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
                order_code=order_code,
                order_name=order_name,
            )

            processed_order_code = result[
                "order_code"
            ]

            if not isinstance(
                processed_order_code,
                str,
            ):
                raise TypeError(
                    "process_order returned an invalid order_code."
                )

            processed_orders += 1

            processed_order_codes.append(
                processed_order_code
            )

        mta.info(
            "Customer processing completed on worker",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            thread_name=thread.name,
            thread_id=thread.ident,
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
            processed_order_codes=processed_order_codes,
        )

        return {
            "cust_nummer": cust_nummer,
            "cust_naam": cust_naam,
            "processed_orders": processed_orders,
            "processed_order_codes": processed_order_codes,
            "thread_name": thread.name,
            "thread_id": thread.ident,
        }

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Customer thread executor example started",
        example="main_customer_thread_executor",
        executor_name=EXECUTOR_NAME,
        executor_count=EXECUTOR_COUNT,
        customer_count=len(customers),
    )

    futures: dict[
        Future[dict[str, Any]],
        dict[str, Any],
    ] = {}

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
                "Submitting customer to executor",
                executor_name=EXECUTOR_NAME,
                executor_count=EXECUTOR_COUNT,
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
                order_count=len(orders),
            )

            future = executor.submit(
                process_customer,
                cust_nummer,
                cust_naam,
                orders,
            )

            futures[future] = {
                "cust_nummer": cust_nummer,
                "cust_naam": cust_naam,
            }

        mta.info(
            "All customers submitted",
            executor_name=EXECUTOR_NAME,
            executor_count=EXECUTOR_COUNT,
            submitted_customers=len(futures),
        )

        completed_customers = 0
        failed_customers = 0
        processed_orders = 0
        used_threads: set[str] = set()

        for future in as_completed(
            futures
        ):
            customer = futures[future]

            try:
                result = future.result()

            except Exception as exception:  # noqa: BLE001
                failed_customers += 1

                mta.error(
                    "Customer worker failed",
                    exception=exception,
                    executor_name=EXECUTOR_NAME,
                    executor_count=EXECUTOR_COUNT,
                    cust_nummer=customer["cust_nummer"],
                    cust_naam=customer["cust_naam"],
                )

            else:
                completed_customers += 1

                processed_order_count = result[
                    "processed_orders"
                ]

                worker_thread = result[
                    "thread_name"
                ]

                if not isinstance(
                    processed_order_count,
                    int,
                ):
                    raise TypeError(
                        "process_customer returned an invalid "
                        "processed_orders value."
                    )

                if not isinstance(
                    worker_thread,
                    str,
                ):
                    raise TypeError(
                        "process_customer returned an invalid "
                        "thread_name value."
                    )

                processed_orders += processed_order_count

                used_threads.add(
                    worker_thread
                )

                mta.info(
                    "Customer result received",
                    executor_name=EXECUTOR_NAME,
                    executor_count=EXECUTOR_COUNT,
                    completed_customers=completed_customers,
                    cust_nummer=result["cust_nummer"],
                    cust_naam=result["cust_naam"],
                    processed_orders=processed_order_count,
                    processed_order_codes=result[
                        "processed_order_codes"
                    ],
                    worker_thread=worker_thread,
                    worker_thread_id=result["thread_id"],
                )

    mta.info(
        "Customer thread executor example completed",
        example="main_customer_thread_executor",
        executor_name=EXECUTOR_NAME,
        executor_count=EXECUTOR_COUNT,
        submitted_customers=len(futures),
        completed_customers=completed_customers,
        failed_customers=failed_customers,
        processed_orders=processed_orders,
        used_thread_count=len(used_threads),
        used_threads=sorted(
            used_threads
        ),
    )

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    if completed_customers + failed_customers != len(
        futures
    ):
        raise AssertionError(
            "The customer result totals do not match the number "
            "of submitted customers."
        )

    if failed_customers:
        raise AssertionError(
            f"Expected no customer failures, got {failed_customers}."
        )

    if completed_customers != len(customers):
        raise AssertionError(
            f"Expected {len(customers)} completed customers, "
            f"got {completed_customers}."
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
        "=== Example completed: customer ThreadPoolExecutor ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - customer-level parallel processing\n"
        f"  - ThreadPoolExecutor with max_workers={EXECUTOR_COUNT}\n"
        "  - one root trace per customer\n"
        "  - nested order traces under each customer\n"
        "  - sequential order processing per customer\n"
        "  - multiple customers running concurrently\n"
        "  - thread names and IDs in structured logging\n"
        "  - customer results collected with as_completed()\n"
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
        "  customer-worker_0\n"
        "  customer-worker_1\n"
        "  customer-worker_2\n"
        "\n"
        "Expected trace hierarchy per customer:\n"
        "  process_customer\n"
        "    process_order\n"
        "    process_order\n"
        "    ...\n"
        "\n"
        "Expected call relationships:\n"
        "  process_customer:\n"
        "    call_id = W\n"
        "    parent_call_id = null\n"
        "\n"
        "  first process_order:\n"
        "    call_id = E1\n"
        "    parent_call_id = W\n"
        "\n"
        "  second process_order:\n"
        "    call_id = E2\n"
        "    parent_call_id = W\n"
        "\n"
        "Expected thread behaviour:\n"
        "  - each customer and its orders use the same worker thread\n"
        "  - different customers can run on different workers\n"
        "  - console output can be interleaved\n"
        "  - persisted records retain call and parent relationships\n"
        "\n"
        "Important:\n"
        "  Thread scheduling is controlled by Python and the operating\n"
        "  system. The exact customer-to-thread assignment can vary.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect interleaved nested customer traces\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()