#!/usr/bin/env python3
"""
Comprehensive validator tests for datasource module.

Tests all validator functions with various valid and invalid inputs
using pytest.mark.parametrize for thorough coverage.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

import facts.datasource as ds


# =============================================================================
# Validator Tests
# =============================================================================


@pytest.mark.parametrize(
    "hostname,expected",
    [
        # Valid hostnames
        ("host", True),
        ("host123", True),
        ("host-123", True),
        ("h", True),
        ("123abc", True),
        ("a-b-c", True),
        ("HOST", True),
        ("Host-123-ABC", True),
        # Invalid hostnames
        ("-host", False),
        ("host-", False),
        ("-", False),
        ("--", False),
        ("host_123", False),
        ("host.name", False),
        ("host name", False),
        ("", False),
        ("host-", False),
        ("-host-", False),
    ],
)
def test_is_valid_hostname(hostname, expected):
    """Test hostname validator with various valid and invalid inputs."""
    assert ds.is_valid_hostname(hostname) == expected


@pytest.mark.parametrize(
    "asset_id,expected",
    [
        ("asset123", True),
        ("ASSET-123", True),
        ("a", True),
        ("-asset", False),
        ("asset-", False),
        ("", False),
    ],
)
def test_is_valid_asset_id(asset_id, expected):
    """Test asset ID validator (same as hostname)."""
    assert ds.is_valid_asset_id(asset_id) == expected


@pytest.mark.parametrize(
    "model,expected",
    [
        # Valid models
        ("ex2200-48p", True),
        ("ex2200-48t", True),
        ("ex2200-24p", True),
        ("ex2200-24t", True),
        ("ex4300-48p", True),
        ("ex2300-c-12t-vc", True),
        # Invalid models
        ("ex9999-48p", False),
        ("invalid", False),
        ("", False),
        ("EX2200-48P", False),  # case sensitive
    ],
)
def test_is_valid_switch_model(model, expected):
    """Test switch model validator."""
    assert ds.is_valid_switch_model(model) == expected


@pytest.mark.parametrize(
    "ipv4,expected",
    [
        # Valid IPv4
        ("192.168.1.1", True),
        ("10.0.0.1", True),
        ("255.255.255.255", True),
        ("0.0.0.0", True),
        ("172.16.0.1", True),
        # Invalid IPv4
        ("256.1.1.1", False),
        ("192.168.1", False),
        ("192.168.1.1.1", False),
        ("invalid", False),
        ("", False),
        ("192.168.1.256", False),
        ("a.b.c.d", False),
    ],
)
def test_is_valid_ipv4_address(ipv4, expected):
    """Test IPv4 address validator."""
    assert ds.is_valid_ipv4_address(ipv4) == expected


@pytest.mark.parametrize(
    "ipv6,expected",
    [
        # Valid IPv6
        ("2001:db8::1", True),
        ("fe80::1", True),
        ("::1", True),
        ("::", True),
        ("2001:db8:0:0:0:0:0:1", True),
        ("ff02::1", True),
        # Invalid IPv6
        ("gggg::1", False),
        ("192.168.1.1", False),
        ("invalid", False),
        ("", False),
        (":::::::", False),
        ("2001:db8::g", False),
    ],
)
def test_is_valid_ipv6_address(ipv6, expected):
    """Test IPv6 address validator."""
    assert ds.is_valid_ipv6_address(ipv6) == expected


@pytest.mark.parametrize(
    "suffix,expected",
    [
        # Valid suffixes
        ("1", True),
        ("abcd:1234", True),
        ("1:2:3:4", True),
        # Invalid suffixes
        ("::1", False),  # double colon would create fe80::::1 which is invalid
        ("gggg", False),
        ("", True),  # empty becomes fe80:: which is valid
        ("invalid", False),
    ],
)
def test_is_valid_ipv6_suffix(suffix, expected):
    """Test IPv6 suffix validator."""
    assert ds.is_valid_ipv6_suffix(suffix) == expected


@pytest.mark.parametrize(
    "subnet,expected",
    [
        # Valid IPv4 subnets
        ("192.168.1.0/24", True),
        ("10.0.0.0/8", True),
        ("172.16.0.0/12", True),
        ("192.168.1.0/32", True),
        ("192.168.1.0", True),  # defaults to /32 which is valid
        # Invalid IPv4 subnets
        ("192.168.1.1/24", False),  # not network address (strict=True)
        ("192.168.1.0/33", False),  # invalid prefix length
        ("invalid", False),
        ("", False),
    ],
)
def test_is_valid_ipv4_subnet(subnet, expected):
    """Test IPv4 subnet validator."""
    assert ds.is_valid_ipv4_subnet(subnet) == expected


@pytest.mark.parametrize(
    "subnet,expected",
    [
        # Valid IPv6 subnets
        ("2001:db8::/32", True),
        ("fe80::/10", True),
        ("::1/128", True),
        ("::/0", True),
        ("2001:db8::", True),  # defaults to /128 which is valid
        # Invalid IPv6 subnets
        ("2001:db8::1/32", False),  # not network address (strict=True)
        ("invalid", False),
        ("", False),
        ("2001:db8::/129", False),  # invalid prefix length
    ],
)
def test_is_valid_ipv6_subnet(subnet, expected):
    """Test IPv6 subnet validator."""
    assert ds.is_valid_ipv6_subnet(subnet) == expected


@pytest.mark.parametrize(
    "mac,expected",
    [
        # Valid MAC addresses
        ("00:11:22:33:44:55", True),
        ("AA:BB:CC:DD:EE:FF", True),
        ("aa:bb:cc:dd:ee:ff", True),
        ("01:23:45:67:89:ab", True),
        # Invalid MAC addresses
        ("00:11:22:33:44", False),  # too short
        ("00:11:22:33:44:55:66", False),  # too long
        ("00-11-22-33-44-55", False),  # wrong separator
        ("00:11:22:33:44:GG", False),  # invalid hex
        ("invalid", False),
        ("", False),
    ],
)
def test_is_valid_mac_address(mac, expected):
    """Test MAC address validator."""
    assert ds.is_valid_mac_address(mac) == expected


@pytest.mark.parametrize(
    "channel,expected",
    [
        # Valid 2.4GHz channels
        (1, True),
        (6, True),
        (11, True),
        ("1", True),
        ("6", True),
        ("11", True),
        # Invalid 2.4GHz channels
        (2, False),
        (7, False),
        (13, False),
        ("2", False),
        ("invalid", False),
        ("", False),
        (-1, False),
        ("-1", False),
    ],
)
def test_is_valid_wifi_24ghz_chan(channel, expected):
    """Test 2.4GHz WiFi channel validator."""
    assert ds.is_valid_wifi_24ghz_chan(channel) == expected


@pytest.mark.parametrize(
    "channel,expected",
    [
        # Valid 5GHz channels
        (36, True),
        (40, True),
        (149, True),
        (165, True),
        ("36", True),
        ("149", True),
        # DFS channels
        (52, True),
        (100, True),
        (140, True),
        # Invalid 5GHz channels
        (1, False),
        (6, False),
        (200, False),
        ("invalid", False),
        ("", False),
        (-1, False),
    ],
)
def test_is_valid_wifi_5ghz_chan(channel, expected):
    """Test 5GHz WiFi channel validator."""
    assert ds.is_valid_wifi_5ghz_chan(channel) == expected


@pytest.mark.parametrize(
    "vlan,expected",
    [
        # Valid PI VLANs
        (107, True),
        (110, True),
        (506, True),
        (507, True),
        ("107", True),
        ("507", True),
        # Invalid PI VLANs
        (1, False),
        (100, False),
        (999, False),
        ("invalid", False),
        ("", False),
        (-1, False),
    ],
)
def test_is_valid_pi_vlan(vlan, expected):
    """Test PI VLAN validator."""
    assert ds.is_valid_pi_vlan(vlan) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        # Valid non-negative integers
        (0, True),
        (1, True),
        (123, True),
        (999999, True),
        ("0", True),
        ("1", True),
        ("123", True),
        # Invalid non-negative integers
        (-1, False),
        (-999, False),
        ("-1", False),
        ("invalid", False),
        ("", False),
        ("12.34", False),
        ("12a", False),
    ],
)
def test_is_non_negative_int(value, expected):
    """Test non-negative integer validator."""
    assert ds.is_non_negative_int(value) == expected


@pytest.mark.parametrize(
    "hierarchy,expected",
    [
        # Valid hierarchies
        ("A.1", True),
        ("ABC.9", True),
        ("XYZ.0", True),
        ("AB.5", True),
        # Invalid hierarchies
        ("a.1", False),  # lowercase
        ("A.10", False),  # two digits
        ("ABC", False),  # no dot
        ("ABC.", False),  # no number
        (".1", False),  # no letters
        ("A-1", False),  # wrong separator
        ("", False),
    ],
)
def test_is_valid_switch_hierarchy(hierarchy, expected):
    """Test switch hierarchy validator."""
    assert ds.is_valid_switch_hierarchy(hierarchy) == expected


@pytest.mark.parametrize(
    "coord,expected",
    [
        # Valid coordinates
        (0, True),
        (50, True),
        (100, True),
        (50.5, True),
        (25.25, True),
        (0.0, True),
        (100.0, True),
        ("50", True),
        ("50.5", True),
        ("25.25", True),
        # Invalid coordinates
        (-1, False),
        (101, False),
        (50.123, False),  # more than 2 decimal places
        ("invalid", False),
        ("", False),
        (None, False),
        ([], False),
        ({}, False),
    ],
)
def test_is_valid_map_coordinate(coord, expected):
    """Test map coordinate validator."""
    assert ds.is_valid_map_coordinate(coord) == expected


def test_is_untested():
    """Test that is_untested always returns True."""
    assert ds.is_untested(None) is True
    assert ds.is_untested("") is True
    assert ds.is_untested("anything") is True
    assert ds.is_untested(123) is True


# =============================================================================
# Preprocessing Function Tests
# =============================================================================


@pytest.mark.parametrize(
    "lines,expected",
    [
        # No continuation
        (["line1\n", "line2\n"], ["line1", "line2"]),
        # Single continuation
        (["line1 \\\n", "continued\n"], ["line1 continued"]),
        # Multiple continuations
        (["a \\\n", "b \\\n", "c\n"], ["a b c"]),
        # Mixed
        (["normal\n", "cont \\\n", "inued\n", "normal2\n"], ["normal", "cont inued", "normal2"]),
        # Trailing continuation
        (["line \\\n"], ["line"]),
        # Empty lines
        ([], []),
        # Whitespace handling
        (["line \\\n", "  continued\n"], ["line continued"]),
    ],
)
def test_join_continuation_lines(lines, expected):
    """Test continuation line joining."""
    assert ds.join_continuation_lines(lines) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        # Empty and whitespace
        ("", True),
        ("   ", True),
        ("\t", True),
        ("\n", True),
        ("  \t  \n", True),
        # Non-blank
        ("text", False),
        ("  text  ", False),
        ("a", False),
    ],
)
def test_is_blank(line, expected):
    """Test blank line detection."""
    assert ds.is_blank(line) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        # // comments
        ("data // comment", "data "),
        ("// full comment", ""),
        ("data", "data"),
        # # comments
        ("data # comment", "data "),
        ("# full comment", ""),
        # Mixed
        ("data // comment # more", "data "),
        ("data # comment // more", "data "),
    ],
)
def test_strip_comments(line, expected):
    """Test comment stripping."""
    assert ds.strip_comments(line) == expected


@pytest.mark.parametrize(
    "line,expected",
    [
        # Single tab
        ("a\tb", "a\tb"),
        # Multiple tabs
        ("a\t\tb", "a\tb"),
        ("a\t\t\tb", "a\tb"),
        # Mixed
        ("a\tb\t\tc\td", "a\tb\tc\td"),
        # No tabs
        ("abc", "abc"),
    ],
)
def test_collapse_tabs(line, expected):
    """Test tab collapsing."""
    assert ds.collapse_tabs(line) == expected


def test_preprocess_line():
    """Test full line preprocessing."""
    line = "data\t\t\tvalue // comment"
    result = ds.preprocess_line(line)
    assert result == "data\tvalue "


def test_read_config_lines(testdata_dir):
    """Test reading and preprocessing a config file."""
    # Create a test file with various features
    test_file = testdata_dir / "test_config.tsv"
    test_file.write_text(
        "field1\tfield2\n"
        "# comment line\n"
        "value1\tvalue2 // inline comment\n"
        "cont \\\n"
        "inued\tvalue3\n"
        "\n"
        "value4\t\t\tvalue5\n"
    )

    lines = ds.read_config_lines(str(test_file))

    # Should have: header, value line, continued line, last line
    assert len(lines) == 4
    assert lines[0] == "field1\tfield2"
    assert lines[1] == "value1\tvalue2 "
    assert lines[2] == "cont inued\tvalue3"
    assert lines[3] == "value4\tvalue5"


# =============================================================================
# DataFrame Function Tests
# =============================================================================


@pytest.mark.parametrize(
    "lines,sep,expected_shape",
    [
        # Normal case
        (["a\tb\tc", "1\t2\t3"], "\t", (2, 3)),
        # Uneven columns (padding)
        (["a\tb", "1\t2\t3"], "\t", (2, 3)),
        # Empty lines list
        ([], "\t", (0, 0)),
        # CSV separator
        (["a,b,c", "1,2,3"], ",", (2, 3)),
    ],
)
def test_lines_to_dataframe(lines, sep, expected_shape):
    """Test converting lines to DataFrame."""
    df = ds.lines_to_dataframe(lines, sep=sep)
    assert df.shape == expected_shape


def test_lines_to_dataframe_empty():
    """Test lines_to_dataframe with empty input."""
    df = ds.lines_to_dataframe([])
    assert df.empty


def test_lines_to_dataframe_padding():
    """Test that short rows are padded."""
    lines = ["a\tb\tc", "1\t2"]
    df = ds.lines_to_dataframe(lines)
    assert df.shape == (2, 3)
    assert df.iloc[1, 2] == ""


@pytest.mark.parametrize(
    "col_count,count_spec,should_pass",
    [
        # Exact match
        (3, 3, True),
        (5, 5, True),
        # Mismatch
        (3, 5, False),
        (5, 3, False),
        # Minimum count (n+)
        (3, "3+", True),
        (5, "3+", True),
        (5, "5+", True),
        (3, "5+", False),
    ],
)
def test_validate_column_count(col_count, count_spec, should_pass):
    """Test column count validation."""
    df = pd.DataFrame([[1] * col_count])
    ok, err = ds.validate_column_count(df, count_spec, "test.csv")
    assert ok == should_pass
    if not should_pass:
        assert "col count" in err


def test_validate_dataframe_with_invalid_data():
    """Test DataFrame validation with invalid data."""
    df = pd.DataFrame([["valid-host"], ["invalid host!"]])
    ok, err = ds.validate_dataframe(
        df,
        [ds.is_valid_hostname],
        "test.csv",
        skip_header=False
    )
    assert not ok
    assert "invalid host!" in err
    assert "is_valid_hostname" in err


def test_validate_dataframe_with_skip_header():
    """Test DataFrame validation skipping header row."""
    df = pd.DataFrame([["Header"], ["valid-host"]])
    ok, err = ds.validate_dataframe(
        df,
        [ds.is_valid_hostname],
        "test.csv",
        skip_header=True
    )
    assert ok


def test_validate_dataframe_with_none_validator():
    """Test DataFrame validation with None validators."""
    df = pd.DataFrame([["anything"], ["anything-else"]])
    ok, err = ds.validate_dataframe(
        df,
        [None],
        "test.csv",
    )
    assert ok


def test_validate_dataframe_beyond_columns():
    """Test DataFrame validation with more validators than columns."""
    df = pd.DataFrame([["host"]])
    ok, err = ds.validate_dataframe(
        df,
        [ds.is_valid_hostname, ds.is_valid_ipv4_address],
        "test.csv",
    )
    assert ok  # Should not fail, just skip extra validators


# =============================================================================
# High-Level Test Function Tests
# =============================================================================


def test_test_csvfile_file_not_found(tmp_path):
    """Test test_csvfile with non-existent file."""
    meta = {
        "file": tmp_path / "nonexistent.csv",
        "header": True,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_csvfile(meta)
    assert not ok
    assert "failed to read" in err.lower()


def test_test_csvfile_empty_file(tmp_path):
    """Test test_csvfile with empty file."""
    test_file = tmp_path / "empty.csv"
    test_file.write_text("")

    meta = {
        "file": test_file,
        "header": True,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_csvfile(meta)
    assert not ok
    assert "failed to read" in err.lower()


def test_test_csvfile_invalid_column_count(tmp_path):
    """Test test_csvfile with wrong column count."""
    test_file = tmp_path / "test.csv"
    test_file.write_text("col1,col2,col3\nval1,val2,val3")

    meta = {
        "file": test_file,
        "header": True,
        "count": 2,  # expects 2, but file has 3
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_csvfile(meta)
    assert not ok
    assert "col count" in err


def test_test_csvfile_invalid_data(tmp_path):
    """Test test_csvfile with invalid data."""
    test_file = tmp_path / "test.csv"
    test_file.write_text("hostname,ip\nvalid-host,192.168.1.1\ninvalid!,not-an-ip")

    meta = {
        "file": test_file,
        "header": True,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_csvfile(meta)
    assert not ok
    assert "invalid!" in err or "not-an-ip" in err


def test_test_tsvfile_file_not_found(tmp_path):
    """Test test_tsvfile with non-existent file."""
    meta = {
        "file": tmp_path / "nonexistent.tsv",
        "header": False,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_tsvfile(meta)
    assert not ok
    assert "failed to read" in err.lower()


def test_test_tsvfile_empty_file(tmp_path):
    """Test test_tsvfile with empty file."""
    test_file = tmp_path / "empty.tsv"
    test_file.write_text("")

    meta = {
        "file": test_file,
        "header": False,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_tsvfile(meta)
    assert ok  # Empty file is valid for TSV


def test_test_tsvfile_invalid_column_count(tmp_path):
    """Test test_tsvfile with wrong column count."""
    test_file = tmp_path / "test.tsv"
    test_file.write_text("col1\tcol2\tcol3\nval1\tval2\tval3")

    meta = {
        "file": test_file,
        "header": False,
        "count": 2,  # expects 2, but file has 3
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_tsvfile(meta)
    assert not ok
    assert "col count" in err


def test_test_tsvfile_with_comments_and_continuations(tmp_path):
    """Test test_tsvfile with comments and continuation lines."""
    test_file = tmp_path / "test.tsv"
    test_file.write_text(
        "# Comment line\n"
        "host1\t192.168.1.1\n"
        "host2\t192.168.1.2 // inline comment\n"
    )

    meta = {
        "file": test_file,
        "header": False,
        "count": 2,
        "cols": [ds.is_valid_hostname, ds.is_valid_ipv4_address],
    }
    ok, err = ds.test_tsvfile(meta)
    assert ok


def test_first_existing_dir(tmp_path):
    """Test _first_existing_dir helper."""
    existing_dir = tmp_path / "exists"
    existing_dir.mkdir()
    non_existing = tmp_path / "not-exists"

    result = ds._first_existing_dir([non_existing, existing_dir])
    assert result == existing_dir

    result = ds._first_existing_dir([non_existing])
    assert result is None
