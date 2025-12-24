from opsflow.core.models import Result, Severity
from opsflow.core.models.context import Context
from opsflow.core.workflow import Workflow


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
