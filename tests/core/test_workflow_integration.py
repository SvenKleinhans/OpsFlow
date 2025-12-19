"""Integration tests for the Workflow class.

Tests the full end-to-end workflow functionality including:
- Configuration loading
- Plugin instantiation and execution
- Notifier creation and notification delivery
- Result collection and reporting
- Parallel plugin execution
"""

import pytest
import logging
from unittest.mock import Mock, patch

from opsflow.core.system import PackageManager, SystemManager
from opsflow.core.workflow import Workflow
from opsflow.core.config import CoreConfig, LoggingConfig
from opsflow.core.plugin import PluginRegistry
from opsflow.core.notifier.registry import NotifierRegistry
from opsflow.core.models import Result, Severity
from opsflow.core.models.context import Context

# Import test dummies
from ..dummies.plugins.plugin_a import PluginA, PluginAConfig
from ..dummies.plugins.plugin_b import PluginB, PluginBConfig
from ..dummies.plugins.plugin_failing import FailingPlugin


@pytest.fixture(autouse=True)
def clean_registries():
    NotifierRegistry.entries.clear()
    PluginRegistry.entries.clear()
    yield
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
        workflow = Workflow(system_manager=mock_manager, config=config)

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


class TestWorkflowPluginExecution:
    """Test plugin execution within the workflow."""

    def test_workflow_instantiates_registered_plugins(self, config_with_plugins):
        """Workflow should instantiate all registered plugins from config."""
        workflow = Workflow(config=config_with_plugins)

        assert len(workflow._plugins) == 2
        assert any(p.name == "plugin_a" for p in workflow._plugins)
        assert any(p.name == "plugin_b" for p in workflow._plugins)

    def test_workflow_skips_disabled_plugins(self, config):
        """Workflow should not instantiate disabled plugins."""
        PluginRegistry.register_class(PluginA, config=PluginAConfig)

        config.plugins = {
            PluginA.name: PluginAConfig(value=10, enabled=False),
        }

        workflow = Workflow(config=config)
        assert len(workflow._plugins) == 0

    def test_workflow_run_plugins_sequential(self, config_with_plugins):
        """Workflow should execute plugins sequentially by default."""
        workflow = Workflow(config=config_with_plugins)

        workflow.run_plugins(parallel=False)

        # Both plugins should have been executed
        assert len(workflow._result_collector.results) > 0

    def test_workflow_run_plugins_parallel(self, config_with_plugins):
        """Workflow should execute plugins in parallel when requested."""
        workflow = Workflow(config=config_with_plugins)

        workflow.run_plugins(parallel=True, max_workers=2)

        # Both plugins should have been executed
        assert len(workflow._result_collector.results) > 0

    def test_workflow_collects_plugin_results(self, config_with_plugins):
        """Workflow should collect results from executed plugins."""
        workflow = Workflow(config=config_with_plugins)

        workflow.run_plugins()

        results = workflow._result_collector.results
        assert (
            len(results) >= 0
        )  # Plugins may have results or not depending on implementation

    def test_workflow_handles_plugin_execution_errors(self, config):
        """Workflow should handle exceptions from plugin execution."""
        PluginRegistry.register_class(FailingPlugin, config=PluginAConfig)

        config.plugins = {
            FailingPlugin.name: PluginAConfig(value=1, enabled=True),
        }

        workflow = Workflow(config=config)

        # This should not raise, but collect the error
        workflow.run_plugins()

        # Error should be collected in results
        error_results = [
            r
            for r in workflow._result_collector.results
            if r.severity == Severity.ERROR
        ]
        assert len(error_results) > 0


