# examples/scripts/sinks/main_query_delta.py

"""
MonitAudit local Delta query example.

Purpose
-------
Reads an existing local MonitAudit Delta destination and makes it available
as a temporary Spark SQL view.

The example provides several predefined queries for inspecting MonitAudit
records written by the local DeltaSink.
"""

from __future__ import annotations

from pathlib import Path

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

from main_load_config import (
    CONFIG_DIR,
    DATA_DIR,
    EXAMPLES_DIR,
    OUTPUT_DIR,
    SCRIPTS_DIR,
)


# ---------------------------------------------------------------------------
# Delta
# ---------------------------------------------------------------------------

DELTA_TABLE = "main.logging.delta_local"

DELTA_PATH = EXAMPLES_DIR / Path(
    DELTA_TABLE.replace(
        ".",
        "/",
    )
)

VIEW_NAME = "monitaudit_logs"


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

QUERIES = [
    """
    SELECT
        message,
        error_message
    FROM monitaudit_logs
    LIMIT 20
    """,
    """
    SELECT
        COUNT(*) AS record_count
    FROM monitaudit_logs
    """,
    """
    SELECT
        message,
        application
    FROM monitaudit_logs
    LIMIT 20
    """,
]


# Select query using a zero-based index.
QUERY_INDEX = 0


# ---------------------------------------------------------------------------
# Spark
# ---------------------------------------------------------------------------

def create_spark() -> SparkSession:
    builder = (
        SparkSession.builder
        .appName("monitaudit-query-delta")
        .master("local[*]")
        .config(
            "spark.sql.extensions",
            "io.delta.sql.DeltaSparkSessionExtension",
        )
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )

    return configure_spark_with_delta_pip(
        builder
    ).getOrCreate()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("MonitAudit Delta query")
    print("=" * 70)
    print()
    print(f"Examples   : {EXAMPLES_DIR}")
    print(f"Config     : {CONFIG_DIR}")
    print(f"Data       : {DATA_DIR}")
    print(f"Scripts    : {SCRIPTS_DIR}")
    print(f"Output     : {OUTPUT_DIR}")
    print()
    print(f"Delta table: {DELTA_TABLE}")
    print(f"Delta path : {DELTA_PATH}")
    print(f"SQL view   : {VIEW_NAME}")
    print(f"Query      : {QUERY_INDEX + 1}")
    print()

    if not DELTA_PATH.exists():
        raise FileNotFoundError(
            "MonitAudit Delta destination does not exist: "
            f"{DELTA_PATH}"
        )

    delta_log = DELTA_PATH / "_delta_log"

    if not delta_log.is_dir():
        raise RuntimeError(
            "Path exists but is not a Delta table: "
            f"{DELTA_PATH}"
        )

    if not 0 <= QUERY_INDEX < len(QUERIES):
        raise ValueError(
            "QUERY_INDEX must be between 0 and "
            f"{len(QUERIES) - 1}: {QUERY_INDEX}"
        )

    spark = create_spark()

    try:
        dataframe = (
            spark.read
            .format("delta")
            .load(str(DELTA_PATH))
        )

        print("=== MonitAudit Delta schema ===")
        print()

        dataframe.printSchema()

        dataframe.createOrReplaceTempView(
            VIEW_NAME
        )

        query = QUERIES[
            QUERY_INDEX
        ].strip()

        print()
        print(
            f"=== SQL query {QUERY_INDEX + 1} ==="
        )
        print()
        print(query)
        print()

        spark.sql(
            query
        ).show(
            n=20,
            truncate=False,
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()