#!/usr/bin/env python3
"""
CSV data source tests
"""

import os
import facts.datasource as ds


def test_apuse_csv(pkg_path):
    """test apuse.csv"""
    meta = {
        "file": pkg_path("aps/apuse.csv"),
        "header": True,
        "count": 9,
        "cols": [
            ds.is_valid_hostname,
            ds.is_in_ap_list,
            ds.is_valid_ipv4_address,
            ds.is_valid_wifi_24ghz_chan,
            ds.is_valid_wifi_5ghz_chan,
            ds.is_non_negative_int,  # config version
            ds.is_non_negative_int,  # map id
            ds.is_valid_map_coordinate,
            ds.is_valid_map_coordinate,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_aps_csv(pkg_path):
    """test aps.csv"""
    meta = {
        "file": pkg_path("aps/aps.csv"),
        "header": True,
        "count": 2,
        "cols": [
            ds.is_untested,
            ds.is_valid_mac_address,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_pis_csv(pkg_path):
    """test pis.csv"""
    meta = {
        "file": pkg_path("pi/pis.csv"),
        "header": True,
        "count": 3,
        "cols": [
            ds.is_valid_asset_id,
            ds.is_valid_mac_address,
            ds.is_valid_ipv6_suffix,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_piuse_csv(pkg_path):
    """test piuse.csv"""
    meta = {
        "file": pkg_path("pi/piuse.csv"),
        "header": True,
        "count": 3,
        "cols": [
            ds.is_valid_hostname,
            ds.is_valid_asset_id,
            ds.is_valid_pi_vlan,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_routerlist_csv(pkg_path):
    """test routerlist.csv"""
    meta = {
        "file": pkg_path("routers/routerlist.csv"),
        "header": True,
        "count": 2,
        "cols": [
            ds.is_valid_hostname,
            ds.is_valid_ipv6_address,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_serverlist_csv(pkg_path):
    """test serverlist.csv"""
    meta = {
        "file": pkg_path("servers/serverlist.csv"),
        "header": True,
        "count": 5,
        "cols": [
            ds.is_valid_hostname,
            ds.is_valid_mac_address,
            ds.is_valid_ipv6_address,
            ds.is_valid_ipv4_address,
            ds.is_untested,
        ],
    }
    result, err = ds.test_csvfile(meta)
    assert result, err


def test_switchtypes_tsv(pkg_path):
    """test switchtypes"""
    meta = {
        "file": pkg_path("switch-config/switchtypes"),
        "header": False,
        "count": "9+",
        "cols": [
            ds.is_valid_hostname,
            ds.is_non_negative_int,
            ds.is_non_negative_int,
            ds.is_valid_ipv6_address,
            ds.is_valid_switch_type,
            ds.is_valid_switch_hierarchy,
            ds.is_untested,
            ds.is_valid_switch_model,
            ds.is_valid_mac_address,
        ],
    }
    result, err = ds.test_tsvfile(meta)
    assert result, err


def test_vlansd_tsv(pkg_path):
    """test vlans.d/"""

    packaged_vlansd = pkg_path("switch-config/vlans.d")
    if os.path.isdir(packaged_vlansd):
        vlansddir = str(packaged_vlansd)
    else:
        vlansddir = "../switch-configuration/config/vlans.d"

    for filename in os.listdir(vlansddir):
        meta = {
            "file": os.path.join(vlansddir, filename),
            "header": False,
            "count": "6+",
            "cols": [
                ds.is_untested,
                ds.is_untested,
                ds.is_untested,
                ds.is_valid_ipv6_subnet,
                ds.is_valid_ipv4_subnet,
                ds.is_untested,
            ],
        }
        result, err = ds.test_tsvfile(meta)
        assert result, err