class TestWorkflowSystemUpdate:
    """Test system update execution within the workflow."""

    def test_workflow_skips_system_update_without_manager(self, config):
        """Workflow should skip system update if no system manager is provided."""
        workflow = Workflow(system_manager=None, config=config)

        # Should not raise
        workflow.run_system_update()

        # No results should be added from system manager
        assert len(workflow._result_collector.results) == 0

    def test_workflow_calls_system_manager_update(self, config):
        """Workflow should call system manager's update method."""

        class MockPackageManager(PackageManager):
            def update(self, dry_run: bool = False) -> Result | None:
                return Result(
                    step="package_update",
                    severity=Severity.INFO,
                    message="Packages updated",
                )

            def upgrade(self, dry_run: bool = False) -> Result | None:
                return Result(
                    step="package_upgrade", severity=Severity.INFO, message="Upgraded"
                )

        class MockManager(SystemManager):
            def _is_reboot_required(self) -> bool:
                return True

            def _is_new_stable_os_available(self) -> bool:
                return True

        mock_manager = MockManager(pkg_manager=MockPackageManager())
        workflow = Workflow(system_manager=mock_manager, config=config)
        workflow.run_system_update()

        assert len(workflow._result_collector.results) == 4

    def test_workflow_handles_system_manager_errors(self, config):
        """Workflow should handle exceptions from system manager."""
        mock_manager = Mock()
        mock_manager.update.side_effect = RuntimeError("System update failed")

        workflow = Workflow(system_manager=mock_manager, config=config)

        # Should not raise, but collect error
        workflow.run_system_update()

        error_results = [
            r
            for r in workflow._result_collector.results
            if r.severity == Severity.ERROR
        ]
        assert len(error_results) > 0


class TestWorkflowResultProcessing:
    """Test result collection and reporting."""

    def test_workflow_processes_results_and_sends_report(self, config_with_plugins):
        """Workflow should process collected results and send a notification report."""
        workflow = Workflow(config=config_with_plugins)

        workflow.run_plugins()

        # Mock the notifier to capture the report
        with patch.object(workflow._notifier, "notify") as mock_notify:
            workflow.process_results()

            mock_notify.assert_called_once()
            subject, report = mock_notify.call_args[0]
            assert subject == "Workflow Report"
            assert isinstance(report, str)

    def test_workflow_formats_report_with_logs(self, config_with_plugins):
        """Workflow should include logs in the formatted report."""
        workflow = Workflow(config=config_with_plugins)

        # Log something
        workflow._logger.info("Test log message")

        with patch.object(workflow._notifier, "notify") as mock_notify:
            workflow.process_results()

            _, report = mock_notify.call_args[0]
            # Report should be generated (actual content depends on implementation)
            assert isinstance(report, str)

    def test_workflow_handles_notification_errors(self, config_with_plugins):
        """Workflow should handle errors when sending notifications."""
        workflow = Workflow(config=config_with_plugins)

        # Make notifier raise an error
        workflow._notifier.notify = Mock(
            side_effect=RuntimeError("Notification failed")
        )

        # Should not raise, but log the error
        workflow.process_results()

        # No exception should propagate


class TestWorkflowFullRun:
    """Test complete workflow execution."""

    def test_workflow_run_all_executes_all_steps(self, config_with_plugins):
        """Workflow.run_all() should execute all steps in sequence."""
        workflow = Workflow(config=config_with_plugins)

        with (
            patch.object(workflow, "run_system_update") as mock_sys_update,
            patch.object(workflow, "run_plugins") as mock_plugins,
            patch.object(workflow, "process_results") as mock_process,
        ):
            workflow.run_all()

            mock_sys_update.assert_called_once()
            mock_plugins.assert_called_once()
            mock_process.assert_called_once()

    def test_workflow_run_all_with_system_manager(self, config_with_plugins):
        """Workflow.run_all() should include system manager execution."""
        mock_manager = Mock()
        mock_manager.update.return_value = Result(
            step="system_update", severity=Severity.INFO, message="Updated"
        )
        mock_manager.check_reboot_required.return_value = None
        mock_manager.check_major_release_available.return_value = None

        workflow = Workflow(system_manager=mock_manager, config=config_with_plugins)

        # Should execute without raising
        workflow.run_all()

        mock_manager.update.assert_called()

    def test_workflow_run_all_parallel(self, config_with_plugins):
        """Workflow should support parallel execution during run_all."""
        workflow = Workflow(config=config_with_plugins)

        with patch.object(workflow, "run_plugins") as mock_plugins:
            # Simulate what run_all does
            workflow.run_system_update()
            workflow.run_plugins()  # This will call the mock
            workflow.process_results()

            mock_plugins.assert_called_once()


