# examples/scripts/sink_failure/main_sink_failure_continue.py

"""
MonitAudit sink-failure isolation example using continue mode.

Purpose
-------
Demonstrates how MonitAudit behaves when one configured sink fails while
sink_failure_mode is set to continue.

A deliberately broken sink is inserted before the normally configured
MonitAudit sinks.

When BrokenSink fails, MonitAudit should continue writing to the remaining
configured sinks and the application should continue running normally.
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

    This sink exists only for demonstrating MonitAudit sink-failure
    isolation behaviour.
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

    # Add the deliberately broken sink before the sinks created from
    # configuration.
    configured_sinks = mta.logger.sinks

    mta.logger.sinks = (
        broken_sink,
        *configured_sinks,
    )

    print(
        "\n"
        "Starting sink-failure continue-mode example.\n"
        "\n"
        "BrokenSink will deliberately fail for every log record.\n"
        "MonitAudit should report those failures while the remaining\n"
        "configured sinks continue writing.\n"
    )

    mta.info(
        "Sink failure example started",
        example="main_sink_failure_continue",
        sink_failure_mode="continue",
        broken_sink="BrokenSink",
    )

    mta.debug(
        "Debug message after BrokenSink installation",
        sequence=1,
    )

    mta.info(
        "Information message after BrokenSink failure",
        sequence=2,
    )

    mta.warning(
        "Warning message after BrokenSink failure",
        sequence=3,
    )

    # Reaching this log call demonstrates that BrokenSink exceptions have
    # not propagated back to the application.
    mta.info(
        "Application still running after sink failures",
        sequence=4,
        broken_sink_write_count=broken_sink.write_count,
    )

    # Do not log the final count through MonitAudit because that would cause
    # one additional BrokenSink write attempt.
    final_write_count = broken_sink.write_count

    print(
        "\n"
        "Application reached the end of the example.\n"
        f"BrokenSink write attempts: {final_write_count}\n"
    )

    if final_write_count < 1:
        raise AssertionError(
            "BrokenSink was never called."
        )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: sink failure continue mode ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - deliberately failing Sink implementation\n"
        "  - BrokenSink inserted before configured sinks\n"
        "  - BrokenSink raises RuntimeError\n"
        "  - sink_failure_mode = continue\n"
        "  - remaining sinks are still attempted\n"
        "  - application continues executing\n"
        "  - subsequent log calls still work\n"
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
        "    remaining configured sinks continue\n"
        "  application continues\n"
        "\n"
        "Expected application messages:\n"
        "  - Sink failure example started\n"
        "  - Debug message after BrokenSink installation\n"
        "  - Information message after BrokenSink failure\n"
        "  - Warning message after BrokenSink failure\n"
        "  - Application still running after sink failures\n"
        "\n"
        "Where to look for the results:\n"
        "  - ConsoleSink: configured console output\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
        "\n"
        "Important:\n"
        "  Reaching this summary demonstrates that the deliberately\n"
        "  failing sink did not stop application execution while\n"
        "  sink_failure_mode is continue.\n"
    )


if __name__ == "__main__":
    main()
    print_summary()