"""
Demo workflow using auto-registered ExamplePlugin and ExampleNotifier.

This script demonstrates how the workflow can automatically load plugins
and notifiers from a directory using the module loader, without any manual registration.
"""

from opsflow.core.workflow import Workflow


# Create and run the workflow
wf = Workflow(
    plugin_dir="components/auto_registered_plugins",
    notifier_dir="components/auto_registered_notifiers",
)

wf.run_all()
