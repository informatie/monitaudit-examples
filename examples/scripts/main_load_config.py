# examples/scripts/main_load_config.py

from __future__ import annotations

from pathlib import Path


EXAMPLES_DIR = Path.cwd()

CONFIG_DIR = EXAMPLES_DIR / "config"
DATA_DIR = EXAMPLES_DIR / "data"
SCRIPTS_DIR = EXAMPLES_DIR / "scripts"
OUTPUT_DIR = EXAMPLES_DIR / "output"


def get_config_path(
    main_file: str | Path,
) -> Path:
    main_path = Path(main_file)

    config_path = CONFIG_DIR / f"{main_path.stem}.yaml"

    if not config_path.is_file():
        raise FileNotFoundError(
            f"Runtime configuration not found: {config_path}"
        )

    return config_path