from unittest.mock import Mock

from opsflow.core.system import PackageManager, SystemManager
from opsflow.core.workflow import Workflow
from opsflow.core.models import Result, Severity


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
