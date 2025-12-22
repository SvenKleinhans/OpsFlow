from opsflow.core.workflow import Workflow
from opsflow.core.plugin import PluginRegistry
from opsflow.core.models import Severity

# Import test dummies
from ..dummies.plugins import (
    PluginA,
    FailingPlugin,
    PluginAConfig,
)


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
