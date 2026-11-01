# examples/scripts/tracing/main_trace.py

"""
MonitAudit tracing example.

Purpose
-------
Demonstrates how @mta.trace automatically records function execution and
builds a hierarchy using call_id and parent_call_id.

The example processes the customer/order dataset from:

    data/example_dataset.yaml

Each customer is processed by a traced parent function. Each order in the
customer is processed by a traced child function.

Unlike the error examples, every operation in this example completes
successfully.
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
from monitaudit.models.monitaudit import Monitaudit
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

def run_trace_example(
    mta: Monitaudit,
    dataset: dict[str, Any],
) -> None:
    @mta.trace
    def process_order(
        cust_nummer: int,
        order_code: str,
        order_name: str,
        validate: bool = True,
    ) -> None:
        # Simulate order processing.
        _ = cust_nummer
        _ = order_code
        _ = order_name
        _ = validate

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

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            process_order(
                cust_nummer=cust_nummer,
                order_code=order["order_code"],
                order_name=order["order_name"],
            )

        mta.info(
            "Customer completed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=len(orders),
        )

    customers = dataset["customers"]

    for customer in customers:
        if not isinstance(customer, dict):
            raise ValueError(
                "Each customer must be a mapping."
            )

        orders = customer["orders"]

        if not isinstance(orders, list):
            raise ValueError(
                f"Customer {customer['cust_nummer']!r} "
                "'orders' must be a list."
            )

        process_customer(
            cust_nummer=customer["cust_nummer"],
            cust_naam=customer["cust_naam"],
            orders=orders,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "Tracing example started",
        example="main_trace",
    )

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Dataset loaded",
        dataset_path=str(DATASET_PATH),
        customer_count=len(customers),
    )

    run_trace_example(
        mta=mta,
        dataset=dataset,
    )

    mta.info(
        "Tracing example completed",
        customer_count=len(customers),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: tracing ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - example-specific MonitAudit configuration\n"
        "  - example dataset loaded from YAML\n"
        "  - @mta.trace\n"
        "  - customer parent traces\n"
        "  - order child traces\n"
        "  - function_start and function_end events\n"
        "  - call_id and parent_call_id\n"
        "  - automatic parameter capture\n"
        "  - default parameter capture\n"
        "  - execution duration\n"
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
        "Where to look for the results:\n"
        "  - Console: inspect nested indentation above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
        "\n"
        "For each order trace inspect:\n"
        "  - call_id\n"
        "  - parent_call_id\n"
        "  - parameters\n"
        "  - duration_ms\n"
        "  - attributes.event\n"
    )


if __name__ == "__main__":
    main()
    print_summary()