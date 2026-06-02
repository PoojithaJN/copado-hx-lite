import json
from pathlib import Path

from typer.testing import CliRunner

import main


runner = CliRunner()


def invoke(args: list[str], tmp_path: Path):
    original_state_file = main.STATE_FILE
    main.STATE_FILE = tmp_path / ".copado-hx.json"
    try:
        return runner.invoke(main.app, args)
    finally:
        main.STATE_FILE = original_state_file


def test_help_command_works(tmp_path: Path) -> None:
    result = invoke(["--help"], tmp_path)

    assert result.exit_code == 0
    assert "Commands" in result.output
    assert "deliver" in result.output


def test_status_json_returns_valid_json(tmp_path: Path) -> None:
    result = invoke(["status", "--json"], tmp_path)

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["auth"] == "Not authenticated"


def test_dashboard_json_returns_progress(tmp_path: Path) -> None:
    result = invoke(["dashboard", "--json"], tmp_path)

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "overall_progress_percentage" in payload
    assert payload["overall_progress_percentage"] == 0


def test_deliver_completes_with_browser_summary(tmp_path: Path) -> None:
    login = invoke(["auth", "login", "--token", "demo-token"], tmp_path)
    assert login.exit_code == 0

    result = invoke(["deliver", "--id", "US-1234"], tmp_path)

    assert result.exit_code == 0
    assert "Browser tabs opened: 0" in result.output

