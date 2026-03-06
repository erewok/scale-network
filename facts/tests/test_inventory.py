#!/usr/bin/env python3
"""
Tests for inventory.py
"""

import json

import pytest

import facts.inventory as inventory


@pytest.mark.parametrize(
    "prefix,bitmask,expected",
    [
        (
            "2001:470:f325:504::",
            64,
            ["2001:470:f325:504:d8c::1", "2001:470:f325:504:d8c::800"],
        ),
        (
            "2001:470:f325:111::",
            64,
            ["2001:470:f325:111:d8c::1", "2001:470:f325:111:d8c::800"],
        ),
        ("::", 0, ["", ""]),
    ],
)
def test_dhcp6ranges(prefix, bitmask, expected):
    """test cases for the dhcp6ranges() function"""
    assert inventory.dhcp6ranges(prefix, bitmask) == expected


@pytest.mark.parametrize(
    "prefix,bitmask,expected",
    [
        ("10.0.136.0", 21, ["10.0.136.80", "10.0.143.254", "10.0.136.1"]),
        ("10.0.2.0", 24, ["10.0.2.80", "10.0.2.254", "10.0.2.1"]),
        ("0.0.0.0", 0, ["", "", "", "", ""]),
        ("38.98.46.128", 25, ["", "", "", "", ""]),
    ],
)
def test_dhcp4ranges(prefix, bitmask, expected):
    """test cases for the dhcp4ranges() function"""
    assert inventory.dhcp4ranges(prefix, bitmask) == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            {
                "id": "504",
                "name": "cfCTF",
                "v6cidr": "2001:470:f325:504::/64",
                "v4cidr": "10.128.4.0/24",
                "description": "Capture the Flag",
                "building": "Conference",
            },
            {
                "name": "cfCTF",
                "id": "504",
                "ipv6prefix": "2001:470:f325:504::",
                "ipv6bitmask": "64",
                "ipv4prefix": "10.128.4.0",
                "ipv4bitmask": "24",
                "building": "Conference",
                "description": "Capture the Flag",
                "ipv6dhcpStart": "2001:470:f325:504:d8c::1",
                "ipv6dhcpEnd": "2001:470:f325:504:d8c::800",
                "ipv4dhcpStart": "10.128.4.80",
                "ipv4dhcpEnd": "10.128.4.254",
                "ipv4router": "10.128.4.1",
                "ipv4netmask": "255.255.255.0",
                "ipv6dns1": "",
                "ipv6dns2": "",
                "ipv4dns1": "",
                "ipv4dns2": "",
            },
        ),
        (
            {
                "id": "ABC",
                "name": "BadVLAN",
                "v6cidr": "2001:470:f325:504::/64",
                "v4cidr": "10.128.4.0/24",
                "description": "Bad VLAN",
            },
            None,
        ),
    ],
)
def test_make_vlan(config, expected):
    """test case for make_vlan()"""
    assert inventory.make_vlan(config) == expected


@pytest.mark.parametrize(
    "bitmask,expected",
    [
        (16, None),
        (17, "255.255.128.0"),
        (18, "255.255.192.0"),
        (19, "255.255.224.0"),
        (20, "255.255.240.0"),
        (21, "255.255.248.0"),
        (22, "255.255.252.0"),
        (23, "255.255.254.0"),
        (24, "255.255.255.0"),
        (25, None),
    ],
)
def test_bitmasktonetmask(bitmask, expected):
    """test cases for the bitmasktonetmask() function"""
    assert inventory.bitmasktonetmask(bitmask) == expected


