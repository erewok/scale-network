# facts

A Python tool for managing network inventory and generating configuration files for the SCaLE (SoCal Linux Expo) network infrastructure.

## Overview

This package reads network inventory data from CSV files and generates configuration files for various network services including DHCP servers, DNS zones, and monitoring systems. It includes bundled inventory data but can use external data sources via command-line options.

## Installation

```bash
pip install .
```

For development:

```bash
uv sync
```

## Usage

Run as an installed command:

```bash
facts --help
```

Run as a Python module:

```bash
python3 -m facts --help
```

During development with uv:

```bash
uv run facts --help
uv run python -m facts --help
```

## Commands

### Generate configurations

- `facts kea OUTPUT_DIR` - Generate Kea DHCP server configuration
- `facts nsd OUTPUT_DIR` - Generate NSD DNS zone files
- `facts prom OUTPUT_DIR` - Generate Prometheus monitoring configuration
- `facts wasgeht OUTPUT_DIR` - Generate wasgeht monitoring configuration
- `facts allnet OUTPUT_DIR` - Generate all network device configurations
- `facts all OUTPUT_DIR` - Generate all configuration files

### Debug

- `facts debug VARIABLE` - Print inventory data as JSON (`switches`, `routers`, `vlans`, `servers`, `aps`, or `pis`)

## Data Sources

By default, the tool uses bundled package data located in `src/facts/data/`. This includes:

- VLANs and switch configurations
- Server inventory
- Router inventory
- Access point inventory
- Raspberry Pi inventory

### Using external data

Override default data sources with command-line options:

```bash
facts --data-dir /path/to/data all output/
facts --servers-file custom-servers.csv kea output/
```

Available options:

- `--data-dir` - Base directory containing inventory data files
- `--swconfig-dir` - Switch configuration directory
- `--vlans-file` - VLAN configuration file
- `--switches-file` - Switch types file
- `--servers-file` - Servers CSV file
- `--routers-file` - Routers CSV file
- `--aps-file` - Access points CSV file
- `--apuse-file` - AP usage CSV file
- `--pis-file` - Raspberry Pis CSV file
- `--piuse-file` - Pi usage CSV file

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Run linter:

```bash
uv run ruff check .
```

The entry point is defined in `src/facts/__main__.py` for clarity during development.
