# examples/scripts/sinks/main_console_sink.py

"""
MonitAudit ConsoleSink example.

Purpose
-------
Demonstrates MonitAudit's human-readable console output and, in particular,
the indentation produced by ConsoleSink for nested traced functions.

The example creates a three-level trace hierarchy:

    process_pipeline
        process_customer
            process_order

Normal mta.info() messages are also written inside each traced function.

This example is intentionally successful. No function_error events should
be produced.
"""

from __future__ import annotations

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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def process_order(
        customer: int,
        order_code: str,
        validate: bool = True,
    ) -> None:
        """
        Third trace level.

        Normal logging inside this function should appear one level below
        the process_order START/END trace records.
        """

        mta.info(
            "Order running",
            customer=customer,
            order_code=order_code,
            validate=validate,
        )

    @mta.trace
    def process_customer(
        customer: int,
    ) -> None:
        """
        Second trace level.
        """

        mta.info(
            "Customer running",
            customer=customer,
        )

        process_order(
            customer=customer,
            order_code="E001",
        )

        process_order(
            customer=customer,
            order_code="E002",
        )

        mta.info(
            "Customer completed",
            customer=customer,
        )

    @mta.trace
    def process_pipeline() -> None:
        """
        Root trace.
        """

        mta.info(
            "Pipeline running"
        )

        process_customer(
            customer=301,
        )

        mta.info(
            "Pipeline completed"
        )

    mta.info(
        "ConsoleSink example started",
        example="main_console_sink",
    )

    process_pipeline()

    mta.info(
        "ConsoleSink example completed",
        example="main_console_sink",
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: ConsoleSink ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - ConsoleSink output\n"
        "  - @mta.trace\n"
        "  - three-level nested tracing\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - trace indentation\n"
        "  - normal logging inside traces\n"
        "  - automatic parameter capture\n"
        "  - default parameter capture\n"
        "  - call_id\n"
        "  - parent_call_id\n"
        "  - duration_ms\n"
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
        "Expected trace hierarchy:\n"
        "  process_pipeline\n"
        "    process_customer\n"
        "      process_order E001\n"
        "      process_order E002\n"
        "\n"
        "Expected call relationships:\n"
        "  process_pipeline:\n"
        "    parent_call_id = null\n"
        "\n"
        "  process_customer:\n"
        "    parent_call_id = process_pipeline.call_id\n"
        "\n"
        "  process_order:\n"
        "    parent_call_id = process_customer.call_id\n"
        "\n"
        "Expected trace counts:\n"
        "  process_pipeline: start=1, end=1\n"
        "  process_customer: start=1, end=1\n"
        "  process_order:    start=2, end=2\n"
        "  function_error:   0\n"
        "\n"
        "Expected process_order parameters:\n"
        "  customer   = 301\n"
        "  order_code = E001 / E002\n"
        "  validate   = true\n"
        "\n"
        "Important:\n"
        "  START and END for the same traced function should have\n"
        "  the same indentation depth.\n"
        "\n"
        "  Normal logging inside the function should appear one\n"
        "  indentation level deeper.\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: inspect indentation and trace hierarchy above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()