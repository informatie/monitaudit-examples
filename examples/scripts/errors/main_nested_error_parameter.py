# examples/scripts/errors/main_nested_error_parameter.py

"""
MonitAudit nested-error parameter example using the customer dataset.

Purpose
-------
Demonstrates nested customer and order tracing with explicit parameters.

When an order fails:
- the order produces a function_error
- the error identifies both the customer and order
- the customer catches the order error
- the remaining orders in that customer are still processed
- after all orders have been attempted, the customer produces its own
  function_error
- the outer loop catches the customer error
- processing continues with the next customer

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
        cust_naam: str,
        order_code: str,
        order_name: str,
    ) -> None:
        if order_code == FAILING_ORDER:
            raise ValueError(
                f"Customer {cust_nummer} ({cust_naam}) - "
                f"order {order_code} ({order_name}) "
                "could not be processed"
            )

        # Simulate successful order processing.
        _ = order_name

    @mta.trace
    def process_customer(
        cust_nummer: int,
        cust_naam: str,
        orders: list[dict[str, Any]],
    ) -> None:
        mta.info(
            "Processing customer",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            order_count=len(orders),
        )

        processed_orders = 0
        failed_orders: list[dict[str, str]] = []

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            order_code = order["order_code"]
            order_name = order["order_name"]

            try:
                process_order(
                    cust_nummer=cust_nummer,
                    cust_naam=cust_naam,
                    order_code=order_code,
                    order_name=order_name,
                )

                processed_orders += 1

            except ValueError as exception:
                failed_orders.append(
                    {
                        "order_code": order_code,
                        "order_name": order_name,
                    }
                )

                mta.warning(
                    "Order processing failed; continuing customer",
                    cust_nummer=cust_nummer,
                    cust_naam=cust_naam,
                    order_code=order_code,
                    order_name=order_name,
                    error_type=type(exception).__name__,
                    error_message=str(exception),
                )

        mta.info(
            "All customer orders attempted",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            total_orders=len(orders),
            processed_orders=processed_orders,
            failed_order_count=len(failed_orders),
        )

        if failed_orders:
            failed_order_details = ", ".join(
                (
                    f"{order['order_code']} "
                    f"({order['order_name']})"
                )
                for order in failed_orders
            )

            raise RuntimeError(
                f"Customer {cust_nummer} ({cust_naam}) failed because "
                f"{len(failed_orders)} order(s) failed: "
                f"{failed_order_details}"
            )

        mta.info(
            "Customer completed successfully",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
        )

    mta.info(
        "Nested error parameter example started",
        example="main_nested_error_parameter",
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

        cust_nummer = customer["cust_nummer"]
        cust_naam = customer["cust_naam"]
        orders = customer["orders"]

        if not isinstance(orders, list):
            raise ValueError(
                f"Customer {cust_nummer!r} "
                "'orders' must be a list."
            )

        try:
            process_customer(
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
                orders=orders,
            )

            successful_customers += 1

        except RuntimeError as exception:
            failed_customers += 1

            mta.warning(
                "Customer processing failed; "
                "continuing with next customer",
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
                error_type=type(exception).__name__,
                error_message=str(exception),
            )

    mta.info(
        "Nested error parameter example completed",
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
        "=== Example completed: nested error parameter tracing ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - customer as parent traced function\n"
        "  - order as child traced function\n"
        "  - explicit customer and order trace parameters\n"
        "  - automatic trace parameter capture\n"
        f"  - deliberate child failure for {FAILING_ORDER}\n"
        "  - customer and order identification in errors\n"
        "  - remaining orders continue processing\n"
        "  - customer fails after all orders are attempted\n"
        "  - next customer continues processing\n"
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
        "Expected trace parameters:\n"
        "  process_customer:\n"
        "    - cust_nummer\n"
        "    - cust_naam\n"
        "    - orders\n"
        "\n"
        "  process_order:\n"
        "    - cust_nummer\n"
        "    - cust_naam\n"
        "    - order_code\n"
        "    - order_name\n"
        "\n"
        "Expected trace flow:\n"
        "  process_customer\n"
        "    process_order -> function_end\n"
        "    ...\n"
        f"    process_order {FAILING_ORDER} -> function_error\n"
        "    customer catches the order failure\n"
        "    remaining process_order calls continue\n"
        "  process_customer -> function_error\n"
        "  next process_customer starts\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect trace hierarchy\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()