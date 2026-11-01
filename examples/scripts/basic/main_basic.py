# examples/scripts/basic/main_basic.py

"""
Basic MonitAudit logging example.

Purpose
-------
Demonstrates the normal MonitAudit logging API without function tracing.

The example reads a small customer/order dataset from:

    data/example_dataset.yaml

The script processes each customer and then processes all orders belonging
to that customer. Individual orders are intentionally not logged.
"""

from __future__ import annotations

from typing import Any, cast

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
        data: Any = yaml.safe_load(file)

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

    return cast(
        dict[str, Any],
        data,
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
        example="main_basic",
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
            "Processing customer",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
        )

        processed_orders = 0

        for order in orders:
            if not isinstance(order, dict):
                raise ValueError(
                    f"Customer {cust_nummer!r} contains "
                    "an invalid order."
                )

            order_code = order["order_code"]
            order_name = order["order_name"]

            # Simulate actual order processing.
            # Individual orders are deliberately not logged.
            _ = order_code
            _ = order_name

            processed_orders += 1

        mta.info(
            "Customer completed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=processed_orders,
        )

    mta.warning(
        "Example warning",
        reason="This warning is generated intentionally",
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
        "=== Example completed: basic logging ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - reading the example dataset from YAML\n"
        "  - DEBUG, INFO and WARNING logging\n"
        "  - structured log attributes\n"
        "  - customer-level processing\n"
        "  - order processing without order-level logging\n"
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
        "  - Console: output above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()