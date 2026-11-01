# examples/scripts/sinks/main_json_sink.py

"""
MonitAudit JsonSink example.

Purpose
-------
Demonstrates MonitAudit logging to an append-only JSON Lines (JSONL) file.

JsonSink writes one complete JSON object per line. Running the example
multiple times appends new records to the existing file.

The example includes structured logging, nested attributes, tracing,
exception information and JSONL output validation.
"""

from __future__ import annotations

import json
from pathlib import Path

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

JSON_PATH = (
    OUTPUT_DIR
    / "json_sink"
    / "main_json_sink.jsonl"
)


# ---------------------------------------------------------------------------
# Output preparation
# ---------------------------------------------------------------------------

def prepare_output_directory() -> None:
    """
    Ensure the JsonSink output directory exists.
    """

    JSON_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


# ---------------------------------------------------------------------------
# Output verification
# ---------------------------------------------------------------------------

def count_json_lines(
    path: Path,
) -> int:
    """
    Count non-empty JSONL records.
    """

    if not path.is_file():
        return 0

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return sum(
            1
            for line in file
            if line.strip()
        )


def validate_json_lines(
    path: Path,
) -> int:
    """
    Validate every non-empty line as an independent JSON document.

    Returns the number of valid JSON records.
    """

    if not path.is_file():
        raise FileNotFoundError(
            f"JsonSink output not found: {path}"
        )

    record_count = 0

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            try:
                json.loads(
                    line
                )

            except json.JSONDecodeError as exception:
                raise ValueError(
                    "Invalid JSONL record at "
                    f"line {line_number}: {path}"
                ) from exception

            record_count += 1

    return record_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    prepare_output_directory()

    mta = build_monitaudit(
        CONFIG_PATH,
    )

    records_before = count_json_lines(
        JSON_PATH
    )

    print()
    print("JsonSink configuration:")
    print(f"  config    = {CONFIG_PATH}")
    print(f"  JSON path = {JSON_PATH}")
    print()

    mta.info(
        "JsonSink example started",
        example="main_json_sink",
        records_before=records_before,
    )

    mta.info(
        "Structured information record",
        record_number=1,
        customer=301,
        status="started",
    )

    mta.warning(
        "Structured warning record",
        record_number=2,
        customer=302,
        details={
            "source": "example",
            "retry": 2,
        },
    )

    @mta.trace
    def calculate(
        first: int,
        second: int,
        operation: str = "add",
    ) -> int:
        """
        Produce function_start and function_end records in JSON.
        """

        mta.info(
            "Calculation running",
            first=first,
            second=second,
            operation=operation,
        )

        if operation != "add":
            raise ValueError(
                f"Unsupported operation: {operation}"
            )

        return first + second

    result = calculate(
        first=20,
        second=22,
    )

    mta.info(
        "Calculation completed",
        result=result,
    )

    try:
        raise RuntimeError(
            "JsonSink demonstration failure"
        )

    except RuntimeError as exception:
        mta.error(
            "Demonstration error captured",
            exception=exception,
            example="main_json_sink",
        )

    mta.info(
        "JsonSink example completed",
        example="main_json_sink",
    )

    # -----------------------------------------------------------------------
    # Verify output
    # -----------------------------------------------------------------------

    if not JSON_PATH.is_file():
        raise AssertionError(
            "JsonSink output file was not created: "
            f"{JSON_PATH}"
        )

    records_after = count_json_lines(
        JSON_PATH
    )

    added_records = (
        records_after
        - records_before
    )

    validated_records = validate_json_lines(
        JSON_PATH
    )

    print()
    print("JsonSink write statistics:")
    print(f"  JSON path         = {JSON_PATH}")
    print(f"  records before    = {records_before}")
    print(f"  records after     = {records_after}")
    print(f"  records added     = {added_records}")
    print(f"  records validated = {validated_records}")
    print()

    if added_records <= 0:
        raise AssertionError(
            "JsonSink did not append JSONL records: "
            f"{JSON_PATH}"
        )

    if validated_records != records_after:
        raise AssertionError(
            "JsonSink JSONL record count does not match "
            "the validated record count."
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: JsonSink ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - JSON Lines output\n"
        "  - append-only writes\n"
        "  - JSON validation\n"
        "  - structured attributes\n"
        "  - nested structured attributes\n"
        "  - @mta.trace\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - automatic parameter capture\n"
        "  - default parameter capture\n"
        "  - call_id\n"
        "  - parent_call_id\n"
        "  - duration_ms\n"
        "  - ERROR serialisation\n"
        "  - error_type\n"
        "  - error_message\n"
        "  - traceback\n"
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
        "Output file:\n"
        f"  {JSON_PATH}\n"
        "\n"
        "Expected trace flow:\n"
        "  calculate -> function_start\n"
        "    Calculation running\n"
        "  calculate -> function_end\n"
        "\n"
        "Expected calculate parameters:\n"
        "  first     = 20\n"
        "  second    = 22\n"
        "  operation = add\n"
        "\n"
        "Expected ERROR information:\n"
        "  level         = ERROR\n"
        "  error_type    = RuntimeError\n"
        "  error_message = JsonSink demonstration failure\n"
        "  traceback     = populated\n"
        "\n"
        "JSONL verification:\n"
        "  - output file exists\n"
        "  - records were appended\n"
        "  - every non-empty line parses with json.loads()\n"
        "\n"
        "Where to look for the results:\n"
        f"  - JsonSink: {JSON_PATH}\n"
        "  - ConsoleSink: configured console output\n"
        "  - FileSink: configured file_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()