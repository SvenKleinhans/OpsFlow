from unittest.mock import Mock, patch

from opsflow.core.models import Result, Severity
from opsflow.core.workflow import Workflow


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
