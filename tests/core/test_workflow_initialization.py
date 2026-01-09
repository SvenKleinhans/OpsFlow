import logging
from unittest.mock import Mock, patch

from opsflow.core.workflow import Workflow
from tests.support.fake_pkg_manager import FakePkgManager


class TestWorkflowInitialization:
    """Test Workflow initialization and setup."""

    def test_workflow_initializes_with_minimal_config(self, config):
        """Workflow should initialize successfully with minimal configuration."""
        workflow = Workflow(config=config)

        assert workflow._config is not None
        assert workflow._result_collector is not None
        assert workflow._logger is not None
        assert workflow._notifier is not None
        assert isinstance(workflow._plugins, list)

    def test_workflow_initializes_without_system_manager(self, config):
        """Workflow should work without a system manager."""
        workflow = Workflow(system_manager=None, config=config)

        assert workflow._system_manager is None
        assert workflow._config is not None

    def test_workflow_initializes_with_system_manager(self, config):
        """Workflow should initialize with an optional system manager."""
        mock_manager = Mock()
        workflow = Workflow(
            system_manager=mock_manager, pkg_manager=FakePkgManager(), config=config
        )

        assert workflow._system_manager is mock_manager

    def test_workflow_sets_up_logging(self, config):
        """Workflow should set up logging with configured settings."""
        workflow = Workflow(config=config)

        assert workflow._logger is not None
        assert workflow._memory_handler is not None
        assert workflow._logger.isEnabledFor(logging.DEBUG)

    def test_workflow_loads_plugins_from_directory(self, tmp_path, config):
        """Workflow should load plugins from a specified directory."""
        # Create a temporary plugin module
        plugin_dir = tmp_path / "plugins"
        plugin_dir.mkdir()

        # For this test, we just verify the parameter is accepted
        # Actual module loading is tested separately
        with patch("opsflow.core.utils.module_loader.ModuleLoader.load_from_directory"):
            workflow = Workflow(config=config, plugin_dir=str(plugin_dir))
            assert workflow._config is not None

    def test_workflow_loads_notifiers_from_directory(self, tmp_path, config):
        """Workflow should load notifiers from a specified directory."""
        notifier_dir = tmp_path / "notifiers"
        notifier_dir.mkdir()

        with patch("opsflow.core.utils.module_loader.ModuleLoader.load_from_directory"):
            workflow = Workflow(config=config, notifier_dir=str(notifier_dir))
            assert workflow._config is not None
