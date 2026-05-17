"""
Shared pytest configuration and fixtures for ARMD validation tests.
"""

import os
import sys

import pytest

# Make `config` importable from the tests/ directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def pytest_addoption(parser):
    """Add custom CLI options for test configuration."""
    parser.addoption(
        "--bq-project",
        default="som-nero-phi-jonc101",
        help="BigQuery project ID (default: som-nero-phi-jonc101)",
    )
    parser.addoption(
        "--year",
        type=int,
        default=None,
        help=(
            "Year of the ARMD build to validate (e.g. 2024 or 2025). "
            "Resolves tables to ARMD_<year>.*. Defaults to config.DEFAULT_YEAR."
        ),
    )


def pytest_configure(config):
    """Register custom markers and bind the chosen year to the config module.

    We mutate `config.TABLES` (and DEST_DATASET etc.) in place so that test
    modules importing `from config import TABLES` still see the right values
    after they're loaded during collection.
    """
    config.addinivalue_line("markers", "slow: marks tests that are slow to run")
    config.addinivalue_line("markers", "cross_table: marks cross-table consistency tests")

    import config as armd_config

    year = config.getoption("--year") or armd_config.DEFAULT_YEAR
    new_tables = armd_config.tables_for_year(year)
    armd_config.TABLES.clear()
    armd_config.TABLES.update(new_tables)
    armd_config.DEST_DATASET = armd_config.fully_qualified_dest(year)
    armd_config.SOURCE_DATASET = armd_config.fully_qualified_source(year)
    armd_config.BQ_DATASET = armd_config.dest_dataset(year)
    armd_config.BQ_SOURCE_DATASET = armd_config.source_dataset(year)
    armd_config._RESOLVED_YEAR = year


def pytest_collection_modifyitems(config, items):
    """Auto-mark slow tests."""
    for item in items:
        if "cross_table" in item.nodeid.lower() or "smoke" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def armd_year():
    """The year being validated for the current test run."""
    import config as armd_config
    return getattr(armd_config, "_RESOLVED_YEAR", armd_config.DEFAULT_YEAR)
