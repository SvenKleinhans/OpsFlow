"""
Demo workflow using auto-registered ExamplePlugin and ExampleNotifier.

This script demonstrates how the workflow can automatically load plugins
and notifiers from a directory using the module loader, without any manual registration.
"""

from pathlib import Path

from components.auto_registered_notifiers.example_notifier_auto import (
    ExampleNotifierAutoConfig,
)
from components.auto_registered_plugins.example_plugin_auto import (
    ExamplePluginAutoConfig,
)
from opsflow.core.config.schema import CoreConfig, LoggingConfig
from opsflow.core.workflow import Workflow

cfg = CoreConfig(
    dry_run=True,
    logging=LoggingConfig(debug=False, file="demo_workflow.log"),
    notifiers={
        "example_notifier_auto": ExampleNotifierAutoConfig(
            enabled=True, notify_option="notify_value"
        )
    },
    plugins={
        "example_plugin_auto": ExamplePluginAutoConfig(
            enabled=True, example_option="demo_value"
        )
    },
)

components = Path.cwd() / "examples" / "components"

# Create and run the workflow
wf = Workflow(
    config=cfg,
    plugin_dir=str(components / "auto_registered_plugins"),
    notifier_dir=str(components / "auto_registered_notifiers"),
)

wf.run_all()
