import pytest
import logging

from opsflow.core.config.schema import CoreConfig, LoggingConfig
from opsflow.core.models.context import Context
from opsflow.core.models.result import ResultCollector
from opsflow.core.notifier.registry import NotifierRegistry
from opsflow.core.plugin.registry import PluginRegistry

from .support.factories import make_components_factory, TestRegistry

# Import test dummies
from .dummies.plugins import (
    PluginA,
    PluginAConfig,
    PluginB,
    PluginBConfig,
)


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
    NotifierRegistry.entries.clear()
    PluginRegistry.entries.clear()
    yield
    TestRegistry.entries.clear()
    NotifierRegistry.entries.clear()
    PluginRegistry.entries.clear()


@pytest.fixture
def config_with_plugins(config):
    """Create a workflow configuration with test plugins enabled."""
    PluginRegistry.register_class(PluginA, config=PluginAConfig)
    PluginRegistry.register_class(PluginB, config=PluginBConfig)

    config.plugins = {
        PluginA.name: PluginAConfig(value=42, enabled=True),
        PluginB.name: PluginBConfig(flag=True, enabled=True),
    }
    return config
