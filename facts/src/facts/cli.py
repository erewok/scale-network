"""Command-line interface for facts inventory management."""

import json
import os

import click

from . import inventory
from . import resources


@click.group()
@click.option(
    "--data-dir",
    type=click.Path(exists=True, file_okay=False),
    help="Base directory containing inventory data files (overrides bundled package data)",
)
@click.option(
    "--swconfig-dir",
    type=click.Path(exists=True, file_okay=False),
    help="Switch configuration directory (overrides bundled data)",
)
@click.option(
    "--vlans-file",
    type=click.Path(exists=True, dir_okay=False),
    help="VLAN configuration file (overrides bundled data)",
)
@click.option(
    "--switches-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Switch types file (overrides bundled data)",
)
@click.option(
    "--servers-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Servers CSV file (overrides bundled data)",
)
@click.option(
    "--routers-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Routers CSV file (overrides bundled data)",
)
@click.option(
    "--aps-file",
    type=click.Path(exists=True, dir_okay=False),
    help="APs CSV file (overrides bundled data)",
)
@click.option(
    "--apuse-file",
    type=click.Path(exists=True, dir_okay=False),
    help="AP usage CSV file (overrides bundled data)",
)
@click.option(
    "--pis-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Raspberry Pis CSV file (overrides bundled data)",
)
@click.option(
    "--piuse-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Pi usage CSV file (overrides bundled data)",
)
@click.pass_context
def cli(
    ctx,
    data_dir,
    swconfig_dir,
    vlans_file,
    switches_file,
    servers_file,
    routers_file,
    aps_file,
    apuse_file,
    pis_file,
    piuse_file,
):
    """
    SCaLE network inventory management.

    Generate configuration files for various network services from inventory data.

    By default, uses bundled package data. All paths can be overridden via options
    to use external data files.
    """
    ctx.ensure_object(dict)

    # If any custom paths provided, use custom logic; otherwise use bundled defaults
    if data_dir or any(
        [
            swconfig_dir,
            vlans_file,
            switches_file,
            servers_file,
            routers_file,
            aps_file,
            apuse_file,
            pis_file,
            piuse_file,
        ]
    ):
        # Custom data sources - apply defaults based on data_dir if provided
        if data_dir:
            swconfig_dir = swconfig_dir or os.path.join(data_dir, "switch-configuration", "config")

        ctx.obj["swconfigdir"] = swconfig_dir + "/" if swconfig_dir else ""
        ctx.obj["vlansfile"] = vlans_file or "vlans"
        ctx.obj["switchesfile"] = switches_file or (os.path.join(swconfig_dir, "switchtypes") if swconfig_dir else "")
        ctx.obj["serversfile"] = servers_file or (
            os.path.join(data_dir, "facts", "servers", "serverlist.csv") if data_dir else ""
        )
        ctx.obj["routersfile"] = routers_file or (
            os.path.join(data_dir, "facts", "routers", "routerlist.csv") if data_dir else ""
        )
        ctx.obj["apsfile"] = aps_file or (os.path.join(data_dir, "facts", "aps", "aps.csv") if data_dir else "")
        ctx.obj["apusefile"] = apuse_file or (os.path.join(data_dir, "facts", "aps", "apuse.csv") if data_dir else "")
        ctx.obj["pifile"] = pis_file or (os.path.join(data_dir, "facts", "pi", "pis.csv") if data_dir else "")
        ctx.obj["piusefile"] = piuse_file or (os.path.join(data_dir, "facts", "pi", "piuse.csv") if data_dir else "")
    else:
        # Use bundled package data
        ctx.obj.update(resources.get_default_paths())
    vlans = inventory.populate_vlans(ctx.obj["swconfigdir"], ctx.obj["vlansfile"])
    switches = inventory.populateswitches(ctx.obj["switchesfile"])
    servers = inventory.populateservers(ctx.obj["serversfile"], vlans)
    routers = inventory.populaterouters(ctx.obj["routersfile"])
    aps = inventory.populateaps(ctx.obj["apsfile"], ctx.obj["apusefile"])
    pis = inventory.populatepis(ctx.obj["pifile"], ctx.obj["piusefile"])

    ctx.obj["inventory_data"] = {
        "vlans": vlans,
        "switches": switches,
        "servers": servers,
        "routers": routers,
        "aps": aps,
        "pis": pis,
    }
    return ctx.obj["inventory_data"]


