# examples/scripts/sinks/main_all_sinks.py

from __future__ import annotations

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

JSON_DIR = OUTPUT_DIR / "json_sink"
FILE_DIR = OUTPUT_DIR / "file_sink"

JSON_PATH = JSON_DIR / "main_all_sinks.jsonl"
FILE_PATH = FILE_DIR / "main_all_sinks.log"

DELTA_TABLE = "main.alldelta.local"

DELTA_PATH = Path(
    DELTA_TABLE.replace(
        ".",
        "/",
    )
)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def prepare_output_directories() -> None:
    JSON_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FILE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def count_json_records() -> int:
    if not JSON_PATH.is_file():
        return 0

    return sum(
        1
        for line in JSON_PATH.read_text(
            encoding="utf-8",
        ).splitlines()
        if line.strip()
    )


def count_file_lines() -> int:
    if not FILE_PATH.is_file():
        return 0

    return len(
        FILE_PATH.read_text(
            encoding="utf-8",
        ).splitlines()
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    prepare_output_directories()

    json_before = count_json_records()
    file_before = count_file_lines()

    mta = build_monitaudit(
        CONFIG_PATH,
    )

    mta.info(
        "All-sinks example started",
        example="main_all_sinks",
        delta_table=DELTA_TABLE,
    )

    mta.info(
        "Structured record sent to all sinks",
        customer=301,
        order_code="E001",
        status="running",
    )

    @mta.trace
    def operation(
        value: int,
        multiplier: int = 2,
    ) -> int:
        mta.info(
            "Operation running",
            value=value,
            multiplier=multiplier,
        )

        return value * multiplier

    result = operation(
        value=21,
    )

    mta.info(
        "Operation result received",
        result=result,
    )

    try:
        raise ValueError(
            "All-sinks demonstration failure"
        )

    except ValueError as exception:
        mta.error(
            "Demonstration error sent to all sinks",
            exception=exception,
            component="main_all_sinks",
        )

    mta.warning(
        "All-sinks demonstration warning",
        reason="Intentional example warning",
    )

    mta.info(
        "All-sinks example completed",
        example="main_all_sinks",
    )

    json_after = count_json_records()
    file_after = count_file_lines()

    print(
        "\n"
        "File/JSON verification:\n"
        f"  JSON records before = {json_before}\n"
        f"  JSON records after  = {json_after}\n"
        f"  JSON records added  = {json_after - json_before}\n"
        "\n"
        f"  File lines before   = {file_before}\n"
        f"  File lines after    = {file_after}\n"
        f"  File lines added    = {file_after - file_before}\n"
    )

    if json_after <= json_before:
        raise AssertionError(
            "JsonSink did not append records. "
            f"path={JSON_PATH}, "
            f"exists={JSON_PATH.is_file()}, "
            f"before={json_before}, "
            f"after={json_after}"
        )

    if file_after <= file_before:
        raise AssertionError(
            "FileSink did not append output. "
            f"path={FILE_PATH}, "
            f"exists={FILE_PATH.is_file()}, "
            f"before={file_before}, "
            f"after={file_after}"
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: all sinks ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - normal structured logging\n"
        "  - @mta.trace\n"
        "  - ConsoleSink\n"
        "  - JsonSink\n"
        "  - FileSink\n"
        "  - DeltaSink configuration\n"
        "  - INFO, WARNING and ERROR logging\n"
        "  - exception logging\n"
        "  - output verification\n"
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
        "Output:\n"
        f"  JSON     : {JSON_PATH}\n"
        f"  File     : {FILE_PATH}\n"
        f"  Delta    : {DELTA_TABLE}\n"
        f"  DeltaPath: {DELTA_PATH}\n"
    )


if __name__ == "__main__":
    main()
    print_summary()