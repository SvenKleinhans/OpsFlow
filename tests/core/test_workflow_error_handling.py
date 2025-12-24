from unittest.mock import Mock, patch

from opsflow.core.models import Severity
from opsflow.core.workflow import Workflow


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
                r for r in workflow._result_collector.results if "module_load:plugins" in r.step
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
                r for r in workflow._result_collector.results if "module_load:notifiers" in r.step
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

        error_results = [r for r in workflow._result_collector.results if "setup" in r.step]
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
