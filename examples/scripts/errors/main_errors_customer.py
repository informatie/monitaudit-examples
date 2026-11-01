# examples/scripts/errors/main_nested_error.py

"""
MonitAudit nested-error example using the example customer dataset.

Purpose
-------
Demonstrates a nested traced order-processing call that fails while the
parent customer catches the exception, continues processing the remaining
orders, and eventually completes successfully.

The dataset is read from:

    data/example_dataset.yaml

This scenario is particularly useful for validating ConsoleSink depth state,
ContextVar restoration, call_id and parent_call_id handling.
"""

from __future__ import annotations

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
# Test configuration
# ---------------------------------------------------------------------------

# This order deliberately fails to demonstrate nested error handling.
FAILING_ORDER = "E005"


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
        order: dict[str, Any],
    ) -> None:
        order_code = order["order_code"]

        if order_code == FAILING_ORDER:
            raise ValueError(
                f"Order {order_code} could not be processed"
            )

        # Simulate successful order processing.
        _ = order["order_name"]

    @mta.trace
    def process_customer(
        customer: dict[str, Any],
    ) -> None:
        cust_nummer = customer["cust_nummer"]
        cust_naam = customer["cust_naam"]
        orders = customer["orders"]

        if not isinstance(orders, list):
            raise ValueError(
                f"Customer {cust_nummer!r} "
                "'orders' must be a list."
            )

        mta.info(
            "Processing customer",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_count=len(orders),
        )

        processed_orders = 0
        failed_orders = 0

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            try:
                process_order(
                    cust_nummer,
                    order,
                )

                processed_orders += 1

            except ValueError:
                failed_orders += 1

                mta.warning(
                    "Order processing failed",
                    cust_nummer=cust_nummer,
                    order_code=order["order_code"],
                )

        mta.info(
            "Customer completed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
            failed_orders=failed_orders,
        )

    mta.info(
        "Nested error example started",
        example="main_nested_error",
    )

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Dataset loaded",
        customer_count=len(customers),
    )

    for customer in customers:
        if not isinstance(customer, dict):
            raise ValueError(
                "Each customer must be a mapping."
            )

        process_customer(
            customer
        )

    mta.info(
        "Nested error example completed",
        customer_count=len(customers),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: nested error tracing ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - customer as parent traced function\n"
        "  - order as child traced function\n"
        f"  - deliberate child failure for {FAILING_ORDER}\n"
        "  - child function_error cleanup\n"
        "  - customer remains active after child failure\n"
        "  - remaining orders continue processing\n"
        "  - customer completes successfully\n"
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
        "Expected trace flow:\n"
        "  process_customer\n"
        "    process_order -> function_end\n"
        "    ...\n"
        f"    process_order {FAILING_ORDER} -> function_error\n"
        "    customer catches failure\n"
        "    process_order -> function_end\n"
        "  process_customer -> function_end\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect indentation and trace hierarchy above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()