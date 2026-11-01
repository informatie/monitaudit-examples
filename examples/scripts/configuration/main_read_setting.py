# examples/scripts/main_read_setting.py

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import yaml

from main_load_config import (
    CONFIG_DIR,
    DATA_DIR,
    EXAMPLES_DIR,
    OUTPUT_DIR,
    SCRIPTS_DIR,
    get_config_path,
)
from monitaudit.utilities.load_config import (
    ENVIRONMENT_VARIABLES,
    load_config,
)


MISSING = "-"

CONFIG_PATH = get_config_path(__file__)
# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def find_environment() -> tuple[str | None, str | None]:
    """
    Find the environment variable used by MonitAudit.

    Priority is determined by ENVIRONMENT_VARIABLES.
    """

    for variable in ENVIRONMENT_VARIABLES:
        value = os.getenv(variable)

        if value is not None and value.strip():
            return variable, value.strip().lower()

    return None, None


# ---------------------------------------------------------------------------
# Runtime configuration
# ---------------------------------------------------------------------------

def find_runtime_file() -> Path:
    """
    Select a runtime YAML from examples/config.

    main_read_setting.yaml is preferred when available.
    """

    config_path = CONFIG_DIR / "main_read_setting.yaml"

    if config_path.is_file():
        return config_path

    runtime_files = sorted(
        CONFIG_DIR.glob("*.yaml")
    )

    if not runtime_files:
        raise FileNotFoundError(
            f"No MonitAudit runtime configuration found in: {CONFIG_DIR}"
        )

    if len(runtime_files) > 1:
        files = "\n".join(
            f"  - {path.name}"
            for path in runtime_files
        )

        raise RuntimeError(
            "Multiple MonitAudit runtime configurations found.\n"
            "Create config/main_read_setting.yaml or select one "
            "explicitly.\n"
            f"{files}"
        )

    return runtime_files[0]


# ---------------------------------------------------------------------------
# Flatten
# ---------------------------------------------------------------------------

def flatten(
    data: Mapping[str, Any],
    *,
    prefix: str = "",
) -> dict[str, object]:
    result: dict[str, object] = {}

    for key, value in data.items():
        full_key = (
            f"{prefix}.{key}"
            if prefix
            else str(key)
        )

        if isinstance(value, Mapping):
            result.update(
                flatten(
                    value,
                    prefix=full_key,
                )
            )
        else:
            result[full_key] = value

    return result


# ---------------------------------------------------------------------------
# Runtime YAML
# ---------------------------------------------------------------------------

def load_runtime_for_report(
    path: Path,
    environment: str,
) -> dict[str, object]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data: Any = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Runtime configuration must be a YAML mapping."
        )

    monitaudit = data.get("monitaudit")

    if not isinstance(monitaudit, dict):
        raise ValueError(
            "Missing 'monitaudit' section."
        )

    result: dict[str, object] = {}

    application = monitaudit.get(
        "application"
    )

    if application is not None:
        result["application"] = application

    global_config = monitaudit.get(
        "global",
        {},
    )

    if isinstance(global_config, dict):
        result.update(
            flatten(global_config)
        )

    environments = monitaudit.get(
        "environments",
        {},
    )

    if isinstance(environments, dict):
        selected = environments.get(
            environment,
            {},
        )

        if isinstance(selected, dict):
            result.update(
                flatten(selected)
            )

    return result


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_value(
    value: object,
) -> str:
    if value is None:
        return "null"

    if isinstance(value, bool):
        return str(value).lower()

    if isinstance(value, (list, tuple)):
        return ", ".join(
            str(item)
            for item in value
        )

    return str(value)


def print_matrix(
    runtime: dict[str, object],
    result: dict[str, object],
) -> None:
    keys = sorted(
        set(runtime)
        | set(result)
    )

    rows: list[
        tuple[str, str, str]
    ] = []

    for key in keys:
        rows.append(
            (
                key,
                format_value(
                    runtime.get(
                        key,
                        MISSING,
                    )
                ),
                format_value(
                    result.get(
                        key,
                        MISSING,
                    )
                ),
            )
        )

    headers = (
        "KEY",
        "RUNTIME YAML",
        "RESULT",
    )

    widths = [
        max(
            len(headers[index]),
            max(
                (
                    len(row[index])
                    for row in rows
                ),
                default=0,
            ),
        )
        for index in range(3)
    ]

    separator = (
        "+"
        + "+".join(
            "-" * (width + 2)
            for width in widths
        )
        + "+"
    )

    print(separator)

    print(
        "| "
        + " | ".join(
            headers[index].ljust(
                widths[index]
            )
            for index in range(3)
        )
        + " |"
    )

    print(separator)

    for row in rows:
        print(
            "| "
            + " | ".join(
                row[index].ljust(
                    widths[index]
                )
                for index in range(3)
            )
            + " |"
        )

    print(separator)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    environment_variable, environment = find_environment()

    if environment_variable is None or environment is None:
        variables = ", ".join(
            ENVIRONMENT_VARIABLES
        )

        raise RuntimeError(
            "No MonitAudit environment variable found. "
            f"Checked: {variables}"
        )

    config_path = find_runtime_file()

    runtime = load_runtime_for_report(
        config_path,
        environment,
    )

    config = load_config(
        config_path,
    )

    result = flatten(
        config.model_dump(
            mode="python",
            exclude_none=False,
        )
    )

    print()
    print("MONITAUDIT CONFIGURATION REPORT")
    print("=" * 80)
    print()
    print(f"Environment : {environment}")
    print(f"Variable    : {environment_variable}")
    print(f"Runtime     : {config_path}")
    print()
    print(f"Examples    : {EXAMPLES_DIR}")
    print(f"Config      : {CONFIG_DIR}")
    print(f"Data        : {DATA_DIR}")
    print(f"Scripts     : {SCRIPTS_DIR}")
    print(f"Output      : {OUTPUT_DIR}")
    print()

    print_matrix(
        runtime,
        result,
    )


if __name__ == "__main__":
    main()