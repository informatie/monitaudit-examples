# examples/scripts/sinks/main_file_sink.py

"""
MonitAudit FileSink example.

Purpose
-------
Demonstrates MonitAudit's human-readable text-file logging through FileSink.

The example produces several different log records:

- INFO
- WARNING
- traced function_start
- normal logging inside a traced function
- traced function_end
- ERROR with exception information and traceback

Running the example multiple times should append records to the configured
FileSink output.
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
from monitaudit.utilities.build_monitaudit import build_monitaudit


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CONFIG_PATH = get_config_path(__file__)


# ---------------------------------------------------------------------------
# FileSink
# ---------------------------------------------------------------------------

def find_file_sink(
    mta: Any,
) -> Any:
    """
    Find the configured FileSink.
    """

    for sink in mta.logger.sinks:
        if type(sink).__name__ == "FileSink":
            return sink

    raise RuntimeError(
        "Configured FileSink was not found."
    )


def get_file_sink_path(
    file_sink: Any,
) -> Path:
    """
    Return the actual path used by FileSink.
    """

    path = getattr(
        file_sink,
        "path",
        None,
    )

    if path is None:
        raise RuntimeError(
            "Configured FileSink does not expose a path."
        )

    return Path(path).resolve()


# ---------------------------------------------------------------------------
# Output verification
# ---------------------------------------------------------------------------

def count_log_lines(
    path: Path,
) -> int:
    """
    Count physical lines currently stored in the FileSink output.

    Error records may occupy multiple physical lines because traceback
    information can span multiple lines.
    """

    if not path.is_file():
        return 0

    return len(
        path.read_text(
            encoding="utf-8",
        ).splitlines()
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    file_sink = find_file_sink(
        mta
    )

    log_path = get_file_sink_path(
        file_sink
    )

    lines_before = count_log_lines(
        log_path
    )

    print()
    print("FileSink configuration:")
    print(f"  sink type = {type(file_sink).__name__}")
    print(f"  log path  = {log_path}")
    print()

    mta.info(
        "FileSink example started",
        example="main_file_sink",
        lines_before=lines_before,
    )

    mta.info(
        "Structured information record",
        customer=301,
        status="running",
        attempt=1,
    )

    mta.warning(
        "Demonstration warning",
        customer=302,
        reason="This warning is intentional",
    )

    @mta.trace
    def calculate(
        first: int,
        second: int,
        operation: str = "add",
    ) -> int:
        """
        Produce trace output in the human-readable FileSink log.
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
        raise ValueError(
            "FileSink example failure"
        )

    except ValueError as exception:
        mta.error(
            "Demonstration error captured",
            exception=exception,
            component="main_file_sink",
        )

    mta.info(
        "FileSink example completed",
        example="main_file_sink",
    )

    lines_after = count_log_lines(
        log_path
    )

    added_lines = (
        lines_after
        - lines_before
    )

    print(
        "\n"
        "FileSink write statistics:\n"
        f"  log path     = {log_path}\n"
        f"  lines before = {lines_before}\n"
        f"  lines after  = {lines_after}\n"
        f"  lines added  = {added_lines}\n"
    )

    if not log_path.is_file():
        raise AssertionError(
            "FileSink output file was not created: "
            f"{log_path}"
        )

    if lines_after <= lines_before:
        raise AssertionError(
            "FileSink did not append output: "
            f"{log_path}"
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: FileSink ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - human-readable FileSink output\n"
        "  - append-only file logging\n"
        "  - INFO logging\n"
        "  - WARNING logging\n"
        "  - structured attributes\n"
        "  - @mta.trace\n"
        "  - function_start\n"
        "  - function_end\n"
        "  - parameter capture\n"
        "  - default parameter capture\n"
        "  - call_id\n"
        "  - duration_ms\n"
        "  - ERROR logging\n"
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
        "  error_type    = ValueError\n"
        "  error_message = FileSink example failure\n"
        "  traceback     = populated\n"
        "\n"
        "Important:\n"
        "  The example obtains the output path directly from the\n"
        "  configured FileSink instead of duplicating the path in\n"
        "  the Python example.\n"
    )


if __name__ == "__main__":
    main()
    print_summary()