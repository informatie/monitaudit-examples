# examples/scripts/errors/main_stacktrace.py

"""
MonitAudit CRITICAL stack-trace example.

Purpose
-------
Demonstrates how MonitAudit records one severe application failure as a
CRITICAL log including the full Python traceback.

The example uses the customer/order dataset from:

    data/example_dataset.yaml

The application processes customers and their orders. A specific order
deliberately raises an exception. The exception propagates to the application
boundary, where exactly one CRITICAL log is created.

This example deliberately does not use @mta.trace for the failing operation.
"""

from __future__ import annotations

import traceback
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

FAILING_CUSTOMER = 303
FAILING_ORDER = "E007"


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
# Exception serialisation
# ---------------------------------------------------------------------------

def serialize_exception(
    exception: BaseException,
) -> dict[str, str]:
    """
    Convert an exception and its complete traceback into strings.

    The original exception object is not included in the returned
    dictionary. All returned values are JSON-safe strings.
    """

    traceback_text = "".join(
        traceback.format_exception(
            type(exception),
            exception,
            exception.__traceback__,
        )
    )

    return {
        "error_type": type(exception).__name__,
        "error_message": str(exception),
        "traceback": traceback_text,
    }


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------

def process_order(
    cust_nummer: int,
    order_code: str,
    order_name: str,
) -> None:
    if (
        cust_nummer == FAILING_CUSTOMER
        and order_code == FAILING_ORDER
    ):
        raise RuntimeError(
            f"Order {order_code} in customer "
            f"{cust_nummer} could not be processed"
        )

    # Simulate normal order processing.
    _ = order_name


def process_customer(
    customer: dict[str, Any],
) -> None:
    cust_nummer = customer["cust_nummer"]
    orders = customer["orders"]

    if not isinstance(orders, list):
        raise ValueError(
            f"Customer {cust_nummer!r} "
            "'orders' must be a list."
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "Stack-trace example started",
        example="main_stacktrace",
    )

    try:
        dataset = load_dataset()
        customers = dataset["customers"]

        mta.info(
            "Dataset loaded",
            dataset_path=str(DATASET_PATH),
            customer_count=len(customers),
        )

        for customer in customers:
            if not isinstance(customer, dict):
                raise ValueError(
                    "Each customer must be a mapping."
                )

            cust_nummer = customer["cust_nummer"]
            cust_naam = customer["cust_naam"]

            mta.info(
                "Processing customer",
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
            )

            process_customer(
                customer
            )

            mta.info(
                "Customer completed",
                cust_nummer=cust_nummer,
                cust_naam=cust_naam,
            )

    except RuntimeError as exception:
        error = serialize_exception(
            exception
        )

        mta.critical(
            "Application cannot continue",
            exception=exception,
            component="order_processing",
            cust_nummer=FAILING_CUSTOMER,
            order_code=FAILING_ORDER,
            error_type=error["error_type"],
            error_message=error["error_message"],
            traceback=error["traceback"],
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: CRITICAL stack trace ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - dataset loaded from YAML\n"
        "  - customers processed sequentially\n"
        "  - orders processed without @mta.trace\n"
        f"  - {FAILING_ORDER} in customer "
        f"{FAILING_CUSTOMER} raises RuntimeError\n"
        "  - exception propagates to application boundary\n"
        "  - one CRITICAL log records the failure\n"
        "  - error_type serialised\n"
        "  - error_message serialised\n"
        "  - full traceback serialised\n"
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
        "Expected failure:\n"
        "  level         = CRITICAL\n"
        "  error_type    = RuntimeError\n"
        f"  error_message = Order {FAILING_ORDER} in customer "
        f"{FAILING_CUSTOMER} could not be processed\n"
        "  traceback     = complete Python traceback\n"
        "\n"
        "Expected traceback chain:\n"
        "  main()\n"
        "    process_customer()\n"
        "      process_order()\n"
        "        RuntimeError\n"
        "\n"
        "Expected processing:\n"
        "  customer 301 -> completed\n"
        "  customer 302 -> completed\n"
        f"  customer {FAILING_CUSTOMER} -> "
        f"{FAILING_ORDER} fails\n"
        "  application processing stops\n"
        "  CRITICAL record is written\n"
        "\n"
        "Important:\n"
        "  process_customer() and process_order() deliberately do not\n"
        "  use @mta.trace, so this failure is logged at the application\n"
        "  boundary rather than as an automatic function_error.\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect the CRITICAL record\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()