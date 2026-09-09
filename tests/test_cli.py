"""Unit tests for ClipRing CLI."""

from typer.testing import CliRunner

from clipring.cli.main import app

runner = CliRunner()


def test_cli_info():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "ClipRing System Diagnostics" in result.output
    assert "Active Backend" in result.output


def test_cli_read():
    result = runner.invoke(app, ["read"])
    assert result.exit_code == 0


def test_cli_read_json():
    result = runner.invoke(app, ["read", "--json"])
    assert result.exit_code == 0
    assert "content_type" in result.output
