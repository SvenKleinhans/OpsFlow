"""
Demo workflow using YAML configuration with Example components.

This script demonstrates two variants:
1. Workflow without SystemManager.
2. Workflow with SystemManager and PackageManager integrated.
"""

from opsflow.core.workflow import Workflow
from opsflow.core.plugin import PluginRegistry
from opsflow.core.notifier import NotifierRegistry

from examples.components.example_plugin import ExamplePlugin, ExamplePluginConfig
from examples.components.example_notifier import ExampleNotifier, ExampleNotifierConfig
from examples.components.example_system_manager import ExampleSystemManager
from examples.components.example_package_manager import ExamplePackageManager

# Register the example plugin and notifier
PluginRegistry.register_class(ExamplePlugin, ExamplePluginConfig)
NotifierRegistry.register_class(ExampleNotifier, ExampleNotifierConfig)

# -------------------------------
# Workflow without SystemManager
# -------------------------------
wf_no_system = Workflow(config_path="example_config.yaml")
wf_no_system.run_all()

# -------------------------------
# Workflow with SystemManager
# -------------------------------
system_manager = ExampleSystemManager(pkg_manager=ExamplePackageManager())
wf_with_system = Workflow(
    system_manager=system_manager, config_path="example_config.yaml"
)
wf_with_system.run_all()
