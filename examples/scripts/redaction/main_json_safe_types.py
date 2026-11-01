# examples/scripts/json_safe/main_json_safe_types.py

"""
MonitAudit JSON-safe parameter conversion example.

Purpose
-------
Demonstrates how MonitAudit converts common Python and Pydantic values into
JSON-safe representations before captured trace parameters are written to
structured sinks such as JsonSink.

The example passes one dictionary containing several different Python value
types to a traced function.

The traced function itself receives the original Python objects. JSON-safe
conversion only affects the captured parameter representation.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from enum import Enum
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel

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
# Example types
# ---------------------------------------------------------------------------

class State(Enum):
    READY = "ready"


class Payload(BaseModel):
    name: str
    count: int


class CustomObject:
    def __repr__(self) -> str:
        return "CustomObject(example)"


class BrokenRepr:
    def __repr__(self) -> str:
        raise RuntimeError(
            "repr failed"
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
        values: dict[str, object],
    ) -> None:
        """
        Receive the original Python objects.

        MonitAudit converts the captured trace representation before writing
        the parameters to its configured sinks.
        """

        assert isinstance(
            values["datetime_value"],
            datetime,
        )

        assert isinstance(
            values["date_value"],
            date,
        )

        assert isinstance(
            values["time_value"],
            time,
        )

        assert isinstance(
            values["path_value"],
            Path,
        )

        assert isinstance(
            values["uuid_value"],
            UUID,
        )

        assert (
            values["enum_value"]
            is State.READY
        )

        assert isinstance(
            values["model_value"],
            Payload,
        )

        assert isinstance(
            values["tuple_value"],
            tuple,
        )

        assert isinstance(
            values["set_value"],
            set,
        )

        assert isinstance(
            values["frozenset_value"],
            frozenset,
        )

        assert isinstance(
            values["bytes_value"],
            bytes,
        )

        assert isinstance(
            values["custom_value"],
            CustomObject,
        )

        assert isinstance(
            values["broken_repr_value"],
            BrokenRepr,
        )

        mta.info(
            "Original Python values received by function",
            value_count=len(values),
        )

    values: dict[str, object] = {
        "datetime_value": datetime(
            2026,
            10,
            23,
            12,
            30,
            tzinfo=UTC,
        ),
        "date_value": date(
            2026,
            10,
            23,
        ),
        "time_value": time(
            12,
            30,
        ),
        "path_value": Path(
            "/tmp/example"
        ),
        "uuid_value": UUID(
            "12345678-1234-5678-1234-567812345678"
        ),
        "enum_value": State.READY,
        "model_value": Payload(
            name="example",
            count=2,
        ),
        "tuple_value": (
            1,
            2,
        ),
        "set_value": {
            1,
            2,
        },
        "frozenset_value": frozenset(
            {
                3,
                4,
            }
        ),
        "bytes_value": b"example",
        "custom_value": CustomObject(),
        "broken_repr_value": BrokenRepr(),
    }

    mta.info(
        "JSON-safe types example started",
        example="main_json_safe_types",
        value_count=len(values),
    )

    process(
        values
    )

    mta.info(
        "JSON-safe types example completed",
        value_count=len(values),
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: JSON-safe types ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - @mta.trace parameter capture\n"
        "  - recursive JSON-safe conversion\n"
        "  - datetime -> string\n"
        "  - date -> string\n"
        "  - time -> string\n"
        "  - Path -> string\n"
        "  - UUID -> string\n"
        "  - Enum -> value\n"
        "  - Pydantic model -> mapping\n"
        "  - tuple -> list\n"
        "  - set -> list\n"
        "  - frozenset -> list\n"
        "  - bytes -> representation\n"
        "  - custom object -> representation\n"
        "  - broken repr -> safe representation\n"
        "  - original Python objects remain unchanged\n"
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
        "Expected captured values:\n"
        "  datetime_value  -> 2026-10-23T12:30:00+00:00\n"
        "  date_value      -> 2026-10-23\n"
        "  time_value      -> 12:30:00\n"
        "  path_value      -> /tmp/example\n"
        "  uuid_value      -> 12345678-1234-5678-1234-567812345678\n"
        "  enum_value      -> ready\n"
        "  model_value     -> mapping\n"
        "  tuple_value     -> list\n"
        "  set_value       -> list containing 1 and 2\n"
        "  frozenset_value -> list containing 3 and 4\n"
        "  bytes_value     -> bytes representation\n"
        "  custom_value    -> CustomObject(example)\n"
        "  broken_repr     -> safe representation\n"
        "\n"
        "Important:\n"
        "  The Python function receives the original objects.\n"
        "  Only the captured trace representation is converted.\n"
        "\n"
        "  Set and frozenset ordering is not significant.\n"
        "\n"
        "  JSON-safe conversion is not redaction.\n"
        "  Sensitive values still require redaction.\n"
        "\n"
        "Where to look for the results:\n"
        "  - Console: inspect trace execution above\n"
        "  - FileSink: configured file_sink.path\n"
        "  - JsonSink: configured json_sink.path\n"
        "  - DeltaSink: configured delta_sink.table\n"
    )


if __name__ == "__main__":
    main()
    print_summary()