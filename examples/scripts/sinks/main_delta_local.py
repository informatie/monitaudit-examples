# examples/scripts/sinks/main_delta_local.py

"""
MonitAudit local DeltaSink example.

Purpose
-------
Demonstrates writing MonitAudit log records to a local Delta Lake destination.

The Delta table name and physical base path are configured in:

    examples/config/main_delta_local.yaml

The example does not duplicate those settings. After MonitAudit has been
constructed, the configured DeltaSink provides the logical table name and
physical local Delta path.

After writing, the example reads the Delta data back using the same Spark
session used by DeltaSink.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from main_load_config import (
    CONFIG_DIR,
    DATA_DIR,
    EXAMPLES_DIR,
    OUTPUT_DIR,
    SCRIPTS_DIR,
    get_config_path,
)
from monitaudit.sinks.delta import DeltaSink
from monitaudit.utilities.build_monitaudit import build_monitaudit


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_PATH = get_config_path(__file__)


# ---------------------------------------------------------------------------
# DeltaSink
# ---------------------------------------------------------------------------

def find_delta_sink(
    mta: Any,
) -> DeltaSink:
    """
    Return the configured DeltaSink.
    """

    for sink in mta.logger.sinks:
        if isinstance(
            sink,
            DeltaSink,
        ):
            return sink

    raise RuntimeError(
        "Configured DeltaSink was not found."
    )


def get_local_delta_path(
    delta_sink: DeltaSink,
) -> Path:
    """
    Return the physical path used by the local DeltaSink.
    """

    path = delta_sink.local_path

    if path is None:
        raise RuntimeError(
            "Configured DeltaSink does not expose a local path."
        )

    return Path(
        path
    ).resolve()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    delta_sink = find_delta_sink(
        mta
    )

    delta_table = delta_sink.table

    delta_path = get_local_delta_path(
        delta_sink
    )

    spark = delta_sink.spark

    print()
    print("Local DeltaSink configuration:")
    print(f"  config = {CONFIG_PATH}")
    print(f"  table  = {delta_table}")
    print(f"  path   = {delta_path}")
    print()

    mta.info(
        "Local DeltaSink example started",
        example="main_delta_local",
        delta_table=delta_table,
        delta_path=str(delta_path),
    )

    mta.info(
        "Structured local Delta record",
        customer=301,
        order_code="E001",
        status="processing",
    )

    @mta.trace
    def calculate(
        first: int,
        second: int,
        operation: str = "add",
    ) -> int:
        """
        Generate trace records that can be inspected in Delta.
        """

        mta.info(
            "Calculation running",
            first=first,
            second=second,
            operation=operation,
        )

        return first + second

    result = calculate(
        first=20,
        second=22,
    )

    mta.info(
        "Calculation result received",
        result=result,
    )

    mta.warning(
        "Example warning written to Delta",
        reason="Intentional demonstration warning",
    )

    mta.info(
        "Local DeltaSink example completed",
        example="main_delta_local",
    )

    # -----------------------------------------------------------------------
    # Verify local Delta destination
    # -----------------------------------------------------------------------

    if not delta_path.is_dir():
        raise FileNotFoundError(
            "Local Delta destination was not created: "
            f"{delta_path}"
        )

    delta_log_path = (
        delta_path
        / "_delta_log"
    )

    if not delta_log_path.is_dir():
        raise RuntimeError(
            "Local destination exists but is not a Delta table: "
            f"{delta_path}"
        )

    # -----------------------------------------------------------------------
    # Read Delta records
    # -----------------------------------------------------------------------

    dataframe = (
        spark.read
        .format("delta")
        .load(str(delta_path))
    )

    print()
    print("=" * 70)
    print("Local Delta records")
    print("=" * 70)
    print()
    print(f"Delta table : {delta_table}")
    print(f"Delta path  : {delta_path}")
    print()

    dataframe.orderBy(
        "timestamp"
    ).show(
        200,
        truncate=False,
    )

    record_count = dataframe.count()

    print()
    print("Local Delta verification:")
    print(f"  Delta table = {delta_table}")
    print(f"  Delta path  = {delta_path}")
    print(f"  Row count   = {record_count}")
    print()

    if record_count < 1:
        raise AssertionError(
            "No MonitAudit records were found "
            "in the local Delta destination."
        )

    # -----------------------------------------------------------------------
    # Trace verification
    # -----------------------------------------------------------------------

    trace_records = dataframe.filter(
        dataframe.function
        == "calculate"
    )

    print("Trace records for calculate():")
    print()

    trace_records.select(
        "timestamp",
        "level",
        "function",
        "call_id",
        "parent_call_id",
        "duration_ms",
        "parameters",
        "attributes",
        "message",
    ).orderBy(
        "timestamp"
    ).show(
        50,
        truncate=False,
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: local DeltaSink ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - local Spark session\n"
        "  - DeltaSink configuration from YAML\n"
        "  - logical Delta table from YAML\n"
        "  - physical Delta base path from YAML\n"
        "  - DeltaSink initialisation\n"
        "  - structured INFO records\n"
        "  - WARNING record\n"
        "  - @mta.trace\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - parameter storage\n"
        "  - call_id storage\n"
        "  - parent_call_id storage\n"
        "  - duration_ms storage\n"
        "  - Delta read-back verification\n"
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
        "Important:\n"
        "  The Delta table and physical path are not hard-coded in\n"
        "  this example. Both originate from the YAML configuration\n"
        "  and are exposed by the configured DeltaSink.\n"
        "\n"
        "Expected trace records:\n"
        "  calculate function_start\n"
        "    first     = 20\n"
        "    second    = 22\n"
        "    operation = add\n"
        "\n"
        "  calculate function_end\n"
        "    same call_id as function_start\n"
        "    duration_ms populated\n"
        "\n"
        "Expected errors:\n"
        "  function_error = 0\n"
    )


if __name__ == "__main__":
    main()
    print_summary()