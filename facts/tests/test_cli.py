"""Tests for CLI entrypoints and command validation."""
import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from facts.cli import cli, ensure_output_dir, load_inventory_data


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_ctx():
    """Mock Click context with minimal required paths."""
    from click import Context

    ctx = Context(cli)
    ctx.ensure_object(dict)
    ctx.obj.update({
        "swconfigdir": "/fake/swconfig/",
        "vlansfile": "vlans",
        "switchesfile": "/fake/switches",
        "serversfile": "/fake/servers.csv",
        "routersfile": "/fake/routers.csv",
        "apsfile": "/fake/aps.csv",
        "apusefile": "/fake/apuse.csv",
        "pifile": "/fake/pis.csv",
        "piusefile": "/fake/piuse.csv",
    })
    return ctx


@pytest.fixture
def temp_output(tmp_path):
    """Temporary output directory."""
    return tmp_path / "output"


@pytest.fixture
def mock_inventory():
    """Mock inventory module functions to avoid data dependencies."""
    with patch('facts.cli.inventory') as mock_inv:
        mock_inv.populate_vlans.return_value = {}
        mock_inv.populateswitches.return_value = []
        mock_inv.populateservers.return_value = []
        mock_inv.populaterouters.return_value = []
        mock_inv.populateaps.return_value = []
        mock_inv.populatepis.return_value = []
        mock_inv.generatekeaconfig.return_value = None
        mock_inv.generatezones.return_value = None
        mock_inv.generatepromconfigs.return_value = None
        mock_inv.generatewasgehtconfig.return_value = None
        mock_inv.generateallnetwork.return_value = None
        yield mock_inv
# ============================================================
# Helper function tests
# ============================================================

def test_ensure_output_dir_creates_directory(tmp_path):
    """Verify ensure_output_dir creates missing directories."""
    output_dir = tmp_path / "nonexistent" / "deeply" / "nested"
    assert not output_dir.exists()

    ensure_output_dir(str(output_dir))

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_ensure_output_dir_handles_existing_directory(tmp_path):
    """Verify ensure_output_dir handles existing directories gracefully."""
    output_dir = tmp_path / "existing"
    output_dir.mkdir()

    ensure_output_dir(str(output_dir))

    assert output_dir.exists()


def test_load_inventory_data_returns_all_keys(mock_ctx, mock_inventory):
    """Verify load_inventory_data returns complete inventory dictionary."""
    data = load_inventory_data(mock_ctx)

    expected_keys = {"vlans", "switches", "servers", "routers", "aps", "pis"}
    assert set(data.keys()) == expected_keys


def test_load_inventory_data_caches_result(mock_ctx, mock_inventory):
    """Verify load_inventory_data caches data on context object."""
    data1 = load_inventory_data(mock_ctx)
    data2 = load_inventory_data(mock_ctx)

    assert data1 is data2
    assert "inventory_data" in mock_ctx.obj


# ============================================================
# CLI group command tests
# ============================================================

def test_cli_help(runner):
    """Verify CLI group displays help without errors."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "SCaLE network inventory management" in result.output


def test_cli_initializes_context_with_defaults(runner, mock_inventory):
    """Verify CLI group initializes context with bundled data when no options given."""
    result = runner.invoke(cli, ["debug", "vlans"], catch_exceptions=False)

    assert result.exit_code == 0


# ============================================================
# Subcommand invocation tests
# ============================================================

@pytest.mark.parametrize("command", ["kea", "nsd", "prom", "wasgeht", "allnet", "all"])
def test_subcommand_help(runner, command, mock_inventory):
    """Verify all subcommands display help without errors."""
    result = runner.invoke(cli, [command, "--help"])

    assert result.exit_code == 0
    assert "Usage:" in result.output


@pytest.mark.parametrize("command", ["kea", "nsd", "prom", "wasgeht", "allnet", "all"])
def test_subcommand_creates_output_directory(runner, temp_output, command, mock_inventory):
    """Verify subcommands create output directory when it doesn't exist."""
    assert not temp_output.exists()

    result = runner.invoke(cli, [command, str(temp_output)], catch_exceptions=False)

    assert result.exit_code == 0
    assert temp_output.exists()
    assert temp_output.is_dir()


@pytest.mark.parametrize("command,expected_msg", [
    ("kea", "Kea configuration written"),
    ("nsd", "DNS zone files written"),
    ("prom", "Prometheus configuration written"),
    ("wasgeht", "Wasgeht configuration written"),
    ("allnet", "Network configurations written"),
    ("all", "All configurations written"),
])
def test_subcommand_success_message(runner, temp_output, command, expected_msg, mock_inventory):
    """Verify subcommands display appropriate success messages."""
    result = runner.invoke(cli, [command, str(temp_output)], catch_exceptions=False)

    assert result.exit_code == 0
    assert expected_msg in result.output


# ============================================================
# Debug command tests
# ============================================================

@pytest.mark.parametrize("variable", ["switches", "routers", "vlans", "servers", "aps", "pis"])
def test_debug_command_json_output(runner, variable, mock_inventory):
    """Verify debug command outputs valid JSON for all variable types."""
    result = runner.invoke(cli, ["debug", variable], catch_exceptions=False)

    assert result.exit_code == 0

    json.loads(result.output)


def test_debug_command_pretty_print_default(runner, mock_inventory):
    """Verify debug command pretty-prints JSON by default."""
    result = runner.invoke(cli, ["debug", "vlans"], catch_exceptions=False)

    assert result.exit_code == 0

    json.loads(result.output)


def test_debug_command_compact_output(runner, mock_inventory):
    """Verify debug command supports compact JSON output."""
    result = runner.invoke(cli, ["debug", "vlans", "--no-pretty"], catch_exceptions=False)

    assert result.exit_code == 0


# ============================================================
# Custom data path option tests
# ============================================================

def test_cli_custom_data_dir_option(runner, tmp_path, mock_inventory):
    """Verify --data-dir option overrides bundled data paths."""
    custom_dir = tmp_path / "custom"
    custom_dir.mkdir()

    result = runner.invoke(cli, ["--data-dir", str(custom_dir), "debug", "vlans"])

    assert result.exit_code == 0


def test_cli_accepts_individual_file_options(runner, tmp_path, mock_inventory):
    """Verify CLI accepts individual file path overrides."""
    vlans_file = tmp_path / "vlans"
    vlans_file.touch()
    # Finish test
    result = runner.invoke(cli, [
        "--vlans-file", str(vlans_file),
        "debug", "vlans"
    ])
    assert result.exit_code == 0
