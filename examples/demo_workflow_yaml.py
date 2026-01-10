"""
Demo workflow using YAML configuration with Example components.

This script demonstrates two variants:
1. Workflow without SystemManager.
2. Workflow with SystemManager and PackageManager integrated.
"""

from pathlib import Path

from components.example_notifier import ExampleNotifier, ExampleNotifierConfig
from components.example_plugin import ExamplePlugin, ExamplePluginConfig
from components.example_system_manager import ExampleSystemManager
from components.example_package_manager import ExamplePackageManager
from opsflow.core.notifier import NotifierRegistry
from opsflow.core.plugin import PluginRegistry
from opsflow.core.workflow import Workflow

# Register the example plugin and notifier
PluginRegistry.register_class(ExamplePlugin, ExamplePluginConfig)
NotifierRegistry.register_class(ExampleNotifier, ExampleNotifierConfig)

example_config = Path.cwd() / "examples" / "example_config.yaml"

# -------------------------------
# Workflow without SystemManager
# -------------------------------
wf_no_system = Workflow(config_path=str(example_config))
wf_no_system.run_all()

# -------------------------------
# Workflow with SystemManager
# -------------------------------
wf_with_system = Workflow(
    system_manager=ExampleSystemManager(),
    pkg_manager=ExamplePackageManager(),
    config_path=str(example_config),
)
wf_with_system.run_all()
