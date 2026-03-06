"""Package resource utilities for accessing bundled data files."""

import atexit
import sys
from contextlib import ExitStack
from pathlib import Path

if sys.version_info >= (3, 9):
    from importlib.resources import as_file, files
else:
    from importlib_resources import as_file, files

_STACK = ExitStack()
atexit.register(_STACK.close)


def get_data_file(relative_path: str) -> Path:
    """
    Get a filesystem path to a bundled data file.

    Args:
        relative_path: Path relative to the data directory (e.g., 'aps/aps.csv')

    Returns:
        Filesystem Path to the data file
    """
    resource = files("facts") / "data" / relative_path
    return _STACK.enter_context(as_file(resource))


def get_data_dir(relative_path: str = "") -> Path:
    """
    Get a filesystem path to a bundled data directory.

    Args:
        relative_path: Path relative to the data directory (e.g., 'aps' or 'switch-config')

    Returns:
        Filesystem Path to the data directory
    """
    resource = files("facts") / "data"
    if relative_path:
        resource = resource / relative_path
    return _STACK.enter_context(as_file(resource))


# Default data file paths (can be overridden via CLI options)
def get_default_paths():
    """Get default paths for all inventory data files."""
    return {
        "swconfigdir": str(get_data_dir("switch-config")) + "/",
        "vlansfile": "vlans",
        "switchesfile": str(get_data_file("switch-config/switchtypes")),
        "serversfile": str(get_data_file("servers/serverlist.csv")),
        "routersfile": str(get_data_file("routers/routerlist.csv")),
        "apsfile": str(get_data_file("aps/aps.csv")),
        "apusefile": str(get_data_file("aps/apuse.csv")),
        "pifile": str(get_data_file("pi/pis.csv")),
        "piusefile": str(get_data_file("pi/piuse.csv")),
    }
