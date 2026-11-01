# examples/scripts/sinks/main_delta_databricks.py

"""
MonitAudit Databricks DeltaSink example.

Purpose
-------
Demonstrates writing MonitAudit records to a managed Delta table on
Databricks.

The example writes normal log records, nested trace records and one handled
ERROR record. It then queries the configured Delta table and displays only
records belonging to the current correlation_id.

This example is intended to run inside Databricks.
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
# Delta
# ---------------------------------------------------------------------------

DELTA_TABLE = "main.logging.delta_databricks"


def quote_identifier(
    value: str,
) -> str:
    """
    Quote a Spark SQL identifier.
    """

    return f"`{value.replace('`', '``')}`"


def quote_string(
    value: str,
) -> str:
    """
    Quote a Spark SQL string value.
    """

    return value.replace(
        "'",
        "''",
    )


def qualified_table_name(
    table: str,
) -> str:
    """
    Quote each part of a catalog.schema.table name.
    """

    parts = table.split(".")

    if len(parts) != 3:
        raise ValueError(
            "Delta table must use catalog.schema.table format: "
            f"{table}"
        )

    return ".".join(
        quote_identifier(part)
        for part in parts
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "Databricks DeltaSink example started",
        example="main_delta_databricks",
        delta_table=DELTA_TABLE,
    )

    mta.info(
        "Structured Databricks Delta record",
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
        Generate trace records for inspection in the Delta table.
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

    try:
        raise RuntimeError(
            "Databricks DeltaSink demonstration failure"
        )

    except RuntimeError as exception:
        mta.error(
            "Demonstration error captured",
            exception=exception,
            component="main_delta_databricks",
        )

    mta.warning(
        "Example warning written to Databricks Delta",
        reason="Intentional demonstration warning",
    )

    mta.info(
        "Databricks DeltaSink example completed",
        example="main_delta_databricks",
    )

    delta_sink = next(
        (
            sink
            for sink in mta.logger.sinks
            if getattr(
                sink,
                "table",
                None,
            )
            == DELTA_TABLE
        ),
        None,
    )

    if delta_sink is None:
        raise RuntimeError(
            "Configured Databricks DeltaSink was not found "
            f"for table: {DELTA_TABLE}"
        )

    spark = getattr(
        delta_sink,
        "spark",
        None,
    )

    if spark is None:
        raise RuntimeError(
            "Configured Databricks DeltaSink does not expose "
            "a Spark session."
        )

    correlation_id = str(
        mta.correlation_id
    )

    table_name = qualified_table_name(
        DELTA_TABLE
    )

    escaped_correlation_id = quote_string(
        correlation_id
    )

    dataframe = spark.sql(
        f"""
        SELECT
            timestamp,
            level,
            message,
            application,
            environment,
            correlation_id,
            run_id,
            call_id,
            parent_call_id,
            duration_ms,
            module,
            function,
            parameters,
            attributes,
            error_type,
            error_message,
            traceback
        FROM {table_name}
        WHERE correlation_id = '{escaped_correlation_id}'
        ORDER BY timestamp
        """
    )

    print()
    print("=" * 70)
    print("Databricks MonitAudit records")
    print("=" * 70)
    print()
    print(f"Table          : {DELTA_TABLE}")
    print(f"Correlation ID : {correlation_id}")
    print()

    dataframe.show(
        200,
        truncate=False,
    )

    record_count = dataframe.count()

    if record_count < 1:
        raise AssertionError(
            "No MonitAudit records were found for the current "
            "correlation_id."
        )

    trace_records = dataframe.filter(
        dataframe.function
        == "calculate"
    )

    print()
    print("calculate() trace records:")
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

    error_records = dataframe.filter(
        dataframe.level
        == "ERROR"
    )

    print()
    print("ERROR records:")
    print()

    error_records.select(
        "timestamp",
        "message",
        "error_type",
        "error_message",
        "traceback",
    ).orderBy(
        "timestamp"
    ).show(
        50,
        truncate=False,
    )

    print()
    print("Databricks Delta verification:")
    print(f"  table          = {DELTA_TABLE}")
    print(f"  correlation_id = {correlation_id}")
    print(f"  records        = {record_count}")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: Databricks DeltaSink ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - Databricks Spark session\n"
        "  - DeltaSink Databricks mode\n"
        "  - catalogue.schema.table addressing\n"
        "  - managed Delta table writes\n"
        "  - structured INFO records\n"
        "  - WARNING record\n"
        "  - @mta.trace\n"
        "  - function_start and function_end\n"
        "  - automatic parameter capture\n"
        "  - default parameter capture\n"
        "  - call_id and parent_call_id\n"
        "  - duration_ms\n"
        "  - ERROR record\n"
        "  - error_type and error_message\n"
        "  - traceback\n"
        "  - Spark SQL read-back\n"
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
        "Delta table:\n"
        f"  {DELTA_TABLE}\n"
        "\n"
        "Expected calculate trace:\n"
        "  first     = 20\n"
        "  second    = 22\n"
        "  operation = add\n"
        "  result    = 42\n"
        "\n"
        "Expected error record:\n"
        "  level         = ERROR\n"
        "  error_type    = RuntimeError\n"
        "  error_message = Databricks DeltaSink demonstration failure\n"
        "  traceback     = populated\n"
        "\n"
        "Important:\n"
        "  The query filters the Delta table using the current\n"
        "  correlation_id so records from earlier executions are\n"
        "  excluded from this verification.\n"
    )


if __name__ == "__main__":
    main()
    print_summary()