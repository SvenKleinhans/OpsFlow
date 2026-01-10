"""
Demo workflow using preconfigured ExamplePlugin and ExampleNotifier.

This script demonstrates two variants:
1. Running the workflow without a SystemManager.
2. Running the workflow with an ExampleSystemManager.
"""

from components.example_notifier import ExampleNotifier, ExampleNotifierConfig
from components.example_package_manager import ExamplePackageManager
from components.example_plugin import ExamplePlugin, ExamplePluginConfig
from components.example_system_manager import ExampleSystemManager
from opsflow.core.config import CoreConfig, LoggingConfig
from opsflow.core.notifier import NotifierRegistry
from opsflow.core.plugin import PluginRegistry
from opsflow.core.workflow import Workflow

# Register the example plugin and notifier
PluginRegistry.register_class(ExamplePlugin, ExamplePluginConfig)
NotifierRegistry.register_class(ExampleNotifier, ExampleNotifierConfig)

# -------------------------------
# Configuration setup
# -------------------------------
cfg = CoreConfig(
    dry_run=True,
    logging=LoggingConfig(debug=True, file="demo_workflow.log"),
    notifiers={
        "example_notifier": ExampleNotifierConfig(
            enabled=True, notify_option="notify_value"
        )
    },
    plugins={
        "example_plugin": ExamplePluginConfig(enabled=True, example_option="demo_value")
    },
)
ExampleNotifierConfig.model_validate(cfg.notifiers["example_notifier"])

# -------------------------------
# Workflow without SystemManager
# -------------------------------
wf_no_system = Workflow(config=cfg)
wf_no_system.run_all()

# -------------------------------
# Workflow with SystemManager and PackageManager
# -------------------------------
wf_with_system = Workflow(
    system_manager=ExampleSystemManager(),
    pkg_manager=ExamplePackageManager(),
    config=cfg,
)
wf_with_system.run_all()