def ensure_output_dir(output_dir):
    """Ensure the output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def load_inventory_data(ctx):
    """Load inventory data using paths initialized on the Click context."""
    data = ctx.obj.get("inventory_data")
    if data is not None:
        return data

    vlans = inventory.populate_vlans(ctx.obj["swconfigdir"], ctx.obj["vlansfile"])
    switches = inventory.populateswitches(ctx.obj["switchesfile"])
    servers = inventory.populateservers(ctx.obj["serversfile"], vlans)
    routers = inventory.populaterouters(ctx.obj["routersfile"])
    aps = inventory.populateaps(ctx.obj["apsfile"], ctx.obj["apusefile"])
    pis = inventory.populatepis(ctx.obj["pifile"], ctx.obj["piusefile"])

    data = {
        "vlans": vlans,
        "switches": switches,
        "servers": servers,
        "routers": routers,
        "aps": aps,
        "pis": pis,
    }
    ctx.obj["inventory_data"] = data
    return data


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def kea(ctx, output_dir):
    """Generate Kea DHCP server configuration."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)
    inventory.generatekeaconfig(data["servers"], data["aps"], data["vlans"], output_dir)
    click.echo(f"✓ Kea configuration written to {output_dir}")


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def nsd(ctx, output_dir):
    """Generate NSD DNS zone files."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)
    inventory.generatezones(
        data["switches"],
        data["routers"],
        data["pis"],
        data["aps"],
        data["servers"],
        output_dir,
    )
    click.echo(f"✓ DNS zone files written to {output_dir}")


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def prom(ctx, output_dir):
    """Generate Prometheus monitoring configuration."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)
    inventory.generatepromconfigs(data["switches"], data["pis"], data["aps"], output_dir)
    click.echo(f"✓ Prometheus configuration written to {output_dir}")


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def wasgeht(ctx, output_dir):
    """Generate wasgeht monitoring configuration."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)
    inventory.generatewasgehtconfig(
        data["switches"],
        data["routers"],
        data["pis"],
        data["aps"],
        data["servers"],
        data["vlans"],
        output_dir,
    )
    click.echo(f"✓ Wasgeht configuration written to {output_dir}")


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def allnet(ctx, output_dir):
    """Generate all network device configurations."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)
    inventory.generateallnetwork(data["switches"], data["routers"], output_dir)
    click.echo(f"✓ Network configurations written to {output_dir}")


@cli.command()
@click.argument("output_dir", type=click.Path())
@click.pass_context
def all(ctx, output_dir):
    """Generate all configuration files."""
    ensure_output_dir(output_dir)
    data = load_inventory_data(ctx)

    click.echo("Generating all configurations...")

    inventory.generatekeaconfig(data["servers"], data["aps"], data["vlans"], output_dir)
    click.echo("  ✓ Kea DHCP")

    inventory.generatezones(
        data["switches"],
        data["routers"],
        data["pis"],
        data["aps"],
        data["servers"],
        output_dir,
    )
    click.echo("  ✓ DNS zones")

    inventory.generatepromconfigs(data["switches"], data["pis"], data["aps"], output_dir)
    click.echo("  ✓ Prometheus")

    inventory.generatewasgehtconfig(
        data["switches"],
        data["routers"],
        data["pis"],
        data["aps"],
        data["servers"],
        data["vlans"],
        output_dir,
    )
    click.echo("  ✓ Wasgeht")

    inventory.generateallnetwork(data["switches"], data["routers"], output_dir)
    click.echo("  ✓ Network configs")

    click.echo(f"\n✓ All configurations written to {output_dir}")


@cli.command()
@click.argument(
    "variable",
    type=click.Choice(["switches", "routers", "vlans", "servers", "aps", "pis"], case_sensitive=False),
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    help="Pretty-print JSON output (default: pretty)",
)
@click.pass_context
def debug(ctx, variable, pretty):
    """Debug inventory data by printing a specific variable as JSON."""
    data = load_inventory_data(ctx)

    if pretty:
        output = json.dumps(data[variable], indent=2)
    else:
        output = json.dumps(data[variable])

    click.echo(output)
