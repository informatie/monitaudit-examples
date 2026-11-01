# examples/scripts/sink_failure/main_sink_failure_raise.py

"""
MonitAudit sink-failure isolation example using raise mode.

Purpose
-------
Demonstrates how MonitAudit behaves when one configured sink fails while
sink_failure_mode is set to raise.

A deliberately broken sink is inserted before the normally configured
MonitAudit sinks.

The remaining sinks should still be attempted before MonitAudit propagates
the sink failure back to the application.
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
from monitaudit.models.base import BaseLog
from monitaudit.sinks.base import Sink
from monitaudit.utilities.build_monitaudit import build_monitaudit


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CONFIG_PATH = get_config_path(__file__)


# ---------------------------------------------------------------------------
# Broken sink
# ---------------------------------------------------------------------------

class BrokenSink(Sink):
    """
    Sink that deliberately fails on every write.

    The counter verifies that the sink was invoked before MonitAudit
    propagated the sink-failure exception.
    """

    def __init__(self) -> None:
        self.write_count = 0

    def write(
        self,
        log: BaseLog,
    ) -> None:
        self.write_count += 1

        raise RuntimeError(
            "Deliberate BrokenSink failure"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    broken_sink = BrokenSink()

    configured_sinks = mta.logger.sinks

    # BrokenSink is deliberately placed first.
    #
    # This verifies that processing does not stop immediately after the
    # first sink failure.
    mta.logger.sinks = (
        broken_sink,
        *configured_sinks,
    )

    print(
        "\n"
        "Starting sink-failure RAISE-mode example.\n"
        "\n"
        "BrokenSink will fail first.\n"
        "The remaining configured sinks should still be attempted.\n"
        "MonitAudit should then raise RuntimeError.\n"
    )

    monitaudit_exception: RuntimeError | None = None

    try:
        mta.info(
            "Every sink is attempted before raise mode reports failure",
            example="main_sink_failure_raise",
            sink_failure_mode="raise",
            broken_sink="BrokenSink",
        )

    except RuntimeError as exception:
        monitaudit_exception = exception

        print(
            "\n"
            "Expected MonitAudit failure received:\n"
            f"  {type(exception).__name__}: "
            f"{exception}\n"
        )

        if exception.__cause__ is not None:
            print(
                "Original sink failure:\n"
                f"  {type(exception.__cause__).__name__}: "
                f"{exception.__cause__}\n"
            )

    else:
        raise AssertionError(
            "sink_failure_mode='raise' did not raise"
        )

    if broken_sink.write_count != 1:
        raise AssertionError(
            "BrokenSink should have been called exactly once "
            f"but was called {broken_sink.write_count} times."
        )

    if monitaudit_exception is None:
        raise AssertionError(
            "Expected MonitAudit RuntimeError was not captured."
        )

    expected_message = (
        "monitaudit sink failure(s): BrokenSink"
    )

    if str(monitaudit_exception) != expected_message:
        raise AssertionError(
            "Unexpected MonitAudit exception message: "
            f"{monitaudit_exception}"
        )

    cause = monitaudit_exception.__cause__

    if not isinstance(
        cause,
        RuntimeError,
    ):
        raise AssertionError(
            "MonitAudit RuntimeError should preserve the "
            "original RuntimeError as __cause__."
        )

    if str(cause) != "Deliberate BrokenSink failure":
        raise AssertionError(
            "Unexpected original sink exception: "
            f"{cause}"
        )

    print(
        "Verification successful:\n"
        f"  BrokenSink writes = {broken_sink.write_count}\n"
        "  MonitAudit raised = RuntimeError\n"
        "  Original cause    = RuntimeError\n"
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: sink failure raise mode ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - deliberately failing Sink implementation\n"
        "  - BrokenSink inserted before configured sinks\n"
        "  - BrokenSink raises RuntimeError\n"
        "  - sink_failure_mode = raise\n"
        "  - remaining configured sinks are still attempted\n"
        "  - MonitAudit raises after sink processing\n"
        "  - application catches the MonitAudit RuntimeError\n"
        "  - original sink failure is preserved as __cause__\n"
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
        "Expected execution model:\n"
        "  logger write\n"
        "    BrokenSink -> RuntimeError\n"
        "    remaining configured sinks are attempted\n"
        "    MonitAudit raises RuntimeError afterwards\n"
        "\n"
        "Expected MonitAudit exception:\n"
        "  RuntimeError\n"
        "  monitaudit sink failure(s): BrokenSink\n"
        "\n"
        "Expected original cause:\n"
        "  RuntimeError\n"
        "  Deliberate BrokenSink failure\n"
        "\n"
        "Difference from continue mode:\n"
        "  continue -> remaining sinks run, application continues\n"
        "  raise    -> remaining sinks run, application receives error\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: configured console output\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()