@pytest.mark.parametrize(
    "vlan_range,nameprefix,v6cidr,v4cidr,building,expected",
    [
        (
            "200-201",
            "test_vlan_",
            "2001:470:f325::/48",
            "10.2.0.0/15",
            "Expo",
            [
                {
                    "name": "test_vlan_200",
                    "id": "200",
                    "ipv6prefix": "2001:470:f325:200::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.2.0.0",
                    "ipv4bitmask": "24",
                    "building": "Expo",
                    "description": "Dynamic vlan 200",
                    "ipv6dhcpStart": "2001:470:f325:200:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:200:d8c::800",
                    "ipv4dhcpStart": "10.2.0.80",
                    "ipv4dhcpEnd": "10.2.0.254",
                    "ipv4router": "10.2.0.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "test_vlan_201",
                    "id": "201",
                    "ipv6prefix": "2001:470:f325:201::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.2.1.0",
                    "ipv4bitmask": "24",
                    "building": "Expo",
                    "description": "Dynamic vlan 201",
                    "ipv6dhcpStart": "2001:470:f325:201:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:201:d8c::800",
                    "ipv4dhcpStart": "10.2.1.80",
                    "ipv4dhcpEnd": "10.2.1.254",
                    "ipv4router": "10.2.1.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
            ],
        )
    ],
)
def test_gen_vlans(vlan_range, nameprefix, v6cidr, v4cidr, building, expected):
    """test cases for the gen_vlans() function"""
    result = inventory.gen_vlans(vlan_range, nameprefix, v6cidr, v4cidr, building)
    assert result == expected


@pytest.mark.parametrize(
    "ipaddr,expected",
    [
        ("10.128.3.5", "5.3.128.10.in-addr.arpa"),
        ("10.0.3.200", "200.3.0.10.in-addr.arpa"),
    ],
)
def test_ip4toptr(ipaddr, expected):
    """test cases for the ip4toptr() function"""
    assert inventory.ip4toptr(ipaddr) == expected


@pytest.mark.parametrize(
    "ipaddr,expected",
    [
        (
            "2001:470:f325:103::200:4",
            "4.0.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
        ),
        (
            "2001:470:f325:107:ad84:2d06:1dfe:7f67",
            "7.6.f.7.e.f.d.1.6.0.d.2.4.8.d.a.7.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
        ),
    ],
)
def test_ip6toptr(ipaddr, expected):
    """test cases for the ip6toptr() function"""
    assert inventory.ip6toptr(ipaddr) == expected


@pytest.mark.parametrize(
    "ipaddr,expected",
    [
        ("127.0.0.1", True),
        ("::1", True),
        ("10.1.1.1", True),
        ("2001:470:f325:107:8bfa:646e:811:241c", True),
        ("string", False),
        ("FFFF:VT40:f325:107:8bfa:646e:811:241c", False),
        ("256.0.0.1", False),
        ("2001:470:f325:107:8bfa:646e:811", False),
    ],
)
def test_isvalidip(ipaddr, expected):
    """test cases for the isvalidip() function"""
    assert inventory.isvalidip(ipaddr) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Rm101-102", ["rm101", "rm102"]),
        ("BallroomC", []),
    ],
)
def test_roomalias(name, expected):
    """test cases for the roomalias() function"""
    assert inventory.roomalias(name) == expected


