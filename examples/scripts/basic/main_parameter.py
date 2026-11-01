# examples/scripts/parameters/main_parameter.py

"""
MonitAudit trace parameter example.

Purpose
-------
Demonstrates automatic function parameter capture with MonitAudit tracing.

The example reads customer and order data from:

    data/example_dataset.yaml
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
# Trace example
# ---------------------------------------------------------------------------

def run_parameter_example(
    mta: Any,
    customers: list[dict[str, Any]],
) -> None:
    @mta.trace
    def process_order(
        cust_nummer: int,
        order_name: str,
    ) -> None:
        mta.info(
            "Order running",
        )

    @mta.trace
    def process_customer(
        cust_nummer: int,
        orders: list[dict[str, Any]],
    ) -> None:
        mta.info(
            "Customer running",
        )

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            order_name = order.get(
                "order_name"
            )

            if order_name is None:
                order_name = order.get(
                    "order_code"
                )

            if order_name is None:
                raise ValueError(
                    f"Customer {cust_nummer!r} contains "
                    "an order without 'order_name' "
                    "or 'order_code'."
                )

            process_order(
                cust_nummer=cust_nummer,
                order_name=str(
                    order_name
                ),
            )

        mta.info(
            "Customer completed",
        )

    @mta.trace
    def process_pipeline(
        customers: list[dict[str, Any]],
    ) -> None:
        mta.info(
            "Pipeline running",
        )

        for customer in customers:
            if not isinstance(customer, dict):
                raise ValueError(
                    "Each customer must be a mapping."
                )

            cust_nummer = customer["cust_nummer"]
            orders = customer["orders"]

            if not isinstance(orders, list):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "'orders' must be a list."
                )

            process_customer(
                cust_nummer=cust_nummer,
                orders=orders,
            )

        mta.info(
            "Pipeline completed",
        )

    process_pipeline(
        customers=customers,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "Application started",
        example="main_parameter",
    )

    mta.debug(
        "Loading example dataset",
        dataset_path=str(DATASET_PATH),
    )

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Dataset loaded",
        customer_count=len(customers),
    )

    run_parameter_example(
        mta=mta,
        customers=customers,
    )

    mta.info(
        "Application completed",
        customer_count=len(customers),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: trace parameters ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - reading the example dataset from YAML\n"
        "  - nested MonitAudit tracing\n"
        "  - automatic parameter capture\n"
        "  - cust_nummer on process_customer\n"
        "  - cust_nummer and order_name on process_order\n"
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
        "Expected ConsoleSink parameters:\n"
        "  process_customer:\n"
        "    cust_nummer\n"
        "\n"
        "  process_order:\n"
        "    cust_nummer\n"
        "    order_name\n"
    )


if __name__ == "__main__":
    main()
    print_summary()

    