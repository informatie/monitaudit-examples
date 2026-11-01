# examples/scripts/redaction/main_redaction.py

"""
MonitAudit sensitive-parameters redaction example.

Purpose
-------
Demonstrates sensitive parameter redaction while processing the customer
and order example dataset.

The dataset is loaded from:

    data/example_dataset.yaml

Each customer and its orders are processed normally. During order
processing, example credentials are passed to a traced function to
demonstrate that sensitive values are redacted before trace parameters are
written to the configured MonitAudit sinks.

The traced function itself still receives the original values.
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
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def process_order(
        cust_nummer: int,
        order_code: str,
        order_name: str,
        database_password: str,
        access_token: str,
        config: dict[str, Any],
    ) -> None:
        """
        Process one order using example credentials.

        The original credential values remain available to the function.
        MonitAudit only redacts the captured representation written to sinks.
        """

        assert database_password == "example-password"
        assert access_token == "example-access-token"

        assert (
            config["client_secret"]
            == "example-client-secret"
        )

        credentials = config["credentials"]

        if not isinstance(
            credentials,
            dict,
        ):
            raise ValueError(
                "Example credentials must be a mapping."
            )

        assert (
            credentials["password"]
            == "nested-password"
        )

        # Non-sensitive values remain available as normal.
        assert config["timeout"] == 30

        # Simulate order processing.
        _ = cust_nummer
        _ = order_code
        _ = order_name

    mta.info(
        "Redaction example started",
        example="main_redaction",
    )

    dataset = load_dataset()
    customers = dataset["customers"]

    mta.info(
        "Dataset loaded",
        dataset_path=str(DATASET_PATH),
        customer_count=len(customers),
    )

    for customer in customers:
        if not isinstance(
            customer,
            dict,
        ):
            raise ValueError(
                "Each customer must be a mapping."
            )

        cust_nummer = customer["cust_nummer"]
        cust_naam = customer["cust_naam"]
        orders = customer["orders"]

        if not isinstance(
            orders,
            list,
        ):
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

        for order in orders:
            if not isinstance(
                order,
                dict,
            ):
                raise ValueError(
                    f"Customer {cust_nummer!r} "
                    "contains an invalid order."
                )

            process_order(
                cust_nummer=cust_nummer,
                order_code=order["order_code"],
                order_name=order["order_name"],
                database_password="example-password",
                access_token="example-access-token",
                config={
                    "client_secret": "example-client-secret",
                    "timeout": 30,
                    "credentials": {
                        "username": "example-user",
                        "password": "nested-password",
                    },
                },
            )

        mta.info(
            "Customer completed",
            cust_nummer=cust_nummer,
            cust_naam=cust_naam,
            processed_orders=len(orders),
        )

    mta.info(
        "Redaction example completed",
        example="main_redaction",
        customer_count=len(customers),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: sensitive parameter redaction ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - customer and order dataset processing\n"
        "  - order processing with @mta.trace\n"
        "  - sensitive trace parameter redaction\n"
        "  - password redaction\n"
        "  - token redaction\n"
        "  - client_secret redaction\n"
        "  - nested dictionary redaction\n"
        "  - non-sensitive parameters remain visible\n"
        "  - traced function receives original values\n"
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
        "Expected visible trace parameters:\n"
        "  cust_nummer = normal value\n"
        "  order_code  = normal value\n"
        "  order_name  = normal value\n"
        "  timeout     = 30\n"
        "  username    = example-user\n"
        "\n"
        "Expected redacted trace parameters:\n"
        '  database_password = "***"\n'
        '  access_token      = "***"\n'
        '  client_secret     = "***"\n'
        '  password          = "***"\n'
        "\n"
        "Important:\n"
        "  Redaction affects captured trace parameters only.\n"
        "  The Python function receives the original values.\n"
        "\n"
        "  Sensitive values must not be manually included in log\n"
        "  messages or exception messages.\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect trace output above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()