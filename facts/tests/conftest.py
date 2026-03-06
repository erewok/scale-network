from importlib.resources import as_file, files
from pathlib import Path
from typing import Generator

import pytest


dirname = Path(__file__).parent


@pytest.fixture(scope="session")
def pkg_data_root() -> "Generator[Path, None, None]":
    with as_file(files("facts") / "data") as data_dir:
        yield data_dir


@pytest.fixture
def pkg_path(pkg_data_root):
    def _p(rel: str) -> Path:
        return pkg_data_root / rel
    return _p


@pytest.fixture(scope="session")
def testdata_dir() -> Path:
    """Fixture to provide a temporary directory for test data."""
    return dirname / "testdata"