from opsflow.core.config import CoreConfig, LoggingConfig
from opsflow.core.workflow import Workflow


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
