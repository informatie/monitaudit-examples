# examples/scripts/redaction/main_redaction_exact_names.py

"""
MonitAudit exact-name sensitive-parameter redaction example.

Purpose
-------
Demonstrates how MonitAudit automatically redacts traced parameters whose
names exactly match sensitive parameter names.

The example passes several deliberately sensitive parameters to a traced
function. Their captured trace values should be redacted, while the Python
function itself continues receiving the original values.
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
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    mta = build_monitaudit(
        CONFIG_PATH,
    )

    @mta.trace
    def demo(
        password: str,
        secret: str,
        api_key: str,
        token: str,
        authorization: str,
        visible: str,
    ) -> None:
        """
        Demonstrate exact-name sensitive parameter redaction.

        These assertions verify that redaction does not modify the actual
        values supplied to the Python function.
        """

        assert password == "password-value"
        assert secret == "secret-value"
        assert api_key == "api-key-value"
        assert token == "token-value"
        assert authorization == "authorization-value"
        assert visible == "visible-value"

        # Only log the deliberately non-sensitive value.
        #
        # Sensitive values must not be manually added to messages or
        # structured log attributes.
        mta.info(
            "Function received original values",
            visible=visible,
        )

    mta.info(
        "Exact-name redaction example started",
        example="main_redaction_exact_names",
    )

    demo(
        password="password-value",
        secret="secret-value",
        api_key="api-key-value",
        token="token-value",
        authorization="authorization-value",
        visible="visible-value",
    )

    mta.info(
        "Exact-name redaction example completed",
        example="main_redaction_exact_names",
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: exact-name redaction ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - @mta.trace parameter capture\n"
        "  - exact sensitive-name detection\n"
        "  - password redaction\n"
        "  - secret redaction\n"
        "  - api_key redaction\n"
        "  - token redaction\n"
        "  - authorization redaction\n"
        "  - non-sensitive parameter preservation\n"
        "  - Python function receives original values\n"
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
        "Expected captured trace parameters:\n"
        '  password      = "***"\n'
        '  secret        = "***"\n'
        '  api_key       = "***"\n'
        '  token         = "***"\n'
        '  authorization = "***"\n'
        '  visible       = "visible-value"\n'
        "\n"
        "Expected values inside demo():\n"
        "  password      = password-value\n"
        "  secret        = secret-value\n"
        "  api_key       = api-key-value\n"
        "  token         = token-value\n"
        "  authorization = authorization-value\n"
        "  visible       = visible-value\n"
        "\n"
        "Important:\n"
        "  Redaction affects the captured trace representation only.\n"
        "  The Python function receives the original values.\n"
        "\n"
        "  Sensitive values must not be manually included in log\n"
        "  messages or structured attributes.\n"
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