@pytest.mark.parametrize(
    "vlans_path,expected",
    [
        (
            "testvlans",
            [
                {
                    "name": "exSCALE-SLOW",
                    "id": "100",
                    "ipv6prefix": "2001:470:f325:100::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.0.128.0",
                    "ipv4bitmask": "21",
                    "building": "Expo",
                    "description": "2.4G Wireless Network in Expo Center",
                    "ipv6dhcpStart": "2001:470:f325:100:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:100:d8c::800",
                    "ipv4dhcpStart": "10.0.128.80",
                    "ipv4dhcpEnd": "10.0.135.254",
                    "ipv4router": "10.0.128.1",
                    "ipv4netmask": "255.255.248.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "vendor_vlan_200",
                    "id": "200",
                    "ipv6prefix": "2001:470:f325:200::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.2.0.0",
                    "ipv4bitmask": "24",
                    "building": "Expo",
                    "description": "Dynamic vlan 200",
                    "ipv6dhcpStart": "2001:470:f325:200:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:200:d8c::800",
                    "ipv4dhcpStart": "10.2.0.80",
                    "ipv4dhcpEnd": "10.2.0.254",
                    "ipv4router": "10.2.0.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "vendor_vlan_201",
                    "id": "201",
                    "ipv6prefix": "2001:470:f325:201::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.2.1.0",
                    "ipv4bitmask": "24",
                    "building": "Expo",
                    "description": "Dynamic vlan 201",
                    "ipv6dhcpStart": "2001:470:f325:201:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:201:d8c::800",
                    "ipv4dhcpStart": "10.2.1.80",
                    "ipv4dhcpEnd": "10.2.1.254",
                    "ipv4router": "10.2.1.1",
                    "ipv4netmask": "255.255.255.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "cfSCALE-SLOW",
                    "id": "500",
                    "ipv6prefix": "2001:470:f325:500::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.128.128.0",
                    "ipv4bitmask": "21",
                    "building": "Conference",
                    "description": "2.4G Wireless Network in Conference Center",
                    "ipv6dhcpStart": "2001:470:f325:500:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:500:d8c::800",
                    "ipv4dhcpStart": "10.128.128.80",
                    "ipv4dhcpEnd": "10.128.135.254",
                    "ipv4router": "10.128.128.1",
                    "ipv4netmask": "255.255.248.0",
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
                {
                    "name": "cfSigns",
                    "id": "507",
                    "ipv6prefix": "2001:470:f325:507::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "0.0.0.0",
                    "ipv4bitmask": "0",
                    "building": "Conference",
                    "description": "Signs network (Conference Center) IPv6 Only",
                    "ipv6dhcpStart": "2001:470:f325:507:d8c::1",
                    "ipv6dhcpEnd": "2001:470:f325:507:d8c::800",
                    "ipv4dhcpStart": "",
                    "ipv4dhcpEnd": "",
                    "ipv4router": "",
                    "ipv4netmask": None,
                    "ipv6dns1": "",
                    "ipv6dns2": "",
                    "ipv4dns1": "",
                    "ipv4dns2": "",
                },
            ],
        )
    ],
)
def test_populate_vlans(testdata_dir, vlans_path, expected):
    # pylint: disable=line-too-long
    """test cases for the populate_vlans() function"""
    assert inventory.populate_vlans(str(testdata_dir) + "/", vlans_path) == expected


@pytest.mark.parametrize(
    "switches_file,expected",
    [
        (
            "testswitchtypes",
            [
                {
                    "name": "expo-catwalk",
                    "fqdn": "expo-catwalk.scale.lan",
                    "num": "16",
                    "ipv6": "2001:470:f325:103::200:16",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "6.1.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "switchtype": "Catwalk",
                    "hierarchy": "W.1",
                    "model": "ex4200-48p",
                    "aliases": [],
                },
                {
                    "name": "rm209-210",
                    "fqdn": "rm209-210.scale.lan",
                    "num": "17",
                    "ipv6": "2001:470:f325:503::200:17",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "7.1.0.0.0.0.2.0.0.0.0.0.0.0.0.0.3.0.5.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "switchtype": "cfRoom",
                    "hierarchy": "I.9",
                    "model": "ex4200-48p",
                    "aliases": ["rm209", "rm210"],
                },
            ],
        )
    ],
)
def test_populateswitches(testdata_dir, switches_file, expected):
    """test cases for the populateswitches() function"""
    assert inventory.populateswitches(testdata_dir / switches_file) == expected


@pytest.mark.parametrize(
    "routers_file,expected",
    [
        (
            "testrouterlist.csv",
            [
                {
                    "name": "br-mdf-01",
                    "fqdn": "br-mdf-01.scale.lan",
                    "ipv6": "2001:470:f325:103::2",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.0.1.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                }
            ],
        )
    ],
)
def test_populaterouters(testdata_dir, routers_file, expected):
    """test cases for the populaterouters() function"""
    assert inventory.populaterouters(testdata_dir / routers_file) == expected


@pytest.mark.parametrize(
    "aps_file,apuse_file,expected",
    [
        (
            "testaps.csv",
            "testapuse.csv",
            [
                {
                    "name": "101-a",
                    "fqdn": "101-a.scale.lan",
                    "mac": "e0:46:9a:5a:c0:36",
                    "ipv4": "10.128.3.150",
                    "ipv4ptr": "150.3.128.10.in-addr.arpa",
                    "wifi2": "6",
                    "wifi5": "36",
                    "configver": "0",
                    "aliases": ["n7a-0093"],
                    "map_id": "0",
                    "map_x": "50",
                    "map_y": "50",
                },
                {
                    "name": "101-b",
                    "fqdn": "101-b.scale.lan",
                    "mac": "2c:b0:5d:7f:63:72",
                    "ipv4": "10.128.3.151",
                    "ipv4ptr": "151.3.128.10.in-addr.arpa",
                    "wifi2": "1",
                    "wifi5": "165",
                    "configver": "0",
                    "aliases": ["n8c-0002"],
                    "map_id": "0",
                    "map_x": "50",
                    "map_y": "50",
                },
            ],
        )
    ],
)
def test_populateaps(testdata_dir, aps_file, apuse_file, expected):
    """test cases for the populateaps() function"""
    assert inventory.populateaps(testdata_dir / aps_file, testdata_dir / apuse_file) == expected


@pytest.mark.parametrize(
    "pis_file,piuse_file,expected",
    [
        (
            "testpis.csv",
            "testpiuse.csv",
            [
                {
                    "name": "pi-expo6",
                    "fqdn": "pi-expo6.scale.lan",
                    "ipv6": "2001:470:f026:110:dea6:32ff:fe41:88f4",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "4.f.8.8.1.4.e.f.f.f.2.3.6.a.e.d.0.1.1.0.6.2.0.f.0.7.4.0.1.0.0.2.ip6.arpa",
                }
            ],
        )
    ],
)
def test_populatepis(testdata_dir, pis_file, piuse_file, expected):
    """test cases for the populatepis() function"""
    assert inventory.populatepis(testdata_dir / pis_file, testdata_dir / piuse_file) == expected


@pytest.mark.parametrize(
    "servers_file,mocvlans,expected",
    [
        (
            "testserverlist.csv",
            [
                {
                    "name": "cfInfra",
                    "ipv6prefix": "2001:470:f325:503::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.128.3.0",
                    "ipv4bitmask": "24",
                    "building": "Conference",
                }
            ],
            [
                {
                    "aliases": [],
                    "fqdn": "server1.scale.lan",
                    "ipv4ptr": "5.3.128.10.in-addr.arpa",
                    # pylint: disable=line-too-long
                    "ipv6ptr": "5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.0.5.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
                    "name": "server1",
                    "macaddress": "4c:72:b9:7c:41:17",
                    "ipv6": "2001:470:f325:503::5",
                    "ipv4": "10.128.3.5",
                    "role": "core",
                    "vlan": "cfInfra",
                    "building": "Conference",
                }
            ],
        )
    ],
)
def test_populateservers(testdata_dir, servers_file, mocvlans, expected):
    """test cases for the populateservers() function"""
    assert inventory.populateservers(testdata_dir / servers_file, mocvlans) == expected


# Test coverage for populatedhcpnameservers()
@pytest.mark.parametrize(
    "servers,vlans,expected",
    [
        # Single core server
        (
            [
                {"name": "core1", "ipv4": "10.0.0.1", "ipv6": "2001:db8::1", "role": "core"},
                {"name": "other1", "ipv4": "10.0.0.2", "ipv6": "2001:db8::2", "role": "other"},
            ],
            [
                {"name": "vlan1"},
                {"name": "vlan2"},
            ],
            [
                {
                    "name": "vlan1",
                    "ipv4dns1": "10.0.0.1",
                    "ipv6dns1": "2001:db8::1",
                },
                {
                    "name": "vlan2",
                    "ipv4dns1": "10.0.0.1",
                    "ipv6dns1": "2001:db8::1",
                },
            ],
        ),
        # Two core servers
        (
            [
                {"name": "core1", "ipv4": "10.0.0.1", "ipv6": "2001:db8::1", "role": "core"},
                {"name": "core2", "ipv4": "10.0.0.2", "ipv6": "2001:db8::2", "role": "core"},
                {"name": "other1", "ipv4": "10.0.0.3", "ipv6": "2001:db8::3", "role": "other"},
            ],
            [
                {"name": "vlan1"},
            ],
            [
                {
                    "name": "vlan1",
                    "ipv4dns1": "10.0.0.1",
                    "ipv6dns1": "2001:db8::1",
                    "ipv4dns2": "10.0.0.2",
                    "ipv6dns2": "2001:db8::2",
                },
            ],
        ),
    ],
)
def test_populatedhcpnameservers(servers, vlans, expected):
    """test cases for the populatedhcpnameservers() function"""
    inventory.populatedhcpnameservers(servers, vlans)
    assert vlans == expected


# Test coverage for serveralias()
@pytest.mark.parametrize(
    "name,expected",
    [
        ("core-expo", ["ntpexpo"]),
        ("core-conf", ["loghost", "monitoring", "ntpconf"]),
        ("CORE-EXPO", ["ntpexpo"]),
        ("CORE-CONF", ["loghost", "monitoring", "ntpconf"]),
        ("Core-Expo", ["ntpexpo"]),
        ("unknown-server", []),
        ("server1", []),
        ("", []),
    ],
)
def test_serveralias(name, expected):
    """test cases for the serveralias() function"""
    assert inventory.serveralias(name) == expected


# Test coverage for generatekeaconfig()
def test_generatekeaconfig(tmp_path):
    """test case for the generatekeaconfig() function"""
    servers = [
        {
            "name": "core1",
            "ipv4": "10.0.0.1",
            "ipv6": "2001:db8::1",
            "role": "core",
        },
        {
            "name": "other1",
            "ipv4": "10.0.0.2",
            "ipv6": "2001:db8::2",
            "role": "other",
        },
    ]

    aps = [
        {
            "name": "test-ap",
            "mac": "aa:bb:cc:dd:ee:ff",
            "ipv4": "10.0.1.100",
            "wifi2": "6",
            "wifi5": "36",
            "configver": "1",
        }
    ]

    vlans = [
        {
            "name": "testVlan",
            "id": "100",
            "ipv4prefix": "10.0.1.0",
            "ipv4bitmask": "24",
            "ipv4dhcpStart": "10.0.1.80",
            "ipv4dhcpEnd": "10.0.1.254",
            "ipv4router": "10.0.1.1",
            "ipv6prefix": "2001:db8:100::",
            "ipv6bitmask": "64",
            "ipv6dhcpStart": "2001:db8:100:d8c::1",
            "ipv6dhcpEnd": "2001:db8:100:d8c::800",
            "building": "Test",
        },
        {
            "name": "cfInfra",
            "id": "503",
            "ipv4prefix": "10.128.3.0",
            "ipv4bitmask": "24",
            "ipv4dhcpStart": "10.128.3.80",
            "ipv4dhcpEnd": "10.128.3.254",
            "ipv4router": "10.128.3.1",
            "ipv6prefix": "2001:470:f325:503::",
            "ipv6bitmask": "64",
            "ipv6dhcpStart": "2001:470:f325:503:d8c::1",
            "ipv6dhcpEnd": "2001:470:f325:503:d8c::800",
            "building": "Conference",
        },
        {
            "name": "exInfra",
            "id": "103",
            "ipv4prefix": "10.0.3.0",
            "ipv4bitmask": "24",
            "ipv4dhcpStart": "10.0.3.80",
            "ipv4dhcpEnd": "10.0.3.254",
            "ipv4router": "10.0.3.1",
            "ipv6prefix": "2001:470:f026:103::",
            "ipv6bitmask": "64",
            "ipv6dhcpStart": "2001:470:f026:103:d8c::1",
            "ipv6dhcpEnd": "2001:470:f026:103:d8c::800",
            "building": "Expo",
        },
    ]

    outputdir = str(tmp_path)
    inventory.generatekeaconfig(servers, aps, vlans, outputdir)

    # Verify DHCPv4 file exists and is valid JSON
    dhcp4_file = tmp_path / "dhcp4-server.conf"
    assert dhcp4_file.exists()
    with open(dhcp4_file) as f:
        dhcp4_config = json.load(f)

    # Verify basic structure
    assert "Dhcp4" in dhcp4_config
    assert "subnet4" in dhcp4_config["Dhcp4"]
    assert "reservations" in dhcp4_config["Dhcp4"]

    # Verify AP reservation is present
    assert len(dhcp4_config["Dhcp4"]["reservations"]) == 1
    assert dhcp4_config["Dhcp4"]["reservations"][0]["hostname"] == "test-ap"
    assert dhcp4_config["Dhcp4"]["reservations"][0]["hw-address"] == "aa:bb:cc:dd:ee:ff"

    # Verify subnets are present (should be 3: testVlan, cfInfra, exInfra)
    assert len(dhcp4_config["Dhcp4"]["subnet4"]) == 3

    # Verify core server DNS is configured
    dns_servers = dhcp4_config["Dhcp4"]["option-data"][0]["data"]
    assert "10.0.0.1" in dns_servers

    # Verify DHCPv6 expo file exists and is valid JSON
    dhcp6_expo_file = tmp_path / "dhcp6-server-expo.conf"
    assert dhcp6_expo_file.exists()
    with open(dhcp6_expo_file) as f:
        dhcp6_expo_config = json.load(f)

    assert "Dhcp6" in dhcp6_expo_config
    assert "subnet6" in dhcp6_expo_config["Dhcp6"]

    # Verify DHCPv6 conf file exists and is valid JSON
    dhcp6_conf_file = tmp_path / "dhcp6-server-conf.conf"
    assert dhcp6_conf_file.exists()
    with open(dhcp6_conf_file) as f:
        dhcp6_conf_config = json.load(f)

    assert "Dhcp6" in dhcp6_conf_config
    assert "subnet6" in dhcp6_conf_config["Dhcp6"]

    # Verify core server IPv6 DNS is configured in both DHCPv6 configs
    for config in [dhcp6_expo_config, dhcp6_conf_config]:
        dns_servers_v6 = config["Dhcp6"]["option-data"][0]["data"]
        assert "2001:db8::1" in dns_servers_v6


# Test coverage for _building_from_vlans()
@pytest.mark.parametrize(
    "vlans,ipv6,ipv4,expected",
    [
        # IPv6 match in Conference building
        (
            [
                {
                    "name": "cfInfra",
                    "ipv6prefix": "2001:470:f325:503::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.128.3.0",
                    "ipv4bitmask": "24",
                    "building": "Conference",
                }
            ],
            "2001:470:f325:503::5",
            None,
            "Conference",
        ),
        # IPv4 match in Expo building
        (
            [
                {
                    "name": "exInfra",
                    "ipv6prefix": "2001:470:f026:103::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.0.3.0",
                    "ipv4bitmask": "24",
                    "building": "Expo",
                }
            ],
            None,
            "10.0.3.100",
            "Expo",
        ),
        # No match returns empty string
        (
            [
                {
                    "name": "testVlan",
                    "ipv6prefix": "2001:db8:100::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "10.0.1.0",
                    "ipv4bitmask": "24",
                    "building": "Test",
                }
            ],
            "2001:db8:200::1",
            None,
            "",
        ),
        # Skip invalid IPv4 prefix
        (
            [
                {
                    "name": "ipv6only",
                    "ipv6prefix": "2001:db8:100::",
                    "ipv6bitmask": "64",
                    "ipv4prefix": "0.0.0.0",
                    "ipv4bitmask": "0",
                    "building": "Test",
                }
            ],
            None,
            "10.0.1.100",
            "",
        ),
    ],
)
def test_building_from_vlans(vlans, ipv6, ipv4, expected):
    """test cases for the _building_from_vlans() function"""
    assert inventory._building_from_vlans(vlans, ipv6=ipv6, ipv4=ipv4) == expected


# Test coverage for _prom_exclude()
@pytest.mark.parametrize(
    "name,expected",
    [
        ("deceased", True),
        ("donotuse", True),
        ("expob5", True),
        ("expoc4", True),
        ("expoc5", True),
        ("massflash", True),
        ("pi-massflash", True),
        ("pi-reghelp1", True),
        ("pi-reghelp2", True),
        ("spare", True),
        ("normal-switch", False),
        ("expo-catwalk", False),
        ("core-conf", False),
        ("test-ap", False),
        ("", False),
    ],
)
def test_prom_exclude(name, expected):
    """test cases for the _prom_exclude() function"""
    assert inventory._prom_exclude(name) == expected


# Test coverage for generatepromconfigs()
def test_generatepromconfigs(tmp_path):
    """test case for the generatepromconfigs() function"""
    switches = [
        {
            "name": "test-switch",
            "ipv6": "2001:db8::100",
        },
        {
            "name": "deceased-switch",
            "ipv6": "2001:db8::101",
        },
    ]

    pis = [
        {
            "name": "pi-test",
            "ipv6": "2001:db8::200",
        },
        {
            "name": "pi-massflash",
            "ipv6": "2001:db8::201",
        },
    ]

    aps = [
        {
            "name": "test-ap",
            "ipv4": "10.0.1.100",
        },
        {
            "name": "spare-ap",
            "ipv4": "10.0.1.101",
        },
    ]

    outputdir = str(tmp_path)
    inventory.generatepromconfigs(switches, pis, aps, outputdir)

    # Verify AP config file exists and is valid JSON
    ap_file = tmp_path / "prom-aps.json"
    assert ap_file.exists()
    with open(ap_file) as f:
        ap_config = json.load(f)
    # Should have 1 AP (spare-ap is excluded)
    assert len(ap_config) == 1
    assert ap_config[0]["labels"]["ap"] == "test-ap"
    assert ap_config[0]["targets"][0] == "10.0.1.100:9100"

    # Verify PI config file exists and is valid JSON
    pi_file = tmp_path / "prom-pis.json"
    assert pi_file.exists()
    with open(pi_file) as f:
        pi_config = json.load(f)
    # Should have 1 PI (pi-massflash is excluded)
    assert len(pi_config) == 1
    assert pi_config[0]["labels"]["pi"] == "pi-test"
    assert pi_config[0]["targets"][0] == "[2001:db8::200]:9100"

    # Verify switch config file exists and is valid JSON
    switch_file = tmp_path / "prom-switches.json"
    assert switch_file.exists()
    with open(switch_file) as f:
        switch_config = json.load(f)
    # Should have 1 switch (deceased-switch is excluded)
    assert len(switch_config) == 1
    assert switch_config[0]["labels"]["switch"] == "test-switch"
    assert switch_config[0]["targets"][0] == "[2001:db8::100]:161"


# Test coverage for generatezones()
def test_generatezones(tmp_path):
    """test case for the generatezones() function"""
    switches = [
        {
            "name": "test-switch",
            "fqdn": "test-switch.scale.lan",
            "ipv6": "2001:db8::100",
            "ipv6ptr": "0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            "num": "1",
            "aliases": [],
        }
    ]

    routers = [
        {
            "name": "test-router",
            "fqdn": "test-router.scale.lan",
            "ipv6": "2001:db8::1",
            "ipv6ptr": "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            "aliases": [],
        }
    ]

    pis = [
        {
            "name": "pi-test",
            "fqdn": "pi-test.scale.lan",
            "ipv6": "2001:db8::200",
            "ipv6ptr": "0.0.2.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            "aliases": [],
        }
    ]

    aps = [
        {
            "name": "test-ap",
            "fqdn": "test-ap.scale.lan",
            "ipv4": "10.0.1.100",
            "ipv4ptr": "100.1.0.10.in-addr.arpa",
            "aliases": ["serial123"],
        }
    ]

    servers = [
        {
            "name": "test-server",
            "fqdn": "test-server.scale.lan",
            "ipv4": "10.0.1.1",
            "ipv4ptr": "1.1.0.10.in-addr.arpa",
            "ipv6": "2001:db8::10",
            "ipv6ptr": "0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa",
            "aliases": ["alias1"],
        }
    ]

    outputdir = str(tmp_path)
    result = inventory.generatezones(switches, routers, pis, aps, servers, outputdir)

    assert result is True

    # Verify forward zone file exists and contains expected records
    fwd_file = tmp_path / "db.scale.lan.records"
    assert fwd_file.exists()
    with open(fwd_file) as f:
        fwd_content = f.read()

    assert "test-switch  IN  AAAA    2001:db8::100" in fwd_content
    assert "switch1  IN  CNAME   test-switch.scale.lan." in fwd_content
    assert "test-ap  IN  A    10.0.1.100" in fwd_content
    assert "serial123 IN    CNAME   test-ap.scale.lan." in fwd_content

    # Verify IPv4 PTR zone file exists and contains expected records
    ipv4_file = tmp_path / "db.ipv4.arpa.records"
    assert ipv4_file.exists()
    with open(ipv4_file) as f:
        ipv4_content = f.read()

    assert "100.1.0.10.in-addr.arpa.  IN  PTR    test-ap.scale.lan." in ipv4_content
    assert "1.1.0.10.in-addr.arpa.  IN  PTR    test-server.scale.lan." in ipv4_content

    # Verify IPv6 PTR zone file exists and contains expected records
    ipv6_file = tmp_path / "db.ipv6.arpa.records"
    assert ipv6_file.exists()
    with open(ipv6_file) as f:
        ipv6_content = f.read()

    assert "0.0.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa.  IN  PTR    test-switch.scale.lan." in ipv6_content


# Test coverage for generatewasgehtconfig()
def test_generatewasgehtconfig(tmp_path):
    """test case for the generatewasgehtconfig() function"""
    switches = [
        {
            "name": "test-switch",
            "num": "1",
            "switchtype": "testType",
            "model": "ex4200",
            "ipv6": "2001:470:f325:103::100",
            "hierarchy": "A.1",
            "aliases": ["rm101"],
        }
    ]

    routers = [
        {
            "name": "br-mdf-01",
            "ipv6": "2001:470:f325:103::2",
        },
        {
            "name": "ex-mdf-01",
            "ipv6": "2001:470:f026:104::3",
        },
        {
            "name": "cf-mdf-01",
            "ipv6": "2001:470:f026:901::2",
        },
        {
            "name": "test-router",
            "ipv6": "2001:db8::1",
        },
    ]

    pis = [
        {
            "name": "pi-reg1",
            "ipv6": "2001:470:f026:110::100",
        },
        {
            "name": "pi-massflash",
            "ipv6": "2001:470:f026:110::101",
        },
    ]

    aps = [
        {
            "name": "test-ap",
            "ipv4": "10.128.3.100",
            "wifi2": "6",
            "wifi5": "36",
            "configver": "1",
            "map_id": "1",
            "map_x": "100",
            "map_y": "200",
            "aliases": [],
        }
    ]

    servers = [
        {
            "name": "core-conf",
            "ipv4": "10.128.3.1",
            "ipv6": "2001:470:f325:503::1",
            "ipv4ptr": "1.3.128.10.in-addr.arpa",
            "ipv6ptr": "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.0.5.0.5.2.3.f.0.7.4.0.1.0.0.2.ip6.arpa",
            "fqdn": "core-conf.scale.lan",
            "role": "core",
            "building": "Conference",
            "aliases": ["loghost"],
        }
    ]

    vlans = [
        {
            "name": "cfInfra",
            "ipv6prefix": "2001:470:f325:503::",
            "ipv6bitmask": "64",
            "ipv4prefix": "10.128.3.0",
            "ipv4bitmask": "24",
            "building": "Conference",
        },
        {
            "name": "exInfra",
            "ipv6prefix": "2001:470:f325:103::",
            "ipv6bitmask": "64",
            "ipv4prefix": "10.0.3.0",
            "ipv4bitmask": "24",
            "building": "Expo",
        },
        {
            "name": "exInterlink",
            "ipv6prefix": "2001:470:f026:104::",
            "ipv6bitmask": "64",
            "ipv4prefix": "172.20.4.0",
            "ipv4bitmask": "24",
            "building": "Expo",
        },
        {
            "name": "cfInterlink",
            "ipv6prefix": "2001:470:f026:901::",
            "ipv6bitmask": "64",
            "ipv4prefix": "172.20.1.0",
            "ipv4bitmask": "24",
            "building": "Conference",
        },
    ]

    outputdir = str(tmp_path)
    inventory.generatewasgehtconfig(switches, routers, pis, aps, servers, vlans, outputdir)

    # Verify config file exists and is valid JSON
    config_file = tmp_path / "scale-wasgeht-config.json"
    assert config_file.exists()
    with open(config_file) as f:
        config = json.load(f)

    # Verify uplink check exists
    assert "uplink" in config
    assert "checks" in config["uplink"]

    # Verify switch entry
    assert "test-switch" in config
    assert config["test-switch"]["tags"]["type"] == "switch"
    assert config["test-switch"]["tags"]["building"] == "Expo"
    assert "rm101" in config["test-switch"]["tags"]["aliases"]

    # Verify router entries (all three MDF routers have special ping addresses)
    assert "br-mdf-01" in config
    br_ping_addrs = config["br-mdf-01"]["checks"]["ping"]["addresses"]
    assert len(br_ping_addrs) == 6
    assert "172.20.1.1" in br_ping_addrs
    assert "2001:470:f026:901::1" in br_ping_addrs

    assert "ex-mdf-01" in config
    ex_ping_addrs = config["ex-mdf-01"]["checks"]["ping"]["addresses"]
    assert len(ex_ping_addrs) == 6
    assert "172.20.4.3" in ex_ping_addrs
    assert "2001:470:f026:104::3" in ex_ping_addrs

    assert "cf-mdf-01" in config
    cf_ping_addrs = config["cf-mdf-01"]["checks"]["ping"]["addresses"]
    assert len(cf_ping_addrs) == 6
    assert "172.20.1.2" in cf_ping_addrs
    assert "2001:470:f026:901::2" in cf_ping_addrs

    assert "test-router" in config
    assert config["test-router"]["tags"]["type"] == "router"
    # Generic router has only its IPv6 in ping addresses
    assert len(config["test-router"]["checks"]["ping"]["addresses"]) == 1

    # Verify PI entry (pi-reg1 should be present, pi-massflash excluded)
    assert "pi-reg1" in config
    assert config["pi-reg1"]["tags"]["role"] == "registration"
    assert "pi-massflash" not in config

    # Verify AP entry
    assert "test-ap" in config
    assert config["test-ap"]["tags"]["type"] == "ap"
    assert config["test-ap"]["tags"]["building"] == "Conference"
    assert "10.128.3.100" in config["test-ap"]["checks"]["ping"]["addresses"]

    # Verify server entry (core-conf has DNS checks)
    assert "core-conf" in config
    assert config["core-conf"]["tags"]["type"] == "server"
    assert "dns" in config["core-conf"]["checks"]
    assert "http" in config["core-conf"]["checks"]


# Test coverage for generateallnetwork()
def test_generateallnetwork(tmp_path):
    """test case for the generateallnetwork() function"""
    switches = [
        {
            "name": "test-switch",
            "fqdn": "test-switch.scale.lan",
        },
        {
            "name": "expo-switch",
            "fqdn": "expo-switch.scale.lan",
        },
    ]

    routers = [
        {
            "name": "test-router",
            "fqdn": "test-router.scale.lan",
        },
    ]

    outputdir = str(tmp_path)
    inventory.generateallnetwork(switches, routers, outputdir)

    # Verify output file exists
    output_file = tmp_path / "all-network-devices"
    assert output_file.exists()

    # Verify content
    with open(output_file) as f:
        content = f.read()

    assert "test-switch.scale.lan\n" in content
    assert "expo-switch.scale.lan\n" in content
    assert "test-router.scale.lan\n" in content