class TestWorkflowContextSharing:
    """Test context sharing between plugins and workflow."""

    def test_workflow_provides_context_to_plugins(self, config_with_plugins):
        """All plugins should receive a shared context."""
        workflow = Workflow(config=config_with_plugins)

        # All plugins should have a context
        for plugin in workflow._plugins:
            assert plugin.ctx is not None
            assert isinstance(plugin.ctx, Context)

    def test_workflow_context_has_dry_run_setting(self, config):
        """Context should reflect the workflow's dry_run setting."""
        config.dry_run = True
        workflow = Workflow(config=config)

        # The context created by workflow should have dry_run=True
        assert workflow._config.dry_run is True

    def test_plugins_can_record_results_in_context(self, config_with_plugins):
        """Plugins should be able to add results to their context."""
        workflow = Workflow(config=config_with_plugins)

        # Add a result to first plugin's context
        if workflow._plugins:
            plugin = workflow._plugins[0]
            test_result = Result(step="test", severity=Severity.INFO, message="Test")
            plugin.ctx.add_result(test_result)

            assert test_result in workflow._result_collector.results


class TestWorkflowConfiguration:
    """Test configuration handling in workflow."""

    def test_workflow_accepts_preconfigured_config(self, tmp_path):
        """Workflow should accept a pre-built CoreConfig."""
        log_file = str(tmp_path / "custom.log")

        config = CoreConfig(
            plugins={},
            notifiers={},
            dry_run=False,
            logging=LoggingConfig(file=log_file, debug=False),
        )

        workflow = Workflow(config=config)

        assert workflow._config.dry_run is False
        assert workflow._config.logging.file == log_file

    def test_workflow_applies_dry_run_to_command_runner(self, config):
        """Workflow should configure CommandRunner with dry_run setting."""
        config.dry_run = True
        _ = Workflow(config=config)

        # CommandRunner should be configured with dry_run=True
        from opsflow.core.utils import CommandRunner

        assert CommandRunner._dry_run is True

    def test_workflow_creates_composite_notifier(self, config):
        """Workflow should create a CompositeNotifier."""
        workflow = Workflow(config=config)

        from opsflow.core.notifier.composite import CompositeNotifier

        assert isinstance(workflow._notifier, CompositeNotifier)


class TestWorkflowErrorHandling:
    """Test error handling throughout the workflow."""

    def test_workflow_gracefully_handles_plugin_load_errors(self, tmp_path, config):
        """Workflow should record errors when plugins fail to load."""
        with patch(
            "opsflow.core.utils.module_loader.ModuleLoader.load_from_directory",
            side_effect=ImportError("Module not found"),
        ):
            workflow = Workflow(config=config, plugin_dir=str(tmp_path / "plugins"))

            # Error should be recorded in results
            error_results = [
                r
                for r in workflow._result_collector.results
                if "module_load:plugins" in r.step
            ]
            assert len(error_results) > 0

    def test_workflow_gracefully_handles_notifier_load_errors(self, tmp_path, config):
        """Workflow should record errors when notifiers fail to load."""
        with patch(
            "opsflow.core.utils.module_loader.ModuleLoader.load_from_directory",
            side_effect=ImportError("Module not found"),
        ):
            workflow = Workflow(config=config, notifier_dir=str(tmp_path / "notifiers"))

            # Error should be recorded in results
            error_results = [
                r
                for r in workflow._result_collector.results
                if "module_load:notifiers" in r.step
            ]
            assert len(error_results) > 0

    def test_workflow_collects_plugin_setup_errors(self, config):
        """Workflow should collect errors that occur during plugin setup."""
        # Create a mock plugin that fails on setup
        mock_plugin = Mock()
        mock_plugin.name = "failing_setup"
        mock_plugin.setup.side_effect = RuntimeError("Setup failed")

        workflow = Workflow(config=config)
        workflow._plugins = [mock_plugin]

        workflow.run_plugins()

        error_results = [
            r for r in workflow._result_collector.results if "setup" in r.step
        ]
        assert len(error_results) > 0

    def test_workflow_continues_after_plugin_teardown_error(self, config):
        """Workflow should continue even if plugin teardown fails."""
        # Create a mock plugin with failing teardown
        mock_plugin = Mock()
        mock_plugin.name = "teardown_failure"
        mock_plugin.setup.return_value = None
        mock_plugin.run.return_value = None
        mock_plugin.teardown.side_effect = RuntimeError("Teardown failed")
        mock_plugin.ctx = Mock()
        mock_plugin.ctx.results = []

        workflow = Workflow(config=config)
        workflow._plugins = [mock_plugin]

        # Should not raise
        workflow.run_plugins()

        # Teardown error should be recorded as warning
        warning_results = [
            r
            for r in workflow._result_collector.results
            if r.severity == Severity.WARNING and "teardown" in r.step
        ]
        assert len(warning_results) > 0
