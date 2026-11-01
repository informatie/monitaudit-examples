# examples/scripts/basic/main_all.py

"""
Complete MonitAudit demonstration.

Purpose
-------
Provides one manual acceptance example covering the major MonitAudit features
that are currently implemented.

This example combines normal logging, nested tracing, automatic parameter
capture, sensitive-data redaction, return values and handled failures.
"""

from __future__ import annotations

from typing import Any

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


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def run_demo(
    mta: Monitaudit,
) -> None:
    @mta.trace
    def authenticate(
        username: str,
        password: str,
        access_token: str,
    ) -> None:
        assert password == "secret-password"
        assert access_token == "secret-token"

        mta.info(
            "User authenticated",
            username=username,
        )

    @mta.trace
    def check_database(
        database: str,
        database_password: str,
        options: dict[str, Any],
        timeout: int = 30,
    ) -> int:
        assert database_password == "database-secret"
        assert timeout == 30

        assert (
            options["client_secret"]
            == "nested-secret"
        )

        connection = options["connection"]

        if not isinstance(
            connection,
            dict,
        ):
            raise ValueError(
                "Database connection options must be a mapping."
            )

        assert (
            connection["access_token"]
            == "nested-token"
        )

        mta.info(
            "Executing database check",
            database=database,
            timeout=timeout,
        )

        return 42

    @mta.trace
    def validate_result(
        row_count: int,
    ) -> None:
        mta.info(
            "Validating query result",
            row_count=row_count,
        )

        if row_count < 1:
            raise ValueError(
                "Query returned no records"
            )

    @mta.trace
    def failing_operation(
        operation_id: int,
    ) -> None:
        mta.info(
            "Executing operation",
            operation_id=operation_id,
        )

        raise RuntimeError(
            f"Operation {operation_id} failed"
        )

    @mta.trace
    def process() -> None:
        mta.info(
            "Process started"
        )

        authenticate(
            username="service_account",
            password="secret-password",
            access_token="secret-token",
        )

        row_count = check_database(
            database="oracle",
            database_password="database-secret",
            options={
                "retry": 3,
                "client_secret": "nested-secret",
                "connection": {
                    "host": "database01",
                    "access_token": "nested-token",
                },
            },
        )

        validate_result(
            row_count
        )

        mta.info(
            "Database query completed",
            row_count=row_count,
        )

        try:
            failing_operation(
                operation_id=123,
            )

        except RuntimeError as exception:
            mta.warning(
                "Expected demonstration failure handled",
                operation_id=123,
                error_type=type(exception).__name__,
                error_message=str(exception),
            )

        mta.info(
            "Process completed"
        )

    process()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "MonitAudit demonstration started",
        example="main_all",
        config_path=str(CONFIG_PATH),
    )

    run_demo(
        mta
    )

    mta.info(
        "MonitAudit demonstration completed",
        example="main_all",
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: complete demonstration ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - normal structured logging\n"
        "  - @mta.trace\n"
        "  - nested traces\n"
        "  - call_id and parent_call_id\n"
        "  - automatic parameter capture\n"
        "  - default parameter capture\n"
        "  - execution duration\n"
        "  - password and token redaction\n"
        "  - nested secret redaction\n"
        "  - return values\n"
        "  - function_error\n"
        "  - handled exception\n"
        "  - error_type and error_message\n"
        "  - traceback\n"
        "  - parent continuation after child failure\n"
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
        "  process\n"
        "    authenticate\n"
        "    check_database\n"
        "    validate_result\n"
        "    failing_operation -> function_error\n"
        "    process continues\n"
        "\n"
        "Expected error behaviour:\n"
        "  - failing_operation produces function_error\n"
        "  - error_type is RuntimeError\n"
        "  - error_message is Operation 123 failed\n"
        "  - traceback is populated\n"
        "  - process handles the RuntimeError\n"
        "  - process completes normally\n"
        "\n"
        "Expected redaction:\n"
        "  - password\n"
        "  - access_token\n"
        "  - database_password\n"
        "  - client_secret\n"
        "  - nested access_token\n"
        "\n"
        "Where to inspect the results:\n"
        "  - ConsoleSink: output shown above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()