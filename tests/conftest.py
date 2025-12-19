import pytest
import logging

from opsflow.core.config.schema import CoreConfig, LoggingConfig
from opsflow.core.models.context import Context
from opsflow.core.models.result import ResultCollector

from .support.factories import make_components_factory, TestRegistry


@pytest.fixture
def config(tmp_path):
    log_file = tmp_path / "test.log"
    cfg = CoreConfig(
        plugins={},
        notifiers={},
        dry_run=True,
        logging=LoggingConfig(file=str(log_file), debug=True),
    )
    return cfg


@pytest.fixture
def logger():
    logger = logging.getLogger("test_logger")
    return logger


@pytest.fixture
def context():
    return Context(result_collector=ResultCollector(), dry_run=True)


@pytest.fixture
def make_components(logger):
    return make_components_factory(logger)


@pytest.fixture(autouse=True)
def clean_test_registry():
    TestRegistry.entries.clear()
    yield
    TestRegistry.entries.clear()
