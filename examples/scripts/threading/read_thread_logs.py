# examples/scripts/threading/main_thread_logs.py

"""
MonitAudit workspace-thread log analysis example.

Purpose
-------
Analyses the JSONL output produced by the workspace ThreadPoolExecutor
example using Spark SQL.

The queries inspect worker-thread usage, workspace distribution, trace
lifecycle health, call_id relationships and parent_call_id relationships.
"""

from __future__ import annotations

from pyspark.sql import SparkSession

from main_load_config import (
    CONFIG_DIR,
    DATA_DIR,
    EXAMPLES_DIR,
    OUTPUT_DIR,
    SCRIPTS_DIR,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

LOG_PATH = (
    OUTPUT_DIR
    / "main_workspace_thread_executor.jsonl"
)

VIEW_NAME = "monitaudit_logs"


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

QUERIES: tuple[
    tuple[str, str],
    ...,
] = (
    (
        "Complete chronological log",
        """
        SELECT
            timestamp,
            level,
            function,
            call_id,
            parent_call_id,
            attributes.ws_nummer AS ws_nummer,
            attributes.element_code AS element_code,
            attributes.thread_name AS thread_name,
            attributes.thread_id AS thread_id,
            attributes.event AS event,
            message
        FROM monitaudit_logs
        ORDER BY timestamp
        """,
    ),
    (
        "Worker threads used",
        """
        SELECT DISTINCT
            attributes.thread_name AS thread_name,
            attributes.thread_id AS thread_id
        FROM monitaudit_logs
        WHERE attributes.thread_name IS NOT NULL
        ORDER BY thread_name
        """,
    ),
    (
        "Thread-to-workspace distribution",
        """
        SELECT
            attributes.thread_name AS thread_name,
            attributes.thread_id AS thread_id,

            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) AS ws_nummer,

            COUNT(*) AS log_count,
            MIN(timestamp) AS first_log,
            MAX(timestamp) AS last_log

        FROM monitaudit_logs

        WHERE
            attributes.thread_name IS NOT NULL

            AND COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) IS NOT NULL

        GROUP BY
            attributes.thread_name,
            attributes.thread_id,

            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            )

        ORDER BY
            thread_name,
            ws_nummer
        """,
    ),
    (
        "Detailed thread/workspace debugging",
        """
        SELECT
            attributes.thread_name AS thread_name,

            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) AS ws_nummer,

            timestamp,
            function,
            attributes.event AS event,
            parameters.element_code AS element_code,
            call_id,
            parent_call_id,
            message

        FROM monitaudit_logs

        WHERE
            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) IS NOT NULL

        ORDER BY
            thread_name,
            ws_nummer,
            timestamp
        """,
    ),
    (
        "Counts by thread, workspace, function and event",
        """
        SELECT
            attributes.thread_name AS thread_name,
            attributes.thread_id AS thread_id,

            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) AS ws_nummer,

            function,

            COALESCE(
                attributes.event,
                'log'
            ) AS event,

            COUNT(*) AS log_count,
            MIN(timestamp) AS first_log,
            MAX(timestamp) AS last_log

        FROM monitaudit_logs

        WHERE
            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) IS NOT NULL

        GROUP BY
            attributes.thread_name,
            attributes.thread_id,

            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ),

            function,

            COALESCE(
                attributes.event,
                'log'
            )

        ORDER BY
            thread_name,
            ws_nummer,
            function,
            event
        """,
    ),
    (
        "Trace lifecycle counts",
        """
        SELECT
            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ) AS ws_nummer,

            function,
            attributes.event AS event,
            COUNT(*) AS event_count

        FROM monitaudit_logs

        WHERE
            attributes.event IN (
                'function_start',
                'function_end',
                'function_error'
            )

        GROUP BY
            COALESCE(
                attributes.ws_nummer,
                parameters.ws_nummer
            ),

            function,
            attributes.event

        ORDER BY
            ws_nummer,
            function,
            event
        """,
    ),
    (
        "Trace-health summary",
        """
        SELECT
            COALESCE(
                parameters.ws_nummer,
                attributes.ws_nummer
            ) AS ws_nummer,

            function,

            SUM(
                CASE
                    WHEN attributes.event = 'function_start'
                    THEN 1
                    ELSE 0
                END
            ) AS starts,

            SUM(
                CASE
                    WHEN attributes.event = 'function_end'
                    THEN 1
                    ELSE 0
                END
            ) AS ends,

            SUM(
                CASE
                    WHEN attributes.event = 'function_error'
                    THEN 1
                    ELSE 0
                END
            ) AS errors

        FROM monitaudit_logs

        WHERE
            function IN (
                'process_workspace',
                'process_element'
            )

            AND attributes.event IN (
                'function_start',
                'function_end',
                'function_error'
            )

        GROUP BY
            COALESCE(
                parameters.ws_nummer,
                attributes.ws_nummer
            ),
            function

        ORDER BY
            ws_nummer,
            function
        """,
    ),
    (
        "Broken parent_call_id relationships",
        """
        WITH workspace_calls AS (
            SELECT
                parameters.ws_nummer AS ws_nummer,
                call_id AS workspace_call_id

            FROM monitaudit_logs

            WHERE
                function = 'process_workspace'
                AND attributes.event = 'function_start'
        ),

        element_calls AS (
            SELECT
                parameters.ws_nummer AS ws_nummer,
                parameters.element_code AS element_code,
                call_id AS element_call_id,
                parent_call_id

            FROM monitaudit_logs

            WHERE
                function = 'process_element'
                AND attributes.event = 'function_start'
        )

        SELECT
            element.ws_nummer,
            element.element_code,
            element.element_call_id,
            element.parent_call_id,
            workspace.workspace_call_id

        FROM element_calls AS element

        INNER JOIN workspace_calls AS workspace
            ON element.ws_nummer = workspace.ws_nummer

        WHERE
            element.parent_call_id
            <> workspace.workspace_call_id

        ORDER BY
            element.ws_nummer,
            element.element_code
        """,
    ),
    (
        "Element-to-workspace hierarchy",
        """
        WITH workspace_calls AS (
            SELECT
                parameters.ws_nummer AS ws_nummer,
                call_id AS workspace_call_id

            FROM monitaudit_logs

            WHERE
                function = 'process_workspace'
                AND attributes.event = 'function_start'
        ),

        element_calls AS (
            SELECT
                parameters.ws_nummer AS ws_nummer,
                parameters.element_code AS element_code,
                call_id AS element_call_id,
                parent_call_id AS element_parent_call_id

            FROM monitaudit_logs

            WHERE
                function = 'process_element'
                AND attributes.event = 'function_start'
        )

        SELECT
            element.ws_nummer,
            element.element_code,
            workspace.workspace_call_id,
            element.element_call_id,
            element.element_parent_call_id,

            CASE
                WHEN element.element_parent_call_id
                     = workspace.workspace_call_id
                THEN 'OK'
                ELSE 'INVALID'
            END AS parent_relationship

        FROM element_calls AS element

        INNER JOIN workspace_calls AS workspace
            ON element.ws_nummer = workspace.ws_nummer

        ORDER BY
            element.ws_nummer,
            element.element_code
        """,
    ),
    (
        "Workspace root call IDs",
        """
        SELECT
            parameters.ws_nummer AS ws_nummer,
            call_id AS workspace_call_id,
            parent_call_id

        FROM monitaudit_logs

        WHERE
            function = 'process_workspace'
            AND attributes.event = 'function_start'

        ORDER BY
            ws_nummer
        """,
    ),
    (
        "Detect workspace call_id reuse",
        """
        SELECT
            call_id AS workspace_call_id,

            COUNT(
                DISTINCT parameters.ws_nummer
            ) AS workspace_count

        FROM monitaudit_logs

        WHERE
            function = 'process_workspace'
            AND attributes.event = 'function_start'

        GROUP BY
            call_id

        HAVING
            COUNT(
                DISTINCT parameters.ws_nummer
            ) > 1

        ORDER BY
            workspace_call_id
        """,
    ),
    (
        "Thread/workspace execution matrix",
        """
        SELECT
            attributes.thread_name AS thread_name,
            attributes.thread_id AS thread_id,

            COUNT(
                DISTINCT COALESCE(
                    attributes.ws_nummer,
                    parameters.ws_nummer
                )
            ) AS workspace_count,

            COUNT(*) AS log_count

        FROM monitaudit_logs

        WHERE
            attributes.thread_name IS NOT NULL

        GROUP BY
            attributes.thread_name,
            attributes.thread_id

        ORDER BY
            thread_name
        """,
    ),
)


# ---------------------------------------------------------------------------
# Spark
# ---------------------------------------------------------------------------

def create_spark() -> SparkSession:
    return (
        SparkSession.builder
        .appName(
            "monitaudit-thread-log-analysis"
        )
        .master(
            "local[*]"
        )
        .getOrCreate()
    )


# ---------------------------------------------------------------------------
# Query execution
# ---------------------------------------------------------------------------

def run_queries(
    spark: SparkSession,
) -> None:
    for index, (
        title,
        query,
    ) in enumerate(
        QUERIES,
        start=1,
    ):
        print()
        print("=" * 80)
        print(
            f"Query {index:02d}: {title}"
        )
        print("=" * 80)
        print()

        spark.sql(
            query.strip()
        ).show(
            200,
            truncate=False,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("MONITAUDIT THREAD LOG ANALYSIS")
    print("=" * 80)
    print()
    print(f"Examples : {EXAMPLES_DIR}")
    print(f"Config   : {CONFIG_DIR}")
    print(f"Data     : {DATA_DIR}")
    print(f"Scripts  : {SCRIPTS_DIR}")
    print(f"Output   : {OUTPUT_DIR}")
    print()
    print(f"Log file : {LOG_PATH}")
    print(f"SQL view : {VIEW_NAME}")
    print(f"Queries  : {len(QUERIES)}")
    print()

    if not LOG_PATH.is_file():
        raise FileNotFoundError(
            "Workspace thread JSONL log not found: "
            f"{LOG_PATH}"
        )

    if LOG_PATH.stat().st_size == 0:
        raise ValueError(
            "Workspace thread JSONL log is empty: "
            f"{LOG_PATH}"
        )

    spark = create_spark()

    try:
        logs = spark.read.json(
            str(LOG_PATH)
        )

        if not logs.columns:
            raise ValueError(
                "No columns were found in the JSONL log: "
                f"{LOG_PATH}"
            )

        logs.createOrReplaceTempView(
            VIEW_NAME
        )

        print("Schema:")
        print()

        logs.printSchema()

        record_count = logs.count()

        print()
        print(
            f"Records : {record_count}"
        )

        if record_count < 1:
            raise ValueError(
                "No records were found in the JSONL log: "
                f"{LOG_PATH}"
            )

        run_queries(
            spark
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()