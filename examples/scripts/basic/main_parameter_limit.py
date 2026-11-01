# examples/scripts/parameters/main_parameter_limit.py

"""
MonitAudit traced-parameter length-limit example.

Purpose
-------
Demonstrates how MonitAudit limits the length of captured parameters before
trace records are written to the configured sinks.

For this example the configured maximum parameter length is 50 characters.

The traced function receives the original parameter values. MonitAudit applies
the parameter limit only to the captured representation stored in the trace
records.
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
# Test values
# ---------------------------------------------------------------------------

MAX_PARAMETER_LENGTH = 50

SHORT_VALUE = "short"

EXACT_VALUE = (
    "x" * MAX_PARAMETER_LENGTH
)

LONG_VALUE = (
    "y" * 100
)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def process(
        short_value: str,
        exact_value: str,
        long_value: str,
        nested: dict[str, object],
    ) -> None:
        """
        Receive the original parameter values.

        These assertions verify that parameter limiting does not mutate the
        actual arguments received by the Python function.
        """

        assert short_value == SHORT_VALUE

        assert len(
            exact_value
        ) == MAX_PARAMETER_LENGTH

        assert exact_value == EXACT_VALUE

        assert len(
            long_value
        ) == 100

        assert long_value == LONG_VALUE

        assert (
            nested["message"]
            == LONG_VALUE
        )

        nested_message = nested[
            "message"
        ]

        assert isinstance(
            nested_message,
            str,
        )

        assert len(
            nested_message
        ) == 100

        mta.info(
            "Function received original parameter values",
            short_length=len(short_value),
            exact_length=len(exact_value),
            long_length=len(long_value),
            nested_length=len(nested_message),
        )

    mta.info(
        "Parameter-limit example started",
        example="main_parameter_limit",
        max_parameter_length=MAX_PARAMETER_LENGTH,
    )

    process(
        short_value=SHORT_VALUE,
        exact_value=EXACT_VALUE,
        long_value=LONG_VALUE,
        nested={
            "message": LONG_VALUE,
        },
    )

    mta.info(
        "Parameter-limit example completed",
        example="main_parameter_limit",
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: parameter limit ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - @mta.trace\n"
        "  - automatic parameter capture\n"
        "  - max_parameter_length\n"
        "  - short parameter preservation\n"
        "  - exact-boundary parameter handling\n"
        "  - long parameter limiting\n"
        "  - recursive nested parameter limiting\n"
        "  - original function arguments remain unchanged\n"
        "\n"
        "Configured parameter limit:\n"
        f"  {MAX_PARAMETER_LENGTH}\n"
        "\n"
        "Input lengths:\n"
        f"  short_value    : {len(SHORT_VALUE)}\n"
        f"  exact_value    : {len(EXACT_VALUE)}\n"
        f"  long_value     : {len(LONG_VALUE)}\n"
        f"  nested.message : {len(LONG_VALUE)}\n"
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
        "Where to look for the results:\n"
        "  - Console: inspect trace execution above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
        "\n"
        "Important:\n"
        "  Parameter limiting controls captured size.\n"
        "  It does not modify the original Python arguments.\n"
        "  It does not replace sensitive-data redaction.\n"
    )


if __name__ == "__main__":
    main()
    print_summary()