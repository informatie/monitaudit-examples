# examples/scripts/errors/main_nested_customer_failure.py

"""
MonitAudit nested-error example using the example customer dataset.

Purpose
-------
Demonstrates nested order processing where an order may fail, while the
customer continues processing all remaining orders.

If one or more orders fail, the customer itself is marked as failed after
all its orders have been processed.

The dataset is read from:

    data/example_dataset.yaml

This example is intentionally synchronous.
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
                f"Order {order_code} in customer "
                f"{cust_nummer} could not be processed"
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
        failed_orders: list[str] = []

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

            except ValueError as exception:
                order_code = order["order_code"]

                failed_orders.append(
                    order_code
                )

                mta.warning(
                    "Order processing failed",
                    cust_nummer=cust_nummer,
                    cust_naam=cust_naam,
                    order_code=order_code,
                    error_type=type(exception).__name__,
                    error_message=str(exception),
                )

        mta.info(
            "Customer orders processed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
            failed_order_count=len(failed_orders),
        )

        # Every order has now been attempted.
        #
        # If one or more orders failed, fail the customer itself.
        # Because process_customer is traced, MonitAudit generates a
        # function_error for this customer.
        if failed_orders:
            raise RuntimeError(
                f"Customer {cust_nummer} failed because "
                f"{len(failed_orders)} order(s) failed: "
                f"{', '.join(failed_orders)}"
            )

        mta.info(
            "Customer completed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
        )

    mta.info(
        "Nested customer failure example started",
        example="main_nested_customer_failure",
    )

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Dataset loaded",
        dataset_path=str(DATASET_PATH),
        customer_count=len(customers),
    )

    successful_customers = 0
    failed_customers = 0

    for customer in customers:
        if not isinstance(customer, dict):
            raise ValueError(
                "Each customer must be a mapping."
            )

        try:
            process_customer(
                customer
            )

            successful_customers += 1

        except RuntimeError as exception:
            failed_customers += 1

            mta.warning(
                "Customer processing failed; "
                "continuing with next customer",
                cust_nummer=customer["cust_nummer"],
                cust_naam=customer["cust_naam"],
                error_type=type(exception).__name__,
                error_message=str(exception),
            )

    mta.info(
        "Nested customer failure example completed",
        customer_count=len(customers),
        successful_customers=successful_customers,
        failed_customers=failed_customers,
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: nested customer failure ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - customer as parent traced function\n"
        "  - order as child traced function\n"
        f"  - deliberate child failure for {FAILING_ORDER}\n"
        "  - failed order produces function_error\n"
        "  - remaining orders continue processing\n"
        "  - customer remembers order failures\n"
        "  - customer produces function_error afterwards\n"
        "  - next customer is still processed\n"
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
        "    order failure is caught\n"
        "    remaining process_order calls continue\n"
        "  process_customer -> function_error\n"
        "  next process_customer starts\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect indentation and trace hierarchy\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()