"""Tests for template_loader module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import jinja2
import pytest

from facts.template_loader import get_template_loader, render_template


def test_get_template_loader_returns_environment():
    """Verify get_template_loader returns a Jinja2 Environment."""
    env = get_template_loader()

    assert isinstance(env, jinja2.Environment)
    assert env.loader is not None


def test_get_template_loader_can_load_templates():
    """Verify template loader can access actual template files."""
    env = get_template_loader()

    template = env.get_template("dns_zone_records.jinja2")
    assert template is not None


def test_get_template_loader_filesystem_fallback(tmp_path, monkeypatch):
    """Verify get_template_loader falls back to filesystem when package resources unavailable."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    test_template = templates_dir / "test.jinja2"
    test_template.write_text("Hello {{ name }}")

    with patch("facts.template_loader.files", side_effect=ModuleNotFoundError):
        with monkeypatch.context() as m:
            m.setattr("facts.template_loader.Path", lambda x: tmp_path / "template_loader.py")
            env = get_template_loader()

            assert isinstance(env, jinja2.Environment)


def test_get_template_loader_raises_when_no_templates():
    """Verify get_template_loader raises RuntimeError when templates directory not found."""
    with patch("facts.template_loader.files", side_effect=ModuleNotFoundError):
        with patch("facts.template_loader.Path") as mock_path:
            mock_template_path = MagicMock()
            mock_template_path.is_dir.return_value = False
            mock_path.return_value.parent.__truediv__.return_value = mock_template_path

            with pytest.raises(RuntimeError, match="Could not find templates directory"):
                get_template_loader()


def test_render_template_with_context():
    """Verify render_template renders template with provided context."""
    result = render_template(
        "dns_zone_records.jinja2",
        batch=[
            {
                "name": "test-server",
                "ipv4": "10.0.0.1",
                "ipv6": "2001:db8::1",
                "num": None,
                "fqdn": "test-server.example.com",
                "aliases": ["alias1", "alias2"],
            }
        ]
    )

    assert "test-server" in result
    assert "10.0.0.1" in result
    assert "2001:db8::1" in result
    assert "alias1" in result
    assert "alias2" in result
    assert "AAAA" in result
    assert "A" in result
    assert "CNAME" in result


def test_render_template_empty_batch():
    """Verify render_template handles empty batch gracefully."""
    result = render_template("dns_zone_records.jinja2", batch=[])

    assert result.strip() == ""


def test_render_template_ipv4_only():
    """Verify render_template renders IPv4-only records correctly."""
    result = render_template(
        "dns_zone_records.jinja2",
        batch=[
            {
                "name": "server1",
                "ipv4": "192.168.1.1",
                "ipv6": None,
                "num": None,
                "fqdn": "server1.local",
                "aliases": [],
            }
        ]
    )

    assert "server1" in result
    assert "192.168.1.1" in result
    assert "IN  A" in result
    assert "AAAA" not in result


def test_render_template_ipv6_only():
    """Verify render_template renders IPv6-only records correctly."""
    result = render_template(
        "dns_zone_records.jinja2",
        batch=[
            {
                "name": "server2",
                "ipv4": None,
                "ipv6": "fe80::1",
                "num": None,
                "fqdn": "server2.local",
                "aliases": [],
            }
        ]
    )

    assert "server2" in result
    assert "fe80::1" in result
    assert "IN  AAAA" in result
    assert "192.168" not in result


def test_render_template_with_switch_number():
    """Verify render_template renders switch CNAME records correctly."""
    result = render_template(
        "dns_zone_records.jinja2",
        batch=[
            {
                "name": "sw-test",
                "ipv4": "10.0.0.5",
                "ipv6": None,
                "num": 42,
                "fqdn": "sw-test.local",
                "aliases": [],
            }
        ]
    )

    assert "switch42" in result
    assert "CNAME" in result
    assert "sw-test.local" in result


def test_render_template_ptr_records():
    """Verify render_template can render PTR record templates."""
    result = render_template(
        "dns_ptr_records.jinja2",
        ip="ipv4",
        batch=[
            {
                "ipv4ptr": "1.0.0.10.in-addr.arpa",
                "fqdn": "host1.example.com",
            },
            {
                "ipv4ptr": "2.0.0.10.in-addr.arpa",
                "fqdn": "host2.example.com",
            }
        ]
    )

    assert "1.0.0.10.in-addr.arpa" in result
    assert "host1.example.com" in result
    assert "2.0.0.10.in-addr.arpa" in result
    assert "host2.example.com" in result
    assert "PTR" in result


def test_render_template_multiple_items():
    """Verify render_template handles multiple items in batch."""
    result = render_template(
        "dns_zone_records.jinja2",
        batch=[
            {
                "name": "host1",
                "ipv4": "10.0.0.1",
                "ipv6": None,
                "num": None,
                "fqdn": "host1.local",
                "aliases": [],
            },
            {
                "name": "host2",
                "ipv4": "10.0.0.2",
                "ipv6": None,
                "num": None,
                "fqdn": "host2.local",
                "aliases": [],
            },
            {
                "name": "host3",
                "ipv4": "10.0.0.3",
                "ipv6": None,
                "num": None,
                "fqdn": "host3.local",
                "aliases": [],
            },
        ]
    )

    assert "host1" in result
    assert "host2" in result
    assert "host3" in result
    assert "10.0.0.1" in result
    assert "10.0.0.2" in result
    assert "10.0.0.3" in result
