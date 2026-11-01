# examples/scripts/redaction/main_redaction_suffixes.py

"""
MonitAudit sensitive-parameter suffix redaction example.

Purpose
-------
Demonstrates how MonitAudit automatically redacts traced parameters whose
names end with configured sensitive suffixes.

The example deliberately uses parameter names whose suffixes identify them
as sensitive.

The traced function itself continues receiving the original values.
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
        database_password: str,
        service_api_key: str,
        github_token: str,
        client_secret: str,
        visible: str,
    ) -> None:
        """
        Demonstrate suffix-based parameter redaction.

        These assertions verify that redaction does not modify the actual
        values supplied to the Python function.
        """

        assert database_password == "database-secret"
        assert service_api_key == "api-secret"
        assert github_token == "token-secret"
        assert client_secret == "client-secret"
        assert visible == "visible-value"

        # Only log the deliberately non-sensitive value.
        #
        # Sensitive values must not be manually added to messages or
        # structured log attributes.
        mta.info(
            "Function received original parameter values",
            visible=visible,
        )

    mta.info(
        "Redaction suffix example started",
        example="main_redaction_suffixes",
    )

    demo(
        database_password="database-secret",
        service_api_key="api-secret",
        github_token="token-secret",
        client_secret="client-secret",
        visible="visible-value",
    )

    mta.info(
        "Redaction suffix example completed",
        example="main_redaction_suffixes",
    )


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    print(
        "\n"
        "=== Example completed: suffix redaction ===\n"
        "\n"
        "What was demonstrated:\n"
        "  - @mta.trace parameter capture\n"
        "  - suffix-based redaction\n"
        "  - _password suffix\n"
        "  - _api_key suffix\n"
        "  - _token suffix\n"
        "  - _secret suffix\n"
        "  - non-sensitive value remains visible\n"
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
        '  database_password = "***"\n'
        '  service_api_key   = "***"\n'
        '  github_token      = "***"\n'
        '  client_secret     = "***"\n'
        '  visible           = "visible-value"\n'
        "\n"
        "Expected original function values:\n"
        "  database_password = database-secret\n"
        "  service_api_key   = api-secret\n"
        "  github_token      = token-secret\n"
        "  client_secret     = client-secret\n"
        "  visible           = visible-value\n"